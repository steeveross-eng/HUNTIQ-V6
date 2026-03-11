"""
SEO BIONIC - Script d'Intégration des Partenaires
═══════════════════════════════════════════════════════════════════════════════
DIRECTIVE COPILOT MAÎTRE : Intégration complète avec:
1. Déduplication (exacte + fuzzy)
2. Normalisation des noms et catégories
3. Enrichissement (ecommerce_url, market_scope)
4. Validation des URLs (www. ENFORCÉ)
5. Insertion en base de données
6. Génération des rapports
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
from fuzzywuzzy import fuzz
import re
import sys

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

sys.path.insert(0, '/app/backend')

from modules.seo_engine.seo_normalization import normalize_url
from modules.seo_engine.seo_enrichment import enrich_ecommerce
from modules.seo_engine.seo_database import seo_db


class PartnersIntegration:
    """
    Pipeline d'intégration des partenaires SEO BIONIC
    """
    
    # Seuil de similarité pour déduplication fuzzy
    FUZZY_THRESHOLD = 85
    
    # Mapping de normalisation des catégories
    CATEGORY_MAPPING = {
        'national retailer': 'national_retailer',
        'specialized retailer': 'specialized_retailer',
        'clothing/outdoor': 'clothing_outdoor',
        'hunting gear brand': 'hunting_gear_brand',
        'archery brand': 'archery_brand',
        'outdoor technology': 'outdoor_technology',
        'optics brand': 'optics_brand',
        'ammunition brand': 'ammunition_brand',
        'call/decoy brand': 'call_decoy_brand',
        'us retailer': 'us_retailer',
        'us manufacturer': 'us_manufacturer',
        'game camera': 'game_camera',
        'tree stand': 'tree_stand',
        'general outdoor': 'general_outdoor',
        'e-commerce platform': 'ecommerce_platform'
    }
    
    # Mapping de normalisation des types
    TYPE_MAPPING = {
        'retailer': 'retailer',
        'brand': 'brand',
        'manufacturer': 'manufacturer',
        'distributor': 'distributor',
        'importer': 'importer',
        'retailer/importer': 'retailer_importer',
        'brand/importer': 'brand_importer',
        'platform': 'platform',
        'marketplace': 'marketplace'
    }
    
    # Mapping pays vers market_scope
    COUNTRY_MARKET_MAPPING = {
        'canada': 'canada',
        'usa': 'usa',
        'usa/canada': 'multi',
        'us': 'usa',
        'international': 'international',
        'europe': 'eu',
        'china': 'international',
        'japan': 'international'
    }
    
    def __init__(self):
        self.stats = {
            'total_raw': 0,
            'exact_duplicates_removed': 0,
            'fuzzy_duplicates_removed': 0,
            'total_after_dedup': 0,
            'total_normalized': 0,
            'total_enriched': 0,
            'total_inserted': 0,
            'total_rejected': 0,
            'total_duplicates_db': 0,
            'categories_found': defaultdict(int),
            'types_found': defaultdict(int),
            'countries_found': defaultdict(int),
            'market_scope_distribution': defaultdict(int)
        }
        self.duplicate_log = []
        self.rejected_log = []
    
    def load_raw_data(self, filepath: str) -> List[Dict[str, Any]]:
        """Charge les données brutes depuis le fichier JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        headers = data['headers']
        rows = data['data']
        
        partners = []
        for row in rows:
            if len(row) >= 5:
                partner = {
                    'category': row[0] if len(row) > 0 else '',
                    'name': row[1] if len(row) > 1 else '',
                    'type': row[2] if len(row) > 2 else '',
                    'country': row[3] if len(row) > 3 else '',
                    'url': row[4] if len(row) > 4 else '',
                    'notes': row[5] if len(row) > 5 else ''
                }
                if partner['name']:  # Ignorer les lignes sans nom
                    partners.append(partner)
        
        self.stats['total_raw'] = len(partners)
        return partners
    
    def normalize_name(self, name: str) -> str:
        """Normalise un nom de partenaire"""
        # Retirer les caractères spéciaux et normaliser
        normalized = name.strip()
        # Normaliser les espaces multiples
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def normalize_category(self, category: str) -> str:
        """Normalise une catégorie"""
        cat_lower = category.strip().lower()
        return self.CATEGORY_MAPPING.get(cat_lower, cat_lower.replace(' ', '_').replace('/', '_'))
    
    def normalize_type(self, partner_type: str) -> str:
        """Normalise un type de partenaire"""
        type_lower = partner_type.strip().lower()
        return self.TYPE_MAPPING.get(type_lower, type_lower.replace(' ', '_').replace('/', '_'))
    
    def normalize_country(self, country: str) -> str:
        """Normalise le pays et retourne le market_scope"""
        country_lower = country.strip().lower()
        return self.COUNTRY_MARKET_MAPPING.get(country_lower, 'unknown')
    
    def deduplicate_exact(self, partners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Déduplication exacte par nom et URL"""
        seen_names = set()
        seen_urls = set()
        unique_partners = []
        
        for partner in partners:
            name_key = partner['name'].lower().strip()
            url_key = partner['url'].lower().strip() if partner['url'] else ''
            
            # Vérifier duplication par nom exact
            if name_key in seen_names:
                self.stats['exact_duplicates_removed'] += 1
                self.duplicate_log.append({
                    'type': 'exact_name',
                    'partner': partner['name'],
                    'reason': f"Nom en double: {partner['name']}"
                })
                continue
            
            # Vérifier duplication par URL exacte
            if url_key and url_key in seen_urls:
                self.stats['exact_duplicates_removed'] += 1
                self.duplicate_log.append({
                    'type': 'exact_url',
                    'partner': partner['name'],
                    'reason': f"URL en double: {partner['url']}"
                })
                continue
            
            seen_names.add(name_key)
            if url_key:
                seen_urls.add(url_key)
            unique_partners.append(partner)
        
        return unique_partners
    
    def deduplicate_fuzzy(self, partners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Déduplication fuzzy par similarité de nom"""
        unique_partners = []
        processed_names = []
        
        for partner in partners:
            name = partner['name']
            is_duplicate = False
            
            for existing_name in processed_names:
                similarity = fuzz.ratio(name.lower(), existing_name.lower())
                
                if similarity >= self.FUZZY_THRESHOLD and name.lower() != existing_name.lower():
                    is_duplicate = True
                    self.stats['fuzzy_duplicates_removed'] += 1
                    self.duplicate_log.append({
                        'type': 'fuzzy',
                        'partner': name,
                        'similar_to': existing_name,
                        'similarity': similarity,
                        'reason': f"Similaire à {existing_name} ({similarity}%)"
                    })
                    break
            
            if not is_duplicate:
                unique_partners.append(partner)
                processed_names.append(name)
        
        return unique_partners
    
    def normalize_partners(self, partners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalise tous les partenaires"""
        normalized = []
        
        for partner in partners:
            norm_partner = {
                'name': self.normalize_name(partner['name']),
                'name_original': partner['name'],
                'category': self.normalize_category(partner['category']),
                'category_original': partner['category'],
                'type': self.normalize_type(partner['type']),
                'type_original': partner['type'],
                'country': partner['country'],
                'market_scope': self.normalize_country(partner['country']),
                'url': partner['url'],
                'notes': partner.get('notes', ''),
                # Champs à enrichir
                'ecommerce_url': None,
                'has_ecommerce': False,
                'no_ecommerce': True,
                'url_normalized': False,
                'aliases': []
            }
            
            # Stats
            self.stats['categories_found'][norm_partner['category']] += 1
            self.stats['types_found'][norm_partner['type']] += 1
            self.stats['countries_found'][norm_partner['country']] += 1
            self.stats['market_scope_distribution'][norm_partner['market_scope']] += 1
            
            normalized.append(norm_partner)
        
        self.stats['total_normalized'] = len(normalized)
        return normalized
    
    def enrich_partners(self, partners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrichit les partenaires avec les données e-commerce"""
        enriched = []
        
        for partner in partners:
            # Utiliser le module d'enrichissement
            result = enrich_ecommerce(
                partner_name=partner['name'],
                url=partner['url'],
                additional_info={
                    'country': partner['country'],
                    'category': partner['category'],
                    'notes': partner['notes']
                }
            )
            
            # Mise à jour avec les résultats d'enrichissement
            partner['ecommerce_url'] = result.ecommerce_url
            partner['has_ecommerce'] = result.has_ecommerce
            partner['no_ecommerce'] = result.no_ecommerce
            partner['ecommerce_platform'] = result.ecommerce_platform
            partner['url_normalized'] = result.url_normalized
            
            # Mettre à jour market_scope si détecté
            if result.market_scope != 'unknown':
                partner['market_scope'] = result.market_scope
            
            # Normaliser l'URL principale
            if partner['url']:
                url_result = normalize_url(partner['url'])
                if url_result.normalized_url and not url_result.url_invalid:
                    partner['url'] = url_result.normalized_url
                    partner['url_normalized'] = True
            
            enriched.append(partner)
        
        self.stats['total_enriched'] = len(enriched)
        return enriched
    
    async def insert_to_database(self, partners: List[Dict[str, Any]], collection_name: str = 'seo_partners') -> Dict[str, Any]:
        """Insère les partenaires en base de données"""
        # Préparer les documents pour l'insertion
        documents = []
        
        for partner in partners:
            doc = {
                'name': partner['name'],
                'name_original': partner.get('name_original', partner['name']),
                'category': partner['category'],
                'type': partner['type'],
                'country': partner['country'],
                'market_scope': partner['market_scope'],
                'url': partner['url'],
                'ecommerce_url': partner.get('ecommerce_url'),
                'has_ecommerce': partner.get('has_ecommerce', False),
                'no_ecommerce': partner.get('no_ecommerce', True),
                'ecommerce_platform': partner.get('ecommerce_platform'),
                'notes': partner.get('notes', ''),
                'aliases': partner.get('aliases', []),
                'source': 'docx_import_feb_2026',
                'status': 'active'
            }
            documents.append(doc)
        
        # Insérer en utilisant le module de base de données
        result = await seo_db.insert_batch(
            collection_name=collection_name,
            documents=documents,
            auto_normalize=True,
            strict_validation=True,
            skip_duplicates=True
        )
        
        self.stats['total_inserted'] = result.total_inserted
        self.stats['total_rejected'] = result.total_rejected
        self.stats['total_duplicates_db'] = result.total_duplicates
        
        return {
            'inserted': result.total_inserted,
            'rejected': result.total_rejected,
            'duplicates': result.total_duplicates,
            'inserted_ids': result.inserted_ids[:10]  # Premiers IDs
        }
    
    def generate_reports(self, partners: List[Dict[str, Any]]) -> Dict[str, str]:
        """Génère tous les rapports"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        reports_dir = Path('/app/docs/reports')
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        reports = {}
        
        # Rapport de déduplication
        dedup_report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'statistics': {
                'total_raw': self.stats['total_raw'],
                'exact_duplicates_removed': self.stats['exact_duplicates_removed'],
                'fuzzy_duplicates_removed': self.stats['fuzzy_duplicates_removed'],
                'total_after_dedup': self.stats['total_after_dedup']
            },
            'duplicates_log': self.duplicate_log
        }
        dedup_path = reports_dir / f'PARTNERS_DEDUP_REPORT_{timestamp}.json'
        with open(dedup_path, 'w', encoding='utf-8') as f:
            json.dump(dedup_report, f, indent=2, ensure_ascii=False)
        reports['deduplication'] = str(dedup_path)
        
        # Rapport de validation
        validation_report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'statistics': {
                'total_normalized': self.stats['total_normalized'],
                'total_enriched': self.stats['total_enriched'],
                'total_inserted': self.stats['total_inserted'],
                'total_rejected': self.stats['total_rejected'],
                'total_duplicates_db': self.stats['total_duplicates_db']
            },
            'categories': dict(self.stats['categories_found']),
            'types': dict(self.stats['types_found']),
            'countries': dict(self.stats['countries_found']),
            'market_scope': dict(self.stats['market_scope_distribution']),
            'rejected_log': self.rejected_log
        }
        validation_path = reports_dir / f'PARTNERS_VALIDATION_REPORT_{timestamp}.json'
        with open(validation_path, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        reports['validation'] = str(validation_path)
        
        # Export JSON complet des partenaires
        export_data = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_partners': len(partners),
            'partners': partners
        }
        export_path = reports_dir / f'PARTNERS_EXPORT_{timestamp}.json'
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        reports['export'] = str(export_path)
        
        return reports
    
    async def run_full_pipeline(self, input_file: str) -> Dict[str, Any]:
        """Exécute le pipeline complet d'intégration"""
        print("═══════════════════════════════════════════════════════════════════════════════")
        print("              SEO BIONIC - INTÉGRATION DES PARTENAIRES")
        print("═══════════════════════════════════════════════════════════════════════════════")
        
        # Étape 1: Chargement
        print("\n[1/6] Chargement des données brutes...")
        partners = self.load_raw_data(input_file)
        print(f"      → {len(partners)} partenaires chargés")
        
        # Étape 2: Déduplication exacte
        print("\n[2/6] Déduplication exacte...")
        partners = self.deduplicate_exact(partners)
        print(f"      → {self.stats['exact_duplicates_removed']} doublons exacts retirés")
        print(f"      → {len(partners)} partenaires restants")
        
        # Étape 3: Déduplication fuzzy
        print("\n[3/6] Déduplication fuzzy (similarité)...")
        partners = self.deduplicate_fuzzy(partners)
        self.stats['total_after_dedup'] = len(partners)
        print(f"      → {self.stats['fuzzy_duplicates_removed']} doublons similaires retirés")
        print(f"      → {len(partners)} partenaires uniques")
        
        # Étape 4: Normalisation
        print("\n[4/6] Normalisation des données...")
        partners = self.normalize_partners(partners)
        print(f"      → {len(partners)} partenaires normalisés")
        
        # Étape 5: Enrichissement
        print("\n[5/6] Enrichissement e-commerce + URLs (www. ENFORCÉ)...")
        partners = self.enrich_partners(partners)
        print(f"      → {len(partners)} partenaires enrichis")
        
        # Étape 6: Insertion en base
        print("\n[6/6] Insertion en base de données...")
        db_result = await self.insert_to_database(partners)
        print(f"      → {db_result['inserted']} insérés")
        print(f"      → {db_result['rejected']} rejetés")
        print(f"      → {db_result['duplicates']} duplicats ignorés")
        
        # Génération des rapports
        print("\n[RAPPORTS] Génération des rapports...")
        reports = self.generate_reports(partners)
        for name, path in reports.items():
            print(f"      → {name}: {path}")
        
        print("\n═══════════════════════════════════════════════════════════════════════════════")
        print("                         INTÉGRATION TERMINÉE")
        print("═══════════════════════════════════════════════════════════════════════════════")
        
        return {
            'success': True,
            'statistics': dict(self.stats),
            'reports': reports,
            'db_result': db_result
        }


async def main():
    """Point d'entrée principal"""
    pipeline = PartnersIntegration()
    result = await pipeline.run_full_pipeline('/app/partners_raw.json')
    
    # Sauvegarder le résultat final
    with open('/app/docs/reports/INTEGRATION_RESULT.json', 'w', encoding='utf-8') as f:
        # Convertir les defaultdicts en dicts normaux
        result['statistics']['categories_found'] = dict(result['statistics']['categories_found'])
        result['statistics']['types_found'] = dict(result['statistics']['types_found'])
        result['statistics']['countries_found'] = dict(result['statistics']['countries_found'])
        result['statistics']['market_scope_distribution'] = dict(result['statistics']['market_scope_distribution'])
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result


if __name__ == '__main__':
    result = asyncio.run(main())
    print(f"\nRésultat final sauvegardé: /app/docs/reports/INTEGRATION_RESULT.json")
