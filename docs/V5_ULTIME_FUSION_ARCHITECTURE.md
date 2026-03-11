# HUNTIQ V5-ULTIME-FUSION - Architecture Documentée

## Vue d'ensemble

V5-ULTIME-FUSION est la version canonique de HUNTIQ, fusionnant les meilleures fonctionnalités de toutes les versions précédentes dans une architecture 100% modulaire.

## Sources de la Fusion

| Source | Branche | Commit | Éléments importés |
|--------|---------|--------|-------------------|
| HUNTIQ-V4 | conflict_120226_1312 | 1072e0f | Ossature modulaire (45+ modules) |
| HUNTIQ-V3 | conflict_050226_1749 | 200cca5 | Frontpage analytique (15 modules) |
| HUNTIQ-V2 | conflict_030226_0855 | 886bc5d | Backup cloud, Formations |
| HUNTIQ-BASE | main | cc8ab6f | Social, Rental, Admin avancé, Partners |

## Architecture Backend

### Structure des Modules

```
/app/backend/modules/
├── Phase 2 - Core Engines (7 modules)
│   ├── nutrition_engine/
│   ├── scoring_engine/
│   ├── ai_engine/
│   ├── weather_engine/
│   ├── geospatial_engine/
│   ├── wms_engine/
│   └── strategy_engine/
│
├── Phase 3 - Business Engines (8 modules)
│   ├── user_engine/
│   ├── admin_engine/
│   ├── notification_engine/
│   ├── referral_engine/
│   ├── territory_engine/
│   ├── tracking_engine/
│   ├── marketplace_engine/
│   └── plugins_engine/
│
├── Phase 4 - Master Plan Engines (10 modules)
│   ├── recommendation_engine/
│   ├── collaborative_engine/
│   ├── ecoforestry_engine/
│   ├── engine_3d/
│   ├── wildlife_behavior_engine/
│   ├── weather_fauna_simulation_engine/
│   ├── adaptive_strategy_engine/
│   ├── advanced_geospatial_engine/
│   ├── progression_engine/
│   └── networking_engine/
│
├── Phase 5 - Data Layers (5 modules)
│   └── data_layers/
│       ├── ecoforestry_layers.py
│       ├── behavioral_layers.py
│       ├── simulation_layers.py
│       ├── layers_3d.py
│       └── advanced_geospatial_layers.py
│
├── Phase 6-8 - Special Modules
│   ├── live_heading_engine/
│   ├── legal_time_engine/
│   ├── predictive_engine/
│   └── camera_engine/
│
├── V5-V2 - Modules de V2 (2 modules)
│   ├── backup_cloud_engine/  ← Cloud backup (Atlas, GCS, ZIP)
│   └── formations_engine/    ← FédéCP & BIONIC Academy
│
└── V5-BASE - Modules de HUNTIQ-BASE (5 modules)
    ├── social_engine/        ← Networking, groupes, chat
    ├── rental_engine/        ← Location de terres
    ├── communication_engine/ ← Notifications, emails
    ├── admin_advanced_engine/← Brand, features, maintenance
    └── partner_engine/       ← Partenaires, offres, événements
```

### Total: 52+ modules backend

## Architecture Frontend

### Structure des Composants

```
/app/frontend/src/
├── components/
│   ├── frontpage/          ← V3 (15 modules analytiques)
│   │   ├── HeroSection.jsx
│   │   ├── ProductCarousel.jsx
│   │   ├── MapModule.jsx
│   │   ├── WeatherModule.jsx
│   │   ├── BentoGridSection.jsx
│   │   ├── MarketplaceSection.jsx
│   │   ├── MediaFormationsSection.jsx
│   │   ├── LiveStatsSection.jsx
│   │   ├── PartnersSection.jsx
│   │   ├── BlogSection.jsx
│   │   ├── CommunitySection.jsx
│   │   ├── MobileAppSection.jsx
│   │   ├── NewsletterSection.jsx
│   │   ├── FooterSection.jsx
│   │   └── StatsEngine.jsx
│   │
│   ├── admin/              ← BASE (Admin avancé)
│   │   ├── BackupManager.jsx
│   │   ├── BrandIdentityAdmin.jsx
│   │   ├── EmailAdmin.jsx
│   │   ├── MaintenanceControl.jsx
│   │   └── SiteAccessControl.jsx
│   │
│   ├── partner/            ← BASE (Partenaires)
│   │   ├── PartnerOffers.jsx
│   │   └── PartnerCalendar.jsx
│   │
│   ├── social/             ← BASE (Social)
│   │   └── NotificationCenter.jsx
│   │
│   ├── territory/          ← V4 (Territoire)
│   │   └── ... (composants territoire)
│   │
│   └── ui/                 ← V4 (shadcn/ui)
│       └── ... (composants UI)
│
├── modules/
│   ├── formations/         ← V2 (Formations)
│   │   ├── FormationsPage.jsx
│   │   └── index.js
│   │
│   └── ... (44 modules V4)
│
├── pages/
│   ├── BionicHomePage.jsx  ← V3 (Frontpage principal)
│   └── ... (autres pages V4)
│
└── App.js                  ← V4 (Orchestrateur principal)
```

## APIs Principales

### Endpoints V5-ULTIME-FUSION

| Préfixe | Module | Source |
|---------|--------|--------|
| /api/backup-cloud/* | backup_cloud_engine | V2 |
| /api/formations/* | formations_engine | V2 |
| /api/social/* | social_engine | BASE |
| /api/rental/* | rental_engine | BASE |
| /api/communication/* | communication_engine | BASE |
| /api/admin-advanced/* | admin_advanced_engine | BASE |
| /api/partners/* | partner_engine | BASE |

### Endpoints V4 (conservés)

- /api/auth/* - Authentification
- /api/users/* - Gestion utilisateurs
- /api/territories/* - Territoires
- /api/products/* - Produits
- /api/orders/* - Commandes
- /api/weather/* - Météo
- /api/wms/* - Couches WMS
- /api/ecoforestry/* - Écoforesterie
- ... et 40+ autres endpoints

## Fonctionnalités Clés

### Depuis V4 (Ossature)
- ✅ Architecture modulaire pure v2.1
- ✅ Header avec onglet "Carte"
- ✅ BionicMapSelector (7 cartes premium)
- ✅ Écoforestière complète
- ✅ Couches premium relookées
- ✅ 45 modules backend

### Depuis V3 (Frontpage)
- ✅ BionicHomePage analytique
- ✅ 15 modules frontpage
- ✅ Images fauniques (orignal, cerf, ours, dindon)
- ✅ Design analytique complet

### Depuis V2 (Moteurs uniques)
- ✅ backup_cloud_engine (Atlas, GCS, ZIP, email)
- ✅ formations_engine (FédéCP, BIONIC Academy)

### Depuis HUNTIQ-BASE (Modules sociaux/admin)
- ✅ social_engine (networking, groupes, chat, parrainage)
- ✅ rental_engine (location de terres)
- ✅ communication_engine (notifications, emails)
- ✅ admin_advanced_engine (brand, features, maintenance)
- ✅ partner_engine (partenaires, offres, calendrier)

## Méthode de Fusion

La fusion a été réalisée selon la méthode LEGO:
1. Import modulaire fichier par fichier
2. Conversion des modules monolithiques en engines
3. Aucun merge Git direct
4. Aucune modification des dépôts sources
5. Architecture 100% alignée avec les phases V4

## Stack Technique

- **Backend**: FastAPI + Python 3.11
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Database**: MongoDB
- **Maps**: Leaflet + WMS Quebec
- **Auth**: JWT + Google OAuth

---
Version: V5-ULTIME-FUSION
Date: Février 2026
