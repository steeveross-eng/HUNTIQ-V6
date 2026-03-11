# HUNTIQ-V5 — ARCHITECTURE /core/ DOCUMENTATION

**Date:** 2025-02-20  
**Version:** 6.2.0 (BLOC 3)  
**Type:** DOCUMENTATION DES FRONTIÈRES

---

## 1. STRUCTURE DU DOSSIER /core/

```
/app/frontend/src/core/
├── bionic/           # Moteur BIONIC (VERROUILLÉ)
├── components/       # Composants core (SEOHead, BionicLogo)
├── contexts/         # Contexts sensibles (PopupContext)
├── hooks/            # Hooks core
├── layouts/          # Layouts principaux
├── utils/            # Utilitaires core
└── index.js          # Point d'entrée
```

---

## 2. RESPONSABILITÉS PAR MODULE

### /core/bionic/ — VERROUILLÉ (AUCUNE MODIFICATION)

**Responsabilité:** Moteur d'intelligence BIONIC  
**Statut:** ZONE INTERDITE  
**Contenu:** Algorithmes de scoring, prédiction, analyse territoriale

### /core/components/

**Responsabilité:** Composants fondamentaux réutilisables  
**Fichiers:**
- `SEOHead.jsx` — Gestion des meta tags SEO
- `BionicLogo.jsx` — Logo animé BIONIC

**Note:** Les fichiers ont été dédupliqués en BLOC 3

### /core/contexts/

**Responsabilité:** Contexts React sensibles  
**Fichiers:**
- `PopupContext.jsx` — Gestion des popups/modales

**Note:** LanguageContext et AuthContext sont dans leurs dossiers respectifs

### /core/hooks/

**Responsabilité:** Hooks personnalisés core  
**Statut:** Sensible — modifications avec précaution

### /core/layouts/

**Responsabilité:** Layouts de page principaux  
**Statut:** Modifiable avec précaution

### /core/utils/

**Responsabilité:** Fonctions utilitaires core  
**Statut:** Modifiable

---

## 3. CONTRATS D'INTERFACE

### LanguageContext (src/contexts/LanguageContext.jsx)

**API Publique:**
```typescript
interface LanguageContextValue {
  language: 'fr' | 'en';
  setLanguage: (lang: 'fr' | 'en') => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
  brand: BrandObject;
  translations: TranslationsObject;
}
```

**Contrat:** Ne JAMAIS modifier les clés de traduction existantes

### AuthContext (src/components/GlobalAuth.jsx)

**API Publique:**
```typescript
interface AuthContextValue {
  user: UserObject | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  deviceTrusted: boolean;
  login: (email, password, rememberDevice?) => Promise<Result>;
  register: (name, email, password, phone?) => Promise<Result>;
  logout: () => Promise<void>;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  showLoginModal: boolean;
}
```

**Contrat:** Ne JAMAIS modifier les flux d'authentification

---

## 4. RÈGLES D'ISOLATION

### Zones Verrouillées (AUCUNE MODIFICATION)

| Zone | Raison |
|------|--------|
| `/core/bionic/**` | Moteur propriétaire BIONIC |
| `/core/engine/**` | Logique de calcul critique |
| `/core/security/**` | Garde-fous de sécurité |

### Zones Sensibles (Modifications avec Autorisation)

| Zone | Niveau |
|------|--------|
| `/core/contexts/**` | SENSIBLE |
| `/core/hooks/**` | SENSIBLE |
| `/core/components/**` | MODÉRÉ |

### Zones Autorisées

| Zone | Niveau |
|------|--------|
| `/core/utils/**` | AUTORISÉ |
| `/core/layouts/**` | AUTORISÉ |

---

## 5. PRINCIPES BIONIC V5

1. **Structure vs Logique** — On optimise la STRUCTURE, pas la LOGIQUE MÉTIER
2. **Couplage vs Capacités** — On réduit le COUPLAGE, pas les CAPACITÉS
3. **Segmentation** — On segmente, isole, clarifie sans changer le COMPORTEMENT

---

## 6. HISTORIQUE DES MODIFICATIONS

| Date | Version | Modification |
|------|---------|--------------|
| 2025-02-20 | 6.2.0 | BLOC 3: Documentation des frontières |
| 2025-02-20 | 6.1.0 | BLOC 3: Mémoïsation contexts |
| 2025-02-20 | 6.0.0 | BLOC 2: Code-splitting |

---

*Documentation générée dans le cadre du BLOC 3 — SÉQUENCE 4/4*
