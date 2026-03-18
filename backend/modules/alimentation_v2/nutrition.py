"""
ALIMENTATION-V2 — Base de données nutritionnelle statique
============================================================
Recommandations espèce-spécifique: aliments, nutriments, protéines,
oligo-éléments, corrections de carences locales.
"""

NUTRITION_DB = {
    "CERF": {
        "nom": "Chevreuil (Cerf de Virginie)",
        "aliments_recommandes": [
            {"nom": "Pommes (malus)", "saison": "automne", "priorite": "haute", "apport": "Énergie rapide, sucres naturels"},
            {"nom": "Maïs concassé", "saison": "hiver", "priorite": "haute", "apport": "Glucides, énergie hivernale"},
            {"nom": "Avoine roulée", "saison": "toute", "priorite": "moyenne", "apport": "Fibres, protéines végétales"},
            {"nom": "Luzerne (foin)", "saison": "hiver", "priorite": "haute", "apport": "Protéines, calcium, fibres"},
            {"nom": "Trèfle blanc", "saison": "printemps-été", "priorite": "haute", "apport": "Protéines 18-25%, phosphore"},
            {"nom": "Branches de cèdre", "saison": "hiver", "priorite": "moyenne", "apport": "Fibres, huiles essentielles"},
        ],
        "nutriments_essentiels": [
            {"nom": "Calcium", "besoin_mg_jour": 12000, "source": "Luzerne, os broyés"},
            {"nom": "Phosphore", "besoin_mg_jour": 8000, "source": "Trèfle, grains"},
            {"nom": "Sodium", "besoin_mg_jour": 4000, "source": "Saline minérale"},
            {"nom": "Potassium", "besoin_mg_jour": 6000, "source": "Végétaux verts"},
        ],
        "proteines": {"besoin_pct": 16, "sources": ["Luzerne", "Trèfle", "Soya"], "note": "Critique pour croissance des bois (mars-août)"},
        "oligo_elements": [
            {"nom": "Sélénium", "besoin_mg_jour": 0.3, "carence_symptome": "Myopathie, faiblesse musculaire"},
            {"nom": "Cuivre", "besoin_mg_jour": 10, "carence_symptome": "Pelage terne, anémie"},
            {"nom": "Zinc", "besoin_mg_jour": 50, "carence_symptome": "Retard de croissance bois"},
            {"nom": "Manganèse", "besoin_mg_jour": 40, "carence_symptome": "Problèmes reproductifs"},
            {"nom": "Iode", "besoin_mg_jour": 0.5, "carence_symptome": "Goitre, métabolisme ralenti"},
        ],
        "carences_locales_quebec": [
            "Sélénium déficient dans 80% des sols laurentiens",
            "Cuivre faible en terrain acide (pH < 5.5)",
            "Sodium rare naturellement — salines essentielles",
        ],
        "saline_composition": {
            "sel_mineral_pct": 40, "calcium_pct": 15, "phosphore_pct": 10,
            "selenium_ppm": 30, "cuivre_ppm": 1500, "zinc_ppm": 3000,
            "manganese_ppm": 2000, "iode_ppm": 100,
        },
    },
    "ORIGNAL": {
        "nom": "Orignal",
        "aliments_recommandes": [
            {"nom": "Saule (branches)", "saison": "hiver", "priorite": "haute", "apport": "Fibres, écorce nutritive"},
            {"nom": "Bouleau blanc (branches)", "saison": "hiver", "priorite": "haute", "apport": "Écorce, bourgeons"},
            {"nom": "Nénuphars", "saison": "été", "priorite": "haute", "apport": "Sodium naturel, minéraux aquatiques"},
            {"nom": "Érable à sucre (feuilles)", "saison": "printemps-été", "priorite": "moyenne", "apport": "Sucres, calcium"},
            {"nom": "Pommes sauvages", "saison": "automne", "priorite": "moyenne", "apport": "Énergie, vitamines"},
            {"nom": "Plantes aquatiques", "saison": "été", "priorite": "haute", "apport": "Sodium, potassium, magnésium"},
        ],
        "nutriments_essentiels": [
            {"nom": "Sodium", "besoin_mg_jour": 15000, "source": "Plantes aquatiques, salines"},
            {"nom": "Calcium", "besoin_mg_jour": 20000, "source": "Branches de saule, feuillus"},
            {"nom": "Phosphore", "besoin_mg_jour": 14000, "source": "Végétation mixte"},
            {"nom": "Magnésium", "besoin_mg_jour": 5000, "source": "Plantes aquatiques"},
        ],
        "proteines": {"besoin_pct": 14, "sources": ["Saule", "Plantes aquatiques", "Trèfle"], "note": "Panaches massifs nécessitent apport constant mars-sept"},
        "oligo_elements": [
            {"nom": "Sélénium", "besoin_mg_jour": 0.8, "carence_symptome": "Maladie du muscle blanc chez faons"},
            {"nom": "Cuivre", "besoin_mg_jour": 20, "carence_symptome": "Anémie, dépigmentation"},
            {"nom": "Zinc", "besoin_mg_jour": 80, "carence_symptome": "Croissance panaches réduite"},
            {"nom": "Cobalt", "besoin_mg_jour": 0.1, "carence_symptome": "Déficience B12, émaciation"},
        ],
        "carences_locales_quebec": [
            "Sodium critique — orignal cherche activement les salines",
            "Sélénium très déficient dans les sols boréaux",
            "Cobalt rare en sol granitique du Bouclier canadien",
        ],
        "saline_composition": {
            "sel_mineral_pct": 50, "calcium_pct": 12, "phosphore_pct": 8,
            "selenium_ppm": 50, "cuivre_ppm": 2000, "zinc_ppm": 4000,
            "cobalt_ppm": 50, "iode_ppm": 150,
        },
    },
    "OURS": {
        "nom": "Ours noir",
        "aliments_recommandes": [
            {"nom": "Bleuets sauvages", "saison": "été-automne", "priorite": "haute", "apport": "Sucres, antioxydants, énergie"},
            {"nom": "Framboises", "saison": "été", "priorite": "haute", "apport": "Sucres rapides, vitamines"},
            {"nom": "Glands de chêne", "saison": "automne", "priorite": "haute", "apport": "Lipides, protéines, énergie hivernale"},
            {"nom": "Maïs", "saison": "automne", "priorite": "moyenne", "apport": "Glucides, graisse pré-hibernation"},
            {"nom": "Miel (ruches)", "saison": "été", "priorite": "moyenne", "apport": "Sucres concentrés, protéines (larves)"},
            {"nom": "Poisson (frayères)", "saison": "printemps", "priorite": "haute", "apport": "Protéines, oméga-3, calcium"},
        ],
        "nutriments_essentiels": [
            {"nom": "Lipides", "besoin_mg_jour": 0, "source": "Glands, noix, poisson — 60% alimentation pré-hibernation"},
            {"nom": "Calcium", "besoin_mg_jour": 8000, "source": "Os, poisson, insectes"},
            {"nom": "Fer", "besoin_mg_jour": 50, "source": "Viande, insectes, végétaux"},
        ],
        "proteines": {"besoin_pct": 20, "sources": ["Insectes", "Poisson", "Petits mammifères"], "note": "Hyperphagie automnale: 20000 kcal/jour"},
        "oligo_elements": [
            {"nom": "Fer", "besoin_mg_jour": 50, "carence_symptome": "Anémie, fatigue"},
            {"nom": "Zinc", "besoin_mg_jour": 30, "carence_symptome": "Pelage terne, cicatrisation lente"},
            {"nom": "Sélénium", "besoin_mg_jour": 0.5, "carence_symptome": "Faiblesse musculaire"},
        ],
        "carences_locales_quebec": [
            "Fer variable selon le substrat rocheux",
            "Sources protéiques limitées en forêt boréale dense",
            "Calcium déficient en l'absence de frayères",
        ],
        "saline_composition": {
            "sel_mineral_pct": 30, "calcium_pct": 20, "phosphore_pct": 12,
            "fer_ppm": 5000, "zinc_ppm": 2000, "selenium_ppm": 25,
        },
    },
    "WAPITI": {
        "nom": "Wapiti",
        "aliments_recommandes": [
            {"nom": "Fétuque élevée", "saison": "printemps-été", "priorite": "haute", "apport": "Protéines 12-18%, fibres"},
            {"nom": "Luzerne", "saison": "toute", "priorite": "haute", "apport": "Protéines 20%+, calcium"},
            {"nom": "Avoine", "saison": "automne-hiver", "priorite": "haute", "apport": "Énergie, glucides"},
            {"nom": "Trèfle rouge", "saison": "printemps-été", "priorite": "moyenne", "apport": "Protéines, phosphore"},
            {"nom": "Branches de tremble", "saison": "hiver", "priorite": "moyenne", "apport": "Écorce nutritive, fibres"},
            {"nom": "Pommes", "saison": "automne", "priorite": "moyenne", "apport": "Sucres, énergie rapide"},
        ],
        "nutriments_essentiels": [
            {"nom": "Calcium", "besoin_mg_jour": 25000, "source": "Luzerne, salines minérales"},
            {"nom": "Phosphore", "besoin_mg_jour": 18000, "source": "Grains, trèfle"},
            {"nom": "Sodium", "besoin_mg_jour": 8000, "source": "Salines"},
            {"nom": "Magnésium", "besoin_mg_jour": 4000, "source": "Végétaux verts"},
        ],
        "proteines": {"besoin_pct": 18, "sources": ["Luzerne", "Trèfle", "Fétuque"], "note": "Bois massifs: besoin protéique élevé avril-août"},
        "oligo_elements": [
            {"nom": "Sélénium", "besoin_mg_jour": 0.6, "carence_symptome": "Maladie du muscle blanc"},
            {"nom": "Cuivre", "besoin_mg_jour": 15, "carence_symptome": "Pelage décoloré, boiterie"},
            {"nom": "Zinc", "besoin_mg_jour": 60, "carence_symptome": "Croissance bois insuffisante"},
            {"nom": "Manganèse", "besoin_mg_jour": 50, "carence_symptome": "Infertilité, déformations osseuses"},
        ],
        "carences_locales_quebec": [
            "Sélénium critique dans les Laurentides",
            "Cuivre déficient en terrain tourbeux",
            "Sodium rare — salines indispensables pour wapiti captif/semi-captif",
        ],
        "saline_composition": {
            "sel_mineral_pct": 45, "calcium_pct": 18, "phosphore_pct": 12,
            "selenium_ppm": 40, "cuivre_ppm": 2500, "zinc_ppm": 3500,
            "manganese_ppm": 2500, "iode_ppm": 120,
        },
    },
}

# Alias
NUTRITION_DB["DINDON"] = {
    "nom": "Dindon sauvage",
    "aliments_recommandes": [
        {"nom": "Maïs", "saison": "automne-hiver", "priorite": "haute", "apport": "Énergie, glucides"},
        {"nom": "Glands", "saison": "automne", "priorite": "haute", "apport": "Lipides, protéines"},
        {"nom": "Insectes", "saison": "printemps-été", "priorite": "haute", "apport": "Protéines animales"},
        {"nom": "Baies sauvages", "saison": "été-automne", "priorite": "moyenne", "apport": "Vitamines, sucres"},
    ],
    "nutriments_essentiels": [
        {"nom": "Calcium", "besoin_mg_jour": 3000, "source": "Coquilles, os broyés, gravier"},
        {"nom": "Phosphore", "besoin_mg_jour": 2000, "source": "Grains, insectes"},
    ],
    "proteines": {"besoin_pct": 22, "sources": ["Insectes", "Légumineuses"], "note": "Poussins: 28% protéines requises"},
    "oligo_elements": [
        {"nom": "Sélénium", "besoin_mg_jour": 0.2, "carence_symptome": "Myopathie"},
        {"nom": "Zinc", "besoin_mg_jour": 20, "carence_symptome": "Plumage terne"},
    ],
    "carences_locales_quebec": ["Calcium limité en sol acide", "Protéines animales rares en hiver"],
    "saline_composition": {"sel_mineral_pct": 25, "calcium_pct": 25, "phosphore_pct": 15, "selenium_ppm": 20, "zinc_ppm": 1500},
}


def get_nutrition(species: str) -> dict:
    """Retourne les recommandations nutritionnelles pour une espèce."""
    return NUTRITION_DB.get(species.upper(), NUTRITION_DB["CERF"])
