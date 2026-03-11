"""
BIONIC™ Real Estate Scoring Service
=====================================
Phase 11-15: Module Immobilier

Service de scoring géospatial pour propriétés immobilières.
Calcule le potentiel de chasse et la valeur BIONIC.
"""

from typing import Dict, Any


class RealEstateScoringService:
    """
    Service de scoring BIONIC pour propriétés immobilières.
    
    Évalue le potentiel de chasse d'une propriété en fonction de:
    - Habitat et couverture végétale
    - Proximité des points d'eau
    - Topographie et terrain
    - Accessibilité
    - Biodiversité locale
    """
    
    # Weights for each scoring category
    SCORE_WEIGHTS = {
        'habitat': 0.25,
        'water': 0.20,
        'terrain': 0.20,
        'access': 0.15,
        'biodiversity': 0.20
    }
    
    # Species-specific scoring adjustments
    SPECIES_FACTORS = {
        'moose': {'water': 1.3, 'terrain': 0.8, 'habitat': 1.2},
        'deer': {'habitat': 1.2, 'access': 1.1, 'terrain': 0.9},
        'bear': {'biodiversity': 1.3, 'water': 1.1, 'habitat': 1.2},
        'turkey': {'habitat': 1.1, 'access': 1.2, 'terrain': 0.9},
        'duck': {'water': 1.5, 'habitat': 1.0, 'terrain': 0.7}
    }
    
    @classmethod
    def calculate_property_score(
        cls,
        coordinates: Dict[str, float],
        area_m2: float,
        features: Dict[str, Any] = None,
        species: str = None
    ) -> Dict[str, Any]:
        """
        Calcule le score BIONIC d'une propriété.
        
        Args:
            coordinates: {lat, lng}
            area_m2: Superficie en m²
            features: Caractéristiques optionnelles
            species: Espèce cible (optionnel)
            
        Returns:
            Dict avec les scores détaillés
        """
        features = features or {}
        
        # Calculate individual scores
        scores = {
            'habitat_score': cls._calculate_habitat_score(coordinates, area_m2, features),
            'water_score': cls._calculate_water_score(coordinates, features),
            'terrain_score': cls._calculate_terrain_score(coordinates, features),
            'access_score': cls._calculate_access_score(coordinates, features),
            'biodiversity_score': cls._calculate_biodiversity_score(coordinates, features)
        }
        
        # Apply species-specific factors if provided
        if species and species in cls.SPECIES_FACTORS:
            factors = cls.SPECIES_FACTORS[species]
            for key, factor in factors.items():
                score_key = f"{key}_score"
                if score_key in scores:
                    scores[score_key] = min(100, scores[score_key] * factor)
        
        # Calculate overall score
        overall = sum(
            scores[f"{cat}_score"] * weight 
            for cat, weight in cls.SCORE_WEIGHTS.items()
        )
        scores['overall_score'] = round(overall, 1)
        
        # Determine rating
        scores['rating'] = cls._get_rating(overall)
        
        # Calculate species potential
        scores['species_potential'] = cls._calculate_species_potential(scores)
        
        return scores
    
    @classmethod
    def _calculate_habitat_score(
        cls, 
        coordinates: Dict[str, float], 
        area_m2: float,
        features: Dict
    ) -> float:
        """Calcule le score d'habitat basé sur la végétation et superficie."""
        # Base score from area (larger = better for wildlife)
        area_ha = area_m2 / 10000
        area_score = min(100, 40 + (area_ha * 2))
        
        # Adjust based on vegetation if available
        vegetation_type = features.get('vegetation_type', 'mixed')
        vegetation_bonus = {
            'forest': 20,
            'mixed': 15,
            'wetland': 15,
            'prairie': 10,
            'agricultural': 5,
            'urban': -20
        }.get(vegetation_type, 10)
        
        return min(100, max(0, area_score + vegetation_bonus))
    
    @classmethod
    def _calculate_water_score(
        cls,
        coordinates: Dict[str, float],
        features: Dict
    ) -> float:
        """Calcule le score basé sur la proximité des points d'eau."""
        water_distance = features.get('water_distance_m', 1000)
        has_water = features.get('has_water_body', False)
        
        if has_water:
            return 95
        
        # Score inversely proportional to water distance
        if water_distance < 100:
            return 90
        elif water_distance < 500:
            return 75
        elif water_distance < 1000:
            return 60
        elif water_distance < 2000:
            return 40
        else:
            return 20
    
    @classmethod
    def _calculate_terrain_score(
        cls,
        coordinates: Dict[str, float],
        features: Dict
    ) -> float:
        """Calcule le score basé sur la topographie."""
        elevation_variation = features.get('elevation_variation_m', 50)
        slope_avg = features.get('average_slope_deg', 10)
        
        # Moderate variation is optimal
        if 20 <= elevation_variation <= 100:
            elevation_score = 80
        elif elevation_variation < 20:
            elevation_score = 60
        else:
            elevation_score = 50
        
        # Moderate slope is optimal
        if 5 <= slope_avg <= 20:
            slope_score = 80
        elif slope_avg < 5:
            slope_score = 70
        else:
            slope_score = 50
        
        return (elevation_score + slope_score) / 2
    
    @classmethod
    def _calculate_access_score(
        cls,
        coordinates: Dict[str, float],
        features: Dict
    ) -> float:
        """Calcule le score d'accessibilité."""
        road_distance = features.get('road_distance_m', 500)
        has_road_access = features.get('has_road_access', False)
        
        if has_road_access:
            base_score = 85
        else:
            base_score = 50
        
        # Adjust based on road distance
        if road_distance < 200:
            return min(100, base_score + 10)
        elif road_distance < 1000:
            return base_score
        elif road_distance < 3000:
            return max(30, base_score - 20)
        else:
            return 20
    
    @classmethod
    def _calculate_biodiversity_score(
        cls,
        coordinates: Dict[str, float],
        features: Dict
    ) -> float:
        """Calcule le score de biodiversité."""
        # This would ideally use external biodiversity data
        known_species = features.get('known_species_count', 3)
        ecosystem_diversity = features.get('ecosystem_types', 1)
        
        species_score = min(100, known_species * 15)
        ecosystem_score = min(100, ecosystem_diversity * 25)
        
        return (species_score + ecosystem_score) / 2
    
    @classmethod
    def _get_rating(cls, score: float) -> str:
        """Convertit un score en rating textuel."""
        if score >= 85:
            return "Exceptionnel"
        elif score >= 70:
            return "Excellent"
        elif score >= 55:
            return "Très bon"
        elif score >= 40:
            return "Bon"
        elif score >= 25:
            return "Moyen"
        else:
            return "Faible"
    
    @classmethod
    def _calculate_species_potential(cls, scores: Dict) -> Dict[str, float]:
        """Calcule le potentiel pour chaque espèce."""
        potential = {}
        
        for species, factors in cls.SPECIES_FACTORS.items():
            species_score = sum(
                scores.get(f"{key}_score", 50) * factor * cls.SCORE_WEIGHTS.get(key, 0.2)
                for key, factor in factors.items()
            )
            potential[species] = round(min(100, species_score), 1)
        
        return potential


# Export
__all__ = ['RealEstateScoringService']
