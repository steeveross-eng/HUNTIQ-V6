# RAPPORT 4 : FONTS ET STRATÉGIE DE CHARGEMENT

**Date:** 2025-02-20  
**Mode:** ANALYSE UNIQUEMENT — AUCUNE EXÉCUTION  
**Phase:** PRÉPARATION ACCÉLÉRÉE

---

## 1. INVENTAIRE DES FONTS

### Google Fonts Déclarées

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
```

| Famille | Weights | Usage | Fichiers |
|---------|---------|-------|----------|
| Barlow Condensed | 400, 500, 600, 700, 900 | Headings | 5 |
| Inter | 400, 500, 600, 700 | Body | 4 |
| JetBrains Mono | 400, 500, 600 | Code | 3 |
| **TOTAL** | **12 weights** | — | **~12 fichiers** |

### Estimation Taille

- Barlow Condensed: ~100KB (5 weights × ~20KB)
- Inter: ~80KB (4 weights × ~20KB)
- JetBrains Mono: ~60KB (3 weights × ~20KB)
- **Total estimé: ~240KB**

---

## 2. PROBLÈMES IDENTIFIÉS

### 2.1 Utilisation de @import (CRITIQUE)

```css
/* PROBLÈME: @import est render-blocking */
@import url('https://fonts.googleapis.com/...');
```

**Impact:** Bloque le rendu jusqu'au téléchargement complet

**Solution (Phase C):**
```html
<!-- Dans index.html -->
<link rel="preload" href="https://fonts.googleapis.com/..." as="style">
<link rel="stylesheet" href="https://fonts.googleapis.com/...">
```

### 2.2 Trop de Weights (MOYEN)

| Famille | Weights Déclarés | Weights Utilisés* |
|---------|------------------|-------------------|
| Barlow Condensed | 5 | ~3 |
| Inter | 4 | ~3 |
| JetBrains Mono | 3 | ~2 |

*Estimation basée sur l'analyse du CSS

### 2.3 font-display (BON)

```css
display=swap /* Déjà présent dans l'URL */
```

✅ `font-display: swap` est correctement configuré

---

## 3. PRECONNECT STATUS

### Actuel (index.html)

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
```

✅ Preconnect correctement configuré

---

## 4. STRATÉGIE OPTIMALE RECOMMANDÉE

### Option A: Optimisation Google Fonts (Risque Faible)

1. **Réduire les weights:**
```css
/* Avant */
family=Barlow+Condensed:wght@400;500;600;700;900

/* Après */
family=Barlow+Condensed:wght@400;600;700
```

2. **Utiliser <link> au lieu de @import:**
```html
<link rel="preload" as="style" href="...">
```

3. **Supprimer JetBrains Mono** si non utilisé en production

### Option B: Self-Hosting (Risque Moyen)

- Télécharger les fonts via google-webfonts-helper
- Héberger dans `/public/fonts/`
- Contrôle total sur le cache

**Gain estimé:** 50-100ms LCP

### Option C: Font Subsetting (Risque Faible)

- Utiliser `&text=` pour ne charger que les caractères nécessaires
- Applicable aux titres avec texte statique

---

## 5. MATRICE DÉCISIONNELLE

| Action | Impact | Risque | Phase |
|--------|--------|--------|-------|
| Remplacer @import par <link> | ÉLEVÉ | FAIBLE | C |
| Réduire weights | MOYEN | FAIBLE | C |
| Self-hosting | MOYEN | MOYEN | D |
| Font subsetting | FAIBLE | FAIBLE | E |

---

## 6. CHECKLIST PRÉPARATION

- [ ] Auditer l'utilisation réelle de chaque weight
- [ ] Préparer les balises `<link rel="preload">`
- [ ] Documenter les fonts critiques vs non-critiques
- [ ] Évaluer le self-hosting pour la production

---

*Rapport généré en mode ANALYSE UNIQUEMENT*
