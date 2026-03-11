"""
BIONIC SEO Engine - V5-ULTIME
=============================

Module SEO premium intégré au Knowledge Layer.
Architecture LEGO V5 stricte - Module isolé, autonome et testable.

Composants:
- seo_router.py: Routes API
- seo_service.py: Service principal
- seo_models.py: Modèles Pydantic
- seo_clusters.py: Gestion des clusters SEO
- seo_pages.py: Pages piliers/satellites/opportunités
- seo_jsonld.py: Schémas JSON-LD
- seo_automation.py: Automatisation SEO
- seo_analytics.py: Analytics et KPIs
- seo_generation.py: Génération IA + Knowledge Layer
- seo_normalization.py: Normalisation URLs (www. ENFORCÉ) [v1.0.0]
- seo_enrichment.py: Enrichissement e-commerce [v1.0.0]
- seo_database.py: Gestion BDD avec validation URLs [v1.0.0]
- seo_reporting.py: Génération de rapports [v1.0.0]

Version: 2.0.0
"""

from .seo_router import router
from .seo_service import SEOService
from .seo_models import (
    SEOCluster,
    SEOPage,
    SEOJsonLD,
    SEOCampaign,
    SEOAnalytics
)

# Nouveaux modules v2.0.0 - DIRECTIVE COPILOT MAÎTRE
from .seo_normalization import (
    SEONormalization,
    URLNormalizationResult,
    normalize_url,
    seo_normalizer
)
from .seo_enrichment import (
    SEOEnrichment,
    EcommerceEnrichmentResult,
    enrich_ecommerce,
    seo_enricher
)
from .seo_database import (
    SEODatabase,
    InsertionResult,
    BatchInsertionResult,
    insert,
    insert_batch,
    seo_db
)
from .seo_reporting import (
    SEOReporting,
    SEOIntegrationReport,
    seo_reporter,
    generate
)

__all__ = [
    # Core
    "router",
    "SEOService",
    "SEOCluster",
    "SEOPage",
    "SEOJsonLD",
    "SEOCampaign",
    "SEOAnalytics",
    # v2.0.0 - Normalisation URLs (www. ENFORCÉ)
    "SEONormalization",
    "URLNormalizationResult",
    "normalize_url",
    "seo_normalizer",
    # v2.0.0 - Enrichissement e-commerce
    "SEOEnrichment",
    "EcommerceEnrichmentResult",
    "enrich_ecommerce",
    "seo_enricher",
    # v2.0.0 - Gestion BDD
    "SEODatabase",
    "InsertionResult",
    "BatchInsertionResult",
    "insert",
    "insert_batch",
    "seo_db",
    # v2.0.0 - Reporting
    "SEOReporting",
    "SEOIntegrationReport",
    "seo_reporter",
    "generate"
]

__version__ = "2.0.0"
__module__ = "seo_engine"
