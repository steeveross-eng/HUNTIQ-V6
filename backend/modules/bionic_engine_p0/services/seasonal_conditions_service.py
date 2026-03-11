"""
MODULE PHASE E — Service Conditions Saisonnières
BIONIC V5 — Module 100% isolé

Calcule les conditions saisonnières pour un point géographique:
  - Météo estimée (température, vent, précipitations, pression)
  - Phénologie (phase saisonnière, activité végétale, période de rut)
  - Pression de chasse (intensité, jours restants saison)
  - Score global des conditions

Backend = seule source de vérité.
0 lien transversal avec le pipeline organique.
0 dépendance externe requise (calculs basés sur modèles saisonniers).
"""

import math
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

logger = logging.getLogger("bionic_engine.seasonal_conditions")

# ─── Constantes saisonnières Québec ───────────────────────────────────────

# Températures moyennes mensuelles (°C) — Région de Québec
TEMP_MONTHLY_AVG = {
    1: -12.8, 2: -10.5, 3: -4.2, 4: 4.1, 5: 11.8, 6: 17.5,
    7: 20.2, 8: 18.9, 9: 13.6, 10: 7.0, 11: 0.2, 12: -8.6,
}

# Précipitations moyennes mensuelles (mm)
PRECIP_MONTHLY_AVG = {
    1: 86, 2: 70, 3: 73, 4: 78, 5: 100, 6: 111,
    7: 120, 8: 113, 9: 117, 10: 105, 11: 104, 12: 99,
}

# Vitesse moyenne du vent (km/h)
WIND_MONTHLY_AVG = {
    1: 18, 2: 17, 3: 17, 4: 16, 5: 14, 6: 12,
    7: 11, 8: 11, 9: 12, 10: 14, 11: 16, 12: 17,
}

# Pression atmosphérique moyenne (hPa)
PRESSURE_MONTHLY_AVG = {
    1: 1018, 2: 1017, 3: 1015, 4: 1013, 5: 1013, 6: 1013,
    7: 1014, 8: 1015, 9: 1016, 10: 1017, 11: 1017, 12: 1018,
}

# Saisons de chasse au Québec (approximatif)
HUNTING_SEASONS = {
    "orignal_arc": {"start": (9, 10), "end": (10, 25)},
    "orignal_arme": {"start": (10, 26), "end": (11, 10)},
    "chevreuil_arc": {"start": (9, 25), "end": (10, 28)},
    "chevreuil_arme": {"start": (11, 1), "end": (11, 15)},
    "ours_automne": {"start": (8, 25), "end": (10, 31)},
    "dindon": {"start": (4, 25), "end": (5, 31)},
    "petit_gibier": {"start": (9, 15), "end": (3, 31)},
}

# Phases phénologiques
PHENOLOGY_PHASES = [
    {"id": "dormance", "months": [12, 1, 2], "veg_activity": 0.05, "label": "Dormance hivernale"},
    {"id": "pre_debourrement", "months": [3], "veg_activity": 0.15, "label": "Pre-debourrement"},
    {"id": "debourrement", "months": [4], "veg_activity": 0.40, "label": "Debourrement"},
    {"id": "croissance", "months": [5, 6], "veg_activity": 0.85, "label": "Croissance active"},
    {"id": "maturite", "months": [7, 8], "veg_activity": 1.0, "label": "Maturite estivale"},
    {"id": "senescence", "months": [9, 10], "veg_activity": 0.60, "label": "Senescence automnale"},
    {"id": "chute_feuilles", "months": [11], "veg_activity": 0.20, "label": "Chute des feuilles"},
]

# Périodes de rut
RUT_PERIODS = {
    "orignal": {"peak_start": (9, 15), "peak_end": (10, 15), "pre_rut_days": 14, "post_rut_days": 10},
    "chevreuil": {"peak_start": (11, 1), "peak_end": (11, 25), "pre_rut_days": 14, "post_rut_days": 7},
}


def _deterministic_variation(lat: float, lng: float, day_of_year: int, seed_str: str) -> float:
    """Variation deterministe basee sur position + jour."""
    h = hashlib.md5(f"{lat:.3f}_{lng:.3f}_{day_of_year}_{seed_str}".encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1  # [-1, 1]


def _get_current_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "hiver"
    elif month in [3, 4, 5]:
        return "printemps"
    elif month in [6, 7, 8]:
        return "ete"
    return "automne"


def _get_phenology(month: int) -> Dict[str, Any]:
    for phase in PHENOLOGY_PHASES:
        if month in phase["months"]:
            return {
                "phase_id": phase["id"],
                "label": phase["label"],
                "vegetation_activity": phase["veg_activity"],
            }
    return {"phase_id": "unknown", "label": "Inconnu", "vegetation_activity": 0.5}


def _get_rut_status(now: datetime) -> Dict[str, Any]:
    results = {}
    for species, period in RUT_PERIODS.items():
        peak_start = datetime(now.year, period["peak_start"][0], period["peak_start"][1], tzinfo=timezone.utc)
        peak_end = datetime(now.year, period["peak_end"][0], period["peak_end"][1], tzinfo=timezone.utc)
        pre_rut_start = peak_start - timedelta(days=period["pre_rut_days"])
        post_rut_end = peak_end + timedelta(days=period["post_rut_days"])

        if pre_rut_start <= now <= peak_start:
            status = "pre_rut"
            intensity = (now - pre_rut_start).days / period["pre_rut_days"]
        elif peak_start <= now <= peak_end:
            mid = peak_start + (peak_end - peak_start) / 2
            dist = abs((now - mid).total_seconds()) / ((peak_end - peak_start).total_seconds() / 2)
            status = "rut_actif"
            intensity = 1.0 - dist * 0.3
        elif peak_end <= now <= post_rut_end:
            status = "post_rut"
            intensity = 1.0 - (now - peak_end).days / period["post_rut_days"]
        else:
            status = "inactif"
            intensity = 0.0

        results[species] = {
            "status": status,
            "intensity": round(max(0, min(1, intensity)), 2),
            "peak_start": peak_start.strftime("%d/%m"),
            "peak_end": peak_end.strftime("%d/%m"),
        }
    return results


def _get_hunting_pressure(now: datetime) -> Dict[str, Any]:
    active_seasons = []
    for name, dates in HUNTING_SEASONS.items():
        start = datetime(now.year, dates["start"][0], dates["start"][1], tzinfo=timezone.utc)
        end = datetime(now.year, dates["end"][0], dates["end"][1], tzinfo=timezone.utc)
        if end < start:
            end = end.replace(year=now.year + 1)

        if start <= now <= end:
            days_remaining = (end - now).days
            total_days = (end - start).days
            progress = 1 - (days_remaining / max(1, total_days))
            active_seasons.append({
                "id": name,
                "label": name.replace("_", " ").title(),
                "days_remaining": days_remaining,
                "progress": round(progress, 2),
            })

    if active_seasons:
        pressure_intensity = min(1.0, len(active_seasons) * 0.35 + 0.3)
        label = "Elevee" if pressure_intensity > 0.7 else "Moderee" if pressure_intensity > 0.4 else "Faible"
    else:
        pressure_intensity = 0.05
        label = "Tres faible"

    return {
        "intensity": round(pressure_intensity, 2),
        "label": label,
        "active_seasons": active_seasons,
        "total_active": len(active_seasons),
    }


def compute_seasonal_conditions(lat: float, lng: float) -> Dict[str, Any]:
    """
    Calcul complet des conditions saisonnières pour un point.
    Module 100% isolé, 0 transversalité.

    Returns:
        Dict avec météo, phénologie, pression, score global.
    """
    now = datetime.now(timezone.utc)
    month = now.month
    day_of_year = now.timetuple().tm_yday
    hour = now.hour

    # ─── 1. Météo estimée ─────────────────────────────────────────────
    temp_base = TEMP_MONTHLY_AVG.get(month, 5.0)
    # Variation diurne: +3°C midi, -3°C nuit
    diurnal = 3.0 * math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 18 else -2.0
    # Variation géographique: latitude plus haute = plus froid
    lat_correction = (46.8 - lat) * 1.2
    # Variation déterministe pour unicité par position
    var = _deterministic_variation(lat, lng, day_of_year, "temp")
    temperature = round(temp_base + diurnal + lat_correction + var * 2.5, 1)

    wind_base = WIND_MONTHLY_AVG.get(month, 14)
    wind_var = _deterministic_variation(lat, lng, day_of_year, "wind")
    wind_speed = round(max(0, wind_base + wind_var * 8), 1)
    wind_direction = int((_deterministic_variation(lat, lng, day_of_year, "wdir") + 1) * 180)

    precip_base = PRECIP_MONTHLY_AVG.get(month, 90)
    precip_daily = round(max(0, precip_base / 30 + _deterministic_variation(lat, lng, day_of_year, "precip") * 3), 1)

    pressure_base = PRESSURE_MONTHLY_AVG.get(month, 1015)
    pressure_var = _deterministic_variation(lat, lng, day_of_year, "press")
    pressure = round(pressure_base + pressure_var * 8, 1)

    # Tendance pression (simule hausse/baisse)
    pressure_yesterday = pressure_base + _deterministic_variation(lat, lng, day_of_year - 1, "press") * 8
    pressure_trend = "hausse" if pressure > pressure_yesterday + 1 else "baisse" if pressure < pressure_yesterday - 1 else "stable"

    humidity = round(max(30, min(98, 70 + _deterministic_variation(lat, lng, day_of_year, "hum") * 20)), 0)

    # Condition météo
    if precip_daily > 5:
        condition = "neige" if temperature < 0 else "pluie"
    elif humidity > 85:
        condition = "brouillard" if temperature < 5 else "nuageux"
    elif humidity > 60:
        condition = "partiellement_nuageux"
    else:
        condition = "degaje"

    meteo = {
        "temperature_c": temperature,
        "ressenti_c": round(temperature - wind_speed * 0.15, 1),
        "vent_kmh": wind_speed,
        "vent_direction_deg": wind_direction,
        "precipitations_mm": precip_daily,
        "pression_hpa": pressure,
        "pression_tendance": pressure_trend,
        "humidite_pct": int(humidity),
        "condition": condition,
        "heure_utc": now.strftime("%H:%M"),
    }

    # ─── 2. Phénologie ────────────────────────────────────────────────
    season = _get_current_season(month)
    phenology = _get_phenology(month)

    # Durée du jour (approximation pour latitude ~47°N)
    declination = 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
    hour_angle = math.acos(-math.tan(math.radians(lat)) * math.tan(math.radians(declination)))
    day_length_hours = round(2 * math.degrees(hour_angle) / 15, 1)

    sunrise_hour = round(12 - day_length_hours / 2, 1)
    sunset_hour = round(12 + day_length_hours / 2, 1)

    rut_status = _get_rut_status(now)

    phenologie = {
        "saison": season,
        "phase": phenology,
        "rut": rut_status,
        "duree_jour_h": day_length_hours,
        "lever_soleil": f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}",
        "coucher_soleil": f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}",
    }

    # ─── 3. Pression de chasse ────────────────────────────────────────
    pression = _get_hunting_pressure(now)

    # ─── 4. Score global ──────────────────────────────────────────────
    # Facteurs positifs pour la chasse:
    score_meteo = 0
    # Pression barométrique en hausse = bon
    if pressure_trend == "hausse":
        score_meteo += 25
    elif pressure_trend == "stable":
        score_meteo += 15
    else:
        score_meteo += 5
    # Vent faible = bon
    if wind_speed < 10:
        score_meteo += 25
    elif wind_speed < 20:
        score_meteo += 15
    else:
        score_meteo += 5
    # Pas de pluie forte = bon
    if precip_daily < 1:
        score_meteo += 25
    elif precip_daily < 5:
        score_meteo += 15
    else:
        score_meteo += 5
    # Température confortable
    if -5 <= temperature <= 15:
        score_meteo += 25
    elif -15 <= temperature <= 25:
        score_meteo += 15
    else:
        score_meteo += 5

    score_phenologie = int(phenology["vegetation_activity"] * 40)
    max_rut = max((r["intensity"] for r in rut_status.values()), default=0)
    score_rut = int(max_rut * 30)
    score_pression = int((1 - pression["intensity"]) * 30)

    score_global = min(100, score_meteo + score_phenologie + score_rut + score_pression)

    if score_global >= 80:
        rating = "excellent"
    elif score_global >= 60:
        rating = "bon"
    elif score_global >= 40:
        rating = "moyen"
    else:
        rating = "defavorable"

    return {
        "meteo": meteo,
        "phenologie": phenologie,
        "pression_chasse": pression,
        "score": {
            "global": score_global,
            "rating": rating,
            "detail": {
                "meteo": score_meteo,
                "phenologie": score_phenologie,
                "rut": score_rut,
                "faible_pression": score_pression,
            },
        },
        "position": {"lat": lat, "lng": lng},
        "timestamp": now.isoformat(),
        "date_locale": now.strftime("%d/%m/%Y %H:%M UTC"),
    }
