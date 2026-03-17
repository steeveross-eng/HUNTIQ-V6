"""
Génération PDF — PLAN DE MATCH STEEVE-MAX v1
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
OUTPUT_PATH = os.path.join(STATIC_DIR, "PLAN_DE_MATCH_STEEVE_MAX_v1.pdf")

P = HexColor("#1B5E20")
S = HexColor("#2E7D32")
A = HexColor("#FF6F00")
D = HexColor("#212121")
LB = HexColor("#F5F5F5")
BD = HexColor("#BDBDBD")
W = HexColor("#FFFFFF")

def build_styles():
    st = getSampleStyleSheet()
    st.add(ParagraphStyle('DT', parent=st['Title'], fontSize=20, leading=26, textColor=P, spaceAfter=6, alignment=TA_CENTER))
    st.add(ParagraphStyle('DS', parent=st['Normal'], fontSize=10, leading=13, textColor=D, spaceAfter=14, alignment=TA_CENTER))
    st.add(ParagraphStyle('H1s', parent=st['Heading1'], fontSize=15, leading=19, textColor=P, spaceBefore=18, spaceAfter=8))
    st.add(ParagraphStyle('H2s', parent=st['Heading2'], fontSize=12, leading=15, textColor=S, spaceBefore=12, spaceAfter=6))
    st.add(ParagraphStyle('H3s', parent=st['Heading3'], fontSize=10, leading=13, textColor=D, spaceBefore=8, spaceAfter=4))
    st.add(ParagraphStyle('BJ', parent=st['Normal'], fontSize=8.5, leading=11, textColor=D, alignment=TA_JUSTIFY, spaceAfter=3))
    st.add(ParagraphStyle('CB', parent=st['Normal'], fontSize=7.5, leading=10, fontName='Courier', textColor=D, backColor=LB, leftIndent=10, spaceAfter=4))
    st.add(ParagraphStyle('WN', parent=st['Normal'], fontSize=8.5, leading=11, textColor=A, spaceBefore=4, spaceAfter=4, fontName='Helvetica-Bold'))
    return st

def mt(headers, rows, cw=None):
    data = [headers] + rows
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), P), ('TEXTCOLOR', (0, 0), (-1, 0), W),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 7.5),
        ('FONTSIZE', (0, 1), (-1, -1), 7), ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.3, BD),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [W, LB]),
        ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ])
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(style)
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BD, spaceBefore=4, spaceAfter=4)

def build_pdf():
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
    s = build_styles()
    st = []

    # COVER
    st.append(Spacer(1, 1.2*inch))
    st.append(Paragraph("PLAN DE MATCH STEEVE-MAX v1", s['DT']))
    st.append(Paragraph("Document normatif officiel — BIONIC V3", s['DS']))
    st.append(hr())
    st.append(mt(["Champ", "Valeur"], [
        ["Date", "2026-03-16"], ["Statut", "NORMATIF"], ["Conformite", "BCE-4X + Steeve-MAX"],
        ["Perimeter", "9 definitions ecologiques + normes + roadmap moteurs"]
    ], cw=[1.5*inch, 5*inch]))
    st.append(PageBreak())

    # 1. DEFINITIONS
    st.append(Paragraph("1. DEFINITIONS ECOLOGIQUES 3x PLUS PRECISES", s['H1s']))

    for title, desc, variables in [
        ("1.1 — Habitat optimal (HABITAT-V1)",
         "Zone combinant alimentation, repos, securite, accessibilite, pression faible et connectivite pour occupation reguliere, reproduction, survie hivernale et presence des dominants.",
         [["Score alimentation", "ALIMENTATION-V1", "10m"], ["Score repos", "REPOS-V1", "10m"],
          ["Corridors", "CORRIDORS-V10", "10m"], ["Hydrographie", "Couches fines", "10m"],
          ["Pente + Orientation", "LiDAR/DEM", "10m"], ["Type de foret", "Ecoforestier", "10m"],
          ["Pression humaine", "OSM + algo.", "10m"]]),
        ("1.2 — Zones de rut (RUT-V1)",
         "Pre-rut: alimentation riche + repos securises. Rut: convergence femelles + noyaux marquage + corridors dominants. Post-rut: remise en energie + repos maximal.",
         [["Pre-rut", "Sept-Oct", "Alimentation + repos"], ["Rut", "Oct-Nov", "Convergence + marquage"],
          ["Post-rut", "Nov-Dec", "Energie + repos"]]),
        ("1.3 — Corridors fauniques (CORRIDORS-V10)",
         "Axes de deplacement reellement utilises, reliant repos, alimentation, rut et eau, en minimisant effort, risque et pression.",
         [["Pente", "Cout energetique", "Par segment"], ["Lisieres", "Axes deplacement", "Preferes"],
          ["Ravines/Vallees", "Corridors naturels", "Proteges"], ["Pression humaine", "Evitement", "Routes, batiments"]]),
    ]:
        st.append(Paragraph(title, s['H2s']))
        st.append(Paragraph(desc, s['BJ']))
        st.append(mt(["Variable", "Source", "Detail"], variables, cw=[1.5*inch, 2*inch, 3*inch]))
        st.append(Spacer(1, 4))

    # Hydro, Pentes, Orientation, Ensoleillement
    for title, desc in [
        ("1.4 — Hydrographie", "Ressource (eau, mineraux, fraicheur), barriere ou corridor selon l'espece."),
        ("1.5 — Pentes", "Effort energetique module par espece. Cerf/Dindon: evitent pentes fortes. Orignal/Ours/Wapiti: tolerent."),
        ("1.6 — Orientation", "Versants sud: alimentation + rut. Versants nord: repos + orignal + ours."),
        ("1.7 — Ensoleillement", "Hiver: recherche soleil. Ete: recherche ombre. Automne/Printemps: mixte."),
    ]:
        st.append(Paragraph(title, s['H2s']))
        st.append(Paragraph(desc, s['BJ']))

    st.append(Paragraph("1.8 — Affuts potentiels (AFFUTS-V1)", s['H2s']))
    st.append(Paragraph("Positions ou probabilite de passage est maximale et detection minimale (vent, bruit, visibilite). Bases sur habitat optimal, corridors, rut, hydro, vent dominant.", s['BJ']))

    st.append(Paragraph("1.9 — Trajets de chasse (TRAJETS-V1)", s['H2s']))
    st.append(Paragraph("Sequences continues alignees sur corridors, affuts, zones d'interet. Objectif: minimiser derangement, maximiser opportunites, preserver coherence du territoire.", s['BJ']))

    st.append(PageBreak())

    # 2. BCE-4X
    st.append(Paragraph("2. NORMES BCE-4X — FIREWALL SCIENTIFIQUE", s['H1s']))
    bce_rows = [
        ["GEOM-001", "Score dans [0, 100]", "100% cellules"],
        ["GEOM-002", "Classification valide", "100% cellules"],
        ["GEOM-004", "Aucun pixel hors carre 2km2", "0 violations"],
        ["ECO-001", "Espece -> Profil -> Ponderations coherentes", "Obligatoire"],
        ["ECO-002", "Saisonnalite appliquee (4 saisons + rut)", "Obligatoire"],
        ["TOPO-001", "Pente calculee par cellule 10m", "Obligatoire"],
        ["BEHAV-001", "Profils dominants integres (rut)", "Obligatoire"],
        ["REG-001", "Aucune modification engines existants", "Non-negociable"],
        ["REG-002", "Seuil dynamique inchange", "Non-negociable"],
        ["INTER-001", "Aucune contradiction entre scores moteurs", "Obligatoire"],
    ]
    st.append(mt(["Code", "Regle", "Seuil"], bce_rows, cw=[1*inch, 3.5*inch, 2*inch]))

    # 3. Steeve-MAX
    st.append(Paragraph("3. NORMES STEEVE-MAX — EXECUTION ET QUALITE", s['H1s']))
    smax = [
        ["Documentation", "Fiche technique JSON + metadonnees pour chaque moteur"],
        ["Tracabilite", "Score -> sous-scores -> couches d'entree"],
        ["Coherence visuelle", "Palette bleu -> vert -> jaune -> rouge + badges uniformes"],
        ["Multi-especes", "5 especes, ponderations specifiques documentees"],
        ["Saisonnalite", "4 saisons + 3 phases rut + multiplicateurs tracables"],
        ["Operationnel", "Corridors continus, affuts scientifiques, trajets optimises"],
        ["Execution stricte", "Zero interpretation libre, directives a la lettre"],
    ]
    st.append(mt(["Norme", "Exigence"], smax, cw=[1.5*inch, 5*inch]))

    st.append(PageBreak())

    # 4. ROADMAP
    st.append(Paragraph("4. ROADMAP DES MOTEURS FUTURS", s['H1s']))
    roadmap = [
        ["1", "ALIMENTATION-V1", "LIVRE", "Couches fines", "P0"],
        ["2", "REPOS-V1", "LIVRE", "Couches fines", "P0"],
        ["3", "CORRIDORS-V10", "A CONSTRUIRE", "ALIM + REPOS", "P0"],
        ["4", "HABITAT-V1", "A CONSTRUIRE", "ALIM + REPOS + CORR", "P0"],
        ["5", "RUT-V1", "A CONSTRUIRE", "HABITAT + CORR", "P1"],
        ["6", "AFFUTS-V1", "A CONSTRUIRE", "HAB + CORR + RUT", "P1"],
        ["7", "TRAJETS-V1", "A CONSTRUIRE", "Tous les moteurs", "P2"],
    ]
    st.append(mt(["#", "Moteur", "Statut", "Dependances", "Priorite"], roadmap,
                 cw=[0.3*inch, 1.3*inch, 1.1*inch, 2.3*inch, 0.6*inch]))

    # 5. PIPELINE
    st.append(Paragraph("5. SCHEMA DU PIPELINE INTEGRE", s['H1s']))
    pipeline_text = """COUCHES FINES (LiDAR, essences, hydro, pente)
    |
    +--> ALIMENTATION-V1 --> Score 0-100
    |
    +--> REPOS-V1 ----------> Score 0-100
    |
    +--> CORRIDORS-V10 -----> Score 0-100
    |
    +--> HABITAT-V1 --------> Score 0-100
    |
    +--> RUT-V1 ------------> Score 0-100 (par phase)
    |
    +--> AFFUTS-V1 ---------> Score 0-100
    |
    +--> TRAJETS-V1 --------> Sequence optimisee
    |
    v
SCORE CONSOLIDE --> HEATMAP OFFICIEL
    |
BCE-4X + STEEVE-MAX VALIDATION
    |
LIVRAISON"""
    st.append(Preformatted(pipeline_text, s['CB']))

    # 6. CRITERES LIVRAISON
    st.append(Paragraph("6. CRITERES DE LIVRAISON PAR MOTEUR", s['H1s']))
    crit = [
        ["Technique", "Module independant, grille 10m, 5 especes, API REST, BCE-4X PASS"],
        ["Scientifique", "Variables documentees, ponderations justifiees, saisonnalite"],
        ["Qualite", "Documentation JSON, tracabilite, tests PASS, zero regression"],
        ["Visuel", "Palette conforme, badge score + label + anneau, transparence"],
    ]
    st.append(mt(["Categorie", "Criteres"], crit, cw=[1.2*inch, 5.3*inch]))

    st.append(Spacer(1, 0.5*inch))
    st.append(hr())
    st.append(Paragraph("Fin du PLAN DE MATCH STEEVE-MAX v1 — Document normatif officiel. Toute deviation necessite l'approbation explicite de Steeve.", s['BJ']))

    doc.build(st)
    print(f"PDF genere: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    build_pdf()
