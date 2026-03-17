"""
CORRIDORS-V10 — Classification des corridors fauniques
=========================================================
4 niveaux: OPTIMAL, FONCTIONNEL, DEGRADE, INUTILISABLE
Palette conforme au Plan de Match Steeve-MAX.
"""

CLASSIFICATION_THRESHOLDS = {
    "OPTIMAL": {"min": 75, "max": 100, "color": "#1B5E20", "label_fr": "Optimal"},
    "FONCTIONNEL": {"min": 50, "max": 74, "color": "#4CAF50", "label_fr": "Fonctionnel"},
    "DEGRADE": {"min": 25, "max": 49, "color": "#FF9800", "label_fr": "Degrade"},
    "INUTILISABLE": {"min": 0, "max": 24, "color": "#F44336", "label_fr": "Inutilisable"},
}


def classify(score: float) -> dict:
    """Classifie un score corridor (0-100) en 4 niveaux."""
    if score >= 75:
        cls = "OPTIMAL"
    elif score >= 50:
        cls = "FONCTIONNEL"
    elif score >= 25:
        cls = "DEGRADE"
    else:
        cls = "INUTILISABLE"

    info = CLASSIFICATION_THRESHOLDS[cls]
    return {
        "classe": cls,
        "label_fr": info["label_fr"],
        "color": info["color"],
        "score_range": f"{info['min']}-{info['max']}",
    }


def classify_batch(scores: list) -> dict:
    """Classifie un batch de scores et retourne des statistiques."""
    if not scores:
        return {"total": 0, "distribution": {}, "avg_score": 0, "min_score": 0, "max_score": 0}

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
        "avg_score": round(sum(scores) / total, 1),
        "min_score": round(min(scores), 1),
        "max_score": round(max(scores), 1),
    }
