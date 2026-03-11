"""
Territory Module - GPS, Waypoints, Tracks, Guided Routes, GPX
Phase 1.8 - Split from territory.py
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import Response

from ._base import territory_router, get_db, logger, haversine_distance
from .models import (
    WaypointCreate, WaypointResponse,
    TrackCreate, TrackResponse, TrackPointCreate,
    GuidedRouteRequest, GuidedRouteResponse, RouteSegment,
)
from .analysis_layers import calculate_point_probability, SPECIES_HABITAT_RULES


@territory_router.post("/waypoints", response_model=WaypointResponse)
async def create_waypoint(user_id: str, waypoint: WaypointCreate):
    """Create a new waypoint - UNIFIED single source of truth"""
    database = await get_db()
    waypoint_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    waypoint_doc = {
        "_id": waypoint_id, "user_id": user_id,
        "latitude": waypoint.latitude, "longitude": waypoint.longitude,
        "name": waypoint.name, "description": waypoint.description or waypoint.notes,
        "waypoint_type": waypoint.waypoint_type, "icon": waypoint.icon,
        "created_at": now,
        "active": waypoint.active if waypoint.active is not None else True,
        "color": waypoint.color, "notes": waypoint.notes or waypoint.description
    }
    await database.territory_waypoints.insert_one(waypoint_doc)
    return WaypointResponse(
        id=waypoint_id, latitude=waypoint.latitude, longitude=waypoint.longitude,
        name=waypoint.name, description=waypoint.description or waypoint.notes,
        waypoint_type=waypoint.waypoint_type, icon=waypoint.icon, created_at=now,
        active=waypoint_doc["active"], color=waypoint.color,
        notes=waypoint.notes or waypoint.description, user_id=user_id
    )


@territory_router.get("/waypoints")
async def list_waypoints(user_id: str):
    """List all waypoints for a user - UNIFIED single source of truth"""
    database = await get_db()
    waypoints = await database.territory_waypoints.find({"user_id": user_id}).sort("created_at", -1).to_list(500)
    return [WaypointResponse(
        id=str(wp['_id']), latitude=wp['latitude'], longitude=wp['longitude'],
        name=wp['name'], description=wp.get('description'),
        waypoint_type=wp.get('waypoint_type', 'custom'), icon=wp.get('icon'),
        created_at=wp.get('created_at', datetime.now(timezone.utc)),
        active=wp.get('active', True), color=wp.get('color'),
        notes=wp.get('notes') or wp.get('description'), user_id=wp.get('user_id')
    ) for wp in waypoints]


@territory_router.delete("/waypoints/{waypoint_id}")
async def delete_waypoint(waypoint_id: str, user_id: str):
    """Delete a waypoint"""
    database = await get_db()
    result = await database.territory_waypoints.delete_one({"_id": waypoint_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Waypoint not found")
    return {"status": "deleted", "id": waypoint_id}


@territory_router.post("/tracks", response_model=TrackResponse)
async def create_track(user_id: str, track: TrackCreate):
    """Start a new GPS track recording"""
    database = await get_db()
    track_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    track_doc = {
        "_id": track_id, "user_id": user_id, "name": track.name,
        "description": track.description, "points": [],
        "started_at": now, "ended_at": None, "is_active": True,
        "distance_km": 0, "created_at": now
    }
    await database.territory_tracks.insert_one(track_doc)
    return TrackResponse(
        id=track_id, name=track.name, description=track.description,
        points_count=0, distance_km=0, duration_minutes=0,
        started_at=now, ended_at=None, is_active=True
    )


@territory_router.post("/tracks/{track_id}/points")
async def add_track_point(track_id: str, user_id: str, point: TrackPointCreate):
    """Add a point to an active track"""
    database = await get_db()
    track = await database.territory_tracks.find_one({"_id": track_id, "user_id": user_id})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    if not track.get('is_active'):
        raise HTTPException(status_code=400, detail="Track is not active")
    now = datetime.now(timezone.utc)
    point_data = {
        "lat": point.latitude, "lon": point.longitude, "alt": point.altitude,
        "accuracy": point.accuracy, "speed": point.speed, "heading": point.heading,
        "timestamp": now
    }
    additional_distance = 0
    if track['points']:
        last_point = track['points'][-1]
        additional_distance = haversine_distance(
            last_point['lat'], last_point['lon'], point.latitude, point.longitude
        )
    await database.territory_tracks.update_one(
        {"_id": track_id},
        {"$push": {"points": point_data}, "$inc": {"distance_km": additional_distance}}
    )
    return {"status": "added", "track_id": track_id, "point": point_data,
            "additional_distance_km": round(additional_distance, 3)}


@territory_router.post("/tracks/{track_id}/stop")
async def stop_track(track_id: str, user_id: str):
    """Stop recording a track"""
    database = await get_db()
    now = datetime.now(timezone.utc)
    result = await database.territory_tracks.update_one(
        {"_id": track_id, "user_id": user_id, "is_active": True},
        {"$set": {"is_active": False, "ended_at": now}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Active track not found")
    track = await database.territory_tracks.find_one({"_id": track_id})
    return {"status": "stopped", "track_id": track_id, "ended_at": now,
            "total_points": len(track.get('points', [])),
            "total_distance_km": round(track.get('distance_km', 0), 2)}


@territory_router.get("/tracks")
async def list_tracks(user_id: str, active_only: bool = False):
    """List all tracks for a user"""
    database = await get_db()
    query = {"user_id": user_id}
    if active_only:
        query["is_active"] = True
    tracks = await database.territory_tracks.find(query).sort("created_at", -1).to_list(100)
    results = []
    for track in tracks:
        duration = 0
        if track.get('started_at'):
            end_time = track.get('ended_at') or datetime.now(timezone.utc)
            duration = (end_time - track['started_at']).total_seconds() / 60
        results.append(TrackResponse(
            id=str(track['_id']), name=track['name'], description=track.get('description'),
            points_count=len(track.get('points', [])),
            distance_km=round(track.get('distance_km', 0), 2),
            duration_minutes=round(duration, 1), started_at=track['started_at'],
            ended_at=track.get('ended_at'), is_active=track.get('is_active', False)
        ))
    return results


@territory_router.get("/tracks/{track_id}")
async def get_track(track_id: str, user_id: str):
    """Get track details including all points"""
    database = await get_db()
    track = await database.territory_tracks.find_one({"_id": track_id, "user_id": user_id})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    duration = 0
    if track.get('started_at'):
        end_time = track.get('ended_at') or datetime.now(timezone.utc)
        duration = (end_time - track['started_at']).total_seconds() / 60
    return {
        "id": str(track['_id']), "name": track['name'], "description": track.get('description'),
        "points": track.get('points', []),
        "points_count": len(track.get('points', [])),
        "distance_km": round(track.get('distance_km', 0), 2),
        "duration_minutes": round(duration, 1), "started_at": track['started_at'],
        "ended_at": track.get('ended_at'), "is_active": track.get('is_active', False)
    }


@territory_router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, user_id: str):
    """Delete a track"""
    database = await get_db()
    result = await database.territory_tracks.delete_one({"_id": track_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"status": "deleted", "id": track_id}


# --- GUIDED ROUTE ---

def optimize_waypoint_order(waypoints: list, start_point: dict = None, optimization: str = 'balanced') -> list:
    """Optimize waypoint order using a nearest-neighbor algorithm with probability weighting."""
    if len(waypoints) <= 1:
        return waypoints
    remaining = waypoints.copy()
    ordered = []
    if start_point:
        current = start_point
    else:
        current = remaining.pop(0)
        ordered.append(current)
    while remaining:
        best_next = None
        best_score = float('inf')
        for wp in remaining:
            distance = haversine_distance(
                current['latitude'], current['longitude'],
                wp['latitude'], wp['longitude']
            )
            prob_score = wp.get('probability', {}).get('score', 50)
            if optimization == 'probability':
                score = distance - (prob_score * 0.05)
            elif optimization == 'distance':
                score = distance
            else:
                score = distance - (prob_score * 0.02)
            if score < best_score:
                best_score = score
                best_next = wp
        if best_next:
            remaining.remove(best_next)
            ordered.append(best_next)
            current = best_next
    return ordered


@territory_router.post("/analysis/guided-route", response_model=GuidedRouteResponse)
async def generate_guided_route(request: GuidedRouteRequest, user_id: str):
    """Generate an optimized guided route through waypoints with probability analysis."""
    database = await get_db()
    waypoints_cursor = database.territory_waypoints.find({"user_id": user_id})
    waypoints = await waypoints_cursor.to_list(100)
    if len(waypoints) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 waypoints sont necessaires pour creer un parcours guide")
    waypoints_with_prob = []
    for wp in waypoints:
        prob = calculate_point_probability(wp['latitude'], wp['longitude'], request.species)
        waypoints_with_prob.append({
            "id": str(wp['_id']), "name": wp['name'],
            "latitude": wp['latitude'], "longitude": wp['longitude'],
            "waypoint_type": wp.get('waypoint_type', 'custom'), "probability": prob
        })
    start_point = None
    if request.start_from_current_position and request.current_lat and request.current_lng:
        start_point = {
            "id": "current_position", "name": "Position actuelle",
            "latitude": request.current_lat, "longitude": request.current_lng,
            "waypoint_type": "start",
            "probability": calculate_point_probability(request.current_lat, request.current_lng, request.species)
        }
    optimized_waypoints = optimize_waypoint_order(waypoints_with_prob, start_point, request.optimize_for)
    if start_point and start_point not in optimized_waypoints:
        optimized_waypoints.insert(0, start_point)
    segments = []
    total_distance = 0
    total_prob = 0
    highest_prob_zone = optimized_waypoints[0] if optimized_waypoints else None
    for i in range(len(optimized_waypoints) - 1):
        wp1 = optimized_waypoints[i]
        wp2 = optimized_waypoints[i + 1]
        distance = haversine_distance(wp1['latitude'], wp1['longitude'], wp2['latitude'], wp2['longitude'])
        prob = wp2['probability']
        recommendations = []
        if prob['score'] >= 70:
            recommendations.append(f"Zone a forte probabilite pour {request.species}")
            recommendations.append("Restez vigilant et silencieux")
        elif prob['score'] >= 50:
            recommendations.append("Zone de passage probable")
            recommendations.append("Observez les signes de presence")
        else:
            recommendations.append("Zone de transit - continuez vers le prochain point")
        for factor in prob['factors'][:2]:
            recommendations.append(f"{factor}")
        segment = RouteSegment(
            from_waypoint={"id": wp1['id'], "name": wp1['name'], "lat": wp1['latitude'], "lng": wp1['longitude'], "probability": wp1['probability']['score']},
            to_waypoint={"id": wp2['id'], "name": wp2['name'], "lat": wp2['latitude'], "lng": wp2['longitude'], "probability": wp2['probability']['score']},
            distance_km=round(distance, 2), probability_score=prob['score'],
            probability_level=prob['level'], color=prob['color'], recommendations=recommendations
        )
        segments.append(segment)
        total_distance += distance
        total_prob += prob['score']
        if prob['score'] > highest_prob_zone['probability']['score']:
            highest_prob_zone = wp2
    avg_prob = total_prob / len(segments) if segments else 0
    estimated_hours = total_distance / 3.0
    high_zones = sum(1 for s in segments if s.probability_level == 'high')
    summary = f"Parcours optimise de {round(total_distance, 1)} km passant par {len(optimized_waypoints)} points. "
    summary += f"{high_zones} zone(s) a forte probabilite d'observation ({request.species}). "
    summary += f"Probabilite moyenne: {round(avg_prob)}%. "
    summary += f"Temps estime: {round(estimated_hours, 1)}h."
    return GuidedRouteResponse(
        route_id=str(uuid.uuid4()), species=request.species,
        total_distance_km=round(total_distance, 2),
        estimated_time_hours=round(estimated_hours, 1),
        average_probability=round(avg_prob, 1),
        highest_probability_zone={
            "name": highest_prob_zone['name'], "latitude": highest_prob_zone['latitude'],
            "longitude": highest_prob_zone['longitude'],
            "probability": highest_prob_zone['probability']['score'],
            "factors": highest_prob_zone['probability']['factors']
        },
        segments=segments,
        waypoint_order=[{
            "id": wp['id'], "name": wp['name'], "lat": wp['latitude'], "lng": wp['longitude'],
            "probability": wp['probability']['score'], "probability_level": wp['probability']['level'],
            "color": wp['probability']['color']
        } for wp in optimized_waypoints],
        summary=summary
    )


# --- GPX IMPORT/EXPORT ---

GPX_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="BIONIC Territory Analysis"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>{name}</name>
    <desc>{description}</desc>
    <time>{time}</time>
  </metadata>
'''
GPX_FOOTER = '</gpx>'


@territory_router.get("/export/gpx")
async def export_gpx(user_id: str, include_waypoints: bool = True, include_tracks: bool = True):
    """Export all waypoints and tracks as GPX file"""
    database = await get_db()
    now = datetime.now(timezone.utc).isoformat()
    gpx_content = GPX_HEADER.format(name="BIONIC Territory Export", description=f"Export des donnees de territoire - {now}", time=now)
    if include_waypoints:
        waypoints = await database.territory_waypoints.find({"user_id": user_id}).to_list(1000)
        for wp in waypoints:
            gpx_content += f'''  <wpt lat="{wp['latitude']}" lon="{wp['longitude']}">
    <name>{wp['name']}</name>
    <desc>{wp.get('description', '')}</desc>
    <type>{wp['waypoint_type']}</type>
    <time>{wp['created_at'].isoformat() if wp.get('created_at') else now}</time>
  </wpt>
'''
    if include_tracks:
        tracks = await database.territory_tracks.find({"user_id": user_id, "is_active": False}).to_list(100)
        for track in tracks:
            if track.get('points') and len(track['points']) > 0:
                gpx_content += f'''  <trk>
    <name>{track['name']}</name>
    <desc>{track.get('description', '')}</desc>
    <trkseg>
'''
                for point in track['points']:
                    alt_str = f'<ele>{point["alt"]}</ele>' if point.get('alt') else ''
                    time_str = f'<time>{point["timestamp"].isoformat()}</time>' if point.get('timestamp') else ''
                    gpx_content += f'''      <trkpt lat="{point['lat']}" lon="{point['lon']}">
        {alt_str}
        {time_str}
      </trkpt>
'''
                gpx_content += '''    </trkseg>
  </trk>
'''
    gpx_content += GPX_FOOTER
    return Response(content=gpx_content, media_type="application/gpx+xml",
                    headers={"Content-Disposition": f"attachment; filename=bionic_territory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gpx"})


@territory_router.post("/import/gpx")
async def import_gpx(user_id: str = Form(...), file: UploadFile = File(...)):
    """Import waypoints and tracks from GPX file"""
    import xml.etree.ElementTree as ET
    database = await get_db()
    content = await file.read()
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid GPX file: {e}")
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    imported_waypoints = 0
    imported_tracks = 0
    for wpt in root.findall('.//gpx:wpt', ns) + root.findall('.//wpt'):
        try:
            lat = float(wpt.get('lat'))
            lon = float(wpt.get('lon'))
            name_elem = wpt.find('gpx:name', ns) or wpt.find('name')
            name = name_elem.text if name_elem is not None else "Waypoint importe"
            desc_elem = wpt.find('gpx:desc', ns) or wpt.find('desc')
            desc = desc_elem.text if desc_elem is not None else None
            type_elem = wpt.find('gpx:type', ns) or wpt.find('type')
            wp_type = type_elem.text if type_elem is not None and type_elem.text in ['observation', 'camera', 'cache', 'stand', 'water', 'trail_start', 'custom'] else 'custom'
            waypoint_id = str(uuid.uuid4())
            waypoint_doc = {
                "_id": waypoint_id, "user_id": user_id,
                "latitude": lat, "longitude": lon, "name": name,
                "description": desc, "waypoint_type": wp_type, "icon": None,
                "created_at": datetime.now(timezone.utc), "imported": True
            }
            await database.territory_waypoints.insert_one(waypoint_doc)
            imported_waypoints += 1
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to import waypoint: {e}")
            continue
    for trk in root.findall('.//gpx:trk', ns) + root.findall('.//trk'):
        try:
            name_elem = trk.find('gpx:name', ns) or trk.find('name')
            name = name_elem.text if name_elem is not None else f"Trace importe {datetime.now().strftime('%Y-%m-%d')}"
            desc_elem = trk.find('gpx:desc', ns) or trk.find('desc')
            desc = desc_elem.text if desc_elem is not None else None
            points = []
            total_distance = 0
            for trkseg in trk.findall('.//gpx:trkseg', ns) + trk.findall('.//trkseg'):
                for trkpt in trkseg.findall('gpx:trkpt', ns) + trkseg.findall('trkpt'):
                    lat = float(trkpt.get('lat'))
                    lon = float(trkpt.get('lon'))
                    ele_elem = trkpt.find('gpx:ele', ns) or trkpt.find('ele')
                    alt = float(ele_elem.text) if ele_elem is not None else None
                    time_elem = trkpt.find('gpx:time', ns) or trkpt.find('time')
                    timestamp = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00')) if time_elem is not None else datetime.now(timezone.utc)
                    if points:
                        total_distance += haversine_distance(points[-1]['lat'], points[-1]['lon'], lat, lon)
                    points.append({"lat": lat, "lon": lon, "alt": alt, "timestamp": timestamp})
            if points:
                track_id = str(uuid.uuid4())
                track_doc = {
                    "_id": track_id, "user_id": user_id, "name": name,
                    "description": desc, "points": points,
                    "started_at": points[0]['timestamp'] if points else datetime.now(timezone.utc),
                    "ended_at": points[-1]['timestamp'] if points else datetime.now(timezone.utc),
                    "is_active": False, "distance_km": total_distance,
                    "created_at": datetime.now(timezone.utc), "imported": True
                }
                await database.territory_tracks.insert_one(track_doc)
                imported_tracks += 1
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to import track: {e}")
            continue
    return {"status": "success", "imported_waypoints": imported_waypoints,
            "imported_tracks": imported_tracks,
            "message": f"Importe {imported_waypoints} waypoints et {imported_tracks} traces"}
