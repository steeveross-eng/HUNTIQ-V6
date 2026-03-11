import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Map, Layers, Navigation, Satellite, Mountain, Trees, Target, MapPin, 
  Maximize2, Droplets, Compass, Activity, ChevronRight, Loader2, Database
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useGeospatialStatus, useDataSources } from '@/hooks/geospatial';

// Regions du Québec avec coordonnées
const QUEBEC_REGIONS = [
  { id: 1, name: 'Laurentides', lat: 46.0, lon: -74.5, status: 'Optimal', zones: 4 },
  { id: 2, name: 'Abitibi-Témiscamingue', lat: 48.5, lon: -78.0, status: 'Bon', zones: 3 },
  { id: 3, name: 'Saguenay-Lac-Saint-Jean', lat: 48.4, lon: -71.0, status: 'Excellent', zones: 5 },
  { id: 4, name: 'Outaouais', lat: 46.5, lon: -76.0, status: 'Optimal', zones: 3 },
  { id: 5, name: 'Mauricie', lat: 46.8, lon: -73.0, status: 'Bon', zones: 3 },
  { id: 6, name: 'Bas-Saint-Laurent', lat: 47.8, lon: -68.5, status: 'Bon', zones: 4 },
];

// Status badge colors
const STATUS_COLORS = {
  'Excellent': 'bg-green-500/20 text-green-400 border-green-500/30',
  'Optimal': 'bg-[#f5a623]/20 text-[#f5a623] border-[#f5a623]/30',
  'Bon': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

// Data source status indicator
const DataSourceIndicator = ({ source }) => {
  const isActive = source?.status === 'available' || source?.status === 'operational' || source?.status === 'ready';
  
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 rounded-sm border border-white/10">
      <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
      <span className="text-xs text-gray-300 font-mono">{source?.name || 'Source'}</span>
    </div>
  );
};

// Interactive map placeholder with real data
const InteractiveMapView = ({ engineStatus, dataSources, onExpand }) => {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [activeLayer, setActiveLayer] = useState('terrain');

  const layers = [
    { id: 'terrain', name: 'Terrain', icon: Mountain },
    { id: 'hydro', name: 'Hydrologie', icon: Droplets },
    { id: 'forest', name: 'Forêt', icon: Trees },
    { id: 'satellite', name: 'Satellite', icon: Satellite },
  ];

  return (
    <div className="relative w-full h-full min-h-[520px] bg-[#0d1117] rounded-md overflow-hidden">
      {/* Map background with topographic style */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #0a1628 0%, #0d1117 50%, #0a1628 100%)',
        }}
      />
      
      {/* Topographic grid overlay */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            radial-gradient(circle at 20% 30%, rgba(245,166,35,0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 60%, rgba(59,130,246,0.1) 0%, transparent 50%),
            linear-gradient(rgba(245,166,35,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245,166,35,0.03) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 100% 100%, 40px 40px, 40px 40px'
        }}
      />

      {/* Header with status */}
      <div className="relative z-10 p-4 md:p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-3 h-3 bg-[#f5a623] rounded-full animate-pulse" />
              <div className="absolute inset-0 w-3 h-3 bg-[#f5a623] rounded-full animate-ping" />
            </div>
            <span className="text-[#f5a623] font-mono text-sm uppercase tracking-wider">
              BIONIC™ Engine {engineStatus?.status === 'operational' ? 'Active' : 'Loading'}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30 font-mono">
              <Database className="w-3 h-3 mr-1" />
              {dataSources?.length || 0} sources
            </Badge>
            <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 font-mono">
              29 zones actives
            </Badge>
          </div>
        </div>

        {/* Layer selector */}
        <div className="flex flex-wrap gap-2 mb-6">
          {layers.map((layer) => (
            <Button
              key={layer.id}
              size="sm"
              variant={activeLayer === layer.id ? "default" : "outline"}
              className={`rounded-sm ${
                activeLayer === layer.id 
                  ? 'bg-[#f5a623] text-black hover:bg-[#d9901c]' 
                  : 'border-white/20 text-white hover:bg-white/10'
              }`}
              onClick={() => setActiveLayer(layer.id)}
            >
              <layer.icon className="h-4 w-4 mr-1" />
              {layer.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Main map area with region markers */}
      <div className="relative z-10 px-4 md:px-6 pb-4 h-[280px]">
        <div className="relative h-full border border-white/10 rounded-sm bg-black/30">
          {/* Simplified Quebec outline */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 250" preserveAspectRatio="xMidYMid meet">
            {/* Quebec simplified shape */}
            <path 
              d="M100,200 L80,150 L60,100 L80,60 L120,40 L180,30 L250,35 L320,50 L360,80 L380,120 L370,170 L340,200 L280,220 L200,230 L140,220 Z"
              fill="none"
              stroke="rgba(245,166,35,0.3)"
              strokeWidth="1.5"
              strokeDasharray="4,4"
            />
            
            {/* Region connections */}
            {QUEBEC_REGIONS.map((region, i) => (
              <circle
                key={region.id}
                cx={100 + i * 45}
                cy={100 + (i % 3) * 30}
                r="3"
                fill="#f5a623"
                opacity="0.5"
              />
            ))}
          </svg>

          {/* Region markers */}
          <AnimatePresence>
            {QUEBEC_REGIONS.map((region, i) => (
              <motion.div
                key={region.id}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.15, type: 'spring', stiffness: 200 }}
                className="absolute cursor-pointer group"
                style={{
                  top: `${15 + (i % 3) * 25}%`,
                  left: `${10 + i * 13}%`,
                }}
                onClick={() => setSelectedRegion(region)}
              >
                {/* Marker */}
                <div className="relative">
                  <div className="absolute -inset-2 bg-[#f5a623]/20 rounded-full animate-ping" />
                  <div className={`w-4 h-4 rounded-full relative z-10 ${
                    selectedRegion?.id === region.id ? 'bg-white ring-2 ring-[#f5a623]' : 'bg-[#f5a623]'
                  }`} />
                </div>
                
                {/* Tooltip */}
                <div className="absolute left-6 top-0 opacity-0 group-hover:opacity-100 transition-all duration-200 z-30 pointer-events-none">
                  <div className="bg-black/95 backdrop-blur-sm px-3 py-2 rounded-sm border border-[#f5a623]/30 whitespace-nowrap min-w-[140px]">
                    <p className="text-white font-semibold text-sm">{region.name}</p>
                    <p className="text-gray-300 text-xs font-mono mt-1">
                      {region.lat.toFixed(1)}°N, {Math.abs(region.lon).toFixed(1)}°W
                    </p>
                    <div className="flex items-center justify-between mt-2">
                      <Badge className={`text-xs ${STATUS_COLORS[region.status]}`}>
                        {region.status}
                      </Badge>
                      <span className="text-xs text-gray-500">{region.zones} zones</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Selected region info panel */}
          {selectedRegion && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute right-4 top-4 bg-black/90 backdrop-blur-sm p-4 rounded-sm border border-[#f5a623]/30 w-48"
            >
              <h4 className="text-white font-semibold text-sm mb-2">{selectedRegion.name}</h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between text-gray-300">
                  <span>Latitude</span>
                  <span className="font-mono text-white">{selectedRegion.lat}°N</span>
                </div>
                <div className="flex justify-between text-gray-300">
                  <span>Longitude</span>
                  <span className="font-mono text-white">{Math.abs(selectedRegion.lon)}°W</span>
                </div>
                <div className="flex justify-between text-gray-300">
                  <span>Zones</span>
                  <span className="font-mono text-white">{selectedRegion.zones}</span>
                </div>
              </div>
              <Badge className={`mt-3 w-full justify-center ${STATUS_COLORS[selectedRegion.status]}`}>
                {selectedRegion.status}
              </Badge>
            </motion.div>
          )}
        </div>
      </div>

      {/* Footer with data sources and actions */}
      <div className="relative z-10 px-4 md:px-6 pb-4">
        {/* Data sources row */}
        <div className="flex flex-wrap gap-2 mb-4 overflow-x-auto pb-2">
          {dataSources?.slice(0, 4).map((source, i) => (
            <DataSourceIndicator key={i} source={source} />
          ))}
          {dataSources?.length > 4 && (
            <span className="text-xs text-gray-500 self-center">+{dataSources.length - 4} sources</span>
          )}
        </div>
        
        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-white/10">
          <div className="flex gap-2">
            <Button 
              size="sm" 
              variant="outline" 
              className="border-white/20 text-white hover:bg-white/10 rounded-sm"
            >
              <Layers className="h-4 w-4 mr-1" /> Couches
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              className="border-white/20 text-white hover:bg-white/10 rounded-sm"
            >
              <Compass className="h-4 w-4 mr-1" /> Potentiel
            </Button>
          </div>
          <Button 
            size="sm" 
            className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
            onClick={onExpand}
          >
            <Maximize2 className="h-4 w-4 mr-1" /> Explorer
          </Button>
        </div>
      </div>
    </div>
  );
};

const MapModule = () => {
  const { status: engineStatus, loading: statusLoading } = useGeospatialStatus();
  const { sources: dataSources, loading: sourcesLoading } = useDataSources();

  const loading = statusLoading || sourcesLoading;

  const stats = [
    { icon: Mountain, label: 'Zones montagneuses', value: '12', color: 'text-orange-400' },
    { icon: Trees, label: 'Zones forestières', value: '15', color: 'text-green-400' },
    { icon: Target, label: 'Points chauds actifs', value: '847', color: 'text-red-400' },
    { icon: MapPin, label: 'Pourvoiries partenaires', value: '156', color: 'text-blue-400' },
  ];

  return (
    <section 
      className="py-16 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0d1117]" 
      data-testid="map-module-section"
    >
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Map className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">
                Moteur Géospatial BIONIC™
              </span>
              {engineStatus?.status === 'operational' && (
                <Badge className="bg-green-500/20 text-green-400 text-xs">ACTIF</Badge>
              )}
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Territoires du <span className="text-[#f5a623]">Québec</span>
            </h2>
            <p className="text-gray-300 mt-2 max-w-xl">
              Explorez les 29 zones de chasse avec données géospatiales en temps réel 
              provenant de sources gouvernementales 100% gratuites
            </p>
          </div>
          <Link to="/territoire">
            <Button className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm hidden md:flex">
              <Navigation className="h-4 w-4 mr-2" />
              Explorer la carte complète
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>

        {/* Map Container */}
        <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden">
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center min-h-[520px] bg-[#0d1117]">
                <div className="text-center">
                  <Loader2 className="h-8 w-8 text-[#f5a623] animate-spin mx-auto mb-3" />
                  <p className="text-gray-300 text-sm">Chargement du moteur géospatial...</p>
                </div>
              </div>
            ) : (
              <InteractiveMapView 
                engineStatus={engineStatus}
                dataSources={dataSources}
                onExpand={() => window.location.href = '/territoire'} 
              />
            )}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-md p-4 text-center hover:border-[#f5a623]/30 transition-colors"
            >
              <stat.icon className={`h-6 w-6 mx-auto mb-2 ${stat.color}`} />
              <div className="font-barlow text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-gray-300 text-xs uppercase tracking-wider">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Data Sources Info */}
        <div className="mt-8 p-4 bg-black/40 border border-white/10 rounded-md">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="h-4 w-4 text-[#f5a623]" />
            <span className="text-white font-semibold text-sm">Sources de données actives</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {dataSources?.map((source, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-black/60 rounded-sm border border-white/5">
                <div className={`w-2 h-2 rounded-full ${
                  source.free ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                <span className="text-xs text-gray-300">{source.name}</span>
                <span className="text-xs text-gray-500">({source.license?.split(' ')[0]})</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Toutes les données proviennent de sources ouvertes et gratuites : Données Québec, SIGÉOM, Copernicus, OSM
          </p>
        </div>
      </div>
    </section>
  );
};

export default MapModule;
