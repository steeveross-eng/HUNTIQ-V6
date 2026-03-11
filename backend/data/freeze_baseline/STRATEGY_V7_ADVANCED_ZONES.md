# STRATEGIE D'IDENTIFICATION DES ZONES 200-300% PLUS AVANCEE
## MON TERRITOIRE BIONIC — VISION V7+

**Date :** 2026-03-10
**Statut :** Specification strategique complete
**Branche :** bionic_v6_lab → bionic_v7_strategy

---

# 1. FORMES DES ZONES — ORGANICITE & PRECISION

## 1.1 Diagnostic V5/V6

| Aspect | V5/V6 actuel | Limitation |
|--------|-------------|-----------|
| Contours | Marching Squares + Chaikin ×4 | Formes organiques mais basees sur un raster regulier (grille NxN) |
| Decoupe | V6: Shapely difference | Decoupe nette mais sans lissage post-trim |
| Relief | NON integre | Contours ignorent completement la topographie |
| Plans d'eau | Exclusion binaire | Pas d'epousement des berges |
| Lisieres foret | NON integre | Aucune detection de transition couvert/ouvert |
| Couvert vegetal | NON integre | Meme traitement foret dense vs clairiere |

## 1.2 Strategie V7 — Zones Terrain-Aware

### 1.2.1 Principes

1. **Morphologie terrain-adaptive** — Les contours de zone s'adaptent aux courbes de niveau, lisieres et berges
2. **Snapping topologique** — Les bords de zone "collent" aux features naturelles proches (<30m)
3. **Lissage Chaikin contextuel** — Plus de lissage en terrain plat, moins en terrain accidente (preserves les cretes)
4. **Fusion intelligente** — Deux zones adjacentes du meme type se fusionnent si la distance < 50m et meme layer

### 1.2.2 Operations Shapely avancees

```python
# Pipeline de forme V7
def shape_zone_v7(raw_polygon, terrain_features, config):
    """
    1. snap_to_shorelines() — Coller les bords proches des berges
    2. snap_to_edges() — Coller aux lisieres foret detectees
    3. conform_to_contours() — Adapter aux courbes de niveau
    4. smooth_adaptive() — Chaikin avec intensite variable selon pente
    5. trim_exclusions() — Decoupe V6 propre
    6. validate_topology() — Verifier validite Shapely + min_area
    """
```

### 1.2.3 Sources de donnees necessaires

| Donnee | Source | Disponibilite | Usage |
|--------|--------|--------------|-------|
| Courbes de niveau | SRTM/ASTER DEM (30m) | Gratuit, telecharger | Snapping contours |
| Elevation | SRTM via API Elevation | Disponible | Calcul pentes |
| Couvert forestier | Canopee Canada (RNCAN) / MODIS VCF | Gratuit | Detection lisieres |
| Berges | OSM water (deja disponible) | Deja integre | Snapping berges |
| NDVI | Sentinel-2 / MODIS | Gratuit, API | Transition vegetation |

---

# 2. PERTINENCE CHASSE — ZONES "VIVANTES" POUR LE GIBIER

## 2.1 Architecture multi-signaux

```
           ┌──────────────────────────────────────────────┐
           │           COUCHE COMPORTEMENTALE             │
           │  (besoins espece × conditions × temps)       │
           └────────────────────┬─────────────────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
    ▼                           ▼                           ▼
┌─────────┐             ┌─────────────┐             ┌──────────┐
│ HABITAT │             │ DEPLACEMENTS│             │ PRESSION │
│ (statique)│           │ (dynamique) │             │ (externe)│
│          │             │             │             │          │
│ - couvert│             │ - heure     │             │ - routes │
│ - eau    │             │ - saison    │             │ - urbain │
│ - nourr. │             │ - meteo     │             │ - chasse │
│ - topo   │             │ - rut       │             │ - activite│
└─────────┘             └─────────────┘             └──────────┘
    │                           │                           │
    └───────────────────────────┼───────────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │  SCORE COMPOSITE  │
                    │  + TYPOLOGIE ZONE │
                    │  + HOTSPOT MAP    │
                    └───────────────────┘
```

## 2.2 Besoins par espece — Matrice comportementale

### 2.2.1 Orignal (Moose)

| Besoin | Indicateurs terrain | Score facteur | Saison |
|--------|-------------------|--------------|--------|
| **Alimentation** | Couvert mixte, saules, bouleaux blancs, zones regeneration post-coupe, bord plan d'eau | ×1.0-1.5 | Toute saison |
| **Repos/Couvert** | Foret mature conifere (epinette, sapin), densite canopee >60%, pente <15% | ×1.0-1.3 | Toute saison |
| **Rut** | Zones ouvertes pres eau, tourbiere/marais, clairiere avec visibilite | ×1.2-2.0 | Sept-Oct |
| **Refuge chaleur** | Foret dense nord, proximite eau (<200m), altitude >200m, ombrage | ×1.3-1.8 | Juillet-Aout |
| **Refuge pression** | Foret dense >500m route, terrain accidente, distance urbain >1km | ×1.2-1.6 | Saison chasse |
| **Corridor** | Fond vallee, lisiere foret/clairiere, ruisseau, isthme entre lacs | ×1.0-1.4 | Automne |

### 2.2.2 Chevreuil (White-tailed Deer)

| Besoin | Indicateurs terrain | Score facteur | Saison |
|--------|-------------------|--------------|--------|
| **Alimentation** | Borde foret feuillue, champs en friche, vergers, clairiere riche | ×1.0-1.5 | Toute saison |
| **Repos** | Sous-bois dense, conifere bas, pente sud, protege du vent | ×1.0-1.3 | Hiver surtout |
| **Rut** | Zones ecotone, lisieres, frottoirs (arbres frotte), grattoirs | ×1.5-2.0 | Nov |
| **Refuge chaleur** | Foret feuillue mature, bord ruisseau, versant nord | ×1.2-1.5 | Ete |
| **Refuge pression** | Forets denses avec couvert bas, ravage (zones hivernage connues) | ×1.3-1.8 | Nov-Dec |
| **Corridor** | Lignes de crete boisees, lisieres continues, haies bocageres | ×1.0-1.3 | Automne |

### 2.2.3 Ours Noir (Black Bear)

| Besoin | Indicateurs terrain | Score facteur | Saison |
|--------|-------------------|--------------|--------|
| **Alimentation** | Bleuets (zones post-feu/coupe), chene, hetre, cours d'eau poisson, ruches | ×1.0-1.8 | Printemps-Automne |
| **Repos** | Foret mature, terrain rocheux, taniere, pente >20% | ×1.0-1.3 | Toute saison |
| **Refuge** | Terrain accidente, > 1km urbain, denivele >100m, foret dense | ×1.2-1.5 | Saison chasse |
| **Corridor** | Fonds vallees, rivages, cretes boisees continues | ×1.0-1.3 | Printemps-Automne |

### 2.2.4 Wapiti (Elk)

| Besoin | Indicateurs terrain | Score facteur | Saison |
|--------|-------------------|--------------|--------|
| **Alimentation** | Prairies naturelles, paturages, vergers, zones herbacees | ×1.0-1.5 | Toute saison |
| **Repos** | Foret ouverte, pente douce, proximite eau | ×1.0-1.2 | Toute saison |
| **Rut** | Prairies ouvertes (arenes), clairiere, bugling zones | ×1.5-2.0 | Sept-Oct |
| **Refuge** | Foret dense altitude, terrain accidente, > 2km route | ×1.2-1.6 | Saison chasse |
| **Corridor** | Vallees larges, cols montagneux, lisieres prairies-forets | ×1.0-1.3 | Automne |

## 2.3 Facteurs externes — Impact dynamique

### 2.3.1 Meteo

| Condition | Impact sur zone | Scoring |
|-----------|---------------|---------|
| **Vent fort (>30 km/h)** | Deplacement vers zones protegees (vallees, foret dense) | Refuge ×1.5, Ouvert ×0.5 |
| **Pluie continue** | Alimentation reduite, repos accru, couvert dense | Repos ×1.3, Alimentation ×0.7 |
| **Froid intense (<-15C)** | Regroupement dans ravages, economie d'energie | Repos ×1.5, Corridor ×0.5 |
| **Chaleur (>25C)** | Deplacement vers eau et ombre | Refuge chaleur ×2.0, Ouvert ×0.3 |
| **Neige fraiche** | Deplacement vers couvert dense, traces visibles | Repos ×1.2, Pistage ×2.0 |
| **Brouillard** | Gibier plus actif, visibilite reduite | Alimentation ×1.3, Corridors ×1.2 |

### 2.3.2 Topographie

| Feature | Signal | Scoring |
|---------|--------|---------|
| **Fond de vallee** | Corridor naturel, accumulation humidite, vegetation riche | Corridor ×1.5, Alimentation ×1.3 |
| **Crete** | Ligne de deplacement, visibilite, vent | Corridor crete ×1.2, Repos ×0.7 |
| **Pente sud** | Plus chaud, decrochage neige plus tot, vegetation precoce | Alimentation ×1.3 printemps |
| **Pente nord** | Plus frais, conifere dense, ombrage | Refuge chaleur ×1.5, Repos ×1.2 |
| **Plateau** | Zone de repos, alimentation diversifiee | Repos ×1.2, Alimentation ×1.1 |
| **Col/selle** | Point de passage oblige | Corridor ×2.0 |
| **Terrasse fluviale** | Alimentation riche, acces eau | Alimentation ×1.4, Eau ×1.3 |

### 2.3.3 Proximite eau

| Distance | Impact | Type |
|----------|--------|------|
| **< 50m** | Zone critique (abreuvoir, alimentation aquatique) | Hotspot eau |
| **50-200m** | Zone preferentielle (acces facile) | Alimentation ×1.2 |
| **200-500m** | Zone acceptable | Neutre |
| **> 500m** | Zone defavorable pour especes dependantes | Repos ×0.9 (orignal) |

## 2.4 Identification des Hotspots

### 2.4.1 Algorithme de detection

```
HOTSPOT SCORE = Σ(signal_weight × signal_value) × species_modifier × season_modifier

Ou:
  signal_weight = importance relative du signal (0-1)
  signal_value = valeur normalisee du signal (0-1)
  species_modifier = facteur espece (cf. matrices 2.2)
  season_modifier = facteur saisonnier (cf. 2.3.1)
```

### 2.4.2 Categorie de hotspots

| Hotspot | Definition | Signaux cles | Score min |
|---------|-----------|-------------|----------|
| **Hotspot alimentation** | Zone a forte densite de ressources alimentaires | NDVI eleve, lisiere, couvert mixte, altitude < median | 0.75 |
| **Hotspot repos** | Zone de couvert dense avec peu de perturbation | Canopee >70%, pente <20%, > 500m route | 0.70 |
| **Hotspot rut** | Zone ouverte pres couvert, visibilite, eau proche | Clairiere, marais, < 300m foret dense, saison sept-oct | 0.80 |
| **Hotspot refuge** | Zone de repli sous pression | Terrain accidente, foret dense, > 800m route, > 1.5km urbain | 0.65 |
| **Hotspot passage** | Goulet topographique ou ecologique | Col, isthme, lisiere continue, fond vallee etroit | 0.70 |

---

# 3. SCORE & TYPOLOGIE DES ZONES

## 3.1 Typologie enrichie V7

| Type | Code | Couleur carte | Icone | Description |
|------|------|-------------|-------|------------|
| **Alimentation** | `feed` | Vert emeraude #2E7D32 | Feuille | Zone riche en ressources alimentaires |
| **Repos / Couvert** | `rest` | Bleu nuit #1A237E | Lune | Zone de repos, couvert dense protecteur |
| **Rut / Reproduction** | `rut` | Rouge profond #B71C1C | Coeur | Zone de rut, arenes, frottoirs |
| **Refuge chaleur** | `heat_ref` | Orange #E65100 | Soleil | Zone ombragee, proximite eau, versant nord |
| **Refuge pression** | `hunt_ref` | Violet #4A148C | Bouclier | Zone de repli sous pression de chasse |
| **Transition / Corridor** | `corridor` | Ambre #FF8F00 | Fleche | Zone de passage entre habitats |
| **Mixte** | `mixed` | Gris #455A64 | Cercle | Zone multi-fonction, score equilibre |

## 3.2 Systeme de scoring multi-criteres

### 3.2.1 Sous-scores (0-100)

| Sous-score | Ponderation | Signaux |
|-----------|------------|---------|
| **Nourriture** (food) | 25% | NDVI, couvert mixte, lisieres, altitude, saison |
| **Securite** (safety) | 20% | Distance route, distance urbain, densite canopee, terrain accidente |
| **Accessibilite** (access) | 15% | Distance piste, proximite eau, pente < 30% |
| **Discretion** (stealth) | 15% | Couvert, topographie, distance sentier, vent |
| **Eau** (water) | 10% | Distance plan d'eau, type (lac, ruisseau), debit |
| **Topographie** (topo) | 10% | Pente, orientation, altitude relative, exposition |
| **Dynamique** (dynamic) | 5% | Heure, meteo, phase lunaire, pression de chasse |

### 3.2.2 Score global

```
SCORE_GLOBAL = Σ(sous_score_i × poids_i) × penalite_exclusion × bonus_hotspot

Ou:
  penalite_exclusion = facteur V6 (0.15-1.10)
  bonus_hotspot = 1.0-1.3 si zone est un hotspot detecte
```

### 3.2.3 Classification automatique

```python
def classify_zone(scores: dict) -> str:
    """Determine le type de zone dominant."""
    type_map = {
        "feed": scores["food"] * 0.5 + scores["water"] * 0.2 + scores["topo"] * 0.3,
        "rest": scores["safety"] * 0.5 + scores["stealth"] * 0.3 + scores["topo"] * 0.2,
        "rut": scores["food"] * 0.2 + scores["access"] * 0.3 + scores["topo"] * 0.3 + season_rut_bonus,
        "heat_ref": scores["water"] * 0.4 + scores["stealth"] * 0.3 + topo_north_bonus,
        "hunt_ref": scores["safety"] * 0.6 + scores["stealth"] * 0.3 + scores["topo"] * 0.1,
        "corridor": corridor_score,  # calculated separately
    }
    return max(type_map, key=type_map.get)
```

### 3.2.4 Format de sortie API

```json
{
  "zone_id": "z_moose_feed_001",
  "type": "feed",
  "type_label": "Zone d'alimentation",
  "species": "moose",
  "score_global": 82,
  "scores": {
    "food": 91,
    "safety": 68,
    "access": 75,
    "stealth": 55,
    "water": 85,
    "topo": 70,
    "dynamic": 60
  },
  "hotspot": true,
  "hotspot_type": "alimentation",
  "confidence": "high",
  "penalty_factor": 0.92,
  "exclusion_engine": "v6",
  "season_relevance": {
    "spring": 0.7,
    "summer": 0.9,
    "fall": 1.0,
    "winter": 0.5
  },
  "sex_preference": "both",
  "geometry": { "type": "Polygon", "coordinates": [...] }
}
```

---

# 4. ZONES DE PASSAGE & TRANSITION — REPRESENTATION LINEAIRE AVANCEE

## 4.1 Architecture des corridors

### 4.1.1 Types de corridors

| Type | Representation | Depart | Arrivee | Logique |
|------|---------------|--------|---------|---------|
| **Corridor reel** | Ligne continue | Zone repos | Zone alimentation | Donnees terrain + topographie |
| **Corridor rut** | Ligne continue epaisse | Zone repos | Zone rut | Saison rut, meme logic + arenes |
| **Corridor refuge** | Ligne continue | Zone quelconque | Zone refuge | Pression chasse, pentes |
| **Corridor IA** | Ligne pointillee | Zone A | Zone B | Estime par ML/heuristique |

### 4.1.2 Generation algorithmique

```
PIPELINE CORRIDOR:

1. IDENTIFICATION DES TERMINAUX
   → Pour chaque paire (zone_A, zone_B) de types complementaires:
     - repos ↔ alimentation (quotidien)
     - repos ↔ rut (saisonnier)
     - repos ↔ refuge (conditionnel)
     - alimentation ↔ eau (quotidien)

2. GENERATION DU CHEMIN OPTIMAL
   → A* pathfinding sur grille cout:
     - Cout = f(pente, couvert, distance_route, distance_eau, altitude)
     - Contraintes: pente < 35%, evite eau profonde, evite urbain
     - Preference: fond vallee, lisiere, ruisseau, col

3. LISSAGE + SNAPPING
   → Chaikin smoothing
   → Snap aux features terrain (ruisseau, lisiere, courbe niveau)

4. CLASSIFICATION CONFIANCE
   → Reel (confiance haute): donnees terrain directes
   → IA (confiance moyenne): heuristique + interpolation
   → Hypothetique (confiance basse): extrapolation seule

5. DIFFERENTIATION MALE/FEMELLE
   → Males: rayon plus grand, terrain plus expose, altitude plus haute
   → Femelles: rayon plus court, couvert plus dense, proximite eau
```

### 4.1.3 Grille de cout A*

| Feature terrain | Cout male | Cout femelle | Unite |
|----------------|-----------|-------------|-------|
| Foret dense | 1.0 | 0.7 | (moins = prefere) |
| Foret ouverte | 0.8 | 1.0 | |
| Clairiere | 0.6 | 1.5 | |
| Lisiere | 0.5 | 0.6 | (tous preferent) |
| Fond vallee | 0.4 | 0.5 | (corridor naturel) |
| Crete | 0.7 | 1.3 | (males OK, femelles evitent) |
| Pente >25% | 1.5 | 2.5 | (penalise tous, surtout femelles) |
| Proximite eau <50m | 0.6 | 0.5 | (attirant) |
| Proximite route <100m | 2.0 | 3.0 | (repulsif, surtout femelles) |
| Zone urbaine | 10.0 | 10.0 | (quasi-infranchissable) |
| Col/selle | 0.3 | 0.4 | (passage naturel) |
| Marais/wetland | 0.8 | 1.2 | (orignal OK, chevreuil evite) |

## 4.2 Differentiation males / femelles

### 4.2.1 Parametres comportementaux

| Parametre | Male | Femelle | Source |
|-----------|------|---------|--------|
| Rayon deplacement quotidien | 3-8 km | 1-4 km | Telemetrie MFFP |
| Rayon rut | 8-15 km | 2-5 km | Etudes comportementales |
| Tolerance exposition | Haute | Basse | Ethologie |
| Preference couvert | Moderee | Forte | Etudes habitat |
| Tolerance pente | Haute | Moderee | Observations terrain |
| Activite nocturne | Elevee | Moderee | Telemetrie GPS |
| Distance min route | 200m | 400m | Etudes impact routier |
| Distance min urbain | 500m | 800m | Etudes perturbation |

### 4.2.2 Representation cartographique

| Element | Male | Femelle | Mixte/Neutre |
|---------|------|---------|-------------|
| **Couleur** | #1565C0 (bleu profond) | #C62828 (rouge profond) | #F57F17 (ambre) |
| **Epaisseur** | 3.0px | 2.5px | 2.0px |
| **Opacite** | 0.85 | 0.80 | 0.70 |
| **Style (reel)** | Continu | Continu | Continu |
| **Style (IA)** | Pointille [12, 6] | Pointille [8, 4] | Pointille [10, 5] |

### 4.2.3 Icones de terminaux

| Terminal | Male | Femelle |
|----------|------|---------|
| Zone repos | Cercle plein bleu | Cercle plein rouge |
| Zone alimentation | Losange bleu | Losange rouge |
| Zone rut | Triangle bleu | Triangle rouge |
| Zone refuge | Carre bleu | Carre rouge |

## 4.3 Corridors IA (estimes) — Lignes semi-continues

### 4.3.1 Quand generer un corridor IA ?

| Condition | Type corridor IA | Confiance |
|-----------|-----------------|-----------|
| Deux zones proches (<2km) sans donnees terrain entre elles | Interpolation | Moyenne (0.5-0.7) |
| Zone isolee (>3km de la plus proche) | Extrapolation | Basse (0.3-0.5) |
| Terrain inconnu (pas de DEM/NDVI) | Heuristique | Basse (0.2-0.4) |
| Deduction comportementale (heure, saison) | Prediction | Moyenne (0.5-0.7) |

### 4.3.2 Representation visuelle

```
LEGENDE CORRIDOR:

────────────── Corridor reel male (donnees terrain)
─ ─ ─ ─ ─ ─ ─ Corridor IA male (estime)
━━━━━━━━━━━━━━ Corridor reel femelle (donnees terrain)
╴ ╴ ╴ ╴ ╴ ╴ ╴ Corridor IA femelle (estime)
·············· Corridor neutre IA (faible confiance)
```

### 4.3.3 Tooltip corridor (survol carte)

```json
{
  "corridor_id": "corr_moose_m_001",
  "type": "daily_feed",
  "sex": "male",
  "confidence": "high",
  "source": "terrain",
  "from_zone": "z_moose_rest_003",
  "to_zone": "z_moose_feed_007",
  "distance_m": 1850,
  "estimated_travel_time": "25-40 min",
  "terrain": "fond vallee, lisiere, ruisseau",
  "season_relevance": {"fall": 1.0, "spring": 0.7}
}
```

## 4.4 Palette & lisibilite

### 4.4.1 Palette complete

| Element | Couleur | Hex | Usage |
|---------|---------|-----|-------|
| Corridor male reel | Bleu profond | #1565C0 | Ligne continue |
| Corridor male IA | Bleu clair | #42A5F5 | Ligne pointillee |
| Corridor femelle reel | Rouge profond | #C62828 | Ligne continue |
| Corridor femelle IA | Rouge clair | #EF5350 | Ligne pointillee |
| Corridor mixte reel | Ambre | #F57F17 | Ligne continue |
| Corridor mixte IA | Ambre clair | #FFB74D | Ligne pointillee |
| Zone alimentation | Vert emeraude | #2E7D32 | Polygone fill |
| Zone repos | Bleu nuit | #1A237E | Polygone fill |
| Zone rut | Rouge vin | #B71C1C | Polygone fill |
| Zone refuge chaleur | Orange brule | #E65100 | Polygone fill |
| Zone refuge pression | Violet | #4A148C | Polygone fill |
| Zone corridor | Ambre | #FF8F00 | Polygone fill |

### 4.4.2 Lisibilite fond de carte

| Fond carte | Ajustements |
|-----------|-------------|
| Satellite | Outline blanc 1px, ombre portee, opacite +10% |
| Topographique | Pas d'outline, opacite standard |
| Terrain (relief) | Outline noir 0.5px, fill opacite -10% |
| Sombre | Couleurs saturees +20%, outline lumineux |

---

# 5. EXHAUSTIVITE DE L'ANALYSE — SIGNAUX & COUCHES

## 5.1 Signaux deja disponibles dans BIONIC

| Signal | Source | Integre V5/V6 | Utilisation V7 |
|--------|--------|---------------|---------------|
| **Eau (water)** | OSM Overpass | Oui (exclusion) | Exclusion + scoring positif (proximite) |
| **Wetland** | OSM Overpass | Oui (preserve) | Scoring positif orignal, negatif chevreuil |
| **Routes** | OSM Overpass | Oui (exclusion) | Exclusion + pression + corridors |
| **Urbain** | OSM Overpass | Oui (exclusion) | Exclusion + pression |
| **Infrastructure** | OSM Overpass | Oui (exclusion) | Exclusion |
| **Raster comportemental** | Simplex noise | Oui (base zones) | Enrichir avec vrais signaux |
| **Espece** | Config | Oui (parametres) | Matrice complete comportementale |
| **Couvert forestier (proxy)** | Non integre mais OSM a landuse=forest | Partiel | A enrichir |

## 5.2 Signaux supplementaires a integrer (court terme — 6 mois)

| Signal | Source | Format | Cout | Impact |
|--------|--------|--------|------|--------|
| **Elevation DEM** | SRTM 30m (NASA) | GeoTIFF | Gratuit | CRITIQUE — pente, aspect, corridors |
| **NDVI** | Sentinel-2 (ESA) | Raster 10m | Gratuit | ELEVE — vegetation, lisieres |
| **Couvert canopee** | RNCAN / Global Forest Watch | Raster 30m | Gratuit | ELEVE — couvert, densite |
| **Meteo temps reel** | Environnement Canada API | JSON | Gratuit | MOYEN — dynamique |
| **Phase lunaire** | Calcul astronomique | Calcul | Gratuit | FAIBLE — activite nocturne |
| **Coupes forestieres** | WMS MFFP (deja tente) | WMS | Gratuit si acces | MOYEN — regeneration, alimentation |

## 5.3 Signaux supplementaires a integrer (moyen terme — 12 mois)

| Signal | Source | Format | Impact |
|--------|--------|--------|--------|
| **LST (Land Surface Temperature)** | MODIS | Raster 1km | MOYEN — refuges thermiques |
| **Snow Cover** | MODIS/Sentinel | Raster | MOYEN — deplacements hiver |
| **Donnees telemetrie faune** | MFFP/universites | GPS points | CRITIQUE — validation, ML training |
| **Pression de chasse** | Donnees permis / zones de chasse | Polygones | ELEVE — refuges |
| **Routes forestieres** | Base foret ouverte MFFP | Lignes | MOYEN — acces, perturbation |

## 5.4 Architecture evolutive

```
                    ┌─────────────────────────────┐
                    │      SIGNAL REGISTRY        │
                    │  (plugin architecture)       │
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
     ┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
     │  SIGNAL OSM  │       │ SIGNAL DEM  │       │ SIGNAL NDVI │
     │ (Overpass)   │       │ (SRTM)      │       │ (Sentinel)  │
     └──────────────┘       └─────────────┘       └─────────────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  RASTER FUSION  │
                          │  (weighted sum)  │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │  ZONE GENERATOR │
                          │  (V7 organic)   │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
             ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
             │ EXCLUSION   │ │ SCORING  │ │ CORRIDOR   │
             │ ENGINE V6   │ │ ENGINE   │ │ GENERATOR  │
             └─────────────┘ └──────────┘ └────────────┘
```

### 5.4.1 Interface plugin signal

```python
class SignalProvider:
    """Interface pour ajouter de nouveaux signaux sans modifier le pipeline."""
    
    name: str               # "dem", "ndvi", "meteo"
    weight: float           # 0.0-1.0, poids dans la fusion
    resolution_m: float     # Resolution en metres
    cache_ttl_s: int        # Duree de cache
    
    def fetch(self, bounds: dict) -> np.ndarray:
        """Retourne un raster normalise [0, 1]."""
        
    def is_available(self, bounds: dict) -> bool:
        """Verifie si les donnees sont disponibles pour la zone."""
```

---

# 6. OBJECTIF FINAL — GAINS ATTENDUS

## 6.1 Comparaison V5 → V6 → V7

| Metrique | V5 | V6 (actuel) | V7 (cible) | Gain V5→V7 |
|----------|----|----|-----|-----------|
| **Precision exclusion** | ~50% (5 points) | ~98% (Shapely exact) | ~99% (Shapely + terrain) | **200%** |
| **Qualite formes** | Organique basique | Organique + trim | Organique terrain-adaptive | **250%** |
| **Pertinence chasse** | Score brut (bruit) | Score + penalite | Multi-criteres + hotspot | **300%** |
| **Zones utilisables** | Zones generiques | Zones + exclusion precise | Zones typees + corridors | **300%** |
| **Corridors** | Aucun | Aucun | Reels + IA estimes | **Nouveau** |
| **Differentiation sexe** | Aucune | Aucune | Male/femelle corridors | **Nouveau** |
| **Hotspots** | Aucun | Aucun | 5 types detectes | **Nouveau** |
| **Dynamique meteo** | Aucune | Aucune | Ajustement temps reel | **Nouveau** |
| **Donnees terrain** | OSM seul | OSM + buffers | OSM + DEM + NDVI + canopee | **300%** |
| **Temps pipeline** | 4-12s | 4.5-13s | 6-18s (acceptable) | +50% max |

## 6.2 Parametres cles recommandes

| Parametre | Valeur V7 | Justification |
|-----------|-----------|---------------|
| Resolution raster | 100-120 | Plus fin pour terrain-aware |
| max_zones_per_layer | 12 | Plus de zones typees |
| Chaikin iterations | 6 | Plus lisse |
| min_area_m2 | 3000 | Accepter des zones plus petites (refuges) |
| max_area_m2 | 100000 | Accepter des zones plus grandes (corridors) |
| Corridor max_length_km | 5 | Limiter les corridors trop longs |
| Corridor max_count | 20 | Par viewport |
| Hotspot score_threshold | 0.70 | Minimum pour etre declare hotspot |
| DEM resolution | 30m (SRTM) | Bon compromis precision/performance |
| NDVI resolution | 10m (Sentinel) ou 250m (MODIS) | Selon disponibilite |

## 6.3 Plan d'implementation recommande

### Phase V6.5 (immédiat — deja fait)
- [x] Moteur exclusion V6 Shapely
- [x] Buffers adaptatifs par sous-type
- [x] Zone trimming
- [x] Feature flag V5/V6
- [x] 28/28 tests regression verts

### Phase V7.0 — Scoring & Typologie (P0 — 2-3 semaines)
- [ ] Systeme de scoring multi-criteres
- [ ] Typologie enrichie des zones (feed, rest, rut, heat_ref, hunt_ref, corridor, mixed)
- [ ] Classification automatique
- [ ] Format API enrichi

### Phase V7.1 — DEM & Topographie (P0 — 3-4 semaines)
- [ ] Integration SRTM 30m
- [ ] Calcul pentes, aspects, TPI
- [ ] Raster fusion (comportemental + topo)
- [ ] Snapping topologique des zones

### Phase V7.2 — Corridors (P1 — 4-6 semaines)
- [ ] Generateur de corridors A*
- [ ] Differentiation male/femelle
- [ ] Corridors IA estimes
- [ ] Representation cartographique (lignes, couleurs, pointilles)

### Phase V7.3 — NDVI & Couvert (P1 — 4-6 semaines)
- [ ] Integration Sentinel-2 ou MODIS NDVI
- [ ] Detection lisieres automatique
- [ ] Couvert canopee
- [ ] Morphologie terrain-adaptive des zones

### Phase V7.4 — Dynamique (P2 — 6-8 semaines)
- [ ] Integration meteo temps reel (Environnement Canada)
- [ ] Ajustement scores dynamique
- [ ] Phase lunaire
- [ ] UI affichage conditionnel

### Phase V7.5 — ML & Telemetrie (P3 — 3-6 mois)
- [ ] Entrainement modele sur donnees telemetrie (si disponible)
- [ ] Validation terrain
- [ ] Corridors ML
- [ ] Hotspots predicts

---

## 6.4 Impacts frontend (futur)

| Composant | Modification requise | Priorite |
|-----------|---------------------|----------|
| `TerritoryMap.jsx` | Afficher zones par type (couleur, icone) | V7.0 |
| `ExclusionOverlayLayer.jsx` | Aucun changement | — |
| Nouveau: `CorridorLayer.jsx` | Dessiner les corridors (lignes continues/pointillees) | V7.2 |
| Nouveau: `HotspotMarkerLayer.jsx` | Marqueurs hotspot avec tooltip | V7.0 |
| Nouveau: `ZoneScorePanel.jsx` | Panneau lateral avec sous-scores | V7.0 |
| Nouveau: `CorridorLegend.jsx` | Legende male/femelle/IA | V7.2 |
| Nouveau: `WeatherOverlay.jsx` | Overlay meteo dynamique | V7.4 |

---

**FIN DU DOCUMENT — STRATEGIE V7 200-300% PLUS AVANCEE**
