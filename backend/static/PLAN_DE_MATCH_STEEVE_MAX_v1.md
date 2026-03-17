# PLAN DE MATCH STEEVE-MAX v1

## Document normatif officiel — BIONIC V3
**Date:** 2026-03-16
**Statut:** NORMATIF — Référence obligatoire pour tous les moteurs futurs
**Auteur:** Emergent AI sous direction de Steeve
**Conformité:** BCE-4X + Steeve-MAX

---

## TABLE DES MATIÈRES

1. Définitions écologiques 3× plus précises
2. Normes BCE-4X — Firewall scientifique
3. Normes Steeve-MAX — Norme d'exécution et de qualité
4. Roadmap des moteurs futurs
5. Dépendances entre moteurs
6. Critères de livraison par moteur
7. Schéma du pipeline intégré

---

## 1. DÉFINITIONS ÉCOLOGIQUES 3× PLUS PRÉCISES

### 1.1 — Habitat optimal (HABITAT-V1)

Zone où la combinaison de SCORE_ALIMENTATION_[espèce], SCORE_REPOS_[espèce], sécurité, accessibilité, pression faible et connectivité fonctionnelle permet :
- une occupation régulière,
- la reproduction,
- la survie hivernale,
- la présence des individus dominants.

**Variables d'entrée:**
| Variable | Source | Résolution |
|---|---|---|
| Score alimentation | ALIMENTATION-V1 | 10m |
| Score repos | REPOS-V1 | 10m |
| Corridors | CORRIDORS-V10 | 10m |
| Hydrographie | Couches fines | 10m |
| Pente | LiDAR/DEM | 10m |
| Orientation | LiDAR/DEM | 10m |
| Ensoleillement | Modèle solaire | 10m |
| Type de forêt | Écoforestier | 10m |
| Transition (lisière) | Calcul | 10m |
| Pression humaine | OSM + algorithmique | 10m |

**Score:** SCORE_HABITAT (0-100)
**Classification:** OPTIMAL (80-100) / TRÈS BON (60-79) / UTILISABLE (40-59) / FAIBLE (<40)

### 1.2 — Zones de rut (RUT-V1)

Zones où mâles dominants et femelles se concentrent selon la saison, en fonction de l'alimentation, du repos, de la connectivité, de la structure sociale et de la pression.

**Sous-phases:**
| Phase | Période | Comportement dominant |
|---|---|---|
| Pré-rut | Sept-Oct | Alimentation riche + repos sécurisés + marquage |
| Rut | Oct-Nov | Convergence femelles + noyaux marquage + corridors dominants |
| Post-rut | Nov-Déc | Remise en énergie + repos maximal + récupération |

**Variables d'entrée:**
- ALIMENTATION-V1 (pondération par phase)
- REPOS-V1 (pondération par phase)
- CORRIDORS-V10 (axes de convergence)
- Structure sociale (dominants, femelles)
- Pression humaine (distance perturbations)
- Topographie (crêtes, vallées, points de vue)

**Score:** SCORE_RUT (0-100) par phase (pré-rut, rut, post-rut)
**Classification:** CRITIQUE (80-100) / FORT (60-79) / MODÉRÉ (40-59) / FAIBLE (<40)

### 1.3 — Corridors fauniques (CORRIDORS-V10)

Axes de déplacement réellement utilisés, reliant repos, alimentation, rut et eau, en minimisant effort, risque et pression.

**Variables d'entrée:**
| Variable | Rôle |
|---|---|
| Pente | Coût énergétique par segment |
| Orientation | Préférence micro-climat |
| Ensoleillement | Confort thermique parcours |
| Hydrographie | Ressource + barrière + corridor |
| Zones humides | Minéraux + corridor potentiel |
| Types de forêts | Couvert de transit |
| Lisières | Axes de déplacement préférés |
| Clairières | Points de transition |
| Ravines | Corridors naturels protégés |
| Crêtes | Points de vue + axes d'observation |
| Vallées | Axes de déplacement naturels |
| Pression humaine | Évitement routes, bâtiments |
| Anciens chemins forestiers | Axes réutilisables |
| Zones calmes | Préférence de transit |
| Vent dominant | Direction optimale approche |
| Usages des dominants | Patterns comportementaux |

**Score:** SCORE_CORRIDOR (0-100) par segment
**Classification:** CRITIQUE (86-100) / PRIMAIRE (71-85) / FONCTIONNEL (51-70) / OPPORTUNISTE (31-50) / POTENTIEL (0-30)

### 1.4 — Hydrographie

Rivières, ruisseaux, fossés, mares, zones humides et suintements jouant un rôle de ressource, de barrière ou de corridor.

| Espèce | Rôle principal |
|---|---|
| Cerf | Minéraux + fraîcheur + bordures comme axes |
| Orignal | Minéraux + fraîcheur + végétation aquatique |
| Wapiti | Minéraux + fraîcheur + bordures comme axes |
| Ours | Fraîcheur + baies + zones calmes |
| Dindon | Insectes + nourriture humide |

### 1.5 — Pentes

Carte de l'effort énergétique et de la difficulté de déplacement, modulée par espèce.

| Espèce | Pente optimale | Pente max | Tolérance |
|---|---|---|---|
| Cerf | ≤5° | 15° | Faible |
| Orignal | ≤8° | 25° | Modérée |
| Ours | ≤12° | 35° | Élevée |
| Dindon | ≤3° | 12° | Très faible |
| Wapiti | ≤8° | 22° | Moyenne |

### 1.6 — Orientation

Influence micro-climat, thermique, fonte de neige, productivité.

| Versant | Caractéristiques | Utilisation |
|---|---|---|
| Sud | Sec, chaud, fonte rapide | Alimentation + rut |
| Nord | Frais, ombragé, neige persistante | Repos + orignal + ours |
| Est | Exposition matinale, modéré | Transition |
| Ouest | Chaleur après-midi | Alimentation tardive |

### 1.7 — Ensoleillement

| Saison | Effet principal |
|---|---|
| Hiver | Recherche de soleil (réchauffement, fonte) |
| Été | Recherche d'ombre (confort thermique) |
| Automne | Zones mixtes (alimentation active) |
| Printemps | Zones dégagées (croissance végétale) |

### 1.8 — Affûts potentiels (AFFÛTS-V1)

Positions où probabilité de passage est maximale et détection minimale.

**Variables d'entrée:**
- Habitat optimal (HABITAT-V1)
- Corridors (CORRIDORS-V10)
- Zones de rut (RUT-V1)
- Hydrographie
- Vent dominant (direction + force)
- Pression humaine
- Accessibilité
- Visibilité
- Couvert du chasseur

**Score:** SCORE_AFFUT (0-100)
**Classification:** PREMIUM (80-100) / BON (60-79) / ACCEPTABLE (40-59) / FAIBLE (<40)

### 1.9 — Trajets de chasse (TRAJETS-V1)

Séquences continues alignées sur corridors, affûts, zones d'intérêt, vent dominant, pression et accessibilité.

**Objectifs:**
- Minimiser le dérangement
- Maximiser les opportunités
- Préserver la cohérence du territoire

**Variables d'entrée:**
- Tous les scores moteurs (ALIMENTATION, REPOS, HABITAT, RUT, CORRIDORS, AFFÛTS)
- Vent dominant
- Pression humaine
- Accessibilité physique
- Historique de passages

---

## 2. NORMES BCE-4X — FIREWALL SCIENTIFIQUE ET GÉOMÉTRIQUE

### 2.1 — Validation géométrique (100%)
| Code | Règle | Seuil |
|---|---|---|
| GEOM-001 | Score dans [0, 100] | 100% des cellules |
| GEOM-002 | Classification valide | 100% des cellules |
| GEOM-003 | Polygone ≥ 3 sommets | 100% des polygones |
| GEOM-004 | Aucun pixel hors carré 2km² | 0 violations |
| CLIP-001 | Corridor clippé max 150m | 100% des segments |

### 2.2 — Validation écologique
| Code | Règle |
|---|---|
| ECO-001 | Espèce → Profil → Pondérations cohérentes |
| ECO-002 | Saisonnalité appliquée (4 saisons + rut) |
| ECO-003 | Sources alimentaires scientifiquement fondées |
| ECO-004 | Comportement repos basé sur rythme circadien |

### 2.3 — Validation topographique
| Code | Règle |
|---|---|
| TOPO-001 | Pente calculée par cellule 10m |
| TOPO-002 | Orientation (aspect) par cellule |
| TOPO-003 | Hydrographie intégrée |
| TOPO-004 | LiDAR (MNT/CHM) utilisé |

### 2.4 — Validation comportementale
| Code | Règle |
|---|---|
| BEHAV-001 | Profils dominants intégrés (rut) |
| BEHAV-002 | Rythme circadien par espèce |
| BEHAV-003 | Tolérance au dérangement par espèce |
| BEHAV-004 | Patterns de déplacement réalistes |

### 2.5 — Validation anti-régression
| Code | Règle |
|---|---|
| REG-001 | Aucune modification des engines existants (V2, V3, IA, V9) |
| REG-002 | Seuil dynamique d'attractivité inchangé |
| REG-003 | Carré 2km² réutilisé tel quel |
| REG-004 | Tests d'intégration post-livraison |

### 2.6 — Validation inter-moteurs
| Code | Règle |
|---|---|
| INTER-001 | Aucune contradiction entre scores moteurs |
| INTER-002 | Pondérations cross-moteurs documentées |
| INTER-003 | Score consolidé traçable |

---

## 3. NORMES STEEVE-MAX — EXÉCUTION ET QUALITÉ

### 3.1 — Documentation complète
- Fiche technique JSON pour chaque moteur
- Métadonnées (version, date, auteur, statut)
- Description des inputs/outputs
- Formules de scoring documentées

### 3.2 — Traçabilité totale
- Chaque score décomposable en sous-scores
- Chaque sous-score traçable aux couches d'entrée
- Historique des versions

### 3.3 — Cohérence visuelle
- Palette unique : bleu (faible) → vert (modéré) → jaune (bon) → rouge (optimal)
- Badges et labels uniformes
- Heatmap comme référence visuelle officielle

### 3.4 — Cohérence multi-espèces
- 5 espèces (CERF, ORIGNAL, OURS, DINDON, WAPITI)
- Forces et faiblesses par espèce
- Pondérations spécifiques documentées

### 3.5 — Cohérence saisonnière
- 4 saisons + 3 phases de rut
- Ajustements automatiques par mois
- Multiplicateurs saisonniers traçables

### 3.6 — Cohérence opérationnelle
- Corridors continus et fonctionnels
- Affûts positionnés scientifiquement
- Trajets optimisés et réalistes

### 3.7 — Exécution stricte
- Zéro interprétation libre
- Directives appliquées à la lettre
- Toute déviation documentée et justifiée

---

## 4. ROADMAP DES MOTEURS FUTURS

| # | Moteur | Statut | Dépendances | Priorité |
|---|---|---|---|---|
| 1 | ALIMENTATION-V1 | LIVRÉ | Couches fines | P0 |
| 2 | REPOS-V1 | LIVRÉ | Couches fines | P0 |
| 3 | CORRIDORS-V10 | À CONSTRUIRE | ALIMENTATION-V1, REPOS-V1, couches fines | P0 |
| 4 | HABITAT-V1 | À CONSTRUIRE | ALIMENTATION-V1, REPOS-V1, CORRIDORS-V10 | P0 |
| 5 | RUT-V1 | À CONSTRUIRE | HABITAT-V1, CORRIDORS-V10 | P1 |
| 6 | AFFÛTS-V1 | À CONSTRUIRE | HABITAT-V1, CORRIDORS-V10, RUT-V1 | P1 |
| 7 | TRAJETS-V1 | À CONSTRUIRE | Tous les moteurs | P2 |

---

## 5. DÉPENDANCES ENTRE MOTEURS

```
COUCHES FINES (LiDAR, essences, hydro, pente, sol)
        |
        +-----> ALIMENTATION-V1 (LIVRÉ)
        |               |
        +-----> REPOS-V1 (LIVRÉ)
        |               |
        +-----> CORRIDORS-V10 <--- ALIMENTATION + REPOS
        |               |
        |       HABITAT-V1 <--- ALIMENTATION + REPOS + CORRIDORS-V10
        |               |
        |       RUT-V1 <--- HABITAT + CORRIDORS-V10
        |               |
        |       AFFÛTS-V1 <--- HABITAT + CORRIDORS + RUT
        |               |
        |       TRAJETS-V1 <--- TOUS LES MOTEURS
        |
        v
  SCORE CONSOLIDÉ --> HEATMAP OFFICIEL
        |
  BCE-4X VALIDATION
        |
  STEEVE-MAX VALIDATION
```

---

## 6. CRITÈRES DE LIVRAISON PAR MOTEUR

Chaque moteur doit satisfaire TOUS les critères suivants avant validation :

### Critères techniques
- [ ] Module 100% indépendant (`/app/backend/modules/{moteur}/`)
- [ ] Grille 10m × 10m dans le carré 2km² existant
- [ ] 5 espèces supportées (CERF, ORIGNAL, OURS, DINDON, WAPITI)
- [ ] Score composite documenté (axes + pondérations)
- [ ] Classification 4+ niveaux
- [ ] API REST complète (analyze, point, profiles, documentation)
- [ ] Validation BCE-4X intégrée et PASS

### Critères scientifiques
- [ ] Variables d'entrée documentées
- [ ] Pondérations par espèce justifiées
- [ ] Saisonnalité implémentée
- [ ] Profils espèces conformes aux définitions §1

### Critères qualité (Steeve-MAX)
- [ ] Documentation JSON complète
- [ ] Traçabilité score → sous-scores → couches
- [ ] Tests backend PASS (pytest)
- [ ] Tests frontend PASS (si intégré)
- [ ] Aucune régression (engines existants intacts)

### Critères visuels (si intégré au heatmap)
- [ ] Palette conforme (bleu → vert → jaune → rouge)
- [ ] Badge score + label + anneau
- [ ] Transparence ajustée
- [ ] Contours nets zones fortes

---

## 7. SCHÉMA DU PIPELINE INTÉGRÉ

```
  UTILISATEUR
  [espèce, position, rayon, saison, heure]
        |
        v
  COUCHES FINES ─────────────────────────────────────
  LiDAR | Essences | Sol | Hydro | Conifères | Pente
        |
        +──> ALIMENTATION-V1 ──> Score 0-100
        |
        +──> REPOS-V1 ──────────> Score 0-100
        |
        +──> CORRIDORS-V10 ─────> Score 0-100 (segment)
        |
        +──> HABITAT-V1 ────────> Score 0-100
        |
        +──> RUT-V1 ────────────> Score 0-100 (par phase)
        |
        +──> AFFÛTS-V1 ─────────> Score 0-100
        |
        +──> TRAJETS-V1 ────────> Séquence optimisée
        |
        v
  SCORE CONSOLIDÉ ──────────────────────────────────
  = f(ALIM, REPOS, CORR, HABITAT, RUT) × espèce
        |
        +──> HEATMAP OFFICIEL (palette bleu→rouge)
        +──> Badge score + label + anneau
        +──> Seuil dynamique d'attractivité
        |
        v
  BCE-4X VALIDATION ────────────────────────────────
  GEOM + ECO + TOPO + BEHAV + REG + INTER
        |
        v
  STEEVE-MAX VALIDATION ────────────────────────────
  DOC + TRACE + VISUEL + ESPÈCES + SAISON + OPS
        |
        v
  LIVRAISON ✓
```

---

## ANNEXE — SIGNATURES DE CONFORMITÉ

| Norme | Statut |
|---|---|
| BCE-4X Géométrique | OBLIGATOIRE |
| BCE-4X Écologique | OBLIGATOIRE |
| BCE-4X Topographique | OBLIGATOIRE |
| BCE-4X Comportemental | OBLIGATOIRE |
| BCE-4X Anti-régression | OBLIGATOIRE |
| BCE-4X Inter-moteurs | OBLIGATOIRE |
| Steeve-MAX Documentation | OBLIGATOIRE |
| Steeve-MAX Traçabilité | OBLIGATOIRE |
| Steeve-MAX Visuel | OBLIGATOIRE |
| Steeve-MAX Multi-espèces | OBLIGATOIRE |
| Steeve-MAX Saisonnier | OBLIGATOIRE |
| Steeve-MAX Opérationnel | OBLIGATOIRE |

---

*Fin du PLAN DE MATCH STEEVE-MAX v1 — Document normatif officiel*
*Aucune modification de code effectuée. Observation et formalisation uniquement.*
*Toute déviation aux normes ci-dessus nécessite l'approbation explicite de Steeve.*
