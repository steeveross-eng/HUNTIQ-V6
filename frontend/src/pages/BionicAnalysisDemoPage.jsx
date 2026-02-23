/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Phases 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import WaypointSelector from '@/components/bionic/WaypointSelector';
import EnrichedHotspotPopup from '@/components/bionic/EnrichedHotspotPopup';
import HotspotListPanel from '@/components/bionic/HotspotListPanel';
import MapLegend from '@/components/bionic/MapLegend';
import { 
  ScoreRadarPanel, 
  OptimalWindowsTimeline, 
  ScoreDistributionPanel 
} from '@/components/bionic/charts';
import { BIONIC_COLORS } from '@/config/bionic-colors';

// Liste de waypoints de test
const MOCK_WAYPOINTS = [
  { id: 'WP-001', name: 'Zone Nord - Affût Principal', type: 'hunting', latitude: 46.8139, longitude: -71.2080, score: 85, species: 'Cerf' },
  { id: 'WP-002', name: 'Caméra Trail #1', type: 'camera', latitude: 46.8250, longitude: -71.1950, score: 72, species: 'Orignal' }
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

// Hotspots de test complets
const MOCK_HOTSPOTS = [
  {
    id: 'HS-001',
    name: 'Hotspot Nord-Est - Zone Clairière',
    score: 85,
    quality: 'favorable',
    distance: 2.3,
    direction: 'NE',
    bearing: 45,
    habitat: 'clearing',
    habitatCoverage: 72,
    riskLevel: 'low',
    risks: ['Terrain légèrement accidenté'],
    pressureLevel: 'low',
    pressureScore: 78,
    isLegal: true,
    positiveFactors: ['Excellente visibilité', 'Corridor de passage fréquenté'],
    negativeFactors: ['Accès difficile par temps humide'],
    recommendation: 'Position idéale pour l\'aube.'
  },
  {
    id: 'HS-002',
    name: 'Hotspot Sud - Lisière Forestière',
    score: 62,
    quality: 'moderate',
    distance: 4.1,
    direction: 'S',
    bearing: 180,
    habitat: 'edge',
    habitatCoverage: 58,
    riskLevel: 'moderate',
    risks: ['Zone fréquentée le week-end'],
    pressureLevel: 'moderate',
    pressureScore: 52,
    isLegal: true,
    positiveFactors: ['Transition habitat favorable'],
    negativeFactors: ['Pression de chasse modérée'],
    recommendation: 'Privilégier les jours de semaine.'
  },
  {
    id: 'HS-003',
    name: 'Hotspot Ouest - Zone Humide',
    score: 38,
    quality: 'unfavorable',
    distance: 5.8,
    direction: 'W',
    bearing: 270,
    habitat: 'wetland',
    habitatCoverage: 45,
    riskLevel: 'high',
    risks: ['Terrain instable', 'Accès limité'],
    pressureLevel: 'high',
    pressureScore: 35,
    isLegal: true,
    positiveFactors: ['Présence confirmée d\'orignal'],
    negativeFactors: ['Accès très difficile', 'Risque de sécurité élevé'],
    recommendation: 'Zone déconseillée actuellement.'
  },
  {
    id: 'HS-004',
    name: 'Hotspot Nord - Forêt Dense',
    score: 78,
    quality: 'favorable',
    distance: 1.8,
    direction: 'N',
    bearing: 0,
    habitat: 'forest',
    habitatCoverage: 85,
    riskLevel: 'low',
    risks: [],
    pressureLevel: 'low',
    pressureScore: 82,
    isLegal: true,
    positiveFactors: ['Couvert forestier excellent', 'Faible pression'],
    negativeFactors: ['Visibilité réduite'],
    recommendation: 'Excellent pour l\'approche silencieuse.'
  },
  {
    id: 'HS-005',
    name: 'Hotspot Est - Zone Mixte',
    score: 55,
    quality: 'moderate',
    distance: 3.2,
    direction: 'E',
    bearing: 90,
    habitat: 'mixed',
    habitatCoverage: 62,
    riskLevel: 'moderate',
    risks: ['Proximité route secondaire'],
    pressureLevel: 'moderate',
    pressureScore: 48,
    isLegal: false,
    positiveFactors: ['Diversité d\'habitats'],
    negativeFactors: ['Bruit routier occasionnel'],
    recommendation: 'À éviter aux heures de pointe.'
  },
  {
    id: 'HS-006',
    name: 'Hotspot Sud-Est - Clairière',
    score: 91,
    quality: 'favorable',
    distance: 2.9,
    direction: 'SE',
    bearing: 135,
    habitat: 'clearing',
    habitatCoverage: 78,
    riskLevel: 'low',
    risks: [],
    pressureLevel: 'low',
    pressureScore: 88,
    isLegal: true,
    positiveFactors: ['Score exceptionnel', 'Conditions optimales'],
    negativeFactors: [],
    recommendation: 'Meilleur hotspot de la zone!'
  }
];

// Contexte du waypoint
const getWaypointContext = (waypointId) => {
  const waypoint = MOCK_WAYPOINTS.find(wp => wp.id === waypointId);
  return {
    waypointId,
    waypointName: waypoint?.name || 'Waypoint non sélectionné',
    legalStart: '05:12',
    legalEnd: '21:18',
    legalDuration: '16h06',
    isCurrentlyLegal: true
  };
};

const BionicAnalysisDemoPage = () => {
  const [selectedWaypointId, setSelectedWaypointId] = useState('WP-001');
  const [selectedHotspotId, setSelectedHotspotId] = useState(null);
  const [hoveredHotspot, setHoveredHotspot] = useState(null);
  const [activeSection, setActiveSection] = useState('legend'); // 'main' | 'charts' | 'popups' | 'list' | 'legend'
  const [isLegalPeriod, setIsLegalPeriod] = useState(true); // Pour la démo de la légende
  
  const waypointContext = getWaypointContext(selectedWaypointId);
  const selectedHotspot = MOCK_HOTSPOTS.find(h => h.id === selectedHotspotId);
  
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
            Phase 5.5: Tri/Filtrage Intelligent
          </p>
          
          {/* Section Tabs */}
          <div className="flex justify-center gap-2 flex-wrap">
            {[
              { key: 'legend', label: 'Légende (5.6)' },
              { key: 'main', label: 'Principaux' },
              { key: 'charts', label: 'Graphiques' },
              { key: 'popups', label: 'Popups' },
              { key: 'list', label: 'Liste Hotspots' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveSection(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeSection === tab.key ? 'text-white' : 'bg-gray-800 text-gray-400'
                }`}
                style={activeSection === tab.key ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
        
        {/* Section: Liste Hotspots */}
        {activeSection === 'list' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Liste avec tri/filtrage */}
            <HotspotListPanel
              hotspots={MOCK_HOTSPOTS}
              selectedHotspotId={selectedHotspotId}
              onSelectHotspot={(h) => setSelectedHotspotId(h.id)}
              onHoverHotspot={setHoveredHotspot}
            />
            
            {/* Popup du hotspot sélectionné */}
            <div>
              {selectedHotspot ? (
                <EnrichedHotspotPopup
                  hotspot={selectedHotspot}
                  waypointContext={waypointContext}
                  onClose={() => setSelectedHotspotId(null)}
                  onAnalyze={(h) => alert(`Analyse de: ${h.name}`)}
                />
              ) : (
                <div 
                  className="rounded-lg p-8 text-center"
                  style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
                >
                  <div 
                    className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                    style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
                  >
                    <svg className="w-8 h-8" style={{ color: BIONIC_COLORS.gray[500] }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                      <circle cx="12" cy="10" r="3"/>
                    </svg>
                  </div>
                  <p className="text-white font-medium mb-1">Aucun hotspot sélectionné</p>
                  <p className="text-sm text-gray-500">
                    Cliquez sur un hotspot dans la liste pour voir ses détails
                  </p>
                </div>
              )}
              
              {/* Info survol */}
              {hoveredHotspot && hoveredHotspot.id !== selectedHotspotId && (
                <div 
                  className="mt-4 p-3 rounded-lg"
                  style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
                >
                  <p className="text-xs text-gray-400">
                    Survol: <span className="text-white">{hoveredHotspot.name}</span>
                    {' '} - Score: <span style={{ color: getScoreColor(hoveredHotspot.score) }}>{Math.round(hoveredHotspot.score / 10)}/10</span>
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Section: Composants Principaux */}
        {activeSection === 'main' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <WaypointSelector
              waypoints={MOCK_WAYPOINTS}
              selectedWaypointId={selectedWaypointId}
              onSelectWaypoint={setSelectedWaypointId}
            />
            <HuntPlanAnalysisPanel
              waypointId={selectedWaypointId}
              waypointName={MOCK_WAYPOINTS.find(wp => wp.id === selectedWaypointId)?.name}
              analysisData={{
                unified_score: 72,
                unified_level: 'good',
                is_legal_period: true,
                legal_window: { legal_start: '05:12', legal_end: '21:18', duration_hours: 16.1 },
                score_breakdown: MOCK_SCORES,
                recommendations: ['Période optimale: Aube'],
                metadata: { calculation_time_ms: 142 }
              }}
              onRefresh={() => {}}
            />
          </div>
        )}
        
        {/* Section: Graphiques */}
        {activeSection === 'charts' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ScoreRadarPanel scores={MOCK_SCORES} globalScore={72} />
              <ScoreDistributionPanel scores={MOCK_SCORES} stats={{ median: 70, stdDev: 14.2, min: 42, max: 92 }} />
            </div>
            <OptimalWindowsTimeline windows={[
              { period: 'dawn', start: '05:12', end: '07:42', quality: 'excellent', score: 92 },
              { period: 'morning', start: '08:00', end: '11:30', quality: 'good', score: 75 },
              { period: 'dusk', start: '18:30', end: '21:18', quality: 'excellent', score: 88 }
            ]} legalStart="05:12" legalEnd="21:18" legalDuration="16h06" />
          </div>
        )}
        
        {/* Section: Popups */}
        {activeSection === 'popups' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {MOCK_HOTSPOTS.slice(0, 3).map(hotspot => (
              <EnrichedHotspotPopup
                key={hotspot.id}
                hotspot={hotspot}
                waypointContext={waypointContext}
                onAnalyze={(h) => alert(`Analyse de: ${h.name}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function
const getScoreColor = (score) => {
  if (score >= 80) return BIONIC_COLORS.green.primary;
  if (score >= 60) return BIONIC_COLORS.gold.primary;
  if (score >= 40) return BIONIC_COLORS.blue.light;
  return BIONIC_COLORS.red.primary;
};

export default BionicAnalysisDemoPage;
