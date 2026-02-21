"""
SEO, Analytics & Content Depot API
- SEO: Sitemap XML, Meta tags, Schema.org
- Analytics: Internal tracking (vues, clics, conversions)
- Content Depot: Workflow de validation avec génération IA
"""

from fastapi import APIRouter, HTTPException, Query, Body, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import uuid
import os
import base64
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

seo_router = APIRouter(prefix="/api/seo", tags=["SEO & Analytics"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
SITE_URL = os.environ.get("SITE_URL", "https://contour-mapper-2.preview.emergentagent.com")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db

# ============================================
# PYDANTIC MODELS
# ============================================

class PageMetadata(BaseModel):
    url: str
    title: str
    description: str
    keywords: List[str] = []
    og_image: Optional[str] = None
    og_type: str = "website"
    schema_type: str = "WebPage"
    last_modified: Optional[str] = None

class ContentItem(BaseModel):
    title: str
    description: str
    content_type: str  # "ad", "seo", "social", "email"
    platform: str = "all"  # "facebook", "instagram", "tiktok", "youtube", "all"
    format: str = "square"  # "square", "vertical", "horizontal"
    target_page: Optional[str] = None
    target_video: Optional[str] = None
    hashtags: List[str] = []
    call_to_action: Optional[str] = None

class ContentGenRequest(BaseModel):
    content_type: str = "ad"  # "ad", "seo_title", "seo_description", "hashtags", "cta"
    context: str  # Description du produit/page/vidéo
    tone: str = "professional"  # "professional", "casual", "urgent", "fun"
    platform: str = "all"
    language: str = "fr"

class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "professional"  # "professional", "artistic", "photo-realistic", "hunting"
    format: str = "square"  # "square", "vertical", "horizontal"

class AnalyticsEvent(BaseModel):
    event_type: str  # "page_view", "click", "conversion", "video_view", "add_to_cart"
    page_url: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

# ============================================
# SEO ENDPOINTS
# ============================================

@seo_router.get("/sitemap.xml", response_class=PlainTextResponse)
async def generate_sitemap():
    """Generate dynamic XML sitemap"""
    database = await get_db()
    
    # Static pages
    pages = [
        {"url": "/", "priority": "1.0", "changefreq": "daily"},
        {"url": "/analyze", "priority": "0.9", "changefreq": "weekly"},
        {"url": "/compare", "priority": "0.8", "changefreq": "weekly"},
        {"url": "/shop", "priority": "0.9", "changefreq": "daily"},
        {"url": "/territory", "priority": "0.9", "changefreq": "daily"},
        {"url": "/marketplace", "priority": "0.9", "changefreq": "hourly"},
        {"url": "/formations", "priority": "0.7", "changefreq": "weekly"},
    ]
    
    # Get products from database
    products = await database.products.find({}, {"_id": 0, "id": 1, "updated_at": 1}).to_list(100)
    for product in products:
        pages.append({
            "url": f"/shop/product/{product.get('id', '')}",
            "priority": "0.7",
            "changefreq": "weekly",
            "lastmod": product.get("updated_at", "")
        })
    
    # Get marketplace listings
    listings = await database.marketplace_listings.find(
        {"availability": "disponible"},
        {"_id": 0, "id": 1, "updated_at": 1}
    ).to_list(500)
    for listing in listings:
        pages.append({
            "url": f"/marketplace/listing/{listing.get('id', '')}",
            "priority": "0.6",
            "changefreq": "daily",
            "lastmod": listing.get("updated_at", "")
        })
    
    # Build XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{SITE_URL}{page["url"]}</loc>\n'
        xml_content += f'    <priority>{page["priority"]}</priority>\n'
        xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        if page.get("lastmod"):
            xml_content += f'    <lastmod>{page["lastmod"][:10]}</lastmod>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    return Response(content=xml_content, media_type="application/xml")

@seo_router.get("/robots.txt", response_class=PlainTextResponse)
async def generate_robots():
    """Generate robots.txt"""
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {SITE_URL}/api/seo/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@seo_router.get("/meta/{page_path:path}")
async def get_page_meta(page_path: str):
    """Get meta tags for a specific page"""
    database = await get_db()
    
    # Default meta
    meta = {
        "title": "Chasse Bionic TM | Analyseur d'Attractants de Chasse",
        "description": "Votre parcours guidé vers une chasse parfaite. Analysez, comparez et trouvez les meilleurs attractants pour orignal, chevreuil et ours.",
        "keywords": ["chasse", "attractant", "orignal", "chevreuil", "ours", "Québec", "Chasse Bionic", "Bionic Hunt"],
        "og_image": f"{SITE_URL}/og-image.jpg",
        "og_type": "website",
        "canonical": f"{SITE_URL}/{page_path}",
        "schema": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Chasse Bionic TM",
            "url": SITE_URL,
            "description": "Analyseur d'attractants de chasse professionnel"
        }
    }
    
    # Page-specific meta
    page_meta = {
        "": {
            "title": "Chasse Bionic TM | Votre parcours guidé vers une chasse parfaite",
            "og_type": "website"
        },
        "shop": {
            "title": "Magasin Chasse Bionic TM | Attractants et Équipements de Chasse",
            "description": "Découvrez notre sélection d'attractants et équipements de chasse premium. Livraison rapide au Québec.",
            "schema": {"@type": "Store"}
        },
        "territory": {
            "title": "Territoire | Carte Interactive de Chasse du Québec",
            "description": "Analysez votre territoire de chasse avec notre carte interactive. Spots GPS, zones de probabilité et territoires classés.",
            "schema": {"@type": "WebApplication"}
        },
        "marketplace": {
            "title": "Hunt Marketplace | Achetez & Vendez du Matériel de Chasse",
            "description": "Le marketplace #1 pour acheter, vendre ou louer du matériel de chasse au Québec. Équipements, forfaits et terres à louer.",
            "schema": {"@type": "WebPage", "specialty": "Marketplace"}
        },
        "analyze": {
            "title": "Analyseur Chasse Bionic TM | Trouvez l'Attractant Parfait",
            "description": "Notre IA analyse vos besoins et vous recommande les meilleurs attractants pour votre type de chasse.",
            "schema": {"@type": "WebApplication"}
        },
        "formations": {
            "title": "Formations Chasse | Cours et Certifications FédéCP",
            "description": "Formations officielles de chasse, cours de sécurité et certifications. Apprenez avec les experts.",
            "schema": {"@type": "Course"}
        }
    }
    
    if page_path in page_meta:
        meta.update(page_meta[page_path])
        if "schema" in page_meta[page_path]:
            meta["schema"].update(page_meta[page_path]["schema"])
    
    return meta

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@seo_router.post("/analytics/track")
async def track_event(event: AnalyticsEvent):
    """Track an analytics event"""
    database = await get_db()
    
    event_data = {
        "id": str(uuid.uuid4()),
        "event_type": event.event_type,
        "page_url": event.page_url,
        "user_id": event.user_id,
        "session_id": event.session_id,
        "metadata": event.metadata,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    await database.analytics_events.insert_one(event_data)
    
    # Update page stats
    await database.page_stats.update_one(
        {"page_url": event.page_url, "date": event_data["date"]},
        {
            "$inc": {
                f"{event.event_type}_count": 1,
                "total_events": 1
            },
            "$setOnInsert": {"created_at": event_data["timestamp"]}
        },
        upsert=True
    )
    
    return {"success": True, "event_id": event_data["id"]}

@seo_router.get("/analytics/dashboard")
async def get_analytics_dashboard(days: int = 30):
    """Get analytics dashboard data"""
    database = await get_db()
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Aggregate stats
    pipeline = [
        {"$match": {"date": {"$gte": start_date}}},
        {"$group": {
            "_id": None,
            "total_page_views": {"$sum": "$page_view_count"},
            "total_clicks": {"$sum": "$click_count"},
            "total_conversions": {"$sum": "$conversion_count"},
            "total_add_to_cart": {"$sum": "$add_to_cart_count"},
            "total_video_views": {"$sum": "$video_view_count"},
            "unique_pages": {"$addToSet": "$page_url"}
        }}
    ]
    
    result = await database.page_stats.aggregate(pipeline).to_list(1)
    
    # Daily breakdown
    daily_pipeline = [
        {"$match": {"date": {"$gte": start_date}}},
        {"$group": {
            "_id": "$date",
            "page_views": {"$sum": "$page_view_count"},
            "clicks": {"$sum": "$click_count"},
            "conversions": {"$sum": "$conversion_count"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    daily_stats = await database.page_stats.aggregate(daily_pipeline).to_list(60)
    
    # Top pages
    top_pages_pipeline = [
        {"$match": {"date": {"$gte": start_date}}},
        {"$group": {
            "_id": "$page_url",
            "views": {"$sum": "$page_view_count"},
            "clicks": {"$sum": "$click_count"}
        }},
        {"$sort": {"views": -1}},
        {"$limit": 10}
    ]
    
    top_pages = await database.page_stats.aggregate(top_pages_pipeline).to_list(10)
    
    stats = result[0] if result else {}
    
    return {
        "period_days": days,
        "summary": {
            "total_page_views": stats.get("total_page_views", 0),
            "total_clicks": stats.get("total_clicks", 0),
            "total_conversions": stats.get("total_conversions", 0),
            "total_add_to_cart": stats.get("total_add_to_cart", 0),
            "total_video_views": stats.get("total_video_views", 0),
            "unique_pages": len(stats.get("unique_pages", []))
        },
        "daily_stats": [{"date": d["_id"], **{k: v for k, v in d.items() if k != "_id"}} for d in daily_stats],
        "top_pages": [{"page": p["_id"], "views": p["views"], "clicks": p["clicks"]} for p in top_pages],
        "conversion_rate": round(
            (stats.get("total_conversions", 0) / max(1, stats.get("total_page_views", 1))) * 100, 2
        )
    }

# ============================================
# CONTENT DEPOT ENDPOINTS
# ============================================

@seo_router.post("/content/generate-text")
async def generate_content_text(request: ContentGenRequest):
    """Generate marketing text using AI"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Build prompt based on content type
        prompts = {
            "ad": f"""Génère une publicité accrocheuse pour: {request.context}
            
Plateforme: {request.platform}
Ton: {request.tone}
Langue: Français

Réponds en JSON avec:
- title: titre accrocheur (max 60 caractères)
- description: description engageante (max 200 caractères)
- cta: appel à l'action
- hashtags: liste de 5-8 hashtags pertinents
- hook: phrase d'accroche pour capturer l'attention""",

            "seo_title": f"""Génère un titre SEO optimisé pour: {request.context}

Langue: Français
Max 60 caractères
Inclure le mot-clé principal au début

Réponds uniquement avec le titre, sans guillemets.""",

            "seo_description": f"""Génère une meta description SEO pour: {request.context}

Langue: Français
Entre 120-155 caractères
Inclure un appel à l'action
Inclure le mot-clé principal

Réponds uniquement avec la description, sans guillemets.""",

            "hashtags": f"""Génère des hashtags pour: {request.context}

Plateforme: {request.platform}
Langue: Français

Réponds avec une liste JSON de 10-15 hashtags pertinents, populaires et de niche.""",

            "cta": f"""Génère 5 appels à l'action pour: {request.context}

Ton: {request.tone}
Langue: Français

Réponds avec une liste JSON de CTAs courts et percutants."""
        }
        
        prompt = prompts.get(request.content_type, prompts["ad"])
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"content-gen-{uuid.uuid4()}",
            system_message="Tu es un expert en marketing digital et copywriting spécialisé dans l'industrie de la chasse et du plein air au Québec. Tu génères du contenu engageant, authentique et optimisé pour la conversion."
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {
            "success": True,
            "content_type": request.content_type,
            "generated": response,
            "platform": request.platform,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@seo_router.post("/content/generate-image")
async def generate_content_image(request: ImageGenRequest):
    """Generate marketing image using AI"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        
        # Build enhanced prompt
        style_prompts = {
            "professional": "professional marketing photo, clean composition, high quality",
            "artistic": "artistic illustration, creative, eye-catching colors",
            "photo-realistic": "ultra realistic photography, DSLR quality, natural lighting",
            "hunting": "outdoor hunting scene, wilderness, Canadian forest, professional photography"
        }
        
        size_map = {
            "square": "1024x1024",
            "vertical": "1024x1792",
            "horizontal": "1792x1024"
        }
        
        enhanced_prompt = f"{request.prompt}, {style_prompts.get(request.style, style_prompts['professional'])}, Quebec wilderness theme"
        
        image_gen = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
        images = await image_gen.generate_images(
            prompt=enhanced_prompt,
            model="gpt-image-1",
            number_of_images=1
        )
        
        if images and len(images) > 0:
            image_base64 = base64.b64encode(images[0]).decode('utf-8')
            
            return {
                "success": True,
                "image_base64": image_base64,
                "format": request.format,
                "style": request.style,
                "prompt_used": enhanced_prompt,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="No image generated")
            
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@seo_router.post("/content/depot")
async def create_content_depot_item(item: ContentItem, token: str = Query(None)):
    """Create a new content item in the depot"""
    database = await get_db()
    
    depot_item = {
        "id": str(uuid.uuid4()),
        "title": item.title,
        "description": item.description,
        "content_type": item.content_type,
        "platform": item.platform,
        "format": item.format,
        "target_page": item.target_page,
        "target_video": item.target_video,
        "hashtags": item.hashtags,
        "call_to_action": item.call_to_action,
        "status": "pending",  # pending, optimized, accepted, published
        "versions": [{
            "version": 1,
            "title": item.title,
            "description": item.description,
            "hashtags": item.hashtags,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action": "created"
        }],
        "visuals": [],
        "suggestions": [],
        "publish_history": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await database.content_depot.insert_one(depot_item)
    
    return {"success": True, "item": depot_item}

@seo_router.get("/content/depot")
async def get_content_depot(
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get content depot items"""
    database = await get_db()
    
    query = {}
    if status:
        query["status"] = status
    if content_type:
        query["content_type"] = content_type
    
    total = await database.content_depot.count_documents(query)
    skip = (page - 1) * limit
    
    items = await database.content_depot.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@seo_router.get("/content/depot/{item_id}")
async def get_content_depot_item(item_id: str):
    """Get a specific content depot item"""
    database = await get_db()
    
    item = await database.content_depot.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@seo_router.post("/content/depot/{item_id}/optimize")
async def optimize_content(item_id: str, field: str = "all"):
    """Optimize content using AI"""
    database = await get_db()
    
    item = await database.content_depot.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Optimise ce contenu marketing pour maximiser l'engagement:

Titre actuel: {item['title']}
Description actuelle: {item['description']}
Hashtags actuels: {', '.join(item.get('hashtags', []))}
Plateforme: {item['platform']}
Type: {item['content_type']}

Génère une version améliorée en JSON avec:
- title: titre plus accrocheur
- description: description plus engageante
- hashtags: hashtags optimisés (10 max)
- cta: appel à l'action percutant
- improvements: liste des améliorations apportées"""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"optimize-{item_id}",
            system_message="Tu es un expert en optimisation de contenu marketing pour l'industrie de la chasse au Québec."
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Update item
        new_version = {
            "version": len(item.get("versions", [])) + 1,
            "title": item["title"],
            "description": item["description"],
            "hashtags": item.get("hashtags", []),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action": "optimized",
            "ai_response": response
        }
        
        await database.content_depot.update_one(
            {"id": item_id},
            {
                "$set": {
                    "status": "optimized",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"versions": new_version}
            }
        )
        
        return {
            "success": True,
            "optimized": response,
            "version": new_version["version"]
        }
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@seo_router.post("/content/depot/{item_id}/suggest")
async def suggest_modifications(item_id: str):
    """Generate AI suggestions for content improvement"""
    database = await get_db()
    
    item = await database.content_depot.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Analyse ce contenu marketing et génère des suggestions d'amélioration:

Titre: {item['title']}
Description: {item['description']}
Type: {item['content_type']}
Plateforme: {item['platform']}

Génère une liste JSON de 5-7 suggestions concrètes et actionnables pour améliorer:
- L'accroche et l'engagement
- Le SEO
- La conversion
- L'adaptation à la plateforme cible

Format: [{{"suggestion": "...", "category": "...", "priority": "high/medium/low"}}]"""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"suggest-{item_id}",
            system_message="Tu es un consultant en marketing digital spécialisé dans l'industrie de la chasse."
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        suggestion = {
            "id": str(uuid.uuid4()),
            "ai_suggestions": response,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "applied": False
        }
        
        await database.content_depot.update_one(
            {"id": item_id},
            {"$push": {"suggestions": suggestion}}
        )
        
        return {"success": True, "suggestions": response}
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@seo_router.post("/content/depot/{item_id}/accept")
async def accept_content(item_id: str):
    """Mark content as accepted"""
    database = await get_db()
    
    result = await database.content_depot.update_one(
        {"id": item_id},
        {
            "$set": {
                "status": "accepted",
                "accepted_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"success": True, "status": "accepted"}

@seo_router.post("/content/depot/{item_id}/publish")
async def publish_content(item_id: str, platforms: List[str] = Body(["internal"])):
    """Publish content (internal notification for now)"""
    database = await get_db()
    
    item = await database.content_depot.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    publish_record = {
        "id": str(uuid.uuid4()),
        "platforms": platforms,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "status": "published"
    }
    
    await database.content_depot.update_one(
        {"id": item_id},
        {
            "$set": {
                "status": "published",
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"publish_history": publish_record}
        }
    )
    
    # Log publication
    await database.publication_log.insert_one({
        "content_id": item_id,
        "title": item["title"],
        "platforms": platforms,
        "published_at": publish_record["published_at"]
    })
    
    return {
        "success": True,
        "status": "published",
        "platforms": platforms,
        "note": "Publication interne enregistrée. Intégration réseaux sociaux disponible sur demande."
    }

@seo_router.put("/content/depot/{item_id}")
async def update_content_depot_item(item_id: str, updates: Dict[str, Any] = Body(...)):
    """Update a content depot item"""
    database = await get_db()
    
    item = await database.content_depot.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Create version history
    new_version = {
        "version": len(item.get("versions", [])) + 1,
        "title": updates.get("title", item["title"]),
        "description": updates.get("description", item["description"]),
        "hashtags": updates.get("hashtags", item.get("hashtags", [])),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "action": "manual_edit"
    }
    
    allowed_fields = ["title", "description", "hashtags", "call_to_action", "platform", "format"]
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await database.content_depot.update_one(
        {"id": item_id},
        {
            "$set": update_data,
            "$push": {"versions": new_version}
        }
    )
    
    return {"success": True, "version": new_version["version"]}

@seo_router.delete("/content/depot/{item_id}")
async def delete_content_depot_item(item_id: str):
    """Delete a content depot item"""
    database = await get_db()
    
    result = await database.content_depot.delete_one({"id": item_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"success": True, "deleted": True}

# ============================================
# SEO RECOMMENDATIONS
# ============================================

@seo_router.post("/seo/analyze")
async def analyze_seo(url: str = Body(..., embed=True)):
    """Analyze SEO for a page and generate recommendations"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Analyse cette URL et génère des recommandations SEO: {url}

Génère une analyse JSON avec:
- score: score SEO estimé (0-100)
- title_analysis: analyse du titre
- description_analysis: analyse de la meta description
- keywords: mots-clés recommandés
- recommendations: liste de 5-10 recommandations prioritaires
- quick_wins: améliorations rapides à implémenter
- technical_issues: problèmes techniques potentiels"""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"seo-analyze-{uuid.uuid4()}",
            system_message="Tu es un expert SEO spécialisé dans les sites e-commerce et les applications web."
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {
            "success": True,
            "url": url,
            "analysis": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"SEO analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

logger.info("SEO, Analytics & Content Depot API initialized")
