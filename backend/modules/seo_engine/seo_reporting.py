"""
SEO BIONIC - Module de Génération de Rapports
═══════════════════════════════════════════════════════════════════════════════
DIRECTIVE COPILOT MAÎTRE : Rapports détaillés incluant toutes les URLs
corrigées, invalides, et nécessitant une revue manuelle.
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-18
Status: VERROUILLÉ
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from .seo_normalization import URLNormalizationResult
from .seo_enrichment import EcommerceEnrichmentResult
from .seo_database import InsertionResult, BatchInsertionResult


@dataclass
class URLCorrectionReport:
    """Rapport des URLs corrigées"""
    original_url: str
    normalized_url: str
    was_http: bool = False
    had_www: bool = False
    params_cleaned: bool = False


@dataclass
class URLInvalidReport:
    """Rapport des URLs invalides"""
    url: str
    partner_name: Optional[str] = None
    error_message: str = ""
    requires_manual_review: bool = True


@dataclass
class URLRewriteReport:
    """Rapport des URLs sans www. détectées et réécrites"""
    original_url: str
    rewritten_url: str
    partner_name: Optional[str] = None


@dataclass
class ManualReviewReport:
    """Rapport des URLs nécessitant une revue manuelle"""
    url: str
    partner_name: Optional[str] = None
    reason: str = ""
    http_status: Optional[int] = None
    ssl_valid: Optional[bool] = None


@dataclass
class SEOIntegrationReport:
    """Rapport complet d'intégration SEO BIONIC"""
    report_id: str
    report_type: str = "seo_integration"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Statistiques globales
    total_partners_processed: int = 0
    total_urls_processed: int = 0
    total_urls_normalized: int = 0
    total_urls_invalid: int = 0
    total_urls_requiring_review: int = 0
    
    # Statistiques d'insertion
    total_inserted: int = 0
    total_rejected: int = 0
    total_duplicates: int = 0
    
    # Statistiques market_scope
    market_breakdown: Dict[str, int] = field(default_factory=dict)
    
    # Statistiques e-commerce
    ecommerce_detected: int = 0
    no_ecommerce: int = 0
    platforms_breakdown: Dict[str, int] = field(default_factory=dict)
    
    # Listes détaillées
    urls_corrected: List[Dict[str, Any]] = field(default_factory=list)
    urls_invalid: List[Dict[str, Any]] = field(default_factory=list)
    urls_rewritten: List[Dict[str, Any]] = field(default_factory=list)
    urls_manual_review: List[Dict[str, Any]] = field(default_factory=list)
    
    # Partenaires traités
    partners_inserted: List[Dict[str, Any]] = field(default_factory=list)
    partners_rejected: List[Dict[str, Any]] = field(default_factory=list)
    partners_duplicates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Métadonnées
    execution_time_seconds: float = 0.0
    status: str = "completed"
    errors: List[str] = field(default_factory=list)


class SEOReporting:
    """
    Module de génération de rapports SEO BIONIC
    
    Rapports générés:
    1. Liste des URLs corrigées
    2. Liste des URLs invalides
    3. Liste des URLs sans "www." détectées et réécrites
    4. Liste des URLs nécessitant une revue manuelle
    """
    
    REPORTS_DIR = "/app/docs/reports"
    
    def __init__(self):
        self._current_report: Optional[SEOIntegrationReport] = None
        self._start_time: Optional[datetime] = None
        
        # Créer le dossier de rapports si nécessaire
        Path(self.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    
    def start_report(self, report_id: str, report_type: str = "seo_integration") -> SEOIntegrationReport:
        """
        Démarre un nouveau rapport.
        
        Args:
            report_id: Identifiant unique du rapport
            report_type: Type de rapport
            
        Returns:
            Instance du rapport créé
        """
        self._start_time = datetime.now(timezone.utc)
        self._current_report = SEOIntegrationReport(
            report_id=report_id,
            report_type=report_type
        )
        return self._current_report
    
    def add_url_normalization_result(
        self, 
        result: URLNormalizationResult,
        partner_name: Optional[str] = None
    ):
        """
        Ajoute un résultat de normalisation au rapport.
        
        Args:
            result: Résultat de normalisation
            partner_name: Nom du partenaire associé
        """
        if not self._current_report:
            return
        
        self._current_report.total_urls_processed += 1
        
        if result.url_normalized and result.normalized_url:
            self._current_report.total_urls_normalized += 1
            
            # URL corrigée (changement effectué)
            if result.was_http or not result.had_www or result.params_cleaned:
                self._current_report.urls_corrected.append(asdict(URLCorrectionReport(
                    original_url=result.original_url,
                    normalized_url=result.normalized_url,
                    was_http=result.was_http,
                    had_www=result.had_www,
                    params_cleaned=result.params_cleaned
                )))
            
            # URL sans www. réécrite
            if not result.had_www:
                self._current_report.urls_rewritten.append(asdict(URLRewriteReport(
                    original_url=result.original_url,
                    rewritten_url=result.normalized_url,
                    partner_name=partner_name
                )))
        
        if result.url_invalid:
            self._current_report.total_urls_invalid += 1
            self._current_report.urls_invalid.append(asdict(URLInvalidReport(
                url=result.original_url,
                partner_name=partner_name,
                error_message=result.error_message or "URL invalide",
                requires_manual_review=True
            )))
        
        if result.requires_manual_review:
            self._current_report.total_urls_requiring_review += 1
            self._current_report.urls_manual_review.append(asdict(ManualReviewReport(
                url=result.original_url,
                partner_name=partner_name,
                reason=result.error_message or "Revue manuelle requise",
                http_status=result.http_status,
                ssl_valid=result.ssl_valid
            )))
    
    def add_enrichment_result(self, result: EcommerceEnrichmentResult):
        """
        Ajoute un résultat d'enrichissement au rapport.
        
        Args:
            result: Résultat d'enrichissement e-commerce
        """
        if not self._current_report:
            return
        
        self._current_report.total_partners_processed += 1
        
        # E-commerce stats
        if result.has_ecommerce:
            self._current_report.ecommerce_detected += 1
            
            if result.ecommerce_platform:
                platform = result.ecommerce_platform
                self._current_report.platforms_breakdown[platform] = \
                    self._current_report.platforms_breakdown.get(platform, 0) + 1
        else:
            self._current_report.no_ecommerce += 1
        
        # Market scope stats
        market = result.market_scope
        self._current_report.market_breakdown[market] = \
            self._current_report.market_breakdown.get(market, 0) + 1
        
        # URL normalization tracking
        if result.original_url:
            self._current_report.total_urls_processed += 1
            
            if result.url_normalized:
                self._current_report.total_urls_normalized += 1
            
            if result.url_invalid:
                self._current_report.total_urls_invalid += 1
                self._current_report.urls_invalid.append(asdict(URLInvalidReport(
                    url=result.original_url,
                    partner_name=result.partner_name,
                    error_message=result.error_message or "URL e-commerce invalide",
                    requires_manual_review=result.requires_manual_review
                )))
            
            if result.requires_manual_review:
                self._current_report.total_urls_requiring_review += 1
    
    def add_insertion_result(
        self, 
        result: InsertionResult,
        partner_data: Optional[Dict[str, Any]] = None
    ):
        """
        Ajoute un résultat d'insertion au rapport.
        
        Args:
            result: Résultat d'insertion
            partner_data: Données du partenaire
        """
        if not self._current_report:
            return
        
        partner_info = partner_data or result.normalized_document or {}
        
        if result.success:
            self._current_report.total_inserted += 1
            self._current_report.partners_inserted.append({
                'document_id': result.document_id,
                'name': partner_info.get('name', 'Unknown'),
                'url_normalized': result.url_normalized
            })
        elif result.rejected:
            if 'dupliqué' in (result.rejection_reason or '').lower():
                self._current_report.total_duplicates += 1
                self._current_report.partners_duplicates.append({
                    'name': partner_info.get('name', 'Unknown'),
                    'reason': result.rejection_reason
                })
            else:
                self._current_report.total_rejected += 1
                self._current_report.partners_rejected.append({
                    'name': partner_info.get('name', 'Unknown'),
                    'reason': result.rejection_reason
                })
    
    def add_batch_insertion_result(self, result: BatchInsertionResult):
        """
        Ajoute un résultat d'insertion en lot au rapport.
        
        Args:
            result: Résultat d'insertion en lot
        """
        if not self._current_report:
            return
        
        self._current_report.total_inserted += result.total_inserted
        self._current_report.total_rejected += result.total_rejected
        self._current_report.total_duplicates += result.total_duplicates
        
        for doc in result.rejected_documents:
            self._current_report.partners_rejected.append({
                'name': doc.get('document', {}).get('name', 'Unknown'),
                'reason': '; '.join(doc.get('errors', []))
            })
        
        for doc in result.duplicate_documents:
            self._current_report.partners_duplicates.append({
                'name': doc.get('name', 'Unknown'),
                'reason': 'Document dupliqué'
            })
    
    def add_error(self, error: str):
        """Ajoute une erreur au rapport"""
        if self._current_report:
            self._current_report.errors.append(error)
    
    def finalize_report(self, status: str = "completed") -> SEOIntegrationReport:
        """
        Finalise le rapport actuel.
        
        Args:
            status: Statut final du rapport
            
        Returns:
            Rapport finalisé
        """
        if not self._current_report:
            raise ValueError("Aucun rapport en cours")
        
        self._current_report.status = status
        
        if self._start_time:
            end_time = datetime.now(timezone.utc)
            self._current_report.execution_time_seconds = \
                (end_time - self._start_time).total_seconds()
        
        return self._current_report
    
    def generate(self, output_format: str = "json") -> str:
        """
        Génère le rapport dans le format spécifié.
        
        Args:
            output_format: Format de sortie ("json", "summary")
            
        Returns:
            Chemin du fichier généré ou contenu du rapport
        """
        if not self._current_report:
            raise ValueError("Aucun rapport en cours")
        
        report_dict = asdict(self._current_report)
        
        if output_format == "json":
            filename = f"{self._current_report.report_id}_{self._current_report.report_type}.json"
            filepath = os.path.join(self.REPORTS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            return filepath
        
        elif output_format == "summary":
            return self._generate_summary()
        
        else:
            raise ValueError(f"Format non supporté: {output_format}")
    
    def _generate_summary(self) -> str:
        """Génère un résumé textuel du rapport"""
        if not self._current_report:
            return "Aucun rapport disponible"
        
        r = self._current_report
        
        summary = f"""
═══════════════════════════════════════════════════════════════════════════════
              RAPPORT SEO BIONIC - {r.report_id}
═══════════════════════════════════════════════════════════════════════════════
Généré: {r.generated_at}
Statut: {r.status}
Durée: {r.execution_time_seconds:.2f} secondes

─────────────────────────────────────────────────────────────────────────────
                        STATISTIQUES GLOBALES
─────────────────────────────────────────────────────────────────────────────
  Partenaires traités:     {r.total_partners_processed}
  URLs traitées:           {r.total_urls_processed}
  URLs normalisées:        {r.total_urls_normalized}
  URLs invalides:          {r.total_urls_invalid}
  URLs revue manuelle:     {r.total_urls_requiring_review}

─────────────────────────────────────────────────────────────────────────────
                        STATISTIQUES INSERTION
─────────────────────────────────────────────────────────────────────────────
  Insérés avec succès:     {r.total_inserted}
  Rejetés:                 {r.total_rejected}
  Duplicats ignorés:       {r.total_duplicates}

─────────────────────────────────────────────────────────────────────────────
                        RÉPARTITION MARKET SCOPE
─────────────────────────────────────────────────────────────────────────────
"""
        for market, count in r.market_breakdown.items():
            summary += f"  {market.upper():20} {count}\n"
        
        summary += """
─────────────────────────────────────────────────────────────────────────────
                        STATISTIQUES E-COMMERCE
─────────────────────────────────────────────────────────────────────────────
"""
        summary += f"  E-commerce détecté:      {r.ecommerce_detected}\n"
        summary += f"  Sans e-commerce:         {r.no_ecommerce}\n"
        
        if r.platforms_breakdown:
            summary += "\n  Plateformes détectées:\n"
            for platform, count in r.platforms_breakdown.items():
                summary += f"    - {platform}: {count}\n"
        
        summary += """
─────────────────────────────────────────────────────────────────────────────
                        URLS CORRIGÉES (www. ENFORCÉ)
─────────────────────────────────────────────────────────────────────────────
"""
        summary += f"  Total URLs réécrites avec www.: {len(r.urls_rewritten)}\n"
        
        if r.urls_rewritten[:5]:
            summary += "\n  Exemples:\n"
            for url_info in r.urls_rewritten[:5]:
                summary += f"    {url_info['original_url']}\n"
                summary += f"    → {url_info['rewritten_url']}\n\n"
        
        if r.urls_invalid:
            summary += f"""
─────────────────────────────────────────────────────────────────────────────
                        URLS INVALIDES ({len(r.urls_invalid)})
─────────────────────────────────────────────────────────────────────────────
"""
            for url_info in r.urls_invalid[:10]:
                summary += f"  • {url_info['url']}\n"
                summary += f"    Erreur: {url_info['error_message']}\n"
        
        if r.urls_manual_review:
            summary += f"""
─────────────────────────────────────────────────────────────────────────────
                        REVUE MANUELLE REQUISE ({len(r.urls_manual_review)})
─────────────────────────────────────────────────────────────────────────────
"""
            for url_info in r.urls_manual_review[:10]:
                summary += f"  • {url_info['url']}\n"
                summary += f"    Raison: {url_info['reason']}\n"
        
        if r.errors:
            summary += f"""
─────────────────────────────────────────────────────────────────────────────
                        ERREURS ({len(r.errors)})
─────────────────────────────────────────────────────────────────────────────
"""
            for error in r.errors:
                summary += f"  • {error}\n"
        
        summary += """
═══════════════════════════════════════════════════════════════════════════════
                        FIN DU RAPPORT
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return summary


# Instance globale du module
seo_reporter = SEOReporting()


def generate(report_id: str = None) -> str:
    """
    Fonction utilitaire pour générer un rapport.
    Point d'entrée principal conforme à la directive COPILOT MAÎTRE.
    """
    if report_id and not seo_reporter._current_report:
        seo_reporter.start_report(report_id)
    
    return seo_reporter.generate()


# ══════════════════════════════════════════════════════════════════════════════
# MODULE VERROUILLÉ — v1.0.0
# Toute modification requiert approbation COPILOT MAÎTRE
# ══════════════════════════════════════════════════════════════════════════════
