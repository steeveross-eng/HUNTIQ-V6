/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Phases 5.1, 5.2, 5.3, 5.4
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import WaypointSelector from '@/components/bionic/WaypointSelector';
import EnrichedHotspotPopup from '@/components/bionic/EnrichedHotspotPopup';
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

// Hotspots de test pour le popup
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
    positiveFactors: [
      'Excellente visibilité',
      'Corridor de passage fréquenté',
      'Source d\'eau à proximité'
    ],
    negativeFactors: [
      'Accès difficile par temps humide'
    ],
    recommendation: 'Position idéale pour l\'aube. Arrivez 30 minutes avant le lever du soleil pour une installation silencieuse.'
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
    risks: ['Zone fréquentée le week-end', 'Sentier de randonnée proche'],
    pressureLevel: 'moderate',
    pressureScore: 52,
    positiveFactors: [
      'Transition habitat favorable',
      'Zone de gagnage identifiée'
    ],
    negativeFactors: [
      'Pression de chasse modérée',
      'Mobilité réduite en journée'
    ],
    recommendation: 'Privilégier les jours de semaine. Crépuscule recommandé pour cette zone.'
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
    risks: ['Terrain instable', 'Accès limité', 'Zone inondable'],
    pressureLevel: 'high',
    pressureScore: 35,
    positiveFactors: [
      'Présence confirmée d\'orignal'
    ],
    negativeFactors: [
      'Accès très difficile',
      'Risque de sécurité élevé',
      'Forte pression de chasse'
    ],
    recommendation: 'Zone déconseillée actuellement. Envisager comme alternative en période sèche uniquement.'
  }
];

// Contexte du waypoint (heures légales liées au waypoint sélectionné)
const getWaypointContext = (waypointId) => {
  const waypoint = MOCK_WAYPOINTS.find(wp => wp.id === waypointId);
  return {
    waypointId,
    waypointName: waypoint?.name || 'Waypoint non sélectionné',
    legalStart: '05:12',
    legalEnd: '21:18',
    legalDuration: '16h06',
    isCurrentlyLegal: true // Simulé - serait calculé dynamiquement en production
  };
};

const BionicAnalysisDemoPage = () => {
  const [selectedWaypointId, setSelectedWaypointId] = useState('WP-001');
  const [isLoading, setIsLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('popups'); // 'main' | 'charts' | 'popups'
  const [selectedHotspotIndex, setSelectedHotspotIndex] = useState(0);
  
  const waypointContext = getWaypointContext(selectedWaypointId);
  
  const handleWaypointSelect = (waypointId) => {
    setIsLoading(true);
    setSelectedWaypointId(waypointId);
    setTimeout(() => setIsLoading(false), 800);
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
            Phase 5.4: Popups Enrichis
          </p>
          
          {/* Section Tabs */}
          <div className="flex justify-center gap-2 flex-wrap">
            <button
              onClick={() => setActiveSection('main')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === 'main' ? 'text-white' : 'bg-gray-800 text-gray-400'
              }`}
              style={activeSection === 'main' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
            >
              Composants Principaux
            </button>
            <button
              onClick={() => setActiveSection('charts')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === 'charts' ? 'text-white' : 'bg-gray-800 text-gray-400'
              }`}
              style={activeSection === 'charts' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
            >
              Graphiques Premium
            </button>
            <button
              onClick={() => setActiveSection('popups')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === 'popups' ? 'text-white' : 'bg-gray-800 text-gray-400'
              }`}
              style={activeSection === 'popups' ? { backgroundColor: BIONIC_COLORS.gold.primary } : {}}
            >
              Popups Enrichis
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
              isLoading={isLoading}
              onRefresh={() => {}}
            />
          </div>
        )}
        
        {/* Section: Graphiques Premium */}
        {activeSection === 'charts' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ScoreRadarPanel scores={MOCK_SCORES} globalScore={72} />
              <ScoreDistributionPanel scores={MOCK_SCORES} stats={{ median: 70, stdDev: 14.2, min: 42, max: 92 }} />
            </div>
            <OptimalWindowsTimeline windows={MOCK_WINDOWS} legalStart="05:12" legalEnd="21:18" legalDuration="16h06" />
          </div>
        )}
        
        {/* Section: Popups Enrichis */}
        {activeSection === 'popups' && (
          <div className="space-y-6">
            {/* Sélecteur de hotspot */}
            <div className="flex justify-center gap-2 flex-wrap">
              {MOCK_HOTSPOTS.map((hs, index) => (
                <button
                  key={hs.id}
                  onClick={() => setSelectedHotspotIndex(index)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedHotspotIndex === index ? 'text-white' : 'bg-gray-800 text-gray-400'
                  }`}
                  style={selectedHotspotIndex === index ? { 
                    backgroundColor: hs.quality === 'favorable' ? BIONIC_COLORS.green.primary :
                                     hs.quality === 'moderate' ? BIONIC_COLORS.gold.primary :
                                     BIONIC_COLORS.red.primary
                  } : {}}
                >
                  {hs.quality === 'favorable' ? 'Favorable' : 
                   hs.quality === 'moderate' ? 'Modéré' : 'Défavorable'}
                </button>
              ))}
            </div>
            
            {/* Affichage des 3 popups côte à côte */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {MOCK_HOTSPOTS.map((hotspot, index) => (
                <div 
                  key={hotspot.id}
                  className={`transition-all duration-300 ${
                    selectedHotspotIndex === index ? 'ring-2 ring-offset-2 ring-offset-black rounded-lg' : 'opacity-70'
                  }`}
                  style={{ 
                    ringColor: hotspot.quality === 'favorable' ? BIONIC_COLORS.green.primary :
                               hotspot.quality === 'moderate' ? BIONIC_COLORS.gold.primary :
                               BIONIC_COLORS.red.primary
                  }}
                >
                  <div className="text-center mb-2">
                    <span className="text-xs text-gray-500">
                      {hotspot.quality === 'favorable' ? 'Hotspot Favorable' : 
                       hotspot.quality === 'moderate' ? 'Hotspot Modéré' : 'Hotspot Défavorable'}
                    </span>
                  </div>
                  <EnrichedHotspotPopup
                    hotspot={hotspot}
                    waypointContext={waypointContext}
                    onClose={() => {}}
                    onAnalyze={(hs) => alert(`Analyse de: ${hs.name}`)}
                  />
                </div>
              ))}
            </div>
            
            {/* Info contextuelle */}
            <div 
              className="p-4 rounded-lg text-center"
              style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
            >
              <p className="text-sm text-gray-400">
                Les heures légales affichées ({waypointContext.legalStart} - {waypointContext.legalEnd}) 
                sont liées au waypoint: <span className="text-white font-medium">{waypointContext.waypointName}</span>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BionicAnalysisDemoPage;
