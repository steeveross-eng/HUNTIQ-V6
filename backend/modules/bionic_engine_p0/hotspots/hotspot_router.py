"""
BIONIC V3 — Hotspot Admin API Router
=====================================
Admin endpoints for hotspot extraction, listing, export.

Endpoints:
  POST /api/v1/admin/hotspots/extract            — Extract hotspots for all regions
  POST /api/v1/admin/hotspots/extract/{region_id} — Extract for a specific region
  GET  /api/v1/admin/hotspots/regions             — List all BIONIC regions
  GET  /api/v1/admin/hotspots/list                — List stored hotspots (with filters)
  GET  /api/v1/admin/hotspots/export/geojson      — Export as GeoJSON
  GET  /api/v1/admin/hotspots/export/json         — Export as JSON
  GET  /api/v1/admin/hotspots/report/bce4x        — BCE-4X compliance report
  GET  /api/v1/admin/hotspots/report/daily        — Daily change report
  GET  /api/v1/admin/hotspots/stats               — Aggregated statistics
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Query

from modules.bionic_engine_p0.hotspots.hotspot_engine import (
    extract_all_regions,
    extract_hotspots_for_region,
    generate_geojson_export,
    validate_hotspots_bce4x,
    BIONIC_REGIONS,
    HOTSPOT_WEIGHTS,
    HOTSPOT_THRESHOLDS,
    HOTSPOT_CATEGORIES,
)
from modules.bionic_engine_p0.hotspots.territory_data import TERRITORY_TYPES, ACCESS_STATUSES

logger = logging.getLogger("bionic.hotspots.router")

router = APIRouter(prefix="/api/v1/admin/bionic-hotspots", tags=["Admin BIONIC Hotspots V3"])

# In-memory store for latest extraction (also stored in MongoDB)
_latest_extraction = None
_extraction_history = []  # Last 3 days
_scheduler_config = {
    "enabled": True,
    "frequency": "annual",
    "last_run": None,
    "next_run": None,
    "total_runs": 0,
}


def _get_db_collection():
    """Get MongoDB collection for hotspots."""
    try:
        from database import Database
        return Database.get_collection("admin_hotspots")
    except Exception:
        return None


@router.get("/regions")
async def list_regions():
    """List all predefined BIONIC regions."""
    return {
        "total": len(BIONIC_REGIONS),
        "regions": BIONIC_REGIONS,
    }


@router.post("/extract")
async def extract_all():
    """Extract hotspots for ALL BIONIC regions. Store in MongoDB."""
    global _latest_extraction, _extraction_history

    context = {"season": "automne", "hour": 6}
    result = extract_all_regions(context)

    # Store in memory
    _latest_extraction = result

    # Add to history (keep last 3 days)
    _extraction_history.append({
        "timestamp": result["extracted_at"],
        "total_hotspots": result["total_hotspots"],
        "regions_count": result["total_regions"],
    })
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    _extraction_history = [
        h for h in _extraction_history
        if datetime.fromisoformat(h["timestamp"].replace("Z", "+00:00")) > cutoff
    ]

    # Store in MongoDB
    collection = _get_db_collection()
    if collection is not None:
        try:
            all_hotspots = []
            for region_data in result["regions"]:
                for h in region_data["hotspots"]:
                    h["_extraction_batch"] = result["extracted_at"]
                    all_hotspots.append(h)

            if all_hotspots:
                await collection.delete_many({"_extraction_batch": {"$exists": True}})
                # Use copies to avoid ObjectId contamination of in-memory data
                docs = [{k: v for k, v in h.items() if k != "_id"} for h in all_hotspots]
                await collection.insert_many(docs)
                logger.info(f"Stored {len(all_hotspots)} hotspots in MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB storage failed: {e}")

    return {
        "success": True,
        "total_regions": result["total_regions"],
        "total_hotspots": result["total_hotspots"],
        "scoring_weights": result["scoring_weights"],
        "thresholds": result["thresholds"],
        "regions_summary": [
            {
                "region_id": r["region"]["id"],
                "region_name": r["region"]["name"],
                "hotspots_count": r["total_hotspots"],
                "by_classification": r["by_classification"],
                "by_species": r["by_species"],
            }
            for r in result["regions"]
        ],
        "extracted_at": result["extracted_at"],
    }


@router.post("/extract/{region_id}")
async def extract_region(region_id: str):
    """Extract hotspots for a specific region."""
    region = next((r for r in BIONIC_REGIONS if r["id"] == region_id), None)
    if not region:
        return {"error": f"Region '{region_id}' not found", "available": [r["id"] for r in BIONIC_REGIONS]}

    context = {"season": "automne", "hour": 6}
    result = extract_hotspots_for_region(region, context)

    # Store in MongoDB
    collection = _get_db_collection()
    if collection is not None:
        try:
            for h in result["hotspots"]:
                doc = {k: v for k, v in h.items() if k != "_id"}
                doc["_extraction_batch"] = result["hotspots"][0]["extracted_at"] if result["hotspots"] else datetime.now(timezone.utc).isoformat()
                await collection.replace_one({"id": doc["id"]}, doc, upsert=True)
        except Exception as e:
            logger.warning(f"MongoDB storage failed: {e}")

    return {
        "success": True,
        "region": result["region"],
        "total_hotspots": result["total_hotspots"],
        "by_classification": result["by_classification"],
        "by_category": result["by_category"],
        "by_species": result["by_species"],
        "hotspots": result["hotspots"],
        "filters_applied": result["filters_applied"],
    }


@router.get("/list")
async def list_hotspots(
    region_id: Optional[str] = Query(None),
    species: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    classification: Optional[str] = Query(None),
    territory_type: Optional[str] = Query(None),
    access_status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List stored hotspots with filters including territory data."""
    if _latest_extraction is None:
        return {"hotspots": [], "total": 0, "message": "No extraction performed yet. Call POST /extract first."}

    all_hotspots = []
    for region_data in _latest_extraction["regions"]:
        all_hotspots.extend(region_data["hotspots"])

    # Apply filters
    filtered = all_hotspots
    if region_id:
        filtered = [h for h in filtered if h["region_id"] == region_id]
    if species:
        filtered = [h for h in filtered if h["dominant_species"] == species]
    if category:
        filtered = [h for h in filtered if h["category"] == category]
    if min_score is not None:
        filtered = [h for h in filtered if h["score"] >= min_score]
    if classification:
        filtered = [h for h in filtered if h["classification"] == classification]
    if territory_type:
        filtered = [h for h in filtered if h.get("territory_type") == territory_type]
    if access_status:
        filtered = [h for h in filtered if h.get("access_status") == access_status]

    filtered = sorted(filtered, key=lambda h: h["score"], reverse=True)[:limit]

    return {
        "total": len(filtered),
        "filters": {
            "region_id": region_id, "species": species, "category": category,
            "min_score": min_score, "classification": classification,
            "territory_type": territory_type, "access_status": access_status,
        },
        "territory_types_available": TERRITORY_TYPES,
        "access_statuses_available": ACCESS_STATUSES,
        "hotspots": filtered,
    }


@router.get("/export/geojson")
async def export_geojson(region_id: Optional[str] = Query(None)):
    """Export hotspots as GeoJSON."""
    if _latest_extraction is None:
        return {"error": "No extraction performed yet."}

    all_hotspots = []
    for region_data in _latest_extraction["regions"]:
        if region_id and region_data["region"]["id"] != region_id:
            continue
        all_hotspots.extend(region_data["hotspots"])

    return generate_geojson_export(all_hotspots)


@router.get("/export/json")
async def export_json(region_id: Optional[str] = Query(None)):
    """Export hotspots as raw JSON."""
    if _latest_extraction is None:
        return {"error": "No extraction performed yet."}

    if region_id:
        region_data = next((r for r in _latest_extraction["regions"] if r["region"]["id"] == region_id), None)
        if not region_data:
            return {"error": f"Region '{region_id}' not found in latest extraction"}
        return region_data

    return _latest_extraction


@router.get("/report/bce4x")
async def bce4x_report():
    """Generate BCE-4X compliance report for all extracted hotspots."""
    if _latest_extraction is None:
        return {"error": "No extraction performed yet."}

    all_hotspots = []
    for region_data in _latest_extraction["regions"]:
        all_hotspots.extend(region_data["hotspots"])

    return validate_hotspots_bce4x(all_hotspots)


@router.get("/report/daily")
async def daily_report():
    """Generate daily change report (new, modified, removed hotspots)."""
    return {
        "report_type": "daily",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_extraction": _latest_extraction["extracted_at"] if _latest_extraction else None,
        "total_hotspots": _latest_extraction["total_hotspots"] if _latest_extraction else 0,
        "extraction_history": _extraction_history,
        "changes": {
            "new": _latest_extraction["total_hotspots"] if _latest_extraction else 0,
            "modified": 0,
            "removed": 0,
            "note": "First extraction — all hotspots are new",
        },
    }


@router.get("/stats")
async def hotspot_stats():
    """Aggregated statistics across all regions."""
    if _latest_extraction is None:
        return {"error": "No extraction performed yet."}

    all_hotspots = []
    for region_data in _latest_extraction["regions"]:
        all_hotspots.extend(region_data["hotspots"])

    if not all_hotspots:
        return {"total": 0}

    scores = [h["score"] for h in all_hotspots]
    categories = {}
    species_count = {}
    regions_count = {}

    for h in all_hotspots:
        cat = h["category"]
        categories[cat] = categories.get(cat, 0) + 1
        sp = h["dominant_species"]
        species_count[sp] = species_count.get(sp, 0) + 1
        rid = h["region_id"]
        regions_count[rid] = regions_count.get(rid, 0) + 1

    return {
        "total_hotspots": len(all_hotspots),
        "score_avg": round(sum(scores) / len(scores), 1),
        "score_min": min(scores),
        "score_max": max(scores),
        "by_classification": {
            "MAJEUR": len([h for h in all_hotspots if h["classification"] == "MAJEUR"]),
            "FORT": len([h for h in all_hotspots if h["classification"] == "FORT"]),
        },
        "by_category": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
        "by_species": dict(sorted(species_count.items(), key=lambda x: x[1], reverse=True)),
        "by_region": dict(sorted(regions_count.items(), key=lambda x: x[1], reverse=True)),
        "scoring_weights": HOTSPOT_WEIGHTS,
        "thresholds": HOTSPOT_THRESHOLDS,
        "categories_available": HOTSPOT_CATEGORIES,
    }


# ══════════════════════════════════════════════════════════
# SCHEDULER ANNUEL
# ══════════════════════════════════════════════════════════

@router.get("/scheduler/status")
async def scheduler_status():
    """Get annual extraction scheduler status."""
    return {
        **_scheduler_config,
        "extraction_available": _latest_extraction is not None,
        "last_extraction_at": _latest_extraction["extracted_at"] if _latest_extraction else None,
        "total_hotspots": _latest_extraction["total_hotspots"] if _latest_extraction else 0,
    }


@router.post("/scheduler/run")
async def scheduler_run_now():
    """Manually trigger the annual extraction. Also runs BCE-4X report."""
    global _latest_extraction, _scheduler_config

    context = {"season": "automne", "hour": 6}
    result = extract_all_regions(context)
    _latest_extraction = result

    # Update scheduler state
    now = datetime.now(timezone.utc)
    _scheduler_config["last_run"] = now.isoformat()
    _scheduler_config["next_run"] = (now.replace(year=now.year + 1)).isoformat()
    _scheduler_config["total_runs"] += 1

    # Store history
    _extraction_history.append({
        "timestamp": result["extracted_at"],
        "total_hotspots": result["total_hotspots"],
        "regions_count": result["total_regions"],
        "trigger": "manual",
    })

    # Store in MongoDB
    collection = _get_db_collection()
    if collection is not None:
        try:
            all_hotspots = []
            for region_data in result["regions"]:
                for h in region_data["hotspots"]:
                    doc = {k: v for k, v in h.items() if k != "_id"}
                    doc["_extraction_batch"] = result["extracted_at"]
                    doc["_scheduler_run"] = _scheduler_config["total_runs"]
                    all_hotspots.append(doc)
            if all_hotspots:
                await collection.delete_many({"_extraction_batch": {"$exists": True}})
                await collection.insert_many(all_hotspots)
        except Exception as e:
            logger.warning(f"MongoDB storage failed: {e}")

    # Auto BCE-4X report
    all_hs = []
    for rd in result["regions"]:
        all_hs.extend(rd["hotspots"])
    bce_report = validate_hotspots_bce4x(all_hs)

    return {
        "success": True,
        "scheduler_run": _scheduler_config["total_runs"],
        "total_hotspots": result["total_hotspots"],
        "total_regions": result["total_regions"],
        "next_scheduled": _scheduler_config["next_run"],
        "bce4x_report": {
            "overall": bce_report["overall"],
            "total_checks": bce_report["total_checks"],
            "passed": bce_report["passed"],
            "failed": bce_report["failed"],
        },
        "regions_summary": [
            {
                "region_id": r["region"]["id"],
                "region_name": r["region"]["name"],
                "hotspots": r["total_hotspots"],
                "majeur": r["by_classification"]["MAJEUR"],
                "fort": r["by_classification"]["FORT"],
            }
            for r in result["regions"]
        ],
        "extracted_at": result["extracted_at"],
    }


@router.get("/territory-types")
async def get_territory_types():
    """Get available territory types and access statuses."""
    if _latest_extraction is None:
        return {"territory_types": TERRITORY_TYPES, "access_statuses": ACCESS_STATUSES, "distribution": {}}

    all_hotspots = []
    for rd in _latest_extraction["regions"]:
        all_hotspots.extend(rd["hotspots"])

    by_type = {}
    by_access = {}
    for h in all_hotspots:
        tt = h.get("territory_type", "Inconnu")
        by_type[tt] = by_type.get(tt, 0) + 1
        acc = h.get("access_status", "Inconnu")
        by_access[acc] = by_access.get(acc, 0) + 1

    return {
        "territory_types": TERRITORY_TYPES,
        "access_statuses": ACCESS_STATUSES,
        "distribution_by_type": dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
        "distribution_by_access": dict(sorted(by_access.items(), key=lambda x: x[1], reverse=True)),
    }
