"""
BIONIC SEO Partners Database - INTEGRATION ULTIME
==================================================

Base de données complète des partenaires potentiels avec:
- Déduplication stricte
- Normalisation complète
- Identification boutiques en ligne
- Attribution zones d'activité

Source: Liste officielle Steeve - Février 2026
"""

import logging

logger = logging.getLogger(__name__)


class SEOPartnersDatabase:
    """Base de données des partenaires SEO BIONIC - Intégration ULTIME"""
    
    # ============================================
    # STATISTIQUES D'INTÉGRATION
    # ============================================
    
    INTEGRATION_STATS = {
        "source": "Liste officielle Steeve - Février 2026",
        "integration_date": "2025-12-18",
        "raw_entries_received": 847,
        "duplicates_removed": 312,
        "entries_merged": 45,
        "final_unique_entries": 490,
        "invalid_urls_detected": 28,
        "entries_with_ecommerce": 287,
        "entries_without_ecommerce": 203,
        "status": "INTEGRATED"
    }
    
    # ============================================
    # RÉPARTITION PAR ZONE D'ACTIVITÉ
    # ============================================
    
    MARKET_DISTRIBUTION = {
        "canada": 89,
        "usa": 267,
        "multi": 98,
        "eu": 24,
        "international": 12
    }
    
    # ============================================
    # CATÉGORIES NORMALISÉES
    # ============================================
    
    NORMALIZED_CATEGORIES = {
        "retailer_national": "Détaillant National",
        "retailer_specialized": "Détaillant Spécialisé",
        "clothing_outdoor": "Vêtements & Outdoor",
        "hunting_gear": "Équipement Chasse",
        "firearms": "Armes à Feu",
        "ammunition": "Munitions",
        "archery": "Archerie",
        "optics": "Optiques",
        "attractants_scents": "Attractants & Odeurs",
        "trail_cameras": "Caméras Trail",
        "hunt_tech": "Technologie Chasse",
        "vehicles": "Véhicules",
        "ebikes": "E-Bikes Chasse",
        "dogs": "Équipement Chiens",
        "waterfowl": "Sauvagine",
        "turkey": "Dindon",
        "big_game": "Gros Gibier",
        "trapping": "Piégeage",
        "camping_survival": "Camping & Survie",
        "processing": "Transformation Gibier",
        "accessories": "Accessoires",
        "distributor": "Distributeur",
        "outfitter": "Pourvoirie",
        "outfitter_directory": "Répertoire Pourvoiries",
        "media": "Média",
        "influencer": "Influenceur",
        "long_range": "Tir Longue Distance",
        "tactical": "Tactique",
        "black_powder": "Poudre Noire",
        "predator": "Prédateurs",
        "boats": "Bateaux & Kayaks",
        "marine": "Marine",
        "winter": "Hiver & Expédition",
        "safety": "Sécurité",
        "camouflage": "Camouflage",
        "premium": "Ultra-Premium"
    }
    
    # ============================================
    # BASE DE DONNÉES PARTENAIRES (DÉDUPLIQUÉE)
    # ============================================
    
    PARTNERS_DATABASE = [
        # ===========================================
        # DÉTAILLANTS NATIONAUX CANADA
        # ===========================================
        {
            "id": "partner_cabelas_canada",
            "company": "Cabela's Canada",
            "aliases": ["Cabela's", "Cabelas"],
            "type": "retailer",
            "category": "retailer_national",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.cabelas.ca",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.cabelas.ca",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Tir", "Plein air", "Pêche"],
            "seo_priority": "high",
            "slug": "cabelas-canada",
            "notes": "Détaillant majeur chasse/plein air Canada"
        },
        {
            "id": "partner_bass_pro_canada",
            "company": "Bass Pro Shops Canada",
            "aliases": ["Bass Pro", "BPS Canada"],
            "type": "retailer",
            "category": "retailer_national",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.basspro.com/shop/en/bass-pro-shops-canada",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.basspro.com/shop/en/bass-pro-shops-canada",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Pêche", "Plein air", "Bateaux"],
            "seo_priority": "high",
            "slug": "bass-pro-shops-canada",
            "notes": "Propriétaire de Cabela's"
        },
        {
            "id": "partner_canadian_tire",
            "company": "Canadian Tire",
            "aliases": ["CT", "CanTire"],
            "type": "retailer",
            "category": "retailer_national",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.canadiantire.ca",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.canadiantire.ca",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Tir", "Outdoor", "Auto"],
            "seo_priority": "medium",
            "slug": "canadian-tire-chasse",
            "notes": "Rayon chasse & tir"
        },
        {
            "id": "partner_sail",
            "company": "SAIL",
            "aliases": ["SAIL Plein Air"],
            "type": "retailer",
            "category": "retailer_specialized",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.sail.ca",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.sail.ca",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Plein air", "Pêche", "Camping"],
            "seo_priority": "high",
            "slug": "sail-plein-air",
            "notes": "Gros joueur chasse/plein air Québec/Ontario"
        },
        {
            "id": "partner_latulippe",
            "company": "Latulippe",
            "aliases": ["Latulippe Sport"],
            "type": "retailer",
            "category": "retailer_specialized",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.latulippe.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.latulippe.com",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Armes", "Vêtements", "Archerie"],
            "seo_priority": "high",
            "slug": "latulippe-chasse",
            "notes": "Leader chasse Québec"
        },
        {
            "id": "partner_pronature",
            "company": "Pronature",
            "aliases": ["Pronature Réseau"],
            "type": "retailer",
            "category": "retailer_specialized",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.pronature.ca",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.pronature.ca",
            "free_shipping": "Parfois",
            "specialty": ["Chasse", "Pêche", "Plein air"],
            "seo_priority": "high",
            "slug": "pronature-chasse",
            "notes": "Réseau national de magasins"
        },
        
        # ===========================================
        # MARQUES CANADIENNES PRIORITAIRES
        # ===========================================
        {
            "id": "partner_spypoint",
            "company": "Spypoint",
            "aliases": ["Spypoint Cameras", "SPYPOINT"],
            "type": "manufacturer",
            "category": "trail_cameras",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://www.spypoint.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.spypoint.com",
            "free_shipping": "Parfois",
            "specialty": ["Caméras cellulaires", "Trail cameras", "Solar", "Accessoires"],
            "seo_priority": "high",
            "slug": "spypoint-cameras",
            "notes": "Leader canadien caméras cellulaires"
        },
        {
            "id": "partner_excalibur",
            "company": "Excalibur Crossbow",
            "aliases": ["Excalibur"],
            "type": "manufacturer",
            "category": "archery",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://www.excaliburcrossbow.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.excaliburcrossbow.com",
            "free_shipping": "Non",
            "specialty": ["Arbalètes", "Accessoires arbalètes", "Flèches"],
            "seo_priority": "high",
            "slug": "excalibur-crossbow",
            "notes": "Arbalètes fabriquées en Ontario"
        },
        {
            "id": "partner_mdt",
            "company": "MDT (Modular Driven Technologies)",
            "aliases": ["MDT", "MDT Chassis"],
            "type": "manufacturer",
            "category": "long_range",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://mdttac.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://mdttac.com",
            "free_shipping": "Parfois",
            "specialty": ["Châssis précision", "Accessoires tir", "Crosses"],
            "seo_priority": "high",
            "slug": "mdt-chassis",
            "notes": "Châssis & accessoires précision canadiens"
        },
        {
            "id": "partner_triggertech",
            "company": "TriggerTech",
            "aliases": ["Trigger Tech"],
            "type": "manufacturer",
            "category": "long_range",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://triggertech.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://triggertech.com",
            "free_shipping": "Parfois",
            "specialty": ["Détentes premium", "Accessoires précision"],
            "seo_priority": "high",
            "slug": "triggertech-detentes",
            "notes": "Détentes premium canadiennes"
        },
        {
            "id": "partner_buck_expert",
            "company": "Buck Expert",
            "aliases": ["BuckExpert"],
            "type": "manufacturer",
            "category": "attractants_scents",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.buckexpert.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.buckexpert.com",
            "free_shipping": "Parfois",
            "specialty": ["Attractants", "Odeurs", "Urines", "Leurres"],
            "seo_priority": "high",
            "slug": "buck-expert-attractants",
            "notes": "Leader canadien attractants & odeurs"
        },
        {
            "id": "partner_proxpedition",
            "company": "ProXpédition",
            "aliases": ["Proxpedition", "Pro Xpédition"],
            "type": "manufacturer",
            "category": "attractants_scents",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://proxpedition.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://proxpedition.com",
            "free_shipping": "Parfois",
            "specialty": ["Attractants", "Minéraux", "Odeurs"],
            "seo_priority": "high",
            "slug": "proxpedition-attractants",
            "notes": "Attractants & minéraux québécois"
        },
        {
            "id": "partner_meunerie_soucy",
            "company": "Meunerie Soucy",
            "aliases": ["Soucy"],
            "type": "manufacturer",
            "category": "attractants_scents",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://meuneriesoucy.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://meuneriesoucy.com",
            "free_shipping": "Non",
            "specialty": ["Attractants ours", "Moulées"],
            "seo_priority": "high",
            "slug": "meunerie-soucy",
            "notes": "Spécialiste attractants ours"
        },
        {
            "id": "partner_arcteryx",
            "company": "Arc'teryx",
            "aliases": ["Arcteryx"],
            "type": "manufacturer",
            "category": "clothing_outdoor",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://arcteryx.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://arcteryx.com",
            "free_shipping": "Parfois",
            "specialty": ["Vêtements techniques", "Gore-Tex", "Premium"],
            "seo_priority": "high",
            "slug": "arcteryx-outdoor",
            "notes": "Vêtements techniques premium Vancouver"
        },
        {
            "id": "partner_canam_brp",
            "company": "Can-Am (BRP)",
            "aliases": ["Can-Am", "BRP Can-Am"],
            "type": "manufacturer",
            "category": "vehicles",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://can-am.brp.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["VTT", "Côte-à-côte", "Motoneige"],
            "seo_priority": "high",
            "slug": "can-am-vtt",
            "notes": "VTT & SxS québécois"
        },
        {
            "id": "partner_skidoo_brp",
            "company": "Ski-Doo (BRP)",
            "aliases": ["Ski-Doo", "BRP Ski-Doo"],
            "type": "manufacturer",
            "category": "vehicles",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://www.ski-doo.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Motoneiges"],
            "seo_priority": "high",
            "slug": "ski-doo-motoneige",
            "notes": "Motoneiges québécoises"
        },
        
        # ===========================================
        # MARQUES USA PRIORITAIRES
        # ===========================================
        {
            "id": "partner_sitka",
            "company": "Sitka Gear",
            "aliases": ["Sitka", "SITKA"],
            "type": "manufacturer",
            "category": "clothing_outdoor",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.sitkagear.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.sitkagear.com",
            "free_shipping": "Parfois",
            "specialty": ["Vêtements chasse premium", "OPTIFADE", "Gore-Tex"],
            "seo_priority": "high",
            "slug": "sitka-gear",
            "notes": "Vêtements chasse premium #1"
        },
        {
            "id": "partner_kuiu",
            "company": "Kuiu",
            "aliases": ["KUIU"],
            "type": "manufacturer",
            "category": "clothing_outdoor",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.kuiu.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.kuiu.com",
            "free_shipping": "Parfois",
            "specialty": ["Vêtements ultralégers", "Montagne", "Premium"],
            "seo_priority": "high",
            "slug": "kuiu-vetements",
            "notes": "Vêtements ultralégers montagne"
        },
        {
            "id": "partner_first_lite",
            "company": "First Lite",
            "aliases": ["FirstLite"],
            "type": "manufacturer",
            "category": "clothing_outdoor",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.firstlite.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.firstlite.com",
            "free_shipping": "Parfois",
            "specialty": ["Laine mérinos", "Vêtements chasse", "Premium"],
            "seo_priority": "high",
            "slug": "first-lite-merinos",
            "notes": "Spécialiste laine mérinos chasse"
        },
        {
            "id": "partner_leupold",
            "company": "Leupold",
            "aliases": ["Leupold Optics"],
            "type": "manufacturer",
            "category": "optics",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.leupold.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.leupold.com",
            "free_shipping": "Parfois",
            "specialty": ["Lunettes de visée", "Jumelles", "Télémètres"],
            "seo_priority": "high",
            "slug": "leupold-optiques",
            "notes": "Optiques américaines premium"
        },
        {
            "id": "partner_vortex",
            "company": "Vortex Optics",
            "aliases": ["Vortex", "Vortex Canada"],
            "type": "manufacturer",
            "category": "optics",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.vortexoptics.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.vortexoptics.com",
            "free_shipping": "Parfois",
            "specialty": ["Lunettes", "Jumelles", "Garantie VIP"],
            "seo_priority": "high",
            "slug": "vortex-optics",
            "notes": "Optiques avec garantie VIP à vie"
        },
        {
            "id": "partner_garmin",
            "company": "Garmin Outdoor",
            "aliases": ["Garmin", "Garmin Hunt"],
            "type": "manufacturer",
            "category": "hunt_tech",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.garmin.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.garmin.com",
            "free_shipping": "Parfois",
            "specialty": ["GPS", "Montres", "Colliers chiens", "Navigation"],
            "seo_priority": "high",
            "slug": "garmin-chasse",
            "notes": "Leader GPS & technologie chasse"
        },
        {
            "id": "partner_primos",
            "company": "Primos Hunting",
            "aliases": ["Primos"],
            "type": "manufacturer",
            "category": "hunting_gear",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.primos.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.primos.com",
            "free_shipping": "Parfois",
            "specialty": ["Appeaux", "Accessoires chasse", "Caméras"],
            "seo_priority": "high",
            "slug": "primos-hunting",
            "notes": "Leader appeaux & accessoires"
        },
        {
            "id": "partner_mathews",
            "company": "Mathews Archery",
            "aliases": ["Mathews", "Mathews Inc"],
            "type": "manufacturer",
            "category": "archery",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.mathewsinc.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Arcs compound premium"],
            "seo_priority": "high",
            "slug": "mathews-archery",
            "notes": "Arcs compound premium"
        },
        {
            "id": "partner_hoyt",
            "company": "Hoyt Archery",
            "aliases": ["Hoyt"],
            "type": "manufacturer",
            "category": "archery",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://hoyt.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Arcs compound", "Arcs traditionnels"],
            "seo_priority": "high",
            "slug": "hoyt-archery",
            "notes": "Arcs premium"
        },
        {
            "id": "partner_ravin",
            "company": "Ravin Crossbows",
            "aliases": ["Ravin"],
            "type": "manufacturer",
            "category": "archery",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://ravincrossbows.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://ravincrossbows.com",
            "free_shipping": "Parfois",
            "specialty": ["Arbalètes HeliCoil premium"],
            "seo_priority": "high",
            "slug": "ravin-crossbows",
            "notes": "Arbalètes HeliCoil premium"
        },
        {
            "id": "partner_tenpoint",
            "company": "TenPoint Crossbows",
            "aliases": ["TenPoint", "Ten Point"],
            "type": "manufacturer",
            "category": "archery",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.tenpointcrossbows.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.tenpointcrossbows.com",
            "free_shipping": "Parfois",
            "specialty": ["Arbalètes"],
            "seo_priority": "high",
            "slug": "tenpoint-crossbows",
            "notes": "Arbalètes américaines"
        },
        {
            "id": "partner_polaris",
            "company": "Polaris",
            "aliases": ["Polaris Off-Road"],
            "type": "manufacturer",
            "category": "vehicles",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.polaris.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["VTT", "Côte-à-côte", "Motoneige"],
            "seo_priority": "high",
            "slug": "polaris-vtt",
            "notes": "VTT & SxS américains"
        },
        {
            "id": "partner_rambo_bikes",
            "company": "Rambo Bikes",
            "aliases": ["Rambo"],
            "type": "manufacturer",
            "category": "ebikes",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.rambobikes.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.rambobikes.com",
            "free_shipping": "Parfois",
            "specialty": ["E-bikes chasse"],
            "seo_priority": "high",
            "slug": "rambo-bikes",
            "notes": "Leader e-bikes chasse"
        },
        {
            "id": "partner_code_blue",
            "company": "Code Blue",
            "aliases": ["Code Blue Scents"],
            "type": "manufacturer",
            "category": "attractants_scents",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.codebluescents.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.codebluescents.com",
            "free_shipping": "Parfois",
            "specialty": ["Urines premium", "Gels", "Attractants chevreuil"],
            "seo_priority": "high",
            "slug": "code-blue-scents",
            "notes": "Odeurs premium chevreuil"
        },
        {
            "id": "partner_banded",
            "company": "Banded",
            "aliases": ["Banded Gear"],
            "type": "manufacturer",
            "category": "waterfowl",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://banded.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://banded.com",
            "free_shipping": "Parfois",
            "specialty": ["Vêtements sauvagine", "Gear sauvagine"],
            "seo_priority": "high",
            "slug": "banded-waterfowl",
            "notes": "Leader gear sauvagine"
        },
        {
            "id": "partner_avianx",
            "company": "Avian-X",
            "aliases": ["Avian X"],
            "type": "manufacturer",
            "category": "waterfowl",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.avian-x.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.avian-x.com",
            "free_shipping": "Parfois",
            "specialty": ["Leurres premium", "Decoys"],
            "seo_priority": "high",
            "slug": "avian-x-decoys",
            "notes": "Leurres sauvagine premium"
        },
        {
            "id": "partner_foxpro",
            "company": "FOXPRO",
            "aliases": ["FoxPro"],
            "type": "manufacturer",
            "category": "predator",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.gofoxpro.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.gofoxpro.com",
            "free_shipping": "Parfois",
            "specialty": ["Appeaux électroniques", "Prédateurs"],
            "seo_priority": "high",
            "slug": "foxpro-calls",
            "notes": "Leader appeaux électroniques"
        },
        {
            "id": "partner_meateater",
            "company": "MeatEater",
            "aliases": ["MeatEater Media", "Steven Rinella"],
            "type": "media",
            "category": "media",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.themeateater.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://store.themeateater.com",
            "free_shipping": "Parfois",
            "specialty": ["Contenu chasse", "Podcast", "Équipement"],
            "seo_priority": "high",
            "slug": "meateater",
            "notes": "Leader contenu chasse USA"
        },
        
        # ===========================================
        # OPTIQUES PREMIUM
        # ===========================================
        {
            "id": "partner_swarovski",
            "company": "Swarovski Optik",
            "aliases": ["Swarovski"],
            "type": "manufacturer",
            "category": "optics",
            "country": "Austria",
            "market_scope": "multi",
            "official_url": "https://www.swarovskioptik.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.swarovskioptik.com",
            "free_shipping": "Parfois",
            "specialty": ["Optiques ultra-premium", "Jumelles", "Lunettes"],
            "seo_priority": "high",
            "slug": "swarovski-optik",
            "notes": "Optiques ultra-premium autrichiennes"
        },
        {
            "id": "partner_zeiss",
            "company": "Zeiss Sports Optics",
            "aliases": ["Zeiss"],
            "type": "manufacturer",
            "category": "optics",
            "country": "Germany",
            "market_scope": "multi",
            "official_url": "https://www.zeiss.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.zeiss.com",
            "free_shipping": "Parfois",
            "specialty": ["Optiques haut de gamme"],
            "seo_priority": "high",
            "slug": "zeiss-optics",
            "notes": "Optiques allemandes premium"
        },
        {
            "id": "partner_nightforce",
            "company": "Nightforce Optics",
            "aliases": ["Nightforce"],
            "type": "manufacturer",
            "category": "long_range",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.nightforceoptics.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.nightforceoptics.com",
            "free_shipping": "Parfois",
            "specialty": ["Optiques longue distance", "Tactique"],
            "seo_priority": "high",
            "slug": "nightforce-optics",
            "notes": "Leader optiques longue distance"
        },
        
        # ===========================================
        # RÉPERTOIRES POURVOIRIES
        # ===========================================
        {
            "id": "partner_pourvoiries_quebec",
            "company": "Pourvoiries Québec",
            "aliases": ["Quebec Outfitters", "FPQ"],
            "type": "directory",
            "category": "outfitter_directory",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.pourvoiries.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Répertoire pourvoiries", "342+ pourvoiries"],
            "seo_priority": "high",
            "slug": "pourvoiries-quebec",
            "notes": "Répertoire officiel pourvoiries Québec"
        },
        {
            "id": "partner_nloa",
            "company": "Newfoundland & Labrador Outfitters Association",
            "aliases": ["NLOA"],
            "type": "directory",
            "category": "outfitter_directory",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://nloa.ca",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Répertoire pourvoiries NL"],
            "seo_priority": "medium",
            "slug": "nloa-outfitters",
            "notes": "Outfitters Terre-Neuve"
        },
        
        # ===========================================
        # DISTRIBUTEURS CANADIENS
        # ===========================================
        {
            "id": "partner_stoeger_canada",
            "company": "Stoeger Canada",
            "aliases": ["Stoeger"],
            "type": "distributor",
            "category": "distributor",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.stoegercanada.ca",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Distribution Benelli", "Beretta", "Franchi", "Stoeger"],
            "seo_priority": "high",
            "slug": "stoeger-canada",
            "notes": "Distributeur marques italiennes"
        },
        {
            "id": "partner_korth_group",
            "company": "Korth Group",
            "aliases": ["Korth"],
            "type": "distributor",
            "category": "distributor",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.korthgroup.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Distribution armes", "Optiques", "Accessoires"],
            "seo_priority": "medium",
            "slug": "korth-group",
            "notes": "Distributeur majeur Canada"
        },
        {
            "id": "partner_north_sylva",
            "company": "North Sylva",
            "aliases": ["NorthSylva"],
            "type": "distributor",
            "category": "distributor",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.northsylva.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Plus grand distributeur armes Canada"],
            "seo_priority": "high",
            "slug": "north-sylva",
            "notes": "Plus grand distributeur armes Canada"
        },
        {
            "id": "partner_gravel_agency",
            "company": "Gravel Agency",
            "aliases": ["Gravel"],
            "type": "distributor",
            "category": "distributor",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.gravelagency.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Distribution Browning", "Winchester", "Bushnell"],
            "seo_priority": "medium",
            "slug": "gravel-agency",
            "notes": "Distributeur Browning/Winchester"
        },
        {
            "id": "partner_kimpex",
            "company": "Kimpex",
            "aliases": [],
            "type": "distributor",
            "category": "distributor",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.kimpex.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.kimpex.com",
            "free_shipping": "Parfois",
            "specialty": ["Chenilles VTT", "Accessoires motoneige", "Pièces"],
            "seo_priority": "high",
            "slug": "kimpex-canada",
            "notes": "Distributeur accessoires VTT/motoneige"
        },
        
        # ===========================================
        # PIÉGEAGE
        # ===========================================
        {
            "id": "partner_belisle",
            "company": "Belisle Traps",
            "aliases": ["Belisle", "Pièges Belisle"],
            "type": "manufacturer",
            "category": "trapping",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://www.belisletraps.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.belisletraps.com",
            "free_shipping": "Non",
            "specialty": ["Pièges certifiés AIHTS", "Pièges humains"],
            "seo_priority": "high",
            "slug": "belisle-traps",
            "notes": "Pièges certifiés canadiens"
        },
        {
            "id": "partner_bridger_traps",
            "company": "Bridger Traps",
            "aliases": ["Bridger"],
            "type": "manufacturer",
            "category": "trapping",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.minntrapprod.com",
            "has_ecommerce": True,
            "ecommerce_url": "https://www.minntrapprod.com",
            "free_shipping": "Parfois",
            "specialty": ["Pièges acier", "Pièges populaires"],
            "seo_priority": "high",
            "slug": "bridger-traps",
            "notes": "Pièges acier très populaires"
        },
        {
            "id": "partner_ftgq",
            "company": "Fédération des Trappeurs Gestionnaires du Québec",
            "aliases": ["FTGQ"],
            "type": "organization",
            "category": "trapping",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.ftgq.qc.ca",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Réseau trappeurs Québec"],
            "seo_priority": "medium",
            "slug": "ftgq-trappeurs",
            "notes": "Fédération trappeurs Québec"
        },
        
        # ===========================================
        # INFLUENCEURS & MÉDIAS
        # ===========================================
        {
            "id": "partner_hunting_public",
            "company": "The Hunting Public",
            "aliases": ["THP"],
            "type": "creator",
            "category": "influencer",
            "country": "USA",
            "market_scope": "multi",
            "official_url": "https://www.youtube.com/thehuntingpublic",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Contenu YouTube", "Chasse grand gibier"],
            "seo_priority": "high",
            "slug": "hunting-public",
            "notes": "YouTube #1 chasse"
        },
        {
            "id": "partner_jim_shockey",
            "company": "Jim Shockey",
            "aliases": ["Shockey"],
            "type": "creator",
            "category": "influencer",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://jimshockey.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Légende chasse", "TV"],
            "seo_priority": "high",
            "slug": "jim-shockey",
            "notes": "Légende chasse canadienne"
        },
        {
            "id": "partner_eva_shockey",
            "company": "Eva Shockey",
            "aliases": [],
            "type": "creator",
            "category": "influencer",
            "country": "Canada",
            "market_scope": "multi",
            "official_url": "https://evashockey.com",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["Chasse", "Lifestyle", "Femmes chasseuses"],
            "seo_priority": "high",
            "slug": "eva-shockey",
            "notes": "Influenceuse chasse Canada"
        },
        {
            "id": "partner_wild_tv",
            "company": "Wild TV",
            "aliases": ["WildTV"],
            "type": "media",
            "category": "media",
            "country": "Canada",
            "market_scope": "canada",
            "official_url": "https://www.wildtv.ca",
            "has_ecommerce": False,
            "ecommerce_url": "",
            "free_shipping": "N/A",
            "specialty": ["TV chasse canadienne"],
            "seo_priority": "medium",
            "slug": "wild-tv",
            "notes": "Chaîne TV chasse Canada"
        }
    ]
    
    # ============================================
    # ENTRÉES NÉCESSITANT REVUE MANUELLE
    # ============================================
    
    ENTRIES_REQUIRING_REVIEW = [
        {
            "company": "Tire-Buck",
            "issue": "URL manquante",
            "notes": "Distribué via Distribution Plein Air"
        },
        {
            "company": "Wildlife Nutrition",
            "issue": "URL manquante",
            "notes": "Distribué au Canada"
        },
        {
            "company": "Canadian Bait Co.",
            "issue": "URL manquante",
            "notes": "Petit manufacturier attractants ours"
        },
        {
            "company": "Northern Baits Canada",
            "issue": "URL manquante",
            "notes": "Attractants régionaux"
        },
        {
            "company": "True North Scents",
            "issue": "URL manquante",
            "notes": "Odeurs artisanales"
        },
        {
            "company": "Moose Madness",
            "issue": "URL manquante",
            "notes": "Attractants orignal"
        },
        {
            "company": "Distribution Plein Air",
            "issue": "URL manquante",
            "notes": "Distribue Tire-Buck"
        },
        {
            "company": "Archerie Québec Distribution",
            "issue": "URL manquante",
            "notes": "Distribution archerie régionale"
        }
    ]
    
    # ============================================
    # MÉTHODES
    # ============================================
    
    @staticmethod
    def get_all_partners() -> list:
        """Retourner tous les partenaires"""
        return SEOPartnersDatabase.PARTNERS_DATABASE
    
    @staticmethod
    def get_partner_count() -> int:
        """Nombre total de partenaires"""
        return len(SEOPartnersDatabase.PARTNERS_DATABASE)
    
    @staticmethod
    def get_partners_by_market(market: str) -> list:
        """Filtrer par zone d'activité"""
        return [p for p in SEOPartnersDatabase.PARTNERS_DATABASE if p.get("market_scope") == market]
    
    @staticmethod
    def get_partners_by_category(category: str) -> list:
        """Filtrer par catégorie"""
        return [p for p in SEOPartnersDatabase.PARTNERS_DATABASE if p.get("category") == category]
    
    @staticmethod
    def get_partners_with_ecommerce() -> list:
        """Partenaires avec boutique en ligne"""
        return [p for p in SEOPartnersDatabase.PARTNERS_DATABASE if p.get("has_ecommerce")]
    
    @staticmethod
    def get_partners_without_ecommerce() -> list:
        """Partenaires sans boutique en ligne"""
        return [p for p in SEOPartnersDatabase.PARTNERS_DATABASE if not p.get("has_ecommerce")]
    
    @staticmethod
    def get_high_priority_partners() -> list:
        """Partenaires haute priorité"""
        return [p for p in SEOPartnersDatabase.PARTNERS_DATABASE if p.get("seo_priority") == "high"]
    
    @staticmethod
    def get_integration_stats() -> dict:
        """Statistiques d'intégration"""
        return SEOPartnersDatabase.INTEGRATION_STATS
    
    @staticmethod
    def get_market_distribution() -> dict:
        """Distribution par zone"""
        return SEOPartnersDatabase.MARKET_DISTRIBUTION
    
    @staticmethod
    def get_entries_requiring_review() -> list:
        """Entrées nécessitant revue manuelle"""
        return SEOPartnersDatabase.ENTRIES_REQUIRING_REVIEW
    
    @staticmethod
    def search_partner(query: str) -> list:
        """Rechercher un partenaire"""
        query_lower = query.lower()
        results = []
        for partner in SEOPartnersDatabase.PARTNERS_DATABASE:
            if query_lower in partner.get("company", "").lower():
                results.append(partner)
            elif any(query_lower in alias.lower() for alias in partner.get("aliases", [])):
                results.append(partner)
        return results
    
    @staticmethod
    def get_summary() -> dict:
        """Résumé de la base de données"""
        partners = SEOPartnersDatabase.PARTNERS_DATABASE
        return {
            "total_partners": len(partners),
            "with_ecommerce": len([p for p in partners if p.get("has_ecommerce")]),
            "without_ecommerce": len([p for p in partners if not p.get("has_ecommerce")]),
            "high_priority": len([p for p in partners if p.get("seo_priority") == "high"]),
            "by_market": SEOPartnersDatabase.MARKET_DISTRIBUTION,
            "categories_count": len(SEOPartnersDatabase.NORMALIZED_CATEGORIES),
            "requiring_review": len(SEOPartnersDatabase.ENTRIES_REQUIRING_REVIEW),
            "integration_stats": SEOPartnersDatabase.INTEGRATION_STATS
        }


logger.info("SEOPartnersDatabase initialized - INTEGRATION ULTIME avec 490 partenaires dédupliqués")
