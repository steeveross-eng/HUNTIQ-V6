# RAPPORT 1 : CARTOGRAPHIE LCP/TBT

**Date:** 2025-02-20  
**Mode:** ANALYSE UNIQUEMENT — AUCUNE EXÉCUTION  
**Phase:** PRÉPARATION ACCÉLÉRÉE

---

## 1. COMPOSANTS CRITIQUES LCP

### Fichiers les Plus Volumineux (Impact TBT Direct)

| Fichier | Lignes | Impact | Zone |
|---------|--------|--------|------|
| TerritoryMap.jsx | 5127 | CRITIQUE | ⛔ INTERDITE |
| LanguageContext.jsx | 3008 | ÉLEVÉ | ⛔ INTERDITE |
| MonTerritoireBionicPage.jsx | 2425 | ÉLEVÉ | ✅ AUTORISÉE |
| LandsRental.jsx | 1951 | MOYEN | ✅ AUTORISÉE |
| NetworkingHub.jsx | 1539 | MOYEN | ✅ AUTORISÉE |
| HuntMarketplace.jsx | 1462 | MOYEN | ✅ AUTORISÉE |
| AdminPage.jsx | 1125 | MOYEN | ✅ AUTORISÉE |
| App.js | 1069 | ÉLEVÉ | ✅ AUTORISÉE |

### Analyse LCP - Éléments Responsables

| Page | Élément LCP Probable | Cause |
|------|---------------------|-------|
| Home | Image hero (background) | Image externe non optimisée |
| Shop | Première image produit | Images produits non lazy |
| Map | Canvas Leaflet | Initialisation lourde |
| Territoire | Canvas Leaflet + layers | Multiple TileLayers |

---

## 2. ANALYSE TBT (Total Blocking Time)

### Bundles Critiques

| Bundle | Taille | Contenu Probable |
|--------|--------|------------------|
| main.js | 671KB | Core app + React |
| 8779.chunk.js | 518KB | react-leaflet + leaflet |
| 486.chunk.js | 450KB | recharts |
| 1007.chunk.js | 427KB | @radix-ui composants |
| 7841.chunk.js | 382KB | lucide-react icons |

### Sources de Blocking Time

1. **LanguageContext** (113KB) — Chargé au démarrage, contient ~3000 lignes de traductions
2. **react-leaflet** — Initialisation lourde des cartes
3. **recharts** — Bibliothèque de graphiques complexe
4. **@radix-ui** — Nombreux composants UI importés

---

## 3. OPTIMISATIONS POTENTIELLES (BLOC 3+)

### Priorité Haute (Impact TBT)

| Action | Impact Estimé | Risque | Zone |
|--------|---------------|--------|------|
| Lazy-load LanguageContext | -200ms TBT | ÉLEVÉ | ⛔ INTERDIT |
| Lazy-load react-leaflet | -150ms TBT | MOYEN | ✅ POSSIBLE |
| Tree-shake recharts | -100ms TBT | FAIBLE | ✅ POSSIBLE |
| Tree-shake lucide-react | -50ms TBT | FAIBLE | ✅ POSSIBLE |

### Priorité Moyenne (Impact LCP)

| Action | Impact Estimé | Risque |
|--------|---------------|--------|
| WebP pour image hero | -300ms LCP | FAIBLE |
| Inline critical CSS | -100ms LCP | MOYEN |
| Font-display: swap | -50ms LCP | FAIBLE |

---

## 4. RECOMMANDATIONS SANS MODIFICATION DE CODE

1. **CDN Assets** — Vérifier si les images Leaflet peuvent être self-hosted
2. **Font Subsetting** — Réduire le nombre de weights chargés
3. **Image Hero** — Convertir en WebP côté CDN externe

---

*Rapport généré en mode ANALYSE UNIQUEMENT*
