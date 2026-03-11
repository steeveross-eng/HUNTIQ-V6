# RAPPORT 3 : IMAGES CRITIQUES ET FORMATS

**Date:** 2025-02-20  
**Mode:** ANALYSE UNIQUEMENT — AUCUNE EXÉCUTION  
**Phase:** PRÉPARATION ACCÉLÉRÉE

---

## 1. INVENTAIRE DES IMAGES

### Images Locales (/assets)

| Type | Quantité | Statut |
|------|----------|--------|
| JPG/JPEG | 0 | ✅ Optimisé (Bloc 1) |
| PNG | 0 | ✅ Optimisé (Bloc 1) |
| WebP | 0 | ⚠️ Non utilisé |
| SVG | 0 | — |

**Note:** Les images ont été optimisées en Bloc 1 (4.7MB → 2.0MB)

### Images Externes (CDN/URLs)

| Image | Source | Format | Impact LCP |
|-------|--------|--------|------------|
| Hero background | customer-assets.emergentagent.com | JPG | CRITIQUE |
| Leaflet markers | cdnjs.cloudflare.com | PNG | FAIBLE |
| Map tiles | cartocdn.com | PNG | MOYEN |
| Avatar badge | avatars.githubusercontent.com | Variable | FAIBLE |

---

## 2. ANALYSE IMAGE HERO (LCP)

### État Actuel

```css
.hero-bg {
  background-image: linear-gradient(...),
    url('https://customer-assets.emergentagent.com/.../IMG_2019.JPG');
  background-size: cover;
  background-position: center 30%;
  background-attachment: fixed;
}
```

### Problèmes Identifiés

1. **Format JPG** — Non optimal pour le web moderne
2. **Taille estimée** — ~500KB+ (full resolution)
3. **Pas de srcset** — Même image pour mobile et desktop
4. **fixed attachment** — Cause des problèmes de performance sur mobile

### Optimisations Possibles (Phase D)

| Action | Impact LCP | Difficulté |
|--------|------------|------------|
| Conversion WebP | -30% taille | FAIBLE |
| Conversion AVIF | -50% taille | MOYENNE |
| Responsive images (srcset) | -40% mobile | MOYENNE |
| Suppression fixed attachment | +10% mobile perf | FAIBLE |

---

## 3. ANALYSE LEAFLET MARKERS

### État Actuel

```javascript
// Versions mixtes détectées
iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png'
iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png'
```

### Problèmes

1. **Incohérence de versions** — 1.7.1 et 1.9.4 utilisées
2. **Téléchargements multiples** — Même icône téléchargée plusieurs fois
3. **Pas de cache control** — CDN externe

### Recommandation (Bloc 3)

- Unifier sur la version 1.9.4
- Self-host les icônes dans `/public/images/`
- Utiliser des icônes SVG personnalisées

---

## 4. FORMAT RECOMMANDÉ PAR TYPE

| Type d'Image | Format Actuel | Format Recommandé | Gain Estimé |
|--------------|---------------|-------------------|-------------|
| Hero | JPG | WebP/AVIF | 40-60% |
| Produits | JPG | WebP | 30% |
| Icônes | PNG | SVG | 80% |
| Logos | SVG | SVG | — |
| Maps tiles | PNG | — (CDN externe) | — |

---

## 5. CHECKLIST PRÉPARATION

- [ ] Image hero : Demander version WebP au CDN
- [ ] Leaflet markers : Préparer migration self-hosted
- [ ] Produits : Implémenter lazy loading avec blur placeholder
- [ ] Responsive : Préparer srcset pour les images critiques

---

*Rapport généré en mode ANALYSE UNIQUEMENT*
