"""
BIONIC™ Opportunity Engine Service
===================================
Phase 11-15: Module Immobilier

Moteur d'analyse d'opportunités d'investissement immobilier.
Identifie les propriétés sous-évaluées avec fort potentiel BIONIC.
"""

from typing import Dict, List, Any
from datetime import datetime
from .scoring_service import RealEstateScoringService


class OpportunityEngineService:
    """
    Moteur d'opportunités d'investissement immobilier.
    
    Analyse les propriétés pour identifier:
    - Propriétés sous-évaluées
    - Fort potentiel de chasse non exploité
    - Opportunités d'investissement
    """
    
    # Market averages per region (placeholder - would be dynamic)
    MARKET_AVERAGES = {
        'quebec': {
            'terrain': 2.50,  # $/m²
            'chalet': 150.00,
            'ferme': 5.00,
            'lot_boise': 1.50
        },
        'default': {
            'terrain': 3.00,
            'chalet': 175.00,
            'ferme': 6.00,
            'lot_boise': 2.00
        }
    }
    
    # Opportunity thresholds
    OPPORTUNITY_THRESHOLDS = {
        'excellent': {'discount': 30, 'score': 80},
        'very_good': {'discount': 20, 'score': 70},
        'good': {'discount': 10, 'score': 60},
        'average': {'discount': 0, 'score': 50},
        'below_average': {'discount': -10, 'score': 0}
    }
    
    @classmethod
    def analyze_opportunity(
        cls,
        property_data: Dict[str, Any],
        region: str = 'quebec'
    ) -> Dict[str, Any]:
        """
        Analyse une propriété pour identifier son niveau d'opportunité.
        
        Args:
            property_data: Données de la propriété
            region: Région pour comparaison de marché
            
        Returns:
            Dict avec l'analyse d'opportunité
        """
        price = property_data.get('price', 0)
        area_m2 = property_data.get('area_m2', 1)
        property_type = property_data.get('property_type', 'terrain')
        coordinates = property_data.get('coordinates', {'lat': 46.8, 'lng': -71.2})
        features = property_data.get('features', {})
        
        # Calculate price per m²
        price_per_m2 = price / area_m2 if area_m2 > 0 else 0
        
        # Get market average
        market_data = cls.MARKET_AVERAGES.get(region, cls.MARKET_AVERAGES['default'])
        market_avg = market_data.get(property_type, market_data['terrain'])
        
        # Calculate discount percentage
        if market_avg > 0:
            discount_pct = ((market_avg - price_per_m2) / market_avg) * 100
        else:
            discount_pct = 0
        
        # Get BIONIC score
        score_data = RealEstateScoringService.calculate_property_score(
            coordinates, area_m2, features
        )
        bionic_score = score_data.get('overall_score', 50)
        
        # Determine opportunity level
        opportunity_level = cls._determine_opportunity_level(discount_pct, bionic_score)
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(
            property_data, score_data, discount_pct
        )
        
        # Calculate investment potential
        investment_potential = cls._calculate_investment_potential(
            discount_pct, bionic_score, area_m2
        )
        
        return {
            'property_id': property_data.get('id', ''),
            'property_title': property_data.get('title', 'Propriété'),
            'opportunity_level': opportunity_level,
            'price_per_m2': round(price_per_m2, 2),
            'market_average_per_m2': market_avg,
            'bionic_score': bionic_score,
            'discount_percentage': round(discount_pct, 1),
            'investment_potential': investment_potential,
            'recommended_actions': recommendations,
            'score_breakdown': score_data,
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    @classmethod
    def find_top_opportunities(
        cls,
        properties: List[Dict[str, Any]],
        region: str = 'quebec',
        limit: int = 10,
        min_score: float = 0,
        min_discount: float = -100
    ) -> List[Dict[str, Any]]:
        """
        Trouve les meilleures opportunités parmi une liste de propriétés.
        
        Args:
            properties: Liste des propriétés à analyser
            region: Région pour comparaison
            limit: Nombre max de résultats
            min_score: Score BIONIC minimum
            min_discount: Rabais minimum en %
            
        Returns:
            Liste des meilleures opportunités triées
        """
        opportunities = []
        
        for prop in properties:
            try:
                analysis = cls.analyze_opportunity(prop, region)
                
                # Apply filters
                if analysis['bionic_score'] < min_score:
                    continue
                if analysis['discount_percentage'] < min_discount:
                    continue
                
                opportunities.append(analysis)
            except Exception:
                continue
        
        # Sort by opportunity score (combination of discount and bionic score)
        opportunities.sort(
            key=lambda x: x['discount_percentage'] * 0.4 + x['bionic_score'] * 0.6,
            reverse=True
        )
        
        return opportunities[:limit]
    
    @classmethod
    def _determine_opportunity_level(
        cls, 
        discount_pct: float, 
        bionic_score: float
    ) -> str:
        """Détermine le niveau d'opportunité."""
        for level, thresholds in cls.OPPORTUNITY_THRESHOLDS.items():
            if discount_pct >= thresholds['discount'] and bionic_score >= thresholds['score']:
                return level
        return 'below_average'
    
    @classmethod
    def _generate_recommendations(
        cls,
        property_data: Dict,
        score_data: Dict,
        discount_pct: float
    ) -> List[str]:
        """Génère des recommandations d'action."""
        recommendations = []
        
        bionic_score = score_data.get('overall_score', 50)
        
        # Price-based recommendations
        if discount_pct >= 20:
            recommendations.append("Prix très attractif - Agir rapidement")
        elif discount_pct >= 10:
            recommendations.append("Prix sous le marché - Bonne opportunité")
        elif discount_pct < 0:
            recommendations.append("Négociation recommandée sur le prix")
        
        # Score-based recommendations
        if bionic_score >= 80:
            recommendations.append("Excellent potentiel de chasse - Propriété premium")
        elif bionic_score >= 60:
            recommendations.append("Bon potentiel - Terrain adapté à la chasse")
        
        # Specific score improvements
        if score_data.get('water_score', 100) < 40:
            recommendations.append("Envisager aménagement point d'eau")
        if score_data.get('access_score', 100) < 40:
            recommendations.append("Vérifier les accès et servitudes")
        if score_data.get('habitat_score', 100) < 40:
            recommendations.append("Potentiel d'amélioration de l'habitat")
        
        # Area-based recommendations
        area = property_data.get('area_m2', 0)
        if area >= 500000:  # 50+ hectares
            recommendations.append("Grande superficie - Potentiel camp/pourvoirie")
        elif area >= 100000:  # 10+ hectares
            recommendations.append("Superficie idéale pour chasse personnelle")
        
        return recommendations[:5]  # Max 5 recommendations
    
    @classmethod
    def _calculate_investment_potential(
        cls,
        discount_pct: float,
        bionic_score: float,
        area_m2: float
    ) -> str:
        """Calcule le potentiel d'investissement global."""
        # Weighted score
        investment_score = (
            discount_pct * 0.35 +
            bionic_score * 0.45 +
            min(20, (area_m2 / 50000) * 20)  # Area bonus up to 20 points
        )
        
        if investment_score >= 70:
            return "Très élevé"
        elif investment_score >= 50:
            return "Élevé"
        elif investment_score >= 30:
            return "Modéré"
        elif investment_score >= 10:
            return "Faible"
        else:
            return "Très faible"


# Export
__all__ = ['OpportunityEngineService']
