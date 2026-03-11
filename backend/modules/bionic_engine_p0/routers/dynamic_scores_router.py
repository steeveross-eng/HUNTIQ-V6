"""
BIONIC V5 — Dynamic Exclusion Scores Router
=============================================
Endpoint: POST /api/v1/bionic/dynamic-scores

Retourne les facteurs d'exclusion dynamiques pour une position donnée:
- Météo (température, vent, humidité)
- Pression humaine (saison chasse, weekend)
- Temporel (heure du jour, activité animale)
- Saisonnier (période de l'année)
- Stress thermique

Source de vérité backend. Aucune logique d'exclusion frontend.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("bionic_engine.dynamic_scores")

router = APIRouter(prefix="/dynamic", tags=["Dynamic Exclusion Scores"])


class DynamicScoreRequest(BaseModel):
    lat: float
    lng: float
    species: str = "moose"
    region: str = "quebec"
    hour: Optional[int] = None
    temperature_c: Optional[float] = None
    humidity: Optional[float] = None


@router.post("/scores")
async def get_dynamic_scores(req: DynamicScoreRequest):
    """
    Calcule les scores d'exclusion dynamiques pour une position.
    Utilise le MultifactorScoringEngine backend.
    """
    try:
        from modules.bionic_engine_p0.services.scoring.multifactor_scoring_engine import (
            MultiFactorScoringEngine
        )

        engine = MultiFactorScoringEngine()
        now = datetime.now(timezone.utc)
        hour = req.hour if req.hour is not None else now.hour
        check_date = now.date()

        result = engine.calculate_composite_score(
            species=req.species,
            region=req.region,
            check_date=check_date,
            hour=hour,
            temperature_c=req.temperature_c,
            humidity=req.humidity,
        )

        # Format response
        factors = {}
        for key, val in result.factors.items():
            factors[key] = {
                "active": val.get("active", False),
                "contribution": round(val.get("contribution", 0), 2),
                "weight": round(val.get("weight", 0), 3),
            }
            # Add specific fields
            if key == "thermal_stress":
                factors[key]["temperature_c"] = val.get("temperature_c")
                factors[key]["modifier"] = round(val.get("modifier", 1.0), 3)
            elif key == "hunting_pressure":
                factors[key]["hunting_season"] = val.get("hunting_season", False)
                factors[key]["is_weekend"] = val.get("is_weekend", False)
                factors[key]["modifier"] = round(val.get("modifier", 1.0), 3)
            elif key == "temporal":
                factors[key]["hour"] = val.get("hour", hour)
                factors[key]["activity_level"] = round(val.get("activity_level", 0), 3)
            elif key == "calving":
                factors[key]["modifier"] = round(val.get("modifier", 1.0), 3)
            elif key == "seasonal_context":
                factors[key]["season"] = val.get("season", "unknown")
                factors[key]["score"] = round(val.get("score", 0), 3)

        return {
            "success": True,
            "score": round(result.score, 2),
            "confidence": round(result.confidence, 3),
            "risk_level": result.risk_level,
            "active_factors": result.active_factors,
            "total_factors": result.total_factors,
            "factors": factors,
            "recommendations": result.recommendations,
            "meta": {
                "species": req.species,
                "region": req.region,
                "date": str(check_date),
                "hour": hour,
                "lat": req.lat,
                "lng": req.lng,
                "version": "ExclusionsSpatiales.v1+dynamic",
            }
        }
    except Exception as e:
        logger.error(f"Dynamic scores error: {e}")
        return {
            "success": False,
            "error": str(e),
            "score": 0,
            "factors": {},
            "recommendations": [],
        }
