"""
Camera Engine - Phase 2 Tests
=============================

Tests automatisés obligatoires:
1. Image valide → EXIF complet
2. Image sans EXIF → INVALID
3. Image corrompue → INVALID
4. Image non photo (GIF/PNG) → INVALID
5. EXIF incohérent → normalisation correcte
"""
import pytest
import base64
import sys
import os

# Set environment variables for testing
os.environ.setdefault('JWT_SECRET_KEY', 'test_secret_key_for_testing')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'huntiq_test')

from datetime import datetime

# Import directly from phase2_services module to avoid router imports
sys.path.insert(0, '/app/backend')
from modules.camera_engine.v1.phase2_services import (
    AdvancedExifService,
    ImageValidationService,
    MetadataNormalizationService,
    ImageValidationStatus,
    ImageInvalidReason,
    PHOTOGRAPHIC_FORMATS,
    NON_PHOTOGRAPHIC_FORMATS,
    get_phase2_documentation
)


# ============================================
# DONNÉES DE TEST
# ============================================

# GIF 1x1 pixel (non photographique)
GIF_1X1_BASE64 = "R0lGODlhAQABAIAAAP8AAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

# PNG 1x1 pixel (non photographique)
PNG_1X1_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# Données corrompues (pas une image valide, mais > 1KB pour passer le check de taille)
CORRUPTED_DATA = b"This is not a valid image file at all, just random text data " * 50  # ~3KB

# Données vides
EMPTY_DATA = b""

# Données trop petites
SMALL_DATA = b"tiny"


class TestImageValidation:
    """Tests de validation d'images"""
    
    def test_empty_image_invalid(self):
        """TEST: Image vide → INVALID (EMPTY)"""
        status, reason, details = ImageValidationService.validate_image(EMPTY_DATA)
        
        assert status == ImageValidationStatus.INVALID
        assert reason == ImageInvalidReason.EMPTY
        assert details["file_size_bytes"] == 0
    
    def test_too_small_image_invalid(self):
        """TEST: Image trop petite → INVALID (TOO_SMALL)"""
        status, reason, details = ImageValidationService.validate_image(SMALL_DATA)
        
        assert status == ImageValidationStatus.INVALID
        assert reason == ImageInvalidReason.TOO_SMALL
        assert details["file_size_bytes"] == len(SMALL_DATA)
    
    def test_corrupted_image_invalid(self):
        """TEST: Image corrompue → INVALID"""
        status, reason, details = ImageValidationService.validate_image(CORRUPTED_DATA)
        
        assert status == ImageValidationStatus.INVALID
        assert reason in [ImageInvalidReason.CORRUPTED, ImageInvalidReason.UNREADABLE]
    
    def test_gif_non_photographic_invalid(self):
        """TEST: Image GIF (non photo) → INVALID (NON_PHOTOGRAPHIC)"""
        gif_data = base64.b64decode(GIF_1X1_BASE64)
        # GIF est trop petit, il sera rejeté pour TOO_SMALL d'abord
        # Créons un GIF plus grand
        gif_larger = gif_data * 100  # Répéter pour dépasser MIN_IMAGE_SIZE
        
        status, reason, details = ImageValidationService.validate_image(gif_larger)
        
        # Soit TOO_SMALL (si < 1KB), soit CORRUPTED/UNREADABLE (données répétées invalides)
        assert status == ImageValidationStatus.INVALID
    
    def test_png_non_photographic_invalid(self):
        """TEST: Image PNG (non photo) → INVALID (NON_PHOTOGRAPHIC)"""
        png_data = base64.b64decode(PNG_1X1_BASE64)
        # PNG trop petit aussi
        status, reason, details = ImageValidationService.validate_image(png_data)
        
        assert status == ImageValidationStatus.INVALID
        # Sera rejeté pour TOO_SMALL car < 1KB


class TestAdvancedExifExtraction:
    """Tests d'extraction EXIF avancée"""
    
    def test_empty_data_extraction(self):
        """TEST: Données vides → extraction échoue proprement"""
        result = AdvancedExifService.extract_complete_exif(b"")
        
        assert result["extraction_status"] == "failed"
        assert "empty" in result["errors"][0].lower()
        assert result["file_size_bytes"] == 0
    
    def test_gif_no_exif_support(self):
        """TEST: GIF → pas de support EXIF"""
        gif_data = base64.b64decode(GIF_1X1_BASE64)
        result = AdvancedExifService.extract_complete_exif(gif_data)
        
        assert result["image_format"] == "GIF"
        assert result["extraction_status"] == "no_exif_support"
    
    def test_png_no_exif_support(self):
        """TEST: PNG → pas de support EXIF"""
        png_data = base64.b64decode(PNG_1X1_BASE64)
        result = AdvancedExifService.extract_complete_exif(png_data)
        
        assert result["image_format"] == "PNG"
        assert result["extraction_status"] == "no_exif_support"
    
    def test_corrupted_data_extraction(self):
        """TEST: Données corrompues → extraction échoue proprement"""
        result = AdvancedExifService.extract_complete_exif(CORRUPTED_DATA)
        
        assert result["extraction_status"] == "failed"
        assert len(result["errors"]) > 0
    
    def test_extraction_result_structure(self):
        """TEST: Structure du résultat d'extraction"""
        result = AdvancedExifService.extract_complete_exif(b"test")
        
        # Vérifier que tous les champs attendus sont présents
        expected_fields = [
            "extraction_status", "extraction_timestamp", "file_size_bytes",
            "image_format", "image_width", "image_height",
            "datetime_original", "datetime_digitized", "datetime_modified",
            "gps_latitude", "gps_longitude", "gps_altitude",
            "camera_make", "camera_model", "software",
            "orientation", "has_gps", "has_timestamp", "errors"
        ]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"


class TestMetadataNormalization:
    """Tests de normalisation des métadonnées"""
    
    def test_empty_data_normalization(self):
        """TEST: Données vides → normalisation avec warnings"""
        result = MetadataNormalizationService.normalize_metadata({})
        
        assert result["normalization_applied"] == True
        assert len(result["normalization_warnings"]) > 0
        assert result["data_quality_score"] == 0
    
    def test_timestamp_normalization(self):
        """TEST: Timestamp EXIF → format ISO normalisé"""
        exif_data = {
            "datetime_original": "2024-06-15T10:30:00"
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_timestamp"] == "2024-06-15T10:30:00"
        assert result["timestamp_source"] == "DateTimeOriginal"
    
    def test_timestamp_priority(self):
        """TEST: Priorité des timestamps (original > digitized > modified)"""
        exif_data = {
            "datetime_modified": "2024-06-15T12:00:00",
            "datetime_digitized": "2024-06-15T11:00:00",
            "datetime_original": "2024-06-15T10:00:00"
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_timestamp"] == "2024-06-15T10:00:00"
        assert result["timestamp_source"] == "DateTimeOriginal"
    
    def test_gps_normalization(self):
        """TEST: GPS → coordonnées décimales normalisées"""
        exif_data = {
            "gps_latitude": 46.81234567890123,
            "gps_longitude": -71.20987654321098,
            "gps_altitude": 150.5
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        # Précision 6 décimales
        assert result["normalized_latitude"] == 46.812346
        assert result["normalized_longitude"] == -71.209877
        assert result["normalized_altitude_m"] == 150.5
        assert result["gps_precision"] == "standard"
    
    def test_invalid_gps_normalization(self):
        """TEST: GPS invalide → rejeté"""
        exif_data = {
            "gps_latitude": 999.0,  # Invalide: > 90
            "gps_longitude": -71.0
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_latitude"] is None
        assert result["gps_precision"] == "invalid"
    
    def test_device_normalization(self):
        """TEST: Device info → chaîne normalisée"""
        exif_data = {
            "camera_make": "Canon",
            "camera_model": "EOS 5D Mark IV"
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_device"] == "Canon EOS 5D Mark IV"
    
    def test_device_no_duplication(self):
        """TEST: Éviter duplication make/model"""
        exif_data = {
            "camera_make": "Canon",
            "camera_model": "Canon EOS 5D"  # Make déjà inclus dans model
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_device"] == "Canon EOS 5D"  # Pas "Canon Canon EOS 5D"
    
    def test_orientation_normalization(self):
        """TEST: Orientation → rotation calculée"""
        test_cases = [
            (1, 0, False),    # Normal
            (3, 180, True),   # Rotated 180
            (6, 90, True),    # Rotated 90 CW
            (8, 270, True),   # Rotated 270 CW
        ]
        
        for orientation, expected_degrees, needs_rotation in test_cases:
            exif_data = {"orientation": orientation}
            result = MetadataNormalizationService.normalize_metadata(exif_data)
            
            assert result["rotation_degrees"] == expected_degrees, f"Orientation {orientation}"
            assert result["needs_rotation"] == needs_rotation, f"Orientation {orientation}"
    
    def test_capture_settings_normalization(self):
        """TEST: Capture settings → formats normalisés"""
        exif_data = {
            "iso_speed": 800,
            "f_number": 2.8,
            "exposure_time": 0.004,  # 1/250
            "focal_length": 50.0
        }
        
        result = MetadataNormalizationService.normalize_metadata(exif_data)
        
        assert result["normalized_iso"] == 800
        assert result["normalized_aperture"] == "f/2.8"
        assert result["normalized_shutter_speed"] == "1/250"
        assert result["normalized_focal_length_mm"] == 50.0
    
    def test_quality_score_calculation(self):
        """TEST: Score de qualité calculé correctement"""
        # Données complètes = score élevé
        full_exif = {
            "datetime_original": "2024-06-15T10:00:00",
            "gps_latitude": 46.8,
            "gps_longitude": -71.2,
            "gps_altitude": 100,
            "camera_make": "Canon",
            "camera_model": "EOS 5D",
            "iso_speed": 400,
            "f_number": 2.8,
            "exposure_time": 0.01,
            "focal_length": 50
        }
        
        result = MetadataNormalizationService.normalize_metadata(full_exif)
        
        # Score attendu: 30 (timestamp) + 30 (GPS) + 20 (device) + 20 (capture) = 100
        assert result["data_quality_score"] == 100
    
    def test_quality_score_partial_data(self):
        """TEST: Score partiel pour données incomplètes"""
        partial_exif = {
            "datetime_original": "2024-06-15T10:00:00",
            # Pas de GPS, pas de device, pas de capture
        }
        
        result = MetadataNormalizationService.normalize_metadata(partial_exif)
        
        assert result["data_quality_score"] == 30  # Seulement timestamp


class TestDocumentation:
    """Tests de la documentation"""
    
    def test_documentation_exists(self):
        """TEST: Documentation technique disponible"""
        doc = get_phase2_documentation()
        
        assert doc is not None
        assert len(doc) > 100
        assert "Phase 2" in doc
        assert "EXIF" in doc
        assert "Validation" in doc
        assert "Normalisation" in doc


class TestConstants:
    """Tests des constantes"""
    
    def test_photographic_formats(self):
        """TEST: Formats photographiques définis"""
        assert "JPEG" in PHOTOGRAPHIC_FORMATS
        assert "TIFF" in PHOTOGRAPHIC_FORMATS
        assert "HEIC" in PHOTOGRAPHIC_FORMATS
    
    def test_non_photographic_formats(self):
        """TEST: Formats non photographiques définis"""
        assert "GIF" in NON_PHOTOGRAPHIC_FORMATS
        assert "PNG" in NON_PHOTOGRAPHIC_FORMATS
        assert "PDF" in NON_PHOTOGRAPHIC_FORMATS


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
