"""Scoring Engine Router - CORE

FastAPI router for scoring-related endpoints.

Version: 1.0.0
API Prefix: /api/v1/scoring
"""

from fastapi import APIRouter, HTTPException
from .service import ScoringService
from .models import ScoreRequest
from .data.criteria import SCORING_CRITERIA, list_criteria

router = APIRouter(prefix="/api/v1/scoring", tags=["Scoring Engine"])

# Initialize service
_service = ScoringService()


@router.get("/")
async def scoring_engine_info():
    """Get scoring engine information"""
    return {
        "module": "scoring_engine",
        "version": "1.0.0",
        "description": "Scientific scoring for hunting attractants (13 weighted criteria)",
        "total_criteria": len(SCORING_CRITERIA),
        "max_score": 10,
        "pastilles": ["green (≥7.5)", "yellow (≥5.0)", "red (<5.0)"]
    }


@router.get("/criteria")
async def list_scoring_criteria():
    """
    List all 13 scoring criteria with weights.
    
    Returns complete scientific criteria used for attractant evaluation.
    """
    criteria = list_criteria()
    total_weight = sum(c["weight"] for c in criteria)
    
    return {
        "success": True,
        "total_criteria": len(criteria),
        "total_weight": total_weight,
        "criteria": criteria,
        "categories": {
            "performance": ["attraction_days", "natural_palatability", "olfactory_power", "persistence"],
            "composition": ["nutrition", "behavioral_compounds", "ingredient_purity"],
            "durability": ["rainproof", "feed_proof", "certified", "physical_resistance"],
            "long_term": ["loyalty", "chemical_stability"]
        }
    }


@router.get("/criteria/{criterion_name}")
async def get_criterion_detail(criterion_name: str):
    """Get detailed information about a specific criterion"""
    criterion = SCORING_CRITERIA.get(criterion_name)
    
    if not criterion:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Criterion '{criterion_name}' not found",
                "available_criteria": list(SCORING_CRITERIA.keys())
            }
        )
    
    return {
        "success": True,
        "criterion": {
            "name": criterion_name,
            **criterion
        }
    }


@router.post("/calculate", response_model=None)
async def calculate_score(request: ScoreRequest):
    """
    Calculate the scientific score for a product.
    
    Uses the 13 weighted criteria algorithm to produce a final score.
    """
    # Convert request to analysis data format
    analysis_data = {
        "attraction_days": request.attraction_days,
        "natural_palatability": request.natural_palatability,
        "olfactory_power": request.olfactory_power,
        "persistence": request.persistence,
        "nutrition": request.nutrition,
        "behavioral_compounds": request.behavioral_compounds,
        "rainproof": request.rainproof,
        "feed_proof": request.feed_proof,
        "certified": request.certified,
        "physical_resistance": request.physical_resistance,
        "ingredient_purity": request.ingredient_purity,
        "loyalty": request.loyalty,
        "chemical_stability": request.chemical_stability
    }
    
    result = _service.calculate_score(analysis_data)
    
    return {
        "success": True,
        "score": result.total_score,
        "pastille": result.pastille,
        "pastille_label": result.pastille_label,
        "breakdown": {
            "criteria_scores": result.criteria_scores,
            "weighted_scores": result.weighted_scores
        }
    }


@router.post("/quick-score")
async def quick_score(
    rainproof: bool = False,
    feed_proof: bool = True,
    certified: bool = False,
    attraction_days: int = 10,
    olfactory_power: float = 7.0
):
    """
    Quick score calculation based on key criteria only.
    
    Useful for fast product comparisons without full analysis.
    """
    score = _service.calculate_quick_score(
        rainproof=rainproof,
        feed_proof=feed_proof,
        certified=certified,
        attraction_days=attraction_days,
        olfactory_power=olfactory_power
    )
    
    # Determine pastille
    if score >= 7.5:
        pastille = "green"
    elif score >= 5.0:
        pastille = "yellow"
    else:
        pastille = "red"
    
    return {
        "success": True,
        "quick_score": score,
        "pastille": pastille,
        "note": "This is an estimated score based on key criteria only"
    }


@router.get("/weights")
async def get_weights():
    """Get the weight distribution for all criteria"""
    weights = _service.get_criteria_weights()
    total = sum(weights.values())
    
    # Calculate percentages
    percentages = {k: round(v / total * 100, 1) for k, v in weights.items()}
    
    return {
        "success": True,
        "weights": weights,
        "percentages": percentages,
        "total_weight": total
    }
