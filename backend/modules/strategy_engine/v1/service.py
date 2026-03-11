"""Strategy Engine Service - CORE

Business logic for hunting strategy generation.
Combines weather, terrain, and species data to create optimal strategies.

Version: 1.0.0
"""

import uuid
from typing import List, Dict, Any
from .models import (
    HuntingContext, 
    HuntingStrategy, 
    StrategyRecommendation,
    StandPlacement,
    AttractantStrategy
)


class StrategyService:
    """Service for hunting strategy generation"""
    
    # Species behavior patterns
    SPECIES_PATTERNS = {
        "deer": {
            "active_times": ["dawn", "dusk"],
            "feeding_times": ["dawn", "afternoon", "dusk"],
            "bedding_times": ["midday"],
            "preferred_terrain": ["edge", "forest"],
            "sensitivity": "high",
            "approach_distance": 30
        },
        "moose": {
            "active_times": ["dawn", "dusk", "night"],
            "feeding_times": ["dawn", "afternoon", "dusk"],
            "bedding_times": ["midday"],
            "preferred_terrain": ["swamp", "forest"],
            "sensitivity": "medium",
            "approach_distance": 50
        },
        "bear": {
            "active_times": ["dawn", "dusk", "morning", "afternoon"],
            "feeding_times": ["morning", "afternoon"],
            "bedding_times": ["midday", "night"],
            "preferred_terrain": ["forest", "edge"],
            "sensitivity": "low",
            "approach_distance": 40
        },
        "wild_boar": {
            "active_times": ["dusk", "night", "dawn"],
            "feeding_times": ["night", "dawn", "dusk"],
            "bedding_times": ["midday", "afternoon"],
            "preferred_terrain": ["forest", "field"],
            "sensitivity": "medium",
            "approach_distance": 35
        },
        "turkey": {
            "active_times": ["dawn", "morning", "afternoon"],
            "feeding_times": ["morning", "afternoon"],
            "roosting_times": ["dusk", "night"],
            "preferred_terrain": ["field", "edge"],
            "sensitivity": "very_high",
            "approach_distance": 20
        }
    }
    
    # Season impact on strategies
    SEASON_MODIFIERS = {
        "spring": {
            "activity_boost": 1.2,
            "feeding_focus": True,
            "territorial": True,
            "notes": "Période de sortie d'hibernation et alimentation intensive"
        },
        "summer": {
            "activity_boost": 0.8,
            "feeding_focus": True,
            "territorial": False,
            "notes": "Chaleur réduit l'activité diurne"
        },
        "fall": {
            "activity_boost": 1.5,
            "feeding_focus": True,
            "territorial": True,
            "notes": "Période du rut - activité maximale"
        },
        "winter": {
            "activity_boost": 0.9,
            "feeding_focus": True,
            "territorial": False,
            "notes": "Conservation d'énergie, déplacements limités"
        }
    }
    
    # Weather impact
    WEATHER_IMPACT = {
        "clear": {"score_modifier": 1.0, "visibility": "excellent", "scent_dispersion": "good"},
        "cloudy": {"score_modifier": 1.1, "visibility": "good", "scent_dispersion": "moderate"},
        "rain": {"score_modifier": 0.7, "visibility": "reduced", "scent_dispersion": "excellent"},
        "snow": {"score_modifier": 1.2, "visibility": "variable", "scent_dispersion": "poor"},
        "fog": {"score_modifier": 1.3, "visibility": "poor", "scent_dispersion": "excellent"},
        "wind": {"score_modifier": 0.8, "visibility": "good", "scent_dispersion": "excellent"}
    }
    
    def generate_strategy(self, context: HuntingContext) -> HuntingStrategy:
        """
        Generate a complete hunting strategy based on context.
        """
        species_data = self.SPECIES_PATTERNS.get(context.species, self.SPECIES_PATTERNS["deer"])
        season_data = self.SEASON_MODIFIERS.get(context.season, self.SEASON_MODIFIERS["fall"])
        weather_data = self.WEATHER_IMPACT.get(context.weather, self.WEATHER_IMPACT["clear"])
        
        # Calculate overall score
        base_score = 6.0
        
        # Time of day impact
        if context.time_of_day in species_data["active_times"]:
            base_score += 2.0
        elif context.time_of_day in species_data.get("feeding_times", []):
            base_score += 1.0
        
        # Apply modifiers
        base_score *= season_data["activity_boost"]
        base_score *= weather_data["score_modifier"]
        
        # Terrain match
        if context.terrain in species_data["preferred_terrain"]:
            base_score += 1.0
        
        overall_score = min(10, max(0, round(base_score, 1)))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context, species_data, season_data, weather_data)
        
        # Determine primary approach
        primary_approach = self._determine_approach(context, species_data)
        
        # Generate equipment list
        equipment = self._generate_equipment_list(context, species_data)
        
        # Timing recommendations
        timing = self._generate_timing(context, species_data)
        
        # Warnings
        warnings = self._generate_warnings(context, weather_data)
        
        # Success estimate
        if overall_score >= 8:
            success_estimate = "Excellentes chances de succès"
        elif overall_score >= 6:
            success_estimate = "Bonnes chances de succès"
        elif overall_score >= 4:
            success_estimate = "Chances modérées"
        else:
            success_estimate = "Conditions difficiles"
        
        return HuntingStrategy(
            id=str(uuid.uuid4()),
            context=context,
            overall_score=overall_score,
            success_estimate=success_estimate,
            primary_approach=primary_approach,
            recommendations=recommendations,
            equipment=equipment,
            timing=timing,
            warnings=warnings
        )
    
    def _generate_recommendations(self, context: HuntingContext, 
                                   species_data: Dict, season_data: Dict, 
                                   weather_data: Dict) -> List[StrategyRecommendation]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Position recommendation
        recommendations.append(StrategyRecommendation(
            priority=1,
            category="Position",
            title="Positionnement optimal",
            description=f"Pour le {context.species}, privilégiez les zones de {context.terrain}",
            tips=[
                f"Distance d'approche recommandée: {species_data['approach_distance']}m",
                "Restez sous le vent par rapport à votre cible",
                "Arrivez sur place 30 min avant l'activité prévue"
            ],
            success_probability=70
        ))
        
        # Movement recommendation
        recommendations.append(StrategyRecommendation(
            priority=2,
            category="Déplacement",
            title="Stratégie de mouvement",
            description="Minimisez vos déplacements pendant les périodes actives",
            tips=[
                "Mouvement lent et silencieux",
                "Évitez de briser des branches",
                "Utilisez le terrain naturel comme couverture"
            ],
            success_probability=65
        ))
        
        # Scent control
        if species_data["sensitivity"] in ["high", "very_high"]:
            recommendations.append(StrategyRecommendation(
                priority=1,
                category="Contrôle des odeurs",
                title="Gestion olfactive critique",
                description="Cette espèce a un odorat très développé",
                tips=[
                    "Utilisez des vêtements traités anti-odeur",
                    "Évitez les parfums et déodorants",
                    "Chassez avec le vent dans le visage",
                    "Changez d'emplacement si le vent tourne"
                ],
                success_probability=80
            ))
        
        # Weather-specific
        if context.weather == "rain":
            recommendations.append(StrategyRecommendation(
                priority=3,
                category="Météo",
                title="Adaptation à la pluie",
                description="La pluie offre une excellente couverture olfactive",
                tips=[
                    "Profitez de la dispersion des odeurs",
                    "Les animaux se déplacent souvent après la pluie",
                    "Équipement imperméable essentiel"
                ],
                success_probability=60
            ))
        
        return sorted(recommendations, key=lambda x: x.priority)
    
    def _determine_approach(self, context: HuntingContext, species_data: Dict) -> str:
        """Determine the primary hunting approach"""
        if context.time_of_day in ["dawn", "dusk"]:
            if context.terrain == "edge":
                return "Affût en lisière de forêt"
            elif context.terrain == "field":
                return "Affût en bordure de champ"
            else:
                return "Affût sur sentier d'accès"
        elif context.time_of_day in ["morning", "afternoon"]:
            if species_data["sensitivity"] == "very_high":
                return "Approche lente et silencieuse"
            else:
                return "Traque douce avec arrêts fréquents"
        else:
            return "Poste fixe près des zones d'alimentation"
    
    def _generate_equipment_list(self, context: HuntingContext, species_data: Dict) -> List[str]:
        """Generate recommended equipment list"""
        equipment = [
            "Jumelles",
            "Boussole/GPS",
            "Couteau de chasse",
            "Kit de premiers soins"
        ]
        
        if context.weather in ["rain", "snow"]:
            equipment.extend(["Vêtements imperméables", "Sac étanche"])
        
        if context.weather == "fog" or context.time_of_day in ["dawn", "dusk"]:
            equipment.append("Lampe frontale (rouge)")
        
        if species_data["sensitivity"] in ["high", "very_high"]:
            equipment.extend(["Spray anti-odeur", "Gants en caoutchouc"])
        
        if context.species in ["moose", "deer"]:
            equipment.append("Appeaux/Calls")
        
        if context.terrain == "swamp":
            equipment.append("Bottes cuissardes")
        
        return equipment
    
    def _generate_timing(self, context: HuntingContext, species_data: Dict) -> Dict[str, Any]:
        """Generate timing recommendations"""
        return {
            "best_times": species_data["active_times"],
            "feeding_periods": species_data.get("feeding_times", []),
            "avoid_times": species_data.get("bedding_times", []),
            "recommended_duration": "3-4 heures par session",
            "arrival_time": "30 minutes avant l'activité prévue",
            "patience_note": "Restez en place au moins 2 heures avant de bouger"
        }
    
    def _generate_warnings(self, context: HuntingContext, weather_data: Dict) -> List[str]:
        """Generate safety and tactical warnings"""
        warnings = []
        
        if weather_data["visibility"] in ["reduced", "poor"]:
            warnings.append("⚠️ Visibilité réduite - Soyez prudent avec les tirs")
        
        if context.weather == "wind":
            warnings.append("⚠️ Vent fort - Difficile de prévoir le déplacement des odeurs")
        
        if context.species == "bear":
            warnings.append("⚠️ Chassez en groupe ou informez quelqu'un de votre position")
        
        if context.time_of_day in ["dusk", "night"]:
            warnings.append("⚠️ Prévoyez votre chemin de retour avant la tombée de la nuit")
        
        if context.terrain == "swamp":
            warnings.append("⚠️ Terrain difficile - Attention aux zones instables")
        
        return warnings
    
    def get_stand_placement(self, context: HuntingContext) -> StandPlacement:
        """Generate stand placement recommendation"""
        species_data = self.SPECIES_PATTERNS.get(context.species, self.SPECIES_PATTERNS["deer"])
        
        # Determine placement type
        if context.terrain == "forest":
            placement_type = "tree_stand"
            height = 4.5
        elif context.terrain == "field":
            placement_type = "ground_blind"
            height = 0
        else:
            placement_type = "natural_blind"
            height = 1.5
        
        return StandPlacement(
            placement_type=placement_type,
            orientation="Face au vent dominant",
            height_meters=height,
            distance_from_trail_meters=species_data["approach_distance"],
            cover_requirements="Couverture arrière et latérale",
            entry_exit_strategy="Approchez par le côté opposé au vent, évitez de croiser les sentiers de gibier"
        )
    
    def get_attractant_strategy(self, context: HuntingContext) -> AttractantStrategy:
        """Generate attractant usage strategy"""
        # Determine best attractant type based on context
        if context.species in ["deer", "moose"] and context.season == "fall":
            product_type = "urine"
        elif context.species == "bear":
            product_type = "gel"  # Sweet attractants
        else:
            product_type = "granules"
        
        return AttractantStrategy(
            product_type=product_type,
            placement_distance_meters=25,
            quantity="50-100ml ou 100-200g",
            timing="24-48h avant la chasse",
            renewal_frequency="Tous les 2-3 jours",
            wind_considerations="Placez l'attractant de sorte que le vent porte l'odeur vers les zones de passage"
        )
