"""
REPOS-V1 — Classification des zones de repos
===============================================
4 niveaux: OPTIMAL, TRÈS BON, UTILISABLE, FAIBLE
"""

CLASSIFICATION_THRESHOLDS = {
    "OPTIMAL": {"min": 80, "max": 100, "color": "#1565C0", "label_fr": "Optimal"},
    "TRES_BON": {"min": 60, "max": 79, "color": "#42A5F5", "label_fr": "Très bon"},
    "UTILISABLE": {"min": 40, "max": 59, "color": "#FF9800", "label_fr": "Utilisable"},
    "FAIBLE": {"min": 0, "max": 39, "color": "#F44336", "label_fr": "Faible"},
}


def classify(score: float) -> dict:
    if score >= 80:
        cls = "OPTIMAL"
    elif score >= 60:
        cls = "TRES_BON"
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
