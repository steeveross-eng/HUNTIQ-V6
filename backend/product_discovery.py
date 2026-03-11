# product_discovery.py - Système intelligent de détection et ingestion automatique de produits
import re
import uuid
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import httpx
from bs4 import BeautifulSoup
from emergentintegrations.llm.chat import LlmChat, UserMessage

# ============================================
# CONFIGURATION
# ============================================

# Sites prioritaires à scanner
PRIORITY_SOURCES = [
    {"name": "Zone Écotone", "url": "https://zone-ecotone.com", "type": "store"},
    {"name": "Sail Outdoors", "url": "https://www.sail.ca", "type": "store"},
    {"name": "Bass Pro Shops", "url": "https://www.basspro.com", "type": "store"},
    {"name": "Cabela's Canada", "url": "https://www.cabelas.ca", "type": "store"},
]

# Mots-clés de recherche pour la découverte
SEARCH_KEYWORDS = [
    "attractant chasse chevreuil",
    "leurre orignal",
    "urine cerf chasse",
    "bloc sel chevreuil",
    "appât ours chasse",
    "deer attractant hunting",
    "moose lure hunting",
    "deer urine scent",
    "mineral block deer",
    "bear bait hunting"
]

# Mots-clés à EXCLURE (armes, munitions, etc.)
EXCLUDED_KEYWORDS = [
    "fusil", "carabine", "pistolet", "munition", "balle", "cartouche",
    "rifle", "gun", "firearm", "ammunition", "bullet", "shotgun",
    "pistol", "revolver", "arme", "weapon", "ammo", "calibre", "caliber"
]

# Catégories de produits valides
VALID_CATEGORIES = {
    "attractant": ["attractant", "leurre", "appât", "bait", "lure"],
    "urine": ["urine", "urin", "scent", "estrous", "rut"],
    "mineral": ["minéral", "mineral", "sel", "salt", "bloc", "block", "lick"],
    "gel": ["gel", "gelée", "jelly", "paste", "pâte"],
    "powder": ["poudre", "powder", "additif", "additive"],
    "liquid": ["liquide", "liquid", "spray", "vaporisateur"],
    "granules": ["granules", "granulé", "pellets", "pellet"],
    "feeder": ["mangeoire", "feeder", "distributeur"]
}

# Espèces ciblées
TARGET_SPECIES = {
    "deer": ["cerf", "chevreuil", "deer", "whitetail", "buck", "doe", "biche"],
    "moose": ["orignal", "moose", "élan", "elk"],
    "bear": ["ours", "bear", "black bear", "grizzly"],
    "multi": ["multi", "all species", "toutes espèces", "universal"]
}

# ============================================
# MODÈLES PYDANTIC
# ============================================

class DiscoveredProduct(BaseModel):
    """Produit découvert par le scanner"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Informations de base
    name_fr: str
    name_en: Optional[str] = None
    brand: str = ""
    source_url: str
    source_name: str
    
    # Classification
    category: str = "attractant"
    subcategory: Optional[str] = None
    target_species: List[str] = []
    season: Optional[str] = None
    
    # Description
    description_fr: str = ""
    description_en: Optional[str] = None
    ingredients: List[str] = []
    advantages_fr: List[str] = []
    advantages_en: List[str] = []
    marketing_claims_fr: List[str] = []
    marketing_claims_en: List[str] = []
    application_mode: Optional[str] = None
    
    # Prix et formats
    formats: List[Dict[str, Any]] = []  # [{size: "500g", price: 29.99}, ...]
    price_regular: float = 0
    price_promo: Optional[float] = None
    price_with_shipping: Optional[float] = None
    price_without_shipping: Optional[float] = None
    
    # Images
    image_urls: List[str] = []
    main_image_url: Optional[str] = None
    
    # Scoring (sur 100)
    score_total: float = 0
    score_chemical_attraction: float = 0  # A: 30 pts
    score_species_relevance: float = 0    # B: 20 pts
    score_application_mode: float = 0     # C: 15 pts
    score_duration_range: float = 0       # D: 10 pts
    score_economic_value: float = 0       # E: 15 pts
    score_brand_quality: float = 0        # F: 5 pts
    score_field_data: float = 0           # G: 5 pts
    
    # Tags générés
    tags_fr: List[str] = []
    tags_en: List[str] = []
    
    # Métadonnées
    status: Literal["pending", "approved", "rejected", "active"] = "pending"
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Hash pour éviter les doublons
    content_hash: str = ""

class ScannerConfig(BaseModel):
    """Configuration du scanner"""
    id: str = "scanner_config"
    frequency: Literal["realtime", "daily", "weekly", "manual"] = "daily"
    is_running: bool = False
    last_scan: Optional[datetime] = None
    next_scan: Optional[datetime] = None
    products_found_last_scan: int = 0
    total_products_found: int = 0
    priority_sources_enabled: bool = True
    web_search_enabled: bool = True
    auto_translate: bool = True
    min_score_threshold: int = 40

class AdminNotification(BaseModel):
    """Notification pour l'administrateur"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["new_product", "scan_complete", "error", "info"] = "new_product"
    title: str
    message: str
    product_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# SERVICE DE DÉCOUVERTE
# ============================================

class ProductDiscoveryService:
    def __init__(self, api_key: str, db):
        self.api_key = api_key
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        
        # LLM pour analyse et traduction
        self.llm = LlmChat(
            api_key=api_key,
            session_id=f"discovery_{uuid.uuid4().hex[:8]}",
            system_message="""Tu es un expert en produits de chasse, spécialisé dans les attractants et leurres.
            Tu analyses les pages web et extraits les informations produits de manière structurée.
            Tu traduis entre français et anglais avec précision.
            Tu génères des scores basés sur des critères objectifs.
            Réponds toujours en JSON valide."""
        ).with_model("openai", "gpt-4.1")
    
    def _generate_content_hash(self, name: str, brand: str, source: str) -> str:
        """Génère un hash unique pour identifier les doublons"""
        content = f"{name.lower().strip()}|{brand.lower().strip()}|{source}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_excluded_product(self, text: str) -> bool:
        """Vérifie si le produit contient des mots-clés exclus"""
        text_lower = text.lower()
        for keyword in EXCLUDED_KEYWORDS:
            if keyword in text_lower:
                return True
        return False
    
    def _detect_category(self, text: str) -> str:
        """Détecte la catégorie du produit"""
        text_lower = text.lower()
        for category, keywords in VALID_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        return "attractant"
    
    def _detect_species(self, text: str) -> List[str]:
        """Détecte les espèces ciblées"""
        text_lower = text.lower()
        detected = []
        for species, keywords in TARGET_SPECIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(species)
                    break
        return list(set(detected)) or ["deer"]  # Par défaut: deer
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Récupère le contenu HTML d'une page"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await self.http_client.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None
    
    async def _analyze_product_page(self, html: str, source_url: str, source_name: str) -> Optional[DiscoveredProduct]:
        """Analyse une page produit avec l'IA"""
        try:
            # Nettoyer le HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # Supprimer les scripts et styles
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            text_content = soup.get_text(separator=' ', strip=True)[:8000]  # Limiter la taille
            
            # Vérifier si c'est un produit exclu
            if self._is_excluded_product(text_content):
                return None
            
            # Extraire les images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http') and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.append(src)
            
            # Analyse par l'IA
            prompt = f"""Analyse cette page de produit de chasse et extrais les informations en JSON:

URL: {source_url}
Contenu: {text_content[:5000]}

Réponds UNIQUEMENT avec ce JSON (sans texte autour):
{{
    "name_fr": "nom du produit en français",
    "brand": "marque",
    "description_fr": "description complète",
    "ingredients": ["liste", "des", "ingrédients"],
    "advantages_fr": ["avantage 1", "avantage 2"],
    "marketing_claims_fr": ["claim 1", "claim 2"],
    "price_regular": prix numérique ou 0,
    "formats": [{{"size": "500g", "price": 29.99}}],
    "application_mode": "mode d'application",
    "season": "saison recommandée",
    "is_hunting_product": true/false,
    "is_excluded": true/false si c'est une arme/munition
}}"""

            response = await self.llm.send_message(UserMessage(text=prompt))
            
            # Parser la réponse JSON
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            data = json.loads(json_str)
            
            # Vérifier si c'est un produit de chasse valide
            if not data.get("is_hunting_product", True) or data.get("is_excluded", False):
                return None
            
            # Créer le produit découvert
            product = DiscoveredProduct(
                name_fr=data.get("name_fr", "Produit inconnu"),
                brand=data.get("brand", ""),
                source_url=source_url,
                source_name=source_name,
                category=self._detect_category(text_content),
                target_species=self._detect_species(text_content),
                description_fr=data.get("description_fr", ""),
                ingredients=data.get("ingredients", []),
                advantages_fr=data.get("advantages_fr", []),
                marketing_claims_fr=data.get("marketing_claims_fr", []),
                price_regular=float(data.get("price_regular", 0)),
                formats=data.get("formats", []),
                application_mode=data.get("application_mode"),
                season=data.get("season"),
                image_urls=images[:5],
                main_image_url=images[0] if images else None
            )
            
            # Générer le hash
            product.content_hash = self._generate_content_hash(
                product.name_fr, product.brand, source_name
            )
            
            return product
            
        except Exception as e:
            print(f"Error analyzing product: {e}")
            return None
    
    async def translate_product(self, product: DiscoveredProduct) -> DiscoveredProduct:
        """Traduit les champs FR vers EN"""
        try:
            prompt = f"""Traduis ces informations produit du français vers l'anglais:

Nom: {product.name_fr}
Description: {product.description_fr}
Avantages: {json.dumps(product.advantages_fr, ensure_ascii=False)}
Claims marketing: {json.dumps(product.marketing_claims_fr, ensure_ascii=False)}

Réponds UNIQUEMENT avec ce JSON:
{{
    "name_en": "product name in English",
    "description_en": "description in English",
    "advantages_en": ["advantage 1", "advantage 2"],
    "marketing_claims_en": ["claim 1", "claim 2"],
    "tags_en": ["tag1", "tag2", "tag3"]
}}"""

            response = await self.llm.send_message(UserMessage(text=prompt))
            
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            data = json.loads(json_str)
            
            product.name_en = data.get("name_en", product.name_fr)
            product.description_en = data.get("description_en", product.description_fr)
            product.advantages_en = data.get("advantages_en", [])
            product.marketing_claims_en = data.get("marketing_claims_en", [])
            product.tags_en = data.get("tags_en", [])
            
            # Générer aussi les tags FR
            product.tags_fr = [
                product.category,
                *product.target_species,
                product.brand.lower() if product.brand else "",
                product.season or ""
            ]
            product.tags_fr = [t for t in product.tags_fr if t]
            
        except Exception as e:
            print(f"Translation error: {e}")
        
        return product
    
    def calculate_score(self, product: DiscoveredProduct) -> DiscoveredProduct:
        """Calcule le score sur 100 points"""
        
        # A. Attractivité chimique (30 pts)
        score_a = 0
        high_value_ingredients = ["phéromone", "urine", "estrous", "tarsal", "gland"]
        medium_value_ingredients = ["minéral", "sel", "mélasse", "pomme", "vanille", "anis"]
        
        for ing in product.ingredients:
            ing_lower = ing.lower()
            if any(hv in ing_lower for hv in high_value_ingredients):
                score_a += 6
            elif any(mv in ing_lower for mv in medium_value_ingredients):
                score_a += 3
        score_a = min(score_a, 30)
        
        # B. Pertinence espèce (20 pts)
        score_b = 0
        if product.target_species:
            if len(product.target_species) == 1:
                score_b = 20  # Produit spécialisé
            elif "multi" in product.target_species:
                score_b = 12  # Multi-espèces
            else:
                score_b = 15  # Quelques espèces ciblées
        
        # C. Mode d'application & efficacité (15 pts)
        score_c = 10  # Score par défaut
        if product.application_mode:
            mode = product.application_mode.lower()
            if "spray" in mode or "vaporis" in mode:
                score_c = 12
            elif "bloc" in mode or "lick" in mode:
                score_c = 15  # Durée prolongée
            elif "urine" in mode or "leurre" in mode:
                score_c = 14
        
        # D. Durée & portée (10 pts)
        score_d = 5  # Score par défaut
        desc = (product.description_fr or "").lower()
        if "longue durée" in desc or "long lasting" in desc.lower():
            score_d = 10
        elif "jours" in desc or "days" in desc:
            score_d = 8
        elif "semaines" in desc or "weeks" in desc:
            score_d = 10
        
        # E. Valeur économique (15 pts) - ratio perf/prix
        score_e = 8  # Score par défaut
        if product.price_regular > 0:
            # Performance estimée basée sur les autres scores
            performance = (score_a + score_b + score_c + score_d) / 75 * 100
            ratio = (performance / product.price_regular) * 3.8 * 100
            
            if ratio > 80:
                score_e = 15
            elif ratio >= 60:
                score_e = 12
            elif ratio >= 40:
                score_e = 8
            elif ratio >= 20:
                score_e = 5
            else:
                score_e = 3
        
        # F. Qualité perçue / marque (5 pts)
        score_f = 3  # Score par défaut
        premium_brands = ["bionic", "tink's", "code blue", "wildlife research"]
        if product.brand and any(pb in product.brand.lower() for pb in premium_brands):
            score_f = 5
        elif product.brand:
            score_f = 4
        
        # G. Données terrain (5 pts)
        score_g = 3  # Score par défaut (pas de données terrain disponibles)
        if product.advantages_fr and len(product.advantages_fr) >= 3:
            score_g = 4
        
        # Score total
        product.score_chemical_attraction = score_a
        product.score_species_relevance = score_b
        product.score_application_mode = score_c
        product.score_duration_range = score_d
        product.score_economic_value = score_e
        product.score_brand_quality = score_f
        product.score_field_data = score_g
        
        product.score_total = score_a + score_b + score_c + score_d + score_e + score_f + score_g
        
        return product
    
    async def check_duplicate(self, product: DiscoveredProduct) -> bool:
        """Vérifie si le produit existe déjà"""
        existing = await self.db.discovered_products.find_one({
            "content_hash": product.content_hash
        })
        return existing is not None
    
    async def save_product(self, product: DiscoveredProduct) -> str:
        """Sauvegarde un produit découvert"""
        doc = product.model_dump()
        doc['discovered_at'] = doc['discovered_at'].isoformat()
        if doc.get('approved_at'):
            doc['approved_at'] = doc['approved_at'].isoformat()
        if doc.get('rejected_at'):
            doc['rejected_at'] = doc['rejected_at'].isoformat()
        
        await self.db.discovered_products.insert_one(doc)
        return product.id
    
    async def create_notification(self, product: DiscoveredProduct) -> str:
        """Crée une notification admin pour un nouveau produit"""
        notification = AdminNotification(
            type="new_product",
            title=f"Nouveau produit détecté: {product.name_fr}",
            message=f"Score: {product.score_total}/100 | Catégorie: {product.category} | Prix: ${product.price_regular}",
            product_id=product.id
        )
        
        doc = notification.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await self.db.admin_notifications.insert_one(doc)
        return notification.id
    
    async def scan_url(self, url: str, source_name: str) -> List[DiscoveredProduct]:
        """Scanne une URL et retourne les produits trouvés"""
        products = []
        
        html = await self._fetch_page(url)
        if not html:
            return products
        
        # Analyser la page
        product = await self._analyze_product_page(html, url, source_name)
        
        if product:
            # Vérifier les doublons
            if await self.check_duplicate(product):
                return products
            
            # Traduire
            product = await self.translate_product(product)
            
            # Calculer le score
            product = self.calculate_score(product)
            
            # Sauvegarder si score suffisant
            config = await self.get_config()
            if product.score_total >= config.min_score_threshold:
                await self.save_product(product)
                await self.create_notification(product)
                products.append(product)
        
        return products
    
    async def get_config(self) -> ScannerConfig:
        """Récupère la configuration du scanner"""
        config = await self.db.scanner_config.find_one({"id": "scanner_config"}, {"_id": 0})
        if config:
            return ScannerConfig(**config)
        
        # Créer config par défaut
        default_config = ScannerConfig()
        await self.db.scanner_config.insert_one(default_config.model_dump())
        return default_config
    
    async def update_config(self, updates: Dict[str, Any]) -> ScannerConfig:
        """Met à jour la configuration du scanner"""
        await self.db.scanner_config.update_one(
            {"id": "scanner_config"},
            {"$set": updates},
            upsert=True
        )
        return await self.get_config()
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.http_client.aclose()


# ============================================
# FONCTIONS UTILITAIRES EXPORTÉES
# ============================================

def normalize_price(price_str: str) -> float:
    """Normalise une chaîne de prix en float"""
    if not price_str:
        return 0.0
    
    # Supprimer les caractères non numériques sauf . et ,
    cleaned = re.sub(r'[^\d.,]', '', str(price_str))
    
    # Gérer les formats européens (virgule décimale)
    if ',' in cleaned and '.' not in cleaned:
        cleaned = cleaned.replace(',', '.')
    elif ',' in cleaned and '.' in cleaned:
        cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except:
        return 0.0


def normalize_weight(weight_str: str) -> Dict[str, Any]:
    """Normalise une chaîne de poids/volume"""
    if not weight_str:
        return {"value": 0, "unit": "g"}
    
    weight_str = weight_str.lower().strip()
    
    # Patterns courants
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*kg', lambda m: {"value": float(m.group(1)) * 1000, "unit": "g"}),
        (r'(\d+(?:\.\d+)?)\s*g(?:r)?', lambda m: {"value": float(m.group(1)), "unit": "g"}),
        (r'(\d+(?:\.\d+)?)\s*lb', lambda m: {"value": float(m.group(1)) * 453.592, "unit": "g"}),
        (r'(\d+(?:\.\d+)?)\s*oz', lambda m: {"value": float(m.group(1)) * 28.3495, "unit": "g"}),
        (r'(\d+(?:\.\d+)?)\s*l(?:itre)?', lambda m: {"value": float(m.group(1)) * 1000, "unit": "ml"}),
        (r'(\d+(?:\.\d+)?)\s*ml', lambda m: {"value": float(m.group(1)), "unit": "ml"}),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, weight_str)
        if match:
            return converter(match)
    
    return {"value": 0, "unit": "g"}
