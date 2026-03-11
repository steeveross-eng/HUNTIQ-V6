"""
SEO BIONIC - Module d'Enrichissement E-commerce
═══════════════════════════════════════════════════════════════════════════════
DIRECTIVE COPILOT MAÎTRE : Enrichissement des données partenaires avec URLs
e-commerce normalisées (www. ENFORCÉ).
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-18
Status: VERROUILLÉ
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

from .seo_normalization import seo_normalizer


@dataclass
class EcommerceEnrichmentResult:
    """Résultat de l'enrichissement e-commerce d'un partenaire"""
    partner_name: str
    original_url: Optional[str] = None
    ecommerce_url: Optional[str] = None
    has_ecommerce: bool = False
    no_ecommerce: bool = True
    ecommerce_platform: Optional[str] = None
    url_normalized: bool = False
    url_invalid: bool = False
    market_scope: str = "unknown"
    enrichment_source: str = "auto"
    requires_manual_review: bool = False
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SEOEnrichment:
    """
    Module d'enrichissement e-commerce SEO BIONIC
    
    Fonctionnalités:
    1. Détection automatique des boutiques en ligne
    2. Normalisation des URLs e-commerce (www. ENFORCÉ)
    3. Identification de la plateforme e-commerce
    4. Détermination du market_scope (pays/zone)
    """
    
    # Plateformes e-commerce connues
    ECOMMERCE_PLATFORMS = {
        'shopify': ['myshopify.com', 'shopify.com'],
        'bigcommerce': ['mybigcommerce.com', 'bigcommerce.com'],
        'woocommerce': ['woocommerce.com'],
        'magento': ['magento.com'],
        'squarespace': ['squarespace.com'],
        'wix': ['wixsite.com', 'wix.com'],
        'etsy': ['etsy.com'],
        'amazon': ['amazon.com', 'amazon.ca', 'amazon.fr', 'amazon.de', 'amazon.co.uk'],
        'ebay': ['ebay.com', 'ebay.ca', 'ebay.fr'],
        'walmart': ['walmart.com', 'walmart.ca']
    }
    
    # Indicateurs de page e-commerce
    ECOMMERCE_PATH_INDICATORS = [
        '/shop', '/store', '/boutique', '/products', '/product',
        '/cart', '/checkout', '/buy', '/order', '/catalog',
        '/collections', '/collection', '/categories', '/category',
        '/add-to-cart', '/panier', '/acheter', '/commande'
    ]
    
    # Sous-domaines e-commerce
    ECOMMERCE_SUBDOMAINS = ['shop', 'store', 'boutique', 'buy', 'order', 'cart', 'ecommerce']
    
    # Mapping TLD vers market_scope
    TLD_MARKET_MAPPING = {
        '.ca': 'canada',
        '.com': 'usa',  # Par défaut, peut être multi
        '.us': 'usa',
        '.fr': 'eu',
        '.de': 'eu',
        '.uk': 'eu',
        '.co.uk': 'eu',
        '.eu': 'eu',
        '.it': 'eu',
        '.es': 'eu',
        '.nl': 'eu',
        '.be': 'eu',
        '.ch': 'eu',
        '.at': 'eu',
        '.mx': 'international',
        '.br': 'international',
        '.au': 'international',
        '.jp': 'international',
        '.cn': 'international'
    }
    
    # Mots-clés pour détection du market_scope
    MARKET_KEYWORDS = {
        'canada': ['canada', 'canadian', 'canadien', 'québec', 'quebec', 'ontario', 'montreal', 'toronto', 'vancouver', 'calgary'],
        'usa': ['usa', 'united states', 'american', 'america', 'us-based'],
        'eu': ['europe', 'european', 'eu', 'france', 'germany', 'uk', 'britain'],
        'international': ['international', 'worldwide', 'global', 'multi-country']
    }
    
    def __init__(self):
        self._stats = {
            'total_processed': 0,
            'ecommerce_detected': 0,
            'no_ecommerce': 0,
            'platform_identified': 0,
            'urls_normalized': 0,
            'urls_invalid': 0,
            'market_canada': 0,
            'market_usa': 0,
            'market_eu': 0,
            'market_international': 0,
            'market_multi': 0,
            'market_unknown': 0
        }
    
    def enrich_ecommerce(
        self, 
        partner_name: str,
        url: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> EcommerceEnrichmentResult:
        """
        Enrichit les données d'un partenaire avec les informations e-commerce.
        
        RÈGLE COPILOT MAÎTRE:
        - ecommerce_url doit être normalisé en: https://www.[domaine]/[chemin]
        - Si sous-domaine (shop.domaine.com): https://www.shop.domaine.com
        - Si domaine externe (Shopify, etc.): https://www.[domaine_externe]
        
        Args:
            partner_name: Nom du partenaire
            url: URL principale du partenaire (optionnel)
            additional_info: Informations supplémentaires (catégorie, pays, etc.)
            
        Returns:
            EcommerceEnrichmentResult avec données enrichies
        """
        self._stats['total_processed'] += 1
        
        result = EcommerceEnrichmentResult(partner_name=partner_name)
        additional_info = additional_info or {}
        
        if not url:
            result.no_ecommerce = True
            result.has_ecommerce = False
            self._stats['no_ecommerce'] += 1
            return result
        
        result.original_url = url
        
        # Étape 1: Normaliser l'URL principale
        norm_result = seo_normalizer.normalize_url(url)
        
        if norm_result.url_invalid:
            result.url_invalid = True
            result.no_ecommerce = True
            result.has_ecommerce = False
            result.error_message = norm_result.error_message
            result.requires_manual_review = True
            self._stats['urls_invalid'] += 1
            return result
        
        normalized_url = norm_result.normalized_url
        result.url_normalized = True
        self._stats['urls_normalized'] += 1
        
        # Étape 2: Détecter si c'est une plateforme e-commerce
        platform = self._detect_platform(normalized_url)
        if platform:
            result.ecommerce_platform = platform
            result.has_ecommerce = True
            result.no_ecommerce = False
            result.ecommerce_url = normalized_url
            self._stats['platform_identified'] += 1
            self._stats['ecommerce_detected'] += 1
        
        # Étape 3: Détecter via les indicateurs de chemin
        if not result.has_ecommerce:
            if self._has_ecommerce_path(normalized_url):
                result.has_ecommerce = True
                result.no_ecommerce = False
                result.ecommerce_url = normalized_url
                self._stats['ecommerce_detected'] += 1
        
        # Étape 4: Détecter via sous-domaine e-commerce
        if not result.has_ecommerce:
            if self._has_ecommerce_subdomain(normalized_url):
                result.has_ecommerce = True
                result.no_ecommerce = False
                result.ecommerce_url = normalized_url
                self._stats['ecommerce_detected'] += 1
        
        # Étape 5: Si pas de e-commerce détecté, garder l'URL normalisée
        if not result.has_ecommerce:
            result.no_ecommerce = True
            self._stats['no_ecommerce'] += 1
        
        # Étape 6: Déterminer le market_scope
        result.market_scope = self._determine_market_scope(
            normalized_url,
            partner_name,
            additional_info
        )
        self._stats[f'market_{result.market_scope}'] += 1
        
        return result
    
    def _detect_platform(self, url: str) -> Optional[str]:
        """Détecte la plateforme e-commerce depuis l'URL"""
        url_lower = url.lower()
        
        for platform, domains in self.ECOMMERCE_PLATFORMS.items():
            for domain in domains:
                if domain in url_lower:
                    return platform
        
        return None
    
    def _has_ecommerce_path(self, url: str) -> bool:
        """Vérifie si l'URL contient un chemin e-commerce"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            for indicator in self.ECOMMERCE_PATH_INDICATORS:
                if indicator in path:
                    return True
            
            return False
        except Exception:
            return False
    
    def _has_ecommerce_subdomain(self, url: str) -> bool:
        """Vérifie si l'URL utilise un sous-domaine e-commerce"""
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            
            # Retirer www. pour l'analyse
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            parts = netloc.split('.')
            if len(parts) >= 3:  # sous-domaine.domaine.tld
                subdomain = parts[0]
                if subdomain in self.ECOMMERCE_SUBDOMAINS:
                    return True
            
            return False
        except Exception:
            return False
    
    def _determine_market_scope(
        self, 
        url: str, 
        partner_name: str,
        additional_info: Dict[str, Any]
    ) -> str:
        """
        Détermine le market_scope d'un partenaire.
        
        Returns:
            "canada", "usa", "eu", "international", "multi", ou "unknown"
        """
        # Priorité 1: Information explicite
        if 'country' in additional_info:
            country = additional_info['country'].lower()
            if country in ['canada', 'ca']:
                return 'canada'
            elif country in ['usa', 'us', 'united states', 'états-unis']:
                return 'usa'
            elif country in ['france', 'germany', 'uk', 'italy', 'spain']:
                return 'eu'
        
        if 'market_scope' in additional_info:
            scope = additional_info['market_scope'].lower()
            if scope in ['canada', 'usa', 'eu', 'international', 'multi']:
                return scope
        
        # Priorité 2: TLD de l'URL
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            
            for tld, market in self.TLD_MARKET_MAPPING.items():
                if netloc.endswith(tld):
                    return market
        except Exception:
            pass
        
        # Priorité 3: Mots-clés dans le nom ou les infos
        combined_text = f"{partner_name} {additional_info.get('description', '')}".lower()
        
        for market, keywords in self.MARKET_KEYWORDS.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return market
        
        # Par défaut
        return 'unknown'
    
    def enrich_batch(
        self,
        partners: List[Dict[str, Any]]
    ) -> List[EcommerceEnrichmentResult]:
        """
        Enrichit un lot de partenaires.
        
        Args:
            partners: Liste de dicts avec au minimum 'name' et optionnellement 'url', etc.
            
        Returns:
            Liste des résultats d'enrichissement
        """
        results = []
        
        for partner in partners:
            result = self.enrich_ecommerce(
                partner_name=partner.get('name', 'Unknown'),
                url=partner.get('url'),
                additional_info=partner
            )
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'enrichissement"""
        return self._stats.copy()
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        for key in self._stats:
            self._stats[key] = 0


# Instance globale du module
seo_enricher = SEOEnrichment()


def enrich_ecommerce(
    partner_name: str,
    url: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> EcommerceEnrichmentResult:
    """
    Fonction utilitaire pour enrichir un partenaire.
    Point d'entrée principal conforme à la directive COPILOT MAÎTRE.
    """
    return seo_enricher.enrich_ecommerce(partner_name, url, additional_info)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE VERROUILLÉ — v1.0.0
# Toute modification requiert approbation COPILOT MAÎTRE
# ══════════════════════════════════════════════════════════════════════════════
