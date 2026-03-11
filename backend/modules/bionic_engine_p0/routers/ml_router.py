"""
ROUTER ML — Machine Learning Behavioral Engine
BIONIC V5 ULTIME 300% — PHASE H

Endpoints:
  POST /api/v1/bionic/ml/features        — Build feature vector
  POST /api/v1/bionic/ml/predictions      — Generate predictions 24h/48h/72h
  POST /api/v1/bionic/ml/training-session — Train model on multi-territory data
  GET  /api/v1/bionic/ml/schema           — Feature & target schemas
  GET  /api/v1/bionic/ml/status           — ML engine status
"""

import logging, time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.ml_router")
router = APIRouter(prefix="/api/v1/bionic/ml", tags=["BIONIC ML Engine"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class MLBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class FeatureRequest(BaseModel):
    bounds: MLBounds
    species: str
    resolution: int = Field(default=30, ge=20, le=60)


class PredictionRequest(BaseModel):
    bounds: MLBounds
    species: str
    horizons: Optional[List[str]] = None
    resolution: int = Field(default=30, ge=20, le=60)


class TrainingRequest(BaseModel):
    territories: List[MLBounds]
    species: str
    horizon: str = Field(default="24h")
    resolution: int = Field(default=30, ge=20, le=60)


@router.post("/features")
async def ml_features(request: FeatureRequest):
    """Build feature vector from full pipeline."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline
    from modules.bionic_engine_p0.services.ml_feature_builder import build_feature_vector

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    pipeline = execute_full_pipeline(bounds, request.species, request.resolution)
    features = build_feature_vector(pipeline)
    features["computation_time_ms"] = round((time.time() - start) * 1000, 1)
    return features


@router.post("/predictions")
async def ml_predictions(request: PredictionRequest):
    """Generate behavioral predictions for 24h/48h/72h."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline
    from modules.bionic_engine_p0.services.ml_feature_builder import build_feature_vector
    from modules.bionic_engine_p0.services.ml_target_builder import build_targets

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    pipeline = execute_full_pipeline(bounds, request.species, request.resolution)
    features = build_feature_vector(pipeline)
    targets = build_targets(features, request.horizons)
    targets["computation_time_ms"] = round((time.time() - start) * 1000, 1)
    return targets


@router.post("/training-session")
async def ml_training_session(request: TrainingRequest):
    """Train a prediction model on multi-territory data."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline
    from modules.bionic_engine_p0.services.ml_feature_builder import build_feature_vector
    from modules.bionic_engine_p0.services.ml_target_builder import build_targets
    from modules.bionic_engine_p0.services.ml_training_service import train_prediction_model

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    if len(request.territories) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 territoires requis pour l'entrainement")

    start = time.time()
    training_data = []
    for t in request.territories:
        bounds = {"north": t.north, "south": t.south, "east": t.east, "west": t.west}
        pipeline = execute_full_pipeline(bounds, request.species, request.resolution)
        features = build_feature_vector(pipeline)
        targets = build_targets(features, [request.horizon])
        training_data.append({
            "feature_vector": features["feature_vector"],
            "targets": targets["predictions"],
            "bounds": bounds,
        })

    result = train_prediction_model(training_data, request.species, request.horizon)
    result["total_computation_time_ms"] = round((time.time() - start) * 1000, 1)
    return result


@router.get("/schema")
async def ml_schema():
    from modules.bionic_engine_p0.services.ml_feature_builder import get_feature_schema
    from modules.bionic_engine_p0.services.ml_target_builder import get_target_schema
    return {
        "features": get_feature_schema(),
        "targets": get_target_schema(),
    }


@router.get("/status")
async def ml_status():
    return {
        "module": "ML_ENGINE",
        "label": "Behavioral Prediction Engine",
        "version": "1.0.0",
        "status": "active",
        "engine": "internal_sklearn_ridge",
        "species_supported": SUPPORTED_SPECIES,
        "endpoints": [
            "POST /api/v1/bionic/ml/features",
            "POST /api/v1/bionic/ml/predictions",
            "POST /api/v1/bionic/ml/training-session",
            "GET /api/v1/bionic/ml/schema",
            "GET /api/v1/bionic/ml/status",
        ],
        "dependencies": ["pipeline_service (10 modules)"],
        "conformity": {
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
            "fallback_available": True,
        },
    }
