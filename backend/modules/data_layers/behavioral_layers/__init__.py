"""Behavioral Data Layers - PHASE 5
Data provider for wildlife behavior patterns and observations.
"""
from .data_layer import BehavioralDataLayer, get_behavioral_layer
from .v1 import router

__all__ = ["BehavioralDataLayer", "get_behavioral_layer", "router"]
