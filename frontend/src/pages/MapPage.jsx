/**
 * MapPage - Interactive Map Page for Waypoints
 * PHASE F — GPS ULTIMATE + BIONIC V5 Organic Zones
 * 
 * Carte interactive avec intégration BIONIC V5:
 * - Waypoints et GPS Tracking
 * - Hotspots dynamiques (AutoCartographyEngine)
 * - Zones de danger (SafetyEngine)
 * - Zones BIONIC V5 organiques avec espèce + ON/OFF
 * 
 * VERSION: 7.3.0
 * Conformité: BIONIC V5 PHASE F
 */
import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { WaypointMap } from '../modules/territory';
import BackgroundTracker from '../components/BackgroundTracker';
import GeoSyncToggle from '../components/GeoSyncToggle';
import BionicMapOverlay from '../components/territoire/BionicMapOverlay';
import { SPECIES_LIST } from '../core/bionic/speciesConfig';
import { BIONIC_MODULES } from '../core/bionic';
import useBionicLayers from '../hooks/useBionicLayers';
import { toast } from 'sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Map, Satellite, RefreshCw, X, Users, MapPin, Bell, BarChart3, 
  Smartphone, ArrowLeft, Layers, Eye, EyeOff, ChevronDown, ChevronUp,
  Target, CheckCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { useLanguage } from '@/contexts/LanguageContext';
import { GroupeTab } from '../modules/groupe';

const MapPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState('map');
  const [refreshKey, setRefreshKey] = useState(0);
  const { t } = useLanguage();
  const navigate = useNavigate();
  
  // BIONIC V5 States
  const [selectedSpecies, setSelectedSpecies] = useState('tous');
  const [showBionicPanel, setShowBionicPanel] = useState(false);
  const [bionicStats, setBionicStats] = useState({});
  const { layersVisible, toggleLayer, showAllLayers, hideAllLayers } = useBionicLayers();
  
  // Get URL parameters for map centering
  const urlParams = useMemo(() => {
    const lat = parseFloat(searchParams.get('lat'));
    const lng = parseFloat(searchParams.get('lng'));
    const zoom = parseInt(searchParams.get('zoom')) || 15;
    
    if (!isNaN(lat) && !isNaN(lng)) {
      return { lat, lng, zoom, hasParams: true };
    }
    return { hasParams: false };
  }, [searchParams]);

  useEffect(() => {
    if (urlParams.hasParams) {
      toast.info(`Carte centrée sur: ${urlParams.lat.toFixed(4)}, ${urlParams.lng.toFixed(4)}`);
    }
  }, [urlParams]);

  const clearUrlParams = () => {
    setSearchParams({});
  };

  const handleProximityAlert = (alert) => {
    console.log('Proximity alert received:', alert);
  };

  const handleEntityReceived = useCallback(({ action, entity, entityId, userId }) => {
    console.log('Sync event:', action, entity || entityId);
    setRefreshKey(prev => prev + 1);
  }, []);

  const handleMemberJoined = useCallback((userId) => {
    console.log('Member joined:', userId);
  }, []);

  const handleMemberLeft = useCallback((userId) => {
    console.log('Member left:', userId);
  }, []);

  const getUserId = () => {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const parsed = JSON.parse(user);
        return parsed.email || parsed.id || 'default_user';
      } catch (e) {
        return 'default_user';
      }
    }
    return 'default_user';
  };

  // Count visible layers
  const visibleLayerCount = useMemo(() => 
    Object.values(layersVisible).filter(Boolean).length
  , [layersVisible]);

  return (
    <div 
      className="fixed inset-0 bg-black flex flex-col overflow-hidden"
      style={{ paddingTop: '64px' }}
      data-testid="map-page"
    >
      {/* Header compact PHASE F */}
      <div className="flex-shrink-0 bg-black/95 border-b border-[#f5a623]/20 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/')} 
              className="text-gray-300 hover:text-white h-8 px-2"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="h-5 w-px bg-[#f5a623]/30" />
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-[#f5a623]" />
              <div>
                <h1 className="text-sm font-bold text-white leading-tight">Carte Interactive PHASE F</h1>
                <p className="text-[10px] text-gray-400 leading-tight">
                  Waypoints • GPS Tracking • Hotspots • BIONIC V5
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* BIONIC V5 Toggle Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowBionicPanel(!showBionicPanel)}
              className={`h-8 px-3 text-xs ${showBionicPanel ? 'bg-amber-500/20 text-amber-400' : 'text-gray-400 hover:text-white'}`}
              data-testid="toggle-bionic-panel"
            >
              <Layers className="h-3.5 w-3.5 mr-1.5" />
              BIONIC V5
              {visibleLayerCount > 0 && (
                <Badge className="ml-1.5 bg-amber-500/30 text-amber-300 text-[9px] px-1">{bionicStats.total || 0}</Badge>
              )}
            </Button>

            <GeoSyncToggle
              groupId="default_group"
              userId={getUserId()}
              onEntityReceived={handleEntityReceived}
              onMemberJoined={handleMemberJoined}
              onMemberLeft={handleMemberLeft}
            />
          </div>
        </div>

        {urlParams.hasParams && (
          <div className="mt-2 p-2 bg-blue-900/30 border border-blue-500/50 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-blue-400" />
              <span className="text-blue-300 text-xs">
                Vue centrée: <strong>{urlParams.lat.toFixed(6)}, {urlParams.lng.toFixed(6)}</strong>
                <span className="text-blue-400 ml-2">(Zoom: {urlParams.zoom})</span>
              </span>
            </div>
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={clearUrlParams}
              className="text-blue-400 hover:text-blue-300 h-6 px-2"
            >
              <X className="h-3 w-3 mr-1" />
              Réinitialiser
            </Button>
          </div>
        )}
      </div>

      {/* Tabs compact */}
      <div className="flex-shrink-0 bg-black/95 border-b border-gray-800 px-4 py-1">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-gray-900/50 h-8">
            <TabsTrigger value="map" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black h-7 text-xs px-3" data-testid="tab-map">
              <Map className="h-3 w-3 mr-1.5" />
              Carte
            </TabsTrigger>
            <TabsTrigger value="tracking" className="data-[state=active]:bg-cyan-600 h-7 text-xs px-3" data-testid="tab-tracking">
              <Satellite className="h-3 w-3 mr-1.5" />
              GPS Tracking
            </TabsTrigger>
            <TabsTrigger value="groupe" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black h-7 text-xs px-3" data-testid="tab-groupe">
              <Users className="h-3 w-3 mr-1.5" />
              {t('groupe_tab_title')}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-hidden relative min-h-0">
        {/* Map Tab */}
        {activeTab === 'map' && (
          <div className="absolute inset-0 w-full h-full">
            <WaypointMap 
              key={refreshKey}
              initialCenter={urlParams.hasParams ? [urlParams.lat, urlParams.lng] : null}
              initialZoom={urlParams.hasParams ? urlParams.zoom : null}
            >
              {/* BIONIC V5 Organic Zones Overlay */}
              <BionicMapOverlay
                selectedSpecies={selectedSpecies}
                layersVisible={layersVisible}
                minPercentage={50}
                showCorridors={true}
                onStatsUpdate={setBionicStats}
              />
            </WaypointMap>

            {/* ============================================ */}
            {/* BIONIC V5 — Panneau de contrôle flottant     */}
            {/* ============================================ */}
            {showBionicPanel && (
              <div 
                className="absolute top-4 right-4 z-[1000] w-64 bg-gray-950/95 backdrop-blur-md rounded-xl border border-amber-500/30 shadow-2xl overflow-hidden"
                data-testid="bionic-control-panel"
              >
                {/* Header */}
                <div className="flex items-center justify-between px-3 py-2 bg-amber-500/10 border-b border-amber-500/20">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-amber-400" />
                    <span className="text-xs font-bold text-white">BIONIC V5</span>
                  </div>
                  <button onClick={() => setShowBionicPanel(false)} className="text-gray-400 hover:text-white">
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="p-3 space-y-3 max-h-[60vh] overflow-y-auto">
                  {/* Espèce cible */}
                  <div>
                    <div className="text-[10px] text-gray-400 uppercase mb-1.5 font-medium">Espèce cible</div>
                    <div className="space-y-1">
                      {SPECIES_LIST.map(sp => (
                        <button
                          key={sp.id}
                          onClick={() => setSelectedSpecies(sp.id)}
                          data-testid={`map-species-btn-${sp.id}`}
                          className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                            selectedSpecies === sp.id
                              ? 'bg-amber-500/20 text-white border border-amber-500/40'
                              : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
                          }`}
                        >
                          <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: sp.color }} />
                          <span className="flex-1 text-left">{sp.name}</span>
                          {selectedSpecies === sp.id && <CheckCircle className="h-3 w-3 text-amber-400" />}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Couches ON/OFF */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] text-gray-400 uppercase font-medium">Couches</span>
                      <div className="flex gap-1">
                        <button onClick={showAllLayers} className="text-[9px] text-emerald-400 hover:underline">Tout</button>
                        <span className="text-gray-600 text-[9px]">|</span>
                        <button onClick={hideAllLayers} className="text-[9px] text-red-400 hover:underline">Rien</button>
                      </div>
                    </div>
                    <div className="space-y-0.5 max-h-[200px] overflow-y-auto">
                      {Object.entries(BIONIC_MODULES)
                        .filter(([, cfg]) => ['behavioral', 'environmental', 'strategic'].includes(cfg.category))
                        .map(([id, cfg]) => (
                        <div key={id} className="flex items-center justify-between py-1 px-1.5 rounded hover:bg-gray-900/50">
                          <div className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
                            <span className="text-[10px] text-gray-300">{cfg.label}</span>
                          </div>
                          <Switch
                            checked={layersVisible[id] ?? false}
                            onCheckedChange={() => toggleLayer(id)}
                            className="scale-[0.6] data-[state=checked]:bg-amber-500"
                            data-testid={`map-layer-toggle-${id}`}
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stats */}
                  {bionicStats.total > 0 && (
                    <div className="bg-gray-900/50 rounded-lg p-2 space-y-1">
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="text-gray-400">Zones organiques</span>
                        <span className="text-amber-400 font-bold">{bionicStats.total}</span>
                      </div>
                      {bionicStats.avgArea > 0 && (
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="text-gray-400">Superficie moy.</span>
                          <span className="text-emerald-400">~{bionicStats.avgArea?.toLocaleString('fr-FR')} m²</span>
                        </div>
                      )}
                      {bionicStats.rejected > 0 && (
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="text-gray-400">Rejetées (terrain)</span>
                          <span className="text-red-400">{bionicStats.rejected}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tracking Tab */}
        {activeTab === 'tracking' && (
          <div className="absolute inset-0 overflow-y-auto p-4">
            <div className="max-w-5xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <BackgroundTracker onProximityAlert={handleProximityAlert} />
                <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700">
                  <h3 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-[#f5a623]" /> Guide de Tracking
                  </h3>
                  <div className="space-y-3 text-xs text-slate-400">
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <h4 className="text-cyan-400 font-medium mb-1 flex items-center gap-2">
                        <Satellite className="h-3 w-3" /> Tracking Arrière-plan
                      </h4>
                      <p>Activez le tracking pour enregistrer automatiquement votre position toutes les 5 minutes.</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <h4 className="text-amber-400 font-medium mb-1 flex items-center gap-2">
                        <Bell className="h-3 w-3" /> Alertes de Proximité
                      </h4>
                      <p>Notification à 500m d'un waypoint (700m pour les hotspots).</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <h4 className="text-emerald-400 font-medium mb-1 flex items-center gap-2">
                        <BarChart3 className="h-3 w-3" /> Sessions de Chasse
                      </h4>
                      <p>Calcul automatique de la distance parcourue et positions enregistrées.</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <h4 className="text-purple-400 font-medium mb-1 flex items-center gap-2">
                        <Smartphone className="h-3 w-3" /> Mode PWA
                      </h4>
                      <p>Installez BIONIC HUNT/Chasse via "Ajouter à l'écran d'accueil" pour une meilleure expérience.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Groupe Tab */}
        {activeTab === 'groupe' && (
          <div className="absolute inset-0 overflow-y-auto p-4">
            <div className="max-w-5xl mx-auto">
              <GroupeTab
                groupId="default_group"
                userId={getUserId()}
                compact={false}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapPage;
