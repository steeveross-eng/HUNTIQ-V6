"""
PHASE E — Router Conditions Saisonnières
BIONIC V5 — Endpoint isolé, 0 transversalité

GET /api/v1/bionic/seasonal-conditions?lat=X&lng=Y
"""

import logging
from fastapi import APIRouter, Query, HTTPException

from modules.bionic_engine_p0.services.seasonal_conditions_service import (
    compute_seasonal_conditions
)

logger = logging.getLogger("bionic_engine.seasonal_conditions_router")

router = APIRouter(prefix="/api/v1/bionic", tags=["PHASE E - Conditions Saisonnieres"])


@router.get("/seasonal-conditions")
async def get_seasonal_conditions(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Retourne les conditions saisonnières pour un point.
    Module isolé: météo, phénologie, pression de chasse, score global.
    """
    try:
        result = compute_seasonal_conditions(lat, lng)
        return result
    except Exception as e:
        logger.error(f"Seasonal conditions error: {e}")
        raise HTTPException(status_code=500, detail="Erreur calcul conditions saisonnieres")
