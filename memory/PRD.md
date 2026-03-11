# BIONIC HUNT V8 — Product Requirements Document

## Problème original
Application d'analyse de territoire de chasse avec moteur géospatial BIONIC Engine, base écologique complète pour 3 espèces (Orignal, Chevreuil, Ours Noir), et système de validation automatisé BCE.

**Repo GitHub:** https://github.com/steeveross-eng/HUNTIQ-V5  
**Branche:** v6_autosave

## Corrections critiques — 11 Mars 2026

### RÉGRESSION #1: Auto-load couches ✅ CORRIGÉE
- **Problème**: Les zones ne s'affichaient pas automatiquement au chargement
- **Cause**: `layersVisible` avait la plupart des couches à `false` par défaut
- **Solution**: Activé par défaut: `habitats`, `alimentation`, `repos`, `rut`, `trajets`, `corridors`, `ensoleillement`, `peuplements`

### RÉGRESSION #2: Zones hors carré 2km² ✅ CORRIGÉE
- **Problème**: Les zones débordaient du carré 2km²
- **Causes**: 
  1. `ANALYSIS_BOX_SIZE_M` était à 3000m au lieu de 2000m
  2. Format GeoJSON [lng,lat] vs Leaflet [lat,lng] non géré
- **Solutions**:
  1. Unifié la taille à 2000m dans `useSpatialClipping.js`
  2. Ajouté normalisation des coordonnées dans `clipZones()`

### Autres correctifs
- Support `lat/latitude` et `lng/longitude` dans `useZoneOrchestrator.js`
- Support des deux formats dans `useSpatialClipping.js`

## Audit de la fenêtre MON TERRITOIRE

### Structure actuelle du panneau de droite

| Composant | Description | Statut |
|-----------|-------------|--------|
| Compteur Zoom | Niveau de zoom | ✅ Conserver |
| Compteur Zones | Nb zones + source V7 | ✅ Conserver |
| Pipeline Version | Badge V7 + Météo V8.2.1 | ✅ Conserver |
| RejectionDiagnosticsPanel | Diagnostics rejets | ✅ Conserver |
| WeatherInfluencePanel | Impact météo | ✅ Conserver |
| CorridorStatsPanel | Stats corridors | ✅ À améliorer |
| Waypoint Cible | Info + actions export | ✅ Conserver |

### Proposition de réorganisation (à valider)

```
┌─ SCORE GLOBAL V8 ─────────────────────┐
│ ██████████████ 75/100 COMPLIANT ✓     │
└───────────────────────────────────────┘
┌─ SCORES ÉCOLOGIQUES V8 ───────────────┐
│ Habitat 80% | Alimentation 72%        │
│ Repos 88% | Rut 65% | Corridors 78%   │
└───────────────────────────────────────┘
┌─ CORRIDORS 10X ───────────────────────┐
│ ● 12 corridors actifs détectés        │
│ Légende WWF: Macro|Biologique|Cons.   │
└───────────────────────────────────────┘
┌─ ZONES PAR ESPÈCE ────────────────────┐
│ 🦌 Orignal: Alimentation (78%)        │
│ 🦌 Chevreuil: Repos (72%)             │
│ 🐻 Ours noir: Alimentation (65%)      │
└───────────────────────────────────────┘
┌─ BCE AUTO-RUN ────────────────────────┐
│ ● COMPLIANT 100%                      │
│ ✓ zone_classification                 │
│ ✓ corridor_continuity                 │
│ ✓ wwf_classification                  │
└───────────────────────────────────────┘
```

### Phase E — Décommission (à planifier)
- `TerritoryAnalysisModule.jsx` — V5 obsolète
- `TerritoryAnalysisPanel.jsx` — V5 obsolète
- Scores legacy (Salines, Affûts) — à évaluer

## Fonctionnalités implémentées

### BIONIC V8
- ✅ Base écologique 3 espèces × 4+ zones
- ✅ Corridors 10X + Classification WWF
- ✅ Style visuel BIONIC (palette, largeur variable)
- ✅ BCE Ruleset V8 (9 règles)
- ✅ BCE Auto-Run activé
- ✅ Auto-load territoire fonctionnel
- ✅ Zone 2km² carrée centrée
- ✅ Clipping strict des zones

## Tests validés
- Auto-load couches au chargement ✅
- Zones dans le carré 2km² ✅
- BCE opérationnel (9 règles) ✅
- API écologique fonctionnelle ✅

## Dates clés
- **2026-03-11 PM**: Corrections régressions critiques, Audit MON TERRITOIRE
- **2026-03-11 AM**: BIONIC V8 — Base écologique, Corridors 10X, BCE V8
