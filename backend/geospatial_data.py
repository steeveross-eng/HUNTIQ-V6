"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
BIONIC™ Geospatial Data Integration Module
============================================
Real-time environmental data from external APIs:
- Open-Meteo: Weather data (temperature, precipitation, wind, humidity)
- NASA MODIS: Satellite data (NDVI, NDWI vegetation indices)
- Open-Elevation: Terrain elevation data

No API keys required for Open-Meteo and Open-Elevation.
NASA AppEEARS requires free Earthdata Login credentials.
"""

import aiohttp
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import logging
import os

logger = logging.getLogger(__name__)

# ============================================
# DATA CLASSES
# ============================================

@dataclass
class WeatherData:
    """Current and forecast weather data"""
    temperature: float  # °C
    apparent_temperature: float  # °C (feels like)
    humidity: float  # %
    precipitation: float  # mm
    precipitation_probability: float  # %
    wind_speed: float  # km/h
    wind_direction: int  # degrees
    cloud_cover: float  # %
    pressure: float  # hPa
    uv_index: float
    is_day: bool
    weather_code: int
    weather_description: str
    timestamp: str
    
    # Forecast data
    forecast_24h: Optional[Dict] = None
    forecast_72h: Optional[Dict] = None
    forecast_7d: Optional[Dict] = None

@dataclass
class TerrainData:
    """Terrain and elevation data"""
    elevation: float  # meters
    slope: Optional[float] = None  # degrees
    aspect: Optional[float] = None  # degrees (N=0, E=90, S=180, W=270)

@dataclass
class VegetationData:
    """Satellite vegetation indices"""
    ndvi: float  # Normalized Difference Vegetation Index (-1 to 1)
    data_date: str
    ndwi: Optional[float] = None  # Normalized Difference Water Index
    evi: Optional[float] = None  # Enhanced Vegetation Index
    lai: Optional[float] = None  # Leaf Area Index
    source: str = "NASA MODIS"
    quality_flag: str = "good"

@dataclass
class GeospatialBundle:
    """Complete geospatial data bundle for a location"""
    latitude: float
    longitude: float
    weather: Optional[WeatherData] = None
    terrain: Optional[TerrainData] = None
    vegetation: Optional[VegetationData] = None
    fetch_timestamp: str = ""
    data_quality: str = "complete"
    errors: List[str] = None


# ============================================
# WEATHER CODE DESCRIPTIONS (WMO)
# ============================================

WMO_WEATHER_CODES = {
    0: "Ciel dégagé",
    1: "Principalement dégagé",
    2: "Partiellement nuageux",
    3: "Couvert",
    45: "Brouillard",
    48: "Brouillard givrant",
    51: "Bruine légère",
    53: "Bruine modérée",
    55: "Bruine dense",
    56: "Bruine verglaçante légère",
    57: "Bruine verglaçante dense",
    61: "Pluie légère",
    63: "Pluie modérée",
    65: "Pluie forte",
    66: "Pluie verglaçante légère",
    67: "Pluie verglaçante forte",
    71: "Neige légère",
    73: "Neige modérée",
    75: "Neige forte",
    77: "Grains de neige",
    80: "Averses légères",
    81: "Averses modérées",
    82: "Averses violentes",
    85: "Averses de neige légères",
    86: "Averses de neige fortes",
    95: "Orage",
    96: "Orage avec grêle légère",
    99: "Orage avec grêle forte"
}


# ============================================
# OPEN-METEO WEATHER API
# ============================================

class OpenMeteoClient:
    """Client for Open-Meteo free weather API"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        """
        Fetch current weather and forecast from Open-Meteo
        
        Args:
            latitude: WGS84 latitude
            longitude: WGS84 longitude
            
        Returns:
            WeatherData object or None on error
        """
        try:
            session = await self._get_session()
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "apparent_temperature",
                    "relative_humidity_2m",
                    "precipitation",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "uv_index",
                    "is_day"
                ],
                "hourly": [
                    "temperature_2m",
                    "precipitation_probability",
                    "precipitation",
                    "weather_code"
                ],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "weather_code"
                ],
                "timezone": "America/Toronto",
                "forecast_days": 7
            }
            
            async with session.get(self.BASE_URL, params=params) as response:
                if response.status != 200:
                    logger.error(f"Open-Meteo API error: {response.status}")
                    return None
                
                data = await response.json()
                
                current = data.get("current", {})
                hourly = data.get("hourly", {})
                daily = data.get("daily", {})
                
                # Build forecast summaries
                forecast_24h = self._build_forecast_summary(hourly, daily, hours=24)
                forecast_72h = self._build_forecast_summary(hourly, daily, hours=72)
                forecast_7d = self._build_daily_summary(daily)
                
                weather_code = current.get("weather_code", 0)
                
                return WeatherData(
                    temperature=current.get("temperature_2m", 0),
                    apparent_temperature=current.get("apparent_temperature", 0),
                    humidity=current.get("relative_humidity_2m", 50),
                    precipitation=current.get("precipitation", 0),
                    precipitation_probability=hourly.get("precipitation_probability", [0])[0] if hourly.get("precipitation_probability") else 0,
                    wind_speed=current.get("wind_speed_10m", 0),
                    wind_direction=current.get("wind_direction_10m", 0),
                    cloud_cover=current.get("cloud_cover", 0),
                    pressure=current.get("pressure_msl", 1013),
                    uv_index=current.get("uv_index", 0),
                    is_day=current.get("is_day", 1) == 1,
                    weather_code=weather_code,
                    weather_description=WMO_WEATHER_CODES.get(weather_code, "Inconnu"),
                    timestamp=current.get("time", datetime.now(timezone.utc).isoformat()),
                    forecast_24h=forecast_24h,
                    forecast_72h=forecast_72h,
                    forecast_7d=forecast_7d
                )
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def _build_forecast_summary(self, hourly: Dict, daily: Dict, hours: int) -> Dict:
        """Build forecast summary for next N hours"""
        temps = hourly.get("temperature_2m", [])[:hours]
        precip_prob = hourly.get("precipitation_probability", [])[:hours]
        precip = hourly.get("precipitation", [])[:hours]
        
        if not temps:
            return {}
        
        return {
            "temp_min": min(temps) if temps else 0,
            "temp_max": max(temps) if temps else 0,
            "temp_avg": sum(temps) / len(temps) if temps else 0,
            "precip_probability_max": max(precip_prob) if precip_prob else 0,
            "precip_total": sum(precip) if precip else 0,
            "hours": hours
        }
    
    def _build_daily_summary(self, daily: Dict) -> Dict:
        """Build 7-day forecast summary"""
        return {
            "dates": daily.get("time", []),
            "temp_max": daily.get("temperature_2m_max", []),
            "temp_min": daily.get("temperature_2m_min", []),
            "precipitation": daily.get("precipitation_sum", []),
            "precip_probability": daily.get("precipitation_probability_max", []),
            "weather_codes": daily.get("weather_code", [])
        }


# ============================================
# OPEN-ELEVATION API
# ============================================

class OpenElevationClient:
    """Client for Open-Elevation free terrain API"""
    
    BASE_URL = "https://api.open-elevation.com/api/v1/lookup"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_elevation(self, latitude: float, longitude: float) -> Optional[TerrainData]:
        """
        Fetch elevation data from Open-Elevation
        
        Args:
            latitude: WGS84 latitude
            longitude: WGS84 longitude
            
        Returns:
            TerrainData object or None on error
        """
        try:
            session = await self._get_session()
            
            # Get elevation for center point and surrounding points to calculate slope/aspect
            points = [
                {"latitude": latitude, "longitude": longitude},
                {"latitude": latitude + 0.001, "longitude": longitude},  # North
                {"latitude": latitude - 0.001, "longitude": longitude},  # South
                {"latitude": latitude, "longitude": longitude + 0.001},  # East
                {"latitude": latitude, "longitude": longitude - 0.001},  # West
            ]
            
            payload = {"locations": points}
            
            async with session.post(self.BASE_URL, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Open-Elevation API error: {response.status}")
                    return None
                
                data = await response.json()
                results = data.get("results", [])
                
                if not results:
                    return None
                
                center_elev = results[0].get("elevation", 0)
                
                # Calculate slope and aspect if we have surrounding points
                slope = None
                aspect = None
                
                if len(results) >= 5:
                    north_elev = results[1].get("elevation", center_elev)
                    south_elev = results[2].get("elevation", center_elev)
                    east_elev = results[3].get("elevation", center_elev)
                    west_elev = results[4].get("elevation", center_elev)
                    
                    # Approximate slope calculation
                    dx = (east_elev - west_elev) / (2 * 111)  # ~111m per 0.001 degree
                    dy = (north_elev - south_elev) / (2 * 111)
                    
                    import math
                    slope = math.degrees(math.atan(math.sqrt(dx**2 + dy**2)))
                    
                    # Aspect calculation (direction of steepest descent)
                    if dx != 0 or dy != 0:
                        aspect = math.degrees(math.atan2(-dx, -dy))
                        if aspect < 0:
                            aspect += 360
                
                return TerrainData(
                    elevation=center_elev,
                    slope=round(slope, 2) if slope else None,
                    aspect=round(aspect, 1) if aspect else None
                )
                
        except Exception as e:
            logger.error(f"Error fetching elevation data: {e}")
            return None


# ============================================
# NASA MODIS NDVI (AppEEARS Integration)
# ============================================

class NDVIDataClient:
    """
    Client for vegetation index data via NASA AppEEARS API.
    
    Primary: NASA AppEEARS (real MODIS satellite data)
    Fallback: Seasonal/regional estimates based on location and date
    
    To use real data:
    1. Register at https://urs.earthdata.nasa.gov/
    2. Enable API access in AppEEARS Settings
    3. Set NASA_EARTHDATA_USERNAME and NASA_EARTHDATA_PASSWORD in .env
    """
    
    APPEEARS_BASE_URL = "https://appeears.earthdatacloud.nasa.gov/api"
    
    # Regional NDVI estimates by season and biome
    # Based on typical Quebec/Eastern Canada boreal forest values
    SEASONAL_NDVI = {
        "boreal_forest": {
            "winter": {"ndvi": 0.15, "ndwi": -0.10},
            "spring": {"ndvi": 0.45, "ndwi": 0.10},
            "summer": {"ndvi": 0.75, "ndwi": 0.25},
            "fall": {"ndvi": 0.50, "ndwi": 0.15}
        },
        "mixed_forest": {
            "winter": {"ndvi": 0.20, "ndwi": -0.05},
            "spring": {"ndvi": 0.55, "ndwi": 0.15},
            "summer": {"ndvi": 0.80, "ndwi": 0.30},
            "fall": {"ndvi": 0.55, "ndwi": 0.20}
        },
        "wetland": {
            "winter": {"ndvi": 0.10, "ndwi": 0.30},
            "spring": {"ndvi": 0.40, "ndwi": 0.45},
            "summer": {"ndvi": 0.65, "ndwi": 0.50},
            "fall": {"ndvi": 0.35, "ndwi": 0.40}
        }
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        
        # NASA Earthdata credentials from environment
        self.username = os.environ.get("NASA_EARTHDATA_USERNAME", "")
        self.password = os.environ.get("NASA_EARTHDATA_PASSWORD", "")
        self.has_credentials = bool(self.username and self.password)
        
        if self.has_credentials:
            logger.info("NASA AppEEARS: Credentials configured")
        else:
            logger.info("NASA AppEEARS: No credentials, using seasonal estimates")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _get_token(self) -> Optional[str]:
        """
        Authenticate with NASA AppEEARS and get bearer token.
        Token is cached for 47 hours (expires at 48h).
        """
        # Check if we have a valid cached token
        if self._token and self._token_expiry:
            if datetime.now(timezone.utc) < self._token_expiry:
                return self._token
        
        if not self.has_credentials:
            return None
        
        try:
            session = await self._get_session()
            
            # Basic auth login
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            async with session.post(
                f"{self.APPEEARS_BASE_URL}/login",
                auth=auth
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self._token = data.get("token")
                    # Token expires in 48h, cache for 47h to be safe
                    self._token_expiry = datetime.now(timezone.utc) + timedelta(hours=47)
                    logger.info("NASA AppEEARS: Authentication successful")
                    return self._token
                else:
                    error_text = await response.text()
                    logger.error(f"NASA AppEEARS login failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"NASA AppEEARS authentication error: {e}")
            return None
    
    def _get_season(self, date: datetime = None) -> str:
        """Determine season from date"""
        if date is None:
            date = datetime.now()
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def _get_biome(self, latitude: float, longitude: float) -> str:
        """Estimate biome type based on location"""
        # Simplified biome classification for North America
        if latitude > 60:
            return "boreal_forest"
        elif latitude > 52:
            return "boreal_forest"
        elif latitude > 45:
            return "mixed_forest"
        else:
            return "mixed_forest"
    
    async def get_vegetation_indices(
        self, 
        latitude: float, 
        longitude: float,
        use_nasa_api: bool = True
    ) -> Optional[VegetationData]:
        """
        Fetch vegetation indices (NDVI, NDWI)
        
        Args:
            latitude: WGS84 latitude
            longitude: WGS84 longitude
            use_nasa_api: Whether to attempt NASA API (requires credentials)
            
        Returns:
            VegetationData object with interpretation
        """
        # Try NASA AppEEARS if credentials available
        if use_nasa_api and self.has_credentials:
            nasa_data = await self._fetch_nasa_appeears(latitude, longitude)
            if nasa_data:
                return nasa_data
        
        # Fallback to seasonal estimates
        return self._get_seasonal_estimate(latitude, longitude)
    
    async def _fetch_nasa_appeears(self, latitude: float, longitude: float) -> Optional[VegetationData]:
        """
        Fetch real NDVI/NDWI data from NASA AppEEARS API
        
        Uses point sample request for quick data retrieval.
        For historical data, would need area request with task queue.
        """
        try:
            token = await self._get_token()
            if not token:
                logger.warning("NASA AppEEARS: No valid token, falling back to estimates")
                return None
            
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get available products for MODIS NDVI
            # MOD13Q1.061 = MODIS Terra Vegetation Indices 16-Day L3 Global 250m
            # MYD13Q1.061 = MODIS Aqua equivalent
            
            # For point samples, AppEEARS can return recent data
            # We'll request the most recent 16-day NDVI product
            
            task_payload = {
                "task_type": "point",
                "task_name": f"bionic_ndvi_{latitude}_{longitude}",
                "params": {
                    "coordinates": [
                        {
                            "latitude": latitude,
                            "longitude": longitude,
                            "id": "location_1"
                        }
                    ],
                    "dates": [
                        {
                            "startDate": (datetime.now() - timedelta(days=32)).strftime("%m-%d-%Y"),
                            "endDate": datetime.now().strftime("%m-%d-%Y")
                        }
                    ],
                    "layers": [
                        {
                            "product": "MOD13Q1.061",
                            "layer": "_250m_16_days_NDVI"
                        },
                        {
                            "product": "MOD13Q1.061",
                            "layer": "_250m_16_days_EVI"
                        }
                    ]
                }
            }
            
            # Submit task
            async with session.post(
                f"{self.APPEEARS_BASE_URL}/task",
                headers=headers,
                json=task_payload
            ) as response:
                if response.status == 202:
                    task_data = await response.json()
                    task_id = task_data.get("task_id")
                    logger.info(f"NASA AppEEARS: Task submitted {task_id}")
                    
                    # Poll for completion (with timeout)
                    result = await self._poll_task_completion(task_id, headers, timeout=30)
                    if result:
                        return result
                else:
                    error = await response.text()
                    logger.warning(f"NASA AppEEARS task submission failed: {response.status} - {error}")
            
            return None
            
        except Exception as e:
            logger.error(f"NASA AppEEARS fetch error: {e}")
            return None
    
    async def _poll_task_completion(
        self, 
        task_id: str, 
        headers: dict, 
        timeout: int = 30
    ) -> Optional[VegetationData]:
        """
        Poll AppEEARS task status and retrieve results when complete
        """
        session = await self._get_session()
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                async with session.get(
                    f"{self.APPEEARS_BASE_URL}/task/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        task_info = await response.json()
                        status = task_info.get("status")
                        
                        if status == "done":
                            # Get the results
                            return await self._download_task_results(task_id, headers)
                        elif status == "error":
                            logger.error(f"NASA AppEEARS task failed: {task_info}")
                            return None
                        
                        # Still processing, wait and retry
                        await asyncio.sleep(2)
                    else:
                        logger.warning(f"NASA AppEEARS status check failed: {response.status}")
                        return None
                        
            except Exception as e:
                logger.error(f"NASA AppEEARS poll error: {e}")
                return None
        
        logger.warning(f"NASA AppEEARS task timeout after {timeout}s")
        return None
    
    async def _download_task_results(self, task_id: str, headers: dict) -> Optional[VegetationData]:
        """
        Download and parse AppEEARS task results
        """
        try:
            session = await self._get_session()
            
            # Get bundle info
            async with session.get(
                f"{self.APPEEARS_BASE_URL}/bundle/{task_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    return None
                
                bundle = await response.json()
                files = bundle.get("files", [])
                
                # Find the CSV result file
                csv_file = next((f for f in files if f.get("file_name", "").endswith(".csv")), None)
                
                if csv_file:
                    file_id = csv_file.get("file_id")
                    async with session.get(
                        f"{self.APPEEARS_BASE_URL}/bundle/{task_id}/{file_id}",
                        headers=headers
                    ) as file_response:
                        if file_response.status == 200:
                            csv_text = await file_response.text()
                            return self._parse_appeears_csv(csv_text)
                
                return None
                
        except Exception as e:
            logger.error(f"NASA AppEEARS download error: {e}")
            return None
    
    def _parse_appeears_csv(self, csv_text: str) -> Optional[VegetationData]:
        """
        Parse AppEEARS CSV output to extract NDVI/NDWI values
        """
        try:
            import csv
            from io import StringIO
            
            reader = csv.DictReader(StringIO(csv_text))
            
            ndvi_values = []
            evi_values = []
            latest_date = None
            
            for row in reader:
                # MODIS scale factor for NDVI/EVI is 0.0001
                if "NDVI" in row.get("Layer", ""):
                    val = float(row.get("Value", 0)) * 0.0001
                    if -1 <= val <= 1:  # Valid range
                        ndvi_values.append(val)
                        date_str = row.get("Date", "")
                        if date_str:
                            latest_date = date_str
                
                if "EVI" in row.get("Layer", ""):
                    val = float(row.get("Value", 0)) * 0.0001
                    if -1 <= val <= 1:
                        evi_values.append(val)
            
            if ndvi_values:
                avg_ndvi = sum(ndvi_values) / len(ndvi_values)
                avg_evi = sum(evi_values) / len(evi_values) if evi_values else avg_ndvi * 0.8
                
                # Estimate NDWI from NDVI (approximation)
                # In reality, NDWI requires NIR and SWIR bands
                estimated_ndwi = (avg_ndvi - 0.3) * 0.5
                
                return VegetationData(
                    ndvi=round(avg_ndvi, 3),
                    data_date=latest_date or datetime.now().strftime("%Y-%m-%d"),
                    ndwi=round(estimated_ndwi, 3),
                    evi=round(avg_evi, 3),
                    lai=round(avg_ndvi * 6, 2),
                    source="NASA AppEEARS (MODIS MOD13Q1.061)",
                    quality_flag="satellite"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"NASA AppEEARS CSV parse error: {e}")
            return None
    
    def _get_seasonal_estimate(self, latitude: float, longitude: float) -> VegetationData:
        """
        Get seasonal NDVI/NDWI estimates based on location and time of year.
        Provides realistic values based on NASA MODIS typical observations.
        """
        import random
        
        season = self._get_season()
        biome = self._get_biome(latitude, longitude)
        
        base_values = self.SEASONAL_NDVI.get(biome, self.SEASONAL_NDVI["mixed_forest"])
        seasonal_values = base_values.get(season, base_values["summer"])
        
        # Add realistic variation (±10%)
        variation = 0.1
        ndvi = seasonal_values["ndvi"] + random.uniform(-variation, variation)
        ndwi = seasonal_values["ndwi"] + random.uniform(-variation, variation)
        
        # Clamp to valid ranges
        ndvi = max(-1.0, min(1.0, ndvi))
        ndwi = max(-1.0, min(1.0, ndwi))
        
        # Calculate EVI estimate (typically ~0.8 * NDVI for forests)
        evi = ndvi * 0.8 + random.uniform(-0.05, 0.05)
        evi = max(-1.0, min(1.0, evi))
        
        return VegetationData(
            ndvi=round(ndvi, 3),
            data_date=datetime.now().strftime("%Y-%m-%d"),
            ndwi=round(ndwi, 3),
            evi=round(evi, 3),
            lai=round(ndvi * 6, 2),
            source="Estimation saisonnière (valeurs typiques NASA MODIS)" if not self.has_credentials else "Estimation saisonnière (API timeout)",
            quality_flag="estimated"
        )


# ============================================
# NDVI/NDWI INTERPRETATION (User-friendly)
# ============================================

def interpret_ndvi(ndvi: float) -> dict:
    """
    Interprétation simple et non technique de la valeur NDVI.
    
    Échelle NDVI — Verdure:
    - 0.00–0.20 : Végétation faible (sol visible, début de saison)
    - 0.20–0.40 : Végétation moyenne (présente mais peu dense)
    - 0.40–0.60 : Bonne végétation (croissance active)
    - >0.60 : Végétation dense (habitat optimal)
    """
    if ndvi < 0:
        return {
            "level": "null",
            "label": "Sol nu ou eau",
            "description": "Absence de végétation. Zone d'eau, roche ou sol exposé.",
            "icon": "🪨",
            "color": "gray"
        }
    elif ndvi < 0.20:
        return {
            "level": "faible",
            "label": "Végétation faible",
            "description": "Sol visible avec peu de verdure. Typique du début de saison ou zones dégagées.",
            "icon": "🌾",
            "color": "yellow"
        }
    elif ndvi < 0.40:
        return {
            "level": "moyenne",
            "label": "Végétation moyenne",
            "description": "Végétation présente mais peu dense. Prairies ou forêts clairsemées.",
            "icon": "🌿",
            "color": "lime"
        }
    elif ndvi < 0.60:
        return {
            "level": "bonne",
            "label": "Bonne végétation",
            "description": "Croissance active avec couvert végétal sain. Conditions favorables.",
            "icon": "🌳",
            "color": "green"
        }
    else:
        return {
            "level": "dense",
            "label": "Végétation dense",
            "description": "Couvert forestier optimal. Habitat idéal pour la faune.",
            "icon": "🌲",
            "color": "darkgreen"
        }


def interpret_ndwi(ndwi: float) -> dict:
    """
    Interprétation simple et non technique de la valeur NDWI.
    
    Échelle NDWI — Humidité:
    - <0.00 : Très sec (stress hydrique)
    - 0.00–0.10 : Sec (humidité faible)
    - 0.10–0.25 : Humidité normale (conditions correctes)
    - 0.25–0.40 : Humide (bonne rétention d'eau)
    - >0.40 : Très humide (sol saturé)
    """
    if ndwi < 0:
        return {
            "level": "tres_sec",
            "label": "Très sec",
            "description": "Stress hydrique probable. Végétation en manque d'eau.",
            "icon": "☀️",
            "color": "orange"
        }
    elif ndwi < 0.10:
        return {
            "level": "sec",
            "label": "Sec",
            "description": "Humidité faible. Conditions normales pour la saison sèche.",
            "icon": "🌤️",
            "color": "yellow"
        }
    elif ndwi < 0.25:
        return {
            "level": "normal",
            "label": "Humidité normale",
            "description": "Conditions d'humidité correctes pour la végétation.",
            "icon": "💧",
            "color": "blue"
        }
    elif ndwi < 0.40:
        return {
            "level": "humide",
            "label": "Humide",
            "description": "Bonne rétention d'eau. Zone favorable près de cours d'eau.",
            "icon": "💦",
            "color": "cyan"
        }
    else:
        return {
            "level": "tres_humide",
            "label": "Très humide",
            "description": "Sol saturé en eau. Zone humide ou marécageuse.",
            "icon": "🌊",
            "color": "darkblue"
        }


def interpret_vegetation(ndvi: float, ndwi: float) -> dict:
    """
    Génère une interprétation complète et accessible des indices de végétation.
    
    Retourne:
    - Une phrase simple pour NDVI (verdure)
    - Une phrase simple pour NDWI (humidité)
    - Une conclusion saisonnière courte
    """
    ndvi_interp = interpret_ndvi(ndvi)
    ndwi_interp = interpret_ndwi(ndwi)
    
    # Conclusion saisonnière basée sur la combinaison NDVI/NDWI
    if ndvi < 0.20 and ndwi < 0:
        conclusion = {
            "status": "dormance",
            "message": "Période de dormance ou début de saison. Végétation peu active.",
            "icon": "❄️"
        }
    elif ndvi < 0.20 and ndwi >= 0:
        conclusion = {
            "status": "emergence",
            "message": "Début de croissance probable. La végétation commence à émerger.",
            "icon": "🌱"
        }
    elif ndvi >= 0.20 and ndvi < 0.40 and ndwi < 0:
        conclusion = {
            "status": "stress_hydrique",
            "message": "Stress hydrique détecté. La végétation manque d'eau.",
            "icon": "⚠️"
        }
    elif ndvi >= 0.40 and ndvi < 0.60:
        conclusion = {
            "status": "croissance_active",
            "message": "Croissance active. Bonnes conditions pour la faune.",
            "icon": "🌿"
        }
    elif ndvi >= 0.60 and ndwi >= 0.10:
        conclusion = {
            "status": "conditions_optimales",
            "message": "Conditions optimales. Habitat de qualité avec végétation dense.",
            "icon": "✅"
        }
    elif ndvi >= 0.60 and ndwi < 0.10:
        conclusion = {
            "status": "dense_sec",
            "message": "Végétation dense mais sèche. Attention au risque d'incendie.",
            "icon": "🔥"
        }
    else:
        conclusion = {
            "status": "normal",
            "message": "Conditions normales pour la saison.",
            "icon": "🌳"
        }
    
    return {
        "ndvi": {
            "value": round(ndvi, 3),
            **ndvi_interp
        },
        "ndwi": {
            "value": round(ndwi, 3),
            **ndwi_interp
        },
        "conclusion": conclusion,
        "summary": f"{ndvi_interp['icon']} {ndvi_interp['label']} • {ndwi_interp['icon']} {ndwi_interp['label']} • {conclusion['icon']} {conclusion['message']}"
    }


# ============================================
# MAIN GEOSPATIAL DATA SERVICE
# ============================================

class GeospatialDataService:
    """
    Main service for fetching all geospatial data
    
    Combines:
    - Open-Meteo: Real-time weather
    - Open-Elevation: Terrain data
    - NASA MODIS/Seasonal estimates: Vegetation indices
    """
    
    def __init__(self):
        self.weather_client = OpenMeteoClient()
        self.elevation_client = OpenElevationClient()
        self.ndvi_client = NDVIDataClient()
    
    async def close(self):
        """Close all client sessions"""
        await self.weather_client.close()
        await self.elevation_client.close()
        await self.ndvi_client.close()
    
    async def get_complete_data(
        self,
        latitude: float,
        longitude: float,
        include_weather: bool = True,
        include_terrain: bool = True,
        include_vegetation: bool = True
    ) -> GeospatialBundle:
        """
        Fetch all geospatial data for a location
        
        Args:
            latitude: WGS84 latitude
            longitude: WGS84 longitude
            include_weather: Fetch weather data
            include_terrain: Fetch elevation/slope data
            include_vegetation: Fetch NDVI/NDWI data
            
        Returns:
            GeospatialBundle with all requested data
        """
        errors = []
        
        # Fetch data in parallel
        tasks = []
        
        if include_weather:
            tasks.append(("weather", self.weather_client.get_weather(latitude, longitude)))
        
        if include_terrain:
            tasks.append(("terrain", self.elevation_client.get_elevation(latitude, longitude)))
        
        if include_vegetation:
            tasks.append(("vegetation", self.ndvi_client.get_vegetation_indices(latitude, longitude)))
        
        # Execute all tasks concurrently
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                errors.append(f"{name}: {str(e)}")
                results[name] = None
        
        # Determine data quality
        data_quality = "complete"
        if errors:
            data_quality = "partial" if any(results.values()) else "failed"
        
        return GeospatialBundle(
            latitude=latitude,
            longitude=longitude,
            weather=results.get("weather"),
            terrain=results.get("terrain"),
            vegetation=results.get("vegetation"),
            fetch_timestamp=datetime.now(timezone.utc).isoformat(),
            data_quality=data_quality,
            errors=errors if errors else None
        )
    
    async def get_weather_only(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        """Fetch only weather data"""
        return await self.weather_client.get_weather(latitude, longitude)
    
    async def get_terrain_only(self, latitude: float, longitude: float) -> Optional[TerrainData]:
        """Fetch only terrain data"""
        return await self.elevation_client.get_elevation(latitude, longitude)
    
    async def get_vegetation_only(self, latitude: float, longitude: float) -> Optional[VegetationData]:
        """Fetch only vegetation data"""
        return await self.ndvi_client.get_vegetation_indices(latitude, longitude)


# ============================================
# HELPER FUNCTIONS FOR BIONIC MODULE INTEGRATION
# ============================================

def weather_to_bionic_factors(weather: WeatherData) -> Dict[str, float]:
    """
    Convert weather data to BIONIC module factors (0-100 scale)
    """
    factors = {}
    
    # Temperature comfort factor (optimal hunting: -5 to 15°C)
    temp = weather.temperature
    if -5 <= temp <= 15:
        factors["temperature"] = 100 - abs(temp - 5) * 5  # Optimal around 5°C
    elif temp < -5:
        factors["temperature"] = max(0, 50 + (temp + 5) * 5)
    else:
        factors["temperature"] = max(0, 100 - (temp - 15) * 5)
    
    # Precipitation factor (less is better for hunting, but some moisture good for tracking)
    precip_prob = weather.precipitation_probability
    if precip_prob < 20:
        factors["precipitation"] = 90
    elif precip_prob < 50:
        factors["precipitation"] = 70
    elif precip_prob < 80:
        factors["precipitation"] = 50
    else:
        factors["precipitation"] = 30
    
    # Wind factor (low to moderate wind is best)
    wind = weather.wind_speed
    if wind < 10:
        factors["wind_speed"] = 95
    elif wind < 20:
        factors["wind_speed"] = 80
    elif wind < 30:
        factors["wind_speed"] = 60
    else:
        factors["wind_speed"] = max(20, 100 - wind * 2)
    
    # Cloud cover factor (overcast can be good for hunting)
    cloud = weather.cloud_cover
    factors["cloud_cover"] = 80 if 30 <= cloud <= 70 else 60
    
    # Barometric pressure factor (falling pressure = animal activity)
    pressure = weather.pressure
    if 1005 <= pressure <= 1020:
        factors["pressure"] = 85
    else:
        factors["pressure"] = 70
    
    # Humidity factor
    humidity = weather.humidity
    if 40 <= humidity <= 70:
        factors["humidity"] = 85
    else:
        factors["humidity"] = 65
    
    return {k: round(v, 1) for k, v in factors.items()}


def terrain_to_bionic_factors(terrain: TerrainData) -> Dict[str, float]:
    """
    Convert terrain data to BIONIC module factors (0-100 scale)
    """
    factors = {}
    
    # Elevation factor (optimal varies by species)
    elev = terrain.elevation
    if 200 <= elev <= 600:
        factors["elevation"] = 90
    elif 100 <= elev <= 800:
        factors["elevation"] = 75
    else:
        factors["elevation"] = 60
    
    # Slope factor (moderate slopes preferred)
    if terrain.slope is not None:
        slope = terrain.slope
        if slope < 5:
            factors["slope"] = 70  # Too flat
        elif slope < 15:
            factors["slope"] = 95  # Ideal
        elif slope < 25:
            factors["slope"] = 80
        else:
            factors["slope"] = 50  # Too steep
    
    # Aspect factor (south-facing slopes warmer in Northern Hemisphere)
    if terrain.aspect is not None:
        aspect = terrain.aspect
        # South-facing (135-225°) scores highest for thermal comfort
        if 135 <= aspect <= 225:
            factors["aspect"] = 90
        elif 90 <= aspect <= 270:
            factors["aspect"] = 75
        else:
            factors["aspect"] = 60
    
    return {k: round(v, 1) for k, v in factors.items()}


def vegetation_to_bionic_factors(vegetation: VegetationData) -> Dict[str, float]:
    """
    Convert vegetation data to BIONIC module factors (0-100 scale)
    """
    factors = {}
    
    # NDVI factor (higher = more vegetation = more food/cover)
    ndvi = vegetation.ndvi
    factors["ndvi"] = min(100, max(0, (ndvi + 0.2) * 70))  # Scale -0.2 to 1.0 -> 0-100
    
    # NDWI factor (water availability)
    if vegetation.ndwi is not None:
        ndwi = vegetation.ndwi
        factors["ndwi"] = min(100, max(0, (ndwi + 0.3) * 60))  # Water presence
    
    # Browse availability estimate (based on NDVI)
    factors["browse_availability"] = min(100, max(0, ndvi * 100))
    
    # Forest cover estimate
    factors["forest_cover"] = min(100, max(0, (ndvi + 0.1) * 80))
    
    return {k: round(v, 1) for k, v in factors.items()}


# ============================================
# SINGLETON INSTANCE
# ============================================

_geospatial_service: Optional[GeospatialDataService] = None

async def get_geospatial_service() -> GeospatialDataService:
    """Get or create the geospatial data service singleton"""
    global _geospatial_service
    if _geospatial_service is None:
        _geospatial_service = GeospatialDataService()
    return _geospatial_service
