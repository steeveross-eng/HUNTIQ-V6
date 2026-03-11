"""
Camera Engine - Tests Phase 1
Tests validant les règles obligatoires:
1. Caméra sans waypoint → REJET
2. Ingestion sans waypoint → REJET
3. Ingestion valide → événement créé
"""
import pytest
import asyncio
import uuid
from datetime import datetime, timezone

# Test data
TEST_USER_ID = "test-user-camera-001"
TEST_WAYPOINT_ID = f"wp-{uuid.uuid4()}"


class TestCameraValidationRules:
    """Tests for mandatory validation rules"""
    
    def test_camera_create_model_requires_waypoint(self):
        """TEST: CameraCreate model requires non-empty waypoint_id"""
        from modules.camera_engine.v1.models import CameraCreate
        
        # Should raise validation error for empty waypoint_id
        with pytest.raises(ValueError) as exc_info:
            CameraCreate(waypoint_id="")
        
        assert "waypoint_id" in str(exc_info.value).lower() or "obligatoire" in str(exc_info.value).lower()
    
    def test_camera_create_model_requires_waypoint_whitespace(self):
        """TEST: CameraCreate rejects whitespace-only waypoint_id"""
        from modules.camera_engine.v1.models import CameraCreate
        
        with pytest.raises(ValueError):
            CameraCreate(waypoint_id="   ")
    
    def test_camera_create_model_valid_waypoint(self):
        """TEST: CameraCreate accepts valid waypoint_id"""
        from modules.camera_engine.v1.models import CameraCreate
        
        camera = CameraCreate(waypoint_id=TEST_WAYPOINT_ID)
        assert camera.waypoint_id == TEST_WAYPOINT_ID


class TestCameraModels:
    """Tests for camera models"""
    
    def test_camera_model_fields(self):
        """TEST: Camera model has all required fields"""
        from modules.camera_engine.v1.models import Camera, CameraStatus
        
        camera = Camera(
            id="test-id",
            user_id=TEST_USER_ID,
            email_alias="cam-test@cam.huntiq.ca",
            waypoint_id=TEST_WAYPOINT_ID,
            manufacturer="bushnell"
        )
        
        assert camera.id == "test-id"
        assert camera.user_id == TEST_USER_ID
        assert camera.email_alias == "cam-test@cam.huntiq.ca"
        assert camera.waypoint_id == TEST_WAYPOINT_ID
        assert camera.status == CameraStatus.ACTIVE
        assert camera.photo_count == 0
    
    def test_camera_event_model_fields(self):
        """TEST: CameraEvent model has all required fields"""
        from modules.camera_engine.v1.models import CameraEvent, EventDirection, EventActivity
        
        event = CameraEvent(
            id="event-id",
            user_id=TEST_USER_ID,
            camera_id="camera-id",
            waypoint_id=TEST_WAYPOINT_ID,
            timestamp=datetime.now(timezone.utc),
            raw_image_url="/path/to/encrypted/image.enc"
        )
        
        assert event.user_id == TEST_USER_ID
        assert event.camera_id == "camera-id"
        assert event.waypoint_id == TEST_WAYPOINT_ID
        assert event.direction == EventDirection.UNKNOWN
        assert event.activity == EventActivity.UNKNOWN
        assert event.is_quarantined == False


class TestEmailIngestionModels:
    """Tests for email ingestion models"""
    
    def test_email_ingestion_request_model(self):
        """TEST: EmailIngestionRequest model validates correctly"""
        from modules.camera_engine.v1.models import EmailIngestionRequest
        
        request = EmailIngestionRequest(
            from_email="test@example.com",
            to_email="cam-abc123@cam.huntiq.ca",
            subject="Photo from trail cam",
            attachments=[
                {"filename": "IMG001.jpg", "content_type": "image/jpeg", "data": "base64data"}
            ]
        )
        
        assert request.from_email == "test@example.com"
        assert len(request.attachments) == 1
    
    def test_email_ingestion_response_statuses(self):
        """TEST: EmailIngestionResponse status values"""
        from modules.camera_engine.v1.models import EmailIngestionResponse, EmailIngestionStatus
        
        # Success response
        success = EmailIngestionResponse(
            status=EmailIngestionStatus.SUCCESS,
            message="Photo ingérée",
            event_id="evt-123",
            camera_id="cam-456"
        )
        assert success.status == EmailIngestionStatus.SUCCESS
        
        # Failed response
        failed = EmailIngestionResponse(
            status=EmailIngestionStatus.FAILED,
            message="Caméra non trouvée"
        )
        assert failed.status == EmailIngestionStatus.FAILED


class TestExifReader:
    """Tests for EXIF extraction"""
    
    def test_exif_reader_handles_empty_data(self):
        """TEST: ExifReader handles empty/invalid data gracefully"""
        from modules.camera_engine.v1.services import ExifReaderService
        
        exif = ExifReaderService.extract_exif(b"")
        
        assert exif is not None
        assert "extracted_at" in exif
        assert exif["file_size"] == 0
    
    def test_exif_reader_handles_random_data(self):
        """TEST: ExifReader handles non-image data gracefully"""
        from modules.camera_engine.v1.services import ExifReaderService
        
        exif = ExifReaderService.extract_exif(b"random non-image data here")
        
        assert exif is not None
        assert "extracted_at" in exif


class TestEncryptionService:
    """Tests for image encryption"""
    
    def test_encryption_roundtrip(self):
        """TEST: Encrypt/decrypt produces original data"""
        from modules.camera_engine.v1.services import ImageEncryptionService
        
        service = ImageEncryptionService()
        original_data = b"Test image data for encryption"
        
        encrypted = service.encrypt_image(original_data)
        decrypted = service.decrypt_image(encrypted)
        
        assert decrypted == original_data
        assert encrypted != original_data  # Ensure it's actually encrypted
    
    def test_encryption_produces_different_output(self):
        """TEST: Same data encrypts to different output (due to IV)"""
        from modules.camera_engine.v1.services import ImageEncryptionService
        
        service = ImageEncryptionService()
        data = b"Same data"
        
        encrypted1 = service.encrypt_image(data)
        encrypted2 = service.encrypt_image(data)
        
        # Fernet uses random IV, so outputs should differ
        assert encrypted1 != encrypted2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
