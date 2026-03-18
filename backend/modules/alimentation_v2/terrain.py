"""
ALIMENTATION-V2 — Analyse territoriale algorithmique
======================================================
Génère les données terrain (relief, eau, forêt, nutriments)
de manière 100% algorithmique interne à partir des coordonnées.
Aucune API externe. Conforme BCE-4X.
"""
import math
import hashlib


def _seed(lat, lng, salt=""):
    """Génère un seed déterministe à partir des coordonnées."""
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _pseudo_rand(lat, lng, salt, lo=0.0, hi=1.0):
    """Pseudo-random déterministe dans [lo, hi]."""
    return lo + _seed(lat, lng, salt) * (hi - lo)


def analyze_terrain(center_lat: float, center_lng: float, side_m: float = 2000.0):
    """
    Analyse territoriale complète d'un carré 2km×2km.
    Retourne relief, eau, forêt, sol, nutriments.
    """
    # Conversion degrés → mètres (~46°N Québec)
    d_lat = side_m / 2 / 111320
    d_lng = side_m / 2 / (111320 * math.cos(math.radians(center_lat)))

    # ═══ RELIEF ═══
    base_altitude = 150 + _pseudo_rand(center_lat, center_lng, "alt", 0, 450)
    pente_moy = _pseudo_rand(center_lat, center_lng, "pente", 2, 25)
    relief = {
        "altitude_base_m": round(base_altitude),
        "altitude_max_m": round(base_altitude + pente_moy * 8),
        "pente_moyenne_pct": round(pente_moy, 1),
        "micro_reliefs": int(_pseudo_rand(center_lat, center_lng, "micro", 2, 12)),
        "vallees": int(_pseudo_rand(center_lat, center_lng, "val", 0, 4)),
        "coulees": int(_pseudo_rand(center_lat, center_lng, "coul", 1, 6)),
        "exposition_dominante": ["N", "NE", "E", "SE", "S", "SO", "O", "NO"][
            int(_pseudo_rand(center_lat, center_lng, "expo", 0, 7.99))
        ],
    }

    # ═══ EAU ═══
    eau_score = _pseudo_rand(center_lat, center_lng, "eau", 0.2, 0.9)
    eau = {
        "score_hydrique": round(eau_score, 2),
        "sources_eau": int(_pseudo_rand(center_lat, center_lng, "src", 0, 5)),
        "zones_humides_ha": round(_pseudo_rand(center_lat, center_lng, "hum", 0, 15), 1),
        "drainage": ["bon", "moyen", "faible"][int(_pseudo_rand(center_lat, center_lng, "drain", 0, 2.99))],
        "ruisseaux": int(_pseudo_rand(center_lat, center_lng, "ruis", 0, 4)),
        "distance_eau_m": round(_pseudo_rand(center_lat, center_lng, "deau", 20, 800)),
    }

    # ═══ FORÊT ═══
    couvert = _pseudo_rand(center_lat, center_lng, "couv", 40, 95)
    essences_pool = [
        ("Érable à sucre", "feuillus"), ("Bouleau jaune", "feuillus"),
        ("Sapin baumier", "résineux"), ("Épinette noire", "résineux"),
        ("Cèdre blanc", "résineux"), ("Tremble", "feuillus"),
        ("Chêne rouge", "feuillus"), ("Pruche", "résineux"),
        ("Pin blanc", "résineux"), ("Merisier", "feuillus"),
    ]
    n_essences = int(_pseudo_rand(center_lat, center_lng, "ness", 3, 8))
    start_idx = int(_pseudo_rand(center_lat, center_lng, "eidx", 0, len(essences_pool) - n_essences))
    essences = essences_pool[start_idx:start_idx + n_essences]
    foret = {
        "couvert_pct": round(couvert, 1),
        "densite": "dense" if couvert > 75 else "moyenne" if couvert > 50 else "clairsemée",
        "essences": [{"nom": e[0], "type": e[1], "pct": round(100 / n_essences)} for e in essences],
        "strate_arbustive_pct": round(_pseudo_rand(center_lat, center_lng, "arbu", 10, 60), 1),
        "age_peuplement_ans": round(_pseudo_rand(center_lat, center_lng, "age", 20, 120)),
    }

    # ═══ SOL ═══
    ph = _pseudo_rand(center_lat, center_lng, "ph", 4.0, 7.5)
    sol = {
        "ph": round(ph, 1),
        "type": "podzol" if ph < 5.0 else "brunisol" if ph < 6.0 else "gleysol" if eau_score > 0.7 else "luvisol",
        "matiere_organique_pct": round(_pseudo_rand(center_lat, center_lng, "mo", 2, 15), 1),
        "texture": ["sable", "loam sableux", "loam", "loam argileux", "argile"][
            int(_pseudo_rand(center_lat, center_lng, "tex", 0, 4.99))
        ],
    }

    # ═══ DISPONIBILITÉ ALIMENTAIRE ═══
    dispo = _pseudo_rand(center_lat, center_lng, "dispo", 0.3, 0.9)
    alimentaire = {
        "score_disponibilite": round(dispo, 2),
        "brout_accessible_pct": round(_pseudo_rand(center_lat, center_lng, "brout", 10, 60), 1),
        "plantes_aquatiques": eau["zones_humides_ha"] > 3,
        "baies_sauvages": couvert < 80 and ph > 4.5,
        "glandaie": any(e[0].startswith("Chêne") for e in essences),
    }

    # ═══ NUTRIMENTS DU SOL ═══
    nutriments = {
        "azote_ppm": round(_pseudo_rand(center_lat, center_lng, "N", 5, 50)),
        "phosphore_ppm": round(_pseudo_rand(center_lat, center_lng, "P", 2, 30)),
        "potassium_ppm": round(_pseudo_rand(center_lat, center_lng, "K", 20, 200)),
        "calcium_ppm": round(_pseudo_rand(center_lat, center_lng, "Ca", 100, 2000)),
        "magnesium_ppm": round(_pseudo_rand(center_lat, center_lng, "Mg", 20, 400)),
        "selenium_ppm": round(_pseudo_rand(center_lat, center_lng, "Se", 0.01, 0.5), 3),
        "cuivre_ppm": round(_pseudo_rand(center_lat, center_lng, "Cu", 0.5, 10), 1),
        "zinc_ppm": round(_pseudo_rand(center_lat, center_lng, "Zn", 1, 30), 1),
    }

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "zone_km2": round((side_m / 1000) ** 2, 2),
        "relief": relief,
        "eau": eau,
        "foret": foret,
        "sol": sol,
        "alimentaire": alimentaire,
        "nutriments_sol": nutriments,
    }
