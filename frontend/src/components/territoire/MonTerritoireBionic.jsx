/**
 * MonTerritoireBionic - Section principale pour la page d'accueil
 * BIONIC Design System compliant - No emojis
 * Affiche une carte BIONIC interactive avec aperçu des scores
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polygon } from 'react-leaflet';
import { Brain, Map, Crosshair, Wind, Thermometer, Droplets, TrendingUp, 
         ChevronRight, Layers, Activity, Target, Navigation, 
         Sun, Moon, ArrowRight, Zap, Eye, EyeOff, Home, Heart, Leaf, Footprints } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import useBionicLayers from '@/hooks/useBionicLayers';
import useBionicWeather from '@/hooks/useBionicWeather';
import { BIONIC_LAYERS, getScoresForWaypoint, adaptWaypointData } from '@/core/bionic';
import { MapInteractionLayer } from '@/modules/map_interaction';
import L from 'leaflet';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Composant pour centrer la carte
const MapController = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 11);
    }
  }, [center, map]);
  return null;
};

// Génère des zones de démonstration
const generateDemoZones = (centerLat, centerLng) => {
  const zones = [];
  const categories = ['habitat', 'rut', 'affut', 'corridor'];
  const colors = {
    habitat: '#22c55e',
    rut: '#e91e63',
    affut: '#9c27b0',
    corridor: '#ff5722'
  };
  
  // Générer quelques zones hexagonales
  for (let i = 0; i < 12; i++) {
    const angle = (i * 30) * Math.PI / 180;
    const distance = 0.02 + Math.random() * 0.03;
    const lat = centerLat + Math.sin(angle) * distance;
    const lng = centerLng + Math.cos(angle) * distance;
    const category = categories[i % 4];
    const score = 55 + Math.floor(Math.random() * 40);
    
    // Créer un hexagone
    const hexPoints = [];
    for (let j = 0; j < 6; j++) {
      const hexAngle = (j * 60 - 30) * Math.PI / 180;
      const size = 0.008;
      hexPoints.push([
        lat + Math.sin(hexAngle) * size,
        lng + Math.cos(hexAngle) * size * 1.2
      ]);
    }
    
    zones.push({
      id: `zone-${i}`,
      positions: hexPoints,
      category,
      color: colors[category],
      score,
      label: category === 'habitat' ? 'Habitat optimal' :
             category === 'rut' ? 'Zone de rut' :
             category === 'affut' ? 'Affût potentiel' : 'Corridor'
    });
  }
  
  return zones;
};

const MonTerritoireBionic = ({ onNavigateToTerritory }) => {
  // Position par défaut (Québec)
  const [mapCenter] = useState([46.8139, -71.2080]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [showLayers, setShowLayers] = useState(true);
  
  // Hooks BIONIC
  const { 
    layersVisible, 
    toggleLayer, 
    showAllLayers, 
    hideAllLayers,
    activeCount 
  } = useBionicLayers({ habitats: true, affuts: true, corridors: true });
  
  const { 
    weather, 
    isLoading: weatherLoading,
    temperature,
    windInfo,
    huntingScore,
    nextOptimalWindow
  } = useBionicWeather(mapCenter[0], mapCenter[1], { autoFetch: true });
  
  // Zones de démonstration
  const demoZones = useMemo(() => generateDemoZones(mapCenter[0], mapCenter[1]), [mapCenter]);
  
  // Score global simulé
  const globalScore = useMemo(() => {
    return Math.round(65 + Math.random() * 20);
  }, []);
  
  // Obtenir la classification du score
  const getScoreRating = (score) => {
    if (score >= 80) return { label: 'Excellent', color: 'bg-green-500' };
    if (score >= 65) return { label: 'Très bon', color: 'bg-lime-500' };
    if (score >= 50) return { label: 'Bon', color: 'bg-yellow-500' };
    return { label: 'Modéré', color: 'bg-orange-500' };
  };
  
  const rating = getScoreRating(globalScore);
  
  return (
    <section 
      className="relative py-16 bg-gradient-to-b from-black via-gray-900 to-black overflow-hidden"
      data-testid="mon-territoire-bionic-section"
    >
      {/* Background effects */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmNWE2MjMiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-full px-4 py-2 mb-4">
            <Brain className="h-5 w-5 text-[#f5a623]" />
            <span className="text-[#f5a623] font-medium text-sm">BIONIC™ Territory Engine</span>
            <Badge variant="outline" className="text-[10px] border-green-500/50 text-green-400">LIVE</Badge>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Mon territoire <span className="text-[#f5a623]">BIONIC™</span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Analyse multi-couches ultra précise de votre territoire de chasse avec données météo en temps réel
          </p>
        </div>
        
        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Carte BIONIC */}
          <div className="lg:col-span-2 bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 overflow-hidden backdrop-blur-sm">
            {/* Carte Header */}
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Map className="h-5 w-5 text-[#f5a623]" />
                <span className="text-white font-semibold">Carte BIONIC™</span>
                <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">
                  {activeCount} couches actives
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowLayers(!showLayers)}
                  className="text-gray-400 hover:text-white"
                >
                  {showLayers ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={showAllLayers}
                  className="text-gray-400 hover:text-white text-xs"
                >
                  Tout
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={hideAllLayers}
                  className="text-gray-400 hover:text-white text-xs"
                >
                  Aucun
                </Button>
              </div>
            </div>
            
            {/* Map Container */}
            <div className="h-[400px] relative">
              <MapContainer
                center={mapCenter}
                zoom={11}
                className="h-full w-full"
                zoomControl={false}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                />
                <MapController center={mapCenter} />
                
                {/* Zones BIONIC */}
                {showLayers && demoZones.map(zone => (
                  <Polygon
                    key={zone.id}
                    positions={zone.positions}
                    pathOptions={{
                      color: zone.color,
                      fillColor: zone.color,
                      fillOpacity: selectedZone?.id === zone.id ? 0.5 : 0.25,
                      weight: selectedZone?.id === zone.id ? 3 : 1.5,
                      opacity: 0.8
                    }}
                    eventHandlers={{
                      click: () => setSelectedZone(zone),
                      mouseover: (e) => {
                        e.target.setStyle({ fillOpacity: 0.4, weight: 2 });
                      },
                      mouseout: (e) => {
                        e.target.setStyle({ 
                          fillOpacity: selectedZone?.id === zone.id ? 0.5 : 0.25, 
                          weight: selectedZone?.id === zone.id ? 3 : 1.5 
                        });
                      }
                    }}
                  >
                    <Popup>
                      <div className="text-center p-2">
                        <div className="font-bold text-sm">{zone.label}</div>
                        <div className="text-lg font-bold text-[#f5a623]">{zone.score}%</div>
                      </div>
                    </Popup>
                  </Polygon>
                ))}
                
                {/* Map Interaction Layer - Coordonnées GPS + Waypoints */}
                <MapInteractionLayer 
                  showCoordinates={true}
                  enableWaypointCreation={true}
                  showHint={true}
                  onWaypointCreated={(waypoint) => console.log('Waypoint créé:', waypoint)}
                />
              </MapContainer>
              
              {/* Score Overlay */}
              <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-sm rounded-xl p-3 border border-[#f5a623]/30 z-[1000]">
                <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Score Global</div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-white">{globalScore}</span>
                  <span className="text-gray-400">/100</span>
                  <Badge className={`${rating.color} text-white text-[10px]`}>{rating.label}</Badge>
                </div>
              </div>
              
              {/* Weather Mini Banner */}
              {weather && (
                <div className="absolute bottom-4 left-4 right-4 bg-black/80 backdrop-blur-sm rounded-lg p-2 border border-gray-700 z-[1000]">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5">
                        <Thermometer className="h-3.5 w-3.5 text-blue-400" />
                        <span className="text-white">{Math.round(temperature)}°C</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Wind className="h-3.5 w-3.5 text-gray-400" />
                        <span className="text-white">{windInfo?.direction} {Math.round(windInfo?.speed)} km/h</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Activity className="h-3.5 w-3.5 text-green-400" />
                        <span className="text-white">Chasse: {huntingScore}/100</span>
                      </div>
                    </div>
                    <Badge className="bg-green-500/20 text-green-400 text-[10px]">
                      <Zap className="h-3 w-3 mr-1" /> LIVE
                    </Badge>
                  </div>
                </div>
              )}
            </div>
            
            {/* Couches Toggle */}
            <div className="p-3 border-t border-gray-800">
              <div className="flex flex-wrap gap-2">
                {BIONIC_LAYERS.slice(0, 8).map(layer => (
                  <button
                    key={layer.id}
                    onClick={() => toggleLayer(layer.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                      layersVisible[layer.id]
                        ? 'bg-[#f5a623]/20 text-[#f5a623] border border-[#f5a623]/30'
                        : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <span>{layer.icon}</span>
                    <span>{layer.name.replace(' potentiels', '').replace(' optimaux', '')}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Panneau latéral */}
          <div className="space-y-4">
            {/* Score Breakdown */}
            <div className="bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 p-4 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Target className="h-5 w-5 text-[#f5a623]" />
                <span className="text-white font-semibold">Analyse BIONIC™</span>
              </div>
              
              <div className="space-y-3">
                {[
                  { label: 'Habitat', score: 78, Icon: Home, color: 'bg-green-500' },
                  { label: 'Rut', score: 72, Icon: Heart, color: 'bg-pink-500' },
                  { label: 'Affûts', score: 85, Icon: Target, color: 'bg-purple-500' },
                  { label: 'Corridors', score: 68, Icon: Footprints, color: 'bg-orange-500' },
                  { label: 'Alimentation', score: 74, Icon: Leaf, color: 'bg-lime-500' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <item.Icon className="w-5 h-5 text-slate-400" />
                    <div className="flex-1">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-400">{item.label}</span>
                        <span className="text-white font-medium">{item.score}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${item.color} rounded-full transition-all duration-500`}
                          style={{ width: `${item.score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Prochaine fenêtre optimale */}
            {nextOptimalWindow && (
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 rounded-2xl border border-green-500/30 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Sun className="h-5 w-5 text-green-400" />
                  <span className="text-green-400 font-semibold text-sm">Prochaine fenêtre optimale</span>
                </div>
                <div className="text-white">
                  <div className="text-lg font-bold">
                    {new Date(nextOptimalWindow.start).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                    {' - '}
                    {new Date(nextOptimalWindow.end).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="text-xs text-green-300 mt-1">
                    Score moyen: {Math.round(nextOptimalWindow.avgScore)}/100
                  </div>
                </div>
              </div>
            )}
            
            {/* Selected Zone Info */}
            {selectedZone && (
              <div className="bg-gray-900/50 rounded-2xl border border-[#f5a623]/20 p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: selectedZone.color }}
                  />
                  <span className="text-white font-semibold">{selectedZone.label}</span>
                </div>
                <div className="text-3xl font-bold text-[#f5a623] mb-2">{selectedZone.score}%</div>
                <p className="text-gray-400 text-sm mb-3">
                  Zone à fort potentiel identifiée par l'analyse multi-couches BIONIC™
                </p>
                <Button 
                  className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-medium"
                  onClick={onNavigateToTerritory}
                >
                  <Navigation className="h-4 w-4 mr-2" />
                  Analyser en détail
                </Button>
              </div>
            )}
            
            {/* CTA */}
            <div className="bg-gradient-to-br from-[#f5a623]/20 to-orange-600/10 rounded-2xl border border-[#f5a623]/30 p-4">
              <div className="text-white font-semibold mb-2">Accéder à la Carte BIONIC™ complète</div>
              <p className="text-gray-400 text-sm mb-4">
                15 couches d'analyse • Météo LIVE • Stratégie temps réel • IA prédictive
              </p>
              <Button 
                className="w-full bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-medium group"
                onClick={onNavigateToTerritory}
              >
                Explorer mon territoire
                <ChevronRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>
        
        {/* Features Grid */}
        <div className="grid md:grid-cols-4 gap-4 mt-8">
          {[
            { icon: Layers, label: '15 couches', desc: 'Analyse multi-critères' },
            { icon: Wind, label: 'Météo LIVE', desc: 'Données en temps réel' },
            { icon: Brain, label: 'IA Hybride', desc: 'Règles + Machine Learning' },
            { icon: Target, label: 'Stratégie', desc: 'Recommandations tactiques' },
          ].map((feature, idx) => (
            <div 
              key={idx}
              className="bg-gray-900/30 rounded-xl border border-gray-800 p-4 text-center hover:border-[#f5a623]/30 transition-colors"
            >
              <feature.icon className="h-8 w-8 text-[#f5a623] mx-auto mb-2" />
              <div className="text-white font-semibold text-sm">{feature.label}</div>
              <div className="text-gray-500 text-xs">{feature.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MonTerritoireBionic;
