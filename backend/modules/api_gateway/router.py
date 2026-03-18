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
