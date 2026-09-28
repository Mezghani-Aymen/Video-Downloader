"""
youtube_auth.py
---------------
Provides yt-dlp options to bypass YouTube bot-detection on cloud servers
(Render, Railway, Fly.io, etc.).

Auth priority (first available wins):
  1. YOUTUBE_COOKIES_B64 env var  — base64-encoded cookies.txt content (MOST RELIABLE)
  2. YOUTUBE_COOKIES_FILE env var — path to an existing cookies.txt on disk
  3. User-Agent spoofing only     — minimal protection, may still be blocked
"""

import base64
import os
import tempfile
import threading
from typing import Any, Dict, Optional

from logger import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# Temporary file written from YOUTUBE_COOKIES_B64 — kept alive for the process lifetime
_temp_cookie_file: Optional[str] = None
_cookie_init_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Cookie file helpers
# ---------------------------------------------------------------------------

def _get_cookie_file_path() -> Optional[str]:
    """
    Return a path to a Netscape cookies.txt file, using whichever source is available.

    Priority:
      1. YOUTUBE_COOKIES_B64  — base64-encoded cookies text (best for Render env vars)
      2. YOUTUBE_COOKIES_FILE — direct file path
    """
    global _temp_cookie_file

    # --- Option 1: base64-encoded cookie content from env var ---
    b64_content = os.getenv("YOUTUBE_COOKIES_B64", "").strip()
    if b64_content:
        with _cookie_init_lock:
            # Re-check inside the lock (another thread may have written it already)
            if _temp_cookie_file and os.path.exists(_temp_cookie_file):
                return _temp_cookie_file
            try:
                cookie_bytes = base64.b64decode(b64_content)
                # NamedTemporaryFile with delete=False lives until the process exits
                tmp = tempfile.NamedTemporaryFile(
                    mode="wb",
                    suffix=".txt",
                    prefix="yt_cookies_",
                    delete=False,
                )
                tmp.write(cookie_bytes)
                tmp.flush()
                tmp.close()
                _temp_cookie_file = tmp.name
                logger.info(f"YouTube cookies loaded from YOUTUBE_COOKIES_B64 → {tmp.name}")
                return _temp_cookie_file
            except Exception as exc:
                logger.warning(f"Failed to decode YOUTUBE_COOKIES_B64: {exc}")

    # --- Option 2: direct file path ---
    file_path = os.getenv("YOUTUBE_COOKIES_FILE", "").strip()
    if file_path and os.path.isfile(file_path):
        logger.info(f"Using YouTube cookies file: {file_path}")
        return file_path

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_ydl_auth_opts() -> Dict[str, Any]:
    """
    Return a dict of yt-dlp options that authenticate against YouTube.

    Usage:
        ydl_opts = {**your_base_opts, **get_ydl_auth_opts()}

    Always safe to call — returns at minimum a User-Agent spoof so yt-dlp
    still works locally / for non-YouTube URLs.
    """
    opts: Dict[str, Any] = {
        "http_headers": {
            "User-Agent": _BROWSER_USER_AGENT,
        },
    }

    cookie_path = _get_cookie_file_path()
    if cookie_path:
        opts["cookiefile"] = cookie_path
        logger.debug(f"yt-dlp will use cookiefile: {cookie_path}")
    else:
        logger.warning(
            "No YouTube cookies configured. "
            "Set YOUTUBE_COOKIES_B64 on Render to fix bot-detection errors."
        )

    return opts

