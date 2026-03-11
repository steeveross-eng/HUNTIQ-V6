"""
BIONIC SEO Rules Engine - V5-ULTIME
====================================

Règles SEO avancées pour conformité internationale et protection système.

Règles Implémentées:
- Règles internationales (7 marchés)
- Règles anti-doublons avancées
- Règles anti-casse-système
- Règles de validation structure
- Règles de conformité Québec

Module isolé - Architecture LEGO V5.
"""

import logging

logger = logging.getLogger(__name__)


class SEORulesEngine:
    """Moteur de règles SEO avancées"""
    
    # ============================================
    # RÈGLES INTERNATIONALES (7 MARCHÉS)
    # ============================================
    
    INTERNATIONAL_RULES = {
        "FR_QC": {
            "id": "rule_fr_qc",
            "name": "Règle Français Québec",
            "market": "FR_QC",
            "language": "fr",
            "region": "Quebec, Canada",
            "requirements": {
                "language_code": "fr-CA",
                "currency": "CAD",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["MFFP", "SEPAQ", "FQF"],
                "regulations_source": "quebec.ca/faune",
                "local_terms": {
                    "deer": "chevreuil",
                    "moose": "orignal",
                    "bear": "ours noir",
                    "hunting": "chasse",
                    "outfitter": "pourvoirie",
                    "zone": "ZEC"
                }
            },
            "seo_config": {
                "title_suffix": " | Québec",
                "meta_lang": "fr-CA",
                "hreflang": "fr-ca",
                "local_schema": "LocalBusiness"
            },
            "is_active": True,
            "priority": 1
        },
        "FR_CA": {
            "id": "rule_fr_ca",
            "name": "Règle Français Canada",
            "market": "FR_CA",
            "language": "fr",
            "region": "Canada (hors Québec)",
            "requirements": {
                "language_code": "fr-CA",
                "currency": "CAD",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["Gouvernement du Canada", "Parcs Canada"],
                "local_terms": {
                    "deer": "cerf",
                    "moose": "orignal",
                    "bear": "ours",
                    "hunting": "chasse",
                    "outfitter": "pourvoyeur"
                }
            },
            "seo_config": {
                "title_suffix": " | Canada",
                "meta_lang": "fr-CA",
                "hreflang": "fr-ca"
            },
            "is_active": True,
            "priority": 2
        },
        "FR_EU": {
            "id": "rule_fr_eu",
            "name": "Règle Français Europe",
            "market": "FR_EU",
            "language": "fr",
            "region": "France, Belgique, Suisse",
            "requirements": {
                "language_code": "fr-FR",
                "currency": "EUR",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["OFB", "Fédération de Chasse"],
                "gdpr_compliant": True,
                "local_terms": {
                    "deer": "cerf",
                    "moose": "élan",
                    "bear": "ours",
                    "hunting": "chasse",
                    "outfitter": "guide de chasse"
                }
            },
            "seo_config": {
                "title_suffix": " | France",
                "meta_lang": "fr-FR",
                "hreflang": "fr"
            },
            "is_active": True,
            "priority": 3
        },
        "EN_CA": {
            "id": "rule_en_ca",
            "name": "English Canada Rule",
            "market": "EN_CA",
            "language": "en",
            "region": "Canada (English)",
            "requirements": {
                "language_code": "en-CA",
                "currency": "CAD",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["Government of Canada", "Parks Canada"],
                "local_terms": {
                    "deer": "whitetail deer",
                    "moose": "moose",
                    "bear": "black bear",
                    "hunting": "hunting",
                    "outfitter": "outfitter"
                }
            },
            "seo_config": {
                "title_suffix": " | Canada",
                "meta_lang": "en-CA",
                "hreflang": "en-ca"
            },
            "is_active": True,
            "priority": 2
        },
        "EN_US": {
            "id": "rule_en_us",
            "name": "English USA Rule",
            "market": "EN_US",
            "language": "en",
            "region": "United States",
            "requirements": {
                "language_code": "en-US",
                "currency": "USD",
                "date_format": "MM/DD/YYYY",
                "measurement_unit": "imperial",
                "legal_mentions": ["USFWS", "State Game Commission"],
                "local_terms": {
                    "deer": "whitetail",
                    "moose": "moose",
                    "bear": "black bear",
                    "hunting": "hunting",
                    "outfitter": "outfitter"
                }
            },
            "seo_config": {
                "title_suffix": " | USA",
                "meta_lang": "en-US",
                "hreflang": "en-us"
            },
            "is_active": True,
            "priority": 2
        },
        "EN_AU": {
            "id": "rule_en_au",
            "name": "English Australia Rule",
            "market": "EN_AU",
            "language": "en",
            "region": "Australia",
            "requirements": {
                "language_code": "en-AU",
                "currency": "AUD",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["State Wildlife Authority"],
                "local_terms": {
                    "deer": "deer",
                    "hunting": "hunting",
                    "outfitter": "hunting guide"
                }
            },
            "seo_config": {
                "title_suffix": " | Australia",
                "meta_lang": "en-AU",
                "hreflang": "en-au"
            },
            "is_active": False,
            "priority": 4
        },
        "EN_NZ": {
            "id": "rule_en_nz",
            "name": "English New Zealand Rule",
            "market": "EN_NZ",
            "language": "en",
            "region": "New Zealand",
            "requirements": {
                "language_code": "en-NZ",
                "currency": "NZD",
                "date_format": "DD/MM/YYYY",
                "measurement_unit": "metric",
                "legal_mentions": ["DOC", "Fish & Game NZ"],
                "local_terms": {
                    "deer": "deer",
                    "hunting": "hunting",
                    "outfitter": "hunting guide"
                }
            },
            "seo_config": {
                "title_suffix": " | New Zealand",
                "meta_lang": "en-NZ",
                "hreflang": "en-nz"
            },
            "is_active": False,
            "priority": 4
        }
    }
    
    # ============================================
    # RÈGLES ANTI-DOUBLONS
    # ============================================
    
    DUPLICATE_RULES = {
        "title_duplicate": {
            "id": "rule_title_duplicate",
            "name": "Règle Anti-Doublon Titre",
            "description": "Empêche la création de pages avec des titres identiques ou très similaires",
            "threshold": 0.85,
            "action": "BLOCK",
            "check_fields": ["title", "title_fr"],
            "algorithm": "cosine_similarity",
            "is_active": True
        },
        "url_duplicate": {
            "id": "rule_url_duplicate",
            "name": "Règle Anti-Doublon URL",
            "description": "Empêche la création de pages avec des URLs identiques",
            "threshold": 1.0,
            "action": "BLOCK",
            "check_fields": ["slug", "url_path"],
            "algorithm": "exact_match",
            "is_active": True
        },
        "content_duplicate": {
            "id": "rule_content_duplicate",
            "name": "Règle Anti-Doublon Contenu",
            "description": "Détecte le contenu dupliqué entre pages",
            "threshold": 0.80,
            "action": "WARN",
            "check_fields": ["content_html", "content_markdown"],
            "algorithm": "simhash",
            "is_active": True
        },
        "meta_duplicate": {
            "id": "rule_meta_duplicate",
            "name": "Règle Anti-Doublon Meta",
            "description": "Empêche les meta descriptions identiques",
            "threshold": 0.90,
            "action": "WARN",
            "check_fields": ["meta_description", "meta_description_fr"],
            "algorithm": "cosine_similarity",
            "is_active": True
        },
        "keyword_cannibalization": {
            "id": "rule_keyword_cannibalization",
            "name": "Règle Anti-Cannibalisation",
            "description": "Détecte les pages ciblant le même mot-clé principal",
            "threshold": 1.0,
            "action": "WARN",
            "check_fields": ["primary_keyword"],
            "algorithm": "exact_match",
            "is_active": True
        }
    }
    
    # ============================================
    # RÈGLES ANTI-CASSE-SYSTÈME
    # ============================================
    
    SYSTEM_PROTECTION_RULES = {
        "prevent_mass_delete": {
            "id": "rule_prevent_mass_delete",
            "name": "Prévention Suppression de Masse",
            "description": "Bloque la suppression de plus de 10 éléments à la fois",
            "max_batch_delete": 10,
            "requires_confirmation": True,
            "audit_log": True,
            "is_active": True
        },
        "prevent_cluster_delete_with_pages": {
            "id": "rule_prevent_cluster_delete",
            "name": "Prévention Suppression Cluster avec Pages",
            "description": "Empêche la suppression d'un cluster contenant des pages",
            "action": "BLOCK",
            "requires_empty": True,
            "is_active": True
        },
        "prevent_published_delete": {
            "id": "rule_prevent_published_delete",
            "name": "Prévention Suppression Page Publiée",
            "description": "Nécessite archivage avant suppression d'une page publiée",
            "action": "REQUIRE_ARCHIVE",
            "grace_period_days": 30,
            "is_active": True
        },
        "prevent_base_cluster_modify": {
            "id": "rule_prevent_base_modify",
            "name": "Protection Clusters de Base",
            "description": "Empêche la modification des 9 clusters de base",
            "protected_ids": [
                "cluster_moose", "cluster_deer", "cluster_bear",
                "cluster_laurentides", "cluster_abitibi", "cluster_rut_season",
                "cluster_calling", "cluster_scouting", "cluster_equipment"
            ],
            "action": "BLOCK",
            "is_active": True
        },
        "require_backup_before_bulk": {
            "id": "rule_require_backup",
            "name": "Backup Obligatoire Avant Bulk",
            "description": "Exige un backup avant toute opération en masse",
            "threshold_items": 5,
            "action": "REQUIRE_BACKUP",
            "is_active": True
        },
        "rate_limit_generation": {
            "id": "rule_rate_limit",
            "name": "Limite de Taux Génération",
            "description": "Limite la génération IA à 10 pages/heure",
            "max_per_hour": 10,
            "max_per_day": 50,
            "action": "THROTTLE",
            "is_active": True
        },
        "validate_before_publish": {
            "id": "rule_validate_publish",
            "name": "Validation Avant Publication",
            "description": "Exige score SEO minimum et structure valide avant publication",
            "min_seo_score": 60,
            "required_fields": ["title_fr", "meta_description_fr", "h1", "primary_keyword"],
            "min_word_count": 300,
            "action": "BLOCK",
            "is_active": True
        },
        "audit_all_changes": {
            "id": "rule_audit_changes",
            "name": "Audit Toutes Modifications",
            "description": "Journalise toutes les modifications pour rollback",
            "log_create": True,
            "log_update": True,
            "log_delete": True,
            "retention_days": 90,
            "is_active": True
        }
    }
    
    # ============================================
    # RÈGLES DE VALIDATION STRUCTURE
    # ============================================
    
    STRUCTURE_RULES = {
        "require_h1": {
            "id": "rule_require_h1",
            "description": "H1 obligatoire et unique",
            "validation": "exactly_one",
            "is_active": True
        },
        "require_h2": {
            "id": "rule_require_h2",
            "description": "Minimum 3 H2 par page",
            "validation": "min_count",
            "min_count": 3,
            "is_active": True
        },
        "require_meta": {
            "id": "rule_require_meta",
            "description": "Meta description obligatoire (120-160 chars)",
            "validation": "length_range",
            "min_length": 120,
            "max_length": 160,
            "is_active": True
        },
        "require_keyword": {
            "id": "rule_require_keyword",
            "description": "Mot-clé principal obligatoire",
            "validation": "not_empty",
            "is_active": True
        },
        "require_internal_links": {
            "id": "rule_require_links",
            "description": "Minimum 8 liens internes",
            "validation": "min_count",
            "min_count": 8,
            "is_active": True
        },
        "require_cta": {
            "id": "rule_require_cta",
            "description": "Au moins 1 CTA par page",
            "validation": "min_count",
            "min_count": 1,
            "is_active": True
        },
        "require_faq": {
            "id": "rule_require_faq",
            "description": "FAQ recommandée (5-8 questions)",
            "validation": "recommended",
            "min_count": 5,
            "max_count": 8,
            "is_active": True
        },
        "require_jsonld": {
            "id": "rule_require_jsonld",
            "description": "Au moins 2 schémas JSON-LD",
            "validation": "min_count",
            "min_count": 2,
            "is_active": True
        }
    }
    
    # ============================================
    # RÈGLES CONFORMITÉ QUÉBEC
    # ============================================
    
    QUEBEC_COMPLIANCE_RULES = {
        "language_bill_96": {
            "id": "rule_bill_96",
            "name": "Conformité Loi 96",
            "description": "Contenu français prioritaire selon la Loi 96",
            "requirements": [
                "Titre français obligatoire",
                "Meta description française obligatoire",
                "Contenu principal en français",
                "Version anglaise optionnelle mais secondaire"
            ],
            "is_active": True
        },
        "mffp_compliance": {
            "id": "rule_mffp",
            "name": "Conformité MFFP",
            "description": "Respect des règlements du Ministère des Forêts, de la Faune et des Parcs",
            "requirements": [
                "Dates de saison officielles",
                "Zones de chasse correctes",
                "Quotas à jour",
                "Permis requis mentionnés"
            ],
            "source": "https://www.quebec.ca/faune",
            "is_active": True
        },
        "sepaq_compliance": {
            "id": "rule_sepaq",
            "name": "Conformité SEPAQ",
            "description": "Informations correctes sur les réserves fauniques",
            "requirements": [
                "Noms officiels des réserves",
                "Tarifs à jour",
                "Disponibilités exactes"
            ],
            "source": "https://www.sepaq.com",
            "is_active": True
        },
        "zec_compliance": {
            "id": "rule_zec",
            "name": "Conformité ZECs",
            "description": "Informations correctes sur les ZECs",
            "requirements": [
                "Liste officielle des ZECs",
                "Coordonnées exactes",
                "Règlements spécifiques"
            ],
            "is_active": True
        }
    }
    
    # ============================================
    # MÉTHODES DE VALIDATION
    # ============================================
    
    @staticmethod
    def validate_page(page_data: dict, db=None) -> dict:
        """Valider une page selon toutes les règles actives"""
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 100
        }
        
        # Validation structure
        structure_issues = SEORulesEngine._validate_structure(page_data)
        results["errors"].extend(structure_issues.get("errors", []))
        results["warnings"].extend(structure_issues.get("warnings", []))
        
        # Validation international
        market = page_data.get("target_market", "FR_QC")
        market_issues = SEORulesEngine._validate_market_compliance(page_data, market)
        results["warnings"].extend(market_issues.get("warnings", []))
        
        # Score adjustment
        results["score"] -= len(results["errors"]) * 10
        results["score"] -= len(results["warnings"]) * 3
        results["score"] = max(0, results["score"])
        
        results["valid"] = len(results["errors"]) == 0
        
        return results
    
    @staticmethod
    def _validate_structure(page_data: dict) -> dict:
        """Valider la structure d'une page"""
        issues = {"errors": [], "warnings": []}
        
        # H1
        if not page_data.get("h1"):
            issues["errors"].append("H1 manquant")
        
        # H2
        h2_list = page_data.get("h2_list", [])
        if len(h2_list) < 3:
            issues["errors"].append(f"Minimum 3 H2 requis (actuel: {len(h2_list)})")
        
        # Meta description
        meta = page_data.get("meta_description_fr", "")
        if not meta:
            issues["errors"].append("Meta description manquante")
        elif len(meta) < 120:
            issues["warnings"].append(f"Meta description trop courte ({len(meta)} chars)")
        elif len(meta) > 160:
            issues["warnings"].append(f"Meta description trop longue ({len(meta)} chars)")
        
        # Keyword
        if not page_data.get("primary_keyword"):
            issues["errors"].append("Mot-clé principal manquant")
        
        # Internal links
        links = page_data.get("internal_links_out", [])
        if len(links) < 8:
            issues["warnings"].append(f"Minimum 8 liens internes recommandés (actuel: {len(links)})")
        
        # Word count
        word_count = page_data.get("word_count", 0)
        min_words = {"pillar": 2000, "satellite": 800, "opportunity": 400}.get(
            page_data.get("page_type", "satellite"), 800
        )
        if word_count < min_words:
            issues["errors"].append(f"Contenu trop court ({word_count} mots, min: {min_words})")
        
        return issues
    
    @staticmethod
    def _validate_market_compliance(page_data: dict, market: str) -> dict:
        """Valider la conformité marché"""
        issues = {"warnings": []}
        
        rule = SEORulesEngine.INTERNATIONAL_RULES.get(market)
        if not rule:
            issues["warnings"].append(f"Marché inconnu: {market}")
            return issues
        
        # Check language code
        expected_lang = rule["requirements"]["language_code"]
        # Additional market-specific checks can be added here
        
        return issues
    
    @staticmethod
    async def check_duplicates(db, page_data: dict) -> dict:
        """Vérifier les doublons potentiels"""
        results = {
            "has_duplicates": False,
            "duplicates": []
        }
        
        # Check title duplicate
        title = page_data.get("title_fr", page_data.get("title", ""))
        if title:
            existing = await db.seo_pages.find_one(
                {"title_fr": title, "id": {"$ne": page_data.get("id")}},
                {"_id": 0, "id": 1, "title_fr": 1}
            )
            if existing:
                results["has_duplicates"] = True
                results["duplicates"].append({
                    "type": "title",
                    "existing_id": existing["id"],
                    "existing_title": existing["title_fr"],
                    "action": "BLOCK"
                })
        
        # Check URL duplicate
        slug = page_data.get("slug", "")
        if slug:
            existing = await db.seo_pages.find_one(
                {"slug": slug, "id": {"$ne": page_data.get("id")}},
                {"_id": 0, "id": 1, "slug": 1}
            )
            if existing:
                results["has_duplicates"] = True
                results["duplicates"].append({
                    "type": "url",
                    "existing_id": existing["id"],
                    "existing_slug": existing["slug"],
                    "action": "BLOCK"
                })
        
        # Check keyword cannibalization
        keyword = page_data.get("primary_keyword", "")
        if keyword:
            existing = await db.seo_pages.find_one(
                {"primary_keyword": keyword, "id": {"$ne": page_data.get("id")}},
                {"_id": 0, "id": 1, "primary_keyword": 1, "title_fr": 1}
            )
            if existing:
                results["duplicates"].append({
                    "type": "keyword_cannibalization",
                    "existing_id": existing["id"],
                    "keyword": keyword,
                    "action": "WARN"
                })
        
        return results
    
    @staticmethod
    def get_all_rules() -> dict:
        """Retourner toutes les règles actives"""
        return {
            "international_rules": SEORulesEngine.INTERNATIONAL_RULES,
            "duplicate_rules": SEORulesEngine.DUPLICATE_RULES,
            "system_protection_rules": SEORulesEngine.SYSTEM_PROTECTION_RULES,
            "structure_rules": SEORulesEngine.STRUCTURE_RULES,
            "quebec_compliance_rules": SEORulesEngine.QUEBEC_COMPLIANCE_RULES,
            "total_rules": (
                len(SEORulesEngine.INTERNATIONAL_RULES) +
                len(SEORulesEngine.DUPLICATE_RULES) +
                len(SEORulesEngine.SYSTEM_PROTECTION_RULES) +
                len(SEORulesEngine.STRUCTURE_RULES) +
                len(SEORulesEngine.QUEBEC_COMPLIANCE_RULES)
            )
        }
    
    @staticmethod
    def get_rules_summary() -> dict:
        """Résumé des règles"""
        return {
            "international_markets": 7,
            "active_markets": len([r for r in SEORulesEngine.INTERNATIONAL_RULES.values() if r["is_active"]]),
            "duplicate_rules": len(SEORulesEngine.DUPLICATE_RULES),
            "protection_rules": len(SEORulesEngine.SYSTEM_PROTECTION_RULES),
            "structure_rules": len(SEORulesEngine.STRUCTURE_RULES),
            "quebec_rules": len(SEORulesEngine.QUEBEC_COMPLIANCE_RULES)
        }


logger.info("SEORulesEngine initialized - V5 LEGO Module with International + Anti-Duplicate + Protection Rules")
