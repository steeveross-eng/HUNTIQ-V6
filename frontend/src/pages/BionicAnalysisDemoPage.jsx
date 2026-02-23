/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Page temporaire pour tester les composants BIONIC V5.
 * Phases 5.1, 5.2, 5.3
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import WaypointSelector from '@/components/bionic/WaypointSelector';
import { 
  ScoreRadarPanel, 
  OptimalWindowsTimeline, 
  ScoreDistributionPanel 
} from '@/components/bionic/charts';
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
  }
];

// Données de scores pour les graphiques
const MOCK_SCORES = [
  { category: 'probability', score: 75, trend: 'up' },
  { category: 'habitat', score: 92, trend: 'up' },
  { category: 'pressure', score: 58, trend: 'down' },
  { category: 'weather', score: 71 },
  { category: 'behavior', score: 68 },
  { category: 'multifactor', score: 65 },
  { category: 'density', score: 79, trend: 'up' },
  { category: 'risk', score: 84 },
  { category: 'mobility', score: 42, trend: 'down' }
];

// Fenêtres optimales
const MOCK_WINDOWS = [
  { period: 'dawn', start: '05:12', end: '07:42', quality: 'excellent', score: 92, is_legal: true },
  { period: 'morning', start: '08:00', end: '11:30', quality: 'good', score: 75, is_legal: true },
  { period: 'afternoon', start: '12:00', end: '17:00', quality: 'moderate', score: 55, is_legal: true },
  { period: 'dusk', start: '18:30', end: '21:18', quality: 'excellent', score: 88, is_legal: true }
];

// Données d'analyse
const getAnalysisDataForWaypoint = (waypointId) => {
  const waypoint = MOCK_WAYPOINTS.find(wp => wp.id === waypointId);
  if (!waypoint) return null;
  
  const baseScore = waypoint.score || 70;
  
  return {
    analysis_id: `WPA-${Date.now()}-0001`,
    calculated_at: new Date().toISOString(),
    unified_score: baseScore,
    unified_level: baseScore >= 80 ? "good" : baseScore >= 60 ? "moderate" : "poor",
    fused_heatmap_score: baseScore - 5,
    wqs_score: baseScore + 3,
    is_legal_period: true,
    legal_status: "legal",
    legal_window: {
      legal_start: "05:12",
      legal_end: "21:18",
      duration_hours: 16.1,
      duration_formatted: "16h06min"
    },
    score_breakdown: MOCK_SCORES.map(s => ({
      category: s.category,
      raw_value: s.score + (baseScore - 70) / 2,
      weight: 0.11,
      level: "good"
    })),
    insights: {
      positive_factors: [
        "Période légale de chasse",
        `Excellent habitat pour ${waypoint.species}`,
        "Faible niveau de risque"
      ],
      negative_factors: [
        "Pression de chasse modérée",
        "Mobilité réduite en journée"
      ]
    },
    recommendations: [
      "Période optimale: Aube (05:12-07:42)",
      `Zone idéale pour ${waypoint.species}`,
      `Score de ${baseScore} - Conditions favorables`
    ],
    metadata: {
      calculation_time_ms: 142.5,
      version: "BIONIC-V5-ULTIME-WPA-1.0"
    }
  };
};

const BionicAnalysisDemoPage = () => {
  const [selectedWaypointId, setSelectedWaypointId] = useState('WP-001');
  const [isLoading, setIsLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('charts'); // 'main' | 'charts'
  
  const selectedWaypoint = MOCK_WAYPOINTS.find(wp => wp.id === selectedWaypointId);
  const analysisData = selectedWaypointId ? getAnalysisDataForWaypoint(selectedWaypointId) : null;
  
  const handleWaypointSelect = (waypointId) => {
    setIsLoading(true);
    setSelectedWaypointId(waypointId);
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
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 
            className="text-2xl font-bold mb-2"
            style={{ color: BIONIC_COLORS.gold.primary }}
          >
            BIONIC V5 - Demo Components
          </h1>
          <p className="text-gray-400 text-sm mb-4">
            Phase 5.3: Graphiques Analytiques Premium
          </p>
          
          {/* Section Tabs */}
          <div className="flex justify-center gap-2">
            <button
              onClick={() => setActiveSection('main')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === 'main' 
                  ? 'text-white' 
                  : 'bg-gray-800 text-gray-400'
              }`}
              style={activeSection === 'main' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
            >
              Composants Principaux
            </button>
            <button
              onClick={() => setActiveSection('charts')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === 'charts' 
                  ? 'text-white' 
                  : 'bg-gray-800 text-gray-400'
              }`}
              style={activeSection === 'charts' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
            >
              Graphiques Premium
            </button>
          </div>
        </div>
        
        {/* Section: Composants Principaux */}
        {activeSection === 'main' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <WaypointSelector
              waypoints={MOCK_WAYPOINTS}
              selectedWaypointId={selectedWaypointId}
              onSelectWaypoint={handleWaypointSelect}
              isLoading={false}
            />
            <HuntPlanAnalysisPanel
              waypointId={selectedWaypointId}
              waypointName={selectedWaypoint?.name}
              analysisData={analysisData}
              isLoading={isLoading}
              onRefresh={handleRefresh}
              onWaypointChange={() => {}}
            />
          </div>
        )}
        
        {/* Section: Graphiques Premium */}
        {activeSection === 'charts' && (
          <div className="space-y-6">
            {/* Row 1: Profil Analytique (full width) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ScoreRadarPanel
                scores={MOCK_SCORES}
                globalScore={72}
              />
              <ScoreDistributionPanel
                scores={MOCK_SCORES}
                stats={{
                  median: 70,
                  stdDev: 14.2,
                  min: 42,
                  max: 92
                }}
              />
            </div>
            
            {/* Row 2: Timeline (full width) */}
            <OptimalWindowsTimeline
              windows={MOCK_WINDOWS}
              legalStart="05:12"
              legalEnd="21:18"
              legalDuration="16h06"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default BionicAnalysisDemoPage;
