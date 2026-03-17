"""
CORRIDORS-V10 — Classification normative officielle
=========================================================
5 niveaux obligatoires — Norme CORRIDOR-V1/V10

Niveau       | Couleur  | Largeur (m) | Signification
CRITIQUE     | #CC0000  | 4 m         | Corridor critique / ultra-frequent
MAJEUR       | #FF0000  | 6 m         | Corridor majeur / prioritaire
FORT         | #FF8C00  | 11 m        | Corridor fort / frequent
MODERE       | #FFD700  | 17 m        | Corridor modere / secondaire
FAIBLE       | #BFBFBF  | 26 m        | Corridor faible / opportuniste

Aucune variation permise. Palette thermo-intuitive obligatoire.
"""

CORRIDOR_LEVELS = {
    "CRITIQUE": {
        "min": 85, "max": 100,
        "color": "#CC0000", "pattern": "striped",
        "largeur_m": 4, "label_fr": "Critique",
        "render_weight": 6, "dash_array": "10,4",
    },
    "MAJEUR": {
        "min": 70, "max": 84,
        "color": "#FF0000", "pattern": None,
        "largeur_m": 6, "label_fr": "Majeur",
        "render_weight": 5, "dash_array": None,
    },
    "FORT": {
        "min": 50, "max": 69,
        "color": "#FF8C00", "pattern": None,
        "largeur_m": 11, "label_fr": "Fort",
        "render_weight": 4, "dash_array": None,
    },
    "MODERE": {
        "min": 30, "max": 49,
        "color": "#FFD700", "pattern": None,
        "largeur_m": 17, "label_fr": "Modere",
        "render_weight": 3, "dash_array": None,
    },
    "FAIBLE": {
        "min": 0, "max": 29,
        "color": "#BFBFBF", "pattern": None,
        "largeur_m": 26, "label_fr": "Faible",
        "render_weight": 2, "dash_array": None,
    },
}

# Ancien mapping conserve pour compatibilite scoring
CLASSIFICATION_THRESHOLDS = {
    "OPTIMAL": {"min": 75, "max": 100, "color": "#1B5E20", "label_fr": "Optimal"},
    "FONCTIONNEL": {"min": 50, "max": 74, "color": "#4CAF50", "label_fr": "Fonctionnel"},
    "DEGRADE": {"min": 25, "max": 49, "color": "#FF9800", "label_fr": "Degrade"},
    "INUTILISABLE": {"min": 0, "max": 24, "color": "#F44336", "label_fr": "Inutilisable"},
}


def classify(score: float) -> dict:
    """Classifie un score reseau global (0-100) en 4 niveaux."""
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


def classify_corridor(score: float) -> dict:
    """Classifie un corridor individuel (0-100) en 5 niveaux normatifs."""
    if score >= 85:
        lvl = "CRITIQUE"
    elif score >= 70:
        lvl = "MAJEUR"
    elif score >= 50:
        lvl = "FORT"
    elif score >= 30:
        lvl = "MODERE"
    else:
        lvl = "FAIBLE"

    info = CORRIDOR_LEVELS[lvl]
    return {
        "niveau": lvl,
        "label_fr": info["label_fr"],
        "color": info["color"],
        "pattern": info["pattern"],
        "largeur_m": info["largeur_m"],
        "render_weight": info["render_weight"],
        "dash_array": info["dash_array"],
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
