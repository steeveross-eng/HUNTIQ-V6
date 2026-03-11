"""AI Engine Router - CORE

FastAPI router for AI-powered analysis endpoints.
Uses GPT-5.2 via Emergent LLM Key.

Version: 1.1.0
API Prefix: /api/v1/ai
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from .service import AIAnalysisService
from .models import AnalysisRequest, AdvancedAnalysisRequest
from .data.products import BIONIC_PRODUCTS, CATEGORY_KEYWORDS
from .data.references import get_scientific_references, list_sections

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])

# Initialize service
_service = AIAnalysisService()


# New request models for Q&A and comparison
class QueryRequest(BaseModel):
    """Request for AI Q&A"""
    question: str
    context: Optional[str] = None
    species: Optional[str] = None
    session_id: Optional[str] = None


class CompareRequest(BaseModel):
    """Request for AI product comparison"""
    products: List[str]
    criteria: Optional[List[str]] = None
    species: Optional[str] = "deer"


@router.get("/")
async def ai_engine_info():
    """Get AI engine information"""
    return {
        "module": "ai_engine",
        "version": "1.1.0",
        "description": "AI-powered product analysis using GPT-5.2",
        "model": "openai/gpt-5.2",
        "integration": "Emergent LLM Key",
        "supported_types": list(CATEGORY_KEYWORDS.keys()),
        "bionic_products": len(BIONIC_PRODUCTS),
        "features": [
            "Product analysis",
            "Ingredient estimation",
            "Scientific scoring",
            "Competitor comparison",
            "Advanced contextual analysis",
            "Q&A hunting assistant",
            "AI product comparison"
        ]
    }


@router.post("/analyze")
async def analyze_product(request: AnalysisRequest):
    """
    Analyze a hunting attractant product using AI.
    
    Returns complete analysis with scoring, comparison, and recommendations.
    """
    if not request.product_name or len(request.product_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Product name must be at least 2 characters")
    
    try:
        report = await _service.analyze_product(
            product_name=request.product_name,
            product_type=request.product_type
        )
        
        return {
            "success": True,
            "report": {
                "id": report.id,
                "product_name": report.product_name,
                "technical_sheet": report.technical_sheet.model_dump(),
                "scientific_analysis": report.scientific_analysis.model_dump(),
                "scoring": report.scoring,
                "comparison": report.comparison.model_dump() if report.comparison else None,
                "price_analysis": report.price_analysis,
                "recommendations": report.recommendations,
                "bionic_arguments": report.bionic_arguments,
                "conclusion": report.conclusion,
                "scientific_references": report.scientific_references,
                "created_at": report.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/advanced")
async def analyze_advanced(request: AdvancedAnalysisRequest):
    """
    Advanced AI analysis with hunting context.
    
    Takes into account species, season, weather, and terrain.
    """
    try:
        result = await _service.analyze_advanced(
            product_name=request.product_name,
            species=request.species,
            season=request.season,
            weather=request.weather,
            terrain=request.terrain
        )
        
        return {
            "success": True,
            "analysis": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced analysis failed: {str(e)}")


@router.get("/references")
async def get_references():
    """Get all scientific references"""
    references = get_scientific_references()
    
    return {
        "success": True,
        "total_sections": len(references),
        "references": references
    }


@router.get("/references/{section_id}")
async def get_reference_section(section_id: str):
    """Get references for a specific section"""
    from .data.references import get_references_by_section
    
    section = get_references_by_section(section_id)
    
    if not section:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Section '{section_id}' not found",
                "available_sections": list_sections()
            }
        )
    
    return {
        "success": True,
        "section": section
    }


@router.get("/products/bionic")
async def list_bionic_products():
    """List all BIONIC products"""
    return {
        "success": True,
        "count": len(BIONIC_PRODUCTS),
        "products": [
            {
                "type": ptype,
                "name": data["name"],
                "price": data["price"],
                "score": data["score"],
                "attraction_days": data["attraction_days"],
                "buy_link": data["buy_link"]
            }
            for ptype, data in BIONIC_PRODUCTS.items()
        ]
    }


@router.get("/products/bionic/{product_type}")
async def get_bionic_product(product_type: str):
    """Get a specific BIONIC product"""
    from .data.products import get_bionic_product as get_product
    
    product = get_product(product_type)
    
    if product_type not in BIONIC_PRODUCTS:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"BIONIC product type '{product_type}' not found",
                "available_types": list(BIONIC_PRODUCTS.keys())
            }
        )
    
    return {
        "success": True,
        "product": {
            "type": product_type,
            **product
        }
    }


@router.get("/types")
async def list_product_types():
    """List all supported product types with detection keywords"""
    return {
        "success": True,
        "types": [
            {
                "type": ptype,
                "keywords": keywords,
                "has_bionic": ptype in BIONIC_PRODUCTS
            }
            for ptype, keywords in CATEGORY_KEYWORDS.items()
        ]
    }


@router.get("/species")
async def list_species():
    """List supported species for analysis"""
    return {
        "success": True,
        "species": [
            {"id": "deer", "name": "Cerf / Chevreuil", "icon": "🦌"},
            {"id": "moose", "name": "Orignal", "icon": "🫎"},
            {"id": "bear", "name": "Ours", "icon": "🐻"},
            {"id": "wild_boar", "name": "Sanglier", "icon": "🐗"},
            {"id": "turkey", "name": "Dindon sauvage", "icon": "🦃"}
        ]
    }


@router.get("/seasons")
async def list_seasons():
    """List seasons for contextual analysis"""
    return {
        "success": True,
        "seasons": [
            {"id": "spring", "name": "Printemps", "icon": "🌸"},
            {"id": "summer", "name": "Été", "icon": "☀️"},
            {"id": "fall", "name": "Automne / Rut", "icon": "🍂"},
            {"id": "winter", "name": "Hiver", "icon": "❄️"}
        ]
    }


@router.get("/weather")
async def list_weather_conditions():
    """List weather conditions for analysis"""
    return {
        "success": True,
        "conditions": [
            {"id": "cold", "name": "Froid", "icon": "🥶"},
            {"id": "normal", "name": "Normal", "icon": "😊"},
            {"id": "hot", "name": "Chaud", "icon": "🥵"},
            {"id": "rain", "name": "Pluie", "icon": "🌧️"},
            {"id": "snow", "name": "Neige", "icon": "🌨️"}
        ]
    }


@router.get("/terrain")
async def list_terrain_types():
    """List terrain types for analysis"""
    return {
        "success": True,
        "terrains": [
            {"id": "forest", "name": "Forêt", "icon": "🌲"},
            {"id": "field", "name": "Champ / Clairière", "icon": "🌾"},
            {"id": "marsh", "name": "Marais / Humide", "icon": "🏞️"},
            {"id": "mountain", "name": "Montagne", "icon": "⛰️"}
        ]
    }



# ==========================================
# NEW GPT-5.2 ENDPOINTS (P1)
# ==========================================

@router.post("/query")
async def query_ai(request: QueryRequest):
    """
    Ask a question to the AI hunting assistant.
    
    Uses GPT-5.2 to answer questions about:
    - Hunting techniques and strategies
    - Product recommendations
    - Wildlife behavior
    - Regulations and best practices
    """
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters")
    
    try:
        result = await _service.query_assistant(
            question=request.question,
            context=request.context,
            species=request.species,
            session_id=request.session_id
        )
        
        return {
            "success": True,
            "question": request.question,
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "related_products": result.get("related_products", []),
            "session_id": result.get("session_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/compare")
async def compare_products_ai(request: CompareRequest):
    """
    Compare multiple products using AI analysis.
    
    Returns:
    - Side-by-side comparison
    - Winner for each criterion
    - Overall recommendation
    - Best value analysis
    """
    if not request.products or len(request.products) < 2:
        raise HTTPException(status_code=400, detail="At least 2 products required for comparison")
    
    if len(request.products) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 products for comparison")
    
    try:
        result = await _service.compare_products_ai(
            products=request.products,
            criteria=request.criteria,
            species=request.species
        )
        
        return {
            "success": True,
            "products_compared": request.products,
            "comparison": result["comparison"],
            "winner": result["winner"],
            "recommendation": result["recommendation"],
            "best_value": result.get("best_value"),
            "detailed_analysis": result.get("detailed_analysis", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/suggestions")
async def get_suggestions(
    species: str = Query("deer", description="Target species"),
    season: str = Query("fall", description="Hunting season"),
    budget: Optional[float] = Query(None, description="Maximum budget")
):
    """
    Get AI-powered product suggestions based on context.
    
    Returns personalized recommendations for the given hunting context.
    """
    try:
        result = await _service.get_suggestions(
            species=species,
            season=season,
            budget=budget
        )
        
        return {
            "success": True,
            "context": {
                "species": species,
                "season": season,
                "budget": budget
            },
            "suggestions": result["suggestions"],
            "top_pick": result.get("top_pick"),
            "reasoning": result.get("reasoning")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")
