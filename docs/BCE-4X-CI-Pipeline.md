# BCE-4X CI/CD Pipeline — Enforcement Strategy
## Version 1.0 | BIONIC HUNT Certification Gate

---

## 1. Objectif

Garantir que la branche `main` est **toujours BCE-4X compliant**. Aucun code ne peut etre merge vers `main` si `validate_full()` echoue avec des violations de severite **HIGH** ou **MEDIUM**.

---

## 2. Schema du Pipeline CI

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BIONIC HUNT — CI Pipeline                        │
│                  BCE-4X Mandatory Gate (v1.0)                       │
└─────────────────────────────────────────────────────────────────────┘

  Developer Push / PR
        │
        ▼
  ┌─────────────┐
  │  1. LINT     │   ESLint (frontend) + Ruff (backend)
  │  + FORMAT    │   Echec → Blocage immediat
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  2. TESTS    │   pytest (backend) + Jest (frontend)
  │  UNITAIRES   │   Couverture minimale: 80%
  └──────┬──────┘
         │
         ▼
  ┌──────────────────────────────────────────────────────────┐
  │  3. BCE-4X VALIDATION GATE (OBLIGATOIRE)                 │
  │                                                          │
  │  Execution: POST /api/bce/validate                       │
  │                                                          │
  │  ┌─────────────────────────────────────────────────────┐ │
  │  │  validate_full() execute les 10+ validateurs:       │ │
  │  │                                                     │ │
  │  │  - spatial_integrity    - water_exclusion            │ │
  │  │  - species_coherence    - season_coherence           │ │
  │  │  - scoring_determinism  - ui_coherence               │ │
  │  │  - engine_isolation     - pipeline_order             │ │
  │  │  - debug_layer_guard    - golden_state               │ │
  │  │  - corridor_v9 (COR-006, continuity)                │ │
  │  │  - color_contract (VIS-007)                         │ │
  │  │  - geometry_compliance (GEOM-005)                   │ │
  │  └─────────────────────────────────────────────────────┘ │
  │                                                          │
  │  Verdict:                                                │
  │    overall_status = PASS → Merge autorise                │
  │    overall_status = FAIL → BLOCAGE (HIGH/MEDIUM)         │
  │    overall_status = ERROR → BLOCAGE                      │
  │    overall_status = PARTIAL → Autorise (SKIP acceptable) │
  │                                                          │
  │  AUCUN BYPASS POSSIBLE                                   │
  └──────────┬───────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────┐
  │  4. BUILD &      │   Docker build + asset compilation
  │  INTEGRATION     │   Verification des imports/deps
  └──────┬───────────┘
         │
         ▼
  ┌──────────────────┐
  │  5. MERGE TO     │   Auto-merge si toutes les etapes passent
  │  MAIN            │   Tag BCE-4X-COMPLIANT automatique
  └──────────────────┘
```

---

## 3. Regles de Blocage

| Severite | Action | Bypass possible |
|----------|--------|-----------------|
| **HIGH** | Merge **BLOQUE** | NON |
| **MEDIUM** | Merge **BLOQUE** | NON |
| **LOW** | Warning, merge autorise | N/A |
| **SKIP** | Info, merge autorise | N/A |

### Criteres de severite HIGH
- Echec `spatial_integrity` (geometries invalides)
- Echec `water_exclusion` (zones en plans d'eau)
- Echec `scoring_determinism` (scores non-reproductibles)
- Echec `corridor_v9 / COR-006` (reseau discontinu)

### Criteres de severite MEDIUM
- Echec `species_coherence` (incoherence faunique)
- Echec `season_coherence` (logique saisonniere brisee)
- Echec `ui_coherence` (desynchronisation carte/panel)
- Echec `color_contract / VIS-007` (couleurs non harmonisees)

---

## 4. Implementation CI (GitHub Actions)

```yaml
# .github/workflows/bce-4x-gate.yml
name: BCE-4X Compliance Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  bce-4x-validation:
    name: BCE-4X Mandatory Validation
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Start Backend Server
        run: |
          cd backend
          uvicorn server:app --host 0.0.0.0 --port 8001 &
          sleep 5

      - name: Run BCE-4X validate_full()
        id: bce_validate
        run: |
          RESPONSE=$(curl -s -X POST http://localhost:8001/api/bce/validate \
            -H "Content-Type: application/json")

          echo "$RESPONSE" | python3 -c "
          import sys, json
          data = json.load(sys.stdin)
          status = data.get('overall_status', 'UNKNOWN')
          merge_allowed = data.get('merge_allowed', False)
          summary = data.get('summary', {})

          print(f'BCE-4X Status: {status}')
          print(f'Merge Allowed: {merge_allowed}')
          print(f'Validators: {summary.get(\"total_validators\", 0)}')
          print(f'Passed: {summary.get(\"passed\", 0)}')
          print(f'Failed: {summary.get(\"failed\", 0)}')
          print(f'Errors: {summary.get(\"errors\", 0)}')

          if not merge_allowed:
              print('::error::BCE-4X VALIDATION FAILED — Merge to main BLOCKED')
              print('Violations detected:')
              for v in data.get('validators', []):
                  if v.get('status') in ('FAIL', 'ERROR'):
                      print(f'  BLOCKED: {v[\"name\"]} → {v[\"status\"]}')
                      for err in v.get('errors', []):
                          print(f'    - {err}')
              sys.exit(1)
          else:
              print('BCE-4X PASS — Merge to main AUTHORIZED')
          "

      - name: Tag BCE-4X Compliant
        if: success()
        run: |
          echo "BCE-4X-COMPLIANT: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> BCE_AUDIT_LOG.txt
```

---

## 5. Exemple de Merge Bloque

### Scenario: PR #142 — Modification du calcul de corridors

```
=================================================================
 BCE-4X COMPLIANCE GATE — EXECUTION REPORT
 Timestamp: 2026-02-15T14:32:07Z
 Branch: feature/corridor-algorithm-update → main
=================================================================

 BCE-4X Status: FAIL
 Merge Allowed: false

 Summary:
   Total Validators: 12
   Passed: 10
   Failed: 2
   Errors: 0
   Skipped: 0

 BLOCKED VALIDATORS:
 ─────────────────────────────────────────────────────
 [HIGH] corridor_v9 (COR-006)
   Status: FAIL
   Errors:
     - Corridor network disconnected: 3 isolated components
       detected (expected 1 connected graph)
     - Segment gap > 50m between zone_A7 and zone_B3
       (max allowed: 25m)

 [MEDIUM] scoring_determinism
   Status: FAIL
   Errors:
     - Score variance > 0.5% across 3 identical runs
       for waypoint [46.8139, -71.2080]
     - Expected deterministic output, got delta = 1.2%
 ─────────────────────────────────────────────────────

 PASSED VALIDATORS (10/12):
   spatial_integrity ............... PASS
   water_exclusion ................ PASS
   species_coherence .............. PASS
   season_coherence ............... PASS
   ui_coherence ................... PASS
   engine_isolation ............... PASS
   pipeline_order ................. PASS
   debug_layer_guard .............. PASS
   golden_state ................... PASS
   color_contract (VIS-007) ....... PASS

=================================================================
 DECISION: MERGE BLOQUE
 La PR #142 ne peut PAS etre fusionnee dans main.
 
 Actions requises:
   1. Corriger la continuite du reseau de corridors (COR-006)
   2. Assurer le determinisme des scores (variance < 0.5%)
   3. Relancer la pipeline BCE-4X apres corrections
=================================================================
```

---

## 6. Garanties

1. **MAIN = BCE-4X COMPLIANT** : Chaque commit sur `main` a passe `validate_full()` sans violation HIGH ou MEDIUM.
2. **Zero bypass** : Aucun admin override, aucun force-push ne peut contourner la gate BCE-4X. Les branch protection rules GitHub bloquent le merge si le job `bce-4x-validation` echoue.
3. **Audit trail** : Chaque execution de la gate produit un rapport horodate stocke dans les artefacts CI et dans `BCE_AUDIT_LOG.txt`.
4. **Reproductibilite** : La validation utilise les memes endpoints API (`/api/bce/validate`) que le backend en production, garantissant la coherence entre CI et runtime.

---

## 7. Configuration GitHub Branch Protection

```
Repository Settings → Branches → main:
  ✅ Require a pull request before merging
  ✅ Require status checks to pass before merging
     → Required: "BCE-4X Mandatory Validation"
  ✅ Require branches to be up to date before merging
  ✅ Do not allow bypassing the above settings
  ❌ Allow force pushes: DISABLED
  ❌ Allow deletions: DISABLED
```

---

**Document genere le 2026-02-15 | BIONIC HUNT Certification — Phase 6 BCE-4X CI/CD**
