"""
SERVICE SENTINEL OAUTH2 — Client Credentials Flow
BIONIC V5 ULTIME 300% — sentinel_oauth_v1

Gere l'authentification OAuth2 avec Copernicus Data Space.
Token cache en memoire avec renouvellement automatique.

Module isole. 0 impact sur pipeline principal.
"""

import os
import time
import logging
import httpx

logger = logging.getLogger("bionic_engine.sentinel_oauth")

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

_token_cache = {
    "access_token": None,
    "expires_at": 0,
}


async def get_access_token() -> str:
    """Obtain or refresh OAuth2 access token for Copernicus Data Space."""
    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["access_token"]

    client_id = os.environ.get("SENTINEL2_CLIENT_ID")
    client_secret = os.environ.get("SENTINEL2_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("SENTINEL2_CLIENT_ID and SENTINEL2_CLIENT_SECRET required")

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()

    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 300)

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in

    logger.info(f"Sentinel OAuth2 token obtained (expires in {expires_in}s)")
    return access_token


async def check_credentials() -> dict:
    """Verify that Sentinel-2 credentials are valid."""
    try:
        token = await get_access_token()
        return {
            "status": "valid",
            "token_preview": token[:12] + "...",
            "provider": "Copernicus Data Space",
        }
    except ValueError as e:
        return {"status": "not_configured", "error": str(e)}
    except httpx.HTTPStatusError as e:
        return {"status": "invalid", "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
