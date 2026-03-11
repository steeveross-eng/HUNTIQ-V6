"""
Tutorial Engine Router - V5-ULTIME Monétisation
==============================================

Tutoriels dynamiques contextuels.

Types:
- Feature tutorials (comment utiliser)
- Workflow tutorials (flux complets)
- Premium feature previews
- Tips & tricks

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tutorials", tags=["Tutorial Engine - Monétisation"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class TutorialType(str, Enum):
    FEATURE = "feature"
    WORKFLOW = "workflow"
    PREMIUM_PREVIEW = "premium_preview"
    TIP = "tip"

class TutorialTrigger(str, Enum):
    FIRST_VISIT = "first_visit"
    FEATURE_ACCESS = "feature_access"
    MANUAL = "manual"
    CONTEXTUAL = "contextual"

# ==============================================
# TUTORIALS DATABASE
# ==============================================

TUTORIALS = [
    # Feature tutorials
    {
        "id": "tut_strategy_generation",
        "type": TutorialType.FEATURE.value,
        "trigger": TutorialTrigger.FIRST_VISIT.value,
        "feature": "strategy",
        "title": "Génération de Stratégies",
        "description": "Apprenez à générer des stratégies de chasse optimales",
        "tier_required": "free",
        "steps": [
            {
                "order": 1,
                "title": "Sélectionnez votre espèce",
                "content": "Choisissez l'espèce que vous chassez pour des recommandations adaptées.",
                "target": "[data-testid='species-selector']",
                "action": "click"
            },
            {
                "order": 2,
                "title": "Vérifiez votre position",
                "content": "Assurez-vous que votre localisation est correcte pour des données météo précises.",
                "target": "[data-testid='location-indicator']",
                "action": "highlight"
            },
            {
                "order": 3,
                "title": "Lancez la génération",
                "content": "Cliquez sur 'Générer' pour obtenir votre stratégie personnalisée.",
                "target": "[data-testid='generate-strategy-btn']",
                "action": "click"
            }
        ]
    },
    {
        "id": "tut_plan_maitre",
        "type": TutorialType.WORKFLOW.value,
        "trigger": TutorialTrigger.FIRST_VISIT.value,
        "feature": "plan_maitre",
        "title": "Le Plan Maître",
        "description": "Maîtrisez la planification de votre saison de chasse",
        "tier_required": "free",
        "steps": [
            {
                "order": 1,
                "title": "Vue d'ensemble",
                "content": "Le Plan Maître vous aide à planifier toute votre saison de chasse.",
                "target": "[data-testid='plan-maitre-dashboard']",
                "action": "highlight"
            },
            {
                "order": 2,
                "title": "Définissez vos objectifs",
                "content": "Ajoutez des objectifs concrets pour suivre votre progression.",
                "target": "[data-testid='add-objective-btn']",
                "action": "click"
            },
            {
                "order": 3,
                "title": "Suivez les phases",
                "content": "Progressez à travers les phases: Préparation → Exécution → Bilan.",
                "target": "[data-testid='phase-timeline']",
                "action": "highlight"
            }
        ]
    },
    {
        "id": "tut_territory",
        "type": TutorialType.FEATURE.value,
        "trigger": TutorialTrigger.FIRST_VISIT.value,
        "feature": "territory",
        "title": "Gestion du Territoire",
        "description": "Configurez et analysez votre territoire de chasse",
        "tier_required": "free",
        "steps": [
            {
                "order": 1,
                "title": "Créez une zone",
                "content": "Délimitez vos zones de chasse sur la carte.",
                "target": "[data-testid='create-zone-btn']",
                "action": "click"
            },
            {
                "order": 2,
                "title": "Ajoutez des waypoints",
                "content": "Marquez les points importants: miradors, sentiers, points d'eau.",
                "target": "[data-testid='add-waypoint-btn']",
                "action": "click"
            }
        ]
    },
    # Premium previews
    {
        "id": "tut_live_heading_preview",
        "type": TutorialType.PREMIUM_PREVIEW.value,
        "trigger": TutorialTrigger.FEATURE_ACCESS.value,
        "feature": "live_heading",
        "title": "Live Heading View",
        "description": "Découvrez la navigation immersive Premium",
        "tier_required": "premium",
        "steps": [
            {
                "order": 1,
                "title": "Navigation en temps réel",
                "content": "Suivez votre position avec une vue boussole immersive.",
                "media": {"type": "video", "url": "/tutorials/live_heading_demo.mp4"}
            },
            {
                "order": 2,
                "title": "Indicateurs de vent",
                "content": "Visualisez la direction du vent par rapport à votre position.",
                "media": {"type": "image", "url": "/tutorials/wind_indicator.png"}
            }
        ],
        "cta": {
            "text": "Débloquer avec Premium",
            "action": "upgrade",
            "tier": "premium"
        }
    },
    {
        "id": "tut_advanced_layers_preview",
        "type": TutorialType.PREMIUM_PREVIEW.value,
        "trigger": TutorialTrigger.FEATURE_ACCESS.value,
        "feature": "advanced_layers",
        "title": "Couches Avancées",
        "description": "Analyses géospatiales et comportementales",
        "tier_required": "premium",
        "steps": [
            {
                "order": 1,
                "title": "Couche 3D",
                "content": "Visualisez le terrain en 3D pour planifier vos approches.",
                "media": {"type": "image", "url": "/tutorials/3d_layer.png"}
            },
            {
                "order": 2,
                "title": "Simulation comportementale",
                "content": "Simulez les déplacements du gibier selon l'heure et la météo.",
                "media": {"type": "video", "url": "/tutorials/behavior_sim.mp4"}
            }
        ],
        "cta": {
            "text": "Activer Premium",
            "action": "upgrade",
            "tier": "premium"
        }
    },
    # Tips
    {
        "id": "tip_wind_direction",
        "type": TutorialType.TIP.value,
        "trigger": TutorialTrigger.CONTEXTUAL.value,
        "feature": "weather",
        "title": "Conseil du jour",
        "description": "L'importance du vent",
        "tier_required": "free",
        "content": "Approchez toujours face au vent pour éviter que votre odeur ne vous trahisse. Vérifiez la météo avant chaque sortie!",
        "icon": "wind"
    },
    {
        "id": "tip_golden_hours",
        "type": TutorialType.TIP.value,
        "trigger": TutorialTrigger.CONTEXTUAL.value,
        "feature": "timing",
        "title": "Heures d'or",
        "description": "Maximisez vos chances",
        "tier_required": "free",
        "content": "Les meilleures périodes d'activité du gibier sont généralement l'aube (6h-9h) et le crépuscule (16h-18h30).",
        "icon": "sunrise"
    }
]

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def tutorial_engine_info():
    """Get tutorial engine information"""
    return {
        "module": "tutorial_engine",
        "version": "1.0.0",
        "description": "Tutoriels dynamiques V5-ULTIME",
        "types": [t.value for t in TutorialType],
        "triggers": [t.value for t in TutorialTrigger],
        "total_tutorials": len(TUTORIALS)
    }

# ==============================================
# GET TUTORIALS
# ==============================================

@router.get("/list")
async def list_tutorials(
    type: Optional[TutorialType] = None,
    feature: Optional[str] = None,
    tier: str = Query("free")
):
    """List available tutorials"""
    filtered = TUTORIALS
    
    if type:
        filtered = [t for t in filtered if t["type"] == type.value]
    
    if feature:
        filtered = [t for t in filtered if t.get("feature") == feature]
    
    # Filter by tier access
    tier_order = ["free", "premium", "pro"]
    user_tier_index = tier_order.index(tier) if tier in tier_order else 0
    
    accessible = []
    for tut in filtered:
        tut_tier = tut.get("tier_required", "free")
        tut_tier_index = tier_order.index(tut_tier) if tut_tier in tier_order else 0
        
        if user_tier_index >= tut_tier_index:
            accessible.append({**tut, "accessible": True})
        else:
            accessible.append({**tut, "accessible": False, "requires_upgrade": True})
    
    return {"success": True, "tutorials": accessible}

@router.get("/{tutorial_id}")
async def get_tutorial(tutorial_id: str):
    """Get specific tutorial"""
    tutorial = next((t for t in TUTORIALS if t["id"] == tutorial_id), None)
    
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    return {"success": True, "tutorial": tutorial}

# ==============================================
# USER PROGRESS
# ==============================================

@router.get("/progress/{user_id}")
async def get_user_tutorial_progress(user_id: str):
    """Get user's tutorial progress"""
    db = get_db()
    
    progress = await db.tutorial_progress.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(length=100)
    
    completed_ids = [p["tutorial_id"] for p in progress if p.get("completed")]
    
    return {
        "success": True,
        "completed_count": len(completed_ids),
        "total_tutorials": len(TUTORIALS),
        "completed_tutorials": completed_ids,
        "progress": progress
    }

@router.post("/progress/{user_id}/{tutorial_id}")
async def update_tutorial_progress(
    user_id: str, 
    tutorial_id: str,
    step_completed: Optional[int] = None,
    completed: bool = False
):
    """Update user's progress on a tutorial"""
    db = get_db()
    
    tutorial = next((t for t in TUTORIALS if t["id"] == tutorial_id), None)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    total_steps = len(tutorial.get("steps", []))
    
    update_data = {
        "user_id": user_id,
        "tutorial_id": tutorial_id,
        "updated_at": datetime.now(timezone.utc)
    }
    
    if step_completed is not None:
        update_data["current_step"] = step_completed
        if step_completed >= total_steps:
            update_data["completed"] = True
            update_data["completed_at"] = datetime.now(timezone.utc)
    
    if completed:
        update_data["completed"] = True
        update_data["completed_at"] = datetime.now(timezone.utc)
    
    await db.tutorial_progress.update_one(
        {"user_id": user_id, "tutorial_id": tutorial_id},
        {"$set": update_data},
        upsert=True
    )
    
    return {"success": True, "progress": update_data}

@router.post("/skip/{user_id}/{tutorial_id}")
async def skip_tutorial(user_id: str, tutorial_id: str):
    """Mark tutorial as skipped"""
    db = get_db()
    
    await db.tutorial_progress.update_one(
        {"user_id": user_id, "tutorial_id": tutorial_id},
        {
            "$set": {
                "skipped": True,
                "skipped_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": "Tutorial skipped"}

# ==============================================
# CONTEXTUAL TUTORIALS
# ==============================================

@router.get("/contextual/{feature}")
async def get_contextual_tutorial(feature: str, user_id: Optional[str] = None):
    """Get contextual tutorial for a feature"""
    db = get_db()
    
    # Find relevant tutorials
    relevant = [
        t for t in TUTORIALS 
        if t.get("feature") == feature and t["trigger"] in [TutorialTrigger.FIRST_VISIT.value, TutorialTrigger.CONTEXTUAL.value]
    ]
    
    if not relevant:
        return {"success": True, "tutorial": None, "reason": "No tutorial for feature"}
    
    # Check if user has seen it
    if user_id:
        seen = await db.tutorial_progress.find_one({
            "user_id": user_id,
            "tutorial_id": relevant[0]["id"]
        })
        
        if seen and (seen.get("completed") or seen.get("skipped")):
            return {"success": True, "tutorial": None, "reason": "Already completed or skipped"}
    
    return {"success": True, "tutorial": relevant[0]}

# ==============================================
# DAILY TIPS
# ==============================================

@router.get("/tip/daily")
async def get_daily_tip():
    """Get a random daily tip"""
    import random
    
    tips = [t for t in TUTORIALS if t["type"] == TutorialType.TIP.value]
    
    if not tips:
        return {"success": True, "tip": None}
    
    # Use date as seed for consistent daily tip
    today = datetime.now(timezone.utc).date()
    random.seed(today.toordinal())
    tip = random.choice(tips)
    
    return {"success": True, "tip": tip}
