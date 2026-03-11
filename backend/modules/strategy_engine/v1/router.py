"""Strategy Engine Router - CORE

FastAPI router for hunting strategy generation.

Version: 1.0.0
API Prefix: /api/v1/strategy
"""

from fastapi import APIRouter, HTTPException, Query
from .service import StrategyService
from .models import HuntingContext

router = APIRouter(prefix="/api/v1/strategy", tags=["Strategy Engine"])

# Initialize service
_service = StrategyService()


@router.get("/")
async def strategy_engine_info():
    """Get strategy engine information"""
    return {
        "module": "strategy_engine",
        "version": "1.0.0",
        "description": "Hunting strategy generation engine",
        "supported_species": list(_service.SPECIES_PATTERNS.keys()),
        "seasons": list(_service.SEASON_MODIFIERS.keys()),
        "weather_conditions": list(_service.WEATHER_IMPACT.keys()),
        "features": [
            "Complete strategy generation",
            "Stand placement recommendations",
            "Attractant strategies",
            "Equipment lists",
            "Timing optimization"
        ]
    }


@router.post("/generate")
async def generate_strategy(context: HuntingContext):
    """
    Generate a complete hunting strategy based on context.
    
    Provide species, season, time, weather, and terrain to get
    a comprehensive strategy with recommendations.
    """
    strategy = _service.generate_strategy(context)
    
    return {
        "success": True,
        "strategy": {
            "id": strategy.id,
            "overall_score": strategy.overall_score,
            "success_estimate": strategy.success_estimate,
            "primary_approach": strategy.primary_approach,
            "recommendations": [r.model_dump() for r in strategy.recommendations],
            "equipment": strategy.equipment,
            "timing": strategy.timing,
            "warnings": strategy.warnings,
            "created_at": strategy.created_at.isoformat()
        }
    }


@router.get("/quick")
async def quick_strategy(
    species: str = Query("deer", description="Target species"),
    season: str = Query("fall", description="Season"),
    time_of_day: str = Query("dawn", description="Time of day"),
    weather: str = Query("clear", description="Weather conditions"),
    terrain: str = Query("forest", description="Terrain type")
):
    """Quick strategy generation from query parameters"""
    try:
        context = HuntingContext(
            species=species,
            season=season,
            time_of_day=time_of_day,
            weather=weather,
            terrain=terrain
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    strategy = _service.generate_strategy(context)
    
    return {
        "success": True,
        "overall_score": strategy.overall_score,
        "success_estimate": strategy.success_estimate,
        "primary_approach": strategy.primary_approach,
        "top_recommendations": [r.title for r in strategy.recommendations[:3]],
        "warnings": strategy.warnings
    }


@router.post("/stand-placement")
async def get_stand_placement(context: HuntingContext):
    """Get stand/blind placement recommendations"""
    placement = _service.get_stand_placement(context)
    
    return {
        "success": True,
        "placement": placement.model_dump()
    }


@router.post("/attractant")
async def get_attractant_strategy(context: HuntingContext):
    """Get attractant usage strategy"""
    strategy = _service.get_attractant_strategy(context)
    
    return {
        "success": True,
        "attractant_strategy": strategy.model_dump()
    }


@router.get("/species/{species_name}")
async def get_species_info(species_name: str):
    """Get detailed information about a species' behavior patterns"""
    if species_name not in _service.SPECIES_PATTERNS:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Species '{species_name}' not found",
                "available_species": list(_service.SPECIES_PATTERNS.keys())
            }
        )
    
    pattern = _service.SPECIES_PATTERNS[species_name]
    
    return {
        "success": True,
        "species": species_name,
        "behavior": pattern
    }


@router.get("/seasons")
async def list_seasons():
    """List all seasons with their hunting impact"""
    return {
        "success": True,
        "seasons": [
            {"id": season, **data}
            for season, data in _service.SEASON_MODIFIERS.items()
        ]
    }


@router.get("/weather-impact")
async def list_weather_impact():
    """List weather conditions and their impact on hunting"""
    return {
        "success": True,
        "weather_conditions": [
            {"condition": weather, **data}
            for weather, data in _service.WEATHER_IMPACT.items()
        ]
    }


@router.get("/times")
async def list_hunting_times():
    """List hunting time periods"""
    return {
        "success": True,
        "times": [
            {"id": "dawn", "name": "Aube", "hours": "05:00 - 07:00", "rating": "Excellent"},
            {"id": "morning", "name": "Matin", "hours": "07:00 - 10:00", "rating": "Bon"},
            {"id": "midday", "name": "Mi-journée", "hours": "10:00 - 14:00", "rating": "Faible"},
            {"id": "afternoon", "name": "Après-midi", "hours": "14:00 - 17:00", "rating": "Moyen"},
            {"id": "dusk", "name": "Crépuscule", "hours": "17:00 - 19:00", "rating": "Excellent"},
            {"id": "night", "name": "Nuit", "hours": "19:00 - 05:00", "rating": "Variable"}
        ]
    }


@router.get("/terrains")
async def list_terrains():
    """List terrain types with hunting considerations"""
    return {
        "success": True,
        "terrains": [
            {
                "id": "forest",
                "name": "Forêt dense",
                "visibility": "Limitée",
                "approach": "Difficile",
                "species": ["deer", "moose", "bear"]
            },
            {
                "id": "field",
                "name": "Champ ouvert",
                "visibility": "Excellente",
                "approach": "Nécessite couverture",
                "species": ["deer", "turkey", "wild_boar"]
            },
            {
                "id": "edge",
                "name": "Lisière",
                "visibility": "Bonne",
                "approach": "Optimale",
                "species": ["deer", "turkey", "bear"]
            },
            {
                "id": "swamp",
                "name": "Marécage",
                "visibility": "Variable",
                "approach": "Technique",
                "species": ["moose", "deer"]
            },
            {
                "id": "mountain",
                "name": "Montagne",
                "visibility": "Excellente",
                "approach": "Physique",
                "species": ["deer", "bear"]
            }
        ]
    }
