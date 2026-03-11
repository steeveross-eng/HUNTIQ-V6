"""
Reports API — Download and Upload analysis documents
"""
import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "memory")

AVAILABLE_REPORTS = {
    "analyse-360": {
        "filename": "ANALYSE_360_BIONIC_V5.md",
        "title": "Analyse Totale 360° — BIONIC V5",
        "description": "Analyse complète des modules MON TERRITOIRE et CARTE INTERACTIVE"
    },
    "analyse-360-absolue": {
        "filename": "ANALYSE_360_ABSOLUE_BIONIC_V5.md",
        "title": "Analyse 360° ABSOLUE — BIONIC V5 (14 Dimensions)",
        "description": "Extraction exhaustive: architecture, moteurs, scoring, especes, meteo, strategie, freemium, SEO, securite, performance"
    }
}


@router.get("/")
async def list_reports():
    """List all available reports"""
    reports = []
    for slug, meta in AVAILABLE_REPORTS.items():
        filepath = os.path.join(REPORTS_DIR, meta["filename"])
        exists = os.path.isfile(filepath)
        size = os.path.getsize(filepath) if exists else 0
        reports.append({
            "slug": slug,
            "title": meta["title"],
            "description": meta["description"],
            "filename": meta["filename"],
            "exists": exists,
            "size_bytes": size
        })
    return {"reports": reports}


@router.get("/{slug}/download")
async def download_report(slug: str):
    """Download a report file"""
    if slug not in AVAILABLE_REPORTS:
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    meta = AVAILABLE_REPORTS[slug]
    filepath = os.path.join(REPORTS_DIR, meta["filename"])

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Le fichier n'existe pas encore")

    return FileResponse(
        path=filepath,
        filename=meta["filename"],
        media_type="text/markdown"
    )


@router.get("/{slug}/content")
async def get_report_content(slug: str):
    """Get report content as text (for in-browser viewing)"""
    if slug not in AVAILABLE_REPORTS:
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    meta = AVAILABLE_REPORTS[slug]
    filepath = os.path.join(REPORTS_DIR, meta["filename"])

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Le fichier n'existe pas encore")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "slug": slug,
        "title": meta["title"],
        "filename": meta["filename"],
        "content": content
    }


@router.post("/{slug}/upload")
async def upload_report(slug: str, file: UploadFile = File(...)):
    """Upload/replace a report file"""
    if slug not in AVAILABLE_REPORTS:
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers .md sont acceptés")

    meta = AVAILABLE_REPORTS[slug]
    filepath = os.path.join(REPORTS_DIR, meta["filename"])

    # Backup existing file
    if os.path.isfile(filepath):
        backup_path = filepath + ".bak"
        shutil.copy2(filepath, backup_path)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "message": "Rapport mis à jour avec succès",
        "slug": slug,
        "filename": meta["filename"],
        "size_bytes": len(content)
    }
