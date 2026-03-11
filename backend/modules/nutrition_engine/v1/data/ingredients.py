"""Ingredients Database - Nutrition Engine

Complete ingredients database extracted from analyzer.py.
No modifications to original data.

Version: 1.0.0
"""

from typing import Optional, Dict, Any, List

# ============================================
# BASE DE DONNÉES INTERNE - INGRÉDIENTS
# ============================================

INGREDIENTS_DATABASE = {
    # Composés olfactifs
    "acide butyrique": {"type": "olfactif", "attraction_value": 9, "category": "AGV", "description": "Acide gras volatil à forte attraction"},
    "acide propionique": {"type": "olfactif", "attraction_value": 8, "category": "AGV", "description": "AGV attractif pour cervidés"},
    "acide valérique": {"type": "olfactif", "attraction_value": 8, "category": "AGV", "description": "AGV signature olfactive puissante"},
    "acide isovalérique": {"type": "olfactif", "attraction_value": 8, "category": "AGV", "description": "AGV territorial"},
    "limonène": {"type": "olfactif", "attraction_value": 7, "category": "terpène", "description": "Terpène agrumes attractif"},
    "pinène": {"type": "olfactif", "attraction_value": 7, "category": "terpène", "description": "Terpène conifères"},
    "linalol": {"type": "olfactif", "attraction_value": 6, "category": "terpène", "description": "Terpène floral"},
    "vanilline": {"type": "olfactif", "attraction_value": 8, "category": "ester", "description": "Note sucrée attractive"},
    "acétate d'éthyle": {"type": "olfactif", "attraction_value": 7, "category": "ester", "description": "Ester fruité"},
    "acétate d'isoamyle": {"type": "olfactif", "attraction_value": 8, "category": "ester", "description": "Note banane/pomme"},
    "goudron de bouleau": {"type": "olfactif", "attraction_value": 9, "category": "résine", "description": "Résine traditionnelle très attractive"},
    "huile d'anis": {"type": "olfactif", "attraction_value": 9, "category": "huile essentielle", "description": "Très attractive pour ours et cervidés"},
    "huile de pomme": {"type": "olfactif", "attraction_value": 8, "category": "huile essentielle", "description": "Attractif fruité naturel"},
    
    # Composés nutritionnels
    "hydrolysat de protéines": {"type": "nutritionnel", "attraction_value": 9, "category": "protéine", "description": "Protéines pré-digérées hautement attractives"},
    "farine de poisson": {"type": "nutritionnel", "attraction_value": 8, "category": "protéine", "description": "Source protéique riche"},
    "levure de bière": {"type": "nutritionnel", "attraction_value": 7, "category": "protéine", "description": "Riche en vitamines B"},
    "mélasse": {"type": "nutritionnel", "attraction_value": 8, "category": "glucide", "description": "Sucres naturels attractifs"},
    "maïs broyé": {"type": "nutritionnel", "attraction_value": 6, "category": "glucide", "description": "Source énergétique"},
    "sel minéral": {"type": "nutritionnel", "attraction_value": 8, "category": "minéral", "description": "Minéraux essentiels"},
    "phosphate de calcium": {"type": "nutritionnel", "attraction_value": 7, "category": "minéral", "description": "Pour bois et os"},
    "chlorure de sodium": {"type": "nutritionnel", "attraction_value": 8, "category": "minéral", "description": "Sel essentiel"},
    
    # Composés comportementaux
    "urine de cerf": {"type": "comportemental", "attraction_value": 9, "category": "phéromone", "description": "Signal territorial majeur"},
    "urine de biche en rut": {"type": "comportemental", "attraction_value": 10, "category": "phéromone", "description": "Attractif sexuel très puissant"},
    "urine d'orignal femelle": {"type": "comportemental", "attraction_value": 10, "category": "phéromone", "description": "Attractif rut orignal"},
    "sécrétions tarsiennes": {"type": "comportemental", "attraction_value": 9, "category": "phéromone", "description": "Marqueur territorial"},
    "glandes préorbitales": {"type": "comportemental", "attraction_value": 8, "category": "phéromone", "description": "Signal social"},
    
    # Fixateurs
    "glycérine": {"type": "fixateur", "attraction_value": 5, "category": "fixateur", "description": "Prolonge la diffusion"},
    "propylène glycol": {"type": "fixateur", "attraction_value": 6, "category": "fixateur", "description": "Antigel et fixateur"},
    "huile minérale": {"type": "fixateur", "attraction_value": 5, "category": "fixateur", "description": "Base huileuse persistante"},
}


def get_ingredient(name: str) -> Optional[Dict[str, Any]]:
    """Get ingredient data by exact name (case-insensitive)"""
    name_lower = name.lower().strip()
    return INGREDIENTS_DATABASE.get(name_lower)


def search_ingredients(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search ingredients by partial name match"""
    query_lower = query.lower().strip()
    results = []
    
    for name, data in INGREDIENTS_DATABASE.items():
        if query_lower in name:
            results.append({"name": name, **data})
            if len(results) >= limit:
                break
    
    return results


def get_ingredients_by_type(ingredient_type: str) -> List[Dict[str, Any]]:
    """Get all ingredients of a specific type"""
    return [
        {"name": name, **data}
        for name, data in INGREDIENTS_DATABASE.items()
        if data["type"] == ingredient_type
    ]


def get_ingredients_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all ingredients of a specific category"""
    return [
        {"name": name, **data}
        for name, data in INGREDIENTS_DATABASE.items()
        if data["category"] == category
    ]
