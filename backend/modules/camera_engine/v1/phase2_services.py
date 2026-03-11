"""
Camera Engine - Phase 2 Services
================================

Traitement avancé des images:
- Extraction EXIF avancée (complète)
- Détection d'images invalides
- Normalisation des métadonnées

PHASE 2 UNIQUEMENT - Aucune IA, aucune analyse comportementale,
aucun corridor, aucune heatmap, aucune spatialisation.
"""
import io
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# CONSTANTES - PHASE 2
# ============================================

# Formats photographiques supportés (avec EXIF potentiel)
PHOTOGRAPHIC_FORMATS = {"JPEG", "JPG", "TIFF", "TIF", "HEIC", "HEIF", "WEBP"}

# Formats non-photographiques (sans EXIF, invalides pour caméras de chasse)
NON_PHOTOGRAPHIC_FORMATS = {"GIF", "PNG", "BMP", "ICO", "PDF", "SVG"}

# Taille minimale d'une image valide (en bytes) - images < 1KB sont suspectes
MIN_IMAGE_SIZE = 1024

# Taille maximale raisonnable (50MB)
MAX_IMAGE_SIZE = 50 * 1024 * 1024


# ============================================
# CLASSIFICATION IMAGES - PHASE 2
# ============================================

class ImageValidationStatus(str, Enum):
    """Classification simple: VALID ou INVALID"""
    VALID = "valid"
    INVALID = "invalid"


class ImageInvalidReason(str, Enum):
    """Raisons d'invalidité d'une image"""
    EMPTY = "empty"
    TOO_SMALL = "too_small"
    TOO_LARGE = "too_large"
    CORRUPTED = "corrupted"
    UNREADABLE = "unreadable"
    NON_PHOTOGRAPHIC = "non_photographic"
    NO_EXIF = "no_exif"
    UNKNOWN_FORMAT = "unknown_format"


# ============================================
# SERVICE EXIF AVANCÉ - PHASE 2
# ============================================

class AdvancedExifService:
    """
    Service d'extraction EXIF avancée (Phase 2).
    
    Extrait:
    - Timestamp complet
    - GPS complet (lat, lon, altitude, direction)
    - Orientation
    - Métadonnées appareil (make, model, software)
    - Dimensions image
    - Paramètres de prise de vue (exposure, aperture, ISO)
    """
    
    @staticmethod
    def extract_complete_exif(image_data: bytes) -> dict:
        """
        Extraction EXIF complète avec gestion robuste des erreurs.
        
        Returns:
            dict avec toutes les métadonnées EXIF extraites et normalisées
        """
        result = {
            "extraction_status": "success",
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "file_size_bytes": len(image_data),
            "image_format": None,
            "image_width": None,
            "image_height": None,
            # Timestamp
            "datetime_original": None,
            "datetime_digitized": None,
            "datetime_modified": None,
            # GPS
            "gps_latitude": None,
            "gps_longitude": None,
            "gps_altitude": None,
            "gps_altitude_ref": None,
            "gps_direction": None,
            "gps_speed": None,
            "gps_timestamp": None,
            # Orientation
            "orientation": None,
            "orientation_description": None,
            # Device
            "camera_make": None,
            "camera_model": None,
            "software": None,
            "lens_model": None,
            # Capture settings
            "exposure_time": None,
            "f_number": None,
            "iso_speed": None,
            "focal_length": None,
            "flash": None,
            "white_balance": None,
            # Raw EXIF count
            "exif_tags_count": 0,
            "has_gps": False,
            "has_timestamp": False,
            "errors": []
        }
        
        if len(image_data) == 0:
            result["extraction_status"] = "failed"
            result["errors"].append("Image data is empty")
            return result
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            img = Image.open(io.BytesIO(image_data))
            
            # Format et dimensions
            result["image_format"] = img.format
            result["image_width"] = img.width
            result["image_height"] = img.height
            
            # Vérifier si le format supporte EXIF
            if img.format and img.format.upper() not in PHOTOGRAPHIC_FORMATS:
                result["extraction_status"] = "no_exif_support"
                result["errors"].append(f"Format {img.format} does not support EXIF")
                return result
            
            # Extraire EXIF
            exif_raw = None
            try:
                if hasattr(img, '_getexif') and callable(img._getexif):
                    exif_raw = img._getexif()
            except Exception as e:
                result["errors"].append(f"EXIF access error: {str(e)}")
            
            if not exif_raw:
                result["extraction_status"] = "no_exif_data"
                result["errors"].append("No EXIF data found in image")
                return result
            
            result["exif_tags_count"] = len(exif_raw)
            
            # Parser les tags EXIF
            for tag_id, value in exif_raw.items():
                tag = TAGS.get(tag_id, str(tag_id))
                
                try:
                    # Timestamps
                    if tag == "DateTimeOriginal":
                        result["datetime_original"] = AdvancedExifService._parse_exif_datetime(value)
                        result["has_timestamp"] = True
                    elif tag == "DateTimeDigitized":
                        result["datetime_digitized"] = AdvancedExifService._parse_exif_datetime(value)
                    elif tag == "DateTime":
                        result["datetime_modified"] = AdvancedExifService._parse_exif_datetime(value)
                    
                    # Orientation
                    elif tag == "Orientation":
                        result["orientation"] = value
                        result["orientation_description"] = AdvancedExifService._get_orientation_description(value)
                    
                    # Device info
                    elif tag == "Make":
                        result["camera_make"] = AdvancedExifService._clean_string(value)
                    elif tag == "Model":
                        result["camera_model"] = AdvancedExifService._clean_string(value)
                    elif tag == "Software":
                        result["software"] = AdvancedExifService._clean_string(value)
                    elif tag == "LensModel":
                        result["lens_model"] = AdvancedExifService._clean_string(value)
                    
                    # Capture settings
                    elif tag == "ExposureTime":
                        result["exposure_time"] = AdvancedExifService._parse_rational(value)
                    elif tag == "FNumber":
                        result["f_number"] = AdvancedExifService._parse_rational(value)
                    elif tag == "ISOSpeedRatings":
                        result["iso_speed"] = value if isinstance(value, int) else (value[0] if isinstance(value, tuple) else None)
                    elif tag == "FocalLength":
                        result["focal_length"] = AdvancedExifService._parse_rational(value)
                    elif tag == "Flash":
                        result["flash"] = value
                    elif tag == "WhiteBalance":
                        result["white_balance"] = value
                    
                    # GPS
                    elif tag == "GPSInfo":
                        gps_data = AdvancedExifService._parse_gps_info(value, GPSTAGS)
                        result.update(gps_data)
                        if gps_data.get("gps_latitude") and gps_data.get("gps_longitude"):
                            result["has_gps"] = True
                            
                except Exception as e:
                    result["errors"].append(f"Error parsing tag {tag}: {str(e)}")
            
            result["extraction_status"] = "success"
            
        except ImportError:
            result["extraction_status"] = "failed"
            result["errors"].append("PIL/Pillow not available")
        except Exception as e:
            result["extraction_status"] = "failed"
            result["errors"].append(f"Extraction error: {str(e)}")
        
        return result
    
    @staticmethod
    def _parse_exif_datetime(value) -> Optional[str]:
        """Parse EXIF datetime to ISO format."""
        if not value or not isinstance(value, str):
            return None
        try:
            # Format EXIF standard: "YYYY:MM:DD HH:MM:SS"
            dt = datetime.strptime(value.strip(), "%Y:%m:%d %H:%M:%S")
            return dt.isoformat()
        except:
            return None
    
    @staticmethod
    def _clean_string(value) -> Optional[str]:
        """Clean and normalize string value."""
        if not value:
            return None
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8', errors='ignore')
            except:
                return None
        if isinstance(value, str):
            return value.strip().rstrip('\x00')
        return str(value)
    
    @staticmethod
    def _parse_rational(value) -> Optional[float]:
        """Parse EXIF rational value to float."""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                if value.denominator != 0:
                    return float(value.numerator) / float(value.denominator)
            if isinstance(value, tuple) and len(value) == 2:
                if value[1] != 0:
                    return float(value[0]) / float(value[1])
        except:
            pass
        return None
    
    @staticmethod
    def _get_orientation_description(orientation: int) -> str:
        """Get human-readable orientation description."""
        orientations = {
            1: "Normal",
            2: "Mirrored horizontal",
            3: "Rotated 180°",
            4: "Mirrored vertical",
            5: "Mirrored horizontal, rotated 270°",
            6: "Rotated 90° CW",
            7: "Mirrored horizontal, rotated 90°",
            8: "Rotated 270° CW"
        }
        return orientations.get(orientation, f"Unknown ({orientation})")
    
    @staticmethod
    def _parse_gps_info(gps_info: dict, gpstags: dict) -> dict:
        """Parse GPS info from EXIF."""
        result = {
            "gps_latitude": None,
            "gps_longitude": None,
            "gps_altitude": None,
            "gps_altitude_ref": None,
            "gps_direction": None,
            "gps_speed": None,
            "gps_timestamp": None
        }
        
        if not gps_info:
            return result
        
        # Parse GPS tags
        gps_data = {}
        for tag_id, value in gps_info.items():
            tag = gpstags.get(tag_id, str(tag_id))
            gps_data[tag] = value
        
        # Latitude
        if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
            lat = AdvancedExifService._convert_gps_coords(
                gps_data["GPSLatitude"],
                gps_data["GPSLatitudeRef"]
            )
            if lat is not None:
                result["gps_latitude"] = lat
        
        # Longitude
        if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
            lon = AdvancedExifService._convert_gps_coords(
                gps_data["GPSLongitude"],
                gps_data["GPSLongitudeRef"]
            )
            if lon is not None:
                result["gps_longitude"] = lon
        
        # Altitude
        if "GPSAltitude" in gps_data:
            result["gps_altitude"] = AdvancedExifService._parse_rational(gps_data["GPSAltitude"])
            result["gps_altitude_ref"] = gps_data.get("GPSAltitudeRef", 0)
        
        # Direction (compass)
        if "GPSImgDirection" in gps_data:
            result["gps_direction"] = AdvancedExifService._parse_rational(gps_data["GPSImgDirection"])
        
        # Speed
        if "GPSSpeed" in gps_data:
            result["gps_speed"] = AdvancedExifService._parse_rational(gps_data["GPSSpeed"])
        
        # GPS Timestamp
        if "GPSDateStamp" in gps_data and "GPSTimeStamp" in gps_data:
            try:
                date_str = gps_data["GPSDateStamp"]
                time_tuple = gps_data["GPSTimeStamp"]
                hour = int(AdvancedExifService._parse_rational(time_tuple[0]) or 0)
                minute = int(AdvancedExifService._parse_rational(time_tuple[1]) or 0)
                second = int(AdvancedExifService._parse_rational(time_tuple[2]) or 0)
                dt = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}:{second:02d}", "%Y:%m:%d %H:%M:%S")
                result["gps_timestamp"] = dt.isoformat()
            except:
                pass
        
        return result
    
    @staticmethod
    def _convert_gps_coords(coords, ref: str) -> Optional[float]:
        """Convert GPS coordinates from DMS to decimal degrees."""
        try:
            def to_float(val):
                if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                    return float(val.numerator) / float(val.denominator) if val.denominator else 0
                if isinstance(val, tuple) and len(val) == 2:
                    return float(val[0]) / float(val[1]) if val[1] else 0
                return float(val)
            
            degrees = to_float(coords[0])
            minutes = to_float(coords[1])
            seconds = to_float(coords[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref in ("S", "W"):
                decimal = -decimal
            
            return round(decimal, 8)
        except:
            return None


# ============================================
# SERVICE DÉTECTION IMAGES INVALIDES - PHASE 2
# ============================================

class ImageValidationService:
    """
    Service de détection d'images invalides (Phase 2).
    
    Classification simple: VALID / INVALID
    
    Détecte:
    - Images corrompues
    - Images sans EXIF
    - Images non photographiques (GIF, PNG, PDF, etc.)
    - Images vides ou illisibles
    """
    
    @staticmethod
    def validate_image(image_data: bytes) -> Tuple[ImageValidationStatus, Optional[ImageInvalidReason], dict]:
        """
        Valide une image et retourne son statut.
        
        Returns:
            Tuple[status, reason, details]
            - status: VALID ou INVALID
            - reason: raison d'invalidité (None si VALID)
            - details: informations détaillées
        """
        details = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "file_size_bytes": len(image_data),
            "image_format": None,
            "is_photographic": False,
            "has_exif": False,
            "is_readable": False,
            "validation_errors": []
        }
        
        # 1. Vérifier taille minimale
        if len(image_data) == 0:
            logger.info("Image validation: INVALID - empty file")
            return ImageValidationStatus.INVALID, ImageInvalidReason.EMPTY, details
        
        if len(image_data) < MIN_IMAGE_SIZE:
            details["validation_errors"].append(f"File size {len(image_data)} bytes < minimum {MIN_IMAGE_SIZE}")
            logger.info(f"Image validation: INVALID - too small ({len(image_data)} bytes)")
            return ImageValidationStatus.INVALID, ImageInvalidReason.TOO_SMALL, details
        
        if len(image_data) > MAX_IMAGE_SIZE:
            details["validation_errors"].append(f"File size {len(image_data)} bytes > maximum {MAX_IMAGE_SIZE}")
            logger.info(f"Image validation: INVALID - too large ({len(image_data)} bytes)")
            return ImageValidationStatus.INVALID, ImageInvalidReason.TOO_LARGE, details
        
        # 2. Tenter d'ouvrir l'image
        try:
            from PIL import Image
            
            img = Image.open(io.BytesIO(image_data))
            details["image_format"] = img.format
            details["is_readable"] = True
            
            # Vérifier l'intégrité en chargeant les données
            try:
                img.verify()
                # Après verify(), il faut rouvrir l'image
                img = Image.open(io.BytesIO(image_data))
                img.load()
            except Exception as e:
                details["validation_errors"].append(f"Image verification failed: {str(e)}")
                logger.info(f"Image validation: INVALID - corrupted ({e})")
                return ImageValidationStatus.INVALID, ImageInvalidReason.CORRUPTED, details
            
        except ImportError:
            details["validation_errors"].append("PIL/Pillow not available")
            logger.warning("Image validation: cannot validate - PIL not available")
            # Sans PIL, on ne peut pas valider - on accepte par défaut
            return ImageValidationStatus.VALID, None, details
        except Exception as e:
            details["validation_errors"].append(f"Cannot open image: {str(e)}")
            logger.info(f"Image validation: INVALID - unreadable ({e})")
            return ImageValidationStatus.INVALID, ImageInvalidReason.UNREADABLE, details
        
        # 3. Vérifier si format photographique
        if img.format is None:
            details["validation_errors"].append("Unknown image format")
            logger.info("Image validation: INVALID - unknown format")
            return ImageValidationStatus.INVALID, ImageInvalidReason.UNKNOWN_FORMAT, details
        
        format_upper = img.format.upper()
        
        if format_upper in NON_PHOTOGRAPHIC_FORMATS:
            details["validation_errors"].append(f"Non-photographic format: {img.format}")
            details["is_photographic"] = False
            logger.info(f"Image validation: INVALID - non-photographic format ({img.format})")
            return ImageValidationStatus.INVALID, ImageInvalidReason.NON_PHOTOGRAPHIC, details
        
        if format_upper in PHOTOGRAPHIC_FORMATS:
            details["is_photographic"] = True
        
        # 4. Vérifier présence d'EXIF (requis pour caméras de chasse)
        try:
            exif_data = None
            if hasattr(img, '_getexif') and callable(img._getexif):
                exif_data = img._getexif()
            
            if exif_data and len(exif_data) > 0:
                details["has_exif"] = True
            else:
                details["validation_errors"].append("No EXIF data found")
                logger.info("Image validation: INVALID - no EXIF data")
                return ImageValidationStatus.INVALID, ImageInvalidReason.NO_EXIF, details
                
        except Exception as e:
            details["validation_errors"].append(f"EXIF check error: {str(e)}")
            # Si on ne peut pas vérifier l'EXIF mais l'image est valide, on continue
            pass
        
        # 5. Image valide
        logger.info(f"Image validation: VALID - format={img.format}, has_exif={details['has_exif']}")
        return ImageValidationStatus.VALID, None, details


# ============================================
# SERVICE NORMALISATION MÉTADONNÉES - PHASE 2
# ============================================

class MetadataNormalizationService:
    """
    Service de normalisation des métadonnées (Phase 2).
    
    Standardise:
    - Timestamps (ISO 8601 UTC)
    - Coordonnées GPS (decimal degrees, précision 6)
    - Champs EXIF critiques (nettoyage, format uniforme)
    """
    
    @staticmethod
    def normalize_metadata(exif_data: dict) -> dict:
        """
        Normalise les métadonnées EXIF extraites.
        
        Args:
            exif_data: dictionnaire retourné par AdvancedExifService
            
        Returns:
            dict normalisé avec métadonnées standardisées
        """
        normalized = {
            "normalization_timestamp": datetime.now(timezone.utc).isoformat(),
            "normalization_applied": True,
            # Timestamp normalisé (priorité: original > digitized > modified)
            "normalized_timestamp": None,
            "timestamp_source": None,
            # GPS normalisé
            "normalized_latitude": None,
            "normalized_longitude": None,
            "normalized_altitude_m": None,
            "gps_precision": None,
            # Device normalisé
            "normalized_device": None,
            "normalized_software": None,
            # Orientation normalisée
            "normalized_orientation": None,
            "needs_rotation": False,
            "rotation_degrees": 0,
            # Capture settings normalisés
            "normalized_iso": None,
            "normalized_aperture": None,
            "normalized_shutter_speed": None,
            "normalized_focal_length_mm": None,
            # Qualité des données
            "data_quality_score": 0,
            "normalization_warnings": []
        }
        
        if not exif_data:
            normalized["normalization_warnings"].append("No EXIF data to normalize")
            return normalized
        
        # 1. Normaliser timestamp
        normalized_ts, ts_source = MetadataNormalizationService._normalize_timestamp(exif_data)
        normalized["normalized_timestamp"] = normalized_ts
        normalized["timestamp_source"] = ts_source
        
        # 2. Normaliser GPS
        gps_result = MetadataNormalizationService._normalize_gps(exif_data)
        normalized.update(gps_result)
        
        # 3. Normaliser device info
        device = MetadataNormalizationService._normalize_device(exif_data)
        normalized["normalized_device"] = device
        normalized["normalized_software"] = MetadataNormalizationService._clean_value(
            exif_data.get("software")
        )
        
        # 4. Normaliser orientation
        orientation_result = MetadataNormalizationService._normalize_orientation(exif_data)
        normalized.update(orientation_result)
        
        # 5. Normaliser capture settings
        capture = MetadataNormalizationService._normalize_capture_settings(exif_data)
        normalized.update(capture)
        
        # 6. Calculer score qualité
        normalized["data_quality_score"] = MetadataNormalizationService._calculate_quality_score(normalized)
        
        logger.info(f"Metadata normalized: quality_score={normalized['data_quality_score']}, "
                   f"has_timestamp={normalized['normalized_timestamp'] is not None}, "
                   f"has_gps={normalized['normalized_latitude'] is not None}")
        
        return normalized
    
    @staticmethod
    def _normalize_timestamp(exif_data: dict) -> Tuple[Optional[str], Optional[str]]:
        """Normalise timestamp avec priorité."""
        # Priorité: DateTimeOriginal > DateTimeDigitized > DateTime
        sources = [
            ("datetime_original", "DateTimeOriginal"),
            ("datetime_digitized", "DateTimeDigitized"),
            ("datetime_modified", "DateTime"),
            ("gps_timestamp", "GPSTimestamp")
        ]
        
        for field, source_name in sources:
            value = exif_data.get(field)
            if value:
                try:
                    # Déjà en ISO format
                    if isinstance(value, str) and "T" in value:
                        return value, source_name
                    # Parser si nécessaire
                    dt = datetime.fromisoformat(value)
                    return dt.isoformat(), source_name
                except:
                    continue
        
        return None, None
    
    @staticmethod
    def _normalize_gps(exif_data: dict) -> dict:
        """Normalise coordonnées GPS."""
        result = {
            "normalized_latitude": None,
            "normalized_longitude": None,
            "normalized_altitude_m": None,
            "gps_precision": None
        }
        
        lat = exif_data.get("gps_latitude")
        lon = exif_data.get("gps_longitude")
        
        if lat is not None and lon is not None:
            # Arrondir à 6 décimales (précision ~10cm)
            result["normalized_latitude"] = round(float(lat), 6)
            result["normalized_longitude"] = round(float(lon), 6)
            result["gps_precision"] = "standard"
            
            # Valider les coordonnées
            if not (-90 <= result["normalized_latitude"] <= 90):
                result["normalized_latitude"] = None
                result["gps_precision"] = "invalid"
            if not (-180 <= result["normalized_longitude"] <= 180):
                result["normalized_longitude"] = None
                result["gps_precision"] = "invalid"
        
        # Altitude
        alt = exif_data.get("gps_altitude")
        if alt is not None:
            try:
                alt_value = float(alt)
                # Référence: 0 = au-dessus du niveau de la mer, 1 = en-dessous
                alt_ref = exif_data.get("gps_altitude_ref", 0)
                if alt_ref == 1:
                    alt_value = -alt_value
                result["normalized_altitude_m"] = round(alt_value, 1)
            except:
                pass
        
        return result
    
    @staticmethod
    def _normalize_device(exif_data: dict) -> Optional[str]:
        """Normalise device info en une chaîne."""
        make = MetadataNormalizationService._clean_value(exif_data.get("camera_make"))
        model = MetadataNormalizationService._clean_value(exif_data.get("camera_model"))
        
        if make and model:
            # Éviter duplication (ex: "Canon Canon EOS 5D")
            if model.lower().startswith(make.lower()):
                return model
            return f"{make} {model}"
        elif model:
            return model
        elif make:
            return make
        
        return None
    
    @staticmethod
    def _normalize_orientation(exif_data: dict) -> dict:
        """Normalise orientation et calcule rotation nécessaire."""
        result = {
            "normalized_orientation": "normal",
            "needs_rotation": False,
            "rotation_degrees": 0
        }
        
        orientation = exif_data.get("orientation")
        if orientation:
            rotation_map = {
                1: (0, "normal"),
                2: (0, "mirrored"),
                3: (180, "rotated"),
                4: (180, "mirrored"),
                5: (270, "mirrored"),
                6: (90, "rotated"),
                7: (90, "mirrored"),
                8: (270, "rotated")
            }
            
            if orientation in rotation_map:
                degrees, desc = rotation_map[orientation]
                result["rotation_degrees"] = degrees
                result["normalized_orientation"] = desc
                result["needs_rotation"] = degrees != 0
        
        return result
    
    @staticmethod
    def _normalize_capture_settings(exif_data: dict) -> dict:
        """Normalise les paramètres de capture."""
        result = {
            "normalized_iso": None,
            "normalized_aperture": None,
            "normalized_shutter_speed": None,
            "normalized_focal_length_mm": None
        }
        
        # ISO
        iso = exif_data.get("iso_speed")
        if iso:
            try:
                result["normalized_iso"] = int(iso)
            except:
                pass
        
        # Aperture (f-number)
        f_number = exif_data.get("f_number")
        if f_number:
            try:
                result["normalized_aperture"] = f"f/{round(float(f_number), 1)}"
            except:
                pass
        
        # Shutter speed
        exposure = exif_data.get("exposure_time")
        if exposure:
            try:
                exp_val = float(exposure)
                if exp_val < 1:
                    # Format fraction: 1/250
                    result["normalized_shutter_speed"] = f"1/{int(round(1/exp_val))}"
                else:
                    # Format secondes
                    result["normalized_shutter_speed"] = f"{round(exp_val, 1)}s"
            except:
                pass
        
        # Focal length
        focal = exif_data.get("focal_length")
        if focal:
            try:
                result["normalized_focal_length_mm"] = round(float(focal), 1)
            except:
                pass
        
        return result
    
    @staticmethod
    def _clean_value(value) -> Optional[str]:
        """Nettoie une valeur string."""
        if value is None:
            return None
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8', errors='ignore')
            except:
                return None
        if isinstance(value, str):
            cleaned = value.strip().rstrip('\x00').strip()
            return cleaned if cleaned else None
        return str(value).strip()
    
    @staticmethod
    def _calculate_quality_score(normalized: dict) -> int:
        """
        Calcule un score de qualité des métadonnées (0-100).
        
        Critères:
        - Timestamp: 30 points
        - GPS: 30 points
        - Device: 20 points
        - Capture settings: 20 points
        """
        score = 0
        
        # Timestamp (30 points)
        if normalized.get("normalized_timestamp"):
            score += 30
        
        # GPS (30 points)
        if normalized.get("normalized_latitude") and normalized.get("normalized_longitude"):
            score += 25
            if normalized.get("normalized_altitude_m"):
                score += 5
        
        # Device (20 points)
        if normalized.get("normalized_device"):
            score += 20
        
        # Capture settings (20 points - 5 chacun)
        if normalized.get("normalized_iso"):
            score += 5
        if normalized.get("normalized_aperture"):
            score += 5
        if normalized.get("normalized_shutter_speed"):
            score += 5
        if normalized.get("normalized_focal_length_mm"):
            score += 5
        
        return score


# ============================================
# DOCUMENTATION TECHNIQUE - PHASE 2
# ============================================

PHASE2_DOCUMENTATION = """
# Camera Engine - Phase 2 Documentation Technique

## 1. Règles EXIF

### 1.1 Extraction
- Utilisation de PIL/Pillow pour l'extraction EXIF
- Support des formats: JPEG, TIFF, HEIC, HEIF, WEBP
- Fallback gracieux pour formats non supportés (GIF, PNG, BMP)

### 1.2 Tags EXIF extraits
- Timestamps: DateTimeOriginal, DateTimeDigitized, DateTime
- GPS: Latitude, Longitude, Altitude, Direction, Speed, Timestamp
- Device: Make, Model, Software, LensModel
- Orientation: Rotation nécessaire calculée
- Capture: ExposureTime, FNumber, ISO, FocalLength, Flash, WhiteBalance

### 1.3 Gestion des erreurs
- Images sans EXIF: extraction_status = "no_exif_data"
- Formats non supportés: extraction_status = "no_exif_support"
- Erreurs: liste détaillée dans "errors"

## 2. Règles de Validation

### 2.1 Classification
- VALID: Image photographique avec EXIF valide
- INVALID: Tout autre cas

### 2.2 Critères d'invalidité
- EMPTY: Fichier vide (0 bytes)
- TOO_SMALL: < 1024 bytes
- TOO_LARGE: > 50 MB
- CORRUPTED: Échec de verify() PIL
- UNREADABLE: Impossible d'ouvrir avec PIL
- NON_PHOTOGRAPHIC: Format GIF, PNG, BMP, ICO, PDF, SVG
- NO_EXIF: Pas de données EXIF
- UNKNOWN_FORMAT: Format non reconnu

### 2.3 Formats acceptés (photographiques)
- JPEG, JPG, TIFF, TIF, HEIC, HEIF, WEBP

### 2.4 Formats rejetés (non photographiques)
- GIF, PNG, BMP, ICO, PDF, SVG

## 3. Règles de Normalisation

### 3.1 Timestamps
- Format: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- Priorité: DateTimeOriginal > DateTimeDigitized > DateTime > GPSTimestamp

### 3.2 Coordonnées GPS
- Format: Decimal degrees
- Précision: 6 décimales (~10cm)
- Validation: -90 ≤ lat ≤ 90, -180 ≤ lon ≤ 180
- Altitude: en mètres, signée selon référence

### 3.3 Orientation
- Calcul automatique de la rotation nécessaire
- Valeurs: 0°, 90°, 180°, 270°

### 3.4 Score de qualité (0-100)
- Timestamp: 30 points
- GPS complet: 30 points
- Device info: 20 points
- Capture settings: 20 points
"""


def get_phase2_documentation() -> str:
    """Retourne la documentation technique Phase 2."""
    return PHASE2_DOCUMENTATION
