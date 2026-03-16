"""
Script de génération du PDF de l'audit écologique BIONIC V3
Utilise reportlab pour produire un rapport PDF professionnel
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import KeepTogether


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
OUTPUT_PATH = os.path.join(STATIC_DIR, "BIONIC_AUDIT_ECOLOGIQUE_v1.pdf")

PRIMARY = HexColor("#1B5E20")
SECONDARY = HexColor("#2E7D32")
ACCENT = HexColor("#FF6F00")
DARK = HexColor("#212121")
LIGHT_BG = HexColor("#F5F5F5")
BORDER = HexColor("#BDBDBD")
WHITE = HexColor("#FFFFFF")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontSize=22, leading=28, textColor=PRIMARY,
        spaceAfter=6, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontSize=11, leading=14, textColor=DARK,
        spaceAfter=16, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=16, leading=20, textColor=PRIMARY,
        spaceBefore=20, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=13, leading=16, textColor=SECONDARY,
        spaceBefore=14, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=11, leading=14, textColor=DARK,
        spaceBefore=10, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'BodyJ', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=DARK,
        alignment=TA_JUSTIFY, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontSize=8, leading=10, fontName='Courier',
        textColor=DARK, backColor=LIGHT_BG,
        leftIndent=12, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'Warning', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=ACCENT,
        spaceBefore=6, spaceAfter=6, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=7, leading=9, textColor=BORDER,
        alignment=TA_CENTER
    ))
    return styles


def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(style)
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=6, spaceAfter=6)


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=0.7*inch, rightMargin=0.7*inch,
        topMargin=0.7*inch, bottomMargin=0.7*inch
    )
    s = build_styles()
    story = []

    # COVER
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("AUDIT ÉCOLOGIQUE BIONIC V3", s['DocTitle']))
    story.append(Paragraph("Rapport complet — Mode observation uniquement", s['DocSubtitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(hr())
    cover_info = [
        ["Date", "2026-03-16"],
        ["Auditeur", "Emergent AI (mode observation)"],
        ["Périmètre", "Tous les modèles/règles écologiques BIONIC"],
        ["Statut", "OBSERVATION UNIQUEMENT — AUCUNE MODIFICATION"],
        ["Version", "1.0"],
    ]
    story.append(make_table(["Champ", "Valeur"], cover_info, col_widths=[1.5*inch, 5*inch]))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "Ce document constitue une photo fidèle de l'état actuel de tous les modèles "
        "écologiques, règles de scoring, seuils et pipelines utilisés par l'application "
        "BIONIC. Aucune modification n'a été effectuée.",
        s['BodyJ']
    ))
    story.append(PageBreak())

    # TABLE DES MATIÈRES
    story.append(Paragraph("TABLE DES MATIÈRES", s['H1']))
    toc = [
        "1. Inventaire des Modules / Engines",
        "2. Schéma de dépendances (Pipeline)",
        "3. Thème: Zones d'alimentation",
        "4. Thème: Zones de repos",
        "5. Thème: Corridors / Déplacements",
        "6. Thème: Sécurité / Couvert",
        "7. Thème: Thermique / Refuge",
        "8. Thème: Hotspots",
        "9. Thème: Prédiction / Comportement",
        "10. Pipeline global",
        "11. Limites connues",
        "12. Propositions (non appliquées)",
    ]
    for item in toc:
        story.append(Paragraph(item, s['BodyJ']))
    story.append(PageBreak())

    # === SECTION 1: INVENTAIRE ===
    story.append(Paragraph("1. INVENTAIRE DES MODULES / ENGINES", s['H1']))

    # 1.1 Legacy
    story.append(Paragraph("1.1 — LEGACY ENGINE (GELÉ)", s['H2']))
    story.append(Paragraph("Statut: GELÉ (2026-03-10). Remplacé par bionic_engine_p0/.", s['Warning']))
    legacy_rows = [
        ["L1", "ThermalScore v1.0", "Confort thermique (T°, aspect, élévation, canopée, eau)"],
        ["L2", "WetnessScore v1.0", "Hydrologie (TWI, distance ruisseau, zone humide, précip, NDWI)"],
        ["L3", "FoodScore v1.0", "Nourriture (NDVI, type forêt, lisière, glands, brout)"],
        ["L4", "PressureScore v1.0", "Pression humaine (routes, bâtiments, chasse, bruit, lumière)"],
        ["L5", "AccessScore v1.0", "Accessibilité chasse (sentiers, routes, terrain, visibilité)"],
        ["L6", "CorridorScore v1.0", "Corridors (connectivité, goulots, traversées, continuité)"],
        ["L7", "GeoFormScore v1.0", "Géomorphologie (pente, aspect, courbure, rugosité, relief)"],
        ["L8", "CanopyScore v1.0", "Canopée (hauteur, fermeture, sous-bois, diversité, âge)"],
    ]
    story.append(make_table(["#", "Module", "Rôle"], legacy_rows, col_widths=[0.4*inch, 1.6*inch, 4.5*inch]))
    story.append(Spacer(1, 6))

    legacy_species = [
        ["Orignal", "thermal 15%, wetness 20%, food 25%, pressure 15%, corridor 10%, canopy 10%, geoform 5%"],
        ["Cerf", "food 30%, corridor 15%, pressure 15%, thermal 10%, wetness 10%, canopy 10%, geoform 10%"],
        ["Ours", "food 35%, pressure 20%, wetness 15%, thermal 10%, corridor 10%, canopy 5%, geoform 5%"],
        ["Caribou", "pressure 25%, food 20%, thermal 15%, wetness 15%, corridor 15%"],
        ["Loup", "pressure 30%, corridor 25%, food 15%, geoform 10%, wetness 10%"],
        ["Dindon", "food 35%, canopy 20%, corridor 10%, geoform 10%, thermal 10%"],
    ]
    story.append(Paragraph("Modèles par espèce (Legacy):", s['H3']))
    story.append(make_table(["Espèce", "Pondérations"], legacy_species, col_widths=[1*inch, 5.5*inch]))

    # 1.2 V2
    story.append(Paragraph("1.2 — ENGINES V2 (12 moteurs)", s['H2']))
    v2_rows = [
        ["behavior", "1.2", "Courbes d'activité horaires/saisonnières, détection rut"],
        ["keyzone_v2", "1.5", "Densité et diversité des zones clés"],
        ["food_deficit", "1.1", "Déficit alimentaire (NDVI saisonnier)"],
        ["wind_intelligence", "0.8", "Direction vent optimale approche"],
        ["terrain", "0.9", "Pentes, forêts, hydrologie"],
        ["human_pressure", "1.0", "Pression anthropique (routes, structures)"],
        ["corridor_continuity", "1.0", "Santé réseau corridors"],
        ["global_attractiveness", "1.3", "Score attractivité global (dépendant)"],
        ["action_plan", "0.5", "Plan d'action chasse (informatif)"],
        ["predictive_ai", "1.1", "Prédiction probabiliste (dépendant)"],
        ["bce_compliance", "0.3", "Validation conformité BCE-4X"],
        ["rendering", "0.2", "Performance rendu carte"],
    ]
    story.append(make_table(["Engine ID", "Poids", "Rôle"], v2_rows, col_widths=[1.3*inch, 0.6*inch, 4.6*inch]))

    # 1.3 V3
    story.append(Paragraph("1.3 — ENGINES V3 (12 moteurs)", s['H2']))
    v3_rows = [
        ["ecological_hierarchy", "1.1", "ecology", "Hiérarchie strates végétales"],
        ["interaction", "1.0", "ecology", "Effet lisière, paires complémentaires"],
        ["geopedology", "0.8", "terrain", "Pédologie (drainage, profondeur sol)"],
        ["connectivity", "1.2", "landscape", "Connectivité fonctionnelle"],
        ["temporal_dynamics", "1.0", "temporal", "Variations saisonnières + circadiennes"],
        ["hotspot", "1.3", "strategic", "Détection hotspots (dépendant)"],
        ["forest_structure_v2", "1.0", "ecology", "Structure forestière"],
        ["food_score_v2", "1.2", "ecology", "Scoring alimentaire avancé"],
        ["wetness_v2", "0.9", "hydrology", "Humidité avancée"],
        ["geoform_v2", "0.8", "terrain", "Géomorphologie avancée"],
        ["behavior_v2", "1.2", "behavioral", "Modèle circadien 24h par espèce"],
        ["attractiveness_v2", "1.5", "synthesis", "Score global v2 (dépendant)"],
    ]
    story.append(make_table(["Engine ID", "Poids", "Cat.", "Rôle"], v3_rows, col_widths=[1.3*inch, 0.5*inch, 0.7*inch, 4*inch]))

    # 1.4 IA
    story.append(Paragraph("1.4 — ENGINES IA (3 moteurs)", s['H2']))
    ia_rows = [
        ["predictive_models", "1.0", "Prédictions 24h/72h/7j avec décroissance confiance"],
        ["dynamic_scoring", "1.0", "Ajustements temps réel (vent, T°, heure)"],
        ["temporal_analysis", "0.9", "Trends, patterns, forecast horaire"],
    ]
    story.append(make_table(["Engine ID", "Poids", "Rôle"], ia_rows, col_widths=[1.3*inch, 0.6*inch, 4.6*inch]))

    # 1.5 Fauniques V3
    story.append(Paragraph("1.5 — MODÈLES FAUNIQUES V3 (3 espèces)", s['H2']))
    fauna_rows = [
        ["Orignal", "behavior_v2: 1.4, food_score_v2: 1.3, wetness_v2: 1.2, connectivity: 1.2, ecological_hierarchy: 1.1"],
        ["Cerf", "behavior_v2: 1.3, forest_structure_v2: 1.3, food_score_v2: 1.2, interaction: 1.2, geoform_v2: 1.1"],
        ["Ours", "food_score_v2: 1.5, behavior_v2: 1.2, forest_structure_v2: 1.2, temporal_dynamics: 1.1, ecological_hierarchy: 1.1"],
    ]
    story.append(make_table(["Espèce", "Pondérations clés (top 5)"], fauna_rows, col_widths=[1*inch, 5.5*inch]))

    # 1.6 Corridor V9
    story.append(Paragraph("1.6 — 9 MOTEURS CORRIDOR V9", s['H2']))
    c9_rows = [
        ["nutrition", "0.12", "NDVI + fourrage saisonnier + minéraux + besoins espèce"],
        ["daily_routine", "0.10", "Rythmes circadiens, lever/coucher soleil Québec"],
        ["weather", "0.10", "OWM live + cache 60min + fallback algorithmique"],
        ["disturbance", "0.12", "Pression humaine 5 facteurs (score INVERSÉ)"],
        ["movement", "0.15", "DEM algorithmique + A* + énergie + relief Québec"],
        ["phenology", "0.08", "Cycles végétatifs 12 mois, NDVI, couvert"],
        ["typology", "0.08", "5 profils comportementaux x saison x espèce"],
        ["learning", "0.05", "Calibration observations terrain"],
        ["habitat_enhancement", "0.05", "Sol, minéraux, recommandations habitat"],
    ]
    story.append(make_table(["Engine", "Poids", "Rôle"], c9_rows, col_widths=[1.3*inch, 0.6*inch, 4.6*inch]))
    story.append(Paragraph("Total poids V9: 0.85 (normalisé a 1.0 dans le composite)", s['CodeBlock']))

    # 1.7 Hotspot + Support
    story.append(Paragraph("1.7 — HOTSPOT ENGINE + MODULES SUPPORT", s['H2']))
    support_rows = [
        ["Hotspot Extraction", "hotspots/hotspot_engine.py", "Grille 50m, scoring, DBSCAN, polygone"],
        ["Territory Data", "hotspots/territory_data_provider.py", "Enrichissement territorial (MOCKÉ)"],
        ["Pipeline V7", "services/pipeline_v7.py", "Orchestrateur zones, corridors, scoring"],
        ["Corridor Service", "services/corridor_service.py", "Génération corridors A*"],
        ["Corridor 10x", "services/corridor_10x.py", "Pathfinding optimisé"],
        ["Exclusion V7", "services/exclusion_engine_v7.py", "Zones exclusion (eau, urbain)"],
        ["Wildlife Behavior", "wildlife_behavior_engine/", "Comportement faune (module séparé)"],
    ]
    story.append(make_table(["Module", "Fichier", "Rôle"], support_rows, col_widths=[1.2*inch, 2.3*inch, 3*inch]))

    story.append(PageBreak())

    # === SECTION 3: ALIMENTATION ===
    story.append(Paragraph("3. THÈME: ZONES D'ALIMENTATION", s['H1']))

    story.append(Paragraph("Couches utilisées:", s['H3']))
    alim_couches = [
        ["NDVI", "NASA MODIS/Seasonal ou estimation", "~250m"],
        ["Zones alimentation", "OSM Overpass", "Variable"],
        ["Hydrographie", "OSM/Gouv QC", "Variable"],
        ["Peuplements forestiers", "WMS écoforestier QC", "1:20000"],
    ]
    story.append(make_table(["Couche", "Source", "Résolution"], alim_couches, col_widths=[1.5*inch, 3*inch, 2*inch]))

    story.append(Paragraph("Préférences alimentaires par espèce:", s['H3']))
    food_pref = [
        ["Orignal", "30%", "40%", "20%", "10%", "-", "-"],
        ["Cerf", "-", "35%", "-", "30%", "-", "-"],
        ["Ours", "-", "-", "-", "25%", "30%", "20%"],
    ]
    story.append(make_table(["Espèce", "Aquatique", "Brout", "Écorce", "Herbes", "Baies", "Insectes"], food_pref,
                            col_widths=[0.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch]))

    story.append(Paragraph("Règles de scoring:", s['H3']))
    story.append(Paragraph("FoodScore v2: qualité x 0.4 + disponibilité x 0.3 + accessibilité x 0.3 + bonus_diversité", s['CodeBlock']))
    story.append(Paragraph("Food Deficit: food_availability = base_ndvi x 100 + feeding_zones x 15; deficit = max(0, 70 - food_availability)", s['CodeBlock']))
    story.append(Paragraph("Nutrition V9: avg_forage x 0.40 + ndvi x 0.25 + browse x 0.20 + caloric x 0.15 + salt + urgency", s['CodeBlock']))

    story.append(Paragraph("Qualité saisonnière:", s['H3']))
    season_q = [
        ["Printemps", "0.60", "0.7", "0"],
        ["Été", "1.00", "0.9", "0"],
        ["Automne", "0.65", "1.0", "5 x caloric_need"],
        ["Hiver", "0.15", "0.3", "10 x caloric_need"],
    ]
    story.append(make_table(["Saison", "NDVI mult.", "Qualité fourrage", "Urgence calorique"], season_q,
                            col_widths=[1.2*inch, 1.2*inch, 1.5*inch, 2.6*inch]))

    # === SECTION 4: REPOS ===
    story.append(Paragraph("4. THÈME: ZONES DE REPOS", s['H1']))
    story.append(Paragraph("Pourcentage repos par espèce: Orignal 60%, Cerf 50%, Ours 40%", s['BodyJ']))
    story.append(Paragraph("Pics repos Orignal: 0h-4h (10-15%), 10h-14h (15-25%)", s['CodeBlock']))
    story.append(Paragraph("Pics repos Cerf: 0h-4h (5-10%), 10h-14h (10-20%)", s['CodeBlock']))
    story.append(Paragraph("Ours: repos nocturne fort (5-10%), jour actif (55-90%)", s['CodeBlock']))
    story.append(Paragraph("Interaction Engine: Paire (alimentation, repos) = +18 pts edge effect", s['CodeBlock']))

    # === SECTION 5: CORRIDORS ===
    story.append(Paragraph("5. THÈME: CORRIDORS / DÉPLACEMENTS", s['H1']))

    story.append(Paragraph("Classification 5 niveaux:", s['H3']))
    corr_class = [
        ["gris", "0-30", "Potentiel", "#9E9E9E", "1.5px"],
        ["jaune", "31-50", "Opportuniste", "#FFC107", "2.0px"],
        ["orange", "51-70", "Fonctionnel", "#FF9800", "2.8px"],
        ["rouge", "71-85", "Primaire", "#F44336", "3.5px"],
        ["rouge_rayé", "86-100", "Critique", "#B71C1C", "4.5px"],
    ]
    story.append(make_table(["Niveau", "Score", "Label", "Couleur", "Largeur"], corr_class,
                            col_widths=[1*inch, 0.8*inch, 1.2*inch, 1.5*inch, 1*inch]))

    story.append(Paragraph("Distance optimale par espèce:", s['H3']))
    corr_dist = [
        ["Orignal", "200m", "2000m", "800m"],
        ["Cerf", "100m", "1500m", "500m"],
        ["Ours", "300m", "3000m", "1200m"],
    ]
    story.append(make_table(["Espèce", "Min", "Max", "Idéal"], corr_dist, col_widths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch]))

    story.append(Paragraph("Coût énergétique par pente:", s['H3']))
    energy_rows = [
        ["0-3 deg", "1.0"], ["3-8 deg", "1.3"], ["8-15 deg", "1.8"],
        ["15-25 deg", "2.5"], [">25 deg", "4.0"],
    ]
    story.append(make_table(["Pente", "Coût"], energy_rows, col_widths=[2*inch, 2*inch]))

    story.append(Paragraph("Post-traitement: Densification 30m, Lissage Chaikin 2 it., Clipping 2km2, Continuité max gap 150m", s['CodeBlock']))

    # === SECTION 6: SÉCURITÉ ===
    story.append(Paragraph("6. THÈME: SÉCURITÉ / COUVERT", s['H1']))
    story.append(Paragraph("Disturbance Engine (score INVERSÉ):", s['H3']))
    story.append(Paragraph(
        "score = 100 - (zone x 0.30 + road x 0.25 + lat x 0.15 + lng x 0.05 + noise x 0.15 + hunting x 0.10) x time_factor",
        s['CodeBlock']
    ))
    sec_species = [
        ["Orignal", "0.8", "0.7", "0.9", "300m"],
        ["Cerf", "0.6", "0.8", "0.7", "150m"],
        ["Ours", "0.5", "0.6", "0.8", "200m"],
    ]
    story.append(make_table(["Espèce", "Sens. route", "Sens. bruit", "Sens. humain", "Dist. fuite"],
                            sec_species, col_widths=[1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch]))
    story.append(Paragraph("Pression chasse saisonnière: Printemps 0.3, Été 0.1, Automne 1.0, Hiver 0.4", s['CodeBlock']))

    # === SECTION 7: THERMIQUE ===
    story.append(Paragraph("7. THÈME: THERMIQUE / REFUGE", s['H1']))
    therm_rows = [
        ["Orignal", "-10C", "15C", "25C", "-35C"],
        ["Cerf", "-5C", "20C", "30C", "-25C"],
        ["Ours", "5C", "25C", "35C", "-10C"],
    ]
    story.append(make_table(["Espèce", "Optimal min", "Optimal max", "Stress chaleur", "Stress froid"],
                            therm_rows, col_widths=[1*inch, 1.2*inch, 1.2*inch, 1.3*inch, 1.3*inch]))
    story.append(Paragraph("Vent: calm +10, light +5, moderate -5, strong -20, storm -40", s['CodeBlock']))
    story.append(Paragraph("Précip: rain_light -3, rain_mod -8, rain_heavy -15, snow_light -5, snow_mod -12, snow_heavy -25", s['CodeBlock']))
    story.append(Paragraph("Pression: <1000hPa -10, 1000-1008 -5, 1020-1025 +5, >1025 +8", s['CodeBlock']))
    story.append(Paragraph("Phases lunaires: nouvelle -10, pleine +15, descendante +5", s['CodeBlock']))
    story.append(Paragraph("Cache OWM: 60 minutes (non-négociable). Certitude: live 0.90, fallback 0.60", s['CodeBlock']))

    # === SECTION 8: HOTSPOTS ===
    story.append(PageBreak())
    story.append(Paragraph("8. THÈME: HOTSPOTS", s['H1']))
    story.append(Paragraph("Pondérations officielles:", s['H3']))
    hot_weights = [
        ["corridors_v9", "20%"], ["food_score_v2", "15%"], ["forest_structure_v2", "15%"],
        ["wetness_score_v2", "10%"], ["geoform_score_v2", "10%"], ["temporal_dynamics", "10%"],
        ["behavior_v2", "10%"], ["disturbance", "5%"], ["global_attractiveness_v2", "5%"],
    ]
    story.append(make_table(["Engine", "Poids"], hot_weights, col_widths=[2.5*inch, 1*inch]))
    story.append(Paragraph("Classification: MAJEUR >= 80, FORT >= 60, MODÉRÉ >= 40, FAIBLE < 40", s['CodeBlock']))
    story.append(Paragraph("Filtres: score min 60, corridor nearby, accessibilité min 40, max 25/région", s['CodeBlock']))
    story.append(Paragraph("DBSCAN: eps = spacing x 2.5, min_samples = 5", s['CodeBlock']))

    # === SECTION 9: PRÉDICTION ===
    story.append(Paragraph("9. THÈME: PRÉDICTION / COMPORTEMENT", s['H1']))
    pred_rows = [
        ["24h", "avg x 0.4 + behavior x 0.3 + temporal x 0.3", "85%", "1.0"],
        ["72h", "avg x 0.5 + food x 0.25 + behavior x 0.25", "70%", "0.85"],
        ["7j", "avg x 0.6 + food x 0.2 + temporal x 0.2", "55%", "0.70"],
    ]
    story.append(make_table(["Horizon", "Formule", "Confiance", "Decay"], pred_rows,
                            col_widths=[0.6*inch, 3.2*inch, 1*inch, 0.8*inch]))

    story.append(Paragraph("5 Profils comportementaux:", s['H3']))
    profils = [
        ["Conservateur", "0.2", "500m", "0.8", "0.3"],
        ["Explorateur", "0.7", "2000m", "0.4", "0.5"],
        ["Nocturne", "0.5", "1200m", "0.6", "0.9"],
        ["Opportuniste", "0.6", "1500m", "0.5", "0.6"],
        ["Territorial", "0.3", "800m", "0.7", "0.4"],
    ]
    story.append(make_table(["Profil", "Risque", "Range", "Couvert", "Nuit"], profils,
                            col_widths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch]))

    # === SECTION 11: LIMITES ===
    story.append(PageBreak())
    story.append(Paragraph("11. LIMITES CONNUES", s['H1']))

    story.append(Paragraph("Limites données:", s['H2']))
    lim_data = [
        ["LIM-DATA-01", "NDVI estimé (pas satellite réel)", "Précision ~60-70%", "Connu, approuvé"],
        ["LIM-DATA-02", "DEM algorithmique (pas SRTM/LiDAR)", "Précision ~100-200m", "Connu"],
        ["LIM-DATA-03", "Pression humaine algorithmique", "hash(lat,lng)", "Connu"],
        ["LIM-DATA-04", "Données territoriales MOCKÉES", "Générées aléatoirement", "Approuvé"],
        ["LIM-DATA-05", "Pas de données récolte MFFP", "Absent", "Absent"],
    ]
    story.append(make_table(["ID", "Description", "Impact", "Statut"], lim_data,
                            col_widths=[1*inch, 2.3*inch, 1.7*inch, 1.2*inch]))

    story.append(Paragraph("Limites modèles:", s['H2']))
    lim_mod = [
        ["LIM-MOD-01", "Scores hotspots hash-based", "Pseudo-aléatoire déterministe"],
        ["LIM-MOD-02", "Pas de vrai ML dans Learning Engine", "Score = 50 + bonus linéaire"],
        ["LIM-MOD-03", "Profils comportementaux statiques", "Tables fixes, pas calibrés"],
        ["LIM-MOD-04", "Confort thermique simplifié", "Zones rectangulaires"],
        ["LIM-MOD-05", "Aucun modèle prédation", "Interactions non modélisées"],
    ]
    story.append(make_table(["ID", "Description", "Impact"], lim_mod,
                            col_widths=[1*inch, 2.5*inch, 2.8*inch]))

    # === SECTION 12: PROPOSITIONS ===
    story.append(Paragraph("12. PROPOSITIONS (NON APPLIQUÉES)", s['H1']))
    story.append(Paragraph(
        "ATTENTION: Ces propositions sont strictement informatives et ne sont PAS appliquées "
        "sans commande explicite de Steeve.",
        s['Warning']
    ))
    propositions = [
        ["P-ALIM-01", "Remplacer NDVI estimé par intégration Sentinel-2 réel (10m)"],
        ["P-TERR-01", "Intégrer SRTM/ALOS 30m au lieu du DEM algorithmique"],
        ["P-PRESS-01", "Utiliser densité routière OSM réelle au lieu de hash(lat,lng)"],
        ["P-ML-01", "Implémenter vrai modèle ML (gradient boosting sur observations)"],
        ["P-PRED-01", "Ajouter modèle prédateur-proie (loup-cerf/orignal)"],
        ["P-THERM-01", "Remplacer zones thermiques rectangulaires par gaussiennes"],
        ["P-HOT-01", "Remplacer scoring hash-based par scoring écologique réel"],
    ]
    story.append(make_table(["ID", "Description"], propositions, col_widths=[1*inch, 5.5*inch]))

    # FOOTER
    story.append(Spacer(1, 0.5*inch))
    story.append(hr())
    story.append(Paragraph(
        "Fin du rapport d'audit. Aucune modification effectuée. Photo fidèle de l'état actuel.",
        s['BodyJ']
    ))
    story.append(Paragraph(
        "AUDIT ÉCOLOGIQUE BIONIC V3 — Version 1.0 — 2026-03-16 — Emergent AI",
        s['Footer']
    ))

    doc.build(story)
    print(f"PDF généré: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    build_pdf()
