/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Page temporaire pour tester les composants BIONIC V5.
 * À SUPPRIMER après validation.
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import { BIONIC_COLORS } from '@/config/bionic-colors';

// Données de test simulant WaypointAnalysisService
const MOCK_ANALYSIS_DATA = {
  analysis_id: "WPA-20251215143022-0001",
  calculated_at: new Date().toISOString(),
  
  // Scores principaux
  unified_score: 72.5,
  unified_level: "good",
  fused_heatmap_score: 68.3,
  wqs_score: 75.0,
  
  // Légalité
  is_legal_period: true,
  legal_status: "legal",
  legal_window: {
    date: "2025-06-15",
    legal_start: "05:12",
    legal_end: "21:18",
    sunrise: "05:42",
    sunset: "20:48",
    duration_hours: 16.1,
    duration_formatted: "16h06min"
  },
  
  // Breakdown des scores (9 catégories)
  score_breakdown: [
    { category: "probability", raw_value: 75.2, weight: 0.15, level: "good" },
    { category: "habitat", raw_value: 82.1, weight: 0.12, level: "excellent" },
    { category: "pressure", raw_value: 58.4, weight: 0.10, level: "moderate" },
    { category: "weather", raw_value: 71.0, weight: 0.12, level: "good" },
    { category: "behavior", raw_value: 68.5, weight: 0.11, level: "good" },
    { category: "multifactor", raw_value: 65.3, weight: 0.10, level: "good" },
    { category: "density", raw_value: 78.9, weight: 0.10, level: "good" },
    { category: "risk", raw_value: 84.2, weight: 0.10, level: "excellent" },
    { category: "mobility", raw_value: 62.1, weight: 0.10, level: "good" }
  ],
  
  // Analyses locales
  local_analysis: {
    mobility: { mobility_score: 62.1, corridor_proximity_km: 0.8 },
    pressure: { pressure_score: 58.4, hunting_activity_index: 41.6 },
    density: { density_score: 78.9, population_trend: "stable" },
    risk: { safety_score: 84.2, risk_level: "low" }
  },
  
  // Facteurs
  insights: {
    positive_factors: [
      "Période légale de chasse",
      "Habitat de qualité supérieure",
      "Faible niveau de risque",
      "Densité de population favorable"
    ],
    negative_factors: [
      "Pression de chasse modérée dans le secteur",
      "Mobilité animale réduite en milieu de journée"
    ]
  },
  
  // Recommandations
  recommendations: [
    "Période optimale: Aube (05:12-07:42)",
    "Meilleur hotspot: Zone Nord-Est (2.3km NE, score: 85)",
    "Conditions favorables pour le cerf"
  ],
  
  // Métadonnées
  metadata: {
    calculation_time_ms: 156.3,
    version: "BIONIC-V5-ULTIME-WPA-1.0"
  }
};

// Données pour période illégale
const MOCK_ILLEGAL_DATA = {
  ...MOCK_ANALYSIS_DATA,
  analysis_id: "WPA-20251215020000-0002",
  unified_score: 0,
  unified_level: "very_poor",
  fused_heatmap_score: 0,
  is_legal_period: false,
  legal_status: "illegal",
  insights: {
    positive_factors: [],
    negative_factors: [
      "HORS HEURES LÉGALES - Analyse neutralisée",
      "Chasse non autorisée à cette heure"
    ]
  },
  recommendations: [
    "CHASSE NON AUTORISÉE - Attendez les heures légales"
  ]
};

const BionicAnalysisDemoPage = () => {
  const [showIllegal, setShowIllegal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  };
  
  const currentData = showIllegal ? MOCK_ILLEGAL_DATA : MOCK_ANALYSIS_DATA;
  
  return (
    <div 
      className="min-h-screen p-6"
      style={{ backgroundColor: BIONIC_COLORS.black.base }}
    >
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 
            className="text-2xl font-bold mb-2"
            style={{ color: BIONIC_COLORS.gold.primary }}
          >
            BIONIC V5 - Demo
          </h1>
          <p className="text-gray-400 text-sm">
            HuntPlanAnalysisPanel Component
          </p>
        </div>
        
        {/* Toggle */}
        <div className="flex justify-center gap-4 mb-6">
          <button
            onClick={() => setShowIllegal(false)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              !showIllegal 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                : 'bg-gray-800 text-gray-400'
            }`}
          >
            Période Légale
          </button>
          <button
            onClick={() => setShowIllegal(true)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              showIllegal 
                ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
                : 'bg-gray-800 text-gray-400'
            }`}
          >
            Hors Heures
          </button>
        </div>
        
        {/* Component */}
        <HuntPlanAnalysisPanel
          waypointId="WP-TEST-001"
          waypointName="Waypoint Test - Zone Nord"
          analysisData={currentData}
          isLoading={isLoading}
          onRefresh={handleRefresh}
          onWaypointChange={() => alert('Changer de waypoint')}
        />
        
        {/* Empty State Demo */}
        <div className="mt-8">
          <p className="text-gray-500 text-xs text-center mb-4">État vide (sans waypoint)</p>
          <HuntPlanAnalysisPanel
            waypointId={null}
            waypointName={null}
            analysisData={null}
            isLoading={false}
            onWaypointChange={() => alert('Sélectionner un waypoint')}
          />
        </div>
      </div>
    </div>
  );
};

export default BionicAnalysisDemoPage;
