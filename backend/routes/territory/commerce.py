"""
Territory Module - Nutrition Analysis, BIONIC Products, Orders, Prompt Documentation
Phase 1.8 - Split from territory.py
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import HTTPException

from ._base import territory_router, get_db, logger
from .models import (
    NutritionAnalysisRequest, OrderCreate, OrderResponse, PromptDocumentation,
)


# ===========================================
# BIONIC Product Catalog
# ===========================================

BIONIC_PRODUCTS = {
    "bionic_mineral_block": {
        "id": "bionic_mineral_block",
        "name": "BIONIC\u2122 Bloc Min\u00e9ral Premium",
        "category": "minerals",
        "description": "Bloc min\u00e9ral haute performance enrichi en sodium, calcium et phosphore. Formule exclusive BIONIC\u2122 avec oligo-\u00e9l\u00e9ments essentiels pour une attraction maximale.",
        "benefits": [
            "Apport en sodium (sel) - attractif puissant",
            "Calcium et phosphore pour le d\u00e9veloppement des bois",
            "Oligo-\u00e9l\u00e9ments (zinc, cuivre, mangan\u00e8se)",
            "R\u00e9sistant aux intemp\u00e9ries"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "calcium", "phosphore", "zinc", "cuivre"],
        "price_range": "$$",
        "effectiveness_rating": 9.5,
        "image_url": "/images/products/mineral_block.jpg"
    },
    "bionic_protein_mix": {
        "id": "bionic_protein_mix",
        "name": "BIONIC\u2122 M\u00e9lange Prot\u00e9in\u00e9 For\u00eat",
        "category": "protein",
        "description": "M\u00e9lange alimentaire riche en prot\u00e9ines v\u00e9g\u00e9tales con\u00e7u pour compenser les carences en fin d'hiver et d\u00e9but de printemps.",
        "benefits": [
            "16% prot\u00e9ines v\u00e9g\u00e9tales de qualit\u00e9",
            "\u00c9nergie concentr\u00e9e pour l'hiver",
            "Favorise la croissance des bois",
            "Am\u00e9liore la condition corporelle"
        ],
        "target_species": ["orignal", "chevreuil", "ours"],
        "nutrients_provided": ["proteine", "energie", "fibres"],
        "price_range": "$$$",
        "effectiveness_rating": 9.2,
        "image_url": "/images/products/protein_mix.jpg"
    },
    "bionic_apple_attractant": {
        "id": "bionic_apple_attractant",
        "name": "BIONIC\u2122 Attractif Pomme Sauvage",
        "category": "attractant",
        "description": "Attractif liquide concentr\u00e9 \u00e0 base de pomme ferment\u00e9e. Odeur irr\u00e9sistible d\u00e9tectable \u00e0 plus de 500m.",
        "benefits": [
            "Odeur de pomme ferment\u00e9e naturelle",
            "D\u00e9tectable jusqu'\u00e0 500m",
            "Dur\u00e9e d'action 3-4 semaines",
            "Attire en toute saison"
        ],
        "target_species": ["chevreuil", "ours"],
        "nutrients_provided": ["sucres", "attraction"],
        "price_range": "$$",
        "effectiveness_rating": 8.8,
        "image_url": "/images/products/apple_attractant.jpg"
    },
    "bionic_saline_supreme": {
        "id": "bionic_saline_supreme",
        "name": "BIONIC\u2122 Saline Supr\u00eame",
        "category": "salt",
        "description": "Saline liquide concentr\u00e9e pour cr\u00e9er des sites d'attraction durables.",
        "benefits": [
            "Concentration saline optimale",
            "P\u00e9n\u00e8tre le sol en profondeur",
            "Effet attractif multi-saisons",
            "Cr\u00e9e un site de l\u00e9chage permanent"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "mineraux"],
        "price_range": "$",
        "effectiveness_rating": 9.0,
        "image_url": "/images/products/saline_supreme.jpg"
    },
    "bionic_berry_feast": {
        "id": "bionic_berry_feast",
        "name": "BIONIC\u2122 Festin de Baies",
        "category": "food",
        "description": "M\u00e9lange de baies s\u00e9ch\u00e9es et c\u00e9r\u00e9ales enrichi sp\u00e9cialement formul\u00e9 pour l'ours noir.",
        "benefits": [
            "Riche en sucres naturels",
            "Graisses v\u00e9g\u00e9tales pour l'hibernation",
            "Go\u00fbt irr\u00e9sistible pour l'ours",
            "Favorise la prise de poids pr\u00e9-hibernation"
        ],
        "target_species": ["ours"],
        "nutrients_provided": ["sucres", "graisses", "energie"],
        "price_range": "$$$",
        "effectiveness_rating": 9.3,
        "image_url": "/images/products/berry_feast.jpg"
    },
    "bionic_antler_boost": {
        "id": "bionic_antler_boost",
        "name": "BIONIC\u2122 Boost Panache",
        "category": "minerals",
        "description": "Suppl\u00e9ment min\u00e9ral sp\u00e9cialis\u00e9 pour le d\u00e9veloppement optimal des bois.",
        "benefits": [
            "Ratio Ca:P de 2:1 optimal",
            "Favorise des bois plus gros et denses",
            "Oligo-\u00e9l\u00e9ments pour la sant\u00e9 globale",
            "R\u00e9sultats visibles en une saison"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["calcium", "phosphore", "magnesium", "zinc"],
        "price_range": "$$$",
        "effectiveness_rating": 9.4,
        "image_url": "/images/products/antler_boost.jpg"
    }
}

COMPETITOR_PRODUCTS = {
    "trophy_rock": {
        "id": "trophy_rock", "name": "Trophy Rock", "category": "minerals",
        "description": "Roche min\u00e9rale naturelle import\u00e9e.",
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "calcium", "mineraux"],
        "price_range": "$$$", "effectiveness_rating": 7.5
    },
    "deer_cane": {
        "id": "deer_cane", "name": "Deer Cane", "category": "attractant",
        "description": "Attractif min\u00e9ral liquide populaire.",
        "target_species": ["chevreuil"],
        "nutrients_provided": ["sodium", "attraction"],
        "price_range": "$$", "effectiveness_rating": 7.8
    },
    "purina_mineral": {
        "id": "purina_mineral", "name": "Purina AntlerMax", "category": "minerals",
        "description": "Suppl\u00e9ment min\u00e9ral de qualit\u00e9.",
        "target_species": ["chevreuil"],
        "nutrients_provided": ["calcium", "phosphore", "proteine"],
        "price_range": "$$$$", "effectiveness_rating": 8.2
    }
}

# Species-specific nutritional needs by season and forest type
SPECIES_NUTRITION = {
    "orignal": {
        "name": "Orignal",
        "diet_type": "brouteur",
        "primary_foods": ["saule", "bouleau", "\u00e9rable \u00e0 \u00e9pis", "plantes aquatiques", "\u00e9corce"],
        "seasonal_needs": {
            "printemps": {"priority_nutrients": ["sodium", "proteine", "energie"], "deficiencies": ["sel apr\u00e8s l'hiver", "prot\u00e9ines pour croissance bois"], "notes": "P\u00e9riode critique - recherche active de salines naturelles"},
            "ete": {"priority_nutrients": ["calcium", "phosphore", "eau"], "deficiencies": ["min\u00e9raux pour bois en velours"], "notes": "Croissance maximale des bois - besoins min\u00e9raux \u00e9lev\u00e9s"},
            "automne": {"priority_nutrients": ["energie", "graisses"], "deficiencies": ["r\u00e9serves \u00e9nerg\u00e9tiques pour le rut"], "notes": "P\u00e9riode de rut - d\u00e9pense \u00e9nerg\u00e9tique intense"},
            "hiver": {"priority_nutrients": ["fibres", "energie"], "deficiencies": ["\u00e9nergie pour survivre au froid"], "notes": "Survie - alimentation r\u00e9duite, conservation d'\u00e9nergie"}
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "bon"},
            "feuillus": {"food_quality": "tr\u00e8s bon", "cover": "moyen"},
            "coniferes": {"food_quality": "moyen", "cover": "excellent"},
            "regeneration": {"food_quality": "excellent", "cover": "faible"}
        }
    },
    "chevreuil": {
        "name": "Chevreuil",
        "diet_type": "s\u00e9lectif",
        "primary_foods": ["glands", "pommes", "tr\u00e8fle", "bourgeons", "champignons"],
        "seasonal_needs": {
            "printemps": {"priority_nutrients": ["proteine", "calcium", "energie"], "deficiencies": ["prot\u00e9ines apr\u00e8s l'hiver", "min\u00e9raux pour bois"], "notes": "R\u00e9cup\u00e9ration post-hiver, d\u00e9but croissance bois"},
            "ete": {"priority_nutrients": ["calcium", "phosphore", "proteine"], "deficiencies": ["min\u00e9raux pour bois", "condition des biches gestantes"], "notes": "Croissance bois, gestation/allaitement"},
            "automne": {"priority_nutrients": ["graisses", "energie", "sucres"], "deficiencies": ["r\u00e9serves graisseuses pour l'hiver"], "notes": "Accumulation de graisse, pr\u00e9paration rut"},
            "hiver": {"priority_nutrients": ["energie", "fibres"], "deficiencies": ["\u00e9nergie, nourriture rare"], "notes": "Survie - stress alimentaire important"}
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "excellent"},
            "feuillus": {"food_quality": "excellent", "cover": "bon"},
            "coniferes": {"food_quality": "faible", "cover": "excellent"},
            "regeneration": {"food_quality": "tr\u00e8s bon", "cover": "moyen"}
        }
    },
    "ours": {
        "name": "Ours noir",
        "diet_type": "omnivore",
        "primary_foods": ["baies", "noix", "insectes", "charogne", "miel", "poissons"],
        "seasonal_needs": {
            "printemps": {"priority_nutrients": ["proteine", "graisses"], "deficiencies": ["tout apr\u00e8s hibernation", "prot\u00e9ines animales"], "notes": "Sortie hibernation - recherche intensive de nourriture"},
            "ete": {"priority_nutrients": ["proteine", "sucres", "graisses"], "deficiencies": ["vari\u00e9t\u00e9 alimentaire"], "notes": "Alimentation diversifi\u00e9e, baies en abondance"},
            "automne": {"priority_nutrients": ["graisses", "sucres", "energie"], "deficiencies": ["hyperphagie - accumulation graisses critique"], "notes": "P\u00e9riode hyperphagie - jusqu'\u00e0 20,000 cal/jour"},
            "hiver": {"priority_nutrients": [], "deficiencies": [], "notes": "Hibernation - pas d'alimentation"}
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "excellent"},
            "feuillus": {"food_quality": "tr\u00e8s bon", "cover": "bon"},
            "coniferes": {"food_quality": "moyen", "cover": "excellent"},
            "regeneration": {"food_quality": "bon", "cover": "faible"}
        }
    }
}


def generate_recommendation_reason(product: dict, gaps: list, season: str, species: str) -> str:
    reasons = []
    matching = set(product["nutrients_provided"]) & set(gaps)
    if "sodium" in matching:
        reasons.append("Comble le besoin critique en sel")
    if "calcium" in matching or "phosphore" in matching:
        reasons.append("Favorise le d\u00e9veloppement des bois")
    if "proteine" in matching:
        reasons.append("Apport prot\u00e9ique pour la r\u00e9cup\u00e9ration")
    if "energie" in matching or "graisses" in matching:
        reasons.append("Source d'\u00e9nergie concentr\u00e9e")
    if "sucres" in matching:
        reasons.append("Attraction par les sucres naturels")
    if not reasons:
        reasons.append(f"Produit adapt\u00e9 pour {species}")
    if product.get("effectiveness_rating", 0) >= 9.0:
        reasons.append("Efficacit\u00e9 prouv\u00e9e sur le terrain")
    return " \u2022 ".join(reasons)


def generate_analysis_summary(species: str, season: str, gaps: list, forest_quality: dict) -> str:
    species_names = {"orignal": "l'orignal", "chevreuil": "le chevreuil", "ours": "l'ours noir"}
    quality_text = "excellent" if forest_quality["food_quality"] == "excellent" else \
                   "bon" if forest_quality["food_quality"] in ["tr\u00e8s bon", "bon"] else "limit\u00e9"
    gap_text = ", ".join(gaps[:3]) if gaps else "aucune carence majeure"
    return (f"Analyse pour {species_names.get(species, species)} en {season}: "
            f"Le couvert forestier offre un potentiel alimentaire {quality_text}. "
            f"Carences identifi\u00e9es: {gap_text}. "
            f"Les produits BIONIC\u2122 recommand\u00e9s ciblent sp\u00e9cifiquement ces besoins.")


@territory_router.post("/analysis/nutrition")
async def analyze_nutrition_and_products(request: NutritionAnalysisRequest):
    """Analyze nutritional needs and recommend BIONIC products."""
    species_data = SPECIES_NUTRITION.get(request.species)
    if not species_data:
        raise HTTPException(status_code=400, detail="Invalid species")
    if not request.season:
        month = datetime.now().month
        if month in [3, 4, 5]: season = "printemps"
        elif month in [6, 7, 8]: season = "ete"
        elif month in [9, 10, 11]: season = "automne"
        else: season = "hiver"
    else:
        season = request.season
    seasonal_needs = species_data["seasonal_needs"][season]
    forest_quality = species_data["forest_preferences"].get(request.forest_type, {"food_quality": "moyen", "cover": "moyen"})
    food_sources = []
    if request.forest_type == "mixte":
        food_sources = ["Feuillus (bouleau, \u00e9rable)", "Conif\u00e8res (sapin, \u00e9pinette)", "Sous-bois vari\u00e9", "Arbustes fruitiers"]
    elif request.forest_type == "feuillus":
        food_sources = ["\u00c9rables", "Bouleaux", "Ch\u00eanes/glands", "Arbustes \u00e0 feuilles"]
    elif request.forest_type == "coniferes":
        food_sources = ["Sapins", "\u00c9pinettes", "Pins", "Lichens"]
    elif request.forest_type == "regeneration":
        food_sources = ["Jeunes pousses", "Arbustes", "Herbes hautes", "Framboisiers/m\u00fbriers"]
    if request.water_nearby:
        food_sources.append("Plantes aquatiques" if request.species == "orignal" else "V\u00e9g\u00e9tation riveraine")
    gaps = []
    gap_details = []
    for nutrient in seasonal_needs["priority_nutrients"]:
        gap_severity = "moderate"
        if request.forest_type == "coniferes" and nutrient in ["proteine", "sucres"]:
            gap_severity = "high"
        elif request.forest_type == "regeneration" and nutrient in ["fibres"]:
            gap_severity = "low"
        gaps.append(nutrient)
        gap_details.append({"nutrient": nutrient, "severity": gap_severity,
                            "reason": f"Besoin saisonnier ({season}) - {seasonal_needs['notes']}"})
    if request.species in ["orignal", "chevreuil"] and season == "printemps" and "sodium" not in gaps:
        gaps.append("sodium")
        gap_details.append({"nutrient": "sodium", "severity": "high",
                            "reason": "Carence critique en sel apr\u00e8s l'hiver - recherche active de salines"})
    recommended_products = []
    for product_id, product in BIONIC_PRODUCTS.items():
        if request.species in product["target_species"]:
            score = product["effectiveness_rating"]
            matching_nutrients = set(product["nutrients_provided"]) & set(gaps)
            score += len(matching_nutrients) * 1.5
            if season == "printemps" and "sodium" in product["nutrients_provided"]:
                score += 2
            if season == "automne" and ("energie" in product["nutrients_provided"] or "graisses" in product["nutrients_provided"]):
                score += 1.5
            recommended_products.append({
                **product, "relevance_score": round(score, 1),
                "matching_nutrients": list(matching_nutrients),
                "recommendation_reason": generate_recommendation_reason(product, gaps, season, request.species)
            })
    for product_id, product in COMPETITOR_PRODUCTS.items():
        if request.species in product["target_species"]:
            score = product["effectiveness_rating"] * 0.9
            matching_nutrients = set(product["nutrients_provided"]) & set(gaps)
            score += len(matching_nutrients) * 1.2
            recommended_products.append({
                **product, "relevance_score": round(score, 1),
                "matching_nutrients": list(matching_nutrients),
                "recommendation_reason": "Alternative disponible sur le march\u00e9",
                "is_competitor": True
            })
    recommended_products.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_products = recommended_products[:5]
    bionic_in_top3 = any(not p.get("is_competitor", False) for p in top_products[:3])
    if not bionic_in_top3 and recommended_products:
        for i, p in enumerate(recommended_products):
            if not p.get("is_competitor", False):
                top_products[2] = p
                break
    return {
        "location": {"latitude": request.latitude, "longitude": request.longitude},
        "species": {"id": request.species, "name": species_data["name"],
                     "diet_type": species_data["diet_type"], "primary_foods": species_data["primary_foods"]},
        "environment": {"forest_type": request.forest_type, "food_quality": forest_quality["food_quality"],
                         "cover_quality": forest_quality["cover"], "water_nearby": request.water_nearby, "season": season},
        "food_sources_available": food_sources,
        "seasonal_analysis": {"season": season, "priority_nutrients": seasonal_needs["priority_nutrients"],
                               "known_deficiencies": seasonal_needs["deficiencies"], "notes": seasonal_needs["notes"]},
        "nutritional_gaps": gap_details,
        "recommended_products": top_products,
        "summary": generate_analysis_summary(request.species, season, gaps, forest_quality)
    }


# ===========================================
# ORDERS
# ===========================================

@territory_router.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    """Create a new order pending admin approval"""
    database = await get_db()
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    order_doc = {
        "_id": order_id, "customer_name": order.customer_name,
        "customer_email": order.customer_email, "customer_phone": order.customer_phone,
        "notes": order.notes, "items": [item.dict() for item in order.items],
        "total": order.total, "source": order.source, "user_id": order.user_id,
        "status": "pending_approval", "created_at": now, "updated_at": now,
        "approved_at": None, "approved_by": None, "shipped_at": None, "tracking_number": None
    }
    await database.territory_orders.insert_one(order_doc)
    notification_doc = {
        "_id": str(uuid.uuid4()), "type": "new_order", "order_id": order_id,
        "customer_name": order.customer_name, "total": order.total,
        "items_count": len(order.items), "read": False, "created_at": now
    }
    await database.admin_notifications.insert_one(notification_doc)
    logger.info(f"New order created: {order_id} from {order.customer_name}")
    return OrderResponse(
        id=order_id, customer_name=order.customer_name,
        customer_email=order.customer_email,
        items=[item.dict() for item in order.items],
        total=order.total, status="pending_approval", created_at=now
    )


@territory_router.get("/orders")
async def list_orders(status: Optional[str] = None, limit: int = 50):
    """List orders (for admin dashboard)"""
    database = await get_db()
    query = {}
    if status:
        query["status"] = status
    orders = await database.territory_orders.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [{
        "id": str(order['_id']), "customer_name": order['customer_name'],
        "customer_email": order['customer_email'], "customer_phone": order.get('customer_phone'),
        "items": order['items'], "total": order['total'], "status": order['status'],
        "source": order.get('source', 'unknown'), "notes": order.get('notes'),
        "created_at": order['created_at'], "approved_at": order.get('approved_at'),
        "shipped_at": order.get('shipped_at')
    } for order in orders]


@territory_router.post("/orders/{order_id}/approve")
async def approve_order(order_id: str, admin_name: str = "Admin"):
    """Approve an order"""
    database = await get_db()
    now = datetime.now(timezone.utc)
    result = await database.territory_orders.update_one(
        {"_id": order_id, "status": "pending_approval"},
        {"$set": {"status": "approved", "approved_at": now, "approved_by": admin_name, "updated_at": now}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already processed")
    return {"status": "approved", "order_id": order_id, "approved_at": now}


@territory_router.post("/orders/{order_id}/reject")
async def reject_order(order_id: str, reason: str = ""):
    """Reject an order"""
    database = await get_db()
    now = datetime.now(timezone.utc)
    result = await database.territory_orders.update_one(
        {"_id": order_id, "status": "pending_approval"},
        {"$set": {"status": "rejected", "rejection_reason": reason, "updated_at": now}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already processed")
    return {"status": "rejected", "order_id": order_id, "reason": reason}


@territory_router.get("/orders/notifications")
async def get_order_notifications(unread_only: bool = True):
    """Get admin notifications for new orders"""
    database = await get_db()
    query = {}
    if unread_only:
        query["read"] = False
    notifications = await database.admin_notifications.find(query).sort("created_at", -1).limit(20).to_list(20)
    return [{
        "id": str(n['_id']), "type": n['type'], "order_id": n.get('order_id'),
        "customer_name": n.get('customer_name'), "total": n.get('total'),
        "items_count": n.get('items_count'), "read": n['read'], "created_at": n['created_at']
    } for n in notifications]


@territory_router.post("/orders/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    database = await get_db()
    await database.admin_notifications.update_one({"_id": notification_id}, {"$set": {"read": True}})
    return {"status": "marked_read"}


# ===========================================
# PROMPT DOCUMENTATION STORAGE
# ===========================================

@territory_router.post("/prompt/save")
async def save_prompt_documentation(prompt_data: PromptDocumentation):
    """Save the PROMPT documentation to database"""
    database = await get_db()
    now = datetime.now(timezone.utc)
    existing = await database.prompt_documentation.find_one({"app_name": prompt_data.app_name})
    if existing:
        await database.prompt_documentation.update_one(
            {"app_name": prompt_data.app_name},
            {"$set": {**prompt_data.dict(), "last_updated": now, "save_count": existing.get("save_count", 0) + 1}}
        )
        return {"status": "updated", "message": "Documentation mise \u00e0 jour dans la base de donn\u00e9es",
                "last_updated": now, "save_count": existing.get("save_count", 0) + 1}
    else:
        doc = {"_id": str(uuid.uuid4()), **prompt_data.dict(), "created_at": now, "last_updated": now, "save_count": 1}
        await database.prompt_documentation.insert_one(doc)
        return {"status": "created", "message": "Documentation sauvegard\u00e9e dans la base de donn\u00e9es",
                "last_updated": now, "save_count": 1}


@territory_router.get("/prompt/load")
async def load_prompt_documentation():
    """Load the saved PROMPT documentation from database"""
    database = await get_db()
    doc = await database.prompt_documentation.find_one({"app_name": "Chasse Bionic\u2122 / BIONIC\u2122"})
    if not doc:
        return None
    doc.pop("_id", None)
    return doc


@territory_router.get("/prompt/history")
async def get_prompt_save_history():
    """Get the save history of PROMPT documentation"""
    database = await get_db()
    doc = await database.prompt_documentation.find_one({"app_name": "Chasse Bionic\u2122 / BIONIC\u2122"})
    if not doc:
        return {"has_saved": False, "save_count": 0, "last_updated": None}
    return {"has_saved": True, "save_count": doc.get("save_count", 1),
            "last_updated": doc.get("last_updated"), "created_at": doc.get("created_at")}
