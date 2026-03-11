"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
BIONIC™ Territory AI Recommendations & Cartography Module
- AI-powered recommendations by species/season
- GeoJSON integration for heatmaps
- Partnership module integration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(prefix="/api/territories/ai", tags=["Territory AI & Cartography"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


# ============================================
# SPECIES & SEASON CONFIGURATION
# ============================================

SPECIES_SEASONS = {
    "orignal": {
        "name_fr": "Orignal",
        "name_en": "Moose",
        "icon": "🫎",
        "seasons": {
            "archery": {"start": "09-01", "end": "09-30", "name": "Arc"},
            "firearms": {"start": "10-01", "end": "10-31", "name": "Arme à feu"},
            "muzzleloader": {"start": "11-01", "end": "11-15", "name": "Arme à chargement par la bouche"}
        },
        "best_months": [9, 10],
        "habitat_preferences": ["forêt mixte", "bordure de lac", "marécage"],
        "behavior_tips": [
            "Actif à l'aube et au crépuscule",
            "Période du rut en septembre-octobre",
            "Recherche les zones de coupe forestière"
        ]
    },
    "chevreuil": {
        "name_fr": "Chevreuil",
        "name_en": "White-tailed Deer",
        "icon": "🦌",
        "seasons": {
            "archery": {"start": "09-15", "end": "10-31", "name": "Arc"},
            "firearms": {"start": "11-01", "end": "11-15", "name": "Arme à feu"},
            "muzzleloader": {"start": "11-16", "end": "11-30", "name": "Arme à chargement par la bouche"}
        },
        "best_months": [10, 11],
        "habitat_preferences": ["lisière de forêt", "champs agricoles", "vergers"],
        "behavior_tips": [
            "Rut intense en novembre",
            "Utilise les corridors de déplacement",
            "Actif très tôt le matin"
        ]
    },
    "ours": {
        "name_fr": "Ours noir",
        "name_en": "Black Bear",
        "icon": "🐻",
        "seasons": {
            "spring": {"start": "05-15", "end": "06-30", "name": "Printemps"},
            "fall": {"start": "09-01", "end": "10-31", "name": "Automne"}
        },
        "best_months": [5, 6, 9, 10],
        "habitat_preferences": ["forêt dense", "zones de baies", "dépotoirs naturels"],
        "behavior_tips": [
            "Très actif au printemps après l'hibernation",
            "Recherche les sources de nourriture concentrées",
            "Chasse à l'appât efficace"
        ]
    },
    "dindon": {
        "name_fr": "Dindon sauvage",
        "name_en": "Wild Turkey",
        "icon": "🦃",
        "seasons": {
            "spring": {"start": "04-25", "end": "05-31", "name": "Printemps"}
        },
        "best_months": [4, 5],
        "habitat_preferences": ["forêt mixte", "champs", "bordure de bois"],
        "behavior_tips": [
            "Période de reproduction au printemps",
            "Utiliser des appeaux",
            "Se perchent dans les arbres la nuit"
        ]
    },
    "caribou": {
        "name_fr": "Caribou",
        "name_en": "Caribou",
        "icon": "🦌",
        "seasons": {
            "firearms": {"start": "09-01", "end": "09-30", "name": "Arme à feu"}
        },
        "best_months": [9],
        "habitat_preferences": ["toundra", "taïga", "zones alpines"],
        "behavior_tips": [
            "Migrations saisonnières",
            "Chasse souvent en terrain ouvert",
            "Permis limités - tirage au sort"
        ]
    },
    "petit_gibier": {
        "name_fr": "Petit gibier",
        "name_en": "Small Game",
        "icon": "🐰",
        "seasons": {
            "general": {"start": "09-15", "end": "03-31", "name": "Général"}
        },
        "best_months": [10, 11, 12],
        "habitat_preferences": ["forêt mixte", "régénération forestière", "bordure de champs"],
        "behavior_tips": [
            "Lièvre et perdrix disponibles",
            "Utiliser un chien de chasse",
            "Meilleur après les premières neiges"
        ]
    }
}

# Hunting pressure by month (1-100)
MONTHLY_PRESSURE = {
    1: 20, 2: 15, 3: 10, 4: 25, 5: 40,
    6: 30, 7: 20, 8: 25, 9: 70, 10: 90,
    11: 85, 12: 40
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key == '_id':
            result['id'] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def get_current_season_info(species: str) -> Dict:
    """Get current hunting season info for a species"""
    if species not in SPECIES_SEASONS:
        return None
    
    config = SPECIES_SEASONS[species]
    now = datetime.now()
    current_month = now.month
    current_day = now.day
    current_date = f"{current_month:02d}-{current_day:02d}"
    
    active_season = None
    upcoming_season = None
    
    for season_type, season_info in config["seasons"].items():
        start = season_info["start"]
        end = season_info["end"]
        
        # Check if current date is in season
        if start <= current_date <= end:
            active_season = {
                "type": season_type,
                "name": season_info["name"],
                "start": start,
                "end": end,
                "status": "active"
            }
            break
        
        # Check upcoming
        if current_date < start:
            if upcoming_season is None or start < upcoming_season["start"]:
                upcoming_season = {
                    "type": season_type,
                    "name": season_info["name"],
                    "start": start,
                    "end": end,
                    "status": "upcoming"
                }
    
    return {
        "species": species,
        "species_info": {
            "name_fr": config["name_fr"],
            "name_en": config["name_en"],
            "icon": config["icon"]
        },
        "active_season": active_season,
        "upcoming_season": upcoming_season,
        "best_months": config["best_months"],
        "is_best_month": current_month in config["best_months"],
        "current_pressure": MONTHLY_PRESSURE.get(current_month, 50)
    }


def calculate_recommendation_score(territory: Dict, species: str, month: int) -> float:
    """Calculate recommendation score for a territory based on species and timing"""
    base_score = territory.get("scoring", {}).get("global_score", 50)
    
    # Species bonus if territory has this species
    species_bonus = 10 if species in territory.get("species", []) else -20
    
    # Season bonus
    species_config = SPECIES_SEASONS.get(species, {})
    best_months = species_config.get("best_months", [])
    season_bonus = 15 if month in best_months else 0
    
    # Pressure adjustment
    current_pressure = MONTHLY_PRESSURE.get(month, 50)
    territory_pressure = territory.get("scoring", {}).get("pressure_index", 50)
    
    # Lower pressure territories get bonus during high-pressure months
    if current_pressure > 70:
        pressure_bonus = (70 - territory_pressure) * 0.2
    else:
        pressure_bonus = 0
    
    # Success rate bonus
    success_rate = territory.get("success_rate", 0) or 0
    success_bonus = success_rate * 0.1
    
    final_score = base_score + species_bonus + season_bonus + pressure_bonus + success_bonus
    return max(0, min(100, round(final_score, 1)))


# ============================================
# API ENDPOINTS - AI RECOMMENDATIONS
# ============================================

@router.get("/recommendations/species/{species}")
async def get_species_recommendations(
    species: str,
    province: Optional[str] = None,
    month: Optional[int] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Get AI-powered territory recommendations for a specific species"""
    try:
        if species not in SPECIES_SEASONS:
            raise HTTPException(status_code=400, detail=f"Espèce non reconnue: {species}")
        
        # Use current month if not specified
        target_month = month or datetime.now().month
        
        # Get season info
        season_info = get_current_season_info(species)
        
        # Build query
        query = {
            "status": "active",
            "species": {"$in": [species]}
        }
        
        if province:
            query["province"] = province
        
        # Get matching territories
        territories = await db.territories.find(query).to_list(100)
        
        # Calculate recommendation scores
        recommendations = []
        for territory in territories:
            rec_score = calculate_recommendation_score(territory, species, target_month)
            territory_data = serialize_doc(territory)
            territory_data["recommendation_score"] = rec_score
            territory_data["recommendation_reasons"] = generate_recommendation_reasons(
                territory, species, target_month
            )
            recommendations.append(territory_data)
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return {
            "success": True,
            "species": species,
            "season_info": season_info,
            "target_month": target_month,
            "current_pressure": MONTHLY_PRESSURE.get(target_month, 50),
            "count": len(recommendations[:limit]),
            "recommendations": recommendations[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_recommendation_reasons(territory: Dict, species: str, month: int) -> List[str]:
    """Generate human-readable recommendation reasons"""
    reasons = []
    
    # High success rate
    success_rate = territory.get("success_rate")
    if success_rate and success_rate > 50:
        reasons.append(f"Taux de succès élevé ({success_rate}%)")
    
    # Good habitat
    habitat_index = territory.get("scoring", {}).get("habitat_index", 0)
    if habitat_index > 75:
        reasons.append("Habitat de qualité supérieure")
    
    # Low pressure
    pressure_index = territory.get("scoring", {}).get("pressure_index", 50)
    if pressure_index < 40:
        reasons.append("Faible pression de chasse")
    
    # Verified territory
    if territory.get("is_verified"):
        reasons.append("Territoire vérifié BIONIC™")
    
    # Services
    services = territory.get("services", {})
    if services.get("guided_hunts"):
        reasons.append("Chasse guidée disponible")
    if services.get("accommodation"):
        reasons.append("Hébergement sur place")
    
    # Best month for species
    species_config = SPECIES_SEASONS.get(species, {})
    if month in species_config.get("best_months", []):
        reasons.append(f"Mois optimal pour {species_config.get('name_fr', species)}")
    
    return reasons[:5]  # Max 5 reasons


@router.get("/recommendations/optimal")
async def get_optimal_recommendations(
    month: Optional[int] = None,
    province: Optional[str] = None,
    limit: int = Query(15, ge=1, le=50)
):
    """Get optimal territory recommendations considering all active species and seasons"""
    try:
        target_month = month or datetime.now().month
        
        # Get territories
        query = {"status": "active"}
        if province:
            query["province"] = province
        
        territories = await db.territories.find(query).to_list(200)
        
        recommendations = []
        
        for territory in territories:
            territory_species = territory.get("species", [])
            best_species = None
            best_score = 0
            
            # Find best species for this territory this month
            for species in territory_species:
                if species in SPECIES_SEASONS:
                    score = calculate_recommendation_score(territory, species, target_month)
                    if score > best_score:
                        best_score = score
                        best_species = species
            
            if best_species and best_score > 40:
                territory_data = serialize_doc(territory)
                territory_data["recommendation_score"] = best_score
                territory_data["recommended_species"] = best_species
                territory_data["species_info"] = SPECIES_SEASONS[best_species]
                territory_data["recommendation_reasons"] = generate_recommendation_reasons(
                    territory, best_species, target_month
                )
                recommendations.append(territory_data)
        
        # Sort by score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return {
            "success": True,
            "target_month": target_month,
            "current_pressure": MONTHLY_PRESSURE.get(target_month, 50),
            "count": len(recommendations[:limit]),
            "recommendations": recommendations[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error getting optimal recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasons")
async def get_hunting_seasons():
    """Get all hunting seasons configuration"""
    seasons = {}
    for species, config in SPECIES_SEASONS.items():
        seasons[species] = {
            "name_fr": config["name_fr"],
            "name_en": config["name_en"],
            "icon": config["icon"],
            "seasons": config["seasons"],
            "best_months": config["best_months"],
            "habitat_preferences": config["habitat_preferences"],
            "behavior_tips": config["behavior_tips"],
            "current_status": get_current_season_info(species)
        }
    
    return {
        "success": True,
        "seasons": seasons,
        "monthly_pressure": MONTHLY_PRESSURE
    }


# ============================================
# API ENDPOINTS - CARTOGRAPHY / GEOJSON
# ============================================

@router.get("/geojson")
async def get_territories_geojson(
    province: Optional[str] = None,
    establishment_type: Optional[str] = None,
    species: Optional[str] = None,
    min_score: Optional[float] = None
):
    """Get territories as GeoJSON for map integration"""
    try:
        query = {"status": "active"}
        
        if province:
            query["province"] = province
        if establishment_type:
            query["establishment_type"] = establishment_type
        if species:
            query["species"] = {"$in": [species]}
        if min_score:
            query["scoring.global_score"] = {"$gte": min_score}
        
        territories = await db.territories.find(query).to_list(500)
        
        # Province default coordinates
        province_coords = {
            "QC": {"lat": 46.8, "lon": -71.2, "spread": 4},
            "ON": {"lat": 43.7, "lon": -79.4, "spread": 3},
            "NB": {"lat": 46.1, "lon": -66.1, "spread": 1.5},
            "NS": {"lat": 44.6, "lon": -63.6, "spread": 1},
            "NL": {"lat": 53.1, "lon": -57.5, "spread": 3},
            "MB": {"lat": 49.9, "lon": -98.8, "spread": 3},
            "SK": {"lat": 52.1, "lon": -106.7, "spread": 3},
            "AB": {"lat": 53.5, "lon": -114.1, "spread": 3},
            "BC": {"lat": 49.3, "lon": -123.1, "spread": 4},
            "YT": {"lat": 64.0, "lon": -135.0, "spread": 3},
            "NT": {"lat": 64.0, "lon": -125.0, "spread": 4}
        }
        
        features = []
        for idx, territory in enumerate(territories):
            coords = territory.get("coordinates", {}) or {}
            prov = territory.get("province", "QC")
            prov_default = province_coords.get(prov, province_coords["QC"])
            
            # Get or generate coordinates
            lat = coords.get("latitude")
            lon = coords.get("longitude")
            
            if not lat or not lon:
                # Generate coordinates based on province with offset for visual separation
                spread = prov_default["spread"]
                # Use index for deterministic but spread placement
                offset_lat = ((idx * 17) % 100) / 100 * spread - spread/2
                offset_lon = ((idx * 23) % 100) / 100 * spread - spread/2
                lat = prov_default["lat"] + offset_lat
                lon = prov_default["lon"] + offset_lon
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "id": str(territory.get("_id")),
                    "internal_id": territory.get("internal_id"),
                    "name": territory.get("name"),
                    "establishment_type": territory.get("establishment_type"),
                    "province": prov,
                    "region": territory.get("region"),
                    "global_score": territory.get("scoring", {}).get("global_score", 0),
                    "success_rate": territory.get("success_rate"),
                    "species": territory.get("species", []),
                    "is_verified": territory.get("is_verified", False),
                    "is_partner": territory.get("is_partner", False)
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_features": len(features),
                "filters": {
                    "province": province,
                    "establishment_type": establishment_type,
                    "species": species,
                    "min_score": min_score
                }
            }
        }
        
        return geojson
        
    except Exception as e:
        logger.error(f"Error generating GeoJSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap/{metric}")
async def get_heatmap_data(
    metric: str,  # "score", "success", "pressure", "density"
    province: Optional[str] = None
):
    """Get heatmap data for territories"""
    try:
        valid_metrics = ["score", "success", "pressure", "density"]
        if metric not in valid_metrics:
            raise HTTPException(status_code=400, detail=f"Métrique invalide. Valides: {valid_metrics}")
        
        query = {"status": "active"}
        if province:
            query["province"] = province
        
        territories = await db.territories.find(query).to_list(500)
        
        heatmap_points = []
        
        for territory in territories:
            coords = territory.get("coordinates") or {}
            
            # Get value based on metric
            if metric == "score":
                value = territory.get("scoring", {}).get("global_score", 0)
            elif metric == "success":
                value = territory.get("success_rate", 0) or 0
            elif metric == "pressure":
                value = 100 - territory.get("scoring", {}).get("pressure_index", 50)  # Invert for heatmap
            elif metric == "density":
                value = territory.get("scoring", {}).get("habitat_index", 50)
            else:
                value = 50
            
            # Get or generate coordinates
            lat = coords.get("latitude")
            lon = coords.get("longitude")
            
            if not lat or not lon:
                province_coords = {
                    "QC": [-71.2, 46.8],
                    "ON": [-79.4, 43.7],
                    "NB": [-66.1, 46.1],
                    "NL": [-57.5, 53.1],
                    "AB": [-114.1, 53.5],
                    "BC": [-123.1, 49.3],
                    "SK": [-106.7, 52.1]
                }
                default = province_coords.get(territory.get("province", "QC"), [-71.2, 46.8])
                lon = default[0] + random.uniform(-3, 3)
                lat = default[1] + random.uniform(-3, 3)
            
            heatmap_points.append({
                "lat": lat,
                "lon": lon,
                "value": value,
                "name": territory.get("name"),
                "id": str(territory.get("_id"))
            })
        
        return {
            "success": True,
            "metric": metric,
            "points": heatmap_points,
            "count": len(heatmap_points),
            "legend": {
                "score": "Score BIONIC™ (0-100)",
                "success": "Taux de succès (%)",
                "pressure": "Indice de disponibilité (inversé)",
                "density": "Qualité d'habitat"
            }.get(metric)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - PARTNERSHIP INTEGRATION
# ============================================

@router.get("/potential-partners")
async def get_potential_partners(
    min_score: float = Query(60, ge=0, le=100),
    province: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Get territories that could become partners (high score, not yet partners)"""
    try:
        query = {
            "status": "active",
            "is_partner": {"$ne": True},
            "scoring.global_score": {"$gte": min_score}
        }
        
        if province:
            query["province"] = province
        
        territories = await db.territories.find(query).sort([
            ("scoring.global_score", -1),
            ("is_verified", -1)
        ]).limit(limit).to_list(limit)
        
        potential_partners = []
        for territory in territories:
            partner_data = serialize_doc(territory)
            
            # Calculate partnership score
            base_score = territory.get("scoring", {}).get("global_score", 0)
            verified_bonus = 10 if territory.get("is_verified") else 0
            website_bonus = 5 if territory.get("website") else 0
            contact_bonus = 5 if territory.get("email") or territory.get("phone") else 0
            
            partner_data["partnership_score"] = base_score + verified_bonus + website_bonus + contact_bonus
            partner_data["partnership_potential"] = "Élevé" if partner_data["partnership_score"] > 80 else "Moyen"
            
            potential_partners.append(partner_data)
        
        return {
            "success": True,
            "count": len(potential_partners),
            "potential_partners": potential_partners
        }
        
    except Exception as e:
        logger.error(f"Error getting potential partners: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{territory_id}/convert-to-partner")
async def convert_to_partner(territory_id: str):
    """Convert a territory to partner status and create partnership request"""
    try:
        # Find territory
        try:
            query = {"_id": ObjectId(territory_id)}
        except:
            query = {"internal_id": territory_id}
        
        territory = await db.territories.find_one(query)
        
        if not territory:
            raise HTTPException(status_code=404, detail="Territoire non trouvé")
        
        if territory.get("is_partner"):
            raise HTTPException(status_code=400, detail="Déjà partenaire")
        
        # Update territory
        await db.territories.update_one(
            query,
            {"$set": {
                "is_partner": True,
                "partner_since": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Create partnership request
        partnership_request = {
            "company_name": territory.get("name"),
            "partner_type": territory.get("establishment_type"),
            "contact_name": "Auto-généré depuis inventaire",
            "email": territory.get("email", ""),
            "phone": territory.get("phone", ""),
            "website": territory.get("website", ""),
            "description": territory.get("description", ""),
            "services": territory.get("species", []),
            "status": "approved",
            "source": "territory_inventory",
            "territory_id": str(territory.get("_id")),
            "submitted_at": datetime.now(timezone.utc),
            "approved_at": datetime.now(timezone.utc)
        }
        
        await db.partner_requests.insert_one(partnership_request)
        
        return {
            "success": True,
            "message": f"{territory.get('name')} converti en partenaire",
            "territory_id": territory_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to partner: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/partner-territories")
async def get_partner_territories(limit: int = Query(50, ge=1, le=200)):
    """Get all territories that are partners"""
    try:
        territories = await db.territories.find({
            "status": "active",
            "is_partner": True
        }).sort([("scoring.global_score", -1)]).limit(limit).to_list(limit)
        
        return {
            "success": True,
            "count": len(territories),
            "partners": [serialize_doc(t) for t in territories]
        }
        
    except Exception as e:
        logger.error(f"Error getting partner territories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("Territory AI & Cartography module initialized")
