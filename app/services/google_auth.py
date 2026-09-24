"""
Google OAuth 2.0 Integration Service
Handles authorization URL generation, code exchange, and ID token verification.
"""

import logging
import secrets
import urllib.parse
from typing import Any

import httpx

from app.config import settings
from app.core.exceptions import GoogleAuthException
from app.schemas.user import GoogleAuthUrlResponse

logger = logging.getLogger("arkidi.services.google_auth")

GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleAuthService:
    """Service to coordinate OAuth 2.0 communication with Google APIs."""

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._client = http_client

    def get_authorization_url(self, redirect_uri: str | None = None) -> GoogleAuthUrlResponse:
        """Construct the Google OAuth 2.0 consent screen redirect URL."""
        if not settings.GOOGLE_CLIENT_ID:
            raise GoogleAuthException(
                "Google OAuth is not configured on this server.",
                message_key="errors.google_not_configured",
            )

        effective_redirect = (
            redirect_uri
            or settings.GOOGLE_REDIRECT_URI
            or f"{settings.PUBLIC_FRONTEND_URL}/auth/google/callback"
        )
        state = secrets.token_urlsafe(32)

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": effective_redirect,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "state": state,
            "prompt": "select_account",
        }

        url = f"{GOOGLE_AUTH_BASE}?{urllib.parse.urlencode(params)}"
        return GoogleAuthUrlResponse(url=url, state=state)

    async def verify_id_token(self, credential: str) -> dict[str, Any]:
        """Validate a Google ID token (from Google One-Tap or GIS button) against tokeninfo endpoint."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    GOOGLE_TOKENINFO_URL,
                    params={"id_token": credential},
                )
            except httpx.RequestError as exc:
                logger.exception("Google tokeninfo connection error: %s", exc)
                raise GoogleAuthException("Failed to reach Google token verification service.")

        if resp.status_code != 200:
            logger.warning("Google ID token rejected: %s", resp.text)
            raise GoogleAuthException(
                "Invalid Google ID token.",
                message_key="errors.google_auth_failed",
            )

        data = resp.json()
        email = data.get("email")
        if not email:
            raise GoogleAuthException("Google account payload did not contain an email address.")

        email_verified = str(data.get("email_verified", "")).lower() == "true"
        if not email_verified:
            raise GoogleAuthException(
                "Google account email is not verified.",
                message_key="errors.google_auth_failed",
            )

        # Enforce audience match when GOOGLE_CLIENT_ID is configured
        if settings.GOOGLE_CLIENT_ID and data.get("aud") != settings.GOOGLE_CLIENT_ID:
            logger.warning("Google token aud '%s' != configured client_id", data.get("aud"))
            raise GoogleAuthException(
                "Google token audience mismatch.",
                message_key="errors.google_auth_failed",
            )

        return {
            "email": email.lower().strip(),
            "name": data.get("name") or data.get("given_name") or email.split("@")[0],
            "sub": data.get("sub", ""),
        }

    async def exchange_code(self, code: str, redirect_uri: str | None = None) -> dict[str, Any]:
        """Exchange an authorization code for tokens and extract user profile."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise GoogleAuthException(
                "Google OAuth is not configured on this server.",
                message_key="errors.google_not_configured",
            )

        effective_redirect = (
            redirect_uri
            or settings.GOOGLE_REDIRECT_URI
            or f"{settings.PUBLIC_FRONTEND_URL}/auth/google/callback"
        )

        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": effective_redirect,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(GOOGLE_TOKEN_URL, data=payload)
            except httpx.RequestError as exc:
                logger.exception("Google token exchange request failed: %s", exc)
                raise GoogleAuthException("Failed to connect to Google OAuth token endpoint.")

            if resp.status_code != 200:
                logger.warning("Google token exchange error %s: %s", resp.status_code, resp.text)
                raise GoogleAuthException(
                    "Failed to exchange Google authorization code.",
                    message_key="errors.google_auth_failed",
                )

            token_data = resp.json()
            id_token = token_data.get("id_token")
            access_token = token_data.get("access_token")

            # Try reading claims directly from verified id_token
            if id_token:
                return await self.verify_id_token(id_token)

            # Fall back to userinfo endpoint with access_token
            if access_token:
                user_resp = await client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if user_resp.status_code == 200:
                    uinfo = user_resp.json()
                    email = uinfo.get("email")
                    if email:
                        return {
                            "email": email.lower().strip(),
                            "name": uinfo.get("name") or email.split("@")[0],
                            "sub": uinfo.get("sub", ""),
                        }

        raise GoogleAuthException("Could not obtain user profile from Google.")
