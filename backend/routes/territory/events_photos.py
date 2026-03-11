"""
Territory Module - Events & Photos API
Phase 1.8 - Split from territory.py
"""
import uuid
import json
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, File, Form, BackgroundTasks
import exifread
from io import BytesIO

from ._base import territory_router, get_db, logger, UPLOAD_DIR, EMERGENT_LLM_KEY
from .models import EventCreate, EventResponse, PhotoUploadResponse, AIClassificationResult


def extract_exif_data(image_bytes: bytes) -> dict:
    """Extract EXIF data from image bytes"""
    try:
        tags = exifread.process_file(BytesIO(image_bytes), details=False)
        exif_data = {
            'datetime': None, 'gps_lat': None, 'gps_lon': None,
            'camera_make': None, 'camera_model': None
        }
        if 'EXIF DateTimeOriginal' in tags:
            dt_str = str(tags['EXIF DateTimeOriginal'])
            try:
                exif_data['datetime'] = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            except Exception:
                pass
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            try:
                lat = tags['GPS GPSLatitude']
                lon = tags['GPS GPSLongitude']
                lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
                lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
                def convert_to_degrees(value):
                    d = float(value.values[0].num) / float(value.values[0].den)
                    m = float(value.values[1].num) / float(value.values[1].den)
                    s = float(value.values[2].num) / float(value.values[2].den)
                    return d + (m / 60.0) + (s / 3600.0)
                exif_data['gps_lat'] = convert_to_degrees(lat)
                if lat_ref == 'S':
                    exif_data['gps_lat'] = -exif_data['gps_lat']
                exif_data['gps_lon'] = convert_to_degrees(lon)
                if lon_ref == 'W':
                    exif_data['gps_lon'] = -exif_data['gps_lon']
            except Exception as e:
                logger.warning(f"Failed to parse GPS data: {e}")
        if 'Image Make' in tags:
            exif_data['camera_make'] = str(tags['Image Make'])
        if 'Image Model' in tags:
            exif_data['camera_model'] = str(tags['Image Model'])
        return exif_data
    except Exception as e:
        logger.error(f"EXIF extraction error: {e}")
        return {}


async def classify_species_with_ai(image_base64: str) -> AIClassificationResult:
    """Use GPT-4 Vision to classify species in the image"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        prompt = """Analyse cette photo de camera de chasse et identifie l'espece animale presente.

Tu dois repondre UNIQUEMENT avec un JSON valide dans ce format exact (sans markdown):
{"species": "orignal|chevreuil|ours|autre", "confidence": 0.0-1.0, "count_estimate": 1, "reasoning": "explication courte"}

Regles:
- orignal = moose/elan
- chevreuil = white-tailed deer/cerf de Virginie
- ours = black bear/ours noir
- autre = tout autre animal ou absence d'animal visible
- confidence: 0.9+ si tres sur, 0.7-0.9 si probable, <0.7 si incertain
- count_estimate: nombre d'individus visibles de cette espece

Si aucun animal n'est visible, retourne {"species": "autre", "confidence": 0.95, "count_estimate": 0, "reasoning": "Aucun animal visible"}"""

        llm = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="Tu es un expert en identification de la faune sauvage nord-americaine."
        ).with_model("openai", "gpt-4o")
        image_content = ImageContent(image_base64=image_base64)
        user_message = UserMessage(text=prompt, file_contents=[image_content])
        response = await llm.send_message(user_message)
        response_text = response.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        result = json.loads(response_text)
        return AIClassificationResult(
            species=result.get('species', 'autre'),
            confidence=float(result.get('confidence', 0.5)),
            count_estimate=int(result.get('count_estimate', 1)),
            reasoning=result.get('reasoning', '')
        )
    except Exception as e:
        logger.error(f"AI classification error: {e}")
        return AIClassificationResult(
            species='autre', confidence=0.0, count_estimate=0,
            reasoning=f"Erreur d'analyse: {str(e)}"
        )


def _geo_entity_to_event_response(entity: dict) -> EventResponse:
    """Convert a geo_entity document to EventResponse format"""
    location = entity.get('location', {})
    coords = location.get('coordinates', [0, 0])
    lng, lat = coords[0], coords[1]
    metadata = entity.get('metadata', {})
    return EventResponse(
        id=str(entity['_id']),
        event_type=metadata.get('event_type', entity.get('subtype', 'observation')),
        species=metadata.get('species'),
        species_confidence=metadata.get('species_confidence'),
        count_estimate=metadata.get('count_estimate', 1) or 1,
        latitude=lat, longitude=lng,
        captured_at=metadata.get('captured_at') or entity.get('created_at', datetime.now(timezone.utc)),
        source=metadata.get('source', 'app'),
        metadata=metadata
    )


@territory_router.get("/events/recent")
async def get_recent_events(
    user_id: str, species: Optional[str] = None,
    hours: int = 72, limit: int = 100
):
    """Get recent events for a user (P2 NORMALIZED - reads from geo_entities)"""
    database = await get_db()
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    cutoff_naive = cutoff_time.replace(tzinfo=None)
    query = {"user_id": user_id, "entity_type": "observation", "created_at": {"$gte": cutoff_naive}}
    if species:
        query["metadata.species"] = species
    events = await database.geo_entities.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [_geo_entity_to_event_response(event) for event in events]


@territory_router.get("/events/species/{species}")
async def get_events_by_species(user_id: str, species: str, limit: int = 100):
    """Get events filtered by species (P2 NORMALIZED)"""
    if species not in ['orignal', 'chevreuil', 'ours', 'autre']:
        raise HTTPException(status_code=400, detail="Invalid species")
    return await get_recent_events(user_id, species=species, hours=168, limit=limit)


@territory_router.post("/events", response_model=EventResponse)
async def create_event(user_id: str, event: EventCreate):
    """Create a new event/observation (P2 NORMALIZED - writes to geo_entities)"""
    database = await get_db()
    event_id = str(uuid.uuid4())
    captured_at = event.captured_at or datetime.now(timezone.utc)
    now = datetime.now(timezone.utc)
    event_type = event.event_type or 'observation'
    species = event.species or 'inconnu'
    name = f"{event_type.replace('_', ' ').title()} - {species.title()}"
    geo_entity_doc = {
        "_id": event_id, "user_id": user_id, "group_id": None, "name": name,
        "entity_type": "observation", "subtype": event_type,
        "location": {"type": "Point", "coordinates": [event.longitude, event.latitude]},
        "geometry": None, "radius": None, "active": True, "visible": True,
        "color": "#FF6B6B", "icon": "eye",
        "metadata": {
            "event_type": event_type, "species": event.species,
            "species_confidence": event.species_confidence,
            "count_estimate": event.count_estimate or 1,
            "captured_at": captured_at, "source": event.source,
            **(event.metadata or {})
        },
        "description": None, "created_at": now, "updated_at": now
    }
    await database.geo_entities.insert_one(geo_entity_doc)
    return EventResponse(
        id=event_id, event_type=event_type, species=event.species,
        species_confidence=event.species_confidence, count_estimate=event.count_estimate or 1,
        latitude=event.latitude, longitude=event.longitude,
        captured_at=captured_at, source=event.source, metadata=event.metadata or {}
    )


@territory_router.delete("/events/{event_id}")
async def delete_event(event_id: str, user_id: str):
    """Delete an event/observation (P2 NORMALIZED - deletes from geo_entities)"""
    database = await get_db()
    result = await database.geo_entities.delete_one({
        "_id": event_id, "user_id": user_id, "entity_type": "observation"
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully", "id": event_id}


@territory_router.post("/photos/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    camera_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Upload a trail camera photo for AI analysis"""
    database = await get_db()
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    exif_data = extract_exif_data(content)
    file_ext = Path(file.filename).suffix if file.filename else '.jpg'
    photo_id = str(uuid.uuid4())
    photo_filename = f"{photo_id}{file_ext}"
    photo_path = UPLOAD_DIR / photo_filename
    async with aiofiles.open(photo_path, 'wb') as f:
        await f.write(content)
    captured_at = exif_data.get('datetime') or datetime.now(timezone.utc)
    photo_doc = {
        "_id": photo_id, "user_id": user_id, "camera_id": camera_id,
        "photo_path": str(photo_path), "original_filename": file.filename,
        "exif_datetime": exif_data.get('datetime'),
        "exif_gps_lat": exif_data.get('gps_lat'), "exif_gps_lon": exif_data.get('gps_lon'),
        "exif_camera_make": exif_data.get('camera_make'),
        "exif_camera_model": exif_data.get('camera_model'),
        "processing_status": "pending", "captured_at": captured_at,
        "created_at": datetime.now(timezone.utc),
        "species": None, "species_confidence": None, "count_estimate": None
    }
    await database.territory_photos.insert_one(photo_doc)
    background_tasks.add_task(process_photo_ai, photo_id, content, user_id, exif_data)
    return PhotoUploadResponse(
        id=photo_id, photo_url=f"/api/territory/photos/{photo_id}/image",
        processing_status='pending', exif_datetime=exif_data.get('datetime'),
        exif_gps_lat=exif_data.get('gps_lat'), exif_gps_lon=exif_data.get('gps_lon'),
        species=None, species_confidence=None, count_estimate=None
    )


async def process_photo_ai(photo_id: str, image_bytes: bytes, user_id: str, exif_data: dict):
    """Background task to process photo with AI"""
    database = await get_db()
    try:
        await database.territory_photos.update_one(
            {"_id": photo_id}, {"$set": {"processing_status": "processing"}}
        )
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        result = await classify_species_with_ai(image_base64)
        await database.territory_photos.update_one(
            {"_id": photo_id},
            {"$set": {
                "species": result.species, "species_confidence": result.confidence,
                "count_estimate": result.count_estimate,
                "ai_analysis_raw": {"reasoning": result.reasoning},
                "ai_processed_at": datetime.now(timezone.utc),
                "processing_status": "completed"
            }}
        )
        if exif_data.get('gps_lat') and exif_data.get('gps_lon') and result.species != 'autre':
            captured_at = exif_data.get('datetime') or datetime.now(timezone.utc)
            now = datetime.now(timezone.utc)
            event_id = str(uuid.uuid4())
            species = result.species or 'inconnu'
            name = f"Camera Photo - {species.title()}"
            geo_entity_doc = {
                "_id": event_id, "user_id": user_id, "group_id": None, "name": name,
                "entity_type": "observation", "subtype": "camera_photo",
                "location": {"type": "Point", "coordinates": [exif_data['gps_lon'], exif_data['gps_lat']]},
                "geometry": None, "radius": None, "active": True, "visible": True,
                "color": "#FF6B6B", "icon": "camera",
                "metadata": {
                    "event_type": "camera_photo", "species": result.species,
                    "species_confidence": result.confidence,
                    "count_estimate": result.count_estimate,
                    "captured_at": captured_at, "source": "camera",
                    "photo_id": photo_id, "reasoning": result.reasoning
                },
                "description": None, "created_at": now, "updated_at": now
            }
            await database.geo_entities.insert_one(geo_entity_doc)
            await database.territory_photos.update_one(
                {"_id": photo_id}, {"$set": {"event_id": event_id}}
            )
        logger.info(f"Photo {photo_id} classified as {result.species} with {result.confidence:.2f} confidence")
    except Exception as e:
        logger.error(f"Error processing photo {photo_id}: {e}")
        await database.territory_photos.update_one(
            {"_id": photo_id},
            {"$set": {"processing_status": "failed", "processing_error": str(e)}}
        )


@territory_router.get("/photos/{photo_id}")
async def get_photo_status(photo_id: str):
    """Get photo processing status and results"""
    database = await get_db()
    photo = await database.territory_photos.find_one({"_id": photo_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {
        "id": str(photo['_id']),
        "photo_url": f"/api/territory/photos/{photo_id}/image",
        "processing_status": photo.get('processing_status', 'pending'),
        "processing_error": photo.get('processing_error'),
        "exif_datetime": photo.get('exif_datetime'),
        "exif_gps_lat": photo.get('exif_gps_lat'),
        "exif_gps_lon": photo.get('exif_gps_lon'),
        "species": photo.get('species'),
        "species_confidence": photo.get('species_confidence'),
        "count_estimate": photo.get('count_estimate'),
        "ai_analysis": photo.get('ai_analysis_raw'),
        "ai_processed_at": photo.get('ai_processed_at'),
        "event_id": photo.get('event_id')
    }


@territory_router.get("/photos/{photo_id}/image")
async def get_photo_image(photo_id: str):
    """Serve the photo image file"""
    from fastapi.responses import FileResponse
    database = await get_db()
    photo = await database.territory_photos.find_one({"_id": photo_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    photo_path = Path(photo['photo_path'])
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found")
    return FileResponse(photo_path)
