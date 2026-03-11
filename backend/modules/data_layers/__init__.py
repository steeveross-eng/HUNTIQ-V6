"""Data Layers Module - PHASE 5
Central access point for all data layer providers.

Version: 1.0.0
"""

from .ecoforestry_layers import get_ecoforestry_layer, EcoforestryDataLayer
from .behavioral_layers import get_behavioral_layer, BehavioralDataLayer
from .simulation_layers import get_simulation_layer, SimulationDataLayer
from .layers_3d import get_3d_layer, Layers3DDataLayer
from .advanced_geospatial_layers import get_advanced_geospatial_layer, AdvancedGeospatialDataLayer


# Central registry of all data layers
DATA_LAYERS = {
    "ecoforestry": get_ecoforestry_layer,
    "behavioral": get_behavioral_layer,
    "simulation": get_simulation_layer,
    "3d": get_3d_layer,
    "advanced_geospatial": get_advanced_geospatial_layer
}


def get_layer(layer_name: str):
    """Get a data layer by name"""
    factory = DATA_LAYERS.get(layer_name)
    if factory:
        return factory()
    raise ValueError(f"Unknown data layer: {layer_name}")


def get_all_layers():
    """Get all data layer instances"""
    return {name: factory() for name, factory in DATA_LAYERS.items()}


async def get_all_layer_stats():
    """Get statistics from all data layers"""
    stats = {}
    for name, factory in DATA_LAYERS.items():
        layer = factory()
        stats[name] = await layer.get_stats()
    return stats


__all__ = [
    # Layer getters
    "get_ecoforestry_layer",
    "get_behavioral_layer", 
    "get_simulation_layer",
    "get_3d_layer",
    "get_advanced_geospatial_layer",
    # Layer classes
    "EcoforestryDataLayer",
    "BehavioralDataLayer",
    "SimulationDataLayer",
    "Layers3DDataLayer",
    "AdvancedGeospatialDataLayer",
    # Utilities
    "get_layer",
    "get_all_layers",
    "get_all_layer_stats",
    "DATA_LAYERS"
]
