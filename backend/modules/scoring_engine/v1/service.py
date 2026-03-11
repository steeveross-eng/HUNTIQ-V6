"""Scoring Engine Service - CORE

Business logic for scientific scoring of attractants.
Extracted from analyzer.py calculate_score method.

Version: 1.0.0
"""

from typing import Dict, Any, List
from .data.criteria import SCORING_CRITERIA, get_total_weight
from .models import ScoringResult


class ScoringService:
    """Service for calculating scientific scores of attractants"""
    
    def __init__(self):
        self.criteria = SCORING_CRITERIA
        self.total_weight = get_total_weight()
    
    def calculate_score(self, analysis_data: Dict[str, Any], product_type: str = "granules") -> ScoringResult:
        """
        Calculate the scientific score based on weighted criteria.
        
        This is the core scoring algorithm extracted from analyzer.py.
        Uses 13 weighted criteria to produce a final score out of 10.
        
        Args:
            analysis_data: Dictionary with criterion values
            product_type: Type of product (for context)
            
        Returns:
            ScoringResult with total score and breakdown
        """
        criteria_scores = {}
        weighted_scores = {}
        
        # Helper function to safely get numeric value
        def get_numeric(key: str, default: float) -> float:
            value = analysis_data.get(key, default)
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, list):
                return float(len(value)) if value else default
            elif isinstance(value, bool):
                return 10.0 if value else default
            return default
        
        # Extract scores from analysis data
        attraction_days = get_numeric("attraction_days", 10)
        criteria_scores["attraction_days"] = min(attraction_days, 60) / 60 * 10
        criteria_scores["natural_palatability"] = get_numeric("natural_palatability", 7)
        criteria_scores["olfactory_power"] = get_numeric("olfactory_power", 7)
        criteria_scores["persistence"] = get_numeric("persistence", 7)
        criteria_scores["nutrition"] = get_numeric("nutrition", 5)
        criteria_scores["behavioral_compounds"] = get_numeric("behavioral_compounds", 5)
        criteria_scores["rainproof"] = 10 if analysis_data.get("rainproof", False) else 3
        criteria_scores["feed_proof"] = 10 if analysis_data.get("feed_proof", False) else 5
        criteria_scores["certified"] = 10 if analysis_data.get("certified", False) else 4
        criteria_scores["physical_resistance"] = get_numeric("physical_resistance", 6)
        criteria_scores["ingredient_purity"] = get_numeric("ingredient_purity", 6)
        criteria_scores["loyalty"] = get_numeric("loyalty", 6)
        criteria_scores["chemical_stability"] = get_numeric("chemical_stability", 7)
        
        # Calculate weighted scores
        total_score = 0.0
        for criterion, config in self.criteria.items():
            score = criteria_scores.get(criterion, 5)
            weighted = (score / config["max"]) * config["weight"]
            weighted_scores[criterion] = round(weighted, 2)
            total_score += weighted
        
        # Normalize to 10-point scale
        final_score = (total_score / self.total_weight) * 10
        
        # Determine pastille (visual indicator)
        if final_score >= 7.5:
            pastille = "green"
            pastille_label = "🟢 Attraction forte"
        elif final_score >= 5.0:
            pastille = "yellow"
            pastille_label = "🟡 Attraction modérée"
        else:
            pastille = "red"
            pastille_label = "🔴 Attraction faible"
        
        return ScoringResult(
            total_score=round(final_score, 1),
            pastille=pastille,
            pastille_label=pastille_label,
            criteria_scores=criteria_scores,
            weighted_scores=weighted_scores
        )
    
    def get_criteria_weights(self) -> Dict[str, int]:
        """Get all criteria with their weights"""
        return {name: config["weight"] for name, config in self.criteria.items()}
    
    def get_criteria_list(self) -> List[Dict[str, Any]]:
        """Get full criteria list with configurations"""
        return [
            {"name": name, **config}
            for name, config in self.criteria.items()
        ]
    
    def calculate_quick_score(self, rainproof: bool, feed_proof: bool, certified: bool, 
                              attraction_days: int, olfactory_power: float) -> float:
        """
        Quick score calculation based on key criteria.
        Useful for fast comparisons.
        """
        # Simplified scoring for key factors
        score = 0.0
        
        # Attraction days (15% weight)
        score += min(attraction_days, 60) / 60 * 1.5
        
        # Olfactory power (12% weight)
        score += (olfactory_power / 10) * 1.2
        
        # Rainproof (8% weight)
        score += 0.8 if rainproof else 0.24
        
        # Feed proof (7% weight)
        score += 0.7 if feed_proof else 0.35
        
        # Certified (6% weight)
        score += 0.6 if certified else 0.24
        
        # Normalize to base remaining criteria average
        remaining_weight = 10 - (1.5 + 1.2 + 0.8 + 0.7 + 0.6)
        score += remaining_weight * 0.6  # Assume average score of 6/10 for others
        
        return round(score, 1)
