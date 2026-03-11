"""Product Database - AI Engine

Complete product databases for BIONIC and competitors.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

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


def get_bionic_product(product_type: str) -> dict:
    """Get BIONIC product by type"""
    return BIONIC_PRODUCTS.get(product_type, BIONIC_PRODUCTS["granules"])


def get_competitors(product_type: str) -> list:
    """Get competitor products by type"""
    return COMPETITOR_PRODUCTS.get(product_type, COMPETITOR_PRODUCTS["granules"])


def detect_category(product_name: str) -> str:
    """Auto-detect product category from name"""
    product_lower = product_name.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in product_lower:
                return category
    
    return "granules"  # Default
