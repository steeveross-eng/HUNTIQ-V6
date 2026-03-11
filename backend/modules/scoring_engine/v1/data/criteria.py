"""Scoring Criteria Database - Scoring Engine

Complete scoring criteria extracted from analyzer.py.
Based on scientific research for hunting attractants.

Version: 1.0.0
"""

# ============================================
# CRITÈRES DE SCORING (13 critères pondérés)
# ============================================

SCORING_CRITERIA = {
    "attraction_days": {
        "weight": 15, 
        "max": 60, 
        "description": "Durée d'attraction (jours)"
    },
    "natural_palatability": {
        "weight": 12, 
        "max": 10, 
        "description": "Appétence naturelle"
    },
    "olfactory_power": {
        "weight": 12, 
        "max": 10, 
        "description": "Puissance olfactive"
    },
    "persistence": {
        "weight": 10, 
        "max": 10, 
        "description": "Persistance"
    },
    "nutrition": {
        "weight": 10, 
        "max": 10, 
        "description": "Nutrition"
    },
    "behavioral_compounds": {
        "weight": 10, 
        "max": 10, 
        "description": "Composés comportementaux"
    },
    "rainproof": {
        "weight": 8, 
        "max": 10, 
        "description": "Résistance aux intempéries"
    },
    "feed_proof": {
        "weight": 7, 
        "max": 10, 
        "description": "Sécurité alimentaire"
    },
    "certified": {
        "weight": 6, 
        "max": 10, 
        "description": "Certification ACIA/CFIA"
    },
    "physical_resistance": {
        "weight": 4, 
        "max": 10, 
        "description": "Résistance physique"
    },
    "ingredient_purity": {
        "weight": 3, 
        "max": 10, 
        "description": "Pureté des ingrédients"
    },
    "loyalty": {
        "weight": 2, 
        "max": 10, 
        "description": "Fidélisation"
    },
    "chemical_stability": {
        "weight": 1, 
        "max": 10, 
        "description": "Stabilité chimique"
    }
}


def get_total_weight() -> int:
    """Get the sum of all weights"""
    return sum(c["weight"] for c in SCORING_CRITERIA.values())


def get_criterion(name: str) -> dict:
    """Get a specific criterion by name"""
    return SCORING_CRITERIA.get(name, {})


def list_criteria() -> list:
    """List all criteria with their configurations"""
    return [
        {"name": name, **config}
        for name, config in SCORING_CRITERIA.items()
    ]
