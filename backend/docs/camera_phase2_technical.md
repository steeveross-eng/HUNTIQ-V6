# Camera Engine - Phase 2 Documentation Technique

## Vue d'ensemble

La Phase 2 implémente le traitement avancé des images pour le module Caméras:
- Extraction EXIF complète
- Détection d'images invalides
- Normalisation des métadonnées

## 1. Règles EXIF

### 1.1 Extraction
- Utilisation de PIL/Pillow pour l'extraction EXIF
- Support des formats: JPEG, TIFF, HEIC, HEIF, WEBP
- Fallback gracieux pour formats non supportés (GIF, PNG, BMP)

### 1.2 Tags EXIF extraits

| Catégorie | Tags |
|-----------|------|
| Timestamps | DateTimeOriginal, DateTimeDigitized, DateTime |
| GPS | Latitude, Longitude, Altitude, Direction, Speed, Timestamp |
| Device | Make, Model, Software, LensModel |
| Orientation | Rotation nécessaire calculée automatiquement |
| Capture | ExposureTime, FNumber, ISO, FocalLength, Flash, WhiteBalance |

### 1.3 Statuts d'extraction

| Statut | Description |
|--------|-------------|
| `success` | Extraction réussie avec données EXIF |
| `no_exif_data` | Image valide mais sans EXIF |
| `no_exif_support` | Format ne supportant pas EXIF (GIF, PNG) |
| `failed` | Erreur lors de l'extraction |

## 2. Règles de Validation

### 2.1 Classification binaire
- **VALID**: Image photographique avec EXIF valide
- **INVALID**: Tout autre cas

### 2.2 Critères d'invalidité

| Raison | Description |
|--------|-------------|
| `empty` | Fichier vide (0 bytes) |
| `too_small` | Fichier < 1024 bytes |
| `too_large` | Fichier > 50 MB |
| `corrupted` | Échec de verify() PIL |
| `unreadable` | Impossible d'ouvrir avec PIL |
| `non_photographic` | Format GIF, PNG, BMP, ICO, PDF, SVG |
| `no_exif` | Pas de données EXIF |
| `unknown_format` | Format non reconnu |

### 2.3 Formats acceptés (photographiques)
```
JPEG, JPG, TIFF, TIF, HEIC, HEIF, WEBP
```

### 2.4 Formats rejetés (non photographiques)
```
GIF, PNG, BMP, ICO, PDF, SVG
```

## 3. Règles de Normalisation

### 3.1 Timestamps
- **Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- **Priorité**: DateTimeOriginal > DateTimeDigitized > DateTime > GPSTimestamp

### 3.2 Coordonnées GPS
- **Format**: Decimal degrees (DD.DDDDDD)
- **Précision**: 6 décimales (~10cm)
- **Validation**: 
  - Latitude: -90 ≤ lat ≤ 90
  - Longitude: -180 ≤ lon ≤ 180
- **Altitude**: En mètres, signée selon référence

### 3.3 Orientation
Calcul automatique de la rotation nécessaire:

| EXIF | Rotation | Description |
|------|----------|-------------|
| 1 | 0° | Normal |
| 3 | 180° | Rotated 180° |
| 6 | 90° | Rotated 90° CW |
| 8 | 270° | Rotated 270° CW |

### 3.4 Score de qualité (0-100)

| Critère | Points |
|---------|--------|
| Timestamp présent | 30 |
| GPS complet (lat + lon) | 25 |
| GPS altitude | 5 |
| Device info | 20 |
| ISO | 5 |
| Aperture | 5 |
| Shutter speed | 5 |
| Focal length | 5 |

## 4. Services Phase 2

### 4.1 AdvancedExifService
```python
result = AdvancedExifService.extract_complete_exif(image_bytes)
```

### 4.2 ImageValidationService
```python
status, reason, details = ImageValidationService.validate_image(image_bytes)
# status: ImageValidationStatus.VALID ou INVALID
# reason: ImageInvalidReason ou None
```

### 4.3 MetadataNormalizationService
```python
normalized = MetadataNormalizationService.normalize_metadata(exif_data)
```

## 5. Tests Phase 2

24 tests automatisés couvrant:
- Validation images (5 tests)
- Extraction EXIF (5 tests)
- Normalisation métadonnées (11 tests)
- Documentation (1 test)
- Constantes (2 tests)

Exécution:
```bash
python -m pytest tests/test_camera_engine_phase2.py -v
```

## 6. Fichiers Phase 2

```
/app/backend/modules/camera_engine/v1/
├── phase2_services.py    # Services Phase 2
└── ...

/app/backend/tests/
└── test_camera_engine_phase2.py  # Tests Phase 2

/app/backend/docs/
└── camera_phase2_technical.md  # Cette documentation
```
