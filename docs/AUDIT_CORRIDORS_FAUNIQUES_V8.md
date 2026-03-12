# AUDIT CORRIDORS FAUNIQUES BIONIC V8
## Document de validation pre-Phase Corridors V9
## Date: 12 Mars 2026

---

## 1. DEFINITION ACTUELLE

### Definition interne
Un corridor faunique dans BIONIC V8 est une **connexion geospatiale lineaire** (LineString GeoJSON) generee entre deux zones fonctionnelles (alimentation, repos, rut, habitats, etc.) representant un **chemin de deplacement probable** pour la faune.

Le corridor est genere par l'algorithme A* en minimisant un cout de traversee base sur le type de terrain. Chaque corridor est classifie selon la **typologie WWF** (World Wildlife Fund) en fonction de sa distance/largeur.

### Finalite du corridor
La finalite est **triple** dans le modele actuel :

| Finalite | Implementation reelle | Status |
|----------|----------------------|--------|
| **Ecologique** | Classification WWF (macro/biologique/conservation), benefices ecologiques (echanges genetiques, adaptation climatique, attenuation fragmentation) | IMPLEMENTEE — scoring calcule mais **non affiche au frontend** |
| **Comportementale** | Connexion entre zones fonctionnelles (alimentation→repos, rut→habitats, etc.) selon priorites de connectivite par type de zone | IMPLEMENTEE — via `ZONE_CONNECTIVITY_PRIORITY` et `CONNECT_PAIRS` |
| **Predictive** | Pathfinding A* terrain-aware pour chemins optimaux, lissage Bezier pour naturalisation | IMPLEMENTEE — A* a 93% de succes |

### CE QUI MANQUE
- Aucune **donnee reelle DEM** (elevation SRTM) — le terrain est derive des types de zones, pas de l'elevation
- Aucune **donnee reelle NDVI** — la vegetation est inferee des couches
- Aucune **pression humaine reelle** — la valeur `human_pressure` est hardcodee a `0.1`
- Aucune **donnee hydrographique reelle** — les cours d'eau ne sont pas integres comme barrieres
- Le corridor represente un chemin **probable** mais pas **observe** (tous les corridors actuels sont `source: "corridor_10x"`, aucun `source: "real"`)

---

## 2. ARCHITECTURE ACTUELLE

### Classification WWF
Le systeme utilise la classification WWF basee sur la **largeur/distance** :

| Niveau | Label | Critere | Couleur | Largeur ligne | Opacite |
|--------|-------|---------|---------|---------------|---------|
| MACRO | Macro-corridor | > 5 km | #FF5722 (rouge) | 5px | 0.9 |
| BIOLOGICAL | Corridor biologique | 1-5 km | #FF9800 (orange) | 3.5px | 0.85 |
| CONSERVATION | Corridor de conservation | < 1 km | #FFC107 (jaune) | 2.5px | 0.8 |

**PROBLEME IDENTIFIE** : La classification utilise `distance * 0.3` comme proxy de largeur (`classify_corridor_wwf(best_dist * 0.3)`). Cela signifie :
- Distance < 3.33 km → Conservation (< 1 km largeur)
- Distance 3.33 - 16.67 km → Biologique
- Distance > 16.67 km → Macro

Or les corridors sont limites a **3000m max** (`best_dist > 3000: continue`), donc **tous les corridors sont inevitablement "conservation"** (distance * 0.3 = max 900m < 1000m). La classification macro et biologique est **structurellement inaccessible** dans les parametres actuels.

**Il n'existe pas de classification gris/jaune/orange/rouge/rouge raye.** La classification est uniquement WWF (3 niveaux).

### Logique geometrique
- **Type geometrique** : `LineString` GeoJSON (ligne, pas polygone)
- **Generation** : A* sur grille discrete → lissage Bezier (smoothing_factor=0.3)
- **Aucun buffer** : Les corridors sont des lignes sans largeur semantique
- **Aucune zone circulaire** : Chaque corridor est une polyline point-a-point
- **Resolution grille A*** : Adaptative selon distance (30m pour < 300m, 60m pour < 800m, 120m pour < 1500m, 200m sinon)

---

## 3. LOGIQUE DE GENERATION

### Algorithme principal : A* (A-star)
```
Fichier: backend/modules/bionic_engine_p0/services/corridor_10x.py
Classe: CorridorPathfinder
```

**Fonctionnement** :
1. Grille discrete avec resolution adaptative (30-200m)
2. Cout de traversee par type de terrain (`TERRAIN_COSTS`)
3. Heuristique : distance euclidienne
4. Snapping des positions sur la grille
5. Lissage post-traitement (moyenne ponderee des points adjacents)
6. **Fallback** : Bezier quadratique si A* echoue (max_iterations atteint)

### Donnees influencant la generation

| Donnee | Source reelle | Status |
|--------|--------------|--------|
| **Type de terrain** | Derive du `layer_id` des zones (habitats→mature_forest, alimentation→forest_edge, etc.) | SIMULE — pas de donnees raster reelles |
| **Pente** | Hardcodee a 5° partout (`"slope": 5`) | SIMULE |
| **Pression humaine** | Hardcodee a 0.1 partout (`"human_pressure": 0.1`) | SIMULE |
| **Relief (DEM)** | ABSENT — `dem_enhanced: false` pour tous les corridors | NON IMPLEMENTE |
| **NDVI** | ABSENT — pas de donnees de vegetation reelle | NON IMPLEMENTE |
| **Eau** | Type "water_body" dans `TERRAIN_COSTS` (cout 8.0) mais pas de donnees reelles | PARTIEL |
| **Routes** | Types "road_crossing" (4.5), "highway" (12.0), "urban_edge" (5.0) dans les couts | PARTIEL — couts definis mais non alimentes par donnees reelles |

### Poids et ponderations

**Couts de terrain A*** (`TERRAIN_COSTS`):
| Categorie | Exemples | Cout |
|-----------|----------|------|
| Faible (prefere) | Vallee, coulee, ravine, bande boisee, ripisylve | 1.0 - 1.2 |
| Moyen (acceptable) | Foret mixte, mature, coniferes, plateau | 1.3 - 1.8 |
| Eleve (a eviter) | Champ ouvert, agriculture, coupe recente | 2.5 - 4.0 |
| Prohibitif | Urbain (10), eau (8), falaise (15), autoroute (12) | 8.0 - 15.0 |

**Score composite du corridor** :
```
score = connectivity * 0.40 + terrain * 0.25 + habitat * 0.25 + fragmentation * 0.20
```
**MAIS** : Dans `_build_corridor_feature_astar`, le score est calcule differemment :
```python
score = connectivity * 0.4 + fz["score"] * 0.3 + tz["score"] * 0.3
```
Ou `fz["score"]` et `tz["score"]` sont hardcodes a **50** pour toutes les zones.
Donc : `score = connectivity * 0.4 + 50 * 0.3 + 50 * 0.3 = connectivity * 0.4 + 30`

Le score `terrain` (65.0) et `habitat` (70.0) dans `scoring.subscores` sont **hardcodes**, pas calcules.

---

## 4. CONTRAINTES SPATIALES

### Zone active 2 km²
- Le backend utilise `bounds` (south, north, west, east) base sur `radius = 0.015` (~1.67 km) autour du waypoint
- Les corridors sont generes entre zones fonctionnelles **presentes dans ces bounds**
- L'algorithme A* utilise une marge de `margin = 0.02` (~2.2 km) pour la recherche de chemin

### Pourquoi certains corridors apparaissent en dehors de la zone
1. **Marge A*** : La marge de 0.02° permet au pathfinder de chercher des chemins en dehors du perimetre strict de 2km²
2. **Pas de clipping** : Les corridors generes ne sont **pas clippes** aux bounds de la zone active — un corridor qui commence dans la zone peut sortir pour contourner un obstacle
3. **`in_perimeter: true`** : Ce champ est toujours `true` (hardcode) — il n'y a pas de validation reelle

### Regles empechant un corridor de recouvrir une habitation
**AUCUNE REGLE ACTIVE**. Les regles theoriques existent :
- `urban_edge` : cout 5.0 dans `TERRAIN_COSTS`
- `urban` : cout 10.0 (prohibitif)
- `perturbation_humaine` : penalite -80 dans `AVOID_ZONES`

**MAIS** : Ces couts ne sont jamais injectes dans `terrain_data` car la grille de terrain est construite uniquement a partir des `zone_polygons` (types de zones fonctionnelles). Il n'y a **aucune source de donnees immobilieres, cadastrales ou OSM** qui injecterait des cellules "urban" dans la grille.

---

## 5. INTEGRATION AVEC LES MOTEURS BIONIC

### Moteurs influencant les corridors aujourd'hui

| Moteur | Influence reelle | Details |
|--------|-----------------|---------|
| **Movement Engine** | OUI (seul actif) | A* pathfinding, classification WWF, scoring connectivite |
| **Weather Engine** | NON (partiel) | Le meteo influence les scores de zones mais **pas les corridors** — `weather_metadata.influence_multipliers` n'est pas applique aux scores de corridors |
| **Nutrition Engine** | NON | N'existe pas encore |
| **Daily Routine Engine** | NON | N'existe pas encore |
| **Disturbance Engine** | NON | N'existe pas encore |
| **Phenology Engine** | NON | N'existe pas encore |
| **Typology Engine** | NON | N'existe pas encore |
| **Learning Engine** | NON | N'existe pas encore |
| **Habitat Enhancement** | NON | N'existe pas encore |

### Comment les moteurs modifient-ils les corridors

**Etat actuel** : Seul le Movement Engine (A* + classification WWF) genere et score les corridors. Les autres moteurs n'ont **aucune influence** sur :
- **Le score** : Fixe a `connectivity * 0.4 + 30` (zones a score 50 hardcode)
- **La classification** : Toujours "conservation" (distance * 0.3 < 1000m)
- **La geometrie** : Determinee uniquement par les couts de terrain A* (simules)

---

## 6. SCORING

### Formule exacte du score "Corridors & Ecologie V8"
Le score **affiche** dans le panneau CorridorsEcologyPanel est la **moyenne arithmetique** des scores individuels de chaque corridor :

```javascript
// CorridorsEcologyPanel.jsx
avgScore += c.score || 0;
// ...
avgScore: corridors.length ? Math.round(avgScore / corridors.length) : 0,
```

Ou `c.score` vient du backend via :
```python
# zone_engine_core_v2.py, ligne 309
score = round((connectivity * 0.4 + fz["score"] * 0.3 + tz["score"] * 0.3), 1)
```

Avec `fz["score"] = tz["score"] = 50` (hardcode), le score depend uniquement de la **connectivite** :
```
score = connectivity * 0.4 + 30
```

La connectivite est calculee comme : `(priority_from + priority_to) / 2` ou les priorites vont de 70 (thermique) a 100 (alimentation).

Donc les scores corridors oscillent entre **58 et 70** avec une moyenne autour de **60**.

### Comment le score corridors influence le SCORE GLOBAL V8
**IL NE L'INFLUENCE PAS.** Le Score Global V8 est calcule separement :

```javascript
// MonTerritoireBionicPage.jsx, ligne 732-741
const displayScore = useMemo(() => {
    if (globalScore) return globalScore;  // Du hook useBionicScoring (jamais calcule dans le flux actuel)
    if (bionicZones.length > 0) {
        const validScores = bionicZones.map(z => z.score || 0).filter(s => s > 0);
        return Math.round(validScores.reduce((a, b) => a + b, 0) / validScores.length);
    }
    return null;
}, [globalScore, bionicZones]);
```

Le Score Global = **moyenne des scores des zones** (pas des corridors).

### Pourquoi l'ecart (60/100 corridors vs 33/100 global)
- **Score corridors (60)** : Moyenne des `connectivity * 0.4 + 30` pour chaque corridor
- **Score global (33)** : Moyenne des `z.score` pour chaque zone affichee

Les deux scores sont **completement independants** et mesurent des choses differentes :
- Le score corridor = qualite de connexion entre zones
- Le score global = qualite des zones elles-memes (penalites d'exclusion, surface, position)

**Il n'y a aucun mecanisme de ponderation ou d'agregation** entre les deux.

---

## 7. NORMES ARCHITECTURALES

### Normes suivies actuellement
| Norme | Respect | Details |
|-------|---------|---------|
| Modularite | PARTIEL | `corridor_10x.py` est autonome MAIS `_generate_corridors_10x` est defini dans `zone_engine_core_v2.py` (logique dispersee) |
| Absence de duplication | OUI | Le scoring et la classification sont dans un seul fichier |
| Absence de contamination | PARTIEL | Le corridor_10x service est importe mais `_build_corridor_feature_astar` et `_find_astar_path` sont des fonctions globales dans zone_engine_core |
| Coherence visuelle | OUI | Classification WWF avec couleurs coherentes (rouge/orange/jaune) |
| Coherence logique | NON | Score hardcode (terrain=65, habitat=70, zone_score=50), classification structurellement limitee a "conservation" |

### Garanties manquantes
1. **La logique de generation** (`_generate_corridors_10x`, `_build_terrain_grid`, `_find_astar_path`, `_build_corridor_feature_astar`) est dans `zone_engine_core_v2.py` au lieu d'etre dans `corridor_10x.py` — **violation de responsabilite unique**
2. **Les scores subscores** (`terrain: 65.0`, `habitat: 70.0`) sont hardcodes — **violation de coherence logique**
3. **Le score des zones sources** (`fz["score"] = 50`) est hardcode — **violation de coherence logique**
4. **`in_perimeter: true`** est toujours vrai — **violation de tracabilite**
5. **`sex: "both"`** est toujours la meme valeur — **violation de precision comportementale**

---

## 8. CONFORMITE BCE-MAX / BCE-4X

### Regles BCE actuellement appliquees aux corridors

| Regle | Code | Description | Status |
|-------|------|-------------|--------|
| `CORRIDOR_MISSING` | `check_corridors_visible()` | Verifie que `corridors_count > 0` | ACTIVE |
| `auto_load_corridors` | `MANDATORY_FEATURES` | Les corridors doivent etre affiches automatiquement | ACTIVE |
| Couche "corridors" obligatoire | `MANDATORY_LAYERS` | La couche corridors doit etre disponible | ACTIVE |

### Regles BCE NON appliquees
| Regle manquante | Description | Impact |
|-----------------|-------------|--------|
| **Validation score range** | Verifier que les scores sont dans [0, 100] et non hardcodes | HAUT |
| **Validation geometrie** | Verifier que les corridors ne debordent pas du perimetre | HAUT |
| **Validation classification** | Verifier que les 3 niveaux WWF sont accessibles | MOYEN |
| **Validation anti-overlap habitation** | Verifier qu'aucun corridor ne traverse une zone urbaine | HAUT |
| **Validation continuite** | Verifier que `validate_corridor_continuity()` est appelee (elle existe mais n'est JAMAIS appelee dans le pipeline) | MOYEN |
| **Validation coherence score global** | Verifier que les corridors influencent le score global | HAUT |
| **Regression scoring** | Detecter si les scores sont statiques entre sessions | MOYEN |

### Tests automatiques existants
- Test BCE endpoint (`GET /api/bce/status`) — verifie les couches et corridors count
- Test certification V8 (8/8 PASS) — verifie la presence de corridors

### Tests manquants
1. **Test unitaire A*** : Verifier que le pathfinder trouve un chemin optimal connu
2. **Test scoring dynamique** : Verifier que les subscores ne sont pas hardcodes
3. **Test classification diversite** : Verifier que les 3 niveaux WWF sont atteignables
4. **Test perimetre** : Verifier que les corridors restent dans les bounds ± tolerance
5. **Test regression score** : Comparer les scores entre sessions pour detecter des valeurs statiques
6. **Test anti-habitation** : Verifier qu'aucun corridor ne traverse de zone urbaine
7. **Test integration meteo** : Verifier que les multiplicateurs meteo s'appliquent aux corridors

---

## 9. LIMITES ACTUELLES

### Limitations connues

| # | Limitation | Severite | Cause racine |
|---|-----------|----------|-------------|
| 1 | **Classification toujours "conservation"** | HAUTE | `dist * 0.3 < 1000` pour tous les corridors (max 3000m) |
| 2 | **Scores partiellement hardcodes** | HAUTE | `terrain=65`, `habitat=70`, `zone_score=50` non calcules |
| 3 | **Terrain simule** | HAUTE | Grille de terrain derivee des types de zones, pas de DEM/NDVI reel |
| 4 | **Pression humaine absente** | HAUTE | `human_pressure=0.1` partout, pas de donnees OSM |
| 5 | **Corridors hors perimetre** | MOYENNE | Marge A* de 0.02° sans clipping post-generation |
| 6 | **Score global independant** | MOYENNE | Corridors et zones ont des scores non-agreges |
| 7 | **Pas de differenciation male/femelle** | MOYENNE | `sex: "both"` toujours |
| 8 | **`in_perimeter` toujours true** | BASSE | Pas de validation reelle |
| 9 | **Logique dispersee** | BASSE | Generation dans zone_engine, service dans corridor_10x |
| 10 | **`validate_corridor_continuity()` jamais appelee** | BASSE | Fonction existe mais non utilisee dans le pipeline |
| 11 | **Max 20 corridors** | BASSE | Limite hardcodee `corridor_id >= 20` |
| 12 | **Enrichissement `enrich_corridor()` jamais appele** | MOYENNE | Le service corridor_10x a une methode complete d'enrichissement qui n'est jamais invoquee dans le pipeline |

### Causes des ecarts observes sur MON TERRITOIRE
1. **Score global 33 vs corridors 60** : Les deux metriques mesurent des choses differentes et ne sont pas agregees
2. **Tous les corridors sont "conservation"** : La formule `dist * 0.3` ne peut jamais atteindre le seuil biologique (1000m) avec la limite de distance de 3000m
3. **Corridors sortant du carre 2km²** : La marge A* (0.02°) est plus grande que le perimetre d'analyse (0.015°), et aucun clipping n'est applique
4. **Scores statiques** : Les subscores terrain et habitat sont hardcodes, donc les corridors entre memes types de zones ont toujours le meme score

---

## RESUME EXECUTIF

### Etat actuel: FONCTIONNEL mais SIMULE
Le systeme de corridors V8 est **architecturalement solide** (A* + WWF + scoring composite) mais **opere sur des donnees simulees** :
- Terrain derive des types de zones (pas DEM)
- Pression humaine hardcodee (pas OSM)
- Subscores partiellement hardcodes
- Classification structurellement limitee a un seul niveau

### Recommandations pre-V9
1. **URGENT** : Corriger la formule de classification WWF pour utiliser `distance` directement au lieu de `distance * 0.3`
2. **URGENT** : Calculer dynamiquement `terrain` et `habitat` subscores au lieu de les hardcoder
3. **HAUT** : Integrer le clipping post-generation pour garder les corridors dans le perimetre
4. **HAUT** : Appeler `enrich_corridor()` et `validate_corridor_continuity()` dans le pipeline
5. **MOYEN** : Unifier la logique de generation dans `corridor_10x.py` (responsabilite unique)
6. **MOYEN** : Agreger le score corridors dans le score global

---

**Document produit le**: 12 Mars 2026
**Source de verite**: Code source backend + frontend, analyse statique
**Auteur**: Emergent AI
**Validation**: Requise avant Phase Corridors V9
