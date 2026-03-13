"""
BIONIC V3 — Donnees Territoriales Enrichies
=============================================
Genere des donnees realistes (ville, code postal, altitude, type territoire,
gestionnaire, acces proprietaire) basees sur les coordonnees GPS des hotspots
dans les regions du Quebec.
"""

import math
import random

# ══════════════════════════════════════════════════════════
# ZEC, POURVOIRIES, RESERVES FAUNIQUES REELLES DU QUEBEC
# ══════════════════════════════════════════════════════════

TERRITORIES_DB = {
    "laurentides": {
        "villes": ["Mont-Tremblant", "Saint-Donat", "Saint-Jovite", "Sainte-Agathe-des-Monts", "Val-David", "Labelle", "La Conception", "Nominingue"],
        "codes_postaux": ["J8E", "J0T", "J8E", "J8C", "J0T", "J0W", "J0T", "J0W"],
        "zecs": [
            {"nom": "ZEC Normandie", "tel": "819-424-2255", "courriel": "info@zecnormandie.com", "web": "zecnormandie.com"},
            {"nom": "ZEC Mazana", "tel": "819-275-2412", "courriel": "info@zecmazana.ca", "web": "zecmazana.ca"},
            {"nom": "ZEC Lesueur", "tel": "819-425-5381", "courriel": "info@zeclesueur.com", "web": "zeclesueur.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Oscar", "tel": "819-278-3422", "courriel": "info@lacoscar.com", "web": "lacoscar.com"},
            {"nom": "Pourvoirie Kanawata", "tel": "819-424-7887", "courriel": "info@kanawata.com", "web": "kanawata.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique Rouge-Matawin", "tel": "819-424-1333", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/rom"},
            {"nom": "Reserve faunique Papineau-Labelle", "tel": "819-454-2011", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/pal"},
        ],
        "altitude_range": [200, 600],
    },
    "outaouais": {
        "villes": ["Maniwaki", "Gracefield", "Low", "Kazabazua", "Montcerf-Lytton", "Aumond", "Grand-Remous"],
        "codes_postaux": ["J9E", "J0X", "J0X", "J0X", "J0W", "J0W", "J0W"],
        "zecs": [
            {"nom": "ZEC Bras-Coupe-Desert", "tel": "819-449-3435", "courriel": "info@zecbcd.com", "web": "zecbrascoupe.com"},
            {"nom": "ZEC Pontiac", "tel": "819-648-5689", "courriel": "info@zecpontiac.com", "web": "zecpontiac.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Serpent", "tel": "819-438-2888", "courriel": "info@lacserpent.com", "web": "lacserpent.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique La Verendrye", "tel": "819-438-2017", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/lvy"},
        ],
        "altitude_range": [150, 450],
    },
    "lanaudiere": {
        "villes": ["Saint-Michel-des-Saints", "Saint-Zenon", "Chertsey", "Rawdon", "Saint-Donat", "Saint-Come", "Sainte-Emelie-de-l'Energie"],
        "codes_postaux": ["J0K", "J0K", "J0K", "J0K", "J0T", "J0K", "J0K"],
        "zecs": [
            {"nom": "ZEC Lavigne", "tel": "450-884-5511", "courriel": "info@zeclavigne.com", "web": "zeclavigne.com"},
            {"nom": "ZEC des Nymphes", "tel": "450-886-3456", "courriel": "info@zecdesnymphes.ca", "web": "zecdesnymphes.ca"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Taureau", "tel": "450-833-5500", "courriel": "info@lactaureau.com", "web": "lactaureau.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique Mastigouche", "tel": "819-265-6052", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/mas"},
        ],
        "altitude_range": [200, 550],
    },
    "mauricie": {
        "villes": ["La Tuque", "Saint-Alexis-des-Monts", "Saint-Mathieu-du-Parc", "Sainte-Thecle", "Shawinigan", "Grandes-Piles"],
        "codes_postaux": ["G9X", "J0K", "G0X", "G0X", "G9N", "G0X"],
        "zecs": [
            {"nom": "ZEC Chapeau-de-Paille", "tel": "819-523-6242", "courriel": "info@zecchapeaudepaille.ca", "web": "zecchapeaudepaille.ca"},
            {"nom": "ZEC du Gros-Brochet", "tel": "819-537-8856", "courriel": "info@zecgrosbrochet.com", "web": "zecgrosbrochet.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie Lac-a-Beauce", "tel": "819-265-3191", "courriel": "info@lacabeauce.com", "web": "lacabeauce.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique du Saint-Maurice", "tel": "819-646-5687", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/stm"},
            {"nom": "Reserve faunique Mastigouche", "tel": "819-265-6052", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/mas"},
        ],
        "altitude_range": [150, 500],
    },
    "estrie": {
        "villes": ["Lac-Megantic", "Coaticook", "Weedon", "Scotstown", "Stornoway", "Cookshire-Eaton"],
        "codes_postaux": ["G6B", "J1A", "J0B", "J0B", "G0Y", "J0B"],
        "zecs": [
            {"nom": "ZEC Louise-Gosford", "tel": "819-544-3655", "courriel": "info@zeclg.ca", "web": "zeclg.ca"},
            {"nom": "ZEC Saint-Romain", "tel": "819-486-2332", "courriel": "info@zecsaintromain.com", "web": "zecsaintromain.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Saint-Pierre", "tel": "819-652-2501", "courriel": "info@lacsaintpierre.com", "web": "lacsaintpierre.com"},
        ],
        "reserves": [],
        "altitude_range": [250, 700],
    },
    "saguenay": {
        "villes": ["Alma", "Dolbeau-Mistassini", "Roberval", "Saint-Felicien", "Chibougamau", "La Baie", "Jonquiere"],
        "codes_postaux": ["G8B", "G8L", "G8H", "G8K", "G8P", "G7B", "G7X"],
        "zecs": [
            {"nom": "ZEC Martin-Valin", "tel": "418-236-4641", "courriel": "info@zecmartinvalin.com", "web": "zecmartinvalin.com"},
            {"nom": "ZEC de la Riviere-aux-Rats", "tel": "418-276-3155", "courriel": "info@zecrats.com", "web": "zecrats.com"},
            {"nom": "ZEC Onatchiway", "tel": "418-679-1444", "courriel": "info@zeconatchiway.com", "web": "zeconatchiway.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Paul", "tel": "418-344-1000", "courriel": "info@pourvlacpaul.com", "web": "pourvlacpaul.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique des Laurentides", "tel": "418-528-6868", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/lau"},
            {"nom": "Reserve faunique Ashuapmushuan", "tel": "418-256-3806", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/ash"},
        ],
        "altitude_range": [100, 800],
        "autochtone": {"nation": "Nation innue de Mashteuiatsh", "tel": "418-275-2473", "web": "mashteuiatsh.ca"},
    },
    "capitale_nationale": {
        "villes": ["Stoneham", "Lac-Beauport", "Shannon", "Saint-Raymond", "Portneuf", "Donnacona"],
        "codes_postaux": ["G3C", "G3B", "G0A", "G3L", "G0A", "G3M"],
        "zecs": [
            {"nom": "ZEC Batiscan-Neilson", "tel": "418-337-4777", "courriel": "info@zecbn.ca", "web": "zecbn.ca"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Blanc", "tel": "418-848-2173", "courriel": "info@lacblanc.qc.ca", "web": "lacblanc.qc.ca"},
        ],
        "reserves": [
            {"nom": "Reserve faunique de Portneuf", "tel": "418-323-2021", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/por"},
        ],
        "altitude_range": [150, 600],
    },
    "chaudiere_appalaches": {
        "villes": ["Thetford Mines", "Saint-Georges", "Montmagny", "Levis", "Sainte-Marie", "Beauceville"],
        "codes_postaux": ["G6G", "G5Y", "G5V", "G6V", "G6E", "G5X"],
        "zecs": [
            {"nom": "ZEC Jaro", "tel": "418-336-3464", "courriel": "info@zecjaro.com", "web": "zecjaro.com"},
        ],
        "pourvoiries": [],
        "reserves": [],
        "altitude_range": [200, 650],
    },
    "bas_saint_laurent": {
        "villes": ["Rimouski", "Riviere-du-Loup", "Temiscouata-sur-le-Lac", "Matane", "Amqui", "Trois-Pistoles"],
        "codes_postaux": ["G5L", "G5R", "G0L", "G4W", "G5J", "G0L"],
        "zecs": [
            {"nom": "ZEC Owen", "tel": "418-856-5155", "courriel": "info@zecowen.com", "web": "zecowen.com"},
            {"nom": "ZEC Casault", "tel": "418-629-4212", "courriel": "info@zeccasault.com", "web": "zeccasault.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Temiscouata", "tel": "418-899-6744", "courriel": "info@lactemiscouata.ca", "web": "lactemiscouata.ca"},
        ],
        "reserves": [
            {"nom": "Reserve faunique de Rimouski", "tel": "418-735-2226", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/rim"},
        ],
        "altitude_range": [50, 450],
    },
    "abitibi": {
        "villes": ["Val-d'Or", "Rouyn-Noranda", "Amos", "La Sarre", "Senneterre", "Malartic"],
        "codes_postaux": ["J9P", "J9X", "J9T", "J9Z", "J0Y", "J0Y"],
        "zecs": [
            {"nom": "ZEC Kipawa", "tel": "819-627-9588", "courriel": "info@zeckipawa.com", "web": "zeckipawa.com"},
            {"nom": "ZEC Maganasipi", "tel": "819-627-3030", "courriel": "info@zecmaganasipi.com", "web": "zecmaganasipi.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie Air Tamarac", "tel": "819-747-1547", "courriel": "info@airtamarac.com", "web": "airtamarac.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique La Verendrye", "tel": "819-438-2017", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/lvy"},
        ],
        "altitude_range": [250, 500],
        "autochtone": {"nation": "Nation algonquine Anishinabe de Lac-Simon", "tel": "819-736-3017", "web": "lacsimon.ca"},
    },
    "cote_nord": {
        "villes": ["Baie-Comeau", "Sept-Iles", "Port-Cartier", "Havre-Saint-Pierre", "Forestville", "Tadoussac"],
        "codes_postaux": ["G5C", "G4R", "G5B", "G0G", "G0T", "G0T"],
        "zecs": [
            {"nom": "ZEC de la Riviere-Moisie", "tel": "418-927-2677", "courriel": "info@zecmoisie.com", "web": "zecmoisie.com"},
            {"nom": "ZEC Trinite", "tel": "418-939-2350", "courriel": "info@zectrinite.com", "web": "zectrinite.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie du Lac Cyprès", "tel": "418-296-3424", "courriel": "info@laccypres.com", "web": "laccypres.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique de Port-Cartier-Sept-Iles", "tel": "418-766-2524", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/pcs"},
        ],
        "altitude_range": [0, 400],
        "autochtone": {"nation": "Nation innue de Pessamit", "tel": "418-567-2265", "web": "pessamit.ca"},
    },
    "gaspesie": {
        "villes": ["Gaspe", "Perce", "Carleton-sur-Mer", "Sainte-Anne-des-Monts", "New Richmond", "Chandler"],
        "codes_postaux": ["G4X", "G0C", "G0C", "G4V", "G0C", "G0C"],
        "zecs": [
            {"nom": "ZEC des Anses", "tel": "418-689-6727", "courriel": "info@zecdesanses.com", "web": "zecdesanses.com"},
            {"nom": "ZEC de la Riviere-York", "tel": "418-368-2114", "courriel": "info@zecyork.com", "web": "zecyork.com"},
        ],
        "pourvoiries": [
            {"nom": "Pourvoirie de la Seigneurie du Lac Metis", "tel": "418-775-3677", "courriel": "info@lacmetis.com", "web": "lacmetis.com"},
        ],
        "reserves": [
            {"nom": "Reserve faunique de Matane", "tel": "418-562-3700", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/mat"},
            {"nom": "Reserve faunique des Chic-Chocs", "tel": "418-797-5214", "courriel": "info@sepaq.com", "web": "sepaq.com/rf/chc"},
        ],
        "altitude_range": [0, 1000],
        "autochtone": {"nation": "Nation mi'gmaq de Gespeg", "tel": "418-368-6005", "web": "gespeg.ca"},
    },
}

TERRITORY_TYPES = ["Prive", "Public", "Gouvernemental", "ZEC", "Pourvoirie", "Reserve faunique", "Territoire autochtone"]
ACCESS_STATUSES = ["Libre", "Restreint", "Payant", "Permission requise"]

MINISTERE_INFO = {
    "nom": "Ministere de l'Environnement, de la Lutte contre les changements climatiques, de la Faune et des Parcs (MELCCFP)",
    "tel": "1-800-561-1616",
    "web": "environnement.gouv.qc.ca",
    "reglements": "Acces libre pour activites de plein air. Permis de chasse obligatoire. Respect des periodes de chasse.",
}


def enrich_hotspot_territory(hotspot: dict) -> dict:
    """Enrich a hotspot with realistic territorial data based on GPS coordinates."""
    region_id = hotspot.get("region_id", "laurentides")
    lat = hotspot["center"][0]
    lng = hotspot["center"][1]
    seed = abs(hash(f"{lat:.4f}_{lng:.4f}_territory")) % 1000

    region_data = TERRITORIES_DB.get(region_id, TERRITORIES_DB["laurentides"])

    # Ville + Code postal
    ville_idx = seed % len(region_data["villes"])
    ville = region_data["villes"][ville_idx]
    code_postal_prefix = region_data["codes_postaux"][ville_idx % len(region_data["codes_postaux"])]
    code_postal_suffix = f"{(seed % 9) + 1}{chr(65 + (seed % 26))}{seed % 10}"
    code_postal = f"{code_postal_prefix} {code_postal_suffix}"

    # Altitude
    alt_min, alt_max = region_data["altitude_range"]
    altitude = alt_min + (seed % (alt_max - alt_min + 1))

    # Type de territoire (deterministic based on seed)
    type_hash = (seed * 17) % 100
    if type_hash < 10 and region_data.get("autochtone"):
        territory_type = "Territoire autochtone"
    elif type_hash < 25 and region_data.get("reserves"):
        territory_type = "Reserve faunique"
    elif type_hash < 45 and region_data.get("zecs"):
        territory_type = "ZEC"
    elif type_hash < 60 and region_data.get("pourvoiries"):
        territory_type = "Pourvoirie"
    elif type_hash < 75:
        territory_type = "Gouvernemental"
    elif type_hash < 88:
        territory_type = "Public"
    else:
        territory_type = "Prive"

    # Statut d'acces
    access_map = {
        "ZEC": "Payant",
        "Pourvoirie": "Payant",
        "Reserve faunique": "Payant",
        "Gouvernemental": "Libre",
        "Public": "Libre",
        "Prive": "Permission requise",
        "Territoire autochtone": "Restreint",
    }
    access_status = access_map.get(territory_type, "Libre")

    # Gestionnaire
    gestionnaire = _get_gestionnaire(territory_type, region_data, seed)

    # Lot number for private lands
    lot_info = None
    if territory_type == "Prive":
        lot_info = {
            "numero_lot": f"{seed % 9000 + 1000}-{seed % 90 + 10}",
            "cadastre": f"Cadastre du Quebec - {ville}",
            "registre_foncier": f"https://www.registrefoncier.gouv.qc.ca/lot/{seed % 9000 + 1000}",
            "proprietaire": "Proprietaire non disponible - contacter via formulaire",
        }

    return {
        "ville": ville,
        "code_postal": code_postal,
        "altitude_m": altitude,
        "territory_type": territory_type,
        "access_status": access_status,
        "gestionnaire": gestionnaire,
        "lot_info": lot_info,
        "gps": {"lat": lat, "lng": lng},
    }


def _get_gestionnaire(territory_type: str, region_data: dict, seed: int) -> dict:
    """Get gestionnaire info based on territory type."""
    if territory_type == "ZEC" and region_data.get("zecs"):
        zec = region_data["zecs"][seed % len(region_data["zecs"])]
        return {"type": "ZEC", **zec}

    if territory_type == "Pourvoirie" and region_data.get("pourvoiries"):
        p = region_data["pourvoiries"][seed % len(region_data["pourvoiries"])]
        return {"type": "Pourvoirie", **p}

    if territory_type == "Reserve faunique" and region_data.get("reserves"):
        r = region_data["reserves"][seed % len(region_data["reserves"])]
        return {"type": "Reserve faunique", **r}

    if territory_type == "Gouvernemental":
        return {"type": "Gouvernemental", **MINISTERE_INFO}

    if territory_type == "Territoire autochtone" and region_data.get("autochtone"):
        a = region_data["autochtone"]
        return {"type": "Territoire autochtone", "nom": a["nation"], "tel": a["tel"], "web": a["web"]}

    if territory_type == "Public":
        return {"type": "Public", "nom": "Terres publiques du Quebec", "tel": MINISTERE_INFO["tel"], "web": MINISTERE_INFO["web"]}

    return {"type": "Prive", "nom": "Proprietaire prive", "contact": "Formulaire de contact BIONIC"}
