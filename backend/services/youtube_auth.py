"""
youtube_auth.py
---------------
Generates YouTube Proof-of-Origin (PO) tokens to bypass bot-detection when
yt-dlp runs on cloud/datacenter IPs (e.g. Render, Railway, Fly.io).

Strategy:
1. Run `npx -y youtube-po-token-generator` (Node.js – pre-installed on Render).
2. Parse the JSON output: {"visitorData": "...", "poToken": "..."}.
3. Cache the result for PO_TOKEN_CACHE_TTL seconds (default 10 min).
4. Expose `get_ydl_auth_opts()` which merges the tokens into a yt-dlp opts dict.
5. Gracefully fall back to an empty dict if Node / npx is unavailable.
"""

import json
import subprocess
import time
import threading
from typing import Dict, Any

from config import settings
from logger import logger

# Thread-safe cache
_cache_lock = threading.Lock()
_cached_tokens: Dict[str, str] = {}
_cache_expiry: float = 0.0

# Realistic browser User-Agent — helps bypass lightweight IP checks
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def _fetch_tokens() -> Dict[str, str]:
    """
    Invoke the Node.js PO-token generator and return the parsed token dict.
    Returns an empty dict on any failure so callers degrade gracefully.
    """
    try:
        logger.info("Fetching fresh YouTube PO tokens via npx...")
        result = subprocess.run(
            ["npx", "-y", "youtube-po-token-generator"],
            capture_output=True,
            text=True,
            timeout=60,  # npx may need to download the package first time
        )
        if result.returncode != 0:
            logger.warning(
                f"youtube-po-token-generator exited with code {result.returncode}: "
                f"{result.stderr.strip()}"
            )
            return {}

        output = result.stdout.strip()
        # The tool may emit npm logs before the JSON — find the JSON object
        json_start = output.rfind("{")
        json_end = output.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            logger.warning(f"Could not find JSON in token generator output: {output!r}")
            return {}

        data: Dict[str, str] = json.loads(output[json_start:json_end])
        logger.info("YouTube PO tokens fetched successfully.")
        return data

    except FileNotFoundError:
        logger.warning("npx not found — PO token auth is disabled. Falling back to no auth.")
        return {}
    except subprocess.TimeoutExpired:
        logger.warning("youtube-po-token-generator timed out.")
        return {}
    except Exception as exc:
        logger.warning(f"Unexpected error fetching PO tokens: {exc}")
        return {}


def _get_tokens() -> Dict[str, str]:
    """Return cached tokens, refreshing if expired."""
    global _cached_tokens, _cache_expiry

    with _cache_lock:
        if time.monotonic() < _cache_expiry and _cached_tokens:
            return _cached_tokens

        tokens = _fetch_tokens()
        _cached_tokens = tokens
        _cache_expiry = time.monotonic() + settings.PO_TOKEN_CACHE_TTL
        return _cached_tokens


def get_ydl_auth_opts() -> Dict[str, Any]:
    """
    Build and return a dict of yt-dlp options that inject YouTube auth tokens.

    Merge this into your existing ydl_opts before creating a YoutubeDL instance:

        ydl_opts = {**base_opts, **get_ydl_auth_opts()}

    Returns an empty dict if tokens are unavailable (so yt-dlp still works
    on local machines / non-YouTube URLs without crashing).
    """
    tokens = _get_tokens()

    po_token: str = tokens.get("poToken", "")
    visitor_data: str = tokens.get("visitorData", "")

    opts: Dict[str, Any] = {
        # Spoof a real browser regardless of whether we have PO tokens
        "http_headers": {
            "User-Agent": _BROWSER_USER_AGENT,
        },
    }

    if po_token and visitor_data:
        opts["extractor_args"] = {
            "youtube": {
                # Format expected by yt-dlp: "web+<TOKEN>"
                "po_token": [f"web+{po_token}"],
                "player_client": ["web"],
                "visitor_data": [visitor_data],
            }
        }
        logger.debug("Injecting YouTube PO token + visitor_data into yt-dlp opts.")
    else:
        logger.debug("No PO tokens available — using User-Agent spoofing only.")

    # Optional: cookie file fallback (set YOUTUBE_COOKIES_FILE env var on Render)
    if settings.YOUTUBE_COOKIES_FILE:
        opts["cookiefile"] = settings.YOUTUBE_COOKIES_FILE
        logger.debug(f"Using YouTube cookies file: {settings.YOUTUBE_COOKIES_FILE}")

    return opts
