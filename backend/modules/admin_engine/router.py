"""
Admin Engine Router - V5-ULTIME Administration Premium
======================================================

Point d'entrée API pour l'administration premium.
Prefix: /api/v1/admin

Sous-routes:
- /ecommerce/* : Gestion E-Commerce (Phase 1 Migration)
- /payments/* : Gestion paiements Stripe
- /freemium/* : Gestion quotas et tiers
- /upsell/* : Gestion campagnes
- /onboarding/* : Gestion parcours
- /tutorials/* : Gestion tutoriels
- /rules/* : Gestion règles Plan Maître
- /strategy/* : Gestion stratégies
- /users/* : Gestion utilisateurs
- /logs/* : Logs système
- /settings/* : Paramètres globaux

Version: 1.1.0 - Phase 1 Migration E-Commerce
"""

from fastapi import APIRouter, Query, Body
from typing import Optional, List, Any
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# Services modulaires
from .services.payments_admin import PaymentsAdminService
from .services.freemium_admin import FreemiumAdminService
from .services.upsell_admin import UpsellAdminService
from .services.onboarding_admin import OnboardingAdminService
from .services.tutorials_admin import TutorialsAdminService
from .services.rules_admin import RulesAdminService
from .services.strategy_admin import StrategyAdminService
from .services.users_admin import UsersAdminService
from .services.logs_admin import LogsAdminService
from .services.settings_admin import SettingsAdminService
# Phase 1 Migration - E-Commerce
from .services.ecommerce_admin import EcommerceAdminService
# Phase 2 Migration - Content & Backup
from .services.content_admin import ContentAdminService
from .services.backup_admin import BackupAdminService
# Phase 3 Migration - Infrastructure + Contacts
from .services.maintenance_admin import MaintenanceAdminService
from .services.contacts_admin import ContactsAdminService
# Phase 4 Migration - Hotspots & Networking
from .services.hotspots_admin import HotspotsAdminService
from .services.networking_admin import NetworkingAdminService
# Phase 5 Migration - Email & Marketing
from .services.email_admin import EmailAdminService
from .services.marketing_admin import MarketingAdminService
# Phase 6 Migration - Partners & Branding
from .services.partners_admin import PartnersAdminService
from .services.branding_admin import BrandingAdminService
# Marketing Controls (Global ON/OFF)
from .services.marketing_controls import MarketingControlsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Engine - Premium"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# ADMIN AUTHENTICATION DEPENDENCY
# ==============================================

async def verify_admin_role(authorization: str = None):
    """Vérifie que l'utilisateur a le rôle admin"""
    # Note: En production, implémenter vérification JWT complète
    # Pour l'instant, vérification basique
    if not authorization:
        # Mode développement - permettre l'accès
        return {"role": "admin", "user_id": "admin_dev"}
    
    # Vérification JWT à implémenter
    return {"role": "admin", "user_id": "admin_user"}

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def admin_engine_info():
    """Information sur le module Admin Engine"""
    return {
        "module": "admin_engine",
        "version": "1.6.0",
        "description": "Administration Premium V5-ULTIME - Phase 6 Migration",
        "access": "admin_only",
        "sub_modules": [
            "ecommerce", "content", "backup", "maintenance", "contacts",
            "hotspots", "networking", "email", "marketing", "partners", "branding",
            "payments", "freemium", "upsell", "onboarding",
            "tutorials", "rules", "strategy", "users", "logs", "settings"
        ],
        "features": [
            "Gestion E-Commerce (dashboard, sales, products, suppliers, customers, commissions, performance)",
            "Gestion Contenu (categories, SEO, content depot)",
            "Gestion Backups (code, prompts, database)",
            "Gestion Maintenance (mode maintenance, access control, scheduled maintenance)",
            "Gestion Contacts (fournisseurs, fabricants, partenaires, formateurs, experts)",
            "Gestion Hotspots/Terres (annonces, propriétaires, locataires, ententes, tarification)",
            "Gestion Networking (publications, groupes, leads, parrainages, portefeuilles)",
            "Gestion Email (templates, variables, tests, historique)",
            "Gestion Marketing (campagnes, génération IA, publications sociales, segmentation, automations)",
            "Gestion Partenaires (demandes, partenaires officiels, types, conversion, emails)",
            "Gestion Branding (logos, couleurs, documents, assets de marque)",
            "Gestion paiements Stripe",
            "Gestion quotas freemium",
            "Gestion campagnes upsell",
            "Gestion parcours onboarding",
            "Gestion tutoriels",
            "Gestion règles Plan Maître",
            "Gestion stratégies",
            "Gestion utilisateurs",
            "Logs système",
            "Paramètres globaux"
        ]
    }

@router.get("/dashboard")
async def admin_dashboard():
    """Dashboard principal avec KPIs"""
    db = get_db()
    
    # Compter les documents
    users_count = await db.users.count_documents({})
    subscriptions_count = await db.subscriptions.count_documents({})
    premium_count = await db.subscriptions.count_documents({"tier": {"$in": ["premium", "pro"]}})
    transactions_count = await db.payment_transactions.count_documents({})
    
    # Revenus (transactions payées)
    paid_transactions = await db.payment_transactions.find(
        {"payment_status": "paid"},
        {"amount": 1}
    ).to_list(length=1000)
    total_revenue = sum(t.get("amount", 0) for t in paid_transactions)
    
    # KPIs onboarding
    completed_onboarding = await db.onboarding_status.count_documents({"completed": True})
    
    # KPIs upsell
    upsell_impressions = await db.upsell_impressions.count_documents({})
    upsell_clicks = await db.upsell_clicks.count_documents({})
    
    return {
        "success": True,
        "dashboard": {
            "users": {
                "total": users_count,
                "with_subscription": subscriptions_count,
                "premium": premium_count,
                "free": subscriptions_count - premium_count
            },
            "revenue": {
                "total": round(total_revenue, 2),
                "currency": "CAD",
                "transactions": transactions_count
            },
            "onboarding": {
                "completed": completed_onboarding,
                "completion_rate": round((completed_onboarding / max(users_count, 1)) * 100, 1)
            },
            "upsell": {
                "impressions": upsell_impressions,
                "clicks": upsell_clicks,
                "ctr": round((upsell_clicks / max(upsell_impressions, 1)) * 100, 2)
            }
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

# ==============================================
# PAYMENTS ADMIN
# ==============================================

@router.get("/payments/transactions")
async def get_all_transactions(
    limit: int = Query(50, le=500),
    status: Optional[str] = None,
    skip: int = 0
):
    """Liste toutes les transactions"""
    return await PaymentsAdminService.get_transactions(get_db(), limit, status, skip)

@router.get("/payments/transactions/{transaction_id}")
async def get_transaction_detail(transaction_id: str):
    """Détail d'une transaction"""
    return await PaymentsAdminService.get_transaction_detail(get_db(), transaction_id)

@router.get("/payments/revenue")
async def get_revenue_stats(days: int = Query(30, le=365)):
    """Statistiques de revenus"""
    return await PaymentsAdminService.get_revenue_stats(get_db(), days)

@router.get("/payments/subscriptions")
async def get_all_subscriptions(
    tier: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste tous les abonnements"""
    return await PaymentsAdminService.get_subscriptions(get_db(), tier, limit)

# ==============================================
# FREEMIUM ADMIN
# ==============================================

@router.get("/freemium/quotas")
async def get_quota_overview():
    """Vue d'ensemble des quotas"""
    return await FreemiumAdminService.get_quota_overview(get_db())

@router.get("/freemium/users/{user_id}")
async def get_user_freemium_status(user_id: str):
    """Statut freemium d'un utilisateur"""
    return await FreemiumAdminService.get_user_status(get_db(), user_id)

@router.put("/freemium/users/{user_id}/override")
async def override_user_limits(user_id: str, overrides: dict):
    """Override les limites d'un utilisateur"""
    return await FreemiumAdminService.set_user_override(get_db(), user_id, overrides)

@router.get("/freemium/tiers/stats")
async def get_tier_distribution():
    """Distribution des utilisateurs par tier"""
    return await FreemiumAdminService.get_tier_distribution(get_db())

# ==============================================
# UPSELL ADMIN
# ==============================================

@router.get("/upsell/campaigns")
async def get_upsell_campaigns():
    """Liste des campagnes upsell"""
    return await UpsellAdminService.get_campaigns(get_db())

@router.put("/upsell/campaigns/{campaign_name}/toggle")
async def toggle_campaign(campaign_name: str, enabled: bool):
    """Activer/désactiver une campagne"""
    return await UpsellAdminService.toggle_campaign(get_db(), campaign_name, enabled)

@router.get("/upsell/analytics")
async def get_upsell_analytics(days: int = Query(30, le=90)):
    """Analytics des campagnes"""
    return await UpsellAdminService.get_analytics(get_db(), days)

@router.get("/upsell/conversions")
async def get_conversion_funnel():
    """Funnel de conversion"""
    return await UpsellAdminService.get_conversion_funnel(get_db())

# ==============================================
# ONBOARDING ADMIN
# ==============================================

@router.get("/onboarding/stats")
async def get_onboarding_stats():
    """Statistiques d'onboarding"""
    return await OnboardingAdminService.get_stats(get_db())

@router.get("/onboarding/flows")
async def get_onboarding_flows():
    """Configuration des flows"""
    return await OnboardingAdminService.get_flows(get_db())

@router.get("/onboarding/users")
async def get_users_onboarding_status(
    completed: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Liste des utilisateurs et leur statut onboarding"""
    return await OnboardingAdminService.get_users_status(get_db(), completed, limit)

# ==============================================
# TUTORIALS ADMIN
# ==============================================

@router.get("/tutorials/list")
async def get_all_tutorials():
    """Liste tous les tutoriels"""
    return await TutorialsAdminService.get_tutorials(get_db())

@router.put("/tutorials/{tutorial_id}/toggle")
async def toggle_tutorial(tutorial_id: str, enabled: bool):
    """Activer/désactiver un tutoriel"""
    return await TutorialsAdminService.toggle_tutorial(get_db(), tutorial_id, enabled)

@router.get("/tutorials/progress")
async def get_tutorials_progress():
    """Progression globale des tutoriels"""
    return await TutorialsAdminService.get_progress_stats(get_db())

# ==============================================
# RULES ADMIN
# ==============================================

@router.get("/rules/list")
async def get_all_rules():
    """Liste toutes les règles"""
    return await RulesAdminService.get_rules(get_db())

@router.put("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, enabled: bool):
    """Activer/désactiver une règle"""
    return await RulesAdminService.toggle_rule(get_db(), rule_id, enabled)

@router.put("/rules/{rule_id}/weight")
async def update_rule_weight(rule_id: str, weight: float):
    """Modifier le poids d'une règle"""
    return await RulesAdminService.update_weight(get_db(), rule_id, weight)

@router.get("/rules/stats")
async def get_rules_stats():
    """Statistiques des règles"""
    return await RulesAdminService.get_stats(get_db())

# ==============================================
# STRATEGY ADMIN
# ==============================================

@router.get("/strategy/generated")
async def get_generated_strategies(
    limit: int = Query(50, le=500),
    user_id: Optional[str] = None
):
    """Liste les stratégies générées"""
    return await StrategyAdminService.get_strategies(get_db(), limit, user_id)

@router.get("/strategy/logs")
async def get_strategy_logs(limit: int = Query(100, le=1000)):
    """Logs de génération"""
    return await StrategyAdminService.get_logs(get_db(), limit)

@router.get("/strategy/diagnostics")
async def get_strategy_diagnostics():
    """Diagnostics du moteur"""
    return await StrategyAdminService.get_diagnostics(get_db())

# ==============================================
# USERS ADMIN
# ==============================================

@router.get("/users/list")
async def get_all_users(
    limit: int = Query(50, le=500),
    role: Optional[str] = None,
    tier: Optional[str] = None
):
    """Liste tous les utilisateurs"""
    return await UsersAdminService.get_users(get_db(), limit, role, tier)

@router.get("/users/{user_id}")
async def get_user_detail(user_id: str):
    """Détail d'un utilisateur"""
    return await UsersAdminService.get_user_detail(get_db(), user_id)

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str):
    """Modifier le rôle d'un utilisateur"""
    return await UsersAdminService.update_role(get_db(), user_id, role)

@router.get("/users/{user_id}/activity")
async def get_user_activity(user_id: str, days: int = Query(30, le=90)):
    """Historique d'activité"""
    return await UsersAdminService.get_activity(get_db(), user_id, days)

# ==============================================
# LOGS ADMIN
# ==============================================

@router.get("/logs/errors")
async def get_error_logs(
    limit: int = Query(100, le=1000),
    severity: Optional[str] = None
):
    """Logs d'erreurs"""
    return await LogsAdminService.get_errors(get_db(), limit, severity)

@router.get("/logs/webhooks")
async def get_webhook_logs(limit: int = Query(100, le=500)):
    """Logs webhooks"""
    return await LogsAdminService.get_webhooks(get_db(), limit)

@router.get("/logs/events")
async def get_event_logs(
    limit: int = Query(100, le=1000),
    event_type: Optional[str] = None
):
    """Logs d'événements"""
    return await LogsAdminService.get_events(get_db(), limit, event_type)

# ==============================================
# SETTINGS ADMIN
# ==============================================

@router.get("/settings")
async def get_all_settings():
    """Récupérer tous les paramètres"""
    return await SettingsAdminService.get_settings(get_db())

@router.put("/settings/{key}")
async def update_setting(key: str, value: Any):
    """Modifier un paramètre"""
    return await SettingsAdminService.update_setting(get_db(), key, value)

@router.get("/settings/api-keys")
async def get_api_keys_status():
    """Statut des clés API (masquées)"""
    return await SettingsAdminService.get_api_keys_status(get_db())

@router.get("/settings/toggles")
async def get_feature_toggles():
    """Toggles de fonctionnalités"""
    return await SettingsAdminService.get_toggles(get_db())

@router.put("/settings/toggles/{toggle_id}")
async def update_toggle(toggle_id: str, enabled: bool):
    """Modifier un toggle"""
    return await SettingsAdminService.update_toggle(get_db(), toggle_id, enabled)


# ==============================================
# E-COMMERCE ADMIN (Phase 1 Migration)
# ==============================================

@router.get("/ecommerce/dashboard")
async def get_ecommerce_dashboard():
    """Dashboard E-Commerce avec stats globales"""
    return await EcommerceAdminService.get_dashboard_stats(get_db())

@router.get("/ecommerce/orders")
async def get_ecommerce_orders(
    limit: int = Query(50, le=500),
    status: Optional[str] = None,
    skip: int = 0
):
    """Liste des commandes"""
    return await EcommerceAdminService.get_orders(get_db(), limit, status, skip)

@router.put("/ecommerce/orders/{order_id}/status")
async def update_ecommerce_order_status(order_id: str, status: str):
    """Mettre à jour le statut d'une commande"""
    return await EcommerceAdminService.update_order_status(get_db(), order_id, status)

@router.get("/ecommerce/products")
async def get_ecommerce_products(
    limit: int = Query(50, le=500),
    category: Optional[str] = None
):
    """Liste des produits"""
    return await EcommerceAdminService.get_products(get_db(), limit, category)

@router.post("/ecommerce/products")
async def create_ecommerce_product(product_data: dict = Body(...)):
    """Créer un nouveau produit"""
    return await EcommerceAdminService.create_product(get_db(), product_data)

@router.put("/ecommerce/products/{product_id}")
async def update_ecommerce_product(product_id: str, updates: dict = Body(...)):
    """Mettre à jour un produit"""
    return await EcommerceAdminService.update_product(get_db(), product_id, updates)

@router.delete("/ecommerce/products/{product_id}")
async def delete_ecommerce_product(product_id: str):
    """Supprimer un produit"""
    return await EcommerceAdminService.delete_product(get_db(), product_id)

@router.get("/ecommerce/suppliers")
async def get_ecommerce_suppliers(
    limit: int = Query(50, le=500),
    partnership_type: Optional[str] = None
):
    """Liste des fournisseurs"""
    return await EcommerceAdminService.get_suppliers(get_db(), limit, partnership_type)

@router.post("/ecommerce/suppliers")
async def create_ecommerce_supplier(supplier_data: dict = Body(...)):
    """Créer un nouveau fournisseur"""
    return await EcommerceAdminService.create_supplier(get_db(), supplier_data)

@router.get("/ecommerce/customers")
async def get_ecommerce_customers(
    limit: int = Query(50, le=500),
    sort_by: str = Query("total_spent")
):
    """Liste des clients"""
    return await EcommerceAdminService.get_customers(get_db(), limit, sort_by)

@router.get("/ecommerce/commissions")
async def get_ecommerce_commissions(
    limit: int = Query(50, le=500),
    status: Optional[str] = None
):
    """Liste des commissions"""
    return await EcommerceAdminService.get_commissions(get_db(), limit, status)

@router.put("/ecommerce/commissions/{commission_id}/status")
async def update_ecommerce_commission_status(commission_id: str, status: str):
    """Mettre à jour le statut d'une commission"""
    return await EcommerceAdminService.update_commission_status(get_db(), commission_id, status)

@router.get("/ecommerce/performance")
async def get_ecommerce_performance():
    """Rapport de performance des produits"""
    return await EcommerceAdminService.get_performance_report(get_db())

@router.get("/ecommerce/alerts")
async def get_ecommerce_alerts(
    limit: int = Query(20, le=100),
    unread_only: bool = False
):
    """Liste des alertes admin"""
    return await EcommerceAdminService.get_alerts(get_db(), limit, unread_only)


# ==============================================
# CONTENT ADMIN (Phase 2 Migration)
# ==============================================

@router.get("/content/categories")
async def get_content_categories():
    """Liste toutes les catégories"""
    return await ContentAdminService.get_categories(get_db())

@router.post("/content/categories")
async def create_content_category(category_data: dict = Body(...)):
    """Créer une nouvelle catégorie"""
    return await ContentAdminService.create_category(get_db(), category_data)

@router.put("/content/categories/{category_id}")
async def update_content_category(category_id: str, updates: dict = Body(...)):
    """Mettre à jour une catégorie"""
    return await ContentAdminService.update_category(get_db(), category_id, updates)

@router.delete("/content/categories/{category_id}")
async def delete_content_category(category_id: str):
    """Supprimer une catégorie"""
    return await ContentAdminService.delete_category(get_db(), category_id)

@router.post("/content/categories/init-defaults")
async def init_default_categories():
    """Initialiser les catégories par défaut"""
    return await ContentAdminService.init_default_categories(get_db())

@router.get("/content/depot")
async def get_content_depot_items(
    status: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste les items du Content Depot"""
    return await ContentAdminService.get_content_items(get_db(), status, limit)

@router.post("/content/depot")
async def create_content_depot_item(item_data: dict = Body(...)):
    """Créer un nouvel item de contenu"""
    return await ContentAdminService.create_content_item(get_db(), item_data)

@router.put("/content/depot/{item_id}")
async def update_content_depot_item(item_id: str, updates: dict = Body(...)):
    """Mettre à jour un item de contenu"""
    return await ContentAdminService.update_content_item(get_db(), item_id, updates)

@router.put("/content/depot/{item_id}/status")
async def update_content_depot_status(item_id: str, status: str):
    """Mettre à jour le statut d'un item"""
    return await ContentAdminService.update_content_status(get_db(), item_id, status)

@router.delete("/content/depot/{item_id}")
async def delete_content_depot_item(item_id: str):
    """Supprimer un item de contenu"""
    return await ContentAdminService.delete_content_item(get_db(), item_id)

@router.get("/content/seo-analytics")
async def get_seo_analytics():
    """Statistiques SEO globales"""
    return await ContentAdminService.get_seo_analytics(get_db())

# ==============================================
# BACKUP ADMIN (Phase 2 Migration)
# ==============================================

@router.get("/backup/stats")
async def get_backup_stats():
    """Statistiques globales des backups"""
    return await BackupAdminService.get_backup_stats(get_db())

@router.get("/backup/code/files")
async def get_backup_code_files(
    search: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste les fichiers de code suivis"""
    return await BackupAdminService.get_code_files(get_db(), search, limit)

@router.get("/backup/code/files/{file_path:path}/versions")
async def get_backup_file_versions(file_path: str, limit: int = Query(20, le=100)):
    """Récupérer les versions d'un fichier"""
    return await BackupAdminService.get_file_versions(get_db(), file_path, limit)

@router.post("/backup/code/files")
async def create_code_backup(
    file_path: str,
    content: str = Body(...),
    commit_message: str = ""
):
    """Créer une nouvelle version d'un fichier"""
    return await BackupAdminService.create_code_backup(get_db(), file_path, content, commit_message)

@router.get("/backup/code/restore/{file_path:path}/{version}")
async def restore_code_version(file_path: str, version: int):
    """Restaurer une version spécifique"""
    return await BackupAdminService.restore_version(get_db(), file_path, version)

@router.get("/backup/prompts")
async def get_backup_prompt_versions(
    prompt_type: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste les versions de prompts"""
    return await BackupAdminService.get_prompt_versions(get_db(), prompt_type, limit)

@router.get("/backup/prompts/{version_id}")
async def get_backup_prompt_version_detail(version_id: str):
    """Détail d'une version de prompt"""
    return await BackupAdminService.get_prompt_version_detail(get_db(), version_id)

@router.post("/backup/prompts")
async def save_prompt_version(
    prompt_type: str,
    content: str = Body(...),
    metadata: dict = Body(default={})
):
    """Sauvegarder une nouvelle version de prompt"""
    return await BackupAdminService.save_prompt_version(get_db(), prompt_type, content, metadata)

@router.get("/backup/database")
async def get_database_backups(limit: int = Query(20, le=100)):
    """Liste les backups de base de données"""
    return await BackupAdminService.get_db_backups(get_db(), limit)

@router.post("/backup/database")
async def create_database_backup(
    backup_type: str = "manual",
    description: str = ""
):
    """Créer un backup de base de données"""
    return await BackupAdminService.create_db_backup(get_db(), backup_type, description)

@router.delete("/backup/database/{backup_id}")
async def delete_database_backup(backup_id: str):
    """Supprimer un backup"""
    return await BackupAdminService.delete_db_backup(get_db(), backup_id)



# ==============================================
# MAINTENANCE ADMIN (Phase 3 Migration)
# ==============================================

@router.get("/maintenance/status")
async def get_maintenance_status():
    """Récupérer le statut de maintenance actuel"""
    return await MaintenanceAdminService.get_maintenance_status(get_db())

@router.put("/maintenance/toggle")
async def toggle_maintenance_mode(
    enabled: bool,
    message: str = None,
    estimated_end: str = None
):
    """Activer/Désactiver le mode maintenance"""
    return await MaintenanceAdminService.toggle_maintenance_mode(get_db(), enabled, message, estimated_end)

@router.put("/maintenance/config")
async def update_maintenance_config(config_updates: dict = Body(...)):
    """Mettre à jour la configuration de maintenance"""
    return await MaintenanceAdminService.update_maintenance_config(get_db(), config_updates)

@router.get("/maintenance/access-rules")
async def get_access_rules():
    """Récupérer les règles d'accès"""
    return await MaintenanceAdminService.get_access_rules(get_db())

@router.post("/maintenance/access-rules")
async def create_access_rule(rule_data: dict = Body(...)):
    """Créer une nouvelle règle d'accès"""
    return await MaintenanceAdminService.create_access_rule(get_db(), rule_data)

@router.put("/maintenance/access-rules/{rule_id}")
async def update_access_rule(rule_id: str, updates: dict = Body(...)):
    """Mettre à jour une règle d'accès"""
    return await MaintenanceAdminService.update_access_rule(get_db(), rule_id, updates)

@router.delete("/maintenance/access-rules/{rule_id}")
async def delete_access_rule(rule_id: str):
    """Supprimer une règle d'accès"""
    return await MaintenanceAdminService.delete_access_rule(get_db(), rule_id)

@router.put("/maintenance/access-rules/{rule_id}/toggle")
async def toggle_access_rule(rule_id: str, enabled: bool):
    """Activer/Désactiver une règle d'accès"""
    return await MaintenanceAdminService.toggle_access_rule(get_db(), rule_id, enabled)

@router.get("/maintenance/allowed-ips")
async def get_allowed_ips():
    """Récupérer les IPs autorisées en mode maintenance"""
    return await MaintenanceAdminService.get_allowed_ips(get_db())

@router.post("/maintenance/allowed-ips")
async def add_allowed_ip(ip: str, label: str = ""):
    """Ajouter une IP autorisée"""
    return await MaintenanceAdminService.add_allowed_ip(get_db(), ip, label)

@router.delete("/maintenance/allowed-ips/{ip}")
async def remove_allowed_ip(ip: str):
    """Retirer une IP autorisée"""
    return await MaintenanceAdminService.remove_allowed_ip(get_db(), ip)

@router.get("/maintenance/logs")
async def get_maintenance_logs(limit: int = Query(50, le=500)):
    """Récupérer les logs de maintenance"""
    return await MaintenanceAdminService.get_maintenance_logs(get_db(), limit)

@router.get("/maintenance/scheduled")
async def get_scheduled_maintenances():
    """Récupérer les maintenances planifiées"""
    return await MaintenanceAdminService.get_scheduled_maintenances(get_db())

@router.post("/maintenance/scheduled")
async def create_scheduled_maintenance(schedule_data: dict = Body(...)):
    """Créer une maintenance planifiée"""
    return await MaintenanceAdminService.create_scheduled_maintenance(get_db(), schedule_data)

@router.delete("/maintenance/scheduled/{schedule_id}")
async def delete_scheduled_maintenance(schedule_id: str):
    """Supprimer une maintenance planifiée"""
    return await MaintenanceAdminService.delete_scheduled_maintenance(get_db(), schedule_id)

@router.get("/maintenance/system-status")
async def get_system_status():
    """Récupérer le statut système global"""
    return await MaintenanceAdminService.get_system_status(get_db())


# ==============================================
# CONTACTS ADMIN (Directory - Source de vérité V5)
# ==============================================

@router.get("/contacts")
async def get_contacts(
    entity_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste les contacts avec filtres"""
    return await ContactsAdminService.get_contacts(get_db(), entity_type, status, search, limit)

@router.get("/contacts/stats")
async def get_contacts_stats():
    """Statistiques globales des contacts"""
    return await ContactsAdminService.get_contacts_stats(get_db())

@router.get("/contacts/tags")
async def get_all_tags():
    """Récupérer tous les tags utilisés"""
    return await ContactsAdminService.get_all_tags(get_db())

# Shortcuts pour types spécifiques - MUST be before {contact_id} route
@router.get("/contacts/suppliers")
async def get_suppliers(limit: int = Query(50, le=500)):
    """Liste les fournisseurs"""
    return await ContactsAdminService.get_suppliers(get_db(), limit)

@router.get("/contacts/manufacturers")
async def get_manufacturers(limit: int = Query(50, le=500)):
    """Liste les fabricants"""
    return await ContactsAdminService.get_manufacturers(get_db(), limit)

@router.get("/contacts/partners")
async def get_partners(limit: int = Query(50, le=500)):
    """Liste les partenaires"""
    return await ContactsAdminService.get_partners(get_db(), limit)

@router.get("/contacts/trainers")
async def get_trainers(limit: int = Query(50, le=500)):
    """Liste les formateurs"""
    return await ContactsAdminService.get_trainers(get_db(), limit)

@router.get("/contacts/experts")
async def get_experts(limit: int = Query(50, le=500)):
    """Liste les experts"""
    return await ContactsAdminService.get_experts(get_db(), limit)

@router.put("/contacts/bulk/status")
async def bulk_update_status(contact_ids: List[str] = Body(...), new_status: str = Body(...)):
    """Mettre à jour le statut de plusieurs contacts"""
    return await ContactsAdminService.bulk_update_status(get_db(), contact_ids, new_status)

@router.delete("/contacts/bulk/delete")
async def bulk_delete_contacts(contact_ids: List[str] = Body(...)):
    """Supprimer plusieurs contacts"""
    return await ContactsAdminService.bulk_delete(get_db(), contact_ids)

@router.get("/contacts/export/all")
async def export_contacts(entity_type: Optional[str] = None):
    """Exporter les contacts"""
    return await ContactsAdminService.export_contacts(get_db(), entity_type)

@router.post("/contacts/import")
async def import_contacts(contacts_data: List[dict] = Body(...)):
    """Importer des contacts"""
    return await ContactsAdminService.import_contacts(get_db(), contacts_data)

# Generic contact routes - MUST be after specific routes
@router.get("/contacts/{contact_id}")
async def get_contact_by_id(contact_id: str):
    """Récupérer un contact par ID"""
    return await ContactsAdminService.get_contact_by_id(get_db(), contact_id)

@router.post("/contacts")
async def create_contact(contact_data: dict = Body(...)):
    """Créer un nouveau contact"""
    return await ContactsAdminService.create_contact(get_db(), contact_data)

@router.put("/contacts/{contact_id}")
async def update_contact(contact_id: str, updates: dict = Body(...)):
    """Mettre à jour un contact"""
    return await ContactsAdminService.update_contact(get_db(), contact_id, updates)

@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    """Supprimer un contact"""
    return await ContactsAdminService.delete_contact(get_db(), contact_id)

@router.post("/contacts/{contact_id}/tags")
async def add_tag_to_contact(contact_id: str, tag: str):
    """Ajouter un tag à un contact"""
    return await ContactsAdminService.add_tag_to_contact(get_db(), contact_id, tag)

@router.delete("/contacts/{contact_id}/tags/{tag}")
async def remove_tag_from_contact(contact_id: str, tag: str):
    """Retirer un tag d'un contact"""
    return await ContactsAdminService.remove_tag_from_contact(get_db(), contact_id, tag)


# ==============================================
# HOTSPOTS ADMIN (Phase 4 Migration - Terres)
# ==============================================

@router.get("/hotspots/dashboard")
async def get_hotspots_dashboard():
    """Dashboard des terres/hotspots"""
    return await HotspotsAdminService.get_dashboard_stats(get_db())

@router.get("/hotspots/listings")
async def get_hotspots_listings(
    status: Optional[str] = None,
    region: Optional[str] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Liste des annonces de terres"""
    return await HotspotsAdminService.get_listings(get_db(), status, region, is_featured, limit)

@router.get("/hotspots/listings/{listing_id}")
async def get_hotspots_listing_detail(listing_id: str):
    """Détail d'une annonce"""
    return await HotspotsAdminService.get_listing_detail(get_db(), listing_id)

@router.put("/hotspots/listings/{listing_id}/status")
async def update_hotspots_listing_status(listing_id: str, new_status: str):
    """Mettre à jour le statut d'une annonce"""
    return await HotspotsAdminService.update_listing_status(get_db(), listing_id, new_status)

@router.put("/hotspots/listings/{listing_id}/featured")
async def toggle_hotspots_listing_featured(listing_id: str, is_featured: bool):
    """Mettre en vedette une annonce"""
    return await HotspotsAdminService.toggle_featured(get_db(), listing_id, is_featured)

@router.delete("/hotspots/listings/{listing_id}")
async def delete_hotspots_listing(listing_id: str):
    """Supprimer une annonce"""
    return await HotspotsAdminService.delete_listing(get_db(), listing_id)

@router.get("/hotspots/owners")
async def get_hotspots_owners(limit: int = Query(50, le=500)):
    """Liste des propriétaires"""
    return await HotspotsAdminService.get_owners(get_db(), limit)

@router.get("/hotspots/owners/{owner_id}")
async def get_hotspots_owner_detail(owner_id: str):
    """Détail d'un propriétaire"""
    return await HotspotsAdminService.get_owner_detail(get_db(), owner_id)

@router.get("/hotspots/renters")
async def get_hotspots_renters(
    subscription_tier: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des locataires (chasseurs)"""
    return await HotspotsAdminService.get_renters(get_db(), subscription_tier, limit)

@router.get("/hotspots/agreements")
async def get_hotspots_agreements(
    status: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des ententes de location"""
    return await HotspotsAdminService.get_agreements(get_db(), status, limit)

@router.get("/hotspots/agreements/{agreement_id}")
async def get_hotspots_agreement_detail(agreement_id: str):
    """Détail d'une entente"""
    return await HotspotsAdminService.get_agreement_detail(get_db(), agreement_id)

@router.get("/hotspots/pricing")
async def get_hotspots_pricing():
    """Récupérer la tarification"""
    return await HotspotsAdminService.get_pricing(get_db())

@router.put("/hotspots/pricing")
async def update_hotspots_pricing(updates: dict = Body(...)):
    """Mettre à jour la tarification"""
    return await HotspotsAdminService.update_pricing(get_db(), updates)

@router.get("/hotspots/regions")
async def get_hotspots_regions():
    """Statistiques par région"""
    return await HotspotsAdminService.get_regions_stats(get_db())

@router.get("/hotspots/purchases")
async def get_hotspots_purchases(
    status: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des achats/transactions"""
    return await HotspotsAdminService.get_purchases(get_db(), status, limit)


# ==============================================
# NETWORKING ADMIN (Phase 4 Migration - Réseau)
# ==============================================

@router.get("/networking/dashboard")
async def get_networking_dashboard():
    """Dashboard du réseau social"""
    return await NetworkingAdminService.get_dashboard_stats(get_db())

@router.get("/networking/posts")
async def get_networking_posts(
    visibility: Optional[str] = None,
    content_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Liste des publications"""
    return await NetworkingAdminService.get_posts(get_db(), visibility, content_type, is_featured, limit)

@router.put("/networking/posts/{post_id}/featured")
async def toggle_networking_post_featured(post_id: str, is_featured: bool):
    """Mettre en vedette une publication"""
    return await NetworkingAdminService.toggle_post_featured(get_db(), post_id, is_featured)

@router.put("/networking/posts/{post_id}/pinned")
async def toggle_networking_post_pinned(post_id: str, is_pinned: bool):
    """Épingler une publication"""
    return await NetworkingAdminService.toggle_post_pinned(get_db(), post_id, is_pinned)

@router.delete("/networking/posts/{post_id}")
async def delete_networking_post(post_id: str):
    """Supprimer une publication"""
    return await NetworkingAdminService.delete_post(get_db(), post_id)

@router.get("/networking/groups")
async def get_networking_groups(
    privacy: Optional[str] = None,
    group_type: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des groupes"""
    return await NetworkingAdminService.get_groups(get_db(), privacy, group_type, limit)

@router.get("/networking/groups/{group_id}")
async def get_networking_group_detail(group_id: str):
    """Détail d'un groupe"""
    return await NetworkingAdminService.get_group_detail(get_db(), group_id)

@router.put("/networking/groups/{group_id}/active")
async def toggle_networking_group_active(group_id: str, is_active: bool):
    """Activer/désactiver un groupe"""
    return await NetworkingAdminService.toggle_group_active(get_db(), group_id, is_active)

@router.delete("/networking/groups/{group_id}")
async def delete_networking_group(group_id: str):
    """Supprimer un groupe"""
    return await NetworkingAdminService.delete_group(get_db(), group_id)

@router.get("/networking/leads")
async def get_networking_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des leads/prospects"""
    return await NetworkingAdminService.get_all_leads(get_db(), status, source, limit)

@router.get("/networking/referrals")
async def get_networking_referrals(
    status: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des parrainages"""
    return await NetworkingAdminService.get_referrals(get_db(), status, limit)

@router.get("/networking/referrals/pending")
async def get_networking_pending_referrals():
    """Parrainages en attente de validation"""
    return await NetworkingAdminService.get_pending_referrals(get_db())

@router.post("/networking/referrals/{referral_id}/verify")
async def verify_networking_referral(referral_id: str):
    """Vérifier et récompenser un parrainage"""
    return await NetworkingAdminService.verify_referral(get_db(), referral_id)

@router.post("/networking/referrals/{referral_id}/reject")
async def reject_networking_referral(referral_id: str, reason: str = ""):
    """Rejeter un parrainage"""
    return await NetworkingAdminService.reject_referral(get_db(), referral_id, reason)

@router.get("/networking/wallets")
async def get_networking_wallets(limit: int = Query(50, le=500)):
    """Liste des portefeuilles"""
    return await NetworkingAdminService.get_wallets(get_db(), limit)

@router.get("/networking/wallets/{wallet_id}")
async def get_networking_wallet_detail(wallet_id: str):
    """Détail d'un portefeuille"""
    return await NetworkingAdminService.get_wallet_detail(get_db(), wallet_id)

@router.post("/networking/wallets/{user_id}/adjust")
async def adjust_networking_wallet(
    user_id: str,
    amount: float,
    reason: str,
    adjustment_type: str = "manual"
):
    """Ajuster le solde d'un portefeuille"""
    return await NetworkingAdminService.adjust_wallet_balance(get_db(), user_id, amount, reason, adjustment_type)

@router.get("/networking/referral-codes")
async def get_networking_referral_codes(
    is_active: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Liste des codes de parrainage"""
    return await NetworkingAdminService.get_referral_codes(get_db(), is_active, limit)

@router.put("/networking/referral-codes/{code}/toggle")
async def toggle_networking_referral_code(code: str, is_active: bool):
    """Activer/désactiver un code de parrainage"""
    return await NetworkingAdminService.toggle_referral_code(get_db(), code, is_active)



# ==============================================
# EMAIL ADMIN (Phase 5 Migration - Communication)
# ==============================================

@router.get("/email/dashboard")
async def get_email_dashboard():
    """Dashboard email - statistiques"""
    return await EmailAdminService.get_dashboard_stats(get_db())

@router.get("/email/templates")
async def get_email_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Liste des templates email"""
    return await EmailAdminService.get_templates(get_db(), category, is_active)

@router.get("/email/templates/{template_id}")
async def get_email_template_detail(template_id: str):
    """Détail d'un template"""
    return await EmailAdminService.get_template_detail(get_db(), template_id)

@router.post("/email/templates")
async def create_email_template(template_data: dict = Body(...)):
    """Créer un nouveau template"""
    return await EmailAdminService.create_template(get_db(), template_data)

@router.put("/email/templates/{template_id}")
async def update_email_template(template_id: str, updates: dict = Body(...)):
    """Mettre à jour un template"""
    return await EmailAdminService.update_template(get_db(), template_id, updates)

@router.delete("/email/templates/{template_id}")
async def delete_email_template(template_id: str):
    """Supprimer un template"""
    return await EmailAdminService.delete_template(get_db(), template_id)

@router.put("/email/templates/{template_id}/toggle")
async def toggle_email_template(template_id: str, is_active: bool):
    """Activer/désactiver un template"""
    return await EmailAdminService.toggle_template_active(get_db(), template_id, is_active)

@router.get("/email/variables")
async def get_email_variables():
    """Liste des variables disponibles"""
    return await EmailAdminService.get_variables(get_db())

@router.get("/email/logs")
async def get_email_logs(
    status: Optional[str] = None,
    template_id: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Historique des emails envoyés"""
    return await EmailAdminService.get_email_logs(get_db(), status, template_id, limit)

@router.post("/email/test")
async def send_test_email(
    template_id: str,
    recipient_email: str,
    test_variables: dict = Body(default={})
):
    """Envoyer un email de test"""
    return await EmailAdminService.send_test_email(get_db(), template_id, recipient_email, test_variables)

@router.get("/email/config")
async def get_email_config():
    """Récupérer la configuration email"""
    return await EmailAdminService.get_config(get_db())

@router.put("/email/config")
async def update_email_config(updates: dict = Body(...)):
    """Mettre à jour la configuration email"""
    return await EmailAdminService.update_config(get_db(), updates)


# ==============================================
# MARKETING ADMIN (Phase 5 Migration - Communication)
# ==============================================

@router.get("/marketing/dashboard")
async def get_marketing_dashboard():
    """Dashboard marketing - statistiques"""
    return await MarketingAdminService.get_dashboard_stats(get_db())

@router.get("/marketing/campaigns")
async def get_marketing_campaigns(
    status: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des campagnes marketing"""
    return await MarketingAdminService.get_campaigns(get_db(), status, limit)

@router.get("/marketing/campaigns/{campaign_id}")
async def get_marketing_campaign_detail(campaign_id: str):
    """Détail d'une campagne"""
    return await MarketingAdminService.get_campaign_detail(get_db(), campaign_id)

@router.post("/marketing/campaigns")
async def create_marketing_campaign(campaign_data: dict = Body(...)):
    """Créer une nouvelle campagne"""
    return await MarketingAdminService.create_campaign(get_db(), campaign_data)

@router.put("/marketing/campaigns/{campaign_id}")
async def update_marketing_campaign(campaign_id: str, updates: dict = Body(...)):
    """Mettre à jour une campagne"""
    return await MarketingAdminService.update_campaign(get_db(), campaign_id, updates)

@router.put("/marketing/campaigns/{campaign_id}/status")
async def update_marketing_campaign_status(campaign_id: str, status: str):
    """Changer le statut d'une campagne"""
    return await MarketingAdminService.update_campaign_status(get_db(), campaign_id, status)

@router.delete("/marketing/campaigns/{campaign_id}")
async def delete_marketing_campaign(campaign_id: str):
    """Supprimer une campagne"""
    return await MarketingAdminService.delete_campaign(get_db(), campaign_id)

@router.get("/marketing/posts")
async def get_marketing_posts(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des publications marketing"""
    return await MarketingAdminService.get_posts(get_db(), status, platform, limit)

@router.get("/marketing/posts/scheduled")
async def get_marketing_scheduled_posts(limit: int = Query(50, le=500)):
    """Publications programmées"""
    return await MarketingAdminService.get_scheduled_posts(get_db(), limit)

@router.post("/marketing/posts")
async def create_marketing_post(post_data: dict = Body(...)):
    """Créer une publication"""
    return await MarketingAdminService.create_post(get_db(), post_data)

@router.put("/marketing/posts/{post_id}/schedule")
async def schedule_marketing_post(post_id: str, scheduled_at: str):
    """Programmer une publication"""
    return await MarketingAdminService.schedule_post(get_db(), post_id, scheduled_at)

@router.post("/marketing/posts/{post_id}/publish")
async def publish_marketing_post(post_id: str):
    """Publier immédiatement"""
    return await MarketingAdminService.publish_post(get_db(), post_id)

@router.delete("/marketing/posts/{post_id}")
async def delete_marketing_post(post_id: str):
    """Supprimer une publication"""
    return await MarketingAdminService.delete_post(get_db(), post_id)

@router.post("/marketing/generate")
async def generate_marketing_content(params: dict = Body(...)):
    """Générer du contenu marketing avec IA"""
    return await MarketingAdminService.generate_content(get_db(), params)

@router.get("/marketing/segments")
async def get_marketing_segments(limit: int = Query(50, le=500)):
    """Liste des segments d'audience"""
    return await MarketingAdminService.get_segments(get_db(), limit)

@router.post("/marketing/segments")
async def create_marketing_segment(segment_data: dict = Body(...)):
    """Créer un segment d'audience"""
    return await MarketingAdminService.create_segment(get_db(), segment_data)

@router.get("/marketing/automations")
async def get_marketing_automations(
    is_active: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Liste des automations marketing"""
    return await MarketingAdminService.get_automations(get_db(), is_active, limit)

@router.put("/marketing/automations/{automation_id}/toggle")
async def toggle_marketing_automation(automation_id: str, is_active: bool):
    """Activer/désactiver une automation"""
    return await MarketingAdminService.toggle_automation(get_db(), automation_id, is_active)

@router.get("/marketing/content-types")
async def get_marketing_content_types():
    """Types de contenu disponibles"""
    return await MarketingAdminService.get_content_types(get_db())

@router.get("/marketing/platforms")
async def get_marketing_platforms():
    """Plateformes sociales disponibles"""
    return await MarketingAdminService.get_platforms(get_db())

@router.get("/marketing/history")
async def get_marketing_history(
    platform: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Historique des publications"""
    return await MarketingAdminService.get_publish_history(get_db(), platform, limit)


# ==============================================
# PARTNERS ADMIN (Phase 6 Migration - Partenaires)
# ==============================================

@router.get("/partners/dashboard")
async def get_partners_dashboard():
    """Dashboard partenaires - statistiques"""
    return await PartnersAdminService.get_dashboard_stats(get_db())

@router.get("/partners/types")
async def get_partner_types():
    """Liste des types de partenaires"""
    return await PartnersAdminService.get_partner_types(get_db())

@router.get("/partners/requests")
async def get_partner_requests(
    status: Optional[str] = None,
    partner_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des demandes de partenariat"""
    return await PartnersAdminService.get_requests(get_db(), status, partner_type, search, limit)

@router.get("/partners/requests/{request_id}")
async def get_partner_request_detail(request_id: str):
    """Détail d'une demande"""
    return await PartnersAdminService.get_request_detail(get_db(), request_id)

@router.put("/partners/requests/{request_id}/status")
async def update_partner_request_status(request_id: str, status: str, admin_notes: str = None):
    """Mettre à jour le statut d'une demande"""
    return await PartnersAdminService.update_request_status(get_db(), request_id, status, admin_notes)

@router.post("/partners/requests/{request_id}/convert")
async def convert_request_to_partner(request_id: str):
    """Convertir une demande en partenaire officiel"""
    return await PartnersAdminService.convert_to_partner(get_db(), request_id)

@router.get("/partners/list")
async def get_partners_list(
    partner_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """Liste des partenaires officiels"""
    return await PartnersAdminService.get_partners(get_db(), partner_type, is_active, search, limit)

@router.get("/partners/{partner_id}")
async def get_partner_detail(partner_id: str):
    """Détail d'un partenaire"""
    return await PartnersAdminService.get_partner_detail(get_db(), partner_id)

@router.put("/partners/{partner_id}")
async def update_partner(partner_id: str, updates: dict = Body(...)):
    """Mettre à jour un partenaire"""
    return await PartnersAdminService.update_partner(get_db(), partner_id, updates)

@router.put("/partners/{partner_id}/toggle")
async def toggle_partner_status(partner_id: str):
    """Activer/désactiver un partenaire"""
    return await PartnersAdminService.toggle_partner_status(get_db(), partner_id)

@router.put("/partners/{partner_id}/verify")
async def verify_partner(partner_id: str, verified: bool):
    """Vérifier/dévérifier un partenaire"""
    return await PartnersAdminService.verify_partner(get_db(), partner_id, verified)

@router.put("/partners/{partner_id}/commission")
async def update_partner_commission(partner_id: str, rate: float):
    """Mettre à jour le taux de commission"""
    return await PartnersAdminService.update_commission_rate(get_db(), partner_id, rate)

@router.get("/partners/email/settings")
async def get_partner_email_settings():
    """Récupérer les paramètres email partenaires"""
    return await PartnersAdminService.get_email_settings(get_db())

@router.put("/partners/email/toggle/{setting_type}")
async def toggle_partner_email_setting(setting_type: str):
    """Activer/désactiver un type d'email partenaire"""
    return await PartnersAdminService.toggle_email_setting(get_db(), setting_type)


# ==============================================
# BRANDING ADMIN (Phase 6 Migration - Identité visuelle)
# ==============================================

@router.get("/branding/dashboard")
async def get_branding_dashboard():
    """Dashboard branding - statistiques"""
    return await BrandingAdminService.get_dashboard_stats(get_db())

@router.get("/branding/config")
async def get_brand_config():
    """Configuration de la marque"""
    return await BrandingAdminService.get_brand_config(get_db())

@router.get("/branding/logos")
async def get_brand_logos():
    """Liste des logos"""
    return await BrandingAdminService.get_logos(get_db())

@router.get("/branding/logos/{logo_id}")
async def get_brand_logo_detail(logo_id: str):
    """Détail d'un logo"""
    return await BrandingAdminService.get_logo_detail(get_db(), logo_id)

@router.post("/branding/logos")
async def add_custom_logo(
    filename: str,
    url: str,
    language: str,
    logo_type: str,
    file_size: int = 0
):
    """Ajouter un logo personnalisé"""
    return await BrandingAdminService.add_custom_logo(get_db(), filename, url, language, logo_type, file_size)

@router.delete("/branding/logos/{logo_id}")
async def delete_brand_logo(logo_id: str):
    """Supprimer un logo personnalisé"""
    return await BrandingAdminService.delete_logo(get_db(), logo_id)

@router.get("/branding/colors")
async def get_brand_colors():
    """Récupérer les couleurs de la marque"""
    return await BrandingAdminService.get_colors(get_db())

@router.put("/branding/colors/{color_key}")
async def update_brand_color(color_key: str, hex_value: str, name: str = None):
    """Mettre à jour une couleur"""
    return await BrandingAdminService.update_color(get_db(), color_key, hex_value, name)

@router.post("/branding/colors/reset")
async def reset_brand_colors():
    """Réinitialiser les couleurs par défaut"""
    return await BrandingAdminService.reset_colors(get_db())

@router.get("/branding/document-types")
async def get_document_types():
    """Types de documents disponibles"""
    return await BrandingAdminService.get_document_types(get_db())

@router.post("/branding/documents/log")
async def log_document_generation(
    template_type: str,
    language: str,
    title: str = None,
    recipient: str = None
):
    """Logger une génération de document"""
    return await BrandingAdminService.log_document_generation(get_db(), template_type, language, title, recipient)

@router.get("/branding/documents/history")
async def get_document_history(limit: int = Query(50, le=500)):
    """Historique des documents générés"""
    return await BrandingAdminService.get_document_history(get_db(), limit)

@router.get("/branding/uploads/history")
async def get_upload_history(limit: int = Query(50, le=500)):
    """Historique des uploads de logos"""
    return await BrandingAdminService.get_upload_history(get_db(), limit)

@router.get("/branding/assets")
async def get_brand_assets():
    """Récupérer tous les assets de la marque"""
    return await BrandingAdminService.get_brand_assets(get_db())


# ==============================================
# MARKETING CONTROLS (Global ON/OFF)
# ==============================================

@router.get("/marketing-controls")
async def get_marketing_controls():
    """Récupérer tous les contrôles marketing"""
    return await MarketingControlsService.get_all_controls(get_db())

@router.post("/marketing-controls/{control_id}/toggle")
async def toggle_marketing_control(control_id: str, enabled: bool = Body(...)):
    """Activer/désactiver un contrôle marketing"""
    return await MarketingControlsService.toggle_control(get_db(), control_id, enabled)

@router.post("/marketing-controls/bulk-toggle")
async def bulk_toggle_controls(control_ids: List[str] = Body(...), enabled: bool = Body(...)):
    """Activer/désactiver plusieurs contrôles en batch"""
    return await MarketingControlsService.bulk_toggle(get_db(), control_ids, enabled)

@router.get("/marketing-controls/{control_id}")
async def get_control_status(control_id: str):
    """Récupérer le statut d'un contrôle spécifique"""
    return await MarketingControlsService.get_control_status(get_db(), control_id)

@router.post("/marketing-controls/reset")
async def reset_marketing_controls():
    """Réinitialiser tous les contrôles aux valeurs par défaut"""
    return await MarketingControlsService.reset_to_defaults(get_db())

@router.get("/marketing-controls/active/features")
async def get_active_marketing_features():
    """Récupérer la liste des fonctionnalités marketing actives"""
    return await MarketingControlsService.get_active_features(get_db())
