"""WMS Engine Models - CORE

Pydantic models for WMS (Web Map Service) layer management.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class WMSLayer(BaseModel):
    """WMS Layer definition"""
    id: str
    name: str
    title: str
    url: str
    layer_name: str
    format: str = "image/png"
    transparent: bool = True
    opacity: float = Field(default=1.0, ge=0, le=1)
    visible: bool = True
    category: str = "base"
    attribution: Optional[str] = None


class WMSCapabilities(BaseModel):
    """WMS service capabilities"""
    service_url: str
    version: str = "1.3.0"
    title: str
    abstract: Optional[str] = None
    layers: List[WMSLayer] = Field(default_factory=list)
    formats: List[str] = Field(default_factory=list)
    crs: List[str] = Field(default_factory=list)


class MapExtent(BaseModel):
    """Geographic extent/bounding box"""
    min_lat: float = Field(ge=-90, le=90)
    max_lat: float = Field(ge=-90, le=90)
    min_lon: float = Field(ge=-180, le=180)
    max_lon: float = Field(ge=-180, le=180)


class TileRequest(BaseModel):
    """Request for map tiles"""
    layer_id: str
    extent: MapExtent
    width: int = Field(default=256, ge=64, le=4096)
    height: int = Field(default=256, ge=64, le=4096)
    format: str = "image/png"


class LayerConfig(BaseModel):
    """Layer configuration for map display"""
    id: str
    visible: bool = True
    opacity: float = Field(default=1.0, ge=0, le=1)
    z_index: int = 0
