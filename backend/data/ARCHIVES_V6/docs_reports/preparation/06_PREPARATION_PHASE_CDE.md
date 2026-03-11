# RAPPORT 6 : PRÉPARATION PHASES C/D/E

**Date:** 2025-02-20  
**Mode:** ANALYSE UNIQUEMENT — AUCUNE EXÉCUTION  
**Phase:** PRÉPARATION ACCÉLÉRÉE

---

## PHASE C : ACCESSIBILITÉ (WCAG 2.1)

### 1. État Actuel

| Critère WCAG | Statut | Issues |
|--------------|--------|--------|
| 1.1.1 Contenu non textuel | ⚠️ PARTIEL | ~10 images sans alt |
| 1.4.3 Contraste minimum | ❌ ÉCHEC | 3185 occurrences text-gray |
| 2.1.1 Clavier | ⚠️ NON TESTÉ | À vérifier |
| 2.4.4 Lien significatif | ⚠️ PARTIEL | Boutons sans aria-label |
| 4.1.2 Nom, rôle, valeur | ⚠️ PARTIEL | Inputs sans label |

### 2. Issues Détaillées

#### Images sans alt (~10 fichiers)

```
/modules/cart/components/CartWidget.jsx
/modules/admin/components/BrandIdentityAdmin.jsx (4 occurrences)
/modules/admin/components/ContentDepot.jsx (2 occurrences)
/modules/admin/components/ProductDiscoveryAdmin.jsx (2 occurrences)
/modules/realestate/components/PropertyGallery.jsx
```

#### Contraste Insuffisant

```css
/* Classes problématiques (3185 occurrences) */
text-gray-400  /* Ratio ~3:1 sur fond sombre */
text-gray-500  /* Ratio ~4:1 sur fond sombre */
text-gray-600  /* Ratio ~5:1 sur fond sombre */
```

**Seuil WCAG AA:** 4.5:1 pour texte normal, 3:1 pour grand texte

### 3. Plan d'Action Phase C

| Action | Priorité | Fichiers | Risque |
|--------|----------|----------|--------|
| Ajouter alt aux images | P0 | 10 | FAIBLE |
| Corriger contraste | P0 | ~100 | FAIBLE |
| Ajouter aria-labels | P1 | ~50 | FAIBLE |
| Audit clavier complet | P1 | — | — |

---

## PHASE D : CORE WEB VITALS

### 1. État Actuel (Post-Bloc 2)

| Métrique | Valeur | Seuil Google | Statut |
|----------|--------|--------------|--------|
| LCP | ~3.5s | < 2.5s | ❌ |
| FID/INP | Non mesuré | < 100ms | ⚠️ |
| CLS | 0.000 | < 0.1 | ✅ |
| TBT | ~500ms | < 200ms | ❌ |

### 2. Causes Racines

#### LCP Élevé

1. **Image hero** — Format JPG, taille non optimisée
2. **Google Fonts** — @import blocking
3. **Main bundle** — 671KB

#### TBT Élevé

1. **LanguageContext** — 113KB inline
2. **Recharts** — 450KB chunk
3. **react-leaflet** — 518KB chunk

### 3. Plan d'Action Phase D

| Action | Impact | Priorité | Dépendance |
|--------|--------|----------|------------|
| WebP hero image | -300ms LCP | P0 | CDN externe |
| Preload fonts | -100ms LCP | P0 | Aucune |
| Tree-shake recharts | -100ms TBT | P1 | Bloc 3 |
| Split LanguageContext | -200ms TBT | P1 | Bloc 3 |
| Inline critical CSS | -50ms LCP | P2 | Aucune |

---

## PHASE E : SEO AVANCÉ

### 1. État Actuel

| Élément SEO | Statut | Score |
|-------------|--------|-------|
| Meta tags | ✅ | 92% |
| Structured Data | ⚠️ BASIQUE | — |
| Sitemap | ✅ | — |
| Robots.txt | ✅ | — |
| Open Graph | ⚠️ PARTIEL | — |
| Canonical URLs | ✅ | — |

### 2. Structured Data Existant

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Chasse Bionic",
  "url": "...",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "..."
  }
}
```

### 3. Structured Data Manquant

| Type | Usage | Priorité |
|------|-------|----------|
| Organization | À propos | P1 |
| Product | Pages produits | P0 |
| BreadcrumbList | Navigation | P1 |
| LocalBusiness | Contact | P2 |
| FAQPage | FAQ | P2 |

### 4. Plan d'Action Phase E

| Action | Priorité | Complexité |
|--------|----------|------------|
| Schema Product | P0 | FAIBLE |
| Schema Organization | P1 | FAIBLE |
| Schema BreadcrumbList | P1 | MOYENNE |
| Open Graph images | P1 | FAIBLE |
| Twitter Cards | P2 | FAIBLE |

---

## SYNTHÈSE PRÉPARATION C/D/E

### Matrice Effort/Impact

```
              IMPACT
         LOW    MED    HIGH
    LOW  |      |      | Font preload
E   MED  | OG   | Aria | Alt images
F   HIGH |      |      | WebP, Schema
F                         Product
O
R
T
```

### Roadmap Suggérée

1. **Phase C** (Accessibilité)
   - Durée estimée: 2-4 heures
   - Risque: FAIBLE
   - Prérequis: Aucun

2. **Phase D** (Core Web Vitals)
   - Durée estimée: 4-8 heures
   - Risque: MOYEN
   - Prérequis: Bloc 3 pour optimisations profondes

3. **Phase E** (SEO Avancé)
   - Durée estimée: 2-4 heures
   - Risque: FAIBLE
   - Prérequis: Aucun

---

## CHECKLIST PRÉPARATION

### Phase C (Accessibilité)
- [x] Identifier images sans alt
- [x] Auditer contraste couleurs
- [ ] Audit navigation clavier
- [ ] Préparer corrections aria

### Phase D (Core Web Vitals)
- [x] Identifier causes LCP
- [x] Identifier causes TBT
- [ ] Préparer optimisations fonts
- [ ] Préparer plan WebP

### Phase E (SEO)
- [x] Auditer structured data
- [x] Identifier schémas manquants
- [ ] Préparer templates JSON-LD
- [ ] Documenter Open Graph

---

*Rapport généré en mode ANALYSE UNIQUEMENT — AUCUNE MODIFICATION EFFECTUÉE*
