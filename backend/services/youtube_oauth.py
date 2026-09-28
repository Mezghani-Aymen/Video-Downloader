"""
youtube_oauth.py
----------------
Per-session YouTube OAuth2 device-code flow using yt-dlp's built-in support
(available since yt-dlp v2024.10.22).

Flow:
  1. POST /api/auth/youtube/start  → runs yt-dlp to get a device code + verification URL
  2. Frontend shows the code to user; user visits the URL on any device and logs in
  3. GET  /api/auth/youtube/status → polls until auth is complete or times out
  4. Once complete, a token file scoped to the session is written to disk
  5. All yt-dlp calls for that session use --netrc-location or cookiefile pointing
     to that session token file

Each user's session is identified by a session_id (UUID) stored in their browser's
localStorage, so sessions are isolated — users never share credentials.
"""

import asyncio
import os
import queue
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from logger import logger

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class OAuthSession:
    session_id: str
    state: str = "pending"          # pending | waiting_for_user | authorized | failed
    verification_url: str = ""
    user_code: str = ""
    token_dir: str = ""             # temp dir where yt-dlp writes its oauth2 token
    error: str = ""
    created_at: float = field(default_factory=time.monotonic)
    authorized_at: Optional[float] = None

    def is_expired(self, ttl: int = 600) -> bool:
        return time.monotonic() - self.created_at > ttl

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "state": self.state,
            "verification_url": self.verification_url,
            "user_code": self.user_code,
            "error": self.error,
            "authorized": self.state == "authorized",
        }


# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

_sessions: Dict[str, OAuthSession] = {}
_sessions_lock = threading.Lock()


def _cleanup_expired() -> None:
    with _sessions_lock:
        expired = [sid for sid, s in _sessions.items() if s.is_expired(ttl=1800)]
        for sid in expired:
            s = _sessions.pop(sid)
            if s.token_dir and os.path.isdir(s.token_dir):
                try:
                    import shutil
                    shutil.rmtree(s.token_dir, ignore_errors=True)
                except Exception:
                    pass


def get_session(session_id: str) -> Optional[OAuthSession]:
    _cleanup_expired()
    with _sessions_lock:
        return _sessions.get(session_id)


def get_token_dir(session_id: str) -> Optional[str]:
    """Return the token directory for a fully authorized session, or None."""
    session = get_session(session_id)
    if session and session.state == "authorized" and session.token_dir:
        return session.token_dir
    return None


def revoke_session(session_id: str) -> bool:
    with _sessions_lock:
        session = _sessions.pop(session_id, None)
    if session and session.token_dir and os.path.isdir(session.token_dir):
        try:
            import shutil
            shutil.rmtree(session.token_dir, ignore_errors=True)
        except Exception:
            pass
        return True
    return session is not None


# ---------------------------------------------------------------------------
# OAuth2 start — run yt-dlp device-code flow in background thread
# ---------------------------------------------------------------------------

def _run_oauth_flow(session_id: str, token_dir: str) -> None:
    """
    Background thread: runs yt-dlp with --username oauth2 to initiate the
    device-code flow. Parses stdout for the verification URL and user code,
    then waits for the user to authorize.
    """
    session = get_session(session_id)
    if not session:
        return

    # yt-dlp stores oauth2 tokens in a .cache dir inside token_dir
    cache_dir = os.path.join(token_dir, ".cache")
    os.makedirs(cache_dir, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--username", "oauth2",
        "--password", "",
        "--cache-dir", cache_dir,
        "--skip-download",
        # We just need it to go through auth — use a short known video
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        url_pattern = re.compile(r"https://www\.google\.com/device\b\S*")
        code_pattern = re.compile(r"\b([A-Z]{4}-[A-Z]{4})\b")  # e.g. ABCD-EFGH

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            logger.debug(f"[oauth:{session_id[:8]}] {line}")

            # Extract verification URL
            url_match = url_pattern.search(line)
            if url_match and not session.verification_url:
                with _sessions_lock:
                    session.verification_url = url_match.group(0)
                    session.state = "waiting_for_user"

            # Extract user code
            code_match = code_pattern.search(line)
            if code_match and not session.user_code:
                with _sessions_lock:
                    session.user_code = code_match.group(1)

            # Detect success
            if "authorized" in line.lower() or "token" in line.lower() or "successful" in line.lower():
                with _sessions_lock:
                    session.state = "authorized"
                    session.authorized_at = time.monotonic()

        proc.wait(timeout=300)

        with _sessions_lock:
            if session.state not in ("authorized", "failed"):
                if proc.returncode == 0:
                    session.state = "authorized"
                    session.authorized_at = time.monotonic()
                else:
                    session.state = "failed"
                    session.error = f"yt-dlp exited with code {proc.returncode}"

    except subprocess.TimeoutExpired:
        proc.kill()
        with _sessions_lock:
            session.state = "failed"
            session.error = "Authorization timed out (5 minutes)."
    except FileNotFoundError:
        with _sessions_lock:
            session.state = "failed"
            session.error = "yt-dlp not found on server."
    except Exception as exc:
        logger.error(f"OAuth flow error for session {session_id}: {exc}")
        with _sessions_lock:
            session.state = "failed"
            session.error = str(exc)


def start_oauth_session(session_id: str) -> OAuthSession:
    """
    Create a new OAuth session and launch the device-code flow in a daemon thread.
    If a valid authorized session already exists for this ID, return it immediately.
    """
    _cleanup_expired()

    # Reuse existing authorized session
    existing = get_session(session_id)
    if existing and existing.state == "authorized":
        return existing

    # Create temp dir for this session's token
    token_dir = tempfile.mkdtemp(prefix=f"yt_oauth_{session_id[:8]}_")

    session = OAuthSession(
        session_id=session_id,
        state="pending",
        token_dir=token_dir,
    )
    with _sessions_lock:
        _sessions[session_id] = session

    thread = threading.Thread(
        target=_run_oauth_flow,
        args=(session_id, token_dir),
        daemon=True,
        name=f"oauth-{session_id[:8]}",
    )
    thread.start()

    return session


# ---------------------------------------------------------------------------
# yt-dlp opts for an authorized session
# ---------------------------------------------------------------------------

def get_session_ydl_opts(session_id: str) -> dict:
    """
    Return extra yt-dlp opts to use a session's OAuth2 token.
    Returns empty dict if session is not authorized.
    """
    token_dir = get_token_dir(session_id)
    if not token_dir:
        return {}
    cache_dir = os.path.join(token_dir, ".cache")
    return {"cache-dir": cache_dir}
