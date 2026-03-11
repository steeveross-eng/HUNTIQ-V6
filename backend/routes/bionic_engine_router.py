"""
BIONIC Next Step Engine - API Router
═══════════════════════════════════════════════════════════════════════════════
Routes API pour tous les modules du Next Step Engine:
- User Context
- Hunter Score
- Permis Checklist
- Next Steps
- Setup Builder
- Pourvoirie Finder
- Liste Épicerie
- Chasseur Jumeau
- Plan Saison
- Score Préparation
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from dataclasses import asdict

# Import des services
from modules.user_context import user_context_service, UserContextInput
from modules.hunter_score import hunter_score_service
from modules.permis_checklist import permis_checklist_service
from modules.next_step_engine import next_step_engine, ActionType
from modules.setup_builder import setup_builder_service
from modules.pourvoirie_finder import pourvoirie_finder_service
from modules.liste_epicerie import liste_epicerie_service
from modules.chasseur_jumeau import chasseur_jumeau_service
from modules.plan_saison import plan_saison_service
from modules.score_preparation import score_preparation_service

router = APIRouter(prefix="/api/bionic-engine", tags=["BIONIC Engine"])


# ═══════════════════════════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════════════════════════

class SetGibierRequest(BaseModel):
    user_id: str
    gibier: str


class UpdateContextRequest(BaseModel):
    user_id: str
    gibier: Optional[str] = None
    region: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    page_visited: Optional[str] = None
    tool_used: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    user_id: str
    permis_type: str
    item_id: str
    is_completed: bool


class SetupRequest(BaseModel):
    user_id: str
    gibier: str
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    season: str = "automne"


class PourvouirieSearchRequest(BaseModel):
    user_id: str
    gibier: str
    region: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    budget_max: Optional[float] = None


class AddToCartRequest(BaseModel):
    user_id: str
    item_id: str
    item_type: str
    quantity: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# USER CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/context/{user_id}")
async def get_user_context(user_id: str):
    """Récupère le contexte utilisateur"""
    context = await user_context_service.get_context(user_id)
    return asdict(context)


@router.post("/context/update")
async def update_user_context(request: UpdateContextRequest):
    """Met à jour le contexte utilisateur"""
    input_data = UserContextInput(**request.dict())
    context = await user_context_service.update_context(input_data)
    return asdict(context)


@router.post("/context/set-gibier")
async def set_gibier_principal(request: SetGibierRequest):
    """Définit le gibier principal (après popup)"""
    context = await user_context_service.set_gibier_principal(request.user_id, request.gibier)
    return asdict(context)


@router.get("/gibiers")
async def get_gibiers_available():
    """Retourne la liste des gibiers disponibles"""
    return user_context_service.get_gibiers_available()


@router.get("/regions")
async def get_regions():
    """Retourne la liste des régions du Québec"""
    return user_context_service.get_regions_quebec()


# ═══════════════════════════════════════════════════════════════════════════════
# HUNTER SCORE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/score/hunter/{user_id}")
async def get_hunter_score(user_id: str):
    """Calcule et retourne le score chasseur"""
    breakdown = await hunter_score_service.calculate_score(user_id)
    return asdict(breakdown)


@router.get("/score/hunter/leaderboard")
async def get_hunter_leaderboard(limit: int = Query(default=10, le=50)):
    """Retourne le classement des chasseurs"""
    return await hunter_score_service.get_leaderboard(limit)


# ═══════════════════════════════════════════════════════════════════════════════
# PERMIS CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/permis/checklist/create")
async def create_permis_checklist(user_id: str, permis_type: str, province: str = "QC"):
    """Crée une checklist pour un permis"""
    checklist = await permis_checklist_service.create_checklist(user_id, permis_type, province)
    return asdict(checklist)


@router.get("/permis/checklist/{user_id}/{permis_type}")
async def get_permis_checklist(user_id: str, permis_type: str):
    """Récupère une checklist de permis"""
    checklist = await permis_checklist_service.get_checklist(user_id, permis_type)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist non trouvée")
    return asdict(checklist)


@router.get("/permis/checklists/{user_id}")
async def get_user_checklists(user_id: str):
    """Récupère toutes les checklists d'un utilisateur"""
    checklists = await permis_checklist_service.get_user_checklists(user_id)
    return [asdict(c) for c in checklists]


@router.post("/permis/checklist/update-item")
async def update_checklist_item(request: ChecklistItemUpdate):
    """Met à jour un item de la checklist"""
    checklist = await permis_checklist_service.update_item(
        request.user_id, request.permis_type, request.item_id, request.is_completed
    )
    return asdict(checklist)


# ═══════════════════════════════════════════════════════════════════════════════
# NEXT STEP ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/next-steps/{user_id}")
async def get_next_steps(
    user_id: str, 
    action: str = Query(default="login"),
    max_steps: int = Query(default=5, le=10)
):
    """Génère les prochaines étapes recommandées"""
    try:
        action_type = ActionType(action)
    except ValueError:
        action_type = ActionType.LOGIN
    
    response = await next_step_engine.generate_next_steps(user_id, action_type, max_steps)
    return asdict(response)


@router.post("/next-steps/complete")
async def complete_step(user_id: str, step_id: str):
    """Marque un step comme complété"""
    success = await next_step_engine.mark_step_completed(user_id, step_id)
    return {"success": success, "step_id": step_id}


# ═══════════════════════════════════════════════════════════════════════════════
# SETUP BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/setup/generate")
async def generate_setup(request: SetupRequest):
    """Génère un setup personnalisé"""
    response = await setup_builder_service.generate_setup(
        request.user_id, request.gibier, request.gps_lat, request.gps_lng, request.season
    )
    return asdict(response)


@router.post("/setup/add-to-cart")
async def add_setup_item_to_cart(request: AddToCartRequest):
    """Ajoute un item du setup au panier"""
    return await setup_builder_service.add_to_cart(
        request.user_id, request.item_id, request.item_type, request.quantity
    )


# ═══════════════════════════════════════════════════════════════════════════════
# POURVOIRIE FINDER
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/pourvoiries/search")
async def search_pourvoiries(request: PourvouirieSearchRequest):
    """Recherche des pourvoiries"""
    response = await pourvoirie_finder_service.search_pourvoiries(
        request.user_id, request.gibier, request.region,
        request.gps_lat, request.gps_lng, request.budget_max
    )
    return asdict(response)


@router.get("/pourvoiries/{pourvoirie_id}")
async def get_pourvoirie_details(pourvoirie_id: str):
    """Récupère les détails d'une pourvoirie"""
    details = await pourvoirie_finder_service.get_pourvoirie_details(pourvoirie_id)
    if not details:
        raise HTTPException(status_code=404, detail="Pourvoirie non trouvée")
    return details


@router.post("/pourvoiries/book")
async def book_pourvoirie(user_id: str, pourvoirie_id: str, guests: int = 1):
    """Ajoute une réservation au panier"""
    return await pourvoirie_finder_service.book_pourvoirie(user_id, pourvoirie_id, {}, guests)


# ═══════════════════════════════════════════════════════════════════════════════
# LISTE ÉPICERIE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/liste-epicerie/{user_id}")
async def get_liste_epicerie(user_id: str, gibier: str = "orignal"):
    """Génère la liste d'épicerie personnalisée"""
    response = await liste_epicerie_service.generate_liste(user_id, gibier)
    return asdict(response)


@router.get("/liste-epicerie/catalogue")
async def get_catalogue():
    """Retourne le catalogue complet"""
    return liste_epicerie_service.get_catalogue()


@router.post("/liste-epicerie/add-to-cart")
async def add_liste_item_to_cart(request: AddToCartRequest):
    """Ajoute un item au panier"""
    return await liste_epicerie_service.add_to_cart(request.user_id, request.item_id, request.quantity)


@router.delete("/liste-epicerie/remove-from-cart")
async def remove_from_cart(user_id: str, item_id: str):
    """Retire un item du panier"""
    return await liste_epicerie_service.remove_from_cart(user_id, item_id)


@router.get("/cart/{user_id}")
async def get_cart(user_id: str):
    """Récupère le panier"""
    return await liste_epicerie_service.get_cart(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# CHASSEUR JUMEAU
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/chasseur-jumeau/{user_id}")
async def find_chasseur_jumeau(user_id: str, limit: int = Query(default=5, le=10)):
    """Trouve les profils de chasseurs similaires"""
    response = await chasseur_jumeau_service.find_similar_profiles(user_id, limit)
    return asdict(response)


@router.post("/chasseur-jumeau/add-to-cart")
async def add_recommendation_to_cart(request: AddToCartRequest):
    """Ajoute une recommandation au panier"""
    return await chasseur_jumeau_service.add_recommendation_to_cart(
        request.user_id, request.item_id, request.item_type
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN DE SAISON
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/plan-saison/{user_id}")
async def get_plan_saison(user_id: str, gibier: str = "orignal", year: Optional[int] = None):
    """Génère le plan de saison personnalisé"""
    response = await plan_saison_service.generate_plan(user_id, gibier, year)
    return asdict(response)


@router.post("/plan-saison/add-to-cart")
async def add_plan_item_to_cart(request: AddToCartRequest):
    """Ajoute un item du plan au panier"""
    return await plan_saison_service.add_plan_item_to_cart(
        request.user_id, request.item_id, request.item_type
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCORE DE PRÉPARATION
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/score/preparation/{user_id}")
async def get_preparation_score(user_id: str):
    """Calcule et retourne le score de préparation"""
    breakdown = await score_preparation_service.calculate_score(user_id)
    return asdict(breakdown)


@router.get("/score/preparation/leaderboard")
async def get_preparation_leaderboard(limit: int = Query(default=10, le=50)):
    """Retourne le classement des mieux préparés"""
    return await score_preparation_service.get_leaderboard(limit)
