# RAPPORT 4 : Isolation — Cartographie & Clarification

**Date:** 2025-02-20  
**Phase:** BLOC 3 — EXÉCUTION COMPLÈTE (ZONES SENSIBLES)  
**VERROUILLAGE MAÎTRE:** RENFORCÉ

---

## 1. STRUCTURE /core/

### Arborescence Documentée

```
/app/frontend/src/core/
├── bionic/                    # VERROUILLÉ - Moteur BIONIC
│   └── BionicEngine.jsx       # Algorithmes propriétaires
├── components/                # Composants fondamentaux
│   ├── SEOHead.jsx           # Meta tags SEO
│   └── BionicLogo.jsx        # Logo animé
├── contexts/                  # Contexts sensibles
│   └── PopupContext.jsx      # Gestion popups
├── hooks/                     # Hooks core
├── layouts/                   # Layouts principaux
├── utils/                     # Utilitaires
└── index.js                   # Point d'entrée
```

---

## 2. NIVEAUX D'ISOLATION

### Niveau 1 : VERROUILLÉ (Aucune Modification)

| Zone | Responsabilité | Risque |
|------|----------------|--------|
| `/core/bionic/**` | Moteur d'intelligence | CRITIQUE |
| `/core/engine/**` | Calculs métier | CRITIQUE |
| `/core/security/**` | Garde-fous | CRITIQUE |

### Niveau 2 : SENSIBLE (Autorisation Requise)

| Zone | Responsabilité | Risque |
|------|----------------|--------|
| `/contexts/LanguageContext.jsx` | Traductions | ÉLEVÉ |
| `/components/GlobalAuth.jsx` | Authentification | ÉLEVÉ |
| `/core/contexts/**` | Contexts système | MOYEN |
| `/core/hooks/**` | Hooks partagés | MOYEN |

### Niveau 3 : AUTORISÉ (Modifications Libres)

| Zone | Responsabilité | Risque |
|------|----------------|--------|
| `/components/**` | UI composants | FAIBLE |
| `/ui/**` | Composants visuels | FAIBLE |
| `/utils/**` | Utilitaires | FAIBLE |
| `/assets/**` | Assets statiques | FAIBLE |

---

## 3. INTERFACES DOCUMENTÉES

### LanguageContext

```typescript
// CONTRAT PUBLIC - NE PAS MODIFIER
interface LanguageContextAPI {
  language: 'fr' | 'en';
  setLanguage: (lang: 'fr' | 'en') => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
  brand: {
    full: string;
    short: string;
    company: string;
    tagline: string;
    slogan: string;
    logo: string;
  };
  translations: Record<string, string>;
}
```

### AuthContext

```typescript
// CONTRAT PUBLIC - NE PAS MODIFIER
interface AuthContextAPI {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  deviceTrusted: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<Result>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<Result>;
  logout: () => Promise<void>;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  showLoginModal: boolean;
}
```

---

## 4. RÈGLES D'ISOLATION

### Principes BIONIC V5

1. **Structure vs Logique**
   - ✅ On peut restructurer le code
   - ❌ On ne modifie pas les algorithmes

2. **Couplage vs Capacités**
   - ✅ On peut réduire les dépendances
   - ❌ On ne supprime pas de fonctionnalités

3. **Segmentation vs Fusion**
   - ✅ On peut diviser en modules
   - ❌ On ne fusionne pas de zones d'isolation

---

## 5. GARDE-FOUS PRÉSERVÉS

| Garde-fou | Localisation | Statut |
|-----------|--------------|--------|
| Token validation | GlobalAuth.jsx | ✅ INTACT |
| IP-based auto-login | GlobalAuth.jsx | ✅ INTACT |
| Language fallback | LanguageContext.jsx | ✅ INTACT |
| Error boundaries | Components | ✅ INTACT |

---

## 6. DOCUMENTATION CRÉÉE

| Document | Emplacement |
|----------|-------------|
| Architecture /core/ | `/app/docs/architecture/CORE_ISOLATION_DOCUMENTATION.md` |
| TerritoryMap constants | `/app/frontend/src/components/territory/constants.js` |
| MapHelpers | `/app/frontend/src/components/territory/MapHelpers.jsx` |

---

*Rapport généré conformément à la directive MAÎTRE — BLOC 3 ZONES SENSIBLES*
