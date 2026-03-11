# Strategy Engine

## Module de Génération de Stratégies

### Version: 1.0.0
### Phase: 2 (Core Engines)
### API Prefix: `/api/v1/strategy`

---

## Description

Le **Strategy Engine** génère des stratégies de chasse personnalisées basées sur les conditions, l'espèce ciblée et le territoire.

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/strategy/
```

### 2. Générer Stratégie
```
POST /api/v1/strategy/generate
```
Génère une stratégie complète.

**Body:**
```json
{
  "species": "deer",
  "territory_type": "forest",
  "weather": {...},
  "equipment": ["stand", "decoy"],
  "experience_level": "intermediate"
}
```

### 3. Stratégies Prédéfinies
```
GET /api/v1/strategy/templates
```
Liste les templates de stratégie.

### 4. Stratégie par Espèce
```
GET /api/v1/strategy/species/{species}
```
Stratégies spécifiques à une espèce.

---

## Types de Stratégies

| Type | Description | Meilleur Pour |
|------|-------------|---------------|
| Affût | Attente passive | Cerfs, orignaux |
| Approche | Déplacement actif | Petits gibiers |
| Battue | Chasse en groupe | Sangliers |
| Appel | Utilisation d'appels | Orignaux, dindons |

---

## Facteurs Considérés

1. **Espèce ciblée** - Comportement et habitat
2. **Météo** - Conditions actuelles
3. **Terrain** - Type de territoire
4. **Saison** - Période de l'année
5. **Équipement** - Matériel disponible
6. **Expérience** - Niveau du chasseur

---

*HUNTIQ V3 - Strategy Engine - Phase 2*
