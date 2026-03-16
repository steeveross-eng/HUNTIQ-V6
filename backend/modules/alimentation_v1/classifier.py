"""
ALIMENTATION-V1 — Classification des zones alimentaires
=========================================================
4 niveaux: OPTIMALE, TRÈS BONNE, UTILISABLE, FAIBLE
"""

CLASSIFICATION_THRESHOLDS = {
    "OPTIMALE": {"min": 80, "max": 100, "color": "#1B5E20", "label_fr": "Optimale"},
    "TRES_BONNE": {"min": 60, "max": 79, "color": "#4CAF50", "label_fr": "Très bonne"},
    "UTILISABLE": {"min": 40, "max": 59, "color": "#FF9800", "label_fr": "Utilisable"},
    "FAIBLE": {"min": 0, "max": 39, "color": "#F44336", "label_fr": "Faible"},
}


def classify(score: float) -> dict:
    """Classifie un score alimentaire (0-100) en 4 niveaux."""
    if score >= 80:
        cls = "OPTIMALE"
    elif score >= 60:
        cls = "TRES_BONNE"
    elif score >= 40:
        cls = "UTILISABLE"
    else:
        cls = "FAIBLE"

    info = CLASSIFICATION_THRESHOLDS[cls]
    return {
        "classe": cls,
        "label_fr": info["label_fr"],
        "color": info["color"],
        "score_range": f"{info['min']}-{info['max']}",
    }


def classify_batch(scores: list) -> dict:
    """Classifie un batch de scores et retourne des statistiques."""
    results = [classify(s) for s in scores]
    counts = {}
    for r in results:
        cls = r["classe"]
        counts[cls] = counts.get(cls, 0) + 1

    total = len(scores)
    distribution = {}
    for cls, info in CLASSIFICATION_THRESHOLDS.items():
        count = counts.get(cls, 0)
        distribution[cls] = {
            "count": count,
            "pct": round(100 * count / max(total, 1), 1),
            "label_fr": info["label_fr"],
            "color": info["color"],
        }

    return {
        "total": total,
        "distribution": distribution,
        "avg_score": round(sum(scores) / max(total, 1), 1) if scores else 0,
        "min_score": round(min(scores), 1) if scores else 0,
        "max_score": round(max(scores), 1) if scores else 0,
    }
