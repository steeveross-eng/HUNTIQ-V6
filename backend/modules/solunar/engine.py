"""
SOLUNAR ENGINE — Calcul solunaire type LUNASOLCAL
====================================================
BCE-4X: Algorithme déterministe pour positions lunaires/solaires.
Calcule: altitude lune 24h, overhead/underfoot, rise/set,
périodes majeures/mineures, fenêtres de chasse de jour.
"""
import math
from datetime import datetime, timedelta, timezone


def _julian_day(dt: datetime) -> float:
    """Jour Julien à partir d'un datetime UTC."""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 400 - 32045
    return jd + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24.0 - 0.5


def _moon_position(jd: float, lat: float, lng: float):
    """Position lunaire simplifiée (altitude, azimut, phase)."""
    d = jd - 2451545.0  # J2000.0

    # Éléments orbitaux lunaires simplifiés
    L = (218.316 + 13.176396 * d) % 360  # longitude moyenne
    M = (134.963 + 13.064993 * d) % 360  # anomalie moyenne
    F = (93.272 + 13.229350 * d) % 360   # argument de latitude

    L_rad = math.radians(L)
    M_rad = math.radians(M)
    F_rad = math.radians(F)

    # Longitude écliptique
    lon_ecl = L + 6.289 * math.sin(M_rad)
    # Latitude écliptique
    lat_ecl = 5.128 * math.sin(F_rad)
    # Distance (km)
    dist = 385001 - 20905 * math.cos(M_rad)

    lon_rad = math.radians(lon_ecl)
    lat_rad = math.radians(lat_ecl)

    # Obliquité de l'écliptique
    epsilon = math.radians(23.439 - 0.0000004 * d)

    # Coordonnées équatoriales
    ra = math.atan2(
        math.sin(lon_rad) * math.cos(epsilon) - math.tan(lat_rad) * math.sin(epsilon),
        math.cos(lon_rad)
    )
    dec = math.asin(
        math.sin(lat_rad) * math.cos(epsilon) +
        math.cos(lat_rad) * math.sin(epsilon) * math.sin(lon_rad)
    )

    # Angle horaire
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    lmst = math.radians((gmst + lng) % 360)
    ha = lmst - ra

    # Altitude
    lat_r = math.radians(lat)
    alt = math.asin(
        math.sin(lat_r) * math.sin(dec) +
        math.cos(lat_r) * math.cos(dec) * math.cos(ha)
    )

    # Phase lunaire (0=nouvelle, 0.5=pleine)
    sun_M = math.radians((357.529 + 0.98560028 * d) % 360)
    sun_L = (280.459 + 0.98564736 * d) % 360
    sun_lon = sun_L + 1.915 * math.sin(sun_M) + 0.020 * math.sin(2 * sun_M)
    phase_angle = (lon_ecl - sun_lon) % 360
    illumination = (1 - math.cos(math.radians(phase_angle))) / 2

    return {
        "altitude": math.degrees(alt),
        "declination": math.degrees(dec),
        "distance_km": dist,
        "illumination": round(illumination, 3),
        "phase_angle": round(phase_angle, 1),
    }


def _sun_position(jd: float, lat: float, lng: float):
    """Position solaire simplifiée."""
    d = jd - 2451545.0
    sun_M = math.radians((357.529 + 0.98560028 * d) % 360)
    sun_L = (280.459 + 0.98564736 * d) % 360
    sun_lon = math.radians(sun_L + 1.915 * math.sin(sun_M))
    epsilon = math.radians(23.439 - 0.0000004 * d)

    ra = math.atan2(math.cos(epsilon) * math.sin(sun_lon), math.cos(sun_lon))
    dec = math.asin(math.sin(epsilon) * math.sin(sun_lon))

    gmst = (280.46061837 + 360.98564736629 * d) % 360
    lmst = math.radians((gmst + lng) % 360)
    ha = lmst - ra

    lat_r = math.radians(lat)
    alt = math.asin(
        math.sin(lat_r) * math.sin(dec) + math.cos(lat_r) * math.cos(dec) * math.cos(ha)
    )
    return {"altitude": math.degrees(alt)}


def compute_solunar(lat: float, lng: float, date_str: str = None):
    """
    Calcul solunaire complet pour une position et une date.
    Retourne: courbe lunaire 24h, événements, périodes, fenêtres de chasse.
    """
    if date_str:
        base = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        base = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Courbe lunaire 24h (résolution 15 min = 96 points)
    curve = []
    moon_max_alt = -90
    moon_min_alt = 90
    overhead_time = None
    underfoot_time = None
    prev_alt = None
    moon_rise = None
    moon_set = None

    for i in range(97):
        dt = base + timedelta(minutes=i * 15)
        jd = _julian_day(dt)
        moon = _moon_position(jd, lat, lng)
        sun = _sun_position(jd, lat, lng)
        alt = moon["altitude"]

        curve.append({
            "hour": round(i * 0.25, 2),
            "time": dt.strftime("%H:%M"),
            "moon_altitude": round(alt, 2),
            "sun_altitude": round(sun["altitude"], 2),
            "illumination": moon["illumination"],
        })

        if alt > moon_max_alt:
            moon_max_alt = alt
            overhead_time = dt.strftime("%H:%M")
        if alt < moon_min_alt:
            moon_min_alt = alt
            underfoot_time = dt.strftime("%H:%M")

        # Détection lever/coucher lune
        if prev_alt is not None:
            if prev_alt < 0 <= alt and moon_rise is None:
                moon_rise = dt.strftime("%H:%M")
            if prev_alt >= 0 > alt and moon_set is None:
                moon_set = dt.strftime("%H:%M")
        prev_alt = alt

    # 2. Phase lunaire
    jd_noon = _julian_day(base + timedelta(hours=12))
    moon_noon = _moon_position(jd_noon, lat, lng)
    illumination = moon_noon["illumination"]
    phase_angle = moon_noon["phase_angle"]

    if phase_angle < 10 or phase_angle > 350:
        phase_name = "Nouvelle lune"
    elif phase_angle < 90:
        phase_name = "Premier croissant"
    elif phase_angle < 100:
        phase_name = "Premier quartier"
    elif phase_angle < 170:
        phase_name = "Gibbeuse croissante"
    elif phase_angle < 190:
        phase_name = "Pleine lune"
    elif phase_angle < 270:
        phase_name = "Gibbeuse décroissante"
    elif phase_angle < 280:
        phase_name = "Dernier quartier"
    else:
        phase_name = "Dernier croissant"

    # Facteur d'intensité lunaire (0-1): pleine lune = max
    lunar_intensity = illumination

    # 3. Lever/coucher du soleil
    sunrise = None
    sunset = None
    for i in range(97):
        dt = base + timedelta(minutes=i * 15)
        jd = _julian_day(dt)
        sun = _sun_position(jd, lat, lng)
        if sun["altitude"] >= 0 and sunrise is None:
            sunrise = dt.strftime("%H:%M")
        if sunrise and sun["altitude"] < 0 and sunset is None:
            sunset = dt.strftime("%H:%M")

    # 4. Périodes majeures et mineures
    def _parse_time(t_str):
        if not t_str:
            return None
        h, m = map(int, t_str.split(":"))
        return h + m / 60.0

    def _format_range(center_h, half_duration):
        if center_h is None:
            return None
        start = max(0, center_h - half_duration)
        end = min(24, center_h + half_duration)
        sh, sm = int(start), int((start % 1) * 60)
        eh, em = int(end), int((end % 1) * 60)
        return {"start": f"{sh:02d}:{sm:02d}", "end": f"{eh:02d}:{em:02d}",
                "start_h": round(start, 2), "end_h": round(end, 2)}

    overhead_h = _parse_time(overhead_time)
    underfoot_h = _parse_time(underfoot_time)
    rise_h = _parse_time(moon_rise)
    set_h = _parse_time(moon_set)

    major_duration = 1.0 + lunar_intensity * 0.5  # 1h-1.5h de chaque côté
    minor_duration = 0.5 + lunar_intensity * 0.25

    periods = {
        "major": [
            {"type": "overhead", "center": overhead_time, **(_format_range(overhead_h, major_duration) or {})},
            {"type": "underfoot", "center": underfoot_time, **(_format_range(underfoot_h, major_duration) or {})},
        ],
        "minor": [],
    }
    if rise_h is not None:
        periods["minor"].append({"type": "moonrise", "center": moon_rise, **_format_range(rise_h, minor_duration)})
    if set_h is not None:
        periods["minor"].append({"type": "moonset", "center": moon_set, **_format_range(set_h, minor_duration)})

    # 5. Fenêtres de chasse de jour (filtrées lever-coucher soleil)
    sunrise_h = _parse_time(sunrise) or 6
    sunset_h = _parse_time(sunset) or 18

    def _filter_daylight(period):
        if "start_h" not in period:
            return None
        s = max(period["start_h"], sunrise_h)
        e = min(period["end_h"], sunset_h)
        if s >= e:
            return None
        sh, sm = int(s), int((s % 1) * 60)
        eh, em = int(e), int((e % 1) * 60)
        duration_min = round((e - s) * 60)
        return {
            "start": f"{sh:02d}:{sm:02d}", "end": f"{eh:02d}:{em:02d}",
            "duration_min": duration_min,
            "source": period["type"],
        }

    hunting_windows = []
    for p in periods["major"] + periods["minor"]:
        w = _filter_daylight(p)
        if w:
            is_major = p in periods["major"]
            intensity = "fort" if is_major and lunar_intensity > 0.6 else "modéré" if is_major else "faible"
            if lunar_intensity > 0.8 and is_major:
                intensity = "extrême"
            w["intensity"] = intensity
            w["color"] = {"extrême": "#DC2626", "fort": "#EF4444", "modéré": "#F59E0B", "faible": "#6B7280"}[intensity]
            hunting_windows.append(w)

    hunting_windows.sort(key=lambda w: w["start"])

    # 6. Score solunaire global
    score = round(lunar_intensity * 60 + len(hunting_windows) * 10, 1)
    score = min(100, score)

    return {
        "type": "solunar",
        "date": base.strftime("%Y-%m-%d"),
        "location": {"lat": lat, "lng": lng},
        "moon": {
            "phase_name": phase_name,
            "illumination": round(illumination * 100, 1),
            "phase_angle": phase_angle,
            "overhead": overhead_time,
            "underfoot": underfoot_time,
            "rise": moon_rise,
            "set": moon_set,
            "max_altitude": round(moon_max_alt, 1),
        },
        "sun": {
            "rise": sunrise,
            "set": sunset,
        },
        "periods": periods,
        "hunting_windows": hunting_windows,
        "curve_24h": curve,
        "solunar_score": score,
        "lunar_intensity": round(lunar_intensity, 3),
    }
