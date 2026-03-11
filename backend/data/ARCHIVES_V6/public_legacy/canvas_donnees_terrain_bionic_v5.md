/**
 * BIONIC V5 — Canvas Données Terrain
 * =====================================
 * Document de référence pour la préparation des fichiers d'observation.
 * 
 * FORMAT: CSV (virgule, point-virgule, tabulation) ou Excel (.xlsx)
 * ENCODAGE: UTF-8 (avec ou sans BOM)
 * 
 * Ce canvas décrit les champs, contraintes de validation,
 * métadonnées et exemples d'enregistrements attendus.
 * 
 * VERSION: 1.0.0
 * Conformité: BIONIC V5 MASTER — Pipeline Calibration
 */

# ============================================================================
# CANVAS STRUCTURÉ DES DONNÉES TERRAIN — BIONIC V5
# ============================================================================
# 
# Ce document est votre référence complète pour préparer les fichiers
# d'observation terrain destinés au pipeline de Calibration MASTER.
#
# OBJECTIF: Atteindre ≥95% de précision pour verrouiller le modèle MASTER.
# MINIMUM REQUIS: 50 observations (orignal Tier 1), 30 observations (autres)
#
# ============================================================================


## 1. FORMATS ACCEPTÉS

| Format   | Extension   | Encodage           | Délimiteurs         |
|----------|-------------|--------------------|--------------------|
| CSV      | .csv        | UTF-8 (ou UTF-8 BOM) | virgule, point-virgule, tabulation |
| Excel    | .xlsx       | —                  | —                  |

> Le système détecte automatiquement le délimiteur CSV.
> Les noms de colonnes FR et EN sont acceptés (voir section 3).


## 2. COLONNES OBLIGATOIRES

| # | Colonne                 | Type    | Contraintes                          | Description                              |
|---|-------------------------|---------|--------------------------------------|------------------------------------------|
| 1 | `latitude`              | float   | -90 ≤ val ≤ 90, précision ≥4 décimales | Latitude du point d'observation (WGS84) |
| 2 | `longitude`             | float   | -180 ≤ val ≤ 180, précision ≥4 décimales | Longitude du point d'observation (WGS84) |
| 3 | `species`               | string  | Valeurs acceptées (voir section 4)    | Espèce observée                          |
| 4 | `observed_behavior`     | string  | Valeurs acceptées (voir section 5)    | Comportement observé au moment de la collecte |
| 5 | `observation_datetime`  | datetime | ISO 8601 ou formats courants (voir section 6) | Date et heure exacte de l'observation |


## 3. COLONNES OPTIONNELLES

| # | Colonne              | Type    | Défaut        | Description                              |
|---|----------------------|---------|---------------|------------------------------------------|
| 6 | `region`             | string  | `CA-QC`       | Région administrative (ex: CA-QC, CA-ON) |
| 7 | `notes`              | string  | (vide)        | Notes de terrain libres                  |
| 8 | `confidence`         | float   | 0.8           | Niveau de confiance 0.0 à 1.0           |
| 9 | `observer_id`        | string  | `terrain_user`| Identifiant de l'observateur             |

### Colonnes bonus (enrichissement)
| # | Colonne              | Type    | Description                              |
|---|----------------------|---------|------------------------------------------|
| 10 | `temperature_c`     | float   | Température ambiante en °C               |
| 11 | `humidity_pct`       | float   | Humidité relative (0-100)                |
| 12 | `wind_kmh`           | float   | Vitesse du vent en km/h                  |
| 13 | `weather`            | string  | Conditions (ensoleillé, nuageux, pluie, neige) |
| 14 | `terrain_type`       | string  | Type de terrain (forêt, coupe, marais, champ) |
| 15 | `group_size`         | integer | Nombre d'individus observés              |
| 16 | `sex`                | string  | Sexe (mâle, femelle, indéterminé)        |
| 17 | `age_class`          | string  | Classe d'âge (adulte, juvénile, faon)    |


## 4. ESPÈCES ACCEPTÉES

| Valeur CSV                | Alias acceptés                    | Tier | Obs. minimum |
|---------------------------|-----------------------------------|------|-------------|
| `orignal`                 | orignal                           | T1   | 50          |
| `cerf_de_virginie`        | cerf de virginie, cerf            | T2   | 30          |
| `ours_noir`               | ours noir, ours                   | T2   | 25          |
| `caribou`                 | caribou                           | T3   | 20          |
| `wapiti`                  | wapiti                            | T3   | 20          |


## 5. COMPORTEMENTS ACCEPTÉS

| Valeur CSV         | Alias FR            | Alias EN        | Description                              |
|--------------------|---------------------|-----------------|------------------------------------------|
| `alimentation`     | alimentation        | feeding         | Animal en train de se nourrir            |
| `déplacement`      | déplacement, deplacement | movement   | Animal en déplacement actif              |
| `repos`            | repos               | resting         | Animal au repos, couché ou immobile      |
| `rut`              | rut                 | —               | Comportement de reproduction             |
| `allaitement`      | allaitement         | nursing         | Femelle allaitant un faon/veau           |
| `fuite`            | fuite               | flight          | Animal en fuite (dérangement)            |
| `abreuvement`      | abreuvement         | —               | Animal s'abreuvant                       |
| `ravage`           | ravage              | —               | Animal en zone de ravage hivernal        |


## 6. FORMATS DE DATE/HEURE ACCEPTÉS

| Format                      | Exemple                    |
|-----------------------------|----------------------------|
| ISO 8601 complet            | `2026-09-15T06:30:00Z`     |
| ISO 8601 sans Z             | `2026-09-15T06:30:00`      |
| Date + heure (espace)       | `2026-09-15 06:30:00`      |
| Date + heure (court)        | `2026-09-15 06:30`         |
| Date seule                  | `2026-09-15`               |
| Format FR (jj/mm/aaaa)      | `15/09/2026 06:30:00`      |
| Format FR court             | `15/09/2026 06:30`         |
| Format FR date seule        | `15/09/2026`               |

> RECOMMANDATION: Utiliser le format ISO 8601 (`2026-09-15T06:30:00Z`) pour éviter toute ambiguïté.


## 7. NOMS DE COLONNES ALTERNATIFS (FR)

Le système accepte les noms de colonnes en français. La normalisation est automatique:

| Colonne standard         | Alias acceptés                                |
|--------------------------|-----------------------------------------------|
| `latitude`               | `lat`                                         |
| `longitude`              | `lng`, `lon`, `long`                          |
| `species`                | `espèce`, `espece`                            |
| `observed_behavior`      | `comportement`, `behavior`, `behaviour`       |
| `observation_datetime`   | `date`, `datetime`, `date_observation`, `date_heure` |
| `region`                 | `région`                                      |
| `confidence`             | `confiance`                                   |
| `observer_id`            | `observateur`, `observer`                     |


## 8. CONTRAINTES DE VALIDATION

| Règle                              | Action si violation                      |
|------------------------------------|------------------------------------------|
| Latitude hors [-90, 90]            | Ligne rejetée, erreur rapportée          |
| Longitude hors [-180, 180]         | Ligne rejetée, erreur rapportée          |
| Espèce non reconnue                | Ligne rejetée                            |
| Comportement vide                  | Ligne rejetée                            |
| Date non parsable                  | Ligne rejetée, erreur rapportée          |
| Confiance hors [0, 1]              | Corrigée automatiquement (clamped)       |
| Fichier > 10 MB                    | Import refusé                            |
| Plus de 5000 lignes                | Lignes excédentaires ignorées            |
| Colonne requise manquante          | Import refusé, colonnes listées          |

> Les lignes valides sont importées même si d'autres lignes contiennent des erreurs.
> Un rapport détaillé est fourni après chaque import.


## 9. TRAÇABILITÉ

Chaque import génère automatiquement:
- **batch_id**: Identifiant unique du lot (`BATCH-20260224153000-a1b2c3`)
- **source_ids**: `["SRC-IMPORT-BATCH-xxx", "SRC-FILE-nom_fichier.csv"]`
- **version**: `1.0.0` sur chaque observation
- **created_at**: Horodatage UTC de l'import
- **observer_id**: Identifiant de l'observateur (colonne ou défaut)


## 10. EXEMPLES D'ENREGISTREMENTS

### Exemple CSV (format standard, virgule)
```csv
latitude,longitude,species,observed_behavior,observation_datetime,region,notes,confidence
46.8139,-71.2080,orignal,alimentation,2026-09-15T06:30:00Z,CA-QC,Mâle adulte en coupe forestière,0.9
47.1000,-70.5000,cerf_de_virginie,repos,2026-09-15T14:00:00Z,CA-QC,Femelle bordure cédrière,0.85
46.5000,-71.0000,ours_noir,déplacement,2026-06-15T06:00:00Z,CA-QC,Ours en bordure route forestière,0.7
48.0000,-70.0000,orignal,rut,2026-09-20T17:00:00Z,CA-QC,Mâle dominant appel vocal,0.95
46.9500,-71.1000,orignal,abreuvement,2026-07-10T18:30:00Z,CA-QC,Point d'eau bord lac,0.8
47.3000,-70.7000,cerf_de_virginie,fuite,2026-10-05T09:00:00Z,CA-QC,Dérangé par VTT,0.75
46.7000,-71.3000,orignal,alimentation,2026-05-20T05:45:00Z,CA-QC,Femelle avec veau coupe récente,0.9
47.0500,-70.9000,caribou,déplacement,2026-11-01T08:00:00Z,CA-QC,Migration vers ravage,0.8
```

### Exemple CSV (format FR, point-virgule)
```csv
lat;long;espèce;comportement;date;région;notes;confiance
46.8139;-71.2080;orignal;alimentation;15/09/2026 06:30;CA-QC;Mâle adulte coupe;0.9
47.1000;-70.5000;cerf de virginie;repos;15/09/2026 14:00;CA-QC;Femelle cédrière;0.85
```

### Exemple avec colonnes enrichies
```csv
latitude,longitude,species,observed_behavior,observation_datetime,region,notes,confidence,temperature_c,weather,group_size,sex,age_class
46.8139,-71.2080,orignal,alimentation,2026-09-15T06:30:00Z,CA-QC,Coupe forestière,0.9,12.5,ensoleillé,1,mâle,adulte
47.1000,-70.5000,cerf_de_virginie,repos,2026-09-15T14:00:00Z,CA-QC,Cédrière dense,0.85,18.0,nuageux,3,femelle,adulte
46.5000,-71.0000,ours_noir,déplacement,2026-06-15T06:00:00Z,CA-QC,Route forestière,0.7,22.0,ensoleillé,1,indéterminé,adulte
```


## 11. RECOMMANDATIONS DE COLLECTE

### Priorité Tier 1: Orignal (minimum 50 observations)
- **Rut (sept-oct)**: 15+ observations de mâles/femelles
- **Alimentation (mai-août)**: 10+ observations dans coupes forestières
- **Ravage (jan-mars)**: 10+ observations en zones hivernales
- **Déplacement**: 10+ observations de corridors
- **Repos**: 5+ observations zones de repos

### Priorité Tier 2: Cerf de Virginie (minimum 30 observations)
- Mêmes catégories comportementales, ratio adapté

### Priorité Tier 2: Ours noir (minimum 25 observations)
- Focus: alimentation, déplacement, repos (pas de rut)

### Bonnes pratiques
1. **Précision GPS**: ≥4 décimales (±10m)
2. **Heure exacte**: Notez l'heure au moment de l'observation, pas du rapport
3. **Confiance**: 0.9+ si observation directe claire, 0.7 si traces/indices
4. **Notes**: Mentionnez le type de terrain, la météo, le contexte
5. **Répartition**: Variez les heures, saisons, et localisations
