# BIONIC V5 ULTIME 300% — Registre des Cles API et Identifiants

**Version:** R1 — 2026-03-01
**Statut:** AUDIT COMPLET
**Conformite:** BIONIC V5 300%

---

## Resume

| Categorie | Total | Actifs | Inactifs |
|---|---|---|---|
| Infrastructure | 3 | 3 | 0 |
| Authentification | 3 | 3 | 0 |
| APIs externes (actives) | 3 | 3 | 0 |
| APIs gratuites | 1 | 1 | 0 |
| APIs inactives | 3 | 0 | 3 |
| Autres | 3 | 3 | 0 |
| **TOTAL** | **16** | **13** | **3** |

---

## Cles Actives — Donnees Reelles

### 1. OpenTopography (DEM)
- **Variable:** `OPENTOPOGRAPHY_API_KEY`
- **Module:** DEM_SHADOW, TCVE_REAL
- **Rate limit:** 50 appels/24h
- **Cache:** `dem_cache` MongoDB, TTL 90 jours
- **Statut:** ACTIF, VALIDE

### 2. Copernicus Data Space (Sentinel-2 NDVI)
- **Variables:** `SENTINEL2_CLIENT_ID` + `SENTINEL2_CLIENT_SECRET`
- **Module:** NDVI_SHADOW
- **Auth:** OAuth2 Client Credentials
- **Token URL:** `identity.dataspace.copernicus.eu`
- **Process API:** `sh.dataspace.copernicus.eu`
- **Cache:** `ndvi_cache` MongoDB, TTL 30 jours
- **Compte:** Steeve Ross
- **Statut:** ACTIF, VALIDE

### 3. Open-Meteo (Meteo + Windfield)
- **Variable:** Aucune requise
- **Module:** WEATHER_SHADOW, WINDFIELD, TFE_REAL
- **Cache:** `weather_cache` MongoDB, TTL 6 heures
- **Statut:** ACTIF, GRATUIT

---

## Cles Inactives (Fallback disponible)

| Cle | Module | Fallback | Raison |
|---|---|---|---|
| THERMAL_API_KEY | TFE_REAL | synthetic | En attente activation |
| ML_CLOUD_API_KEY | PHASE_H_ML | sklearn | Strategie locale adoptee |
| STORAGE_API_KEY | REPORT_EXPORT | local_filesystem | En attente activation |

---

## Caches MongoDB

| Collection | TTL | Speedup | Statut |
|---|---|---|---|
| dem_cache | 90 jours | 45x | Actif |
| weather_cache | 6 heures | 117x | Actif |
| ndvi_cache | 30 jours | 200x | Actif |

---

## Fichiers de reference
- `/app/backend/.env` — Variables d'environnement
- `/app/backend/config/api_keys_template.json` — Template officiel
- `/app/backend/config/API_KEYS_REGISTRY.json` — Registre complet versionne
- `/api/v1/system/api-keys/status` — Endpoint de verification en temps reel
