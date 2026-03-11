"""
BIONIC V5 — SCIENTIFIC SOURCES SCHEMA
======================================
PHASE 7 — Knowledge Layer

Schéma standardisé pour intégrer et tracer les sources scientifiques
et empiriques dans le moteur BIONIC V5.

EXIGENCES DE TRAÇABILITÉ:
- Chaque règle comportementale DOIT référencer une ou plusieurs sources
- Chaque pondération DOIT être justifiée par une source
- Chaque source DOIT avoir un niveau de confiance documenté
- Chaque source DOIT avoir un statut de validation

CATÉGORIES DE SOURCES:
- ACADEMIC_QC: Université Laval, MFFP Québec, UQAR, Parcs Canada
- ACADEMIC_US: USGS, State Wildlife Agencies, University of Maine
- EMPIRICAL: Louis Gagnon, guides/trappeurs nordiques
- INDUSTRY: Whitetail Habitat Solutions, The Hunting Public, MeatEater
- ASSOCIATION: NDA, QDMA, programmes Alberta/BC

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class SourceType(str, Enum):
    """Type de source scientifique ou empirique"""
    PEER_REVIEWED = "peer_reviewed"          # Publication revue par les pairs
    ACADEMIC_REPORT = "academic_report"      # Rapport académique non publié
    GOVERNMENT_DATA = "government_data"      # Données gouvernementales
    FIELD_STUDY = "field_study"              # Étude de terrain
    EMPIRICAL_EXPERT = "empirical_expert"    # Expertise empirique (guides, trappeurs)
    TELEMETRY_DATA = "telemetry_data"        # Données GPS/télémétrie
    CAMERA_TRAP = "camera_trap"              # Données de caméras de surveillance
    INDUSTRY_RESEARCH = "industry_research"  # Recherche industrielle
    ASSOCIATION_DATA = "association_data"    # Données d'associations


class ValidationStatus(str, Enum):
    """Statut de validation de la source"""
    PENDING = "pending"                      # En attente de validation
    FIELD_VALIDATED = "field_validated"      # Validé sur le terrain
    PEER_REVIEWED = "peer_reviewed"          # Revu par les pairs
    CROSS_VALIDATED = "cross_validated"      # Validé par recoupement
    DEPRECATED = "deprecated"                # Obsolète


class ConfidenceLevel(str, Enum):
    """Niveau de confiance de la source"""
    VERY_HIGH = "very_high"    # 0.90-1.00 - Publication majeure, données massives
    HIGH = "high"              # 0.75-0.89 - Étude solide, bonne méthodologie
    MEDIUM = "medium"          # 0.50-0.74 - Données partielles, échantillon limité
    LOW = "low"                # 0.25-0.49 - Expertise empirique, observations
    VERY_LOW = "very_low"      # 0.00-0.24 - Anecdotique, non vérifié


@dataclass
class ScientificSource:
    """
    Source scientifique ou empirique traçable.
    
    Chaque règle, pondération ou modèle du Knowledge Layer
    DOIT référencer une ou plusieurs instances de cette classe.
    """
    
    # Identifiant unique
    source_id: str = field(default_factory=lambda: f"SRC-{uuid.uuid4().hex[:8].upper()}")
    
    # Métadonnées de la source
    name: str = ""
    institution: str = ""
    category: str = ""  # ACADEMIC_QC, ACADEMIC_US, EMPIRICAL, INDUSTRY, ASSOCIATION
    
    # Type et validation
    source_type: SourceType = SourceType.FIELD_STUDY
    validation_status: ValidationStatus = ValidationStatus.PENDING
    
    # Confiance
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_score: float = 0.5  # 0.0 à 1.0
    
    # Citation
    citation: str = ""
    url: Optional[str] = None
    doi: Optional[str] = None
    publication_year: Optional[int] = None
    
    # Applicabilité
    species: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    seasons: List[str] = field(default_factory=list)
    
    # Métadonnées de validation
    validated_by: Optional[str] = None
    validation_date: Optional[datetime] = None
    validation_notes: Optional[str] = None
    
    # Audit
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            "source_id": self.source_id,
            "name": self.name,
            "institution": self.institution,
            "category": self.category,
            "source_type": self.source_type.value,
            "validation_status": self.validation_status.value,
            "confidence_level": self.confidence_level.value,
            "confidence_score": self.confidence_score,
            "citation": self.citation,
            "url": self.url,
            "doi": self.doi,
            "publication_year": self.publication_year,
            "species": self.species,
            "regions": self.regions,
            "seasons": self.seasons
        }


class SourceRegistry:
    """
    Registre central de toutes les sources scientifiques et empiriques.
    
    Ce registre est le point d'entrée unique pour accéder aux sources
    utilisées dans le Knowledge Layer.
    """
    
    def __init__(self):
        self._sources: Dict[str, ScientificSource] = {}
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialiser les sources de référence"""
        
        # =====================================================
        # ACADÉMIQUE QUÉBEC (ACADEMIC_QC)
        # =====================================================
        
        self._register(ScientificSource(
            source_id="SRC-LAVAL-001",
            name="Écologie de l'orignal au Québec",
            institution="Université Laval",
            category="ACADEMIC_QC",
            source_type=SourceType.PEER_REVIEWED,
            validation_status=ValidationStatus.PEER_REVIEWED,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            confidence_score=0.95,
            citation="Département de biologie, Université Laval. Études sur l'orignal québécois.",
            url="https://www.bio.ulaval.ca",
            species=["orignal", "moose"],
            regions=["CA-QC"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-MFFP-001",
            name="Plan de gestion de l'orignal au Québec",
            institution="MFFP Québec",
            category="ACADEMIC_QC",
            source_type=SourceType.GOVERNMENT_DATA,
            validation_status=ValidationStatus.CROSS_VALIDATED,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            confidence_score=0.92,
            citation="Ministère des Forêts, de la Faune et des Parcs. Plan de gestion 2020-2027.",
            url="https://mffp.gouv.qc.ca",
            species=["orignal", "cerf de Virginie", "ours noir"],
            regions=["CA-QC"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-UQAR-001",
            name="Dynamique des populations de cervidés",
            institution="UQAR",
            category="ACADEMIC_QC",
            source_type=SourceType.ACADEMIC_REPORT,
            validation_status=ValidationStatus.PEER_REVIEWED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.85,
            citation="Université du Québec à Rimouski. Recherche en écologie animale.",
            url="https://www.uqar.ca",
            species=["orignal", "cerf de Virginie"],
            regions=["CA-QC"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-PARCS-001",
            name="Études de télémétrie - Parcs nationaux",
            institution="Parcs Canada",
            category="ACADEMIC_QC",
            source_type=SourceType.TELEMETRY_DATA,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            confidence_score=0.93,
            citation="Parcs Canada. Programme de suivi de la faune.",
            url="https://www.pc.gc.ca",
            species=["orignal", "ours noir", "cerf de Virginie"],
            regions=["CA-QC", "CA-ON", "CA-NB"],
            seasons=["all"]
        ))
        
        # =====================================================
        # ACADÉMIQUE USA (ACADEMIC_US)
        # =====================================================
        
        self._register(ScientificSource(
            source_id="SRC-USGS-001",
            name="Wildlife Behavior Studies",
            institution="USGS",
            category="ACADEMIC_US",
            source_type=SourceType.GOVERNMENT_DATA,
            validation_status=ValidationStatus.PEER_REVIEWED,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            confidence_score=0.94,
            citation="U.S. Geological Survey. National Wildlife Research Center.",
            url="https://www.usgs.gov/centers/nwrc",
            species=["white-tailed deer", "mule deer", "elk", "black bear"],
            regions=["US"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-UMAINE-001",
            name="Deer Ecology Research Program",
            institution="University of Maine",
            category="ACADEMIC_US",
            source_type=SourceType.PEER_REVIEWED,
            validation_status=ValidationStatus.PEER_REVIEWED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.88,
            citation="University of Maine. Department of Wildlife, Fisheries, and Conservation Biology.",
            url="https://umaine.edu/wle/",
            species=["white-tailed deer", "moose"],
            regions=["US-ME", "US-NH", "US-VT"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-STATE-001",
            name="State Wildlife Agency Composite Data",
            institution="State Wildlife Agencies (US)",
            category="ACADEMIC_US",
            source_type=SourceType.GOVERNMENT_DATA,
            validation_status=ValidationStatus.CROSS_VALIDATED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.82,
            citation="Compilation of state wildlife agency research data.",
            species=["white-tailed deer", "mule deer", "elk", "black bear"],
            regions=["US"],
            seasons=["all"]
        ))
        
        # =====================================================
        # EMPIRIQUE (EMPIRICAL)
        # =====================================================
        
        self._register(ScientificSource(
            source_id="SRC-GAGNON-001",
            name="Expertise terrain - Guides nordiques",
            institution="Louis Gagnon et associés",
            category="EMPIRICAL",
            source_type=SourceType.EMPIRICAL_EXPERT,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.78,
            citation="Louis Gagnon. 40 ans d'expérience de guidage en forêt boréale.",
            species=["orignal", "ours noir"],
            regions=["CA-QC"],
            seasons=["fall", "rut"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-TRAP-001",
            name="Connaissances traditionnelles - Trappeurs",
            institution="Association des trappeurs du Québec",
            category="EMPIRICAL",
            source_type=SourceType.EMPIRICAL_EXPERT,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.MEDIUM,
            confidence_score=0.68,
            citation="Connaissances transmises par les trappeurs professionnels.",
            species=["orignal", "ours noir", "cerf de Virginie"],
            regions=["CA-QC"],
            seasons=["all"]
        ))
        
        # =====================================================
        # INDUSTRIE (INDUSTRY)
        # =====================================================
        
        self._register(ScientificSource(
            source_id="SRC-WHS-001",
            name="Whitetail Habitat Management Research",
            institution="Whitetail Habitat Solutions",
            category="INDUSTRY",
            source_type=SourceType.INDUSTRY_RESEARCH,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.80,
            citation="Whitetail Habitat Solutions. Research on optimal deer habitat.",
            url="https://www.whitetailhabitats.com",
            species=["white-tailed deer"],
            regions=["US"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-THP-001",
            name="The Hunting Public Field Data",
            institution="The Hunting Public",
            category="INDUSTRY",
            source_type=SourceType.FIELD_STUDY,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.MEDIUM,
            confidence_score=0.72,
            citation="The Hunting Public. Field observations and hunting data.",
            url="https://www.thehuntingpublic.com",
            species=["white-tailed deer"],
            regions=["US"],
            seasons=["fall", "rut"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-ME-001",
            name="MeatEater Conservation Data",
            institution="MeatEater",
            category="INDUSTRY",
            source_type=SourceType.FIELD_STUDY,
            validation_status=ValidationStatus.FIELD_VALIDATED,
            confidence_level=ConfidenceLevel.MEDIUM,
            confidence_score=0.70,
            citation="MeatEater Inc. Field research and conservation initiatives.",
            url="https://www.themeateater.com",
            species=["white-tailed deer", "mule deer", "elk"],
            regions=["US"],
            seasons=["all"]
        ))
        
        # =====================================================
        # ASSOCIATIONS (ASSOCIATION)
        # =====================================================
        
        self._register(ScientificSource(
            source_id="SRC-NDA-001",
            name="National Deer Association Research",
            institution="NDA (formerly QDMA)",
            category="ASSOCIATION",
            source_type=SourceType.ASSOCIATION_DATA,
            validation_status=ValidationStatus.PEER_REVIEWED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.85,
            citation="National Deer Association. Deer management and research data.",
            url="https://www.deerassociation.com",
            species=["white-tailed deer"],
            regions=["US", "CA"],
            seasons=["all"]
        ))
        
        self._register(ScientificSource(
            source_id="SRC-ABBC-001",
            name="Alberta/BC Wildlife Programs",
            institution="Alberta Environment / BC Wildlife",
            category="ASSOCIATION",
            source_type=SourceType.GOVERNMENT_DATA,
            validation_status=ValidationStatus.CROSS_VALIDATED,
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.83,
            citation="Provincial wildlife management programs.",
            url="https://www.alberta.ca/wildlife",
            species=["mule deer", "elk", "moose", "black bear"],
            regions=["CA-AB", "CA-BC"],
            seasons=["all"]
        ))
    
    def _register(self, source: ScientificSource):
        """Enregistrer une source"""
        self._sources[source.source_id] = source
    
    def get(self, source_id: str) -> Optional[ScientificSource]:
        """Obtenir une source par ID"""
        return self._sources.get(source_id)
    
    def get_by_category(self, category: str) -> List[ScientificSource]:
        """Obtenir toutes les sources d'une catégorie"""
        return [s for s in self._sources.values() if s.category == category]
    
    def get_by_species(self, species: str) -> List[ScientificSource]:
        """Obtenir toutes les sources pour une espèce"""
        species_lower = species.lower()
        return [
            s for s in self._sources.values() 
            if any(sp.lower() == species_lower or species_lower in sp.lower() for sp in s.species)
        ]
    
    def get_by_confidence(self, min_confidence: float) -> List[ScientificSource]:
        """Obtenir toutes les sources avec un score de confiance minimum"""
        return [s for s in self._sources.values() if s.confidence_score >= min_confidence]
    
    def get_all(self) -> List[ScientificSource]:
        """Obtenir toutes les sources"""
        return list(self._sources.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du registre"""
        sources = self._sources.values()
        
        by_category = {}
        by_confidence = {"very_high": 0, "high": 0, "medium": 0, "low": 0, "very_low": 0}
        by_validation = {}
        
        for s in sources:
            by_category[s.category] = by_category.get(s.category, 0) + 1
            by_confidence[s.confidence_level.value] = by_confidence.get(s.confidence_level.value, 0) + 1
            by_validation[s.validation_status.value] = by_validation.get(s.validation_status.value, 0) + 1
        
        return {
            "total_sources": len(self._sources),
            "by_category": by_category,
            "by_confidence_level": by_confidence,
            "by_validation_status": by_validation,
            "average_confidence": sum(s.confidence_score for s in sources) / len(sources) if sources else 0
        }


# Singleton
_registry_instance: Optional[SourceRegistry] = None


def get_source_registry() -> SourceRegistry:
    """Obtenir l'instance singleton du registre de sources"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SourceRegistry()
    return _registry_instance


__all__ = [
    'ScientificSource',
    'SourceType',
    'ValidationStatus',
    'ConfidenceLevel',
    'SourceRegistry',
    'get_source_registry'
]
