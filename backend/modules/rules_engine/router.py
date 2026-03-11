"""
Rules Engine Router - V5-ULTIME Plan Maître
===========================================

Moteur de règles de chasse intelligentes centralisé.

Règles gérées:
- Règles de timing (heures légales, périodes optimales)
- Règles météo (conditions favorables/défavorables)
- Règles de territoire (zones, distances, couverture)
- Règles de scoring (seuils, pondérations)
- Règles de stratégie (approche, affût, traque)

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rules", tags=["Rules Engine - Plan Maître"])

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

class RuleType(str, Enum):
    TIMING = "timing"
    WEATHER = "weather"
    TERRITORY = "territory"
    SCORING = "scoring"
    STRATEGY = "strategy"
    LEGAL = "legal"

class RulePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RuleCondition(BaseModel):
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, not_in, between
    value: Any
    
class RuleAction(BaseModel):
    type: str  # recommend, alert, block, score_modifier
    params: Dict[str, Any] = {}

class HuntingRule(BaseModel):
    name: str
    description: str
    type: RuleType
    priority: RulePriority = RulePriority.MEDIUM
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    enabled: bool = True
    species: List[str] = ["all"]

class RuleEvaluationRequest(BaseModel):
    context: Dict[str, Any]  # weather, location, time, user_profile
    rule_types: List[RuleType] = []

# ==============================================
# DEFAULT RULES (Plan Maître)
# ==============================================

DEFAULT_RULES = [
    # Règles de timing
    {
        "name": "optimal_morning_window",
        "description": "Fenêtre optimale du matin pour la chasse au cerf",
        "type": "timing",
        "priority": "high",
        "conditions": [
            {"field": "time_of_day", "operator": "between", "value": ["06:00", "09:00"]},
            {"field": "species", "operator": "in", "value": ["deer", "moose"]}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.25, "reason": "Période d'activité maximale"}}
        ],
        "enabled": True,
        "species": ["deer", "moose"]
    },
    {
        "name": "optimal_evening_window",
        "description": "Fenêtre optimale du soir pour la chasse",
        "type": "timing",
        "priority": "high",
        "conditions": [
            {"field": "time_of_day", "operator": "between", "value": ["16:00", "18:30"]}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.20, "reason": "Période d'alimentation"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    
    # Règles météo
    {
        "name": "ideal_temperature",
        "description": "Température idéale pour l'activité du gibier",
        "type": "weather",
        "priority": "medium",
        "conditions": [
            {"field": "temperature", "operator": "between", "value": [-5, 5]}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.15, "reason": "Température favorable"}}
        ],
        "enabled": True,
        "species": ["deer", "moose"]
    },
    {
        "name": "low_wind",
        "description": "Vent faible favorisant l'approche",
        "type": "weather",
        "priority": "high",
        "conditions": [
            {"field": "wind_speed", "operator": "lt", "value": 15}
        ],
        "actions": [
            {"type": "recommend", "params": {"strategy": "approach", "reason": "Conditions d'approche idéales"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    {
        "name": "high_wind_warning",
        "description": "Vent fort défavorable",
        "type": "weather",
        "priority": "critical",
        "conditions": [
            {"field": "wind_speed", "operator": "gt", "value": 30}
        ],
        "actions": [
            {"type": "alert", "params": {"level": "warning", "message": "Vent fort - privilégier l'affût"}},
            {"type": "score_modifier", "params": {"modifier": 0.7, "reason": "Conditions défavorables"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    {
        "name": "barometric_drop",
        "description": "Chute barométrique favorable à l'activité",
        "type": "weather",
        "priority": "high",
        "conditions": [
            {"field": "pressure_trend", "operator": "eq", "value": "falling"}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.20, "reason": "Chute barométrique - activité accrue"}},
            {"type": "alert", "params": {"level": "positive", "message": "Conditions météo excellentes!"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    
    # Règles de territoire
    {
        "name": "zone_proximity",
        "description": "Proximité d'une zone d'alimentation",
        "type": "territory",
        "priority": "high",
        "conditions": [
            {"field": "distance_to_feeding_zone", "operator": "lt", "value": 200}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.30, "reason": "Proximité zone alimentation"}},
            {"type": "recommend", "params": {"strategy": "ambush", "reason": "Position stratégique"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    {
        "name": "water_source_nearby",
        "description": "Proximité d'un point d'eau",
        "type": "territory",
        "priority": "medium",
        "conditions": [
            {"field": "distance_to_water", "operator": "lt", "value": 300}
        ],
        "actions": [
            {"type": "score_modifier", "params": {"modifier": 1.15, "reason": "Proximité point d'eau"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    
    # Règles de scoring
    {
        "name": "high_score_threshold",
        "description": "Seuil de score élevé pour recommandation",
        "type": "scoring",
        "priority": "medium",
        "conditions": [
            {"field": "global_score", "operator": "gte", "value": 80}
        ],
        "actions": [
            {"type": "recommend", "params": {"action": "go_hunt", "confidence": "high"}},
            {"type": "alert", "params": {"level": "positive", "message": "Conditions optimales!"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    {
        "name": "low_score_warning",
        "description": "Avertissement score faible",
        "type": "scoring",
        "priority": "medium",
        "conditions": [
            {"field": "global_score", "operator": "lt", "value": 40}
        ],
        "actions": [
            {"type": "alert", "params": {"level": "warning", "message": "Conditions peu favorables"}},
            {"type": "recommend", "params": {"action": "wait", "reason": "Score trop bas"}}
        ],
        "enabled": True,
        "species": ["all"]
    },
    
    # Règles de stratégie
    {
        "name": "rut_season_strategy",
        "description": "Stratégie période de rut",
        "type": "strategy",
        "priority": "high",
        "conditions": [
            {"field": "season", "operator": "eq", "value": "rut"},
            {"field": "species", "operator": "in", "value": ["deer", "moose"]}
        ],
        "actions": [
            {"type": "recommend", "params": {"strategy": "call", "reason": "Période de rut active"}},
            {"type": "score_modifier", "params": {"modifier": 1.25, "reason": "Rut actif"}}
        ],
        "enabled": True,
        "species": ["deer", "moose"]
    },
    {
        "name": "early_season_strategy",
        "description": "Stratégie début de saison",
        "type": "strategy",
        "priority": "medium",
        "conditions": [
            {"field": "season_week", "operator": "lte", "value": 2}
        ],
        "actions": [
            {"type": "recommend", "params": {"strategy": "approach", "reason": "Gibier moins méfiant"}},
            {"type": "alert", "params": {"level": "info", "message": "Début de saison - patience recommandée"}}
        ],
        "enabled": True,
        "species": ["all"]
    }
]

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def rules_engine_info():
    """Get rules engine information"""
    return {
        "module": "rules_engine",
        "version": "1.0.0",
        "description": "Moteur de règles de chasse Plan Maître V5-ULTIME",
        "rule_types": [t.value for t in RuleType],
        "priorities": [p.value for p in RulePriority],
        "default_rules_count": len(DEFAULT_RULES),
        "features": [
            "Règles de timing",
            "Règles météo",
            "Règles de territoire",
            "Règles de scoring",
            "Règles de stratégie",
            "Évaluation dynamique",
            "Actions automatisées"
        ]
    }

# ==============================================
# RULES CRUD
# ==============================================

@router.get("/list")
async def list_rules(
    rule_type: Optional[RuleType] = None,
    enabled_only: bool = Query(True),
    species: Optional[str] = None
):
    """List all hunting rules"""
    db = get_db()
    
    # Build query
    query = {}
    if rule_type:
        query["type"] = rule_type.value
    if enabled_only:
        query["enabled"] = True
    if species:
        query["$or"] = [
            {"species": "all"},
            {"species": species}
        ]
    
    # Get from DB or return defaults
    rules = await db.hunting_rules.find(query, {"_id": 0}).to_list(length=100)
    
    if not rules:
        # Return filtered defaults
        rules = [r for r in DEFAULT_RULES if (
            (not rule_type or r["type"] == rule_type.value) and
            (not enabled_only or r.get("enabled", True)) and
            (not species or "all" in r.get("species", ["all"]) or species in r.get("species", []))
        )]
    
    return {
        "success": True,
        "total": len(rules),
        "rules": rules
    }

@router.post("/create")
async def create_rule(rule: HuntingRule):
    """Create a new hunting rule"""
    db = get_db()
    
    rule_dict = rule.dict()
    rule_dict["type"] = rule.type.value
    rule_dict["priority"] = rule.priority.value
    rule_dict["created_at"] = datetime.now(timezone.utc)
    
    await db.hunting_rules.insert_one(rule_dict)
    del rule_dict["_id"]
    
    return {"success": True, "rule": rule_dict}

@router.put("/{rule_name}")
async def update_rule(rule_name: str, updates: dict):
    """Update an existing rule"""
    db = get_db()
    
    updates["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.hunting_rules.update_one(
        {"name": rule_name},
        {"$set": updates}
    )
    
    return {
        "success": result.modified_count > 0,
        "message": "Rule updated" if result.modified_count > 0 else "Rule not found"
    }

@router.delete("/{rule_name}")
async def delete_rule(rule_name: str):
    """Delete a rule"""
    db = get_db()
    result = await db.hunting_rules.delete_one({"name": rule_name})
    
    return {
        "success": result.deleted_count > 0,
        "message": "Rule deleted" if result.deleted_count > 0 else "Rule not found"
    }

# ==============================================
# RULE EVALUATION
# ==============================================

def evaluate_condition(condition: dict, context: dict) -> bool:
    """Evaluate a single condition against context"""
    field = condition["field"]
    operator = condition["operator"]
    value = condition["value"]
    
    ctx_value = context.get(field)
    if ctx_value is None:
        return False
    
    try:
        if operator == "eq":
            return ctx_value == value
        elif operator == "ne":
            return ctx_value != value
        elif operator == "gt":
            return ctx_value > value
        elif operator == "gte":
            return ctx_value >= value
        elif operator == "lt":
            return ctx_value < value
        elif operator == "lte":
            return ctx_value <= value
        elif operator == "in":
            return ctx_value in value
        elif operator == "not_in":
            return ctx_value not in value
        elif operator == "between":
            if isinstance(value, list) and len(value) == 2:
                return value[0] <= ctx_value <= value[1]
        return False
    except Exception:
        return False

@router.post("/evaluate")
async def evaluate_rules(request: RuleEvaluationRequest):
    """Evaluate rules against a context and return triggered actions"""
    db = get_db()
    
    # Get applicable rules
    query = {"enabled": True}
    if request.rule_types:
        query["type"] = {"$in": [t.value for t in request.rule_types]}
    
    rules = await db.hunting_rules.find(query, {"_id": 0}).to_list(length=100)
    
    # Use defaults if no custom rules
    if not rules:
        rules = [r for r in DEFAULT_RULES if (
            r.get("enabled", True) and
            (not request.rule_types or r["type"] in [t.value for t in request.rule_types])
        )]
    
    # Evaluate each rule
    triggered_rules = []
    actions = []
    score_modifier = 1.0
    
    for rule in rules:
        # Check all conditions
        all_conditions_met = True
        for condition in rule.get("conditions", []):
            if not evaluate_condition(condition, request.context):
                all_conditions_met = False
                break
        
        if all_conditions_met:
            triggered_rules.append({
                "name": rule["name"],
                "type": rule["type"],
                "priority": rule.get("priority", "medium")
            })
            
            # Collect actions
            for action in rule.get("actions", []):
                actions.append({
                    "rule": rule["name"],
                    "type": action["type"],
                    "params": action.get("params", {})
                })
                
                # Apply score modifiers
                if action["type"] == "score_modifier":
                    score_modifier *= action["params"].get("modifier", 1.0)
    
    return {
        "success": True,
        "context_evaluated": request.context,
        "triggered_rules_count": len(triggered_rules),
        "triggered_rules": triggered_rules,
        "actions": actions,
        "cumulative_score_modifier": round(score_modifier, 2)
    }

# ==============================================
# RULE TEMPLATES
# ==============================================

@router.get("/templates")
async def get_rule_templates():
    """Get predefined rule templates"""
    return {
        "success": True,
        "templates": [
            {
                "name": "custom_timing_rule",
                "description": "Modèle pour règle de timing personnalisée",
                "type": "timing",
                "conditions": [
                    {"field": "time_of_day", "operator": "between", "value": ["HH:MM", "HH:MM"]}
                ],
                "actions": [
                    {"type": "score_modifier", "params": {"modifier": 1.0, "reason": ""}}
                ]
            },
            {
                "name": "custom_weather_rule",
                "description": "Modèle pour règle météo personnalisée",
                "type": "weather",
                "conditions": [
                    {"field": "temperature", "operator": "between", "value": [-10, 10]}
                ],
                "actions": [
                    {"type": "recommend", "params": {"strategy": "", "reason": ""}}
                ]
            },
            {
                "name": "custom_territory_rule",
                "description": "Modèle pour règle de territoire personnalisée",
                "type": "territory",
                "conditions": [
                    {"field": "distance_to_zone", "operator": "lt", "value": 500}
                ],
                "actions": [
                    {"type": "alert", "params": {"level": "info", "message": ""}}
                ]
            }
        ]
    }

# ==============================================
# INITIALIZE DEFAULT RULES
# ==============================================

@router.post("/initialize-defaults")
async def initialize_default_rules():
    """Initialize default rules in database"""
    db = get_db()
    
    inserted = 0
    for rule in DEFAULT_RULES:
        # Check if exists
        existing = await db.hunting_rules.find_one({"name": rule["name"]})
        if not existing:
            rule["created_at"] = datetime.now(timezone.utc)
            await db.hunting_rules.insert_one(rule)
            inserted += 1
    
    return {
        "success": True,
        "message": f"Initialized {inserted} default rules",
        "total_defaults": len(DEFAULT_RULES)
    }
