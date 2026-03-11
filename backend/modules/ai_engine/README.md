# AI Engine

## Module d'Intelligence Artificielle

### Version: 1.0.0
### Phase: 2 (Core Engines)
### API Prefix: `/api/v1/ai`

---

## Description

Le **AI Engine** intègre GPT-5.2 pour l'analyse intelligente des produits et la génération de recommandations personnalisées.

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/ai/
```

### 2. Analyse de Produit
```
POST /api/v1/ai/analyze
```
Analyse un produit avec l'IA.

**Body:**
```json
{
  "product_name": "Nom du produit",
  "ingredients": ["ingrédient1", "ingrédient2"],
  "category": "attractant"
}
```

### 3. Requête IA
```
POST /api/v1/ai/query
```
Pose une question à l'IA sur la chasse.

**Body:**
```json
{
  "question": "Quel est le meilleur attractant pour le cerf en novembre?",
  "context": "région Québec, forêt mixte"
}
```

### 4. Comparaison IA
```
POST /api/v1/ai/compare
```
Compare des produits avec analyse IA.

---

## Configuration

Le module utilise l'**Emergent LLM Key** pour accéder à GPT-5.2.

```python
from emergentintegrations.llm.chat import chat

response = await chat(
    api_key=EMERGENT_KEY,
    prompt=user_question,
    model="gpt-5.2"
)
```

---

## Fonctionnalités

1. **Analyse de produits** - Évaluation automatique des ingrédients
2. **Recommandations** - Suggestions personnalisées
3. **Q&A** - Réponses aux questions de chasse
4. **Comparaison** - Analyse comparative de produits

---

## Intégration Future

- [ ] Intégration GPT-5.2 complète
- [ ] Cache des réponses
- [ ] Historique de conversation

---

*HUNTIQ V3 - AI Engine - Phase 2*
