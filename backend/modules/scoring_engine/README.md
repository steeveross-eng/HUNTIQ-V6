# Scoring Engine

## Module de Scoring Multi-Critères

### Version: 1.0.0
### Phase: 2 (Core Engines)
### API Prefix: `/api/v1/scoring`

---

## Description

Le **Scoring Engine** évalue les attractants et produits de chasse selon 13 critères scientifiques pondérés.

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/scoring/
```

### 2. Calcul de Score
```
POST /api/v1/scoring/calculate
```
Calcule le score d'un produit.

### 3. Liste des Critères
```
GET /api/v1/scoring/criteria
```
Retourne les 13 critères et leurs pondérations.

### 4. Comparaison
```
POST /api/v1/scoring/compare
```
Compare plusieurs produits.

---

## 13 Critères Scientifiques

| # | Critère | Poids | Description |
|---|---------|-------|-------------|
| 1 | Attractivité olfactive | 15% | Puissance et qualité de l'odeur |
| 2 | Durée d'efficacité | 12% | Combien de temps le produit reste actif |
| 3 | Résistance météo | 10% | Performance sous pluie/neige |
| 4 | Portée d'attraction | 10% | Distance d'attraction du gibier |
| 5 | Naturalité | 8% | Caractère naturel des ingrédients |
| 6 | Facilité d'utilisation | 7% | Simplicité d'application |
| 7 | Rapport qualité/prix | 8% | Valeur pour le prix |
| 8 | Sécurité | 5% | Sans danger pour l'environnement |
| 9 | Polyvalence | 6% | Utilisation sur plusieurs espèces |
| 10 | Saisonnalité | 6% | Efficacité selon la saison |
| 11 | Avis chasseurs | 5% | Retours de la communauté |
| 12 | Innovation | 4% | Nouvelles technologies |
| 13 | Certification | 4% | Labels et certifications |

---

## Formule de Calcul

```
score_final = Σ(critère_i × poids_i) / 10
```

Score final: 0-100 points, affiché en pastille colorée.

---

## Pastilles de Score

| Score | Couleur | Label |
|-------|---------|-------|
| 90-100 | 🟢 Vert | Excellent |
| 70-89 | 🟡 Jaune | Bon |
| 50-69 | 🟠 Orange | Moyen |
| 0-49 | 🔴 Rouge | Faible |

---

*HUNTIQ V3 - Scoring Engine - Phase 2*
