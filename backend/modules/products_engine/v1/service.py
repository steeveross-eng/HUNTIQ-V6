"""Products Engine Service - PHASE 7 EXTRACTION
Business logic extracted from server.py.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient

from .models import Product, ProductCreate, ProductUpdate, ProductSearchRequest


class ProductsService:
    """Service for product operations"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def collection(self):
        return self.db.products
    
    # ===========================================
    # CRUD OPERATIONS
    # ===========================================
    
    async def get_all(
        self,
        category: Optional[str] = None,
        animal_type: Optional[str] = None,
        season: Optional[str] = None,
        sale_mode: Optional[str] = None,
        limit: int = 100
    ) -> List[Product]:
        """Get all products with optional filters"""
        query = {}
        if category:
            query["category"] = category
        if animal_type:
            query["animal_type"] = animal_type
        if season:
            query["season"] = season
        if sale_mode:
            query["sale_mode"] = sale_mode
        
        products = list(self.collection.find(query, {"_id": 0}).sort("rank", 1).limit(limit))
        
        for product in products:
            if isinstance(product.get('created_at'), str):
                product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return [Product(**p) for p in products]
    
    async def get_top(self, limit: int = 5) -> List[Product]:
        """Get top products by rank"""
        products = list(self.collection.find({}, {"_id": 0}).sort("rank", 1).limit(limit))
        
        for product in products:
            if isinstance(product.get('created_at'), str):
                product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return [Product(**p) for p in products]
    
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID and increment views"""
        product = self.collection.find_one({"id": product_id}, {"_id": 0})
        if not product:
            return None
        
        # Increment views
        self.collection.update_one({"id": product_id}, {"$inc": {"views": 1}})
        
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return Product(**product)
    
    async def create(self, product_input: ProductCreate) -> Product:
        """Create a new product"""
        product_dict = product_input.model_dump()
        product_obj = Product(**product_dict)
        
        doc = product_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        self.collection.insert_one(doc)
        return product_obj
    
    async def update(self, product_id: str, update_data: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return await self.get_by_id(product_id)
        
        self.collection.update_one({"id": product_id}, {"$set": update_dict})
        return await self.get_by_id(product_id)
    
    async def delete(self, product_id: str) -> bool:
        """Delete a product"""
        result = self.collection.delete_one({"id": product_id})
        return result.deleted_count > 0
    
    # ===========================================
    # FILTER OPTIONS
    # ===========================================
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """Get all available filter options based on existing products"""
        products = list(self.collection.find({}, {"_id": 0}).limit(1000))
        
        formats = set()
        brands = set()
        scents = set()
        animals = set()
        seasons = set()
        price_ranges = {"min": float('inf'), "max": 0}
        
        for product in products:
            if product.get("product_format"):
                formats.add(product["product_format"])
            if product.get("brand"):
                brands.add(product["brand"])
            if product.get("scent_flavor"):
                scents.add(product["scent_flavor"])
            if product.get("animal_type"):
                animals.add(product["animal_type"])
            if product.get("target_animals"):
                animals.update(product["target_animals"])
            if product.get("season"):
                seasons.add(product["season"])
            if product.get("price"):
                price_ranges["min"] = min(price_ranges["min"], product["price"])
                price_ranges["max"] = max(price_ranges["max"], product["price"])
        
        return {
            "formats": [
                {"id": "gel", "name": "Gel / Gelée", "icon": "🧴"},
                {"id": "bloc", "name": "Bloc de sel", "icon": "🧱"},
                {"id": "urine", "name": "Urine / Leurre", "icon": "💧"},
                {"id": "granules", "name": "Granules / Pellets", "icon": "🌾"},
                {"id": "liquide", "name": "Liquide / Spray", "icon": "💨"},
                {"id": "poudre", "name": "Poudre / Additif", "icon": "✨"}
            ],
            "brands": sorted(list(brands)),
            "scent_flavors": sorted(list(scents)),
            "animals": [
                {"id": "cerf", "name": "Cerf de Virginie", "icon": "🦌"},
                {"id": "orignal", "name": "Orignal", "icon": "🫎"},
                {"id": "ours", "name": "Ours noir", "icon": "🐻"},
                {"id": "dindon", "name": "Dindon sauvage", "icon": "🦃"},
                {"id": "sanglier", "name": "Sanglier", "icon": "🐗"},
                {"id": "coyote", "name": "Coyote / Prédateurs", "icon": "🐺"}
            ],
            "seasons": [
                {"id": "pre_rut", "name": "Pré-rut (Sept-Oct)", "icon": "🍂"},
                {"id": "rut", "name": "Rut (Nov)", "icon": "🔥"},
                {"id": "post_rut", "name": "Post-rut (Déc)", "icon": "❄️"},
                {"id": "printemps", "name": "Printemps (Avr-Mai)", "icon": "🌷"},
                {"id": "ete", "name": "Été (Juin-Août)", "icon": "☀️"},
                {"id": "all_season", "name": "Toute saison", "icon": "📅"}
            ],
            "features": [
                {"id": "rainproof", "name": "Résistant pluie", "icon": "🌧️", "field": "rainproof"},
                {"id": "pheromones", "name": "Avec phéromones", "icon": "💕", "field": "has_pheromones"},
                {"id": "natural", "name": "100% Naturel", "icon": "🌿", "field": "ingredients_natural"},
                {"id": "certified", "name": "Certifié alimentaire", "icon": "✅", "field": "certified_food"}
            ],
            "price_range": {
                "min": 0 if price_ranges["min"] == float('inf') else price_ranges["min"],
                "max": price_ranges["max"]
            }
        }
    
    # ===========================================
    # ADVANCED SEARCH
    # ===========================================
    
    async def search(self, request: ProductSearchRequest) -> Dict[str, Any]:
        """Advanced product search"""
        query = {}
        
        # Text search
        if request.query:
            query["$or"] = [
                {"name": {"$regex": request.query, "$options": "i"}},
                {"brand": {"$regex": request.query, "$options": "i"}},
                {"description": {"$regex": request.query, "$options": "i"}},
                {"scent_flavor": {"$regex": request.query, "$options": "i"}}
            ]
        
        # Category filter
        if request.categories:
            query["category"] = {"$in": request.categories}
        
        # Format filter
        if request.formats:
            query["product_format"] = {"$in": request.formats}
        
        # Brand filter
        if request.brands:
            query["brand"] = {"$in": request.brands}
        
        # Animal filter
        if request.animals:
            query["$or"] = query.get("$or", []) + [
                {"animal_type": {"$in": request.animals}},
                {"target_animals": {"$in": request.animals}}
            ]
        
        # Season filter
        if request.seasons:
            query["season"] = {"$in": request.seasons}
        
        # Features filter
        if request.features:
            for feature in request.features:
                if feature == "rainproof":
                    query["rainproof"] = True
                elif feature == "pheromones":
                    query["has_pheromones"] = True
                elif feature == "natural":
                    query["ingredients_natural"] = True
                elif feature == "certified":
                    query["certified_food"] = True
        
        # Price filter
        if request.price_min is not None or request.price_max is not None:
            query["price"] = {}
            if request.price_min is not None:
                query["price"]["$gte"] = request.price_min
            if request.price_max is not None:
                query["price"]["$lte"] = request.price_max
        
        # Score filter
        if request.score_min is not None:
            query["score"] = {"$gte": request.score_min}
        
        # Sorting
        sort_direction = 1 if request.sort_order == "asc" else -1
        sort_field = request.sort_by
        
        # Execute query with pagination
        total = self.collection.count_documents(query)
        products = list(
            self.collection.find(query, {"_id": 0})
            .sort(sort_field, sort_direction)
            .skip(request.offset)
            .limit(request.limit)
        )
        
        for product in products:
            if isinstance(product.get('created_at'), str):
                product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        return {
            "products": [Product(**p) for p in products],
            "total": total,
            "limit": request.limit,
            "offset": request.offset,
            "has_more": (request.offset + len(products)) < total
        }
    
    # ===========================================
    # TRACKING
    # ===========================================
    
    async def track_analyze(self, product_id: str) -> bool:
        """Track product analysis action"""
        result = self.collection.update_one(
            {"id": product_id},
            {"$inc": {"views": 1}}
        )
        return result.modified_count > 0
    
    async def track_compare(self, product_id: str) -> bool:
        """Track product comparison action"""
        result = self.collection.update_one(
            {"id": product_id},
            {"$inc": {"comparisons": 1}}
        )
        return result.modified_count > 0
    
    async def track_click(self, product_id: str) -> bool:
        """Track product click action"""
        result = self.collection.update_one(
            {"id": product_id},
            {"$inc": {"clicks": 1}}
        )
        return result.modified_count > 0
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        total = self.collection.count_documents({})
        
        by_category = {}
        pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
        for doc in self.collection.aggregate(pipeline):
            by_category[doc["_id"]] = doc["count"]
        
        return {
            "engine": "products_engine",
            "version": "1.0.0",
            "total_products": total,
            "by_category": by_category,
            "status": "operational"
        }


# Singleton instance
_service_instance = None

def get_products_service() -> ProductsService:
    """Get singleton instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ProductsService()
    return _service_instance
