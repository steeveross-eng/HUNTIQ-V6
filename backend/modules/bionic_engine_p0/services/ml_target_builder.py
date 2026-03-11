"""
SERVICE ML — Target Builder
BIONIC V5 ULTIME 300% — PHASE H

Genere les cibles comportementales pour l'apprentissage ML.
Cibles: presence, deplacement, micro-patterns, pression.
Horizons: 24h, 48h, 72h.
"""

import logging
import hashlib
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger("bionic_engine.ml_target_builder")

TARGET_SCHEMA = [
    "presence_probability",
    "movement_intensity",
    "retreat_probability",
    "exploration_probability",
    "pressure_sensitivity",
    "thermal_comfort_index",
]

HORIZON_DECAY = {
    "24h": 1.0,
    "48h": 0.85,
    "72h": 0.70,
}


def _generate_target_from_features(
    feature_vector: List[float],
    species: str,
    horizon: str,
) -> Dict[str, float]:
    """Generate behavioral targets from feature vector."""
    decay = HORIZON_DECAY.get(horizon, 1.0)
    seed = int(hashlib.md5(f"{species}_{horizon}".encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed & 0x7FFFFFFF)
    noise = rng.uniform(-0.05, 0.05, len(TARGET_SCHEMA))

    fv = feature_vector
    habitat = fv[0] if len(fv) > 0 else 0.5
    wind = fv[7] if len(fv) > 7 else 0.5
    prudence = fv[11] if len(fv) > 11 else 0.5
    pressure = fv[18] if len(fv) > 18 else 0.5
    retreat = fv[22] if len(fv) > 22 else 0.5
    exploration = fv[23] if len(fv) > 23 else 0.5
    thermal = fv[31] if len(fv) > 31 else 0.5

    targets = {
        "presence_probability": max(0.0, min(1.0,
            (habitat * 0.30 + (1 - pressure) * 0.25 + thermal * 0.20
             + (1 - wind) * 0.15 + noise[0] * 0.10) * decay)),
        "movement_intensity": max(0.0, min(1.0,
            (exploration * 0.30 + (1 - prudence) * 0.20 + (1 - pressure) * 0.20
             + habitat * 0.15 + noise[1] * 0.15) * decay)),
        "retreat_probability": max(0.0, min(1.0,
            (retreat * 0.35 + pressure * 0.25 + wind * 0.15
             + prudence * 0.15 + noise[2] * 0.10) * decay)),
        "exploration_probability": max(0.0, min(1.0,
            (exploration * 0.35 + habitat * 0.20 + (1 - pressure) * 0.20
             + thermal * 0.15 + noise[3] * 0.10) * decay)),
        "pressure_sensitivity": max(0.0, min(1.0,
            (pressure * 0.35 + prudence * 0.25 + retreat * 0.20
             + wind * 0.10 + noise[4] * 0.10) * decay)),
        "thermal_comfort_index": max(0.0, min(1.0,
            (thermal * 0.35 + habitat * 0.20 + (1 - wind) * 0.20
             + (1 - pressure) * 0.15 + noise[5] * 0.10) * decay)),
    }

    return {k: round(v, 4) for k, v in targets.items()}


def build_targets(
    feature_result: Dict[str, Any],
    horizons: List[str] = None,
) -> Dict[str, Any]:
    """Generate targets for all horizons from a feature vector."""
    horizons = horizons or ["24h", "48h", "72h"]
    species = feature_result["species"]
    fv = feature_result["feature_vector"]

    predictions = {}
    for h in horizons:
        predictions[h] = _generate_target_from_features(fv, species, h)

    return {
        "species": species,
        "bounds": feature_result["bounds"],
        "horizons": horizons,
        "target_names": TARGET_SCHEMA,
        "predictions": predictions,
        "source_ids": feature_result.get("source_ids", {}),
    }


def get_target_schema() -> Dict[str, Any]:
    return {
        "target_count": len(TARGET_SCHEMA),
        "target_names": TARGET_SCHEMA,
        "horizons": list(HORIZON_DECAY.keys()),
        "horizon_decay": HORIZON_DECAY,
    }
