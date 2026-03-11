"""
SEO BIONIC - Module de Normalisation des URLs
═══════════════════════════════════════════════════════════════════════════════
DIRECTIVE COPILOT MAÎTRE : Toutes les URLs doivent être normalisées au format
    https://www.[domaine]
AUCUNE exception permise.
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-18
Status: VERROUILLÉ
"""

import httpx
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import asyncio


@dataclass
class URLNormalizationResult:
    """Résultat de la normalisation d'une URL"""
    original_url: str
    normalized_url: Optional[str] = None
    url_valid: bool = True
    url_invalid: bool = False
    url_normalized: bool = False
    had_www: bool = False
    was_http: bool = False
    params_cleaned: bool = False
    ssl_valid: Optional[bool] = None
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    requires_manual_review: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SEONormalization:
    """
    Module de normalisation des URLs SEO BIONIC
    
    Règles STRICTES appliquées:
    1. Toutes les URLs doivent avoir le préfixe "www."
    2. Toutes les URLs doivent utiliser HTTPS
    3. Paramètres inutiles nettoyés (?ref=, ?utm=, etc.)
    4. Validation SSL systématique
    5. Vérification HTTP 200
    """
    
    # Paramètres à supprimer automatiquement
    PARAMS_TO_REMOVE = [
        'ref', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'msclkid', 'dclid', 'zanpid', 'mc_cid', 'mc_eid',
        'affiliate', 'partner', 'source', 'campaign', 'medium', 'term', 'content',
        '_ga', '_gl', 'trk', 'track', 'ref_', 'sid', 'sessionid'
    ]
    
    # Sous-domaines spéciaux à conserver avec www.
    SPECIAL_SUBDOMAINS = ['shop', 'store', 'boutique', 'buy', 'order', 'cart', 'checkout']
    
    def __init__(self, timeout: float = 10.0, verify_ssl: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._stats = {
            'total_processed': 0,
            'total_normalized': 0,
            'total_invalid': 0,
            'urls_without_www_corrected': 0,
            'http_to_https_converted': 0,
            'params_cleaned': 0,
            'ssl_failures': 0,
            'http_failures': 0
        }
    
    def normalize_url(self, url: str) -> URLNormalizationResult:
        """
        Normalise une URL selon les règles COPILOT MAÎTRE.
        
        Transformations appliquées:
        - http://domaine.com      → https://www.domaine.com
        - https://domaine.com     → https://www.domaine.com
        - http://www.domaine.com  → https://www.domaine.com
        - shop.domaine.com        → https://www.shop.domaine.com
        
        Args:
            url: URL originale à normaliser
            
        Returns:
            URLNormalizationResult avec tous les détails de la transformation
        """
        self._stats['total_processed'] += 1
        result = URLNormalizationResult(original_url=url)
        
        if not url or not isinstance(url, str):
            result.url_valid = False
            result.url_invalid = True
            result.error_message = "URL vide ou invalide"
            self._stats['total_invalid'] += 1
            return result
        
        # Nettoyer l'URL de base
        url = url.strip()
        
        # Ajouter le schéma si absent
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            result.url_valid = False
            result.url_invalid = True
            result.error_message = f"Erreur de parsing URL: {str(e)}"
            self._stats['total_invalid'] += 1
            return result
        
        # Vérifier si le domaine est valide
        if not parsed.netloc:
            result.url_valid = False
            result.url_invalid = True
            result.error_message = "Aucun domaine détecté"
            self._stats['total_invalid'] += 1
            return result
        
        # Étape 1: Vérifier HTTP vs HTTPS
        if parsed.scheme == 'http':
            result.was_http = True
            self._stats['http_to_https_converted'] += 1
        
        # Étape 2: Normaliser le netloc avec www.
        netloc = parsed.netloc.lower()
        
        # Retirer le port si présent pour l'analyse
        port = None
        if ':' in netloc:
            netloc_base, port = netloc.rsplit(':', 1)
        else:
            netloc_base = netloc
        
        # Vérifier si www. est déjà présent
        if netloc_base.startswith('www.'):
            result.had_www = True
            normalized_netloc = netloc_base
        else:
            # Vérifier si c'est un sous-domaine spécial
            parts = netloc_base.split('.')
            if len(parts) >= 2:
                first_part = parts[0]
                if first_part in self.SPECIAL_SUBDOMAINS:
                    # shop.domaine.com → www.shop.domaine.com
                    normalized_netloc = f"www.{netloc_base}"
                else:
                    # domaine.com → www.domaine.com
                    normalized_netloc = f"www.{netloc_base}"
            else:
                result.url_valid = False
                result.url_invalid = True
                result.error_message = "Domaine incomplet"
                self._stats['total_invalid'] += 1
                return result
            
            self._stats['urls_without_www_corrected'] += 1
        
        # Restaurer le port si présent
        if port:
            normalized_netloc = f"{normalized_netloc}:{port}"
        
        # Étape 3: Nettoyer les paramètres inutiles
        query = parsed.query
        if query:
            query_params = parse_qs(query, keep_blank_values=True)
            cleaned_params = {
                k: v for k, v in query_params.items() 
                if k.lower() not in self.PARAMS_TO_REMOVE
            }
            
            if len(cleaned_params) < len(query_params):
                result.params_cleaned = True
                self._stats['params_cleaned'] += 1
            
            # Reconstruire la query string
            if cleaned_params:
                # Aplatir les listes de valeurs
                flat_params = []
                for k, v_list in cleaned_params.items():
                    for v in v_list:
                        flat_params.append((k, v))
                cleaned_query = urlencode(flat_params)
            else:
                cleaned_query = ''
        else:
            cleaned_query = ''
        
        # Étape 4: Normaliser le path
        path = parsed.path
        if not path:
            path = '/'
        elif not path.startswith('/'):
            path = '/' + path
        
        # Construire l'URL normalisée
        normalized_parts = (
            'https',           # scheme (toujours HTTPS)
            normalized_netloc, # netloc avec www.
            path,              # path
            '',                # params (deprecated)
            cleaned_query,     # query
            ''                 # fragment (supprimé)
        )
        
        result.normalized_url = urlunparse(normalized_parts)
        result.url_normalized = True
        result.url_valid = True
        result.url_invalid = False
        
        self._stats['total_normalized'] += 1
        
        return result
    
    async def normalize_url_with_validation(self, url: str) -> URLNormalizationResult:
        """
        Normalise une URL ET effectue la validation HTTP/SSL.
        
        Args:
            url: URL originale à normaliser
            
        Returns:
            URLNormalizationResult avec validation complète
        """
        result = self.normalize_url(url)
        
        if result.url_invalid or not result.normalized_url:
            return result
        
        # Vérification HTTP 200 et SSL
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=True
            ) as client:
                response = await client.head(result.normalized_url)
                result.http_status = response.status_code
                result.ssl_valid = True
                
                if response.status_code != 200:
                    if response.status_code >= 400:
                        result.requires_manual_review = True
                        self._stats['http_failures'] += 1
                        
        except httpx.SSLError as e:
            result.ssl_valid = False
            result.error_message = f"Erreur SSL: {str(e)}"
            result.requires_manual_review = True
            self._stats['ssl_failures'] += 1
            
        except httpx.TimeoutException:
            result.error_message = "Timeout lors de la validation"
            result.requires_manual_review = True
            self._stats['http_failures'] += 1
            
        except Exception as e:
            result.error_message = f"Erreur de validation: {str(e)}"
            result.requires_manual_review = True
            self._stats['http_failures'] += 1
        
        return result
    
    async def normalize_batch(
        self, 
        urls: list[str], 
        validate: bool = False,
        max_concurrent: int = 10
    ) -> list[URLNormalizationResult]:
        """
        Normalise un lot d'URLs en parallèle.
        
        Args:
            urls: Liste des URLs à normaliser
            validate: Si True, effectue aussi la validation HTTP/SSL
            max_concurrent: Nombre max de requêtes concurrentes
            
        Returns:
            Liste des résultats de normalisation
        """
        if not validate:
            return [self.normalize_url(url) for url in urls]
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(url: str) -> URLNormalizationResult:
            async with semaphore:
                return await self.normalize_url_with_validation(url)
        
        tasks = [process_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de traitement"""
        return self._stats.copy()
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        for key in self._stats:
            self._stats[key] = 0


# Instance globale du module
seo_normalizer = SEONormalization()


def normalize_url(url: str) -> URLNormalizationResult:
    """
    Fonction utilitaire pour normaliser une URL.
    Point d'entrée principal conforme à la directive COPILOT MAÎTRE.
    
    Exemple:
        result = normalize_url("http://example.com/page?utm_source=test")
        # result.normalized_url = "https://www.example.com/page"
    """
    return seo_normalizer.normalize_url(url)


async def normalize_url_validated(url: str) -> URLNormalizationResult:
    """
    Normalise une URL avec validation HTTP/SSL.
    """
    return await seo_normalizer.normalize_url_with_validation(url)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE VERROUILLÉ — v1.0.0
# Toute modification requiert approbation COPILOT MAÎTRE
# ══════════════════════════════════════════════════════════════════════════════
