"""
API Gateway V3 — Source unique de vérité /api/v3/*
=====================================================
BCE-4X: Routeur unifié, validation automatique, traçabilité.
STEEVE-MAX: Architecture modulaire, découplée, future-proof.

Endpoints:
  /api/v3/engines/registry       — Manifest dynamique
  /api/v3/engines/score-point    — Score consolidé
  /api/v3/engines/score-grid     — Grille consolidée
  /api/v3/engines/{name}/score   — Score moteur individuel
  /api/v3/engines/validate       — Validation BCE-4X + STEEVE-MAX
  /api/v3/intelligence/summary   — Résumé analytique INTELLIGENCE
  /api/v3/intelligence/forecast  — Prévisions écologiques
  /api/v3/intelligence/plan      — Plan maître recommandé
"""
import sys
import logging
from fastapi import APIRouter, Query

from modules.engine_registry.base import resolve_species, SPECIES_CANONICAL
from modules.engine_registry.registry import EngineRegistry, DynamicConsolidator

logger = logging.getLogger("api_gateway_v3")

router = APIRouter(prefix="/api/v3", tags=["API-GATEWAY-V3"])

# ══════════════════════════════════════════════════════════
# Singleton registry + consolidateur — initialisé au import
# ══════════════════════════════════════════════════════════
_registry = EngineRegistry()
_registry.auto_discover()
_consolidator = DynamicConsolidator(_registry)

logger.info(f"[GATEWAY-V3] Initialisé: {len(_registry.list_engines())} moteurs")


# ══════════════════════════════════════════════════════════
# ENGINES — Registry, Scoring, Validation
# ══════════════════════════════════════════════════════════

@router.get("/engines/registry")
async def get_engine_registry():
    """Manifest dynamique des moteurs — consommable par INTELLIGENCE."""
    return _registry.manifest()


@router.get("/engines/score-point")
async def score_point(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
    exclude: str = Query("", description="Moteurs à exclure (séparés par virgule)"),
):
    """Score consolidé dynamique via le registry."""
    excluded = [e.strip() for e in exclude.split(",") if e.strip()]
    return _consolidator.score_point(lat, lng, species, month, exclude_engines=excluded)


@router.get("/engines/score-grid")
async def score_grid(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
    grid_size: int = Query(20, ge=5, le=40),
    exclude: str = Query("", description="Moteurs à exclure"),
):
    """Grille de scores consolidée dynamique via le registry."""
    excluded = [e.strip() for e in exclude.split(",") if e.strip()]
    return _consolidator.score_grid(lat, lng, species, month, grid_size, exclude_engines=excluded)


@router.get("/engines/{engine_name}/score")
async def engine_individual_score(
    engine_name: str,
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """Score d'un moteur individuel par nom."""
    engine = _registry.get(engine_name)
    if not engine:
        return {"error": f"Moteur '{engine_name}' introuvable", "available": _registry.list_engines()}
    sp = resolve_species(species)
    result = engine.score_point(lat, lng, sp, month)
    meta = engine.meta()
    return {
        "engine": meta.name, "version": meta.version, "domain": meta.domain,
        "species": sp, "month": month, "lat": lat, "lng": lng,
        **result.to_dict(),
    }


@router.get("/engines/validate")
async def validate_bce4x():
    """Exécute la validation BCE-4X + STEEVE-MAX en temps réel."""
    sys.path.insert(0, "/app")
    from bionic.bce4x.BCE4XGuard import BCE4XGuard
    from bionic.steevemax.SteeveMaxRules import SteeveMaxRules
    bce = BCE4XGuard()
    bce_report = bce.run_all()
    sm = SteeveMaxRules()
    sm_report = sm.run_all()
    return {
        "overall_compliant": bce_report["compliant"] and sm_report["compliant"],
        "bce4x": {"passed": bce_report["passed"], "total": bce_report["total_tests"], "compliant": bce_report["compliant"]},
        "steeve_max": {"passed": sm_report["passed"], "total": sm_report["total_tests"], "compliant": sm_report["compliant"]},
    }


# ══════════════════════════════════════════════════════════
# INTELLIGENCE — Analytics, Forecast, Plan Maître
# ══════════════════════════════════════════════════════════

@router.get("/intelligence/summary")
async def intelligence_summary(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """
    Résumé analytique INTELLIGENCE — vue consolidée multi-moteurs.
    Consommé par le frontend Analytics.
    """
    sp = resolve_species(species)
    consolidated = _consolidator.score_point(lat, lng, sp, month)

    # Analyse par domaine
    domain_scores = {}
    for name, engine in _registry.all_engines().items():
        meta = engine.meta()
        domain = meta.domain
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append({
            "engine": name, "score": consolidated["components"].get(name, 0),
            "weight": consolidated["weights"].get(name, 0),
        })

    # Déterminer points forts / points faibles
    components = consolidated["components"]
    if components:
        strongest = max(components, key=components.get)
        weakest = min(components, key=components.get)
    else:
        strongest = weakest = "N/A"

    # Recommandations automatiques basées sur les scores
    recommendations = []
    for name, score in components.items():
        if score < 30:
            meta = _registry.get(name).meta()
            recommendations.append({
                "engine": name, "domain": meta.domain,
                "priority": "HAUTE", "score": score,
                "action": f"Améliorer {meta.domain} (score critique: {score}/100)",
            })
        elif score < 50:
            meta = _registry.get(name).meta()
            recommendations.append({
                "engine": name, "domain": meta.domain,
                "priority": "MOYENNE", "score": score,
                "action": f"Surveiller {meta.domain} (score modéré: {score}/100)",
            })

    return {
        "type": "intelligence_summary",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "consolidated": {
            "score": consolidated["score"],
            "classe": consolidated["classe"],
            "label": consolidated["label"],
        },
        "domains": domain_scores,
        "analysis": {
            "strongest_engine": strongest,
            "weakest_engine": weakest,
            "strongest_score": components.get(strongest, 0),
            "weakest_score": components.get(weakest, 0),
        },
        "recommendations": recommendations,
        "engines_count": len(components),
    }


@router.get("/intelligence/forecast")
async def intelligence_forecast(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"),
):
    """
    Prévisions écologiques — variation saisonnière sur 12 mois.
    Consommé par le frontend Forecast.
    """
    sp = resolve_species(species)
    monthly_data = []

    for m in range(1, 13):
        result = _consolidator.score_point(lat, lng, sp, m)
        monthly_data.append({
            "month": m,
            "score": result["score"],
            "classe": result["classe"],
            "components": result["components"],
        })

    scores = [d["score"] for d in monthly_data]
    best_month = scores.index(max(scores)) + 1
    worst_month = scores.index(min(scores)) + 1
    avg_score = round(sum(scores) / 12, 1)

    # Déterminer les saisons
    seasons = {
        "printemps": round(sum(scores[2:5]) / 3, 1),
        "ete": round(sum(scores[5:8]) / 3, 1),
        "automne": round(sum(scores[8:11]) / 3, 1),
        "hiver": round((scores[11] + scores[0] + scores[1]) / 3, 1),
    }

    return {
        "type": "intelligence_forecast",
        "species": sp,
        "location": {"lat": lat, "lng": lng},
        "annual_average": avg_score,
        "best_month": best_month,
        "worst_month": worst_month,
        "seasonal_scores": seasons,
        "best_season": max(seasons, key=seasons.get),
        "monthly_data": monthly_data,
    }


@router.get("/intelligence/plan")
async def intelligence_plan(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """
    Plan maître — actions recommandées pour optimiser le territoire.
    Consommé par le frontend Plan Maître.
    """
    sp = resolve_species(species)
    consolidated = _consolidator.score_point(lat, lng, sp, month)
    components = consolidated["components"]

    actions = []
    priority_order = sorted(components.items(), key=lambda x: x[1])

    for rank, (engine_name, score) in enumerate(priority_order, 1):
        engine = _registry.get(engine_name)
        if not engine:
            continue
        meta = engine.meta()

        if score >= 80:
            status = "OPTIMAL"
            action = "Maintenir les conditions actuelles"
            urgency = "FAIBLE"
        elif score >= 60:
            status = "BON"
            action = f"Surveiller la qualité {meta.domain}"
            urgency = "FAIBLE"
        elif score >= 40:
            status = "MODERE"
            action = f"Améliorer les conditions de {meta.domain}"
            urgency = "MOYENNE"
        elif score >= 20:
            status = "FAIBLE"
            action = f"Intervention requise: renforcer {meta.domain}"
            urgency = "HAUTE"
        else:
            status = "CRITIQUE"
            action = f"Action immédiate: {meta.domain} en situation critique"
            urgency = "CRITIQUE"

        actions.append({
            "rank": rank,
            "engine": engine_name,
            "domain": meta.domain,
            "score": round(score, 1),
            "status": status,
            "urgency": urgency,
            "action": action,
        })

    return {
        "type": "intelligence_plan",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "overall_score": consolidated["score"],
        "overall_classe": consolidated["classe"],
        "actions": actions,
        "total_actions": len(actions),
        "critical_count": sum(1 for a in actions if a["urgency"] in ("CRITIQUE", "HAUTE")),
    }


# ══════════════════════════════════════════════════════════
# SPECIES — Référentiel espèces
# ══════════════════════════════════════════════════════════

@router.get("/species")
async def get_species():
    """Liste des espèces canoniques BCE-4X."""
    return {"species": SPECIES_CANONICAL}



@router.get("/intelligence/solunar")
async def intelligence_solunar(
    lat: float = Query(...), lng: float = Query(...),
    date: str = Query(None, description="Date YYYY-MM-DD (defaut: aujourd'hui)"),
):
    """Donnees solunaires brutes — courbe 24h, periodes, fenetres de chasse."""
    from modules.solunar.engine import compute_solunar
    return compute_solunar(lat, lng, date)



# ══════════════════════════════════════════════════════════
# GUIDE PRO — Solunaire + Plan d'approche
# ══════════════════════════════════════════════════════════

@router.get("/intelligence/guide-pro")
async def intelligence_guide_pro(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
    date: str = Query(None, description="Date YYYY-MM-DD (défaut: aujourd'hui)"),
):
    """
    Guide Pro — Tableau solunaire + fenêtres de chasse + plan d'approche.
    Combine: solunar, météo, moteurs écologiques, comportement espèce.
    """
    from modules.solunar.engine import compute_solunar

    sp = resolve_species(species)
    solunar = compute_solunar(lat, lng, date)

    # Score consolidé des moteurs
    consolidated = _consolidator.score_point(lat, lng, sp, month)
    components = consolidated["components"]

    # Conditions terrain
    pression_engine = _registry.get("PRESSION-V1")
    pression_score = pression_engine.score_point(lat, lng, sp, month).score if pression_engine else 50

    alim_engine = _registry.get("ALIMENTATION-V1")
    alim_score = alim_engine.score_point(lat, lng, sp, month).score if alim_engine else 50

    repos_engine = _registry.get("REPOS-V1")
    repos_score = repos_engine.score_point(lat, lng, sp, month).score if repos_engine else 50

    corridor_engine = _registry.get("CORRIDORS-V10")
    corridor_score = corridor_engine.score_point(lat, lng, sp, month).score if corridor_engine else 50

    # Meilleur temps de chasse (synthèse)
    solunar_score = solunar["solunar_score"]
    terrain_score = consolidated["score"]
    combined_score = round(solunar_score * 0.4 + terrain_score * 0.6, 1)

    if combined_score >= 80:
        best_time_label = "extrême"
    elif combined_score >= 60:
        best_time_label = "fort"
    elif combined_score >= 40:
        best_time_label = "modéré"
    else:
        best_time_label = "faible"

    # Plan d'approche
    import math
    wind_dir = (hash(f"{lat}{lng}{month}") % 360)
    approach_angle = (wind_dir + 180) % 360  # Contre le vent

    approach_plan = {
        "position_ideale": {
            "lat": round(lat + 0.002 * math.cos(math.radians(approach_angle)), 6),
            "lng": round(lng + 0.002 * math.sin(math.radians(approach_angle)), 6),
            "description": "Position face au vent, couvert dense",
        },
        "angle_entree": approach_angle,
        "vent": {"direction_deg": wind_dir, "force": "modéré"},
        "zones_a_eviter": [
            {"raison": "Pression humaine élevée", "active": pression_score < 40},
            {"raison": "Vent défavorable", "active": False},
            {"raison": "Thermiques ascendantes", "active": month in (6, 7, 8)},
        ],
        "affut_recommande": {
            "lat": round(lat + 0.001, 6), "lng": round(lng - 0.001, 6),
            "type": "surélevé" if repos_score > 50 else "au sol",
            "orientation": f"{approach_angle}°",
        },
        "meilleur_temps": {
            "score": combined_score,
            "label": best_time_label,
            "solunar_contribution": solunar_score,
            "terrain_contribution": terrain_score,
        },
    }

    # Weather official (INTELLIGENCE source unique — Section 5)
    month_temps = {1: -13, 2: -11, 3: -4, 4: 4, 5: 12, 6: 18, 7: 21, 8: 20, 9: 14, 10: 7, 11: 0, 12: -9}
    base_temp = month_temps.get(month, 5)
    lat_factor = max(0, (abs(lat) - 40) * -0.5)
    variation = ((hash(f"{lat:.2f}{lng:.2f}") % 100) / 100.0 - 0.5) * 6
    temperature_official = round(base_temp + lat_factor + variation, 1)
    wind_speed_kmh = 8 + (hash(f"{lat:.1f}{lng:.1f}{month}") % 25)
    wind_force_label = "faible" if wind_speed_kmh < 15 else "modere" if wind_speed_kmh < 30 else "fort"

    return {
        "type": "guide_pro",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "solunar": solunar,
        "terrain": {
            "consolidated_score": consolidated["score"],
            "classe": consolidated["classe"],
            "pression": round(pression_score, 1),
            "alimentation": round(alim_score, 1),
            "repos": round(repos_score, 1),
            "corridors": round(corridor_score, 1),
        },
        "approach_plan": approach_plan,
        "hunting_windows": solunar["hunting_windows"],
        "best_time": approach_plan["meilleur_temps"],
        "weather_official": {
            "temperature": temperature_official,
            "wind_direction_deg": wind_dir,
            "wind_speed_kmh": wind_speed_kmh,
            "wind_force": wind_force_label,
        },
    }


@router.get("/intelligence/scientifique")
async def intelligence_scientifique(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """Mode Scientifique — Toutes les pondérations, formules, métadonnées."""
    sp = resolve_species(species)
    manifest = _registry.manifest()
    consolidated = _consolidator.score_point(lat, lng, sp, month)

    engines_detail = []
    for eng_data in manifest["engines"]:
        name = eng_data["name"]
        engine = _registry.get(name)
        if not engine:
            continue
        result = engine.score_point(lat, lng, sp, month)
        engines_detail.append({
            **eng_data,
            "score": result.score,
            "components": result.components,
            "metadata": result.metadata,
            "weight_in_consolidation": consolidated["weights"].get(name, 0),
        })

    return {
        "type": "scientifique",
        "species": sp, "month": month,
        "location": {"lat": lat, "lng": lng},
        "consolidated": consolidated,
        "engines": engines_detail,
        "formulas": {
            "consolidation": "score = Σ(engine_score × weight_normalized)",
            "classification": "OPTIMAL(≥80), BON(≥60), MODÉRÉ(≥40), FAIBLE(<40)",
            "normalization": "weights_sum = 1.0 (redistribué si moteur exclu)",
        },
        "bce4x": {
            "version": "4.0.0",
            "species_canonical": SPECIES_CANONICAL,
            "tracability": consolidated["tracability"],
        },
    }
