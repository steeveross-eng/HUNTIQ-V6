/**
 * BionicAnalysisDemoPage - Page de démonstration BIONIC V5
 * =========================================================
 * Phases 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.4, 6.5
 */

import React, { useState } from 'react';
import HuntPlanAnalysisPanel from '@/components/bionic/HuntPlanAnalysisPanel';
import WaypointSelector from '@/components/bionic/WaypointSelector';
import EnrichedHotspotPopup from '@/components/bionic/EnrichedHotspotPopup';
import HotspotListPanel from '@/components/bionic/HotspotListPanel';
import MapLegend from '@/components/bionic/MapLegend';
import LayerControlPanel from '@/components/bionic/LayerControlPanel';
import CarteBionic from '@/components/bionic/CarteBionic';
import { AdminBionicHotspots } from '@/components/bionic/admin';
import { 
  ScoreRadarPanel, 
  OptimalWindowsTimeline, 
  ScoreDistributionPanel 
} from '@/components/bionic/charts';
import { BIONIC_COLORS } from '@/config/bionic-colors';
import { toast } from 'sonner';

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

// Hotspots de test complets (format liste)
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

// Hotspots enrichis pour le module Admin (avec données GPS, adresse, terrain)
const MOCK_ADMIN_HOTSPOTS = [
  {
    id: 'HS-001',
    name: 'Hotspot Nord-Est - Zone Clairière',
    score: 8.5,
    latitude: 46.8250,
    longitude: -71.1850,
    address: '123 Chemin du Lac',
    city: 'Saint-Raymond',
    province: 'Québec',
    postalCode: 'G3L 2P5',
    country: 'Canada',
    terrainType: 'private',
    owner: 'Jean Tremblay',
    factors: { habitat: 9.0, pressure: 7.5, coverage: 8.0, water: 8.5, accessibility: 7.0, attractivity: 9.0 },
    notes: 'Zone de passage fréquent au lever du soleil'
  },
  {
    id: 'HS-002',
    name: 'Hotspot Sud - Lisière Forestière',
    score: 6.2,
    latitude: 46.8050,
    longitude: -71.2100,
    address: 'Route 365 Nord',
    city: 'Portneuf',
    province: 'Québec',
    postalCode: 'G0A 2Y0',
    country: 'Canada',
    terrainType: 'zec',
    owner: 'ZEC Batiscan-Neilson',
    factors: { habitat: 6.5, pressure: 5.0, coverage: 6.0, water: 7.0, accessibility: 6.5, attractivity: 6.0 },
    notes: 'Activité accrue en fin de semaine'
  },
  {
    id: 'HS-003',
    name: 'Hotspot Ouest - Zone Humide',
    score: 3.8,
    latitude: 46.8100,
    longitude: -71.2400,
    address: 'Secteur Marais Nord',
    city: 'Lac-Sergent',
    province: 'Québec',
    postalCode: 'G3L 4H2',
    country: 'Canada',
    terrainType: 'public',
    owner: null,
    factors: { habitat: 4.5, pressure: 2.5, coverage: 3.5, water: 5.5, accessibility: 2.0, attractivity: 4.5 },
    notes: 'Accès difficile - terrain marécageux'
  },
  {
    id: 'HS-004',
    name: 'Hotspot Nord - Forêt Dense',
    score: 7.8,
    latitude: 46.8350,
    longitude: -71.2050,
    address: 'Chemin Forestier #7',
    city: 'Saint-Basile',
    province: 'Québec',
    postalCode: 'G0A 3G0',
    country: 'Canada',
    terrainType: 'pourvoirie',
    owner: 'Pourvoirie du Lac Blanc',
    factors: { habitat: 8.5, pressure: 8.0, coverage: 9.0, water: 6.5, accessibility: 7.5, attractivity: 7.5 },
    notes: 'Excellent couvert forestier'
  },
  {
    id: 'HS-005',
    name: 'Hotspot Est - Zone Mixte',
    score: 5.5,
    latitude: 46.8150,
    longitude: -71.1700,
    address: 'Route 138 Est',
    city: 'Donnacona',
    province: 'Québec',
    postalCode: 'G3M 1E8',
    country: 'Canada',
    terrainType: 'private',
    owner: 'Famille Gagnon',
    factors: { habitat: 6.0, pressure: 4.5, coverage: 5.5, water: 5.0, accessibility: 6.0, attractivity: 5.5 },
    notes: 'Proximité de la route - bruit occasionnel'
  },
  {
    id: 'HS-006',
    name: 'Hotspot Sud-Est - Clairière Premium',
    score: 9.1,
    latitude: 46.8000,
    longitude: -71.1800,
    address: '456 Rang des Érables',
    city: 'Cap-Santé',
    province: 'Québec',
    postalCode: 'G0A 1L0',
    country: 'Canada',
    terrainType: 'reserve',
    owner: 'Réserve faunique de Portneuf',
    factors: { habitat: 9.5, pressure: 9.0, coverage: 8.5, water: 9.0, accessibility: 8.5, attractivity: 9.5 },
    notes: 'Meilleur hotspot de la zone - conditions optimales'
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

// Helper function
const getScoreColor = (score) => {
  if (score >= 80) return BIONIC_COLORS.green.primary;
  if (score >= 60) return BIONIC_COLORS.gold.primary;
  if (score >= 40) return BIONIC_COLORS.blue.light;
  return BIONIC_COLORS.red.primary;
};

const BionicAnalysisDemoPage = () => {
  const [selectedWaypointId, setSelectedWaypointId] = useState('WP-001');
  const [selectedHotspotId, setSelectedHotspotId] = useState(null);
  const [hoveredHotspot, setHoveredHotspot] = useState(null);
  const [activeSection, setActiveSection] = useState('carte'); // 'carte' | 'layers' | 'main' | 'charts' | 'popups' | 'list' | 'legend' | 'admin'
  const [isLegal, setIsLegal] = useState(true);
  const [adminHotspots, setAdminHotspots] = useState(MOCK_ADMIN_HOTSPOTS);
  const [layerVisibility, setLayerVisibility] = useState(null); // Contrôlé par LayerControlPanel
  const [analysisResult, setAnalysisResult] = useState(null); // Résultat de l'analyse API
  const [analysisMode, setAnalysisMode] = useState('rut'); // 'live', 'pre_rut', 'rut', 'post_rut'
  
  const waypointContext = getWaypointContext(selectedWaypointId);
  const selectedHotspot = MOCK_HOTSPOTS.find(h => h.id === selectedHotspotId);
  const selectedWaypoint = MOCK_WAYPOINTS.find(wp => wp.id === selectedWaypointId);
  
  // Callback pour changement de mode d'analyse
  const handleAnalysisModeChange = (newMode) => {
    setAnalysisMode(newMode);
    const modeLabels = {
      'live': 'LIVE (temps réel)',
      'pre_rut': 'PRÉ-RUT',
      'rut': 'RUT (pic)',
      'post_rut': 'POST-RUT'
    };
    toast.info(`Mode d'analyse: ${modeLabels[newMode] || newMode}`);
    // Note: L'analyse est automatiquement relancée via CarteBionic 
    // lorsque analysisMode change grâce au useEffect
  };
  
  // Handlers pour le module Admin
  const handleHotspotUpdate = (updatedHotspot) => {
    setAdminHotspots(prev => prev.map(h => h.id === updatedHotspot.id ? updatedHotspot : h));
    toast.success(`Hotspot "${updatedHotspot.name}" mis à jour`);
  };
  
  const handleViewOnMap = (hotspot) => {
    toast.info(`Centrer carte sur: ${hotspot.name} (${hotspot.latitude}, ${hotspot.longitude})`);
  };
  
  const handleViewSelectedOnMap = (hotspots) => {
    toast.info(`Afficher ${hotspots.length} hotspot(s) sur la carte`);
  };
  
  const handleSellHotspot = (hotspot) => {
    toast.success(`Préparation vente: ${hotspot.name} - Redirection vers Marketplace...`);
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
            Phase 6 - ACTION 5: CarteBionic + Intégration API
          </p>
          
          {/* Section Tabs */}
          <div className="flex justify-center gap-2 flex-wrap">
            {[
              { key: 'carte', label: 'Carte' },
              { key: 'layers', label: 'Layers' },
              { key: 'admin', label: 'Admin' },
              { key: 'legend', label: 'Légende' },
              { key: 'main', label: 'Principaux' },
              { key: 'charts', label: 'Graphiques' },
              { key: 'popups', label: 'Popups' },
              { key: 'list', label: 'Liste' }
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
        
        {/* Section: Carte BIONIC (PHASE 6 - ACTION 5) */}
        {activeSection === 'carte' && (
          <div className="space-y-4">
            <p className="text-gray-500 text-xs text-center">
              Carte interactive avec intégration API /api/v1/bionic/analyze_waypoint
            </p>
            
            {/* Sélecteur de waypoint */}
            <div className="max-w-md mx-auto mb-4">
              <select
                value={selectedWaypointId}
                onChange={(e) => setSelectedWaypointId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-gray-800 text-white border border-gray-700 text-sm"
              >
                {MOCK_WAYPOINTS.map(wp => (
                  <option key={wp.id} value={wp.id}>
                    {wp.name} ({wp.latitude.toFixed(4)}, {wp.longitude.toFixed(4)})
                  </option>
                ))}
              </select>
            </div>
            
            {/* Carte BIONIC */}
            <CarteBionic
              waypoint={MOCK_WAYPOINTS.find(wp => wp.id === selectedWaypointId)}
              species="orignal"
              targetDatetime={new Date().toISOString()}
              analysisMode={analysisMode}
              showLayerControl={true}
              autoAnalyze={true}
              onAnalysisComplete={(result) => {
                setAnalysisResult(result);
                console.log('Analysis complete:', result);
              }}
              onAnalysisModeChange={handleAnalysisModeChange}
            />
            
            {/* Info API Response */}
            {analysisResult && (
              <div 
                className="p-4 rounded-lg"
                style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
              >
                <p className="text-sm text-white font-medium mb-2">Réponse API (aperçu)</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
                  <div>
                    <span className="text-gray-500">Analysis ID</span>
                    <p className="text-white">{analysisResult.analysis_id}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Score Final</span>
                    <p className="text-white">{analysisResult.scores?.score_bionic_final?.toFixed(1)}/100</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Mode d'Analyse</span>
                    <p className="text-white font-semibold" style={{ color: BIONIC_COLORS.gold.primary }}>
                      {analysisResult.scores?.analysis_mode?.toUpperCase() || analysisMode.toUpperCase()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Engine Version</span>
                    <p className="text-white">{analysisResult.engine_version}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Processing Time</span>
                    <p className="text-white">{analysisResult.metadata?.processing_time_ms}ms</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Section: Layer Control (PHASE 6 - ACTION 4) */}
        {activeSection === 'layers' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Panneau de contrôle complet */}
              <div>
                <p className="text-gray-500 text-xs text-center mb-3">Mode Complet - Toutes options</p>
                <LayerControlPanel
                  layerVisibility={layerVisibility}
                  onLayerVisibilityChange={setLayerVisibility}
                  analysisMode={analysisMode}
                  onAnalysisModeChange={handleAnalysisModeChange}
                  compact={false}
                  showQuickActions={true}
                  defaultAllOpen={false}
                />
              </div>
              
              {/* Panneau de contrôle compact */}
              <div>
                <p className="text-gray-500 text-xs text-center mb-3">Mode Compact</p>
                <LayerControlPanel
                  layerVisibility={layerVisibility}
                  onLayerVisibilityChange={setLayerVisibility}
                  analysisMode={analysisMode}
                  onAnalysisModeChange={handleAnalysisModeChange}
                  compact={true}
                  showQuickActions={true}
                  defaultAllOpen={true}
                />
              </div>
            </div>
            
            {/* Info panel */}
            <div 
              className="p-4 rounded-lg"
              style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
            >
              <p className="text-sm text-white font-medium mb-2">État des Layers</p>
              <p className="text-xs text-gray-400 mb-3">
                Les modifications sont synchronisées entre les deux panneaux via l'état partagé <code className="text-yellow-500">layerVisibility</code>.
              </p>
              <pre className="text-xs text-gray-500 overflow-auto max-h-40 p-2 rounded" style={{ backgroundColor: BIONIC_COLORS.black.base }}>
                {JSON.stringify(layerVisibility, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        {/* Section: Admin Hotspots (PHASE 5.7) */}
        {activeSection === 'admin' && (
          <AdminBionicHotspots
            hotspots={adminHotspots}
            activeWaypoint={selectedWaypoint ? {
              ...selectedWaypoint,
              latitude: selectedWaypoint.latitude,
              longitude: selectedWaypoint.longitude
            } : null}
            loading={false}
            onRefresh={() => toast.info('Rafraîchissement des données...')}
            onHotspotUpdate={handleHotspotUpdate}
            onViewOnMap={handleViewOnMap}
            onViewSelectedOnMap={handleViewSelectedOnMap}
            onSellHotspot={handleSellHotspot}
          />
        )}
        
        {/* Section: Légende (PHASE 5.6) */}
        {activeSection === 'legend' && (
          <div className="space-y-6">
            {/* Toggle légalité pour demo */}
            <div className="flex justify-center gap-4">
              <button
                onClick={() => setIsLegal(true)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isLegal ? 'text-white' : 'bg-gray-800 text-gray-400'
                }`}
                style={isLegal ? { backgroundColor: '#00A676' } : {}}
              >
                Heures Légales
              </button>
              <button
                onClick={() => setIsLegal(false)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  !isLegal ? 'text-white' : 'bg-gray-800 text-gray-400'
                }`}
                style={!isLegal ? { backgroundColor: '#B91C1C' } : {}}
              >
                Hors Heures
              </button>
            </div>
            
            {/* Légendes côte à côte */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Légende complète */}
              <div>
                <p className="text-gray-500 text-xs text-center mb-3">Légende complète</p>
                <MapLegend
                  isLegal={isLegal}
                  waypointName={selectedWaypoint?.name}
                  maxDistance={10}
                  compact={false}
                  showDistanceScale={true}
                  showLegalIndicator={true}
                  showWaypointInfo={true}
                />
              </div>
              
              {/* Légende compacte */}
              <div>
                <p className="text-gray-500 text-xs text-center mb-3">Légende compacte</p>
                <MapLegend
                  isLegal={isLegal}
                  waypointName={selectedWaypoint?.name}
                  maxDistance={10}
                  compact={true}
                  showDistanceScale={true}
                  showLegalIndicator={true}
                  showWaypointInfo={false}
                />
              </div>
            </div>
            
            {/* Info palette */}
            <div 
              className="p-4 rounded-lg text-center"
              style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
            >
              <p className="text-sm text-white font-medium mb-2">Palette BIONIC Officielle</p>
              <div className="flex justify-center gap-4 flex-wrap">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#00A676' }} />
                  <span className="text-xs text-gray-400">9-10 Vert (#00A676)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#C9A86A' }} />
                  <span className="text-xs text-gray-400">7-8 Doré (#C9A86A)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#1E3A8A' }} />
                  <span className="text-xs text-gray-400">5-6 Bleu (#1E3A8A)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#C26A2E' }} />
                  <span className="text-xs text-gray-400">3-4 Orange (#C26A2E)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: '#B91C1C' }} />
                  <span className="text-xs text-gray-400">0-2 Rouge (#B91C1C)</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Section: Liste Hotspots */}
        {activeSection === 'list' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HotspotListPanel
              hotspots={MOCK_HOTSPOTS}
              selectedHotspotId={selectedHotspotId}
              onSelectHotspot={(h) => setSelectedHotspotId(h.id)}
              onHoverHotspot={setHoveredHotspot}
            />
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
              waypointName={selectedWaypoint?.name}
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

export default BionicAnalysisDemoPage;
