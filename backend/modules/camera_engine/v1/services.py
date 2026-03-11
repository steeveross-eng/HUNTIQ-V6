"""
Camera Engine - Services
Phase 1: Camera Registry, Email Ingestion, and EXIF Reader services
"""
import os
import uuid
import base64
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import (
    Camera, CameraCreate, CameraUpdate, CameraStatus,
    CameraEvent, EmailIngestionRequest, EmailIngestionResponse, EmailIngestionStatus,
    IngestionLog
)

logger = logging.getLogger(__name__)

# Domain for email aliases
EMAIL_DOMAIN = os.environ.get("CAMERA_EMAIL_DOMAIN", "cam.huntiq.ca")

# Encryption key for images (in production, use proper key management)
ENCRYPTION_KEY = os.environ.get("CAMERA_ENCRYPTION_KEY", "huntiq_camera_key_v1")


# ============================================
# CAMERA REGISTRY SERVICE
# ============================================

class CameraRegistryService:
    """
    Service for camera management.
    
    RÈGLE FONDAMENTALE: Une caméra ne peut JAMAIS exister sans waypoint.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.cameras_collection = db['cameras']
        self.waypoints_collection = db['waypoints']
    
    def _generate_email_alias(self, user_id: str, camera_id: str) -> str:
        """Generate unique email alias for camera ingestion."""
        # Create a short hash from user_id + camera_id for uniqueness
        hash_input = f"{user_id}:{camera_id}:{datetime.utcnow().timestamp()}"
        short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        return f"cam-{short_hash}@{EMAIL_DOMAIN}"
    
    async def _validate_waypoint_exists(self, waypoint_id: str, user_id: str) -> bool:
        """Validate that waypoint exists and belongs to user."""
        # Check in territory_waypoints collection (primary)
        waypoint = await self.db['territory_waypoints'].find_one({
            "$or": [
                {"_id": waypoint_id, "user_id": user_id},
                {"id": waypoint_id, "user_id": user_id},
                {"waypoint_id": waypoint_id, "user_id": user_id}
            ]
        })
        if waypoint:
            return True
        
        # Fallback to waypoints collection
        waypoint = await self.waypoints_collection.find_one({
            "$or": [
                {"id": waypoint_id, "user_id": user_id},
                {"waypoint_id": waypoint_id, "user_id": user_id}
            ]
        })
        if waypoint:
            return True
        
        # Check geo_entities collection
        waypoint = await self.db['geo_entities'].find_one({
            "$or": [
                {"id": waypoint_id, "user_id": user_id},
                {"entity_id": waypoint_id, "user_id": user_id}
            ]
        })
        return waypoint is not None
    
    async def create_camera(self, user_id: str, data: CameraCreate) -> Tuple[Optional[Camera], Optional[str]]:
        """
        Create a new camera with MANDATORY waypoint association.
        
        Returns: (camera, error_message)
        """
        # RÈGLE ABSOLUE: Vérifier que le waypoint existe
        waypoint_exists = await self._validate_waypoint_exists(data.waypoint_id, user_id)
        if not waypoint_exists:
            logger.warning(f"Camera creation rejected: waypoint {data.waypoint_id} not found for user {user_id}")
            return None, "REJET: Le waypoint spécifié n'existe pas ou n'appartient pas à l'utilisateur"
        
        camera_id = str(uuid.uuid4())
        email_alias = self._generate_email_alias(user_id, camera_id)
        
        camera = Camera(
            id=camera_id,
            user_id=user_id,
            email_alias=email_alias,
            waypoint_id=data.waypoint_id,
            manufacturer=data.manufacturer,
            model=data.model,
            serial=data.serial,
            name=data.name,
            gps_lat=data.gps_lat,
            gps_lon=data.gps_lon,
            status=CameraStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        await self.cameras_collection.insert_one(camera.model_dump())
        logger.info(f"Camera created: {camera_id} for user {user_id} with waypoint {data.waypoint_id}")
        
        return camera, None
    
    async def get_camera(self, camera_id: str, user_id: str) -> Optional[Camera]:
        """Get camera by ID (user isolation enforced)."""
        doc = await self.cameras_collection.find_one(
            {"id": camera_id, "user_id": user_id},
            {"_id": 0}
        )
        return Camera(**doc) if doc else None
    
    async def get_camera_by_email_alias(self, email_alias: str) -> Optional[Camera]:
        """Get camera by email alias (for ingestion service)."""
        doc = await self.cameras_collection.find_one(
            {"email_alias": email_alias},
            {"_id": 0}
        )
        return Camera(**doc) if doc else None
    
    async def list_cameras(self, user_id: str, skip: int = 0, limit: int = 50) -> Tuple[List[Camera], int]:
        """List all cameras for user."""
        cursor = self.cameras_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).skip(skip).limit(limit)
        
        cameras = [Camera(**doc) async for doc in cursor]
        total = await self.cameras_collection.count_documents({"user_id": user_id})
        
        return cameras, total
    
    async def update_camera(self, camera_id: str, user_id: str, data: CameraUpdate) -> Tuple[Optional[Camera], Optional[str]]:
        """Update camera (waypoint cannot be changed or removed)."""
        existing = await self.get_camera(camera_id, user_id)
        if not existing:
            return None, "Caméra non trouvée"
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await self.cameras_collection.update_one(
            {"id": camera_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        return await self.get_camera(camera_id, user_id), None
    
    async def delete_camera(self, camera_id: str, user_id: str) -> bool:
        """Delete camera (soft delete by setting status to inactive)."""
        result = await self.cameras_collection.update_one(
            {"id": camera_id, "user_id": user_id},
            {"$set": {"status": CameraStatus.INACTIVE.value, "updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def increment_photo_count(self, camera_id: str):
        """Increment photo count and update last_photo_at."""
        await self.cameras_collection.update_one(
            {"id": camera_id},
            {
                "$inc": {"photo_count": 1},
                "$set": {
                    "last_photo_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )


# ============================================
# EXIF READER SERVICE
# ============================================

class ExifReaderService:
    """
    Service for extracting EXIF metadata from images.
    Phase 1: Minimal extraction (timestamp, GPS if available).
    """
    
    @staticmethod
    def extract_exif(image_data: bytes) -> dict:
        """
        Extract minimal EXIF data from image bytes.
        
        In Phase 1, we do basic extraction. Full EXIF parsing
        will be enhanced in later phases.
        """
        exif_data = {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(image_data),
            "timestamp": None,
            "gps_lat": None,
            "gps_lon": None,
            "camera_make": None,
            "camera_model": None
        }
        
        if len(image_data) == 0:
            return exif_data
        
        try:
            # Try to import PIL for EXIF extraction
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            import io
            
            img = Image.open(io.BytesIO(image_data))
            
            # Check if image format supports EXIF (JPEG, TIFF)
            if not hasattr(img, '_getexif') or img._getexif is None:
                # Image format doesn't support EXIF (GIF, PNG, etc.)
                logger.debug(f"Image format {img.format} does not support EXIF extraction")
                return exif_data
            
            exif_raw = img._getexif()
            
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    if tag == "DateTimeOriginal":
                        try:
                            exif_data["timestamp"] = datetime.strptime(
                                value, "%Y:%m:%d %H:%M:%S"
                            ).isoformat()
                        except:
                            pass
                    elif tag == "Make":
                        exif_data["camera_make"] = value
                    elif tag == "Model":
                        exif_data["camera_model"] = value
                    elif tag == "GPSInfo":
                        # Parse GPS data
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        
                        # Convert GPS to decimal
                        if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                            try:
                                lat = ExifReaderService._convert_gps_to_decimal(
                                    gps_data["GPSLatitude"],
                                    gps_data.get("GPSLatitudeRef", "N")
                                )
                                lon = ExifReaderService._convert_gps_to_decimal(
                                    gps_data["GPSLongitude"],
                                    gps_data.get("GPSLongitudeRef", "W")
                                )
                                exif_data["gps_lat"] = lat
                                exif_data["gps_lon"] = lon
                            except:
                                pass
        except ImportError:
            logger.warning("PIL not available for EXIF extraction")
        except Exception as e:
            logger.debug(f"EXIF extraction skipped: {e}")
        
        return exif_data
    
    @staticmethod
    def _convert_gps_to_decimal(coords, ref: str) -> float:
        """Convert GPS coordinates from DMS to decimal."""
        try:
            degrees = float(coords[0])
            minutes = float(coords[1])
            seconds = float(coords[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref in ["S", "W"]:
                decimal = -decimal
            
            return decimal
        except:
            return None


# ============================================
# IMAGE ENCRYPTION SERVICE
# ============================================

class ImageEncryptionService:
    """
    Service for encrypting and storing camera images.
    Phase 1: Basic encryption using Fernet (symmetric).
    """
    
    def __init__(self):
        # In production, use proper key derivation
        self.key = self._derive_key(ENCRYPTION_KEY)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"huntiq_camera_salt_v1",  # In production, use unique salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_image(self, image_data: bytes) -> bytes:
        """Encrypt image data."""
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.encrypt(image_data)
    
    def decrypt_image(self, encrypted_data: bytes) -> bytes:
        """Decrypt image data."""
        from cryptography.fernet import Fernet
        f = Fernet(self.key)
        return f.decrypt(encrypted_data)


# ============================================
# EMAIL INGESTION SERVICE
# ============================================

class EmailIngestionService:
    """
    Service for processing incoming photos via email.
    
    RÈGLE FONDAMENTALE: N'ingérer AUCUNE photo si la caméra n'a pas de waypoint.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.events_collection = db['camera_events']
        self.logs_collection = db['camera_ingestion_logs']
        self.camera_service = CameraRegistryService(db)
        self.exif_service = ExifReaderService()
        self.encryption_service = ImageEncryptionService()
    
    async def _log_ingestion(
        self,
        email_alias: str,
        from_email: str,
        status: EmailIngestionStatus,
        message: str,
        camera_id: Optional[str] = None,
        event_id: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log ingestion attempt."""
        log = IngestionLog(
            camera_id=camera_id,
            email_alias=email_alias,
            from_email=from_email,
            status=status,
            message=message,
            event_id=event_id,
            error_details=error_details,
            created_at=datetime.now(timezone.utc)
        )
        await self.logs_collection.insert_one(log.model_dump())
    
    async def process_email(self, request: EmailIngestionRequest) -> EmailIngestionResponse:
        """
        Process incoming email with photo attachments.
        
        RÈGLE: Rejeter si caméra non trouvée ou sans waypoint.
        """
        # Extract email alias from to_email
        to_email = request.to_email.lower().strip()
        email_alias = to_email.split("@")[0] + "@" + EMAIL_DOMAIN if "@" in to_email else to_email
        
        # Find camera by email alias
        camera = await self.camera_service.get_camera_by_email_alias(to_email)
        
        if not camera:
            # Try with constructed email_alias
            camera = await self.camera_service.get_camera_by_email_alias(email_alias)
        
        if not camera:
            await self._log_ingestion(
                email_alias=to_email,
                from_email=request.from_email,
                status=EmailIngestionStatus.FAILED,
                message="Caméra non trouvée pour cet alias email"
            )
            return EmailIngestionResponse(
                status=EmailIngestionStatus.FAILED,
                message="REJET: Aucune caméra associée à cette adresse email"
            )
        
        # RÈGLE ABSOLUE: Vérifier que la caméra a un waypoint
        if not camera.waypoint_id:
            await self._log_ingestion(
                email_alias=to_email,
                from_email=request.from_email,
                status=EmailIngestionStatus.FAILED,
                message="Caméra sans waypoint - ingestion interdite",
                camera_id=camera.id
            )
            return EmailIngestionResponse(
                status=EmailIngestionStatus.FAILED,
                message="REJET: La caméra n'a pas de waypoint associé - ingestion impossible",
                camera_id=camera.id
            )
        
        # Check for image attachments
        image_attachments = [
            att for att in request.attachments
            if att.get("content_type", "").startswith("image/")
        ]
        
        if not image_attachments:
            await self._log_ingestion(
                email_alias=to_email,
                from_email=request.from_email,
                status=EmailIngestionStatus.FAILED,
                message="Aucune image trouvée dans l'email",
                camera_id=camera.id
            )
            return EmailIngestionResponse(
                status=EmailIngestionStatus.FAILED,
                message="REJET: Aucune image jointe à l'email",
                camera_id=camera.id
            )
        
        # Process first image (in Phase 1, we process one image per email)
        attachment = image_attachments[0]
        
        try:
            # Decode image data
            image_data = base64.b64decode(attachment.get("data", ""))
            
            if len(image_data) == 0:
                raise ValueError("Image data is empty")
            
            # Extract EXIF
            exif_data = self.exif_service.extract_exif(image_data)
            
            # Encrypt and store image
            encrypted_data = self.encryption_service.encrypt_image(image_data)
            
            # Generate storage path
            event_id = str(uuid.uuid4())
            storage_path = f"/app/backend/uploads/photos/{camera.user_id}/{camera.id}/{event_id}.enc"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Write encrypted image
            with open(storage_path, "wb") as f:
                f.write(encrypted_data)
            
            # Determine timestamp
            if exif_data.get("timestamp"):
                try:
                    timestamp = datetime.fromisoformat(exif_data["timestamp"])
                except:
                    timestamp = datetime.now(timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)
            
            # Create camera event
            event = CameraEvent(
                id=event_id,
                user_id=camera.user_id,
                camera_id=camera.id,
                waypoint_id=camera.waypoint_id,
                timestamp=timestamp,
                raw_image_url=storage_path,
                exif_data=exif_data,
                created_at=datetime.now(timezone.utc)
            )
            
            await self.events_collection.insert_one(event.model_dump())
            
            # Update camera photo count
            await self.camera_service.increment_photo_count(camera.id)
            
            await self._log_ingestion(
                email_alias=to_email,
                from_email=request.from_email,
                status=EmailIngestionStatus.SUCCESS,
                message="Photo ingérée avec succès",
                camera_id=camera.id,
                event_id=event_id
            )
            
            logger.info(f"Email ingestion success: event {event_id} for camera {camera.id}")
            
            return EmailIngestionResponse(
                status=EmailIngestionStatus.SUCCESS,
                message="Photo ingérée et événement créé avec succès",
                event_id=event_id,
                camera_id=camera.id
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Email ingestion error: {error_msg}")
            
            await self._log_ingestion(
                email_alias=to_email,
                from_email=request.from_email,
                status=EmailIngestionStatus.QUARANTINED,
                message="Erreur lors du traitement de l'image",
                camera_id=camera.id,
                error_details=error_msg
            )
            
            return EmailIngestionResponse(
                status=EmailIngestionStatus.QUARANTINED,
                message="L'image a été mise en quarantaine suite à une erreur de traitement",
                camera_id=camera.id,
                quarantine_reason=error_msg
            )
    
    async def get_events(
        self,
        user_id: str,
        camera_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[CameraEvent], int]:
        """Get camera events for user."""
        query = {"user_id": user_id, "is_quarantined": False}
        if camera_id:
            query["camera_id"] = camera_id
        
        cursor = self.events_collection.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        events = [CameraEvent(**doc) async for doc in cursor]
        total = await self.events_collection.count_documents(query)
        
        return events, total
    
    async def get_event(self, event_id: str, user_id: str) -> Optional[CameraEvent]:
        """Get single event by ID."""
        doc = await self.events_collection.find_one(
            {"id": event_id, "user_id": user_id},
            {"_id": 0}
        )
        return CameraEvent(**doc) if doc else None
    
    async def get_ingestion_logs(
        self,
        user_id: str,
        camera_id: Optional[str] = None,
        limit: int = 100
    ) -> List[IngestionLog]:
        """Get ingestion logs for user's cameras."""
        # Get all camera IDs for user
        cameras, _ = await self.camera_service.list_cameras(user_id, limit=1000)
        camera_ids = [c.id for c in cameras]
        
        if not camera_ids:
            return []
        
        query = {"camera_id": {"$in": camera_ids}}
        if camera_id:
            query["camera_id"] = camera_id
        
        cursor = self.logs_collection.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        
        return [IngestionLog(**doc) async for doc in cursor]
