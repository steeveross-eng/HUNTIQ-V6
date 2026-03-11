# Orders Engine

## Module de Gestion des Commandes

### Version: 1.0.0
### Phase: 7 (Decoupled from Monolith)
### API Prefix: `/api/v1/orders`

---

## Description

Le **Orders Engine** gère les commandes avec support du modèle hybride dropshipping/affiliation.

---

## Endpoints API

### 1. Liste des Commandes
```
GET /api/v1/orders/
```
Retourne les commandes de l'utilisateur connecté.

### 2. Créer Commande
```
POST /api/v1/orders/
```
Crée une nouvelle commande.

**Body:**
```json
{
  "items": [
    {"product_id": "prod_123", "quantity": 2}
  ],
  "shipping_address": {...},
  "payment_method": "card"
}
```

### 3. Détail Commande
```
GET /api/v1/orders/{order_id}
```

### 4. Annuler Commande
```
POST /api/v1/orders/{order_id}/cancel
```

### 5. Suivi
```
GET /api/v1/orders/{order_id}/tracking
```

---

## Statuts de Commande

| Status | Description |
|--------|-------------|
| `pending` | En attente de paiement |
| `paid` | Payée |
| `processing` | En préparation |
| `shipped` | Expédiée |
| `delivered` | Livrée |
| `cancelled` | Annulée |

---

## Modèle Hybride

Le système supporte deux modèles de vente :

### Dropshipping
- HUNTIQ ne stocke pas les produits
- Commande transmise au fournisseur
- Livraison directe au client

### Affiliation
- Redirection vers le site partenaire
- Commission sur les ventes
- Suivi des clics via `affiliate_engine`

---

## Modèle de Données

```json
{
  "id": "ord_456",
  "user_id": "user_123",
  "items": [...],
  "subtotal": 59.98,
  "shipping": 9.99,
  "total": 69.97,
  "status": "paid",
  "created_at": "2026-02-09T12:00:00Z"
}
```

---

*HUNTIQ V3 - Orders Engine - Phase 7*
