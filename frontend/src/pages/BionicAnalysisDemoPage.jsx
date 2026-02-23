/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Page temporaire pour tester les composants BIONIC V5.
 * À SUPPRIMER après validation.
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import WaypointSelector from '@/components/bionic/WaypointSelector';
import { BIONIC_COLORS } from '@/config/bionic-colors';

// Liste de waypoints de test
const MOCK_WAYPOINTS = [
  {
    id: 'WP-001',
    name: 'Zone Nord - Affût Principal',
    type: 'hunting',
    latitude: 46.8139,
    longitude: -71.2080,
    score: 85,
    species: 'Cerf'
  },
  {
    id: 'WP-002',
    name: 'Caméra Trail #1',
    type: 'camera',
    latitude: 46.8250,
    longitude: -71.1950,
    score: 72,
    species: 'Orignal'
  },
  {
    id: 'WP-003',
    name: 'Point d\'observation Est',
    type: 'observation',
    latitude: 46.8100,
    longitude: -71.1800,
    score: 68,
    species: 'Cerf'
  },
  {
    id: 'WP-004',
    name: 'Zone alimentation Sud',
    type: 'feeding',
    latitude: 46.7950,
    longitude: -71.2200,
    score: 91,
    species: 'Orignal'
  },
  {
    id: 'WP-005',
    name: 'Affût secondaire',
    type: 'blind',
    latitude: 46.8300,
    longitude: -71.2400,
    score: 55,
    species: 'Ours'
  },
  {
    id: 'WP-006',
    name: 'Point GPS personnalisé',
    type: 'custom',
    latitude: 46.8050,
    longitude: -71.1700,
    score: 45,
    species: 'Dindon'
  }
];

// Données de test simulant WaypointAnalysisService
const getAnalysisDataForWaypoint = (waypointId) => {
  const waypoint = MOCK_WAYPOINTS.find(wp => wp.id === waypointId);
  if (!waypoint) return null;
  
  const baseScore = waypoint.score || 70;
  
  return {
    analysis_id: `WPA-${Date.now()}-0001`,
    calculated_at: new Date().toISOString(),
    
    // Scores principaux
    unified_score: baseScore,
    unified_level: baseScore >= 80 ? "good" : baseScore >= 60 ? "moderate" : "poor",
    fused_heatmap_score: baseScore - 5,
    wqs_score: baseScore + 3,
    
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
      { category: "probability", raw_value: baseScore + 2, weight: 0.15, level: "good" },
      { category: "habitat", raw_value: baseScore + 8, weight: 0.12, level: "excellent" },
      { category: "pressure", raw_value: baseScore - 15, weight: 0.10, level: "moderate" },
      { category: "weather", raw_value: baseScore - 2, weight: 0.12, level: "good" },
      { category: "behavior", raw_value: baseScore - 5, weight: 0.11, level: "good" },
      { category: "multifactor", raw_value: baseScore - 8, weight: 0.10, level: "good" },
      { category: "density", raw_value: baseScore + 5, weight: 0.10, level: "good" },
      { category: "risk", raw_value: baseScore + 10, weight: 0.10, level: "excellent" },
      { category: "mobility", raw_value: baseScore - 12, weight: 0.10, level: "moderate" }
    ],
    
    // Facteurs
    insights: {
      positive_factors: [
        "Période légale de chasse",
        `Excellent habitat pour ${waypoint.species}`,
        "Faible niveau de risque"
      ],
      negative_factors: [
        "Pression de chasse modérée dans le secteur",
        "Mobilité animale réduite en milieu de journée"
      ]
    },
    
    // Recommandations
    recommendations: [
      "Période optimale: Aube (05:12-07:42)",
      `Zone idéale pour ${waypoint.species}`,
      `Score de ${baseScore} - Conditions ${baseScore >= 70 ? 'favorables' : 'acceptables'}`
    ],
    
    // Métadonnées
    metadata: {
      calculation_time_ms: 142.5,
      version: "BIONIC-V5-ULTIME-WPA-1.0"
    }
  };
};

const BionicAnalysisDemoPage = () => {
  const [selectedWaypointId, setSelectedWaypointId] = useState('WP-001');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('selector'); // 'selector' | 'panel'
  
  const selectedWaypoint = MOCK_WAYPOINTS.find(wp => wp.id === selectedWaypointId);
  const analysisData = selectedWaypointId ? getAnalysisDataForWaypoint(selectedWaypointId) : null;
  
  const handleWaypointSelect = (waypointId) => {
    setIsLoading(true);
    setSelectedWaypointId(waypointId);
    // Simuler un délai de chargement
    setTimeout(() => setIsLoading(false), 800);
  };
  
  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };
  
  return (
    <div 
      className="min-h-screen p-4 md:p-6"
      style={{ backgroundColor: BIONIC_COLORS.black.base }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 
            className="text-2xl font-bold mb-2"
            style={{ color: BIONIC_COLORS.gold.primary }}
          >
            BIONIC V5 - Demo Components
          </h1>
          <p className="text-gray-400 text-sm">
            Phase 5.1: HuntPlanAnalysisPanel | Phase 5.2: WaypointSelector
          </p>
        </div>
        
        {/* Tab Navigation (Mobile) */}
        <div className="flex gap-2 mb-6 md:hidden">
          <button
            onClick={() => setActiveTab('selector')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'selector' 
                ? 'text-white' 
                : 'bg-gray-800 text-gray-400'
            }`}
            style={activeTab === 'selector' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
          >
            Waypoints
          </button>
          <button
            onClick={() => setActiveTab('panel')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'panel' 
                ? 'text-white' 
                : 'bg-gray-800 text-gray-400'
            }`}
            style={activeTab === 'panel' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
          >
            Analyse
          </button>
        </div>
        
        {/* Main Content - Two Columns on Desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Column 1: WaypointSelector */}
          <div className={`${activeTab === 'selector' ? 'block' : 'hidden'} md:block`}>
            <WaypointSelector
              waypoints={MOCK_WAYPOINTS}
              selectedWaypointId={selectedWaypointId}
              onSelectWaypoint={handleWaypointSelect}
              isLoading={false}
            />
          </div>
          
          {/* Column 2: HuntPlanAnalysisPanel */}
          <div className={`${activeTab === 'panel' ? 'block' : 'hidden'} md:block`}>
            <HuntPlanAnalysisPanel
              waypointId={selectedWaypointId}
              waypointName={selectedWaypoint?.name}
              analysisData={analysisData}
              isLoading={isLoading}
              onRefresh={handleRefresh}
              onWaypointChange={() => setActiveTab('selector')}
            />
          </div>
          
        </div>
        
        {/* States Demo Section */}
        <div className="mt-8 pt-8 border-t border-gray-800">
          <h2 className="text-lg font-medium text-white mb-4 text-center">
            États spéciaux
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Empty WaypointSelector */}
            <div>
              <p className="text-gray-500 text-xs text-center mb-3">
                WaypointSelector - État vide
              </p>
              <WaypointSelector
                waypoints={[]}
                selectedWaypointId={null}
                onSelectWaypoint={() => {}}
              />
            </div>
            
            {/* Loading WaypointSelector */}
            <div>
              <p className="text-gray-500 text-xs text-center mb-3">
                WaypointSelector - Chargement
              </p>
              <WaypointSelector
                waypoints={MOCK_WAYPOINTS}
                selectedWaypointId={null}
                onSelectWaypoint={() => {}}
                isLoading={true}
              />
            </div>
            
            {/* HuntPlanAnalysisPanel - Empty */}
            <div>
              <p className="text-gray-500 text-xs text-center mb-3">
                HuntPlanAnalysisPanel - Sans waypoint
              </p>
              <HuntPlanAnalysisPanel
                waypointId={null}
                waypointName={null}
                analysisData={null}
                isLoading={false}
                onWaypointChange={() => {}}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BionicAnalysisDemoPage;
