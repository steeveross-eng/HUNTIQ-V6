"""Scientific References Database - AI Engine

Complete scientific references for attractant analysis.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

from typing import List, Dict, Any

# ============================================
# RÉFÉRENCES SCIENTIFIQUES CONSOLIDÉES
# ============================================

SCIENTIFIC_REFERENCES = {
    "olfaction_perception": {
        "title": "5.1. Olfaction et perception chimique",
        "references": [
            "Sánchez, et al. (2022) – Études sur l'évolution des gènes olfactifs chez les cervidés",
            "Geist, V. (1998). Deer of the World: Their Evolution, Behaviour, and Ecology",
            "Døving, K. B. & Trotier, D. (1998) – Structure et fonction de l'organe voméronasal",
            "Rasmussen, L. E. L. & Schulte, B. A. (1998) – Communication chimique chez les mammifères"
        ]
    },
    "attractants_repellents": {
        "title": "5.2. Odeurs biologiquement significatives, attractants et répulsifs",
        "references": [
            "Nolte, D. L. (1999) – Réponses comportementales des cervidés aux attractants et répulsifs",
            "Müller-Schwarze, D. (2011). Chemical Ecology of Vertebrates",
            "Apfelbach, R., et al. (2005) – Effets des odeurs de prédateurs sur les mammifères",
            "Müller-Schwarze, D. & Sun, L. (2003) – Signaux chimiques chez les vertébrés"
        ]
    },
    "fruits_volatiles": {
        "title": "5.3. Attraction pour fruits mûrs, fermentés et composés volatils",
        "references": [
            "Atkinson, R. G., et al. (2017) – Composés volatils responsables des arômes de fruits",
            "Feldhamer, G. A., Thompson, B. C., & Chapman, J. A. (2003). Wild Mammals of North America (sections sur l'alimentation des cervidés)",
            "Herrera, C. M. (1982) – Mutualisme plantes–animaux et défense des fruits mûrs",
            "Schmidt, K. T., et al. – Sélection alimentaire des cervidés selon les ressources fruitées"
        ]
    },
    "nutrition": {
        "title": "5.4. Minéraux, vitamines, protéines et nutrition faunique",
        "references": [
            "Robbins, C. T. (1993). Wildlife Feeding and Nutrition",
            "Weeks, H. P. & Kirkpatrick, C. M. (1976) – Besoins minéraux des cervidés",
            "Ullrey, D. E., Youatt, W. G., Johnson, H. E., et al. – Travaux sur les besoins nutritionnels des cervidés",
            "Mautz, W. W. (1978) – Cycle des réserves de graisse chez les cervidés"
        ]
    },
    "behavioral_compounds": {
        "title": "5.5. Composés comportementaux et signaux chimiques",
        "references": [
            "Gassett, J. W., et al. (1997) – Communication chimique chez le cerf de Virginie",
            "Brown, R. E. & Macdonald, D. W. (1985). Social Odours in Mammals",
            "Marchinton, R. L. & Hirth, D. H. – Études sur les comportements sociaux et marquages",
            "Müller-Schwarze, D. (série Chemical Signals in Vertebrates)"
        ]
    },
    "ecology_management": {
        "title": "5.6. Écologie chimique, gestion faunique et comportement",
        "references": [
            "Johansson, B. G. & Jones, T. M. (2007) – Rôle de la communication chimique dans le choix du partenaire",
            "Putman, R. J. (1988). The Natural History of Deer",
            "Milner, J. M., Bonenfant, C., Mysterud, A., et al. – Gestion des populations de cervidés",
            "Apfelbach, R., et al. – Réactions comportementales aux signaux olfactifs"
        ]
    }
}


def get_scientific_references() -> List[Dict[str, Any]]:
    """Return formatted scientific references for display"""
    return [
        {
            "section_id": key,
            "title": value["title"],
            "references": value["references"]
        }
        for key, value in SCIENTIFIC_REFERENCES.items()
    ]


def get_references_by_section(section_id: str) -> Dict[str, Any]:
    """Get references for a specific section"""
    section = SCIENTIFIC_REFERENCES.get(section_id)
    if section:
        return {"section_id": section_id, **section}
    return {}


def list_sections() -> List[str]:
    """List all reference section IDs"""
    return list(SCIENTIFIC_REFERENCES.keys())
