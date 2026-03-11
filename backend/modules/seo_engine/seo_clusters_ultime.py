"""
BIONIC SEO Clusters ULTIMES - V5-ULTIME
========================================

Structure complète des clusters SEO pour atteindre +300% trafic organique.

Structure Planifiée:
- 1147 pages totales
- 50 clusters ULTIMES
- 8 types de pages

Module isolé - Architecture LEGO V5.
"""

import logging

logger = logging.getLogger(__name__)


class SEOClustersUltime:
    """Structure des clusters SEO ULTIMES"""
    
    # ============================================
    # OBJECTIFS STRATÉGIQUES
    # ============================================
    
    STRATEGY_TARGETS = {
        "total_pages": 1147,
        "traffic_increase_target": "+300%",
        "timeline": "12 months",
        "page_distribution": {
            "pillar": 50,
            "satellite": 400,
            "opportunity": 300,
            "gear": 150,
            "territory": 100,
            "regulation": 50,
            "intelligence": 47,
            "review": 50
        }
    }
    
    # ============================================
    # CLUSTERS ULTIMES (50)
    # ============================================
    
    CLUSTERS_ULTIME = {
        # ===================
        # ESPÈCES (10 clusters)
        # ===================
        "cluster_moose_ultime": {
            "id": "cluster_moose_ultime",
            "name": "Moose Hunting Ultimate",
            "name_fr": "Chasse à l'Orignal ULTIME",
            "cluster_type": "species",
            "species_ids": ["moose"],
            "target_pages": {
                "pillar": 1,
                "satellites": 10,
                "opportunities": 15,
                "gear": 5
            },
            "primary_keyword_fr": "chasse orignal québec",
            "secondary_keywords_fr": [
                "techniques appel orignal",
                "meilleure période chasse orignal",
                "équipement chasse orignal",
                "zones chasse orignal québec",
                "permis chasse orignal"
            ],
            "search_volume_estimate": 12000,
            "priority": 1,
            "is_active": True
        },
        "cluster_deer_ultime": {
            "id": "cluster_deer_ultime",
            "name": "Whitetail Deer Hunting Ultimate",
            "name_fr": "Chasse au Cerf de Virginie ULTIME",
            "cluster_type": "species",
            "species_ids": ["deer"],
            "target_pages": {
                "pillar": 1,
                "satellites": 10,
                "opportunities": 15,
                "gear": 5
            },
            "primary_keyword_fr": "chasse chevreuil québec",
            "secondary_keywords_fr": [
                "rut chevreuil québec",
                "techniques chasse chevreuil",
                "zones chasse chevreuil",
                "équipement chasse cerf"
            ],
            "search_volume_estimate": 15000,
            "priority": 1,
            "is_active": True
        },
        "cluster_bear_ultime": {
            "id": "cluster_bear_ultime",
            "name": "Black Bear Hunting Ultimate",
            "name_fr": "Chasse à l'Ours Noir ULTIME",
            "cluster_type": "species",
            "species_ids": ["bear"],
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "gear": 4
            },
            "primary_keyword_fr": "chasse ours noir québec",
            "secondary_keywords_fr": [
                "appâtage ours noir",
                "chasse ours printemps",
                "chasse ours automne",
                "zones chasse ours québec"
            ],
            "search_volume_estimate": 8000,
            "priority": 2,
            "is_active": True
        },
        "cluster_turkey_ultime": {
            "id": "cluster_turkey_ultime",
            "name": "Wild Turkey Hunting Ultimate",
            "name_fr": "Chasse au Dindon Sauvage ULTIME",
            "cluster_type": "species",
            "species_ids": ["wild_turkey"],
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "gear": 3
            },
            "primary_keyword_fr": "chasse dindon sauvage québec",
            "search_volume_estimate": 5000,
            "priority": 2,
            "is_active": True
        },
        "cluster_waterfowl_ultime": {
            "id": "cluster_waterfowl_ultime",
            "name": "Waterfowl Hunting Ultimate",
            "name_fr": "Chasse à la Sauvagine ULTIME",
            "cluster_type": "species",
            "species_ids": ["duck", "goose"],
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 12,
                "gear": 5
            },
            "primary_keyword_fr": "chasse canard oie québec",
            "search_volume_estimate": 7000,
            "priority": 2,
            "is_active": True
        },
        "cluster_small_game_ultime": {
            "id": "cluster_small_game_ultime",
            "name": "Small Game Hunting Ultimate",
            "name_fr": "Chasse au Petit Gibier ULTIME",
            "cluster_type": "species",
            "species_ids": ["hare", "grouse", "partridge"],
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8
            },
            "primary_keyword_fr": "chasse petit gibier québec",
            "search_volume_estimate": 4000,
            "priority": 3,
            "is_active": True
        },
        "cluster_caribou_ultime": {
            "id": "cluster_caribou_ultime",
            "name": "Caribou Hunting Ultimate",
            "name_fr": "Chasse au Caribou ULTIME",
            "cluster_type": "species",
            "species_ids": ["caribou"],
            "target_pages": {
                "pillar": 1,
                "satellites": 5,
                "opportunities": 6
            },
            "primary_keyword_fr": "chasse caribou québec",
            "search_volume_estimate": 3000,
            "priority": 3,
            "is_active": True
        },
        
        # ===================
        # RÉGIONS (15 clusters)
        # ===================
        "cluster_laurentides_ultime": {
            "id": "cluster_laurentides_ultime",
            "name": "Laurentides Hunting Ultimate",
            "name_fr": "Chasse dans les Laurentides ULTIME",
            "cluster_type": "region",
            "region_ids": ["laurentides"],
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "territory": 5
            },
            "primary_keyword_fr": "chasse laurentides",
            "search_volume_estimate": 6000,
            "priority": 1,
            "is_active": True
        },
        "cluster_abitibi_ultime": {
            "id": "cluster_abitibi_ultime",
            "name": "Abitibi Hunting Ultimate",
            "name_fr": "Chasse en Abitibi ULTIME",
            "cluster_type": "region",
            "region_ids": ["abitibi"],
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "territory": 6
            },
            "primary_keyword_fr": "chasse abitibi",
            "search_volume_estimate": 5000,
            "priority": 1,
            "is_active": True
        },
        "cluster_outaouais_ultime": {
            "id": "cluster_outaouais_ultime",
            "name": "Outaouais Hunting Ultimate",
            "name_fr": "Chasse en Outaouais ULTIME",
            "cluster_type": "region",
            "region_ids": ["outaouais"],
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "territory": 4
            },
            "primary_keyword_fr": "chasse outaouais",
            "search_volume_estimate": 4000,
            "priority": 2,
            "is_active": True
        },
        "cluster_mauricie_ultime": {
            "id": "cluster_mauricie_ultime",
            "name": "Mauricie Hunting Ultimate",
            "name_fr": "Chasse en Mauricie ULTIME",
            "cluster_type": "region",
            "region_ids": ["mauricie"],
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "territory": 4
            },
            "primary_keyword_fr": "chasse mauricie",
            "search_volume_estimate": 4500,
            "priority": 2,
            "is_active": True
        },
        "cluster_saguenay_ultime": {
            "id": "cluster_saguenay_ultime",
            "name": "Saguenay Hunting Ultimate",
            "name_fr": "Chasse au Saguenay ULTIME",
            "cluster_type": "region",
            "region_ids": ["saguenay"],
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "territory": 5
            },
            "primary_keyword_fr": "chasse saguenay lac-saint-jean",
            "search_volume_estimate": 4000,
            "priority": 2,
            "is_active": True
        },
        "cluster_cote_nord_ultime": {
            "id": "cluster_cote_nord_ultime",
            "name": "Côte-Nord Hunting Ultimate",
            "name_fr": "Chasse sur la Côte-Nord ULTIME",
            "cluster_type": "region",
            "region_ids": ["cote_nord"],
            "target_pages": {
                "pillar": 1,
                "satellites": 5,
                "opportunities": 6,
                "territory": 4
            },
            "primary_keyword_fr": "chasse côte-nord",
            "search_volume_estimate": 3000,
            "priority": 3,
            "is_active": True
        },
        "cluster_gaspesie_ultime": {
            "id": "cluster_gaspesie_ultime",
            "name": "Gaspésie Hunting Ultimate",
            "name_fr": "Chasse en Gaspésie ULTIME",
            "cluster_type": "region",
            "region_ids": ["gaspesie"],
            "target_pages": {
                "pillar": 1,
                "satellites": 5,
                "opportunities": 6,
                "territory": 3
            },
            "primary_keyword_fr": "chasse gaspésie",
            "search_volume_estimate": 3500,
            "priority": 2,
            "is_active": True
        },
        "cluster_lanaudiere_ultime": {
            "id": "cluster_lanaudiere_ultime",
            "name": "Lanaudière Hunting Ultimate",
            "name_fr": "Chasse en Lanaudière ULTIME",
            "cluster_type": "region",
            "region_ids": ["lanaudiere"],
            "target_pages": {
                "pillar": 1,
                "satellites": 5,
                "opportunities": 6,
                "territory": 3
            },
            "primary_keyword_fr": "chasse lanaudière",
            "search_volume_estimate": 3000,
            "priority": 3,
            "is_active": True
        },
        
        # ===================
        # TECHNIQUES (8 clusters)
        # ===================
        "cluster_calling_ultime": {
            "id": "cluster_calling_ultime",
            "name": "Calling Techniques Ultimate",
            "name_fr": "Techniques d'Appel ULTIME",
            "cluster_type": "technique",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 12,
                "gear": 4
            },
            "primary_keyword_fr": "techniques appel chasse",
            "secondary_keywords_fr": [
                "call orignal",
                "call chevreuil",
                "appel dindon",
                "meilleurs calls chasse"
            ],
            "search_volume_estimate": 8000,
            "priority": 1,
            "is_active": True
        },
        "cluster_stalking_ultime": {
            "id": "cluster_stalking_ultime",
            "name": "Stalking Techniques Ultimate",
            "name_fr": "Techniques de Pistage ULTIME",
            "cluster_type": "technique",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8
            },
            "primary_keyword_fr": "techniques pistage chasse",
            "search_volume_estimate": 4000,
            "priority": 2,
            "is_active": True
        },
        "cluster_stand_hunting_ultime": {
            "id": "cluster_stand_hunting_ultime",
            "name": "Stand Hunting Ultimate",
            "name_fr": "Chasse à l'Affût ULTIME",
            "cluster_type": "technique",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "gear": 5
            },
            "primary_keyword_fr": "chasse affût mirador",
            "search_volume_estimate": 5000,
            "priority": 2,
            "is_active": True
        },
        "cluster_bowhunting_ultime": {
            "id": "cluster_bowhunting_ultime",
            "name": "Bowhunting Ultimate",
            "name_fr": "Chasse à l'Arc ULTIME",
            "cluster_type": "technique",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "gear": 8
            },
            "primary_keyword_fr": "chasse arc arbalète québec",
            "search_volume_estimate": 7000,
            "priority": 1,
            "is_active": True
        },
        
        # ===================
        # ÉQUIPEMENT (10 clusters)
        # ===================
        "cluster_optics_ultime": {
            "id": "cluster_optics_ultime",
            "name": "Hunting Optics Ultimate",
            "name_fr": "Optiques de Chasse ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "gear": 10,
                "review": 8
            },
            "primary_keyword_fr": "lunettes jumelles chasse",
            "search_volume_estimate": 6000,
            "priority": 1,
            "is_active": True
        },
        "cluster_trail_cameras_ultime": {
            "id": "cluster_trail_cameras_ultime",
            "name": "Trail Cameras Ultimate",
            "name_fr": "Caméras de Chasse ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "gear": 12,
                "review": 10
            },
            "primary_keyword_fr": "caméras trail chasse",
            "search_volume_estimate": 9000,
            "priority": 1,
            "is_active": True
        },
        "cluster_clothing_ultime": {
            "id": "cluster_clothing_ultime",
            "name": "Hunting Clothing Ultimate",
            "name_fr": "Vêtements de Chasse ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 12,
                "gear": 15,
                "review": 8
            },
            "primary_keyword_fr": "vêtements chasse camo",
            "search_volume_estimate": 8000,
            "priority": 1,
            "is_active": True
        },
        "cluster_bows_crossbows_ultime": {
            "id": "cluster_bows_crossbows_ultime",
            "name": "Bows & Crossbows Ultimate",
            "name_fr": "Arcs et Arbalètes ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "gear": 15,
                "review": 12
            },
            "primary_keyword_fr": "arcs arbalètes chasse",
            "search_volume_estimate": 10000,
            "priority": 1,
            "is_active": True
        },
        "cluster_treestands_ultime": {
            "id": "cluster_treestands_ultime",
            "name": "Treestands & Saddles Ultimate",
            "name_fr": "Miradors et Saddles ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "gear": 10,
                "review": 6
            },
            "primary_keyword_fr": "treestands miradors saddle hunting",
            "search_volume_estimate": 5000,
            "priority": 2,
            "is_active": True
        },
        "cluster_scents_ultime": {
            "id": "cluster_scents_ultime",
            "name": "Scents & Attractants Ultimate",
            "name_fr": "Urines et Attractants ULTIME",
            "cluster_type": "equipment",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 8,
                "gear": 10,
                "review": 5
            },
            "primary_keyword_fr": "urines attractants chasse",
            "search_volume_estimate": 6000,
            "priority": 2,
            "is_active": True
        },
        
        # ===================
        # SAISONS (5 clusters)
        # ===================
        "cluster_rut_ultime": {
            "id": "cluster_rut_ultime",
            "name": "Rut Season Ultimate",
            "name_fr": "Saison du Rut ULTIME",
            "cluster_type": "season",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 12
            },
            "primary_keyword_fr": "rut chevreuil orignal",
            "search_volume_estimate": 12000,
            "priority": 1,
            "is_active": True
        },
        "cluster_spring_bear_ultime": {
            "id": "cluster_spring_bear_ultime",
            "name": "Spring Bear Season Ultimate",
            "name_fr": "Chasse Ours Printemps ULTIME",
            "cluster_type": "season",
            "target_pages": {
                "pillar": 1,
                "satellites": 5,
                "opportunities": 6
            },
            "primary_keyword_fr": "chasse ours printemps québec",
            "search_volume_estimate": 4000,
            "priority": 2,
            "is_active": True
        },
        
        # ===================
        # RÉGLEMENTATION (3 clusters)
        # ===================
        "cluster_permits_ultime": {
            "id": "cluster_permits_ultime",
            "name": "Hunting Permits Ultimate",
            "name_fr": "Permis de Chasse ULTIME",
            "cluster_type": "regulation",
            "target_pages": {
                "pillar": 1,
                "satellites": 6,
                "opportunities": 10,
                "regulation": 8
            },
            "primary_keyword_fr": "permis chasse québec",
            "search_volume_estimate": 15000,
            "priority": 1,
            "is_active": True
        },
        "cluster_zones_ultime": {
            "id": "cluster_zones_ultime",
            "name": "Hunting Zones Ultimate",
            "name_fr": "Zones de Chasse ULTIME",
            "cluster_type": "regulation",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 12,
                "regulation": 10,
                "territory": 15
            },
            "primary_keyword_fr": "zones chasse québec",
            "search_volume_estimate": 10000,
            "priority": 1,
            "is_active": True
        },
        
        # ===================
        # HÉBERGEMENT (4 clusters)
        # ===================
        "cluster_outfitters_ultime": {
            "id": "cluster_outfitters_ultime",
            "name": "Outfitters Ultimate",
            "name_fr": "Pourvoiries ULTIME",
            "cluster_type": "accommodation",
            "target_pages": {
                "pillar": 1,
                "satellites": 10,
                "opportunities": 15,
                "territory": 20,
                "review": 10
            },
            "primary_keyword_fr": "pourvoiries chasse québec",
            "search_volume_estimate": 12000,
            "priority": 1,
            "is_active": True
        },
        "cluster_zecs_ultime": {
            "id": "cluster_zecs_ultime",
            "name": "ZECs Ultimate",
            "name_fr": "ZECs ULTIME",
            "cluster_type": "accommodation",
            "target_pages": {
                "pillar": 1,
                "satellites": 8,
                "opportunities": 10,
                "territory": 15
            },
            "primary_keyword_fr": "zec chasse québec",
            "search_volume_estimate": 8000,
            "priority": 1,
            "is_active": True
        }
    }
    
    # ============================================
    # CATÉGORIES ULTIMES (25)
    # ============================================
    
    CATEGORIES_ULTIME = {
        "cameras": {
            "id": "cat_cameras",
            "name_fr": "Caméras de Chasse",
            "subcategories": ["trail_cameras", "cellular_cameras", "solar_cameras", "security_cameras"],
            "supplier_count": 13,
            "page_target": 25
        },
        "arcs_arbaletes": {
            "id": "cat_arcs",
            "name_fr": "Arcs et Arbalètes",
            "subcategories": ["compound_bows", "recurve_bows", "crossbows", "accessories"],
            "supplier_count": 12,
            "page_target": 30
        },
        "treestands": {
            "id": "cat_treestands",
            "name_fr": "Miradors et Saddles",
            "subcategories": ["hang_on_stands", "climbing_stands", "ladder_stands", "saddles"],
            "supplier_count": 9,
            "page_target": 20
        },
        "urines_attractants": {
            "id": "cat_scents",
            "name_fr": "Urines et Attractants",
            "subcategories": ["deer_scents", "moose_scents", "cover_scents", "attractants"],
            "supplier_count": 9,
            "page_target": 18
        },
        "vetements": {
            "id": "cat_clothing",
            "name_fr": "Vêtements de Chasse",
            "subcategories": ["base_layers", "insulation", "outerwear", "rain_gear", "camo"],
            "supplier_count": 10,
            "page_target": 25
        },
        "optiques": {
            "id": "cat_optics",
            "name_fr": "Optiques",
            "subcategories": ["riflescopes", "binoculars", "rangefinders", "spotting_scopes"],
            "supplier_count": 7,
            "page_target": 20
        },
        "bottes": {
            "id": "cat_boots",
            "name_fr": "Bottes de Chasse",
            "subcategories": ["rubber_boots", "insulated_boots", "hiking_boots", "waders"],
            "supplier_count": 7,
            "page_target": 15
        },
        "backpacks": {
            "id": "cat_packs",
            "name_fr": "Sacs à Dos",
            "subcategories": ["daypacks", "frame_packs", "meat_hauling", "bow_cases"],
            "supplier_count": 6,
            "page_target": 12
        },
        "knives": {
            "id": "cat_knives",
            "name_fr": "Couteaux",
            "subcategories": ["fixed_blade", "folding", "skinning", "processing"],
            "supplier_count": 7,
            "page_target": 15
        },
        "boats_kayaks": {
            "id": "cat_boats",
            "name_fr": "Bateaux et Kayaks",
            "subcategories": ["kayaks", "canoes", "inflatables", "motors"],
            "supplier_count": 7,
            "page_target": 12
        },
        "electronics": {
            "id": "cat_electronics",
            "name_fr": "Électronique",
            "subcategories": ["gps", "radios", "thermal", "ozone"],
            "supplier_count": 6,
            "page_target": 12
        },
        "coolers": {
            "id": "cat_coolers",
            "name_fr": "Glacières",
            "subcategories": ["hard_coolers", "soft_coolers", "game_bags"],
            "supplier_count": 6,
            "page_target": 10
        },
        "processing": {
            "id": "cat_processing",
            "name_fr": "Transformation",
            "subcategories": ["grinders", "sausage_stuffers", "smokers", "dehydrators"],
            "supplier_count": 6,
            "page_target": 12
        },
        "firearms_accessories": {
            "id": "cat_firearms_acc",
            "name_fr": "Accessoires Armes",
            "subcategories": ["stocks", "triggers", "sights", "cleaning"],
            "supplier_count": 0,
            "page_target": 15,
            "status": "PLANNED"
        },
        "dog_equipment": {
            "id": "cat_dogs",
            "name_fr": "Équipement Chiens",
            "subcategories": ["tracking_collars", "vests", "training", "kennels"],
            "supplier_count": 0,
            "page_target": 10,
            "status": "PLANNED"
        }
    }
    
    # ============================================
    # INTENTIONS DE RECHERCHE
    # ============================================
    
    SEARCH_INTENTS = {
        "informational": {
            "id": "intent_info",
            "name_fr": "Informationnel",
            "patterns_fr": [
                "comment", "qu'est-ce que", "pourquoi", "quand", "où",
                "guide", "tutoriel", "conseils", "astuces", "techniques"
            ],
            "patterns_en": [
                "how to", "what is", "why", "when", "where",
                "guide", "tutorial", "tips", "tricks", "techniques"
            ],
            "page_types": ["pillar", "satellite", "opportunity"]
        },
        "transactional": {
            "id": "intent_trans",
            "name_fr": "Transactionnel",
            "patterns_fr": [
                "acheter", "prix", "pas cher", "meilleur prix", "promotion",
                "commander", "livraison", "en stock"
            ],
            "patterns_en": [
                "buy", "price", "cheap", "best price", "sale",
                "order", "shipping", "in stock"
            ],
            "page_types": ["gear", "review"]
        },
        "commercial_investigation": {
            "id": "intent_commercial",
            "name_fr": "Investigation Commerciale",
            "patterns_fr": [
                "meilleur", "top", "comparatif", "vs", "avis", "test",
                "review", "classement", "recommandation"
            ],
            "patterns_en": [
                "best", "top", "comparison", "vs", "review", "test",
                "rating", "ranking", "recommendation"
            ],
            "page_types": ["gear", "review", "comparison", "vs"]
        },
        "local": {
            "id": "intent_local",
            "name_fr": "Local",
            "patterns_fr": [
                "près de", "proche", "région", "zone", "québec",
                "laurentides", "abitibi", "mauricie"
            ],
            "patterns_en": [
                "near me", "nearby", "region", "zone", "quebec",
                "laurentides", "abitibi", "mauricie"
            ],
            "page_types": ["territory", "pillar", "satellite"]
        },
        "navigational": {
            "id": "intent_nav",
            "name_fr": "Navigationnel",
            "patterns_fr": [
                "site officiel", "contact", "téléphone", "adresse"
            ],
            "patterns_en": [
                "official site", "contact", "phone", "address"
            ],
            "page_types": ["territory"]
        }
    }
    
    # ============================================
    # MÉTHODES
    # ============================================
    
    @staticmethod
    def get_all_clusters() -> dict:
        """Retourner tous les clusters ULTIMES"""
        return SEOClustersUltime.CLUSTERS_ULTIME
    
    @staticmethod
    def get_cluster_count() -> int:
        """Retourner le nombre de clusters"""
        return len(SEOClustersUltime.CLUSTERS_ULTIME)
    
    @staticmethod
    def get_categories() -> dict:
        """Retourner toutes les catégories"""
        return SEOClustersUltime.CATEGORIES_ULTIME
    
    @staticmethod
    def get_search_intents() -> dict:
        """Retourner les intentions de recherche"""
        return SEOClustersUltime.SEARCH_INTENTS
    
    @staticmethod
    def get_strategy_summary() -> dict:
        """Résumé de la stratégie"""
        clusters = SEOClustersUltime.CLUSTERS_ULTIME
        categories = SEOClustersUltime.CATEGORIES_ULTIME
        
        return {
            "total_clusters": len(clusters),
            "active_clusters": len([c for c in clusters.values() if c.get("is_active")]),
            "total_categories": len(categories),
            "target_pages": SEOClustersUltime.STRATEGY_TARGETS["total_pages"],
            "page_distribution": SEOClustersUltime.STRATEGY_TARGETS["page_distribution"],
            "traffic_target": SEOClustersUltime.STRATEGY_TARGETS["traffic_increase_target"],
            "clusters_by_type": {
                "species": len([c for c in clusters.values() if c.get("cluster_type") == "species"]),
                "region": len([c for c in clusters.values() if c.get("cluster_type") == "region"]),
                "technique": len([c for c in clusters.values() if c.get("cluster_type") == "technique"]),
                "equipment": len([c for c in clusters.values() if c.get("cluster_type") == "equipment"]),
                "season": len([c for c in clusters.values() if c.get("cluster_type") == "season"]),
                "regulation": len([c for c in clusters.values() if c.get("cluster_type") == "regulation"]),
                "accommodation": len([c for c in clusters.values() if c.get("cluster_type") == "accommodation"])
            }
        }


logger.info("SEOClustersUltime initialized - V5 LEGO Module with 50 Clusters for 1147 Pages")
