"""
Onboarding Engine Router - V5-ULTIME Monétisation
================================================

Profilage automatique utilisateur avec intégration Plan Maître.

Étapes:
1. Profil chasseur (expérience, préférences)
2. Configuration territoire
3. Objectifs de saison
4. Intégration Plan Maître

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timezone
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/onboarding", tags=["Onboarding Engine - Monétisation"])

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

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class HuntingStyle(str, Enum):
    AMBUSH = "ambush"
    TRACKING = "tracking"
    MIXED = "mixed"

class OnboardingStep(str, Enum):
    PROFILE = "profile"
    TERRITORY = "territory"
    OBJECTIVES = "objectives"
    PLAN_MAITRE = "plan_maitre"
    COMPLETED = "completed"

class HunterProfile(BaseModel):
    experience_level: ExperienceLevel
    years_hunting: int = 0
    preferred_species: List[str] = []
    hunting_style: HuntingStyle = HuntingStyle.MIXED
    region: str = ""
    equipment_quality: str = "standard"  # basic, standard, premium

class TerritorySetup(BaseModel):
    name: str = "Mon territoire"
    location: Dict[str, float] = {}  # lat, lng
    area_hectares: float = 0
    terrain_type: str = "mixed_forest"
    has_water: bool = False

class SeasonObjectives(BaseModel):
    target_species: List[str] = []
    success_target: int = 1
    trips_planned: int = 10
    focus_area: str = "strategy"  # strategy, territory, equipment

# ==============================================
# ONBOARDING STEPS CONFIG
# ==============================================

ONBOARDING_STEPS = [
    {
        "step": OnboardingStep.PROFILE.value,
        "title": "Votre profil chasseur",
        "description": "Parlez-nous de votre expérience",
        "questions": [
            {
                "id": "experience_level",
                "type": "select",
                "label": "Niveau d'expérience",
                "options": [
                    {"value": "beginner", "label": "Débutant (< 2 ans)"},
                    {"value": "intermediate", "label": "Intermédiaire (2-5 ans)"},
                    {"value": "advanced", "label": "Avancé (5-10 ans)"},
                    {"value": "expert", "label": "Expert (10+ ans)"}
                ]
            },
            {
                "id": "preferred_species",
                "type": "multiselect",
                "label": "Espèces chassées",
                "options": [
                    {"value": "deer", "label": "Cerf de Virginie"},
                    {"value": "moose", "label": "Orignal"},
                    {"value": "bear", "label": "Ours noir"},
                    {"value": "waterfowl", "label": "Sauvagine"},
                    {"value": "small_game", "label": "Petit gibier"}
                ]
            },
            {
                "id": "hunting_style",
                "type": "select",
                "label": "Style de chasse préféré",
                "options": [
                    {"value": "ambush", "label": "Affût / Mirador"},
                    {"value": "tracking", "label": "Traque / Approche"},
                    {"value": "mixed", "label": "Mixte / Adaptable"}
                ]
            }
        ]
    },
    {
        "step": OnboardingStep.TERRITORY.value,
        "title": "Votre territoire",
        "description": "Configurez votre zone de chasse principale",
        "questions": [
            {
                "id": "territory_name",
                "type": "text",
                "label": "Nom du territoire"
            },
            {
                "id": "territory_location",
                "type": "map_picker",
                "label": "Localisation"
            },
            {
                "id": "terrain_type",
                "type": "select",
                "label": "Type de terrain",
                "options": [
                    {"value": "coniferous", "label": "Forêt de conifères"},
                    {"value": "deciduous", "label": "Forêt de feuillus"},
                    {"value": "mixed_forest", "label": "Forêt mixte"},
                    {"value": "wetland", "label": "Milieu humide"},
                    {"value": "agricultural", "label": "Zone agricole"}
                ]
            }
        ]
    },
    {
        "step": OnboardingStep.OBJECTIVES.value,
        "title": "Objectifs de saison",
        "description": "Définissez vos objectifs pour cette saison",
        "questions": [
            {
                "id": "target_species",
                "type": "multiselect",
                "label": "Espèces ciblées cette saison"
            },
            {
                "id": "success_target",
                "type": "number",
                "label": "Objectif de prises",
                "min": 1,
                "max": 10
            },
            {
                "id": "trips_planned",
                "type": "number",
                "label": "Sorties prévues",
                "min": 1,
                "max": 50
            }
        ]
    },
    {
        "step": OnboardingStep.PLAN_MAITRE.value,
        "title": "Votre Plan Maître",
        "description": "Créons votre premier plan de chasse",
        "auto_generate": True
    }
]

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def onboarding_engine_info():
    """Get onboarding engine information"""
    return {
        "module": "onboarding_engine",
        "version": "1.0.0",
        "description": "Onboarding utilisateur V5-ULTIME",
        "steps": [s["step"] for s in ONBOARDING_STEPS],
        "total_steps": len(ONBOARDING_STEPS)
    }

# ==============================================
# ONBOARDING STATUS
# ==============================================

@router.get("/status/{user_id}")
async def get_onboarding_status(user_id: str):
    """Get user's onboarding status"""
    db = get_db()
    
    status = await db.onboarding_status.find_one({"user_id": user_id}, {"_id": 0})
    
    if not status:
        status = {
            "user_id": user_id,
            "current_step": OnboardingStep.PROFILE.value,
            "completed_steps": [],
            "started_at": datetime.now(timezone.utc),
            "completed": False
        }
        await db.onboarding_status.insert_one(status)
    
    # Add step details
    current_step_config = next(
        (s for s in ONBOARDING_STEPS if s["step"] == status["current_step"]),
        ONBOARDING_STEPS[0]
    )
    
    return {
        "success": True,
        "status": status,
        "current_step_config": current_step_config,
        "total_steps": len(ONBOARDING_STEPS),
        "progress": len(status.get("completed_steps", [])) / len(ONBOARDING_STEPS) * 100
    }

# ==============================================
# STEP SUBMISSION
# ==============================================

@router.post("/steps/{user_id}/{step}")
async def submit_step(user_id: str, step: OnboardingStep, data: dict):
    """Submit onboarding step data"""
    db = get_db()
    
    # Validate step
    step_config = next((s for s in ONBOARDING_STEPS if s["step"] == step.value), None)
    if not step_config:
        raise HTTPException(status_code=400, detail="Invalid step")
    
    # Save step data
    await db.onboarding_data.update_one(
        {"user_id": user_id, "step": step.value},
        {"$set": {"data": data, "submitted_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    
    # Update status
    current_status = await db.onboarding_status.find_one({"user_id": user_id})
    completed_steps = current_status.get("completed_steps", []) if current_status else []
    
    if step.value not in completed_steps:
        completed_steps.append(step.value)
    
    # Determine next step
    step_order = [s["step"] for s in ONBOARDING_STEPS]
    current_index = step_order.index(step.value)
    
    if current_index < len(step_order) - 1:
        next_step = step_order[current_index + 1]
        is_completed = False
    else:
        next_step = OnboardingStep.COMPLETED.value
        is_completed = True
    
    # Update status
    await db.onboarding_status.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "current_step": next_step,
                "completed_steps": completed_steps,
                "completed": is_completed,
                "completed_at": datetime.now(timezone.utc) if is_completed else None
            }
        },
        upsert=True
    )
    
    # If completed, create initial Plan Maître
    if is_completed:
        await _create_initial_plan_maitre(db, user_id)
    
    return {
        "success": True,
        "step_completed": step.value,
        "next_step": next_step,
        "onboarding_completed": is_completed,
        "progress": len(completed_steps) / len(ONBOARDING_STEPS) * 100
    }

async def _create_initial_plan_maitre(db, user_id: str):
    """Create initial Plan Maître based on onboarding data"""
    
    # Get all onboarding data
    onboarding_data = await db.onboarding_data.find({"user_id": user_id}).to_list(length=10)
    
    # Extract profile and objectives
    profile_data = next((d["data"] for d in onboarding_data if d["step"] == "profile"), {})
    objectives_data = next((d["data"] for d in onboarding_data if d["step"] == "objectives"), {})
    territory_data = next((d["data"] for d in onboarding_data if d["step"] == "territory"), {})
    
    # Create plan
    plan = {
        "user_id": user_id,
        "name": f"Plan Maître Saison {datetime.now().year}",
        "season": f"{datetime.now().year}-{datetime.now().year + 1}",
        "species": objectives_data.get("target_species", profile_data.get("preferred_species", ["deer"])),
        "territory_name": territory_data.get("territory_name", "Mon territoire"),
        "current_phase": "preparation",
        "progress": 0,
        "objectives": [
            {
                "id": "obj_1",
                "title": f"Réussir {objectives_data.get('success_target', 1)} prise(s)",
                "description": "Objectif principal de la saison",
                "priority": "high",
                "progress": 0
            },
            {
                "id": "obj_2",
                "title": f"Effectuer {objectives_data.get('trips_planned', 10)} sorties",
                "description": "Sorties de chasse planifiées",
                "priority": "medium",
                "progress": 0
            },
            {
                "id": "obj_3",
                "title": "Cartographier le territoire",
                "description": "Identifier les zones clés",
                "priority": "high",
                "progress": 0
            }
        ],
        "created_at": datetime.now(timezone.utc),
        "created_from": "onboarding"
    }
    
    await db.master_plans.insert_one(plan)
    logger.info(f"Created initial Plan Maître for user {user_id}")

# ==============================================
# GET STEP CONFIG
# ==============================================

@router.get("/steps/{step}")
async def get_step_config(step: OnboardingStep):
    """Get configuration for a specific step"""
    step_config = next((s for s in ONBOARDING_STEPS if s["step"] == step.value), None)
    
    if not step_config:
        raise HTTPException(status_code=404, detail="Step not found")
    
    return {"success": True, "step": step_config}

@router.get("/steps")
async def get_all_steps():
    """Get all onboarding steps"""
    return {"success": True, "steps": ONBOARDING_STEPS}

# ==============================================
# SKIP ONBOARDING
# ==============================================

@router.post("/skip/{user_id}")
async def skip_onboarding(user_id: str):
    """Skip onboarding (mark as completed with defaults)"""
    db = get_db()
    
    await db.onboarding_status.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "current_step": OnboardingStep.COMPLETED.value,
                "completed_steps": [s["step"] for s in ONBOARDING_STEPS],
                "completed": True,
                "skipped": True,
                "completed_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": "Onboarding skipped"}
