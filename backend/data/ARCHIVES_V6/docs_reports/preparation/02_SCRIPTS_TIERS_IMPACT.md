# RAPPORT 2 : SCRIPTS TIERS ET IMPACT

**Date:** 2025-02-20  
**Mode:** ANALYSE UNIQUEMENT — AUCUNE EXÉCUTION  
**Phase:** PRÉPARATION ACCÉLÉRÉE

---

## 1. INVENTAIRE DES SCRIPTS TIERS

### Scripts dans index.html

| Script | Source | Type | Impact |
|--------|--------|------|--------|
| emergent-main.js | assets.emergent.sh | Analytics | FAIBLE |
| PostHog | us.i.posthog.com | Analytics | MOYEN |
| debug-monitor.js | assets.emergent.sh | Dev tools | FAIBLE (iframe only) |
| Tailwind CDN | cdn.tailwindcss.com | CSS | FAIBLE (iframe only) |

### CDN Ressources Externes

| Ressource | CDN | Usage | Impact |
|-----------|-----|-------|--------|
| Leaflet markers | cdnjs.cloudflare.com | Cartes | FAIBLE |
| Map tiles | basemaps.cartocdn.com | Cartes | ÉLEVÉ |
| Map tiles | tile.openstreetmap.org | Cartes | ÉLEVÉ |
| Map tiles | tile.opentopomap.org | Cartes | MOYEN |
| Hero image | customer-assets.emergentagent.com | UI | ÉLEVÉ |

---

## 2. ANALYSE D'IMPACT

### PostHog Analytics

```javascript
// Chargé de manière asynchrone
posthog.init("phc_...", {
  api_host: "https://us.i.posthog.com",
  person_profiles: "identified_only",
  session_recording: { recordCrossOriginIframes: true }
});
```

**Impact:**
- Téléchargement: ~50KB
- Exécution: ~100ms (asynchrone)
- Blocking: NON (async)

**Recommandation:** Conserver tel quel (non-blocking)

### Leaflet/Carto Tiles

**Impact:**
- Latence réseau: Variable (CDN)
- Blocking: NON (lazy loaded)
- Problème: Multiple versions (1.7.1 et 1.9.4)

**Recommandation (Bloc 3):**
- Unifier la version Leaflet
- Considérer le self-hosting des marker icons

### Google Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
```

**Impact:**
- Téléchargement: ~150KB (3 familles × ~5 weights)
- Blocking: OUI (render-blocking CSS @import)

**Recommandation (Phase C):**
- Utiliser `<link rel="preload">` au lieu de `@import`
- Réduire les weights (ex: seulement 400, 600, 700)
- Ajouter `font-display: swap` explicite

---

## 3. MATRICE DE PRIORITÉ

| Script/Ressource | Impact Performance | Criticité Business | Action |
|------------------|-------------------|-------------------|--------|
| PostHog | FAIBLE | HAUTE | CONSERVER |
| Google Fonts | MOYEN | HAUTE | OPTIMISER |
| Leaflet CDN | FAIBLE | MOYENNE | CONSOLIDER |
| Hero Image | ÉLEVÉ | HAUTE | OPTIMISER FORMAT |
| Tailwind CDN | FAIBLE | FAIBLE | IGNORER (iframe) |

---

## 4. QUICK WINS (Sans Modification Code Critique)

1. **Preload fonts** — Ajouter `<link rel="preload">` dans index.html
2. **Font weights** — Réduire de 14 weights à 8
3. **Leaflet version** — Documenter l'incohérence pour Bloc 3

---

*Rapport généré en mode ANALYSE UNIQUEMENT*
