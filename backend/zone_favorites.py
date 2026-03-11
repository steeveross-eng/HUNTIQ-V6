"""
Zone Favorites & Optimal Conditions Alerts System
Système de favoris de zones avec alertes 3 jours à l'avance
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import logging
import os
import httpx

# Configuration MongoDB
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "hunterpro")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
favorite_zones_collection = db["favorite_zones"]
zone_alerts_collection = db["zone_alerts"]
alert_notifications_collection = db["alert_notifications"]

router = APIRouter(prefix="/api/zones", tags=["Zone Favorites"])
logger = logging.getLogger("zone_favorites")

# ============================================
# MODÈLES PYDANTIC
# ============================================

class ZoneLocation(BaseModel):
    lat: float
    lng: float
    radius_meters: float = 200

class FavoriteZoneCreate(BaseModel):
    name: str
    module_id: str  # habitats, corridors, alimentation, etc.
    location: ZoneLocation
    notes: Optional[str] = None
    alert_enabled: bool = True
    alert_days_before: int = Field(default=3, ge=1, le=7)

class FavoriteZoneResponse(BaseModel):
    id: str
    user_id: str
    name: str
    module_id: str
    location: Dict[str, Any]
    notes: Optional[str]
    alert_enabled: bool
    alert_days_before: int
    created_at: str
    last_optimal_check: Optional[str]
    next_optimal_window: Optional[Dict[str, Any]]

class OptimalConditions(BaseModel):
    date: str
    score: int  # 0-100
    weather: Dict[str, Any]
    lunar_phase: str
    thermal_activity: str
    wind_favorable: bool
    interpretation: str

class ZoneAlert(BaseModel):
    id: str
    zone_id: str
    zone_name: str
    user_id: str
    optimal_date: str
    score: int
    conditions: Dict[str, Any]
    created_at: str
    read: bool
    notified: bool

# ============================================
# UTILITAIRES MÉTÉO ET CONDITIONS
# ============================================

async def get_weather_forecast(lat: float, lng: float, days: int = 7) -> List[Dict]:
    """Récupère les prévisions météo pour les X prochains jours"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lng,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,sunrise,sunset",
                "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,visibility",
                "timezone": "America/Toronto",
                "forecast_days": days
            }
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Weather API error: {e}")
    return None

def get_lunar_phase(date: datetime) -> Dict[str, Any]:
    """Calcule la phase lunaire pour une date donnée"""
    # Algorithme simplifié de calcul de phase lunaire
    known_new_moon = datetime(2024, 1, 11, tzinfo=timezone.utc)
    lunar_cycle = 29.53059  # jours
    
    days_since = (date - known_new_moon).total_seconds() / 86400
    phase_position = (days_since % lunar_cycle) / lunar_cycle
    
    if phase_position < 0.0625:
        phase = "new_moon"
        name = "Nouvelle Lune"
        hunting_score = 90
    elif phase_position < 0.1875:
        phase = "waxing_crescent"
        name = "Premier Croissant"
        hunting_score = 75
    elif phase_position < 0.3125:
        phase = "first_quarter"
        name = "Premier Quartier"
        hunting_score = 70
    elif phase_position < 0.4375:
        phase = "waxing_gibbous"
        name = "Gibbeuse Croissante"
        hunting_score = 65
    elif phase_position < 0.5625:
        phase = "full_moon"
        name = "Pleine Lune"
        hunting_score = 85
    elif phase_position < 0.6875:
        phase = "waning_gibbous"
        name = "Gibbeuse Décroissante"
        hunting_score = 70
    elif phase_position < 0.8125:
        phase = "last_quarter"
        name = "Dernier Quartier"
        hunting_score = 75
    else:
        phase = "waning_crescent"
        name = "Dernier Croissant"
        hunting_score = 80
    
    return {
        "phase": phase,
        "name": name,
        "position": round(phase_position, 3),
        "illumination": round(abs(0.5 - abs(phase_position - 0.5)) * 2 * 100, 1),
        "hunting_score": hunting_score
    }

def calculate_thermal_activity(temp_max: float, temp_min: float, humidity: float) -> Dict[str, Any]:
    """Calcule l'activité thermique favorable pour la chasse"""
    temp_diff = temp_max - temp_min
    
    # Meilleure activité avec différentiel de température modéré
    if 8 <= temp_diff <= 15:
        thermal_score = 90
        activity = "Excellente"
    elif 5 <= temp_diff <= 20:
        thermal_score = 75
        activity = "Bonne"
    elif temp_diff < 5:
        thermal_score = 50
        activity = "Faible"
    else:
        thermal_score = 60
        activity = "Variable"
    
    # Ajustement pour l'humidité
    if 40 <= humidity <= 70:
        thermal_score += 10
    elif humidity > 85:
        thermal_score -= 15
    
    return {
        "score": min(100, max(0, thermal_score)),
        "activity": activity,
        "temp_differential": round(temp_diff, 1),
        "humidity_impact": "favorable" if 40 <= humidity <= 70 else "défavorable"
    }

def calculate_wind_favorability(wind_speed: float, wind_direction: float, module_id: str) -> Dict[str, Any]:
    """Évalue si le vent est favorable pour le type de zone"""
    # Vent idéal selon le type de zone
    ideal_conditions = {
        "habitats": {"max_speed": 20, "ideal_speed": 8},
        "corridors": {"max_speed": 25, "ideal_speed": 12},
        "alimentation": {"max_speed": 15, "ideal_speed": 5},
        "repos": {"max_speed": 10, "ideal_speed": 3},
        "affuts": {"max_speed": 18, "ideal_speed": 8},
        "rut": {"max_speed": 20, "ideal_speed": 10},
        "fraicheur": {"max_speed": 15, "ideal_speed": 5},
        "salines": {"max_speed": 12, "ideal_speed": 4},
    }
    
    config = ideal_conditions.get(module_id, {"max_speed": 20, "ideal_speed": 10})
    
    if wind_speed <= config["ideal_speed"]:
        score = 100
        favorable = True
        description = "Conditions idéales"
    elif wind_speed <= config["max_speed"]:
        score = int(100 - ((wind_speed - config["ideal_speed"]) / (config["max_speed"] - config["ideal_speed"]) * 40))
        favorable = True
        description = "Conditions acceptables"
    else:
        score = max(20, int(60 - (wind_speed - config["max_speed"]) * 3))
        favorable = False
        description = "Vent trop fort"
    
    # Direction du vent (simplifiée)
    cardinal = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    direction_name = cardinal[int((wind_direction + 22.5) % 360 / 45)]
    
    return {
        "score": score,
        "favorable": favorable,
        "speed_kmh": round(wind_speed, 1),
        "direction": direction_name,
        "direction_degrees": wind_direction,
        "description": description
    }

async def calculate_optimal_score(lat: float, lng: float, module_id: str, target_date: datetime, weather_data: Dict = None) -> Dict[str, Any]:
    """Calcule le score optimal pour une zone à une date donnée"""
    
    # Obtenir les données météo si non fournies
    if not weather_data:
        weather_data = await get_weather_forecast(lat, lng, 7)
    
    if not weather_data:
        return None
    
    # Trouver l'index du jour dans les prévisions
    today = datetime.now(timezone.utc).date()
    target_day = target_date.date() if hasattr(target_date, 'date') else target_date
    day_index = (target_day - today).days
    
    if day_index < 0 or day_index >= len(weather_data.get("daily", {}).get("time", [])):
        return None
    
    daily = weather_data["daily"]
    
    # Données du jour cible
    temp_max = daily["temperature_2m_max"][day_index]
    temp_min = daily["temperature_2m_min"][day_index]
    precipitation = daily["precipitation_sum"][day_index]
    wind_speed = daily["wind_speed_10m_max"][day_index]
    wind_direction = daily["wind_direction_10m_dominant"][day_index]
    sunrise = daily["sunrise"][day_index]
    sunset = daily["sunset"][day_index]
    
    # Calculer les différents facteurs
    lunar = get_lunar_phase(target_date)
    thermal = calculate_thermal_activity(temp_max, temp_min, 60)  # Humidité moyenne estimée
    wind = calculate_wind_favorability(wind_speed, wind_direction, module_id)
    
    # Pénalité pour précipitations
    precip_penalty = min(30, precipitation * 5)
    
    # Score composite
    weights = {
        "lunar": 0.20,
        "thermal": 0.25,
        "wind": 0.30,
        "precipitation": 0.25
    }
    
    precip_score = max(0, 100 - precip_penalty * 3)
    
    composite_score = int(
        lunar["hunting_score"] * weights["lunar"] +
        thermal["score"] * weights["thermal"] +
        wind["score"] * weights["wind"] +
        precip_score * weights["precipitation"]
    )
    
    # Interprétation
    if composite_score >= 85:
        interpretation = "🎯 Conditions exceptionnelles - À ne pas manquer!"
    elif composite_score >= 75:
        interpretation = "✅ Très bonnes conditions de chasse"
    elif composite_score >= 65:
        interpretation = "👍 Conditions favorables"
    elif composite_score >= 50:
        interpretation = "⚠️ Conditions moyennes"
    else:
        interpretation = "❌ Conditions défavorables"
    
    return {
        "date": target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date),
        "score": composite_score,
        "interpretation": interpretation,
        "weather": {
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precipitation_mm": precipitation,
            "sunrise": sunrise,
            "sunset": sunset
        },
        "lunar": lunar,
        "thermal": thermal,
        "wind": wind,
        "factors": {
            "lunar_score": lunar["hunting_score"],
            "thermal_score": thermal["score"],
            "wind_score": wind["score"],
            "precip_score": precip_score
        }
    }

# ============================================
# ENDPOINTS API
# ============================================

@router.post("/favorites", response_model=FavoriteZoneResponse)
async def add_favorite_zone(
    zone: FavoriteZoneCreate,
    user_id: str = Query(default="anonymous", description="ID de l'utilisateur")
):
    """Ajoute une zone aux favoris de l'utilisateur"""
    
    # Vérifier si la zone existe déjà
    existing = favorite_zones_collection.find_one({
        "user_id": user_id,
        "location.lat": zone.location.lat,
        "location.lng": zone.location.lng,
        "module_id": zone.module_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Cette zone est déjà dans vos favoris")
    
    # Créer la zone favorite
    now = datetime.now(timezone.utc)
    zone_doc = {
        "user_id": user_id,
        "name": zone.name,
        "module_id": zone.module_id,
        "location": zone.location.dict(),
        "notes": zone.notes,
        "alert_enabled": zone.alert_enabled,
        "alert_days_before": zone.alert_days_before,
        "created_at": now,
        "last_optimal_check": None,
        "next_optimal_window": None
    }
    
    result = favorite_zones_collection.insert_one(zone_doc)
    zone_id = str(result.inserted_id)
    
    # Calculer les conditions optimales pour les 7 prochains jours
    optimal_windows = []
    weather_data = await get_weather_forecast(zone.location.lat, zone.location.lng, 7)
    
    for i in range(7):
        target_date = now + timedelta(days=i)
        conditions = await calculate_optimal_score(
            zone.location.lat, 
            zone.location.lng, 
            zone.module_id, 
            target_date,
            weather_data
        )
        if conditions and conditions["score"] >= 70:
            optimal_windows.append(conditions)
    
    # Mettre à jour avec les fenêtres optimales
    next_optimal = optimal_windows[0] if optimal_windows else None
    favorite_zones_collection.update_one(
        {"_id": result.inserted_id},
        {"$set": {
            "last_optimal_check": now,
            "next_optimal_window": next_optimal,
            "upcoming_optimal_windows": optimal_windows[:3]  # Top 3
        }}
    )
    
    # Créer une alerte si conditions optimales dans les X jours
    if zone.alert_enabled and optimal_windows:
        for window in optimal_windows:
            window_date = datetime.fromisoformat(window["date"].replace("Z", "+00:00")) if isinstance(window["date"], str) else window["date"]
            days_until = (window_date.date() - now.date()).days
            
            if days_until <= zone.alert_days_before and window["score"] >= 75:
                alert_doc = {
                    "zone_id": zone_id,
                    "zone_name": zone.name,
                    "user_id": user_id,
                    "optimal_date": window["date"],
                    "score": window["score"],
                    "conditions": window,
                    "created_at": now,
                    "read": False,
                    "notified": False,
                    "alert_type": "optimal_conditions"
                }
                zone_alerts_collection.insert_one(alert_doc)
    
    logger.info(f"Zone favorite ajoutée: {zone.name} pour {user_id}")
    
    return FavoriteZoneResponse(
        id=zone_id,
        user_id=user_id,
        name=zone.name,
        module_id=zone.module_id,
        location=zone.location.dict(),
        notes=zone.notes,
        alert_enabled=zone.alert_enabled,
        alert_days_before=zone.alert_days_before,
        created_at=now.isoformat(),
        last_optimal_check=now.isoformat(),
        next_optimal_window=next_optimal
    )

@router.get("/favorites")
async def get_favorite_zones(
    user_id: str = Query(default="anonymous", description="ID de l'utilisateur")
):
    """Récupère toutes les zones favorites de l'utilisateur"""
    
    zones = list(favorite_zones_collection.find({"user_id": user_id}))
    
    result = []
    for zone in zones:
        result.append({
            "id": str(zone["_id"]),
            "user_id": zone["user_id"],
            "name": zone["name"],
            "module_id": zone["module_id"],
            "location": zone["location"],
            "notes": zone.get("notes"),
            "alert_enabled": zone.get("alert_enabled", True),
            "alert_days_before": zone.get("alert_days_before", 3),
            "created_at": zone["created_at"].isoformat() if zone.get("created_at") else None,
            "last_optimal_check": zone["last_optimal_check"].isoformat() if zone.get("last_optimal_check") else None,
            "next_optimal_window": zone.get("next_optimal_window"),
            "upcoming_optimal_windows": zone.get("upcoming_optimal_windows", [])
        })
    
    return {"favorites": result, "count": len(result)}

@router.delete("/favorites/{zone_id}")
async def remove_favorite_zone(
    zone_id: str,
    user_id: str = Query(default="anonymous", description="ID de l'utilisateur")
):
    """Supprime une zone des favoris"""
    
    result = favorite_zones_collection.delete_one({
        "_id": ObjectId(zone_id),
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zone favorite non trouvée")
    
    # Supprimer les alertes associées
    zone_alerts_collection.delete_many({"zone_id": zone_id, "user_id": user_id})
    
    return {"message": "Zone retirée des favoris", "deleted": True}

@router.put("/favorites/{zone_id}/alerts")
async def update_zone_alerts(
    zone_id: str,
    alert_enabled: bool = Query(...),
    alert_days_before: int = Query(default=3, ge=1, le=7),
    user_id: str = Query(default="anonymous")
):
    """Met à jour les paramètres d'alerte d'une zone favorite"""
    
    result = favorite_zones_collection.update_one(
        {"_id": ObjectId(zone_id), "user_id": user_id},
        {"$set": {
            "alert_enabled": alert_enabled,
            "alert_days_before": alert_days_before
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Zone favorite non trouvée")
    
    return {"message": "Paramètres d'alerte mis à jour", "alert_enabled": alert_enabled}

@router.get("/favorites/{zone_id}/conditions")
async def get_zone_conditions(
    zone_id: str,
    user_id: str = Query(default="anonymous"),
    days: int = Query(default=7, ge=1, le=14)
):
    """Récupère les prévisions de conditions optimales pour une zone"""
    
    try:
        zone_oid = ObjectId(zone_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de zone invalide")
    
    zone = favorite_zones_collection.find_one({
        "_id": zone_oid,
        "user_id": user_id
    })
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone favorite non trouvée")
    
    lat = zone["location"]["lat"]
    lng = zone["location"]["lng"]
    module_id = zone["module_id"]
    
    # Obtenir les prévisions
    weather_data = await get_weather_forecast(lat, lng, days)
    
    conditions = []
    now = datetime.now(timezone.utc)
    
    for i in range(days):
        target_date = now + timedelta(days=i)
        day_conditions = await calculate_optimal_score(lat, lng, module_id, target_date, weather_data)
        if day_conditions:
            conditions.append(day_conditions)
    
    # Mettre à jour la zone avec les nouvelles prévisions
    optimal_windows = [c for c in conditions if c["score"] >= 70]
    favorite_zones_collection.update_one(
        {"_id": zone_oid},
        {"$set": {
            "last_optimal_check": now,
            "next_optimal_window": optimal_windows[0] if optimal_windows else None,
            "upcoming_optimal_windows": optimal_windows[:3]
        }}
    )
    
    return {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "module_id": module_id,
        "forecast_days": days,
        "conditions": conditions,
        "optimal_windows": optimal_windows,
        "best_day": max(conditions, key=lambda x: x["score"]) if conditions else None
    }

@router.get("/alerts")
async def get_user_alerts(
    user_id: str = Query(default="anonymous"),
    unread_only: bool = Query(default=False)
):
    """Récupère toutes les alertes de l'utilisateur"""
    
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    
    alerts = list(zone_alerts_collection.find(query).sort("created_at", -1).limit(50))
    
    result = []
    for alert in alerts:
        result.append({
            "id": str(alert["_id"]),
            "zone_id": alert["zone_id"],
            "zone_name": alert["zone_name"],
            "user_id": alert["user_id"],
            "optimal_date": alert["optimal_date"],
            "score": alert["score"],
            "conditions": alert["conditions"],
            "created_at": alert["created_at"].isoformat() if alert.get("created_at") else None,
            "read": alert.get("read", False),
            "notified": alert.get("notified", False),
            "alert_type": alert.get("alert_type", "optimal_conditions")
        })
    
    unread_count = zone_alerts_collection.count_documents({"user_id": user_id, "read": False})
    
    return {
        "alerts": result,
        "count": len(result),
        "unread_count": unread_count
    }

@router.put("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    user_id: str = Query(default="anonymous")
):
    """Marque une alerte comme lue"""
    
    result = zone_alerts_collection.update_one(
        {"_id": ObjectId(alert_id), "user_id": user_id},
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return {"message": "Alerte marquée comme lue"}

@router.put("/alerts/read-all")
async def mark_all_alerts_read(user_id: str = Query(default="anonymous")):
    """Marque toutes les alertes comme lues"""
    
    result = zone_alerts_collection.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True}}
    )
    
    return {"message": f"{result.modified_count} alertes marquées comme lues"}

@router.post("/check-optimal-conditions")
async def check_optimal_conditions_for_all_zones(
    user_id: str = Query(default="anonymous")
):
    """Vérifie les conditions optimales pour toutes les zones favorites et génère des alertes"""
    
    zones = list(favorite_zones_collection.find({
        "user_id": user_id,
        "alert_enabled": True
    }))
    
    new_alerts = []
    now = datetime.now(timezone.utc)
    
    for zone in zones:
        lat = zone["location"]["lat"]
        lng = zone["location"]["lng"]
        module_id = zone["module_id"]
        alert_days = zone.get("alert_days_before", 3)
        
        # Obtenir les prévisions
        weather_data = await get_weather_forecast(lat, lng, 7)
        
        for i in range(alert_days + 1):  # Inclure aujourd'hui
            target_date = now + timedelta(days=i)
            conditions = await calculate_optimal_score(lat, lng, module_id, target_date, weather_data)
            
            if conditions and conditions["score"] >= 75:
                # Vérifier si une alerte existe déjà pour cette date
                existing_alert = zone_alerts_collection.find_one({
                    "zone_id": str(zone["_id"]),
                    "optimal_date": conditions["date"]
                })
                
                if not existing_alert:
                    alert_doc = {
                        "zone_id": str(zone["_id"]),
                        "zone_name": zone["name"],
                        "user_id": user_id,
                        "optimal_date": conditions["date"],
                        "score": conditions["score"],
                        "conditions": conditions,
                        "created_at": now,
                        "read": False,
                        "notified": False,
                        "alert_type": "optimal_conditions",
                        "days_until": i
                    }
                    result = zone_alerts_collection.insert_one(alert_doc)
                    alert_doc["id"] = str(result.inserted_id)
                    new_alerts.append(alert_doc)
    
    return {
        "checked_zones": len(zones),
        "new_alerts": len(new_alerts),
        "alerts": new_alerts
    }

# Index pour les requêtes fréquentes
favorite_zones_collection.create_index([("user_id", 1)])
favorite_zones_collection.create_index([("user_id", 1), ("module_id", 1)])
zone_alerts_collection.create_index([("user_id", 1), ("read", 1)])
zone_alerts_collection.create_index([("zone_id", 1), ("optimal_date", 1)])
