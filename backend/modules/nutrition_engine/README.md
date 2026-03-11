# Nutrition Engine - CORE Module

## Overview

The Nutrition Engine provides nutritional analysis capabilities for hunting attractants.
It contains the complete ingredients database and analysis logic.

## Version

- **Current**: v1.0.0
- **API Prefix**: `/api/v1/nutrition`

## Features

- Complete ingredients database (28+ ingredients)
- Ingredient search and lookup
- Nutritional analysis of product compositions
- Score calculation based on ingredient profiles

## Ingredient Types

| Type | Description | Count |
|------|-------------|-------|
| `olfactif` | Olfactory compounds | 13 |
| `nutritionnel` | Nutritional compounds | 8 |
| `comportemental` | Behavioral compounds (pheromones) | 5 |
| `fixateur` | Fixative compounds | 3 |

## API Endpoints

### GET `/api/v1/nutrition/`
Module information

### GET `/api/v1/nutrition/ingredients`
List all ingredients with optional filters
- Query params: `type`, `category`, `limit`

### GET `/api/v1/nutrition/ingredients/search`
Search ingredients by name
- Query params: `q` (required), `limit`

### GET `/api/v1/nutrition/ingredients/{name}`
Get ingredient details

### POST `/api/v1/nutrition/analyze`
Analyze ingredient list
- Body: `["ingredient1", "ingredient2", ...]`

### POST `/api/v1/nutrition/score`
Calculate nutrition score
- Body: `["ingredient1", "ingredient2", ...]`

## Usage Example

```python
from modules.nutrition_engine.v1 import NutritionService, INGREDIENTS_DATABASE

service = NutritionService()

# Analyze ingredients
analysis = service.analyze_ingredients(["huile de pomme", "vanilline", "sel minéral"])
print(f"Total attraction score: {analysis.total_attraction_score}")

# Search ingredients
results = service.search("acide")
```

## Data Sources

- Extracted from BIONIC analyzer.py (original)
- Scientific references included in scoring_engine

## Dependencies

- None (isolated module)

---

*BIONIC V3 - Nutrition Engine - Created 2026-02-09*
