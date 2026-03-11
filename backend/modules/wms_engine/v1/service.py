"""WMS Engine Service - CORE

Business logic for WMS layer management.
Provides hunting-specific map layers from Quebec government sources.

Version: 1.0.0
"""

from typing import List, Optional
from .models import WMSLayer, MapExtent


class WMSService:
    """Service for WMS layer management"""
    
    # Pre-configured Quebec hunting layers
    QUEBEC_LAYERS = {
        "base_topo": WMSLayer(
            id="base_topo",
            name="Carte topographique",
            title="Carte topographique du Québec",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="BDTQ_20K",
            category="base",
            attribution="© Gouvernement du Québec"
        ),
        "hunting_zones": WMSLayer(
            id="hunting_zones",
            name="Zones de chasse",
            title="Zones de chasse du Québec",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="ZEC_ZECS",
            category="hunting",
            attribution="© MFFP Québec"
        ),
        "zecs": WMSLayer(
            id="zecs",
            name="ZEC",
            title="Zones d'exploitation contrôlée",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="ZEC_ZECS",
            category="hunting",
            attribution="© Réseau ZEC"
        ),
        "wildlife_reserves": WMSLayer(
            id="wildlife_reserves",
            name="Réserves fauniques",
            title="Réserves fauniques du Québec",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="SEPAQ_RESERVES",
            category="hunting",
            attribution="© SÉPAQ"
        ),
        "public_lands": WMSLayer(
            id="public_lands",
            name="Terres publiques",
            title="Terres du domaine de l'État",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="TERRITOIRE_PUBLIC",
            category="land",
            attribution="© MERN Québec"
        ),
        "hydrography": WMSLayer(
            id="hydrography",
            name="Hydrographie",
            title="Réseau hydrographique",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="BDTQ_HYDRO",
            category="environment",
            attribution="© Gouvernement du Québec"
        ),
        "forests": WMSLayer(
            id="forests",
            name="Couvert forestier",
            title="Inventaire forestier",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="SIEF_PEUPLEMENT",
            category="environment",
            attribution="© MFFP Québec"
        ),
        "elevation": WMSLayer(
            id="elevation",
            name="Élévation",
            title="Modèle numérique de terrain",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="MNT_QUEBEC",
            category="terrain",
            attribution="© MERN Québec"
        ),
        "roads": WMSLayer(
            id="roads",
            name="Réseau routier",
            title="Routes et chemins forestiers",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="ROUTIER_RESEAU",
            category="infrastructure",
            attribution="© MTQ Québec"
        ),
        "satellite": WMSLayer(
            id="satellite",
            name="Imagerie satellite",
            title="Images satellites",
            url="https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi",
            layer_name="ORTHO_QUEBEC",
            category="base",
            attribution="© Gouvernement du Québec"
        )
    }
    
    # Layer categories
    CATEGORIES = {
        "base": "Cartes de base",
        "hunting": "Zones de chasse",
        "land": "Tenure des terres",
        "environment": "Environnement",
        "terrain": "Terrain",
        "infrastructure": "Infrastructure"
    }
    
    def get_all_layers(self) -> List[WMSLayer]:
        """Get all available layers"""
        return list(self.QUEBEC_LAYERS.values())
    
    def get_layer(self, layer_id: str) -> Optional[WMSLayer]:
        """Get a specific layer by ID"""
        return self.QUEBEC_LAYERS.get(layer_id)
    
    def get_layers_by_category(self, category: str) -> List[WMSLayer]:
        """Get all layers in a category"""
        return [
            layer for layer in self.QUEBEC_LAYERS.values()
            if layer.category == category
        ]
    
    def get_hunting_layers(self) -> List[WMSLayer]:
        """Get all hunting-related layers"""
        hunting_categories = ["hunting", "land"]
        return [
            layer for layer in self.QUEBEC_LAYERS.values()
            if layer.category in hunting_categories
        ]
    
    def build_wms_url(self, layer: WMSLayer, extent: MapExtent, 
                      width: int = 256, height: int = 256) -> str:
        """
        Build WMS GetMap URL for a layer.
        
        Args:
            layer: WMS layer configuration
            extent: Geographic extent
            width: Image width
            height: Image height
            
        Returns:
            Complete WMS GetMap URL
        """
        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetMap",
            "LAYERS": layer.layer_name,
            "CRS": "EPSG:4326",
            "BBOX": f"{extent.min_lat},{extent.min_lon},{extent.max_lat},{extent.max_lon}",
            "WIDTH": str(width),
            "HEIGHT": str(height),
            "FORMAT": layer.format,
            "TRANSPARENT": "TRUE" if layer.transparent else "FALSE"
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{layer.url}?{query}"
    
    def get_recommended_layers(self, use_case: str = "general") -> List[str]:
        """
        Get recommended layers for a use case.
        
        Args:
            use_case: "general", "scouting", "navigation", "planning"
        """
        recommendations = {
            "general": ["base_topo", "hunting_zones", "hydrography"],
            "scouting": ["satellite", "forests", "elevation", "hydrography"],
            "navigation": ["base_topo", "roads", "hydrography"],
            "planning": ["hunting_zones", "zecs", "wildlife_reserves", "public_lands"]
        }
        
        return recommendations.get(use_case, recommendations["general"])
    
    def validate_extent(self, extent: MapExtent) -> bool:
        """Validate that extent is within Quebec bounds"""
        quebec_bounds = {
            "min_lat": 44.99,
            "max_lat": 62.59,
            "min_lon": -79.76,
            "max_lon": -57.10
        }
        
        return (
            extent.min_lat >= quebec_bounds["min_lat"] and
            extent.max_lat <= quebec_bounds["max_lat"] and
            extent.min_lon >= quebec_bounds["min_lon"] and
            extent.max_lon <= quebec_bounds["max_lon"]
        )
