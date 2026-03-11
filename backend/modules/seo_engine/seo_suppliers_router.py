"""
BIONIC SEO Engine - Suppliers Router
=====================================

API pour la gestion de la LISTE FOURNISSEURS ULTIME.
Intégration SEO SUPRÊME - Chasse & Outdoors.

Endpoints:
- GET /suppliers : Liste tous les fournisseurs
- GET /suppliers/categories : Liste des catégories
- GET /suppliers/by-category/{category} : Fournisseurs par catégorie
- GET /suppliers/search : Recherche de fournisseurs
- GET /suppliers/stats : Statistiques
- GET /suppliers/export : Export format Excel

Architecture LEGO V5 - Module isolé.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from .data.suppliers.suppliers_database import (
    SUPPLIERS_DATABASE,
    SUPPLIERS_STATS,
    get_all_suppliers,
    get_suppliers_by_category,
    get_categories,
    get_suppliers_count,
    get_total_suppliers,
    search_suppliers,
    get_suppliers_by_country,
    export_to_excel_format
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bionic/seo/suppliers", tags=["SEO Suppliers Database"])


@router.get("/")
async def get_all_suppliers_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    category: Optional[str] = None,
    country: Optional[str] = None,
    priority: Optional[str] = None
):
    """
    Liste tous les fournisseurs avec filtres optionnels.
    
    Args:
        page: Numéro de page (défaut: 1)
        limit: Nombre par page (défaut: 50, max: 200)
        category: Filtrer par catégorie
        country: Filtrer par pays
        priority: Filtrer par priorité SEO (high, medium, low)
    """
    suppliers = get_all_suppliers()
    
    # Apply filters
    if category:
        suppliers = [s for s in suppliers if s["category"] == category]
    if country:
        suppliers = [s for s in suppliers if s["country"].lower() == country.lower()]
    if priority:
        suppliers = [s for s in suppliers if s.get("seo_priority") == priority]
    
    # Pagination
    total = len(suppliers)
    start = (page - 1) * limit
    end = start + limit
    paginated = suppliers[start:end]
    
    return {
        "success": True,
        "suppliers": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        },
        "filters_applied": {
            "category": category,
            "country": country,
            "priority": priority
        }
    }


@router.get("/categories")
async def get_categories_endpoint():
    """
    Liste toutes les catégories disponibles avec leur nombre de fournisseurs.
    """
    categories = get_categories()
    counts = get_suppliers_count()
    
    categories_list = []
    for cat in categories:
        categories_list.append({
            "id": cat,
            "name": cat.replace("_", " ").title(),
            "count": counts.get(cat, 0)
        })
    
    return {
        "success": True,
        "categories": categories_list,
        "total_categories": len(categories),
        "total_suppliers": get_total_suppliers()
    }


@router.get("/by-category/{category}")
async def get_by_category_endpoint(category: str):
    """
    Récupère tous les fournisseurs d'une catégorie spécifique.
    """
    suppliers = get_suppliers_by_category(category)
    
    if not suppliers:
        raise HTTPException(status_code=404, detail=f"Catégorie '{category}' non trouvée")
    
    return {
        "success": True,
        "category": category,
        "suppliers": suppliers,
        "count": len(suppliers)
    }


@router.get("/search")
async def search_suppliers_endpoint(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(20, le=100)
):
    """
    Recherche de fournisseurs par nom.
    """
    results = search_suppliers(q)[:limit]
    
    return {
        "success": True,
        "query": q,
        "results": results,
        "count": len(results)
    }


@router.get("/by-country/{country}")
async def get_by_country_endpoint(country: str):
    """
    Récupère tous les fournisseurs d'un pays spécifique.
    """
    suppliers = get_suppliers_by_country(country)
    
    return {
        "success": True,
        "country": country,
        "suppliers": suppliers,
        "count": len(suppliers)
    }


@router.get("/stats")
async def get_stats_endpoint():
    """
    Statistiques de la base de données fournisseurs.
    """
    stats = SUPPLIERS_STATS.copy()
    
    # Add country distribution
    all_suppliers = get_all_suppliers()
    countries = {}
    for s in all_suppliers:
        country = s["country"]
        countries[country] = countries.get(country, 0) + 1
    
    # Add priority distribution
    priorities = {"high": 0, "medium": 0, "low": 0}
    for s in all_suppliers:
        prio = s.get("seo_priority", "medium")
        priorities[prio] = priorities.get(prio, 0) + 1
    
    stats["by_country"] = countries
    stats["by_priority"] = priorities
    
    return {
        "success": True,
        "stats": stats
    }


@router.get("/export")
async def export_suppliers_endpoint(format: str = Query("json", enum=["json", "csv_ready"])):
    """
    Export de la base de données pour intégration externe.
    
    Args:
        format: Format d'export (json ou csv_ready pour structure tabulaire)
    """
    if format == "csv_ready":
        export = export_to_excel_format()
        return {
            "success": True,
            "format": "csv_ready",
            "data": export,
            "columns": ["Catégorie", "Compagnie", "Pays", "Lien officiel", "Livraison gratuite", "Type", "Spécialités", "Priorité SEO"],
            "count": len(export)
        }
    else:
        return {
            "success": True,
            "format": "json",
            "data": SUPPLIERS_DATABASE,
            "stats": SUPPLIERS_STATS
        }


@router.get("/seo-pages")
async def get_seo_pages_endpoint():
    """
    Génère la structure des pages SEO satellites pour chaque fournisseur.
    Structure prête pour le SEO Engine.
    """
    all_suppliers = get_all_suppliers()
    seo_pages = []
    
    for supplier in all_suppliers:
        slug = supplier["company"].lower().replace(" ", "-").replace("'", "")
        category_slug = supplier["category"].replace("_", "-")
        
        seo_page = {
            "slug": f"/fournisseurs/{category_slug}/{slug}",
            "title": f"{supplier['company']} - Fournisseur {supplier['category'].replace('_', ' ').title()}",
            "meta_description": f"Découvrez {supplier['company']}, fournisseur {supplier['type']} de {', '.join(supplier.get('specialty', [])[:2])}. {supplier['country']}.",
            "h1": supplier["company"],
            "canonical_url": supplier["official_url"],
            "category": supplier["category"],
            "country": supplier["country"],
            "free_shipping": supplier["free_shipping"],
            "seo_priority": supplier.get("seo_priority", "medium"),
            "specialties": supplier.get("specialty", []),
            "type": supplier.get("type", ""),
            "jsonld_ready": True
        }
        seo_pages.append(seo_page)
    
    return {
        "success": True,
        "seo_pages": seo_pages,
        "count": len(seo_pages),
        "ready_for_integration": True
    }


logger.info("SEO Suppliers Router initialized - LISTE FOURNISSEURS ULTIME")
