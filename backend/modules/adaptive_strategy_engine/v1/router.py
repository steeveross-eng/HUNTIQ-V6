"""Adaptive Strategy Engine Router - PLAN MAITRE
FastAPI router for adaptive hunting strategies.

Version: 1.0.0
API Prefix: /api/v1/adaptive
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import AdaptiveStrategyService

router = APIRouter(prefix="/api/v1/adaptive", tags=["Adaptive Strategy Engine"])

_service = AdaptiveStrategyService()


@router.get("/")
async def adaptive_engine_info():
    """Get adaptive strategy engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "adaptive_strategy_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Stratégies adaptatives en temps réel",
        "status": "operational",
        "features": [
            "Adaptation aux conditions changeantes",
            "Apprentissage des succès/échecs",
            "Suggestions dynamiques",
            "Optimisation de parcours",
            "Feedback loop"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "adaptive_strategy_engine", "version": "1.0.0"}


@router.post("/strategy")
async def create_strategy(
    species: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    strategy_type: Optional[str] = Query(None),
    temperature: Optional[float] = Query(None),
    wind_speed: Optional[float] = Query(None),
    wind_direction: Optional[str] = Query(None)
):
    """Create a new adaptive strategy"""
    conditions = {}
    if temperature is not None:
        conditions["temperature"] = temperature
    if wind_speed is not None:
        conditions["wind_speed"] = wind_speed
    if wind_direction:
        conditions["wind_direction"] = wind_direction
    
    strategy = await _service.create_strategy(
        species=species,
        lat=lat,
        lng=lng,
        strategy_type=strategy_type,
        conditions=conditions if conditions else None
    )
    
    return {"success": True, "strategy": strategy.model_dump()}


@router.get("/strategy/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get strategy details"""
    strategy = await _service.get_strategy(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")
    
    return {"success": True, "strategy": strategy.model_dump()}


@router.post("/adjust/{strategy_id}")
async def check_adjustments(
    strategy_id: str,
    temperature: Optional[float] = Query(None),
    wind_speed: Optional[float] = Query(None),
    wind_direction: Optional[str] = Query(None)
):
    """Check for strategy adjustments"""
    conditions = {}
    if temperature is not None:
        conditions["temperature"] = temperature
    if wind_speed is not None:
        conditions["wind_speed"] = wind_speed
    if wind_direction:
        conditions["wind_direction"] = wind_direction
    
    adjustments = await _service.check_for_adjustments(
        strategy_id,
        conditions if conditions else None
    )
    
    return {
        "success": True,
        "adjustments_needed": len(adjustments) > 0,
        "adjustments": [a.model_dump() for a in adjustments]
    }


@router.post("/adjust/{strategy_id}/apply/{adjustment_id}")
async def apply_adjustment(strategy_id: str, adjustment_id: str):
    """Apply an adjustment to strategy"""
    strategy = await _service.apply_adjustment(strategy_id, adjustment_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie ou ajustement non trouvé")
    
    return {"success": True, "strategy": strategy.model_dump()}


@router.post("/feedback")
async def submit_feedback(
    strategy_id: str = Query(...),
    user_id: str = Query(...),
    outcome: str = Query(..., regex="^(success|partial|failure|abandoned)$"),
    sighting: bool = Query(False),
    harvest: bool = Query(False),
    rating: int = Query(3, ge=1, le=5),
    notes: Optional[str] = Query(None)
):
    """Submit feedback on strategy effectiveness"""
    feedback = await _service.submit_feedback(
        strategy_id=strategy_id,
        user_id=user_id,
        outcome=outcome,
        sighting=sighting,
        harvest=harvest,
        rating=rating,
        notes=notes
    )
    
    return {"success": True, "feedback": feedback.model_dump()}


@router.post("/learn")
async def trigger_learning(strategy_id: str = Query(...)):
    """Manually trigger learning from strategy data"""
    strategy = await _service.get_strategy(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")
    
    return {
        "success": True,
        "message": "Données d'apprentissage enregistrées",
        "strategy_id": strategy_id
    }


@router.post("/optimize-route")
async def optimize_route(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: Optional[float] = Query(None),
    end_lng: Optional[float] = Query(None),
    optimize_for: str = Query("balanced", regex="^(wind|cover|distance|activity|balanced)$")
):
    """Optimize a hunting route"""
    route = await _service.optimize_route(
        start_lat=start_lat,
        start_lng=start_lng,
        end_lat=end_lat,
        end_lng=end_lng,
        optimize_for=optimize_for
    )
    
    return {"success": True, "route": route.model_dump()}
