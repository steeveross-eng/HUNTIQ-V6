"""
BIONIC V5 — IMPORT SERVICE (Calibration MASTER)
==================================================
Service d'importation en lot de données terrain.

FORMATS SUPPORTÉS:
- CSV (.csv) avec délimiteurs: virgule, point-virgule, tabulation
- Excel (.xlsx, .xls) via openpyxl

COLONNES REQUISES:
- latitude (float, -90 à 90)
- longitude (float, -180 à 180)
- species (str)
- observed_behavior (str)
- observation_datetime (ISO 8601 ou formats courants)

COLONNES OPTIONNELLES:
- region, notes, confidence, observer_id, weather_conditions

SÉCURITÉ:
- Validation stricte de chaque ligne
- Taille maximale du fichier: 10 MB
- Limite de lignes: 5000 par import
- Parsing sécurisé (pas d'exécution de code)

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

import csv
import io
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid

logger = logging.getLogger("bionic_import_service")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ROWS = 5000

# Colonnes requises et optionnelles
REQUIRED_COLUMNS = {"latitude", "longitude", "species", "observed_behavior", "observation_datetime"}
OPTIONAL_COLUMNS = {"region", "notes", "confidence", "observer_id"}

# Mappings de noms alternatifs
COLUMN_ALIASES = {
    "lat": "latitude",
    "lng": "longitude",
    "lon": "longitude",
    "long": "longitude",
    "espece": "species",
    "espèce": "species",
    "comportement": "observed_behavior",
    "behavior": "observed_behavior",
    "behaviour": "observed_behavior",
    "date": "observation_datetime",
    "datetime": "observation_datetime",
    "date_observation": "observation_datetime",
    "date_heure": "observation_datetime",
    "région": "region",
    "confiance": "confidence",
    "observateur": "observer_id",
    "observer": "observer_id",
}

VALID_SPECIES = {
    "orignal", "cerf_de_virginie", "ours_noir", "caribou", "wapiti",
    "cerf de virginie", "ours noir"
}

VALID_BEHAVIORS = {
    "alimentation", "déplacement", "deplacement", "repos", "rut",
    "allaitement", "fuite", "abreuvement", "ravage",
    "feeding", "movement", "resting", "nursing", "flight"
}

BEHAVIOR_NORMALIZE = {
    "feeding": "alimentation",
    "movement": "déplacement",
    "deplacement": "déplacement",
    "resting": "repos",
    "nursing": "allaitement",
    "flight": "fuite",
}

SPECIES_NORMALIZE = {
    "cerf de virginie": "cerf_de_virginie",
    "ours noir": "ours_noir",
}


def _normalize_column_name(name: str) -> str:
    """Normalise un nom de colonne."""
    clean = name.strip().lower().replace(" ", "_").replace("-", "_")
    return COLUMN_ALIASES.get(clean, clean)


def _parse_datetime(value: str) -> Optional[str]:
    """Parse une date/heure en ISO 8601."""
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    ]
    val = str(value).strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(val, fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        return None


def _validate_row(row: Dict[str, str], row_num: int) -> Tuple[Optional[Dict], Optional[str]]:
    """Valide et normalise une ligne de données."""
    errors = []

    # Latitude
    try:
        lat = float(row.get("latitude", ""))
        if not -90 <= lat <= 90:
            errors.append("latitude hors limites (-90, 90)")
    except (ValueError, TypeError):
        errors.append("latitude invalide")
        lat = None

    # Longitude
    try:
        lng = float(row.get("longitude", ""))
        if not -180 <= lng <= 180:
            errors.append("longitude hors limites (-180, 180)")
    except (ValueError, TypeError):
        errors.append("longitude invalide")
        lng = None

    # Species
    species = str(row.get("species", "")).strip().lower()
    species = SPECIES_NORMALIZE.get(species, species)
    if not species:
        errors.append("espèce manquante")

    # Behavior
    behavior = str(row.get("observed_behavior", "")).strip().lower()
    behavior = BEHAVIOR_NORMALIZE.get(behavior, behavior)
    if not behavior:
        errors.append("comportement manquant")

    # Datetime
    dt_raw = str(row.get("observation_datetime", "")).strip()
    dt_parsed = _parse_datetime(dt_raw) if dt_raw else None
    if not dt_parsed:
        errors.append(f"date invalide: '{dt_raw}'")

    # Confidence
    confidence = 0.8
    conf_raw = row.get("confidence", "")
    if conf_raw:
        try:
            confidence = float(conf_raw)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            pass

    if errors:
        return None, f"Ligne {row_num}: {'; '.join(errors)}"

    return {
        "latitude": lat,
        "longitude": lng,
        "species": species,
        "observed_behavior": behavior,
        "observation_datetime": dt_parsed,
        "region": str(row.get("region", "CA-QC")).strip() or "CA-QC",
        "notes": str(row.get("notes", "")).strip(),
        "confidence": confidence,
        "observer_id": str(row.get("observer_id", "import_csv")).strip() or "import_csv",
    }, None


def parse_csv_content(content: bytes, filename: str) -> Tuple[List[Dict], List[str]]:
    """Parse un fichier CSV et retourne les observations validées + erreurs."""
    text = content.decode("utf-8-sig", errors="replace")

    # Détecter le délimiteur
    sample = text[:2000]
    delimiter = ","
    if sample.count(";") > sample.count(","):
        delimiter = ";"
    elif sample.count("\t") > sample.count(","):
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    # Normaliser les noms de colonnes
    if reader.fieldnames:
        normalized_fields = [_normalize_column_name(f) for f in reader.fieldnames]
        reader.fieldnames = normalized_fields

    # Vérifier les colonnes requises
    if reader.fieldnames:
        found = set(reader.fieldnames)
        missing = REQUIRED_COLUMNS - found
        if missing:
            return [], [f"Colonnes manquantes: {', '.join(missing)}. Trouvées: {', '.join(found)}"]

    valid_rows = []
    errors = []

    for i, row in enumerate(reader, start=2):
        if i > MAX_ROWS + 1:
            errors.append(f"Limite de {MAX_ROWS} lignes atteinte, lignes restantes ignorées")
            break

        parsed, error = _validate_row(row, i)
        if error:
            errors.append(error)
        elif parsed:
            valid_rows.append(parsed)

    return valid_rows, errors


def parse_excel_content(content: bytes, filename: str) -> Tuple[List[Dict], List[str]]:
    """Parse un fichier Excel et retourne les observations validées + erreurs."""
    try:
        import openpyxl
    except ImportError:
        return [], ["openpyxl non installé — import Excel impossible"]

    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
    except Exception as e:
        return [], [f"Erreur de lecture du fichier Excel: {str(e)}"]

    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return [], ["Fichier vide ou sans données"]

    # Normaliser les en-têtes
    headers = [_normalize_column_name(str(h or "")) for h in rows[0]]

    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        return [], [f"Colonnes manquantes: {', '.join(missing)}. Trouvées: {', '.join(headers)}"]

    valid_rows = []
    errors = []

    for i, row_values in enumerate(rows[1:], start=2):
        if i > MAX_ROWS + 1:
            errors.append(f"Limite de {MAX_ROWS} lignes atteinte")
            break

        row = {headers[j]: str(v) if v is not None else "" for j, v in enumerate(row_values) if j < len(headers)}
        parsed, error = _validate_row(row, i)
        if error:
            errors.append(error)
        elif parsed:
            valid_rows.append(parsed)

    wb.close()
    return valid_rows, errors


async def import_observations_from_file(
    db,
    content: bytes,
    filename: str,
    source_label: str = "import_file"
) -> Dict[str, Any]:
    """
    Pipeline complet d'import de fichier.
    
    1. Détecte le format (CSV/Excel)
    2. Parse et valide chaque ligne
    3. Bulk insert dans MongoDB
    4. Retourne un rapport détaillé
    """
    from modules.bionic_engine_p0.services.calibration_service import create_observation_doc

    # Vérifier la taille
    if len(content) > MAX_FILE_SIZE:
        return {
            "status": "error",
            "message": f"Fichier trop volumineux ({len(content)} bytes > {MAX_FILE_SIZE} max)",
            "imported": 0,
            "errors": []
        }

    # Détecter le format
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext in ("xlsx", "xls"):
        valid_rows, parse_errors = parse_excel_content(content, filename)
    elif ext == "csv":
        valid_rows, parse_errors = parse_csv_content(content, filename)
    else:
        return {
            "status": "error",
            "message": f"Format non supporté: .{ext}. Formats acceptés: .csv, .xlsx",
            "imported": 0,
            "errors": []
        }

    if not valid_rows and parse_errors:
        return {
            "status": "error",
            "message": "Aucune ligne valide trouvée",
            "imported": 0,
            "errors": parse_errors[:50],
            "total_rows_parsed": 0
        }

    # Générer un batch ID pour traçabilité
    batch_id = f"BATCH-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    source_ids = [f"SRC-IMPORT-{batch_id}", f"SRC-FILE-{filename}"]

    # Créer les documents
    docs = []
    for row in valid_rows:
        doc = create_observation_doc(
            latitude=row["latitude"],
            longitude=row["longitude"],
            species=row["species"],
            observed_behavior=row["observed_behavior"],
            observation_datetime=row["observation_datetime"],
            region=row["region"],
            notes=row["notes"],
            confidence=row["confidence"],
            observer_id=row["observer_id"],
            source_ids=source_ids
        )
        docs.append(doc)

    # Bulk insert
    inserted = 0
    if docs:
        result = await db.bionic_calibration_observations.insert_many(docs)
        inserted = len(result.inserted_ids)

    logger.info(f"Import batch {batch_id}: {inserted}/{len(valid_rows)} inserted from {filename}")

    return {
        "status": "success",
        "batch_id": batch_id,
        "filename": filename,
        "format": ext,
        "imported": inserted,
        "total_rows_parsed": len(valid_rows) + len(parse_errors),
        "valid_rows": len(valid_rows),
        "errors_count": len(parse_errors),
        "errors": parse_errors[:50],
        "source_ids": source_ids,
        "version": "1.0.0"
    }
