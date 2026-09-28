"""
auth_router.py
--------------
FastAPI router for YouTube OAuth2 device-code flow.

Endpoints:
  POST   /api/auth/youtube/start   — start device-code flow for a session
  GET    /api/auth/youtube/status  — poll auth state for a session
  DELETE /api/auth/youtube/logout  — revoke a session's token
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from services.youtube_oauth import (
    start_oauth_session,
    get_session,
    revoke_session,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StartAuthRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated UUID identifying the browser session")


class AuthStatusResponse(BaseModel):
    session_id: str
    state: str           # pending | waiting_for_user | authorized | failed
    verification_url: str
    user_code: str
    error: str
    authorized: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "/youtube/start",
    response_model=AuthStatusResponse,
    summary="Start YouTube OAuth2 device-code flow",
)
async def start_youtube_auth(body: StartAuthRequest):
    """
    Kick off the YouTube TV device-code flow for a user session.
    Returns the verification URL and user code immediately (state='pending' or
    'waiting_for_user' once the background thread has fetched them).
    The client should then poll /status.
    """
    session = start_oauth_session(body.session_id)
    return AuthStatusResponse(**session.to_dict())


@router.get(
    "/youtube/status",
    response_model=AuthStatusResponse,
    summary="Poll OAuth2 authorization status",
)
async def get_youtube_auth_status(session_id: str):
    """
    Poll the state of an ongoing or completed OAuth2 authorization flow.
    Keep polling every 3–5 seconds until state == 'authorized' or 'failed'.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No auth session found for session_id='{session_id}'. Call /start first.",
        )
    return AuthStatusResponse(**session.to_dict())


@router.delete(
    "/youtube/logout",
    summary="Revoke YouTube session token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_youtube_auth(session_id: str):
    """
    Delete the OAuth2 token for a session. The user will need to re-authorize
    the next time they want to download a YouTube video.
    """
    revoke_session(session_id)
