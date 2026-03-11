"""
MongoDB Database Service
=========================
Centralized MongoDB connection and collection management.

Version: 1.0.0
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Database configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "huntiq_v3")


class Database:
    """MongoDB database manager"""
    
    _client: Optional[AsyncIOMotorClient] = None
    _sync_client: Optional[MongoClient] = None
    _db = None
    _sync_db = None
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get async MongoDB client"""
        if cls._client is None:
            cls._client = AsyncIOMotorClient(MONGO_URL)
            logger.info(f"MongoDB async client connected to {MONGO_URL}")
        return cls._client
    
    @classmethod
    def get_sync_client(cls) -> MongoClient:
        """Get sync MongoDB client"""
        if cls._sync_client is None:
            cls._sync_client = MongoClient(MONGO_URL)
            logger.info(f"MongoDB sync client connected to {MONGO_URL}")
        return cls._sync_client
    
    @classmethod
    def get_database(cls):
        """Get async database instance"""
        if cls._db is None:
            cls._db = cls.get_client()[DB_NAME]
        return cls._db
    
    @classmethod
    def get_sync_database(cls):
        """Get sync database instance"""
        if cls._sync_db is None:
            cls._sync_db = cls.get_sync_client()[DB_NAME]
        return cls._sync_db
    
    @classmethod
    def get_collection(cls, name: str):
        """Get async collection by name"""
        return cls.get_database()[name]
    
    @classmethod
    def get_sync_collection(cls, name: str):
        """Get sync collection by name"""
        return cls.get_sync_database()[name]
    
    @classmethod
    async def close(cls):
        """Close database connections"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
        if cls._sync_client:
            cls._sync_client.close()
            cls._sync_client = None
            cls._sync_db = None


# Collection names
COLLECTIONS = {
    "users": "users",
    "products": "products",
    "orders": "orders",
    "territories": "territories",
    "sightings": "sightings",
    "analytics": "analytics",
    "sessions": "sessions",
    "notifications": "notifications",
    "preferences": "user_preferences",
}


# Helper functions
async def find_one(collection_name: str, filter: Dict) -> Optional[Dict]:
    """Find one document in collection"""
    collection = Database.get_collection(collection_name)
    doc = await collection.find_one(filter, {"_id": 0})
    return doc


async def find_many(
    collection_name: str, 
    filter: Dict = None, 
    limit: int = 100,
    sort: List = None
) -> List[Dict]:
    """Find multiple documents in collection"""
    collection = Database.get_collection(collection_name)
    cursor = collection.find(filter or {}, {"_id": 0})
    
    if sort:
        cursor = cursor.sort(sort)
    
    cursor = cursor.limit(limit)
    return await cursor.to_list(length=limit)


async def insert_one(collection_name: str, document: Dict) -> str:
    """Insert one document into collection"""
    collection = Database.get_collection(collection_name)
    # Remove _id if present to let MongoDB generate it
    doc = {k: v for k, v in document.items() if k != "_id"}
    result = await collection.insert_one(doc)
    return str(result.inserted_id)


async def update_one(
    collection_name: str, 
    filter: Dict, 
    update: Dict,
    upsert: bool = False
) -> bool:
    """Update one document in collection"""
    collection = Database.get_collection(collection_name)
    result = await collection.update_one(filter, {"$set": update}, upsert=upsert)
    return result.modified_count > 0 or result.upserted_id is not None


async def delete_one(collection_name: str, filter: Dict) -> bool:
    """Delete one document from collection"""
    collection = Database.get_collection(collection_name)
    result = await collection.delete_one(filter)
    return result.deleted_count > 0


async def count_documents(collection_name: str, filter: Dict = None) -> int:
    """Count documents in collection"""
    collection = Database.get_collection(collection_name)
    return await collection.count_documents(filter or {})


async def aggregate(collection_name: str, pipeline: List[Dict]) -> List[Dict]:
    """Run aggregation pipeline"""
    collection = Database.get_collection(collection_name)
    cursor = collection.aggregate(pipeline)
    return await cursor.to_list(length=1000)


# Database initialization
async def init_database():
    """Initialize database with indexes and seed data"""
    db = Database.get_database()
    
    # Create indexes
    try:
        # Users collection
        await db.users.create_index("email", unique=True)
        await db.users.create_index("username")
        
        # Products collection
        await db.products.create_index("category")
        await db.products.create_index("name")
        await db.products.create_index([("score", -1)])
        
        # Orders collection
        await db.orders.create_index("user_id")
        await db.orders.create_index("status")
        await db.orders.create_index([("created_at", -1)])
        
        # Sightings collection
        await db.sightings.create_index([("location", "2dsphere")])
        await db.sightings.create_index("species")
        await db.sightings.create_index([("timestamp", -1)])
        
        # Analytics collection
        await db.analytics.create_index("event_type")
        await db.analytics.create_index([("timestamp", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")
    
    # Seed initial data if empty
    product_count = await db.products.count_documents({})
    if product_count == 0:
        await seed_products(db)
    
    return True


async def seed_products(db):
    """Seed initial products data"""
    products = [
        {
            "id": "prod_001",
            "name": "BIONIC Urine de Cerf Premium",
            "brand": "BIONIC",
            "category": "attractants",
            "subcategory": "urine",
            "price": 34.99,
            "score": 92,
            "rank": 1,
            "image_url": "/images/products/urine_cerf.png",
            "description": "Urine de cerf 100% naturelle, haute concentration",
            "ingredients": ["urine de cerf", "conservateurs naturels"],
            "target_species": ["deer"],
            "season": "fall",
            "in_stock": True
        },
        {
            "id": "prod_002",
            "name": "BIONIC Attractant Minéral",
            "brand": "BIONIC",
            "category": "attractants",
            "subcategory": "mineral",
            "price": 24.99,
            "score": 88,
            "rank": 2,
            "image_url": "/images/products/mineral_block.png",
            "description": "Bloc minéral enrichi pour cervidés",
            "ingredients": ["sel", "minéraux essentiels", "mélasse"],
            "target_species": ["deer", "moose"],
            "season": "spring",
            "in_stock": True
        },
        {
            "id": "prod_003",
            "name": "BIONIC Gel Attractif Pomme",
            "brand": "BIONIC",
            "category": "attractants",
            "subcategory": "food",
            "price": 19.99,
            "score": 85,
            "rank": 3,
            "image_url": "/images/products/gel_pomme.png",
            "description": "Gel attractif saveur pomme longue durée",
            "ingredients": ["arôme pomme naturel", "gel végétal"],
            "target_species": ["deer", "bear"],
            "season": "fall",
            "in_stock": True
        },
        {
            "id": "prod_004",
            "name": "BIONIC Spray Tarsal",
            "brand": "BIONIC",
            "category": "attractants",
            "subcategory": "gland",
            "price": 29.99,
            "score": 90,
            "rank": 4,
            "image_url": "/images/products/spray_tarsal.png",
            "description": "Spray imitation glande tarsale pour le rut",
            "ingredients": ["phéromones synthétiques", "base alcool"],
            "target_species": ["deer"],
            "season": "fall",
            "in_stock": True
        },
        {
            "id": "prod_005",
            "name": "Code Bleu Urine Estrus",
            "brand": "Code Bleu",
            "category": "attractants",
            "subcategory": "urine",
            "price": 39.99,
            "score": 89,
            "rank": 5,
            "image_url": "/images/products/urine_estrus.png",
            "description": "Urine de femelle en chaleur",
            "ingredients": ["urine de biche estrus"],
            "target_species": ["deer"],
            "season": "fall",
            "in_stock": True
        }
    ]
    
    await db.products.insert_many(products)
    logger.info(f"Seeded {len(products)} products")
