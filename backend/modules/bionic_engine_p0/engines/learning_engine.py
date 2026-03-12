"""
Learning Engine — Calibration par observations terrain
========================================================
Collecte: cameras, indices terrain, waypoints, observations utilisateur.
Mode initial: ponderation par defaut. Mode calibre: ajustement modele.
"""

from .base import BionicEngine, EngineResult


# Observation types and their confidence contribution
OBSERVATION_CONFIDENCE = {
    "camera_trap": 0.20,       # Visual confirmation
    "tracks": 0.10,            # Track identification
    "scat": 0.08,              # Scat analysis
    "browse_sign": 0.06,       # Browse damage
    "bedding_site": 0.05,      # Bedding depression
    "rub_scrape": 0.07,        # Rut sign
    "vocal": 0.12,             # Call/vocalization
    "visual_sighting": 0.15,   # Direct observation
    "waypoint": 0.04,          # User-marked waypoint
}

# Temporal decay: observations lose relevance over time
TEMPORAL_DECAY_DAYS = {
    "camera_trap": 30,
    "tracks": 7,
    "scat": 14,
    "browse_sign": 21,
    "visual_sighting": 3,
    "waypoint": 60,
}


class LearningEngine(BionicEngine):
    ENGINE_ID = "learning"
    ENGINE_NAME = "Learning Engine"
    DEFAULT_WEIGHT = 0.05

    def evaluate(self, context):
        observations = context.get("observations", [])
        waypoint_history = context.get("waypoint_history", [])
        corridor_id = context.get("corridor_id", "unknown")

        observation_count = len(observations)
        waypoint_count = len(waypoint_history)
        has_data = observation_count > 0 or waypoint_count > 0

        if has_data:
            # Calculate confidence from observation types
            type_confidence = 0
            for obs in observations:
                obs_type = obs.get("type", "waypoint") if isinstance(obs, dict) else "waypoint"
                type_confidence += OBSERVATION_CONFIDENCE.get(obs_type, 0.04)
            type_confidence = min(0.6, type_confidence)

            # Waypoint contribution
            wp_confidence = min(0.3, waypoint_count * 0.05)

            total_confidence = min(0.9, 0.2 + type_confidence + wp_confidence)

            # Score: more data = higher corridor confidence
            confidence_boost = min(35, observation_count * 5 + waypoint_count * 3)
            score = 50 + confidence_boost

            # Spatial relevance: observations near this corridor get extra weight
            spatial_bonus = 0
            for obs in observations:
                if isinstance(obs, dict) and obs.get("corridor_id") == corridor_id:
                    spatial_bonus += 5
            score = min(100, score + spatial_bonus)

            justification = (
                f"{observation_count} obs., {waypoint_count} waypoints - "
                f"modele calibre (confiance: {total_confidence:.0%})"
            )
            certainty = total_confidence
        else:
            score = 50
            certainty = 0.20
            justification = "Aucune observation - modele par defaut (non calibre)"

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=certainty,
            justification=justification,
            classification_impact=0,
            details={
                "observations": observation_count,
                "waypoints": waypoint_count,
                "calibrated": has_data,
                "corridor_id": corridor_id,
            },
        )
