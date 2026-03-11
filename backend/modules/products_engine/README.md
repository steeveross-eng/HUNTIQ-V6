# Products Engine

## Module de Gestion des Produits

### Version: 1.0.0
### Phase: 7 (Decoupled from Monolith)
### API Prefix: `/api/v1/products`

---

## Description

Le **Products Engine** gère le catalogue de produits de chasse : attractants, équipements, vêtements et accessoires.

---

## Endpoints API

### 1. Liste des Produits
```
GET /api/v1/products/
```
Retourne la liste des produits avec pagination.

**Paramètres:**
- `page` (int): Numéro de page
- `limit` (int): Produits par page
- `category` (string): Filtrer par catégorie
- `sort` (string): Tri (price, score, name)

### 2. Produit par ID
```
GET /api/v1/products/{product_id}
```

### 3. Recherche
```
GET /api/v1/products/search
```
Recherche full-text dans les produits.

### 4. Par Catégorie
```
GET /api/v1/products/category/{category}
```

### 5. Top Produits
```
GET /api/v1/products/top
```
Retourne les produits les mieux notés.

---

## Catégories

| Code | Nom | Description |
|------|-----|-------------|
| `attractants` | Attractants | Leurres olfactifs |
| `equipment` | Équipement | Matériel de chasse |
| `clothing` | Vêtements | Tenues camouflage |
| `optics` | Optique | Lunettes, jumelles |
| `accessories` | Accessoires | Divers |

---

## Modèle de Données

```json
{
  "id": "prod_123",
  "name": "Attractant Cerf Premium",
  "brand": "BionicHunt",
  "category": "attractants",
  "price": 29.99,
  "score": 92,
  "description": "...",
  "image_url": "...",
  "ingredients": [...],
  "specs": {...}
}
```

---

## Intégration Frontend

```javascript
import { ProductsService } from '../modules/products';

// Liste des produits
const products = await ProductsService.getProducts();

// Top produits
const top = await ProductsService.getTopProducts();

// Par catégorie
const attractants = await ProductsService.getByCategory('attractants');
```

---

*HUNTIQ V3 - Products Engine - Phase 7*
