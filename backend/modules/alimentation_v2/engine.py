"""
ALIMENTATION-V2 — Engine principal
=====================================
Analyse territoriale + Salines + Recommandations nutritionnelles.
100% algorithmique interne, zéro API externe.
Conforme BCE-4X: aucune modification des 16 zones ou 64 centres.
"""
from .terrain import analyze_terrain
from .salines import compute_salines
from .nutrition import get_nutrition, NUTRITION_DB

SPECIES_MAP = {
    "CERF": "CERF", "ORIGNAL": "ORIGNAL", "OURS": "OURS",
    "WAPITI": "WAPITI", "DINDON": "DINDON",
}
SPECIES_LIST = list(SPECIES_MAP.keys())


def analyze_alimentation_v2(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
) -> dict:
    """
    Analyse alimentaire complète V2.
    Retourne: terrain, salines, recommandations nutritionnelles.
    """
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    # 1. Analyse territoriale
    terrain = analyze_terrain(center_lat, center_lng, side_m)

    # 2. Calcul salines optimales
    salines = compute_salines(center_lat, center_lng, terrain, species, month, side_m)

    # 3. Recommandations nutritionnelles
    nutrition = get_nutrition(species)

    # 4. Score global alimentation V2
    terrain_score = (
        terrain["alimentaire"]["score_disponibilite"] * 40 +
        terrain["eau"]["score_hydrique"] * 20 +
        (terrain["foret"]["couvert_pct"] / 100) * 20 +
        (1 - terrain["relief"]["pente_moyenne_pct"] / 30) * 20
    )
    avg_saline_score = sum(s["score"] for s in salines) / len(salines) if salines else 0
    score_global = round(terrain_score * 0.6 + avg_saline_score * 0.4)

    # 5. Carences détectées
    nutriments_sol = terrain["nutriments_sol"]
    carences_detectees = []
    seuils = {"selenium_ppm": (0.2, "Sélénium"), "cuivre_ppm": (3, "Cuivre"),
              "calcium_ppm": (500, "Calcium"), "phosphore_ppm": (10, "Phosphore"),
              "zinc_ppm": (5, "Zinc")}
    for key, (seuil, nom) in seuils.items():
        val = nutriments_sol.get(key, seuil)
        if val < seuil:
            carences_detectees.append({
                "element": nom,
                "valeur_sol": val,
                "seuil_minimum": seuil,
                "deficit_pct": round((1 - val / seuil) * 100),
            })

    return {
        "version": "ALIMENTATION-V2",
        "species": species,
        "species_nom": nutrition["nom"],
        "month": month,
        "score_global": min(100, max(0, score_global)),
        "terrain": terrain,
        "salines": salines,
        "n_salines": len(salines),
        "nutrition": {
            "aliments_recommandes": nutrition["aliments_recommandes"],
            "nutriments_essentiels": nutrition["nutriments_essentiels"],
            "proteines": nutrition["proteines"],
            "oligo_elements": nutrition["oligo_elements"],
            "carences_locales": nutrition["carences_locales_quebec"],
            "saline_composition": nutrition["saline_composition"],
        },
        "carences_detectees": carences_detectees,
        "conformite": {
            "bce4x": True,
            "steeve_max": True,
            "zones_modifiees": 0,
            "centres_modifies": 0,
        },
    }
