# PLAN DE TRANSFERT BCE-4X — Tous Modules Critiques
## Date: 12 Mars 2026
## Version: BCE-4X-TRANSFER-1.0

---

## 1. MODULES ENCORE HORS BCE-4X (avant ce transfert)

| Module | Fichier existant | Etait couvert | Status |
|--------|-----------------|---------------|--------|
| Weather Engine | weather_service.py, open_meteo_service.py | NON (partiel = pas de validateur) | TRANSFERE |
| Waypoint Engine | waypoint_analysis_service.py, useWaypointActions.js | NON | TRANSFERE |
| Nutrition Engine | N'existe pas encore | NON | PLANIFIE |
| Daily Routine Engine | N'existe pas encore | NON | PLANIFIE |
| Disturbance Engine | human_pressure_model.py (inactif) | NON | PLANIFIE |
| Phenology Engine | N'existe pas encore | NON | PLANIFIE |
| Typology Engine | N'existe pas encore | NON | PLANIFIE |
| Learning Engine | N'existe pas encore | NON | PLANIFIE |
| Habitat Enhancement | N'existe pas encore | NON | PLANIFIE |
| Hunting Path Engine | route_planner_service.py (legacy) | NON | PLANIFIE |
| UI Coherence | Panneau droit, legendes | PARTIEL (via ui_coherence.py) | RENFORCE |
| Scoring Determinism | useBionicScoring.js, scoring_service.py | PARTIEL (via scoring_determinism.py) | RENFORCE |

---

## 2. PLAN DE TRANSFERT (ordre d'execution)

### Phase A — IMMEDIATE (pre-V9, FAIT)

| Etape | Module | Action | Validateur | Tests | Status |
|-------|--------|--------|------------|-------|--------|
| A1 | corridor_10x | Declare critique, 8 regles | corridor_v9.py | 21 pytest | DONE |
| A2 | Weather Engine | Declare actif, 5 regles | bionic_engine_framework.py | Integre | DONE |
| A3 | Waypoint Engine | Declare actif, 3 regles | bionic_engine_framework.py | Integre | DONE |
| A4 | UI Coherence | Registre mis a jour | ui_coherence.py (existant) | Existants | DONE |
| A5 | Scoring Determinism | Registre mis a jour | scoring_determinism.py (existant) | Existants | DONE |
| A6 | Registre central | 16 modules, auto-blocking | bce_max_4_1.py | check_critical_module_coverage() | DONE |

### Phase B — CORRIDORS V9 (prochaine)

| Etape | Module | Action | Validateur | Tests requis |
|-------|--------|--------|------------|--------------|
| B1 | Movement Engine V9 | Supprimer hardcoding, scores dynamiques | corridor_v9.py (maj) | Scoring dynamique |
| B2 | Disturbance Engine | Integrer pression humaine algorithmique | DisturbanceEngineValidator | Sources, score range |
| B3 | Zone Engine Core | Clipping strict, validation geometrie | spatial_integrity.py (maj) | Bounds validation |

### Phase C — HUB ECOLOGIQUE (V9-V10)

| Etape | Module | Action | Validateur | Tests requis |
|-------|--------|--------|------------|--------------|
| C1 | Nutrition Engine | Implementer Sol→Nutriments→Fourrage→Attractivite | NutritionEngineValidator | Espece, score, hardcoding |
| C2 | Daily Routine Engine | Implementer rythmes journaliers | DailyRoutineEngineValidator | Fenetres, espece, temps |
| C3 | Phenology Engine | Implementer debourrement→senescence | PhenologyEngineValidator | Saison, fourrage, date |
| C4 | Typology Engine | Implementer profils comportementaux | TypologyEngineValidator | Profil, type valide |
| C5 | Learning Engine | Implementer ajustement par observations | LearningEngineValidator | Observations, modele |
| C6 | Habitat Enhancement | Implementer analyse sol + recommandations | HabitatEnhancementValidator | Sol, recommandations |
| C7 | Hunting Path Engine | Implementer trajet de chasse intelligent | HuntingPathEngineValidator | Geometrie, securite |

### Phase D — NETTOYAGE

| Etape | Action | Impact |
|-------|--------|--------|
| D1 | Supprimer 8 fichiers legacy | Reduction dette technique |
| D2 | Unifier logique corridor dans corridor_10x.py | Responsabilite unique |
| D3 | Audit final BCE-4X complet | Certification V9 |

---

## 3. GARANTIE AUTO-BLOCKING

### Mecanisme implemente

```python
# bce_max_4_1.py — validate_full()
uncovered = check_critical_module_coverage()
for module_id in uncovered:
    violations.append(BCEMaxViolation(
        type=ViolationType.REGRESSION_DETECTED,
        severity="high",
        message=f"Module critique '{module_id}' actif sans validateur BCE-4X",
        ...
    ))
```

### Regles:
1. **Tout module `status: active` sans validateur** → violation HIGH → deploiement BLOQUE
2. **Modules `planned`** → toleres (validateur pret, en attente d'implementation)
3. **Passage planned → active** → le validateur est execute immediatement, violations detectees
4. **Impossible de contourner** : le registre est dans bce_max_4_1.py (fichier protege BCE)

### Verification via API:
- `GET /api/bce/registry` → liste tous les modules et leur couverture
- `POST /api/bce/validate-engines` → execute tous les validateurs
- `POST /api/bce/validate-corridors` → validation specifique corridors

---

## 4. TESTS ANTI-REGRESSION PAR MODULE

| Module | Test File | Tests | Couverture |
|--------|-----------|-------|------------|
| corridor_10x | tests/test_bce_corridor_v9.py | 21 | Hardcoding, geometrie, clipping, classification, scoring, batch, anti-regression |
| Tous moteurs BIONIC | bionic_engine_framework.py | Integres (validate() par moteur) | Data presence, score range, hardcoding, coherence |
| BCE-MAX 4.1 | bce_max_4_1.py validate_full() | Check 6 (nouveau) | Couverture registre modules critiques |

### Tests a creer avec chaque moteur (Phase C):
- Test unitaire validate() avec donnees valides → COMPLIANT
- Test unitaire validate() avec donnees invalides → violations
- Test hardcoding avec valeurs connues → BLOCKED
- Test integration avec pipeline zones/corridors
- Test regression entre sessions

---

## 5. CHOIX TECHNOLOGIQUE CONFIRME

**Option A — Modele algorithmique interne**

| Composant | Approche | Avantages |
|-----------|----------|-----------|
| DEM SRTM | Derivation altitude par formules topographiques Quebec (latitude, distance mer, bassins versants) | Zero dependance, reproductible, BCE-4X deterministe |
| NDVI | Estimation densite couvert par type de zone + saison phenologique | Coherent avec ecological_database_v8 |
| Pression humaine | Estimation par distance aux centroïdes de perturbation (routes, chalets, sentiers) | Calculable sans API externe |

### Raisons:
- Coherence BCE-4X (determinisme, reproductibilite)
- Performance (zero latence reseau)
- Independance (zero dependance API externe)
- Testabilite (valeurs previsibles pour tests anti-regression)

---

## RESUME

| Metrique | Avant | Apres |
|----------|-------|-------|
| Modules dans le registre | 0 | **16** |
| Modules actifs avec validateur | 0 | **8** |
| Modules planifies avec validateur pret | 0 | **8** |
| Modules non couverts | Tous | **0** |
| Tests BCE-4X corridors | 0 | **21** |
| Regles BCE-4X corridors | 0 | **8** |
| Regles BCE-4X moteurs | 0 | **35** (total) |
| Endpoints BCE-4X | 1 | **4** |
| Auto-blocking | NON | **OUI** |

---

**Document produit le**: 12 Mars 2026
**Auteur**: Emergent AI / BCE-4X Engine
**Validation requise**: Utilisateur avant Phase Corridors V9
