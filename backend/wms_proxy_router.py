"""
WMS Proxy Router - Proxy pour les services WMS qui ne supportent pas CORS

Ce module permet de:
1. Proxifier les requêtes WMS depuis le frontend
2. Contourner les restrictions CORS des services gouvernementaux
3. Ajouter du cache pour les tuiles fréquemment demandées

Auteur: BIONIC™ Team
"""

from fastapi import APIRouter, HTTPException, Response
import httpx
import logging
import asyncio
from typing import Optional
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Concurrency limiter for WMS proxy — prevents event loop starvation
_WMS_SEMAPHORE = asyncio.Semaphore(4)

router = APIRouter(prefix="/api/wms-proxy", tags=["WMS Proxy"])

# Cache simple pour les tuiles WMS (en mémoire)
WMS_CACHE = {}
CACHE_DURATION = timedelta(hours=1)
MAX_CACHE_SIZE = 500

# Services WMS autorisés (whitelist)
ALLOWED_WMS_HOSTS = [
    "servicescarto.mern.gouv.qc.ca",
    "servicescarto.mffp.gouv.qc.ca",
    "ca.nfis.org",
    "geo.api.gov.bc.ca",
    "maps.geogratis.gc.ca",
    "hydro.nationalmap.gov",
    "geoegl.msp.gouv.qc.ca"
]

def is_host_allowed(url: str) -> bool:
    """Vérifie si l'hôte de l'URL est dans la whitelist"""
    for host in ALLOWED_WMS_HOSTS:
        if host in url:
            return True
    return False

def get_cache_key(url: str, params: dict) -> str:
    """Génère une clé de cache unique pour la requête"""
    key_str = url + str(sorted(params.items()))
    return hashlib.md5(key_str.encode()).hexdigest()

def clean_cache():
    """Nettoie les entrées expirées du cache"""
    global WMS_CACHE
    now = datetime.now()
    expired_keys = [k for k, v in WMS_CACHE.items() if now - v['timestamp'] > CACHE_DURATION]
    for k in expired_keys:
        del WMS_CACHE[k]
    
    # Limiter la taille du cache
    if len(WMS_CACHE) > MAX_CACHE_SIZE:
        oldest_keys = sorted(WMS_CACHE.keys(), key=lambda k: WMS_CACHE[k]['timestamp'])[:100]
        for k in oldest_keys:
            del WMS_CACHE[k]

@router.get("/tile")
async def proxy_wms_tile(
    url: str,
    service: str = "WMS",
    request: str = "GetMap",
    version: str = "1.3.0",
    layers: str = "0",
    styles: str = "",
    format: str = "image/png",
    transparent: str = "true",
    width: int = 256,
    height: int = 256,
    crs: Optional[str] = None,
    srs: Optional[str] = None,
    bbox: str = ""
):
    """
    Proxy une requête WMS GetMap
    
    Cette route permet de récupérer des tuiles WMS depuis des services
    qui ne supportent pas CORS (comme les services gouvernementaux du Québec).
    
    # Vérification de sécurité
    if not is_host_allowed(url):
        raise HTTPException(status_code=403, detail="WMS host not allowed")
    
    Note: Utilise curl en subprocess pour contourner les problèmes de connexion
    avec httpx/requests depuis certains environnements cloud.
    """
    if not bbox:
        raise HTTPException(status_code=400, detail="BBOX parameter required")
    
    # Construire l'URL complète (supporte les URLs avec paramètres existants comme ?DATASTORE=...)
    # Support WMS 1.1.1 (SRS) et WMS 1.3.0 (CRS)
    effective_crs = crs or srs or "EPSG:3857"
    crs_param_name = "SRS" if srs and not crs else "CRS"
    separator = '&' if '?' in url else '?'
    wms_url = f"{url}{separator}SERVICE={service}&REQUEST={request}&VERSION={version}&LAYERS={layers}&STYLES={styles}&FORMAT={format}&TRANSPARENT={transparent}&WIDTH={width}&HEIGHT={height}&{crs_param_name}={effective_crs}&BBOX={bbox}"
    
    # Vérifier le cache
    wms_params = {"url": wms_url}
    cache_key = get_cache_key(url, wms_params)
    if cache_key in WMS_CACHE:
        cached = WMS_CACHE[cache_key]
        if datetime.now() - cached['timestamp'] < CACHE_DURATION:
            logger.debug(f"WMS cache hit for {layers}")
            return Response(
                content=cached['data'],
                media_type=format,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600"
                }
            )
    
    # Nettoyer le cache périodiquement
    if len(WMS_CACHE) > MAX_CACHE_SIZE * 0.9:
        clean_cache()
    
    try:
        async with _WMS_SEMAPHORE:
            # Non-blocking subprocess via asyncio
            proc = await asyncio.create_subprocess_exec(
                'curl', '-s', '-L', wms_url, '--connect-timeout', '5', '--max-time', '8',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                logger.warning(f"WMS proxy timeout for {url}")
                raise HTTPException(status_code=504, detail="WMS service timeout")
            
            if proc.returncode != 0:
                raise HTTPException(status_code=502, detail="WMS service error")
            
            content = stdout
        
        # Mettre en cache
        WMS_CACHE[cache_key] = {
            'data': content,
            'timestamp': datetime.now()
        }
        
        logger.debug(f"WMS proxy: {layers} - {len(content)} bytes")
        
        return Response(
            content=content,
            media_type=format,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WMS proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def proxy_wms_capabilities(url: str):
    """
    Proxy une requête WMS GetCapabilities
    """
    if not is_host_allowed(url):
        raise HTTPException(status_code=403, detail="WMS host not allowed")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            params = {
                "SERVICE": "WMS",
                "REQUEST": "GetCapabilities",
                "VERSION": "1.3.0"
            }
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            return Response(
                content=response.content,
                media_type="application/xml",
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
    except Exception as e:
        logger.error(f"WMS capabilities proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check")
async def check_wms_availability(url: str):
    """
    Vérifie la disponibilité d'un service WMS
    
    Note: Les services WMS gouvernementaux du Québec peuvent ne pas être 
    accessibles depuis certains environnements cloud/datacenter en raison
    de restrictions géographiques ou de sécurité.
    """
    logger.info(f"Checking WMS availability for: {url}")
    
    if not is_host_allowed(url):
        logger.warning(f"WMS host not allowed: {url}")
        return {"available": False, "error": "Host not allowed"}
    
    try:
        import time
        import subprocess
        
        start_time = time.time()
        
        # Utiliser curl en subprocess car httpx/requests ont des problèmes de connexion
        # avec certains services gouvernementaux depuis les environnements cloud
        separator = '&' if '?' in url else '?'
        result = subprocess.run(
            [
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                f"{url}{separator}SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.3.0",
                '--connect-timeout', '10'
            ],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        status_code = int(result.stdout) if result.stdout.isdigit() else 0
        
        logger.info(f"WMS check response: status={status_code}, time={elapsed_ms}ms")
        
        return {
            "available": status_code == 200,
            "status_code": status_code,
            "response_time_ms": elapsed_ms
        }
            
    except subprocess.TimeoutExpired:
        logger.warning(f"WMS check timeout")
        return {"available": False, "error": "Timeout"}
    except Exception as e:
        logger.error(f"WMS check error: {type(e).__name__}: {e}")
        return {"available": False, "error": str(e)}

logger.info("WMS Proxy Router initialized")
