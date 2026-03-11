# analyzer.py - Module d'analyse scientifique des attractants
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# ============================================
# BASE DE DONNÉES INTERNE - PRODUITS BIONIC™
# ============================================

BIONIC_PRODUCTS = {
    "gel": {
        "name": "BIONIC™ Apple Jelly Premium",
        "price": 29.99,
        "price_with_shipping": 39.99,
        "score": 9.2,
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400",
        "attraction_days": 21,
        "ingredients": ["huile de pomme", "vanilline", "hydrolysat de protéines", "glycérine", "acide butyrique"],
        "rainproof": True,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/apple-jelly"
    },
    "bloc": {
        "name": "BIONIC™ Bloc Mix Ultra",
        "price": 24.99,
        "price_with_shipping": 34.99,
        "score": 9.0,
        "image_url": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=400",
        "attraction_days": 45,
        "ingredients": ["sel minéral", "phosphate de calcium", "mélasse", "huile d'anis", "levure de bière"],
        "rainproof": True,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/bloc-mix"
    },
    "urine": {
        "name": "BIONIC™ Buck Urine Premium",
        "price": 34.99,
        "price_with_shipping": 44.99,
        "score": 9.5,
        "image_url": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400",
        "attraction_days": 14,
        "ingredients": ["urine de cerf", "sécrétions tarsiennes", "acide butyrique", "propylène glycol"],
        "rainproof": True,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/buck-urine"
    },
    "granules": {
        "name": "BIONIC™ Deer Granules Pro",
        "price": 19.99,
        "price_with_shipping": 29.99,
        "score": 8.8,
        "image_url": "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400",
        "attraction_days": 10,
        "ingredients": ["maïs broyé", "mélasse", "huile de pomme", "sel minéral", "vanilline"],
        "rainproof": False,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/deer-granules"
    },
    "liquide": {
        "name": "BIONIC™ Spray Attraction Max",
        "price": 22.99,
        "price_with_shipping": 32.99,
        "score": 8.5,
        "image_url": "https://images.unsplash.com/photo-1517022812141-23620dba5c23?w=400",
        "attraction_days": 7,
        "ingredients": ["acide butyrique", "limonène", "vanilline", "propylène glycol", "huile de pomme"],
        "rainproof": False,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/spray-max"
    },
    "poudre": {
        "name": "BIONIC™ Powder Attract Plus",
        "price": 17.99,
        "price_with_shipping": 27.99,
        "score": 8.3,
        "image_url": "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400",
        "attraction_days": 5,
        "ingredients": ["farine de poisson", "levure de bière", "sel minéral", "vanilline"],
        "rainproof": False,
        "feed_proof": True,
        "certified": True,
        "buy_link": "https://bionic-direct.com/powder-plus"
    }
}

# ============================================
# BASE DE DONNÉES INTERNE - CONCURRENTS
# ============================================

COMPETITOR_PRODUCTS = {
    "gel": [
        {
            "name": "Tink's Power Jelly",
            "brand": "Tink's",
            "price": 24.99,
            "price_with_shipping": 34.99,
            "score": 7.8,
            "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400",
            "attraction_days": 14,
            "ingredients": ["huile de pomme", "mélasse", "glycérine"],
            "rainproof": True,
            "feed_proof": False,
            "certified": False,
            "buy_link": "https://tinks.com/power-jelly"
        },
        {
            "name": "Code Blue Apple Jelly",
            "brand": "Code Blue",
            "price": 27.99,
            "price_with_shipping": 37.99,
            "score": 8.2,
            "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400",
            "attraction_days": 18,
            "ingredients": ["huile de pomme", "vanilline", "glycérine", "acide butyrique"],
            "rainproof": True,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://code-blue.com/apple-jelly"
        }
    ],
    "bloc": [
        {
            "name": "Deer Cane Black Magic",
            "brand": "Evolved Habitats",
            "price": 19.99,
            "price_with_shipping": 29.99,
            "score": 7.5,
            "image_url": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=400",
            "attraction_days": 30,
            "ingredients": ["sel minéral", "mélasse", "phosphate de calcium"],
            "rainproof": True,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://evolved.com/deer-cane"
        },
        {
            "name": "Trophy Rock",
            "brand": "Trophy Rock",
            "price": 34.99,
            "price_with_shipping": 44.99,
            "score": 8.0,
            "image_url": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=400",
            "attraction_days": 60,
            "ingredients": ["sel minéral", "oligo-éléments naturels"],
            "rainproof": True,
            "feed_proof": True,
            "certified": True,
            "buy_link": "https://trophyrock.com/original"
        }
    ],
    "urine": [
        {
            "name": "Tink's #69 Doe-in-Rut",
            "brand": "Tink's",
            "price": 29.99,
            "price_with_shipping": 39.99,
            "score": 8.5,
            "image_url": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400",
            "attraction_days": 10,
            "ingredients": ["urine de biche en rut", "propylène glycol"],
            "rainproof": True,
            "feed_proof": True,
            "certified": True,
            "buy_link": "https://tinks.com/69-doe-rut"
        },
        {
            "name": "Code Blue Doe Estrous",
            "brand": "Code Blue",
            "price": 24.99,
            "price_with_shipping": 34.99,
            "score": 8.8,
            "image_url": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400",
            "attraction_days": 12,
            "ingredients": ["urine de biche en rut", "sécrétions tarsiennes", "glycérine"],
            "rainproof": True,
            "feed_proof": True,
            "certified": True,
            "buy_link": "https://code-blue.com/doe-estrous"
        }
    ],
    "granules": [
        {
            "name": "Wildgame Innovations Acorn Rage",
            "brand": "Wildgame Innovations",
            "price": 14.99,
            "price_with_shipping": 24.99,
            "score": 7.2,
            "image_url": "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400",
            "attraction_days": 7,
            "ingredients": ["maïs broyé", "gland", "mélasse"],
            "rainproof": False,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://wildgame.com/acorn-rage"
        },
        {
            "name": "Buck Bomb Deer Corn",
            "brand": "Buck Bomb",
            "price": 16.99,
            "price_with_shipping": 26.99,
            "score": 7.5,
            "image_url": "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400",
            "attraction_days": 8,
            "ingredients": ["maïs broyé", "sel minéral", "huile de pomme"],
            "rainproof": False,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://buckbomb.com/deer-corn"
        }
    ],
    "liquide": [
        {
            "name": "Buck Bomb Dominant Buck",
            "brand": "Buck Bomb",
            "price": 19.99,
            "price_with_shipping": 29.99,
            "score": 7.8,
            "image_url": "https://images.unsplash.com/photo-1517022812141-23620dba5c23?w=400",
            "attraction_days": 5,
            "ingredients": ["urine de cerf", "acide butyrique", "propylène glycol"],
            "rainproof": False,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://buckbomb.com/dominant-buck"
        },
        {
            "name": "Code Blue Screamin Heat",
            "brand": "Code Blue",
            "price": 24.99,
            "price_with_shipping": 34.99,
            "score": 8.0,
            "image_url": "https://images.unsplash.com/photo-1517022812141-23620dba5c23?w=400",
            "attraction_days": 6,
            "ingredients": ["urine de biche en rut", "vanilline", "glycérine"],
            "rainproof": False,
            "feed_proof": True,
            "certified": True,
            "buy_link": "https://code-blue.com/screamin-heat"
        }
    ],
    "poudre": [
        {
            "name": "C'Mere Deer Powder",
            "brand": "C'Mere Deer",
            "price": 12.99,
            "price_with_shipping": 22.99,
            "score": 7.0,
            "image_url": "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400",
            "attraction_days": 4,
            "ingredients": ["farine de maïs", "sel minéral", "arôme pomme"],
            "rainproof": False,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://cmeredeer.com/powder"
        },
        {
            "name": "Evolved Habitats Dirt Bag",
            "brand": "Evolved Habitats",
            "price": 15.99,
            "price_with_shipping": 25.99,
            "score": 7.3,
            "image_url": "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400",
            "attraction_days": 5,
            "ingredients": ["minéraux", "levure de bière", "mélasse en poudre"],
            "rainproof": False,
            "feed_proof": True,
            "certified": False,
            "buy_link": "https://evolved.com/dirt-bag"
        }
    ]
}

# ============================================
# CRITÈRES DE SCORING
# ============================================

SCORING_CRITERIA = {
    "attraction_days": {"weight": 15, "max": 60, "description": "Durée d'attraction (jours)"},
    "natural_palatability": {"weight": 12, "max": 10, "description": "Appétence naturelle"},
    "olfactory_power": {"weight": 12, "max": 10, "description": "Puissance olfactive"},
    "persistence": {"weight": 10, "max": 10, "description": "Persistance"},
    "nutrition": {"weight": 10, "max": 10, "description": "Nutrition"},
    "behavioral_compounds": {"weight": 10, "max": 10, "description": "Composés comportementaux"},
    "rainproof": {"weight": 8, "max": 10, "description": "Résistance aux intempéries"},
    "feed_proof": {"weight": 7, "max": 10, "description": "Sécurité alimentaire"},
    "certified": {"weight": 6, "max": 10, "description": "Certification ACIA/CFIA"},
    "physical_resistance": {"weight": 4, "max": 10, "description": "Résistance physique"},
    "ingredient_purity": {"weight": 3, "max": 10, "description": "Pureté des ingrédients"},
    "loyalty": {"weight": 2, "max": 10, "description": "Fidélisation"},
    "chemical_stability": {"weight": 1, "max": 10, "description": "Stabilité chimique"}
}

# ============================================
# MOTS-CLÉS POUR DÉTECTION DE CATÉGORIE
# ============================================

CATEGORY_KEYWORDS = {
    "gel": ["gel", "gelée", "jelly", "jam", "pâte", "paste"],
    "bloc": ["bloc", "block", "pierre", "stone", "lick", "lécher", "sel", "salt"],
    "urine": ["urine", "urin", "leurre urinaire", "scent", "estrous", "rut", "doe", "buck", "tarsal"],
    "granules": ["granules", "granulé", "pellets", "pellet", "sec", "dry", "corn", "maïs", "grain"],
    "liquide": ["liquide", "liquid", "spray", "bombe", "bomb", "vaporisateur", "aerosol"],
    "poudre": ["poudre", "powder", "additif", "additive", "dust"]
}

# ============================================
# RÉFÉRENCES SCIENTIFIQUES CONSOLIDÉES
# ============================================

SCIENTIFIC_REFERENCES = {
    "olfaction_perception": {
        "title": "5.1. Olfaction et perception chimique",
        "references": [
            "Sánchez, et al. (2022) – Études sur l'évolution des gènes olfactifs chez les cervidés",
            "Geist, V. (1998). Deer of the World: Their Evolution, Behaviour, and Ecology",
            "Døving, K. B. & Trotier, D. (1998) – Structure et fonction de l'organe voméronasal",
            "Rasmussen, L. E. L. & Schulte, B. A. (1998) – Communication chimique chez les mammifères"
        ]
    },
    "attractants_repellents": {
        "title": "5.2. Odeurs biologiquement significatives, attractants et répulsifs",
        "references": [
            "Nolte, D. L. (1999) – Réponses comportementales des cervidés aux attractants et répulsifs",
            "Müller-Schwarze, D. (2011). Chemical Ecology of Vertebrates",
            "Apfelbach, R., et al. (2005) – Effets des odeurs de prédateurs sur les mammifères",
            "Müller-Schwarze, D. & Sun, L. (2003) – Signaux chimiques chez les vertébrés"
        ]
    },
    "fruits_volatiles": {
        "title": "5.3. Attraction pour fruits mûrs, fermentés et composés volatils",
        "references": [
            "Atkinson, R. G., et al. (2017) – Composés volatils responsables des arômes de fruits",
            "Feldhamer, G. A., Thompson, B. C., & Chapman, J. A. (2003). Wild Mammals of North America (sections sur l'alimentation des cervidés)",
            "Herrera, C. M. (1982) – Mutualisme plantes–animaux et défense des fruits mûrs",
            "Schmidt, K. T., et al. – Sélection alimentaire des cervidés selon les ressources fruitées"
        ]
    },
    "nutrition": {
        "title": "5.4. Minéraux, vitamines, protéines et nutrition faunique",
        "references": [
            "Robbins, C. T. (1993). Wildlife Feeding and Nutrition",
            "Weeks, H. P. & Kirkpatrick, C. M. (1976) – Besoins minéraux des cervidés",
            "Ullrey, D. E., Youatt, W. G., Johnson, H. E., et al. – Travaux sur les besoins nutritionnels des cervidés",
            "Mautz, W. W. (1978) – Cycle des réserves de graisse chez les cervidés"
        ]
    },
    "behavioral_compounds": {
        "title": "5.5. Composés comportementaux et signaux chimiques",
        "references": [
            "Gassett, J. W., et al. (1997) – Communication chimique chez le cerf de Virginie",
            "Brown, R. E. & Macdonald, D. W. (1985). Social Odours in Mammals",
            "Marchinton, R. L. & Hirth, D. H. – Études sur les comportements sociaux et marquages",
            "Müller-Schwarze, D. (série Chemical Signals in Vertebrates)"
        ]
    },
    "ecology_management": {
        "title": "5.6. Écologie chimique, gestion faunique et comportement",
        "references": [
            "Johansson, B. G. & Jones, T. M. (2007) – Rôle de la communication chimique dans le choix du partenaire",
            "Putman, R. J. (1988). The Natural History of Deer",
            "Milner, J. M., Bonenfant, C., Mysterud, A., et al. – Gestion des populations de cervidés",
            "Apfelbach, R., et al. – Réactions comportementales aux signaux olfactifs"
        ]
    }
}

def get_scientific_references() -> List[Dict[str, Any]]:
    """Retourne les références scientifiques formatées pour l'affichage"""
    return [
        {
            "section_id": key,
            "title": value["title"],
            "references": value["references"]
        }
        for key, value in SCIENTIFIC_REFERENCES.items()
    ]

# ============================================
# MODÈLES PYDANTIC
# ============================================

class AnalysisRequest(BaseModel):
    product_name: str
    product_type: Optional[str] = None  # Auto-détecté si non fourni

class ProductTechnicalSheet(BaseModel):
    name: str
    detected_type: str
    brand: Optional[str] = None
    estimated_price: Optional[float] = None
    estimated_price_with_shipping: Optional[float] = None
    estimated_ingredients: List[str] = []
    estimated_composition: Dict[str, Any] = {}
    confidence_level: str = "estimated"  # "confirmed" or "estimated"
    notes: List[str] = []

class ScientificAnalysis(BaseModel):
    olfactory_compounds: List[Dict[str, Any]] = []
    nutritional_compounds: List[Dict[str, Any]] = []
    behavioral_compounds: List[Dict[str, Any]] = []
    fixatives: List[Dict[str, Any]] = []
    durability_criteria: Dict[str, Any] = {}

class ScoringResult(BaseModel):
    total_score: float
    pastille: Literal["green", "yellow", "red"]
    pastille_label: str
    criteria_scores: Dict[str, float] = {}
    weighted_scores: Dict[str, float] = {}

class CompetitorComparison(BaseModel):
    bionic_product: Dict[str, Any]
    competitor_1: Dict[str, Any]
    competitor_2: Dict[str, Any]
    comparison_table: List[Dict[str, Any]]

class AnalysisReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    technical_sheet: ProductTechnicalSheet
    scientific_analysis: ScientificAnalysis
    scoring: ScoringResult
    comparison: CompetitorComparison
    price_analysis: Dict[str, Any] = {}
    recommendations: List[str] = []
    bionic_arguments: List[str] = []
    conclusion: str = ""
    scientific_references: List[Dict[str, Any]] = Field(default_factory=get_scientific_references)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmailConsent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    region: str
    consent_marketing: bool
    consent_statistics: bool
    report_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# CLASSE PRINCIPALE D'ANALYSE
# ============================================

class ProductAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.chat = LlmChat(
            api_key=api_key,
            session_id=f"analyzer_{uuid.uuid4().hex[:8]}",
            system_message="""Tu es un expert scientifique en attractants pour la chasse au Québec et en Amérique du Nord.
            Tu analyses les produits de manière impartiale et scientifique basé sur 13 critères d'évaluation.
            Tu dois fournir des analyses détaillées basées sur les ingrédients, la composition chimique et les conditions d'utilisation.
            Tu prends en compte l'espèce cible, la saison de chasse, les conditions météorologiques et le type d'habitat.
            Réponds toujours en JSON valide."""
        ).with_model("openai", "gpt-5.2")
    
    def detect_category(self, product_name: str) -> str:
        """Détecte automatiquement la catégorie du produit"""
        product_lower = product_name.lower()
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in product_lower:
                    return category
        
        return "granules"  # Défaut
    
    def calculate_score(self, analysis_data: Dict[str, Any], product_type: str) -> ScoringResult:
        """Calcule le score scientifique basé sur les critères pondérés"""
        criteria_scores = {}
        weighted_scores = {}
        total_weight = sum(c["weight"] for c in SCORING_CRITERIA.values())
        
        # Helper function to safely get numeric value
        def get_numeric(key, default):
            value = analysis_data.get(key, default)
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, list):
                return len(value) if value else default
            elif isinstance(value, bool):
                return 10 if value else default
            return default
        
        # Extraction des scores depuis l'analyse
        attraction_days = get_numeric("attraction_days", 10)
        criteria_scores["attraction_days"] = min(attraction_days, 60) / 60 * 10
        criteria_scores["natural_palatability"] = get_numeric("natural_palatability", 7)
        criteria_scores["olfactory_power"] = get_numeric("olfactory_power", 7)
        criteria_scores["persistence"] = get_numeric("persistence", 7)
        criteria_scores["nutrition"] = get_numeric("nutrition", 5)
        criteria_scores["behavioral_compounds"] = get_numeric("behavioral_compounds", 5)
        criteria_scores["rainproof"] = 10 if analysis_data.get("rainproof", False) else 3
        criteria_scores["feed_proof"] = 10 if analysis_data.get("feed_proof", False) else 5
        criteria_scores["certified"] = 10 if analysis_data.get("certified", False) else 4
        criteria_scores["physical_resistance"] = get_numeric("physical_resistance", 6)
        criteria_scores["ingredient_purity"] = get_numeric("ingredient_purity", 6)
        criteria_scores["loyalty"] = get_numeric("loyalty", 6)
        criteria_scores["chemical_stability"] = get_numeric("chemical_stability", 7)
        
        # Calcul des scores pondérés
        total_score = 0
        for criterion, config in SCORING_CRITERIA.items():
            score = criteria_scores.get(criterion, 5)
            weighted = (score / config["max"]) * config["weight"]
            weighted_scores[criterion] = weighted
            total_score += weighted
        
        # Normalisation sur 10
        final_score = (total_score / total_weight) * 10
        
        # Détermination de la pastille
        if final_score >= 7.5:
            pastille = "green"
            pastille_label = "🟢 Attraction forte"
        elif final_score >= 5.0:
            pastille = "yellow"
            pastille_label = "🟡 Attraction modérée"
        else:
            pastille = "red"
            pastille_label = "🔴 Attraction faible"
        
        return ScoringResult(
            total_score=round(final_score, 1),
            pastille=pastille,
            pastille_label=pastille_label,
            criteria_scores=criteria_scores,
            weighted_scores=weighted_scores
        )
    
    def get_comparison(self, product_type: str, analyzed_score: float) -> CompetitorComparison:
        """Génère la comparaison à 3 colonnes"""
        bionic = BIONIC_PRODUCTS.get(product_type, BIONIC_PRODUCTS["granules"])
        competitors = COMPETITOR_PRODUCTS.get(product_type, COMPETITOR_PRODUCTS["granules"])
        
        # Trier les concurrents par score
        sorted_competitors = sorted(competitors, key=lambda x: x["score"], reverse=True)
        
        competitor_1 = sorted_competitors[0] if len(sorted_competitors) > 0 else competitors[0]
        competitor_2 = sorted_competitors[1] if len(sorted_competitors) > 1 else competitors[0]
        
        comparison_table = []
        criteria_list = [
            ("score", "Score d'attraction"),
            ("pastille", "Pastille"),
            ("attraction_days", "Durée d'attraction (jours)"),
            ("price", "Meilleur prix (sans transport)"),
            ("price_with_shipping", "Meilleur prix (avec transport)"),
            ("buy_link", "Lien vers l'offre"),
            ("performance_price", "Performance/prix"),
            ("rainproof", "Rainproof"),
            ("feed_proof", "Feed-Proof"),
            ("certified", "Certification alimentaire"),
        ]
        
        for key, label in criteria_list:
            row = {"criterion": label}
            
            if key == "score":
                row["bionic"] = bionic["score"]
                row["competitor_1"] = competitor_1["score"]
                row["competitor_2"] = competitor_2["score"]
            elif key == "pastille":
                row["bionic"] = "🟢" if bionic["score"] >= 7.5 else "🟡"
                row["competitor_1"] = "🟢" if competitor_1["score"] >= 7.5 else "🟡" if competitor_1["score"] >= 5 else "🔴"
                row["competitor_2"] = "🟢" if competitor_2["score"] >= 7.5 else "🟡" if competitor_2["score"] >= 5 else "🔴"
            elif key == "attraction_days":
                row["bionic"] = bionic["attraction_days"]
                row["competitor_1"] = competitor_1["attraction_days"]
                row["competitor_2"] = competitor_2["attraction_days"]
            elif key == "price":
                row["bionic"] = f"${bionic['price']}"
                row["competitor_1"] = f"${competitor_1['price']}"
                row["competitor_2"] = f"${competitor_2['price']}"
            elif key == "price_with_shipping":
                row["bionic"] = f"${bionic['price_with_shipping']}"
                row["competitor_1"] = f"${competitor_1['price_with_shipping']}"
                row["competitor_2"] = f"${competitor_2['price_with_shipping']}"
            elif key == "buy_link":
                row["bionic"] = bionic["buy_link"]
                row["competitor_1"] = competitor_1["buy_link"]
                row["competitor_2"] = competitor_2["buy_link"]
            elif key == "performance_price":
                row["bionic"] = round(bionic["score"] / bionic["price"] * 10, 2)
                row["competitor_1"] = round(competitor_1["score"] / competitor_1["price"] * 10, 2)
                row["competitor_2"] = round(competitor_2["score"] / competitor_2["price"] * 10, 2)
            elif key in ["rainproof", "feed_proof", "certified"]:
                row["bionic"] = "✅" if bionic.get(key, False) else "❌"
                row["competitor_1"] = "✅" if competitor_1.get(key, False) else "❌"
                row["competitor_2"] = "✅" if competitor_2.get(key, False) else "❌"
            
            comparison_table.append(row)
        
        return CompetitorComparison(
            bionic_product={
                "name": bionic["name"],
                "image_url": bionic["image_url"],
                "score": bionic["score"],
                "price": bionic["price"],
                "price_with_shipping": bionic["price_with_shipping"],
                "buy_link": bionic["buy_link"]
            },
            competitor_1={
                "name": competitor_1["name"],
                "brand": competitor_1["brand"],
                "image_url": competitor_1["image_url"],
                "score": competitor_1["score"],
                "price": competitor_1["price"],
                "price_with_shipping": competitor_1["price_with_shipping"],
                "buy_link": competitor_1["buy_link"]
            },
            competitor_2={
                "name": competitor_2["name"],
                "brand": competitor_2["brand"],
                "image_url": competitor_2["image_url"],
                "score": competitor_2["score"],
                "price": competitor_2["price"],
                "price_with_shipping": competitor_2["price_with_shipping"],
                "buy_link": competitor_2["buy_link"]
            },
            comparison_table=comparison_table
        )
    
    async def analyze_product(self, product_name: str, product_type: Optional[str] = None) -> AnalysisReport:
        """Analyse complète d'un produit"""
        
        # Détection de catégorie
        detected_type = product_type or self.detect_category(product_name)
        
        # Prompt pour l'IA
        analysis_prompt = f"""Analyse le produit attractant de chasse suivant: "{product_name}"

Type détecté: {detected_type}

Base de données d'ingrédients connus: {json.dumps(list(INGREDIENTS_DATABASE.keys()), ensure_ascii=False)}

Fournis une analyse JSON avec cette structure exacte:
{{
    "brand": "marque détectée ou estimée",
    "estimated_price": prix estimé en dollars,
    "estimated_ingredients": ["liste", "des", "ingrédients", "estimés"],
    "olfactory_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "nutritional_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "behavioral_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "attraction_days": nombre de jours d'attraction estimé,
    "natural_palatability": score 1-10,
    "olfactory_power": score 1-10,
    "persistence": score 1-10,
    "nutrition": score 1-10,
    "rainproof": true/false,
    "feed_proof": true/false,
    "certified": true/false,
    "physical_resistance": score 1-10,
    "ingredient_purity": score 1-10,
    "loyalty": score 1-10,
    "chemical_stability": score 1-10,
    "notes": ["informations", "importantes", "sur", "le", "produit"],
    "recommendations": ["recommandation 1", "recommandation 2"]
}}

Sois précis et scientifique. Si des informations sont estimées, indique-le dans les notes."""

        try:
            response = await self.chat.send_message(UserMessage(text=analysis_prompt))
            
            # Parser la réponse JSON
            # Nettoyer la réponse si nécessaire
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            analysis_data = json.loads(json_str)
        except Exception as e:
            # Fallback avec données par défaut
            analysis_data = {
                "brand": "Marque inconnue",
                "estimated_price": 25.00,
                "estimated_ingredients": ["ingrédients non identifiés"],
                "olfactory_compounds": [],
                "nutritional_compounds": [],
                "behavioral_compounds": [],
                "attraction_days": 10,
                "natural_palatability": 6,
                "olfactory_power": 6,
                "persistence": 6,
                "nutrition": 5,
                "rainproof": False,
                "feed_proof": True,
                "certified": False,
                "physical_resistance": 6,
                "ingredient_purity": 5,
                "loyalty": 5,
                "chemical_stability": 6,
                "notes": [f"Analyse automatique - erreur: {str(e)}"],
                "recommendations": ["Vérifier les informations du produit"]
            }
        
        # Créer la fiche technique
        technical_sheet = ProductTechnicalSheet(
            name=product_name,
            detected_type=detected_type,
            brand=analysis_data.get("brand"),
            estimated_price=analysis_data.get("estimated_price"),
            estimated_price_with_shipping=analysis_data.get("estimated_price", 25) + 10,
            estimated_ingredients=analysis_data.get("estimated_ingredients", []),
            confidence_level="estimated",
            notes=analysis_data.get("notes", [])
        )
        
        # Créer l'analyse scientifique
        scientific_analysis = ScientificAnalysis(
            olfactory_compounds=analysis_data.get("olfactory_compounds", []),
            nutritional_compounds=analysis_data.get("nutritional_compounds", []),
            behavioral_compounds=analysis_data.get("behavioral_compounds", []),
            fixatives=[],
            durability_criteria={
                "rainproof": analysis_data.get("rainproof", False),
                "feed_proof": analysis_data.get("feed_proof", True),
                "certified": analysis_data.get("certified", False)
            }
        )
        
        # Calculer le score
        scoring = self.calculate_score(analysis_data, detected_type)
        
        # Générer la comparaison
        comparison = self.get_comparison(detected_type, scoring.total_score)
        
        # Analyse des prix
        price_analysis = {
            "analyzed_product": {
                "price": analysis_data.get("estimated_price", 25),
                "price_with_shipping": analysis_data.get("estimated_price", 25) + 10,
                "performance_price_ratio": round(scoring.total_score / max(analysis_data.get("estimated_price", 25), 1) * 10, 2)
            },
            "bionic": {
                "price": comparison.bionic_product["price"],
                "price_with_shipping": comparison.bionic_product["price_with_shipping"],
                "performance_price_ratio": round(comparison.bionic_product["score"] / comparison.bionic_product["price"] * 10, 2)
            },
            "best_value": "BIONIC™" if comparison.bionic_product["score"] / comparison.bionic_product["price"] > scoring.total_score / max(analysis_data.get("estimated_price", 25), 1) else product_name
        }
        
        # Générer les arguments BIONIC™
        bionic_product = BIONIC_PRODUCTS.get(detected_type, BIONIC_PRODUCTS["granules"])
        bionic_arguments = []
        
        if bionic_product["score"] > scoring.total_score:
            bionic_arguments.append(f"Score d'attraction supérieur: {bionic_product['score']}/10 vs {scoring.total_score}/10")
        if bionic_product["attraction_days"] > analysis_data.get("attraction_days", 10):
            bionic_arguments.append(f"Durée d'attraction plus longue: {bionic_product['attraction_days']} jours vs {analysis_data.get('attraction_days', 10)} jours")
        if bionic_product.get("certified") and not analysis_data.get("certified"):
            bionic_arguments.append("Certification alimentaire ACIA/CFIA garantie")
        if bionic_product.get("rainproof") and not analysis_data.get("rainproof"):
            bionic_arguments.append("Résistance aux intempéries (Rainproof)")
        if bionic_product.get("feed_proof"):
            bionic_arguments.append("100% Feed-Proof - Sécurité alimentaire garantie")
        
        # Conclusion
        if scoring.total_score >= 8:
            conclusion = f"Le produit {product_name} présente une performance d'attraction excellente avec un score de {scoring.total_score}/10."
        elif scoring.total_score >= 6:
            conclusion = f"Le produit {product_name} offre une performance d'attraction correcte ({scoring.total_score}/10) mais pourrait être optimisé."
        else:
            conclusion = f"Le produit {product_name} présente des limitations significatives ({scoring.total_score}/10). Considérez les alternatives BIONIC™."
        
        if bionic_product["score"] > scoring.total_score:
            conclusion += f" Le produit BIONIC™ {bionic_product['name']} offre une performance supérieure documentée."
        
        return AnalysisReport(
            product_name=product_name,
            technical_sheet=technical_sheet,
            scientific_analysis=scientific_analysis,
            scoring=scoring,
            comparison=comparison,
            price_analysis=price_analysis,
            recommendations=analysis_data.get("recommendations", []),
            bionic_arguments=bionic_arguments,
            conclusion=conclusion
        )
