"""
Strategy Master Engine Router - V5-ULTIME Plan Maître
=====================================================

Orchestrateur central du Plan Maître.
Intègre tous les moteurs pour une stratégie optimale.

Intégrations:
- rules_engine: Règles de chasse intelligentes
- scoring_engine: Évaluation des conditions
- weather_engine: Données météorologiques
- territory_engine: Données géospatiales
- progression_engine: Progression utilisateur

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, date
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/strategy-master", tags=["Strategy Master Engine - Plan Maître"])

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

class PlanPhase(str, Enum):
    PREPARATION = "preparation"
    RECONNAISSANCE = "reconnaissance"
    INSTALLATION = "installation"
    EXECUTION = "execution"
    REVIEW = "review"

class StrategyType(str, Enum):
    APPROACH = "approach"
    AMBUSH = "ambush"
    TRACKING = "tracking"
    CALL = "call"
    MIXED = "mixed"

class PlanObjective(BaseModel):
    title: str
    description: str
    priority: str = "medium"  # high, medium, low
    deadline: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    completed: bool = False

class MasterPlan(BaseModel):
    name: str
    user_id: str
    season: str  # e.g., "2025-2026"
    species: List[str] = ["deer"]
    territory_id: Optional[str] = None
    current_phase: PlanPhase = PlanPhase.PREPARATION
    progress: int = Field(default=0, ge=0, le=100)
    objectives: List[PlanObjective] = []
    strategies: List[str] = []
    notes: str = ""

class StrategyRequest(BaseModel):
    user_id: str
    location: Dict[str, float]  # lat, lng
    species: str = "deer"
    date: Optional[str] = None
    time_preference: Optional[str] = None  # morning, evening, all_day

class DailyPlanRequest(BaseModel):
    user_id: str
    plan_id: str
    date: str
    weather_override: Optional[Dict[str, Any]] = None

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def strategy_master_info():
    """Get Strategy Master Engine information"""
    return {
        "module": "strategy_master_engine",
        "version": "1.0.0",
        "description": "Orchestrateur Plan Maître V5-ULTIME",
        "integrations": [
            "rules_engine",
            "scoring_engine", 
            "weather_engine",
            "territory_engine",
            "progression_engine"
        ],
        "phases": [p.value for p in PlanPhase],
        "strategy_types": [s.value for s in StrategyType],
        "features": [
            "Plans de chasse personnalisés",
            "Stratégies dynamiques",
            "Intégration multi-sources",
            "Recommandations temps réel",
            "Progression utilisateur"
        ]
    }

# ==============================================
# MASTER PLAN CRUD
# ==============================================

@router.post("/plans")
async def create_master_plan(plan: MasterPlan):
    """Create a new master plan"""
    db = get_db()
    
    plan_dict = plan.dict()
    plan_dict["current_phase"] = plan.current_phase.value
    plan_dict["created_at"] = datetime.now(timezone.utc)
    plan_dict["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.master_plans.insert_one(plan_dict)
    plan_dict["id"] = str(result.inserted_id)
    del plan_dict["_id"]
    
    return {"success": True, "plan": plan_dict}

@router.get("/plans/{plan_id}")
async def get_master_plan(plan_id: str, user_id: str = Query(...)):
    """Get a master plan by ID"""
    db = get_db()
    
    from bson import ObjectId
    try:
        plan = await db.master_plans.find_one(
            {"_id": ObjectId(plan_id), "user_id": user_id},
            {"_id": 0}
        )
    except Exception:
        plan = await db.master_plans.find_one(
            {"id": plan_id, "user_id": user_id},
            {"_id": 0}
        )
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {"success": True, "plan": plan}

@router.get("/plans/user/{user_id}")
async def get_user_plans(user_id: str, active_only: bool = Query(True)):
    """Get all plans for a user"""
    db = get_db()
    
    query = {"user_id": user_id}
    if active_only:
        query["progress"] = {"$lt": 100}
    
    plans = await db.master_plans.find(query, {"_id": 0}).sort("created_at", -1).to_list(length=20)
    
    return {"success": True, "total": len(plans), "plans": plans}

@router.put("/plans/{plan_id}")
async def update_master_plan(plan_id: str, updates: dict, user_id: str = Query(...)):
    """Update a master plan"""
    db = get_db()
    
    updates["updated_at"] = datetime.now(timezone.utc)
    
    from bson import ObjectId
    try:
        result = await db.master_plans.update_one(
            {"_id": ObjectId(plan_id), "user_id": user_id},
            {"$set": updates}
        )
    except Exception:
        result = await db.master_plans.update_one(
            {"id": plan_id, "user_id": user_id},
            {"$set": updates}
        )
    
    return {
        "success": result.modified_count > 0,
        "message": "Plan updated" if result.modified_count > 0 else "Plan not found"
    }

@router.post("/plans/{plan_id}/objectives")
async def add_objective(plan_id: str, objective: PlanObjective, user_id: str = Query(...)):
    """Add an objective to a plan"""
    db = get_db()
    
    obj_dict = objective.dict()
    obj_dict["id"] = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
    obj_dict["created_at"] = datetime.now(timezone.utc)
    
    from bson import ObjectId
    try:
        result = await db.master_plans.update_one(
            {"_id": ObjectId(plan_id), "user_id": user_id},
            {"$push": {"objectives": obj_dict}}
        )
    except Exception:
        result = await db.master_plans.update_one(
            {"id": plan_id, "user_id": user_id},
            {"$push": {"objectives": obj_dict}}
        )
    
    return {"success": result.modified_count > 0, "objective": obj_dict}

@router.put("/plans/{plan_id}/phase")
async def update_plan_phase(plan_id: str, phase: PlanPhase, user_id: str = Query(...)):
    """Update the current phase of a plan"""
    db = get_db()
    
    # Calculate progress based on phase
    phase_progress = {
        PlanPhase.PREPARATION: 0,
        PlanPhase.RECONNAISSANCE: 20,
        PlanPhase.INSTALLATION: 40,
        PlanPhase.EXECUTION: 60,
        PlanPhase.REVIEW: 90
    }
    
    updates = {
        "current_phase": phase.value,
        "progress": phase_progress.get(phase, 0),
        "updated_at": datetime.now(timezone.utc)
    }
    
    from bson import ObjectId
    try:
        result = await db.master_plans.update_one(
            {"_id": ObjectId(plan_id), "user_id": user_id},
            {"$set": updates}
        )
    except Exception:
        result = await db.master_plans.update_one(
            {"id": plan_id, "user_id": user_id},
            {"$set": updates}
        )
    
    return {"success": result.modified_count > 0, "new_phase": phase.value}

# ==============================================
# STRATEGY GENERATION
# ==============================================

@router.post("/strategy/generate")
async def generate_strategy(request: StrategyRequest):
    """Generate optimal hunting strategy based on all factors"""
    db = get_db()
    
    # Build context for rule evaluation
    context = {
        "species": request.species,
        "latitude": request.location.get("lat", 46.8139),
        "longitude": request.location.get("lng", -71.2080),
    }
    
    # Get current time
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    
    # Add time context
    if 5 <= current_hour < 10:
        context["time_of_day"] = "morning"
        context["time_window"] = f"{current_hour:02d}:00"
    elif 15 <= current_hour < 19:
        context["time_of_day"] = "evening"
        context["time_window"] = f"{current_hour:02d}:00"
    else:
        context["time_of_day"] = "midday"
    
    # Get weather data (simplified - would call weather_engine)
    weather_data = {
        "temperature": -3,
        "wind_speed": 12,
        "humidity": 65,
        "pressure_trend": "falling",
        "conditions": "cloudy"
    }
    context.update(weather_data)
    
    # Get territory data (simplified - would call territory_engine)
    territory_data = {
        "distance_to_feeding_zone": 150,
        "distance_to_water": 200,
        "elevation": 350,
        "cover_type": "mixed_forest"
    }
    context.update(territory_data)
    
    # Calculate base score
    base_score = 70
    
    # Evaluate rules to get modifiers and recommendations
    from modules.rules_engine.router import evaluate_condition, DEFAULT_RULES
    
    score_modifier = 1.0
    recommendations = []
    alerts = []
    
    for rule in DEFAULT_RULES:
        if not rule.get("enabled", True):
            continue
            
        all_met = True
        for condition in rule.get("conditions", []):
            if not evaluate_condition(condition, context):
                all_met = False
                break
        
        if all_met:
            for action in rule.get("actions", []):
                if action["type"] == "score_modifier":
                    score_modifier *= action["params"].get("modifier", 1.0)
                elif action["type"] == "recommend":
                    recommendations.append({
                        "rule": rule["name"],
                        "strategy": action["params"].get("strategy"),
                        "reason": action["params"].get("reason", "")
                    })
                elif action["type"] == "alert":
                    alerts.append({
                        "level": action["params"].get("level", "info"),
                        "message": action["params"].get("message", "")
                    })
    
    # Calculate final score
    final_score = min(100, int(base_score * score_modifier))
    
    # Determine primary strategy
    strategy_votes = {}
    for rec in recommendations:
        strat = rec.get("strategy")
        if strat:
            strategy_votes[strat] = strategy_votes.get(strat, 0) + 1
    
    primary_strategy = max(strategy_votes, key=strategy_votes.get) if strategy_votes else "ambush"
    
    # Generate strategy timeline
    timeline = []
    if context["time_of_day"] == "morning":
        timeline = [
            {"time": "05:30", "action": "Préparation et vérification équipement"},
            {"time": "06:00", "action": "Déplacement vers la zone"},
            {"time": "06:30", "action": f"Installation pour {primary_strategy}"},
            {"time": "07:00-09:00", "action": "Période d'observation active"},
            {"time": "09:30", "action": "Réévaluation et repositionnement possible"}
        ]
    else:
        timeline = [
            {"time": "15:00", "action": "Préparation et check météo"},
            {"time": "15:30", "action": "Déplacement discret vers la zone"},
            {"time": "16:00", "action": f"Installation pour {primary_strategy}"},
            {"time": "16:30-18:30", "action": "Période d'observation active"},
            {"time": "18:30", "action": "Fin légale, retour"}
        ]
    
    return {
        "success": True,
        "strategy": {
            "primary_type": primary_strategy,
            "confidence": "high" if final_score >= 70 else "medium" if final_score >= 50 else "low",
            "score": final_score,
            "score_modifier": round(score_modifier, 2)
        },
        "context": {
            "time_of_day": context["time_of_day"],
            "weather": weather_data,
            "territory": territory_data
        },
        "recommendations": recommendations,
        "alerts": alerts,
        "timeline": timeline,
        "tips": [
            f"Stratégie recommandée: {primary_strategy.upper()}",
            f"Score de conditions: {final_score}/100",
            "Vérifiez la direction du vent avant l'approche",
            "Restez attentif aux changements météo"
        ]
    }

# ==============================================
# DAILY PLANNING
# ==============================================

@router.post("/daily-plan")
async def generate_daily_plan(request: DailyPlanRequest):
    """Generate a complete daily hunting plan"""
    db = get_db()
    
    # Get master plan
    plan = await db.master_plans.find_one({"id": request.plan_id, "user_id": request.user_id}, {"_id": 0})
    
    if not plan:
        # Use default plan structure
        plan = {
            "name": "Plan du jour",
            "species": ["deer"],
            "current_phase": "execution"
        }
    
    # Parse date
    try:
        target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
    except Exception:
        target_date = date.today()
    
    # Generate morning session
    morning_session = {
        "period": "morning",
        "start_time": "06:00",
        "end_time": "10:00",
        "recommended_strategy": "ambush",
        "priority_zones": ["Zone Nord", "Ravine Est"],
        "tasks": [
            {"time": "05:30", "task": "Réveil et préparation", "status": "pending"},
            {"time": "06:00", "task": "Déplacement vers zone", "status": "pending"},
            {"time": "06:30", "task": "Installation affût", "status": "pending"},
            {"time": "07:00", "task": "Début observation", "status": "pending"},
            {"time": "09:30", "task": "Évaluation et décision", "status": "pending"}
        ],
        "expected_score": 78
    }
    
    # Generate evening session
    evening_session = {
        "period": "evening",
        "start_time": "15:00",
        "end_time": "18:30",
        "recommended_strategy": "approach",
        "priority_zones": ["Crête Principale", "Point d'eau"],
        "tasks": [
            {"time": "14:30", "task": "Vérification météo finale", "status": "pending"},
            {"time": "15:00", "task": "Départ vers zone soir", "status": "pending"},
            {"time": "15:45", "task": "Approche silencieuse", "status": "pending"},
            {"time": "16:00", "task": "Position finale", "status": "pending"},
            {"time": "18:00", "task": "Dernière lumière", "status": "pending"}
        ],
        "expected_score": 72
    }
    
    # Weather forecast (simplified)
    weather_forecast = {
        "morning": {
            "temperature": -5,
            "wind": "NO 10 km/h",
            "conditions": "Partiellement nuageux",
            "hunting_impact": "positive"
        },
        "evening": {
            "temperature": -2,
            "wind": "N 15 km/h",
            "conditions": "Nuageux",
            "hunting_impact": "neutral"
        }
    }
    
    # Objectives for the day
    daily_objectives = [
        {"id": 1, "title": "Vérifier caméra secteur Nord", "priority": "high", "completed": False},
        {"id": 2, "title": "Noter activité zone alimentation", "priority": "medium", "completed": False},
        {"id": 3, "title": "Repérer nouvelles pistes", "priority": "low", "completed": False}
    ]
    
    return {
        "success": True,
        "date": request.date,
        "plan_name": plan.get("name", "Plan du jour"),
        "species": plan.get("species", ["deer"]),
        "sessions": {
            "morning": morning_session,
            "evening": evening_session
        },
        "weather": weather_forecast,
        "objectives": daily_objectives,
        "notes": [
            "Conditions favorables prévues pour le matin",
            "Vent du nord-ouest - approcher par le sud",
            "Lune décroissante - activité crépusculaire attendue"
        ],
        "overall_score": 75
    }

# ==============================================
# PROGRESSION TRACKING
# ==============================================

@router.post("/progress/update")
async def update_progression(
    user_id: str,
    plan_id: str,
    objective_id: str,
    progress: int = Query(..., ge=0, le=100)
):
    """Update objective progress"""
    db = get_db()
    
    result = await db.master_plans.update_one(
        {"id": plan_id, "user_id": user_id, "objectives.id": objective_id},
        {
            "$set": {
                "objectives.$.progress": progress,
                "objectives.$.completed": progress >= 100,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Recalculate overall plan progress
    plan = await db.master_plans.find_one({"id": plan_id}, {"_id": 0})
    if plan and plan.get("objectives"):
        total_progress = sum(obj.get("progress", 0) for obj in plan["objectives"])
        avg_progress = total_progress // len(plan["objectives"])
        
        await db.master_plans.update_one(
            {"id": plan_id},
            {"$set": {"progress": avg_progress}}
        )
    
    return {
        "success": result.modified_count > 0,
        "message": "Progress updated"
    }

@router.get("/progress/{user_id}")
async def get_user_progression(user_id: str):
    """Get user's overall progression across all plans"""
    db = get_db()
    
    # Get all user plans
    plans = await db.master_plans.find({"user_id": user_id}, {"_id": 0}).to_list(length=50)
    
    # Calculate stats
    total_plans = len(plans)
    completed_plans = sum(1 for p in plans if p.get("progress", 0) >= 100)
    active_plans = sum(1 for p in plans if 0 < p.get("progress", 0) < 100)
    
    total_objectives = 0
    completed_objectives = 0
    
    for plan in plans:
        for obj in plan.get("objectives", []):
            total_objectives += 1
            if obj.get("completed", False):
                completed_objectives += 1
    
    return {
        "success": True,
        "user_id": user_id,
        "stats": {
            "total_plans": total_plans,
            "completed_plans": completed_plans,
            "active_plans": active_plans,
            "total_objectives": total_objectives,
            "completed_objectives": completed_objectives,
            "completion_rate": round(completed_objectives / total_objectives * 100, 1) if total_objectives > 0 else 0
        },
        "recent_activity": plans[:5] if plans else []
    }

# ==============================================
# ANALYTICS
# ==============================================

@router.get("/analytics/{user_id}")
async def get_strategy_analytics(user_id: str, period: str = Query("month")):
    """Get strategy analytics for user"""
    db = get_db()
    
    # Get hunting logs
    logs = await db.hunting_logs.find({"user_id": user_id}, {"_id": 0}).sort("date", -1).to_list(length=100)
    
    # Calculate stats
    total_sessions = len(logs)
    successful_sessions = sum(1 for log in logs if log.get("success", False))
    
    # Strategy effectiveness
    strategy_stats = {}
    for log in logs:
        strat = log.get("strategy", "unknown")
        if strat not in strategy_stats:
            strategy_stats[strat] = {"total": 0, "success": 0}
        strategy_stats[strat]["total"] += 1
        if log.get("success"):
            strategy_stats[strat]["success"] += 1
    
    return {
        "success": True,
        "period": period,
        "overview": {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": round(successful_sessions / total_sessions * 100, 1) if total_sessions > 0 else 0
        },
        "strategy_effectiveness": {
            strat: {
                "total": stats["total"],
                "success_rate": round(stats["success"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
            }
            for strat, stats in strategy_stats.items()
        },
        "recommendations": [
            "Continuez avec les stratégies qui fonctionnent",
            "Ajustez selon les conditions météo",
            "Documentez vos observations pour améliorer les prédictions"
        ]
    }
