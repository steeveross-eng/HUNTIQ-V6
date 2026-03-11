# BIONIC V5 ULTIME 300% — STRATEGIE ML PHASE H+

**Version:** Strategy_v1 — 2026-03-01
**Approche:** Ultra Minimum Cost (0-20$/mois)

---

## Architecture ML BIONIC V5

### Principes fondamentaux
1. **Entrainement sur GPU gratuits** (Google Colab, Kaggle Kernels, SageMaker Lab)
2. **Stockage gratuit des modeles** (GitHub LFS, HuggingFace Hub)
3. **Inference locale** dans le backend BIONIC (CPU, 0$)
4. **Reentrainement rare** (1x/mois ou par saison)
5. **Shadow Mode permanent** (0 impact sur predictions existantes)

### Stack technique
- **Framework:** scikit-learn (deja installe) + joblib
- **Features:** Modules existants SSE→TFE + donnees reelles (DEM, Meteo, NDVI)
- **Target:** Probabilite de presence faunique par zone
- **Format modele:** joblib/pickle (leger, rapide a charger)

### Pipeline ML
```
[Feature Builder] → [Training Session] → [Model Store]
                                              ↓
[Prediction Engine] ← [Model Loader] ←───────┘
        ↓
[Shadow Comparator] → [Validation Metrics]
```

### Modules prevus (Phase H — deja structures)
- `feature_builder.py` — Extraction de features depuis le pipeline BIONIC
- `target_builder.py` — Construction des cibles d'entrainement
- `model_store.py` — Gestion versionnee des modeles
- `prediction_engine.py` — Inference en production
- `ml_validator.py` — Validation des predictions

### Workflow d'entrainement
1. Exporter les features depuis le pipeline (CSV/JSON)
2. Uploader sur Google Colab/Kaggle
3. Entrainer le modele (Random Forest, Gradient Boosting)
4. Exporter le modele (.joblib)
5. Deposer dans le repo ou HuggingFace
6. Charger dans le backend BIONIC
7. Activer en Shadow Mode
8. Comparer avec les predictions synthétiques

### Couts estimes
| Composant | Cout mensuel |
|---|---|
| Entrainement (Colab) | 0$ |
| Stockage modele (GitHub) | 0$ |
| Inference (CPU local) | 0$ |
| Donnees (Open-Meteo, cache) | 0$ |
| Donnees (Sentinel-2) | 0$ |
| **TOTAL** | **0$/mois** |

### Versionnement
- `ml_model_v1` — Premier modele baseline (Random Forest)
- `ml_model_v2` — Enrichi avec donnees reelles
- `ml_model_v3` — Optimise par saison

### Logs et tracabilite
- `ml_training.log` — Sessions d'entrainement
- `ml_inference.log` — Predictions en production
- `ml_comparison.log` — Comparaisons Shadow

---

## Prochaines etapes
1. Exporter features depuis le pipeline BIONIC (feature_builder)
2. Creer un notebook Colab de reference pour l'entrainement
3. Implementer le module de chargement de modele
4. Activer les predictions en Shadow Mode
5. Comparer avec les modules PME/BMPE existants
