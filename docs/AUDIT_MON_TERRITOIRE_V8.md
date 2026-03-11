# AUDIT COMPLET — FENÊTRE MON TERRITOIRE
## BIONIC V8 — 11 Mars 2026

---

## 1. STRUCTURE ACTUELLE DU PANNEAU DE DROITE

### 1.1 Composant principal: `SidePanelZones.jsx`

| Élément | Fichier | Description | Statut |
|---------|---------|-------------|--------|
| **Compteur Zoom** | SidePanelZones.jsx | Affiche le niveau de zoom actuel | ✅ Conserver |
| **Compteur Zones** | SidePanelZones.jsx | Affiche le nombre de zones visibles + source (V7/Cache) | ✅ Conserver |
| **Pipeline Version** | SidePanelZones.jsx | Badge "Pipeline V7 + Météo V8.2.1" | ✅ Conserver |
| **RejectionDiagnosticsPanel** | SidePanelZones.jsx | Diagnostics des zones rejetées (par raison/couche) | ✅ Conserver |
| **WeatherInfluencePanel** | SidePanelZones.jsx | Impact météo sur les scores (température, vent, badges) | ✅ Conserver |
| **CorridorStatsPanel** | CorridorStatsPanel.jsx | Statistiques des corridors | ✅ À améliorer |
| **Waypoint Cible** | SidePanelZones.jsx | Info waypoint sélectionné + actions export | ✅ Conserver |

### 1.2 Composants de la barre d'outils (header)

| Élément | Description | Statut |
|---------|-------------|--------|
| Score Global | 41/100 Modéré | ✅ Conserver |
| Température | -8°C | ✅ Conserver |
| Vent | NE 45 km/h | ✅ Conserver |
| Chasse Score | 40/100 | ✅ Conserver |
| Live Indicator | Point vert | ✅ Conserver |
| Bouton + WAYPOINT | Ajout waypoint | ✅ Conserver |

### 1.3 Panneau "Analyse du territoire" (visible sur screenshot)

| Élément | Description | Statut |
|---------|-------------|--------|
| SCORE GLOBAL | 41/100 Modéré | ✅ Conserver (dupliquer header) |
| Habitat | 75% | ⚠️ Fusionner avec V8 |
| Rut | 74% | ⚠️ Fusionner avec V8 |
| Salines | 62% | ⚠️ Legacy - À évaluer |
| Affûts | 83% | ⚠️ Legacy - À évaluer |
| Trajets | 74% | ⚠️ Fusionner avec Corridors V8 |
| Peuplements | 75% | ⚠️ Fusionner avec Habitat V8 |

---

## 2. PROBLÈMES IDENTIFIÉS

### 2.1 RÉGRESSION CRITIQUE #1: Auto-load couches désactivé
- **Symptôme**: Les zones ne s'affichent pas automatiquement au chargement
- **Cause**: Le hook `useTerritoryAutoLoad.js` n'est pas intégré dans `MonTerritoireBionicPage.jsx`
- **Solution**: Intégrer le hook et déclencher le chargement automatique

### 2.2 RÉGRESSION CRITIQUE #2: Zones hors carré 2km²
- **Symptôme**: Les zones colorées débordent du carré pointillé orangé
- **Cause**: Incohérence entre:
  - `BionicZone2km.jsx`: ZONE_SIZE_M = 2000m (2km)
  - `useSpatialClipping.js`: ANALYSIS_BOX_SIZE_M = 3000m (3km)
  - Le clipping client n'est pas appliqué systématiquement
- **Solution**: 
  1. Unifier la taille à 2000m (2km²)
  2. Appliquer le clipping systématiquement dans MapContent

### 2.3 Doublons détectés
| Élément dupliqué | Localisation 1 | Localisation 2 | Action |
|------------------|----------------|----------------|--------|
| Score Global | Header toolbar | Panneau droite | Garder les deux (contexte différent) |
| Habitat score | SCORE_CATEGORIES | Panneau droite | Fusionner vers V8 |
| Trajets/Corridors | SCORE_CATEGORIES | CorridorStatsPanel | Fusionner vers Corridors 10X |

### 2.4 Composants Legacy (V5/V6/V7) à évaluer

| Composant | Version | Action recommandée |
|-----------|---------|-------------------|
| TerritoryAnalysisModule.jsx | V5 | ⚠️ Phase E - Décommission |
| TerritoryAnalysisPanel.jsx | V5 | ⚠️ Phase E - Décommission |
| StructureContrastLayer.jsx | V6 | ✅ Déjà désactivé |
| Salines score | V5 | ⚠️ Évaluer pertinence |
| Affûts score | V5 | ⚠️ Évaluer pertinence |

---

## 3. PROPOSITION DE RÉORGANISATION

### 3.1 Structure recommandée pour le panneau de droite

```
┌─────────────────────────────────────────┐
│ SCORE GLOBAL V8                         │
│ ██████████████████████░░░░░ 75/100      │
│ COMPLIANT ✓                             │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ SCORES ÉCOLOGIQUES V8                   │
│ ├─ Habitat      ████████░░ 80%          │
│ ├─ Alimentation ███████░░░ 72%          │
│ ├─ Repos        █████████░ 88%          │
│ ├─ Rut          ██████░░░░ 65%          │
│ └─ Corridors    ████████░░ 78%          │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ CORRIDORS 10X                           │
│ ● 12 corridors actifs détectés          │
│ ├─ Macro-corridor (>5km): 2             │
│ ├─ Biologique (1-5km): 6                │
│ └─ Conservation (<1km): 4               │
│ [Légende WWF]                           │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ ZONES PAR ESPÈCE                        │
│ 🦌 Orignal                              │
│    Zone dominante: Alimentation         │
│    Corridors: 5 | Connectivité: 78%     │
│ 🦌 Chevreuil                            │
│    Zone dominante: Repos                │
│    Corridors: 4 | Connectivité: 72%     │
│ 🐻 Ours noir                            │
│    Zone dominante: Alimentation         │
│    Corridors: 3 | Connectivité: 65%     │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ BCE AUTO-RUN STATUS                     │
│ ● COMPLIANT 100%                        │
│ ├─ zone_classification    ✓             │
│ ├─ corridor_continuity    ✓             │
│ ├─ wwf_classification     ✓             │
│ └─ human_pressure         ✓             │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ MÉTÉO INFLUENCE V8.2                    │
│ 🌡️ -8°C | 💨 NE 45km/h                  │
│ Global: x1.15 (+15%)                    │
│ [Badges: Favorable, Wind Alert]         │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ WAYPOINT CIBLE                          │
│ 📍 "test" (46.8061, -71.1037)           │
│ Zone 2km² active                        │
│ [Export JSON] [Export PDF]              │
└─────────────────────────────────────────┘
```

### 3.2 Composants à intégrer

1. **EcologicalPanel.jsx** → Scores écologiques V8 + Zones par espèce
2. **CorridorsLegend** (de CorridorsVisualLayer.jsx) → Légende WWF
3. **BCEStatusWidget** (nouveau) → Statut BCE Auto-Run

### 3.3 Composants à retirer (Phase E)

1. `TerritoryAnalysisModule.jsx` — Module V5 obsolète
2. `TerritoryAnalysisPanel.jsx` — Panneau V5 obsolète
3. Scores legacy (Salines, Affûts) si non pertinents

---

## 4. CORRECTIONS IMMÉDIATES REQUISES

### 4.1 Correction #1: Unifier la taille de zone à 2km²

**Fichier**: `/app/frontend/src/hooks/useSpatialClipping.js`
```javascript
// AVANT: const ANALYSIS_BOX_SIZE_M = 3000;
// APRÈS: const ANALYSIS_BOX_SIZE_M = 2000;
```

### 4.2 Correction #2: Appliquer le clipping systématique

**Fichier**: `/app/frontend/src/components/territoire/map/MapContent.jsx`
- Utiliser `clipZonesClient()` avant le rendu des zones

### 4.3 Correction #3: Activer l'auto-load

**Fichier**: `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`
- Intégrer `useTerritoryAutoLoad` hook
- Déclencher le chargement automatique au montage

---

## 5. LIVRABLES ATTENDUS

| # | Livrable | Priorité | Status |
|---|----------|----------|--------|
| 1 | Correction auto-load couches | P0 | 🔄 À faire |
| 2 | Correction clipping zones 2km² | P0 | 🔄 À faire |
| 3 | Validation BCE post-correction | P0 | 🔄 À faire |
| 4 | Structure réorganisée panneau | P1 | 📋 Proposé |
| 5 | Intégration EcologicalPanel | P1 | 📋 Après validation |
| 6 | Phase E décommission | P2 | 📋 Planifié |

---

## 6. VALIDATION BCE REQUISE

Après corrections, BCE doit retourner:
- `global_status: COMPLIANT`
- `global_score: 100`
- Tous les validateurs en status `COMPLIANT`

---

**Audit réalisé le**: 11 Mars 2026
**Version BIONIC**: V8
**Auteur**: Emergent AI
