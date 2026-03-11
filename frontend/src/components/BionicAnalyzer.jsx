/**
 * BionicAnalyzer - Advanced Territory Analysis Component
 * ========================================================
 * Features:
 * - 8 Thematic Modules (Thermal, Wetness, Food, Pressure, Access, Corridor, GeoForm, Canopy)
 * - 6 Wildlife Models (Moose, Deer, Bear, Caribou, Wolf, Turkey)
 * - AI Predictions (24h, 72h, 7d forecasts)
 * - Temporal Analysis (NDVI/NDWI trends)
 * - Dynamic Scoring (weather-adjusted)
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Thermometer,
  Droplets,
  Leaf,
  Users,
  MapPin,
  GitBranch,
  Mountain,
  Trees,
  TreePine,
  Target,
  Brain,
  TrendingUp,
  Clock,
  Zap,
  RefreshCw,
  Loader2,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Info,
  BarChart3,
  LineChart,
  Compass,
  Sun,
  Moon,
  CloudRain,
  Wind,
  Cloud,
  Satellite,
  CircleDot
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = process.env.REACT_APP_BACKEND_URL;

// Module configurations with icons and colors
const MODULE_ICONS = {
  thermal: { icon: Thermometer, color: 'text-red-400', bg: 'bg-red-500/20' },
  wetness: { icon: Droplets, color: 'text-blue-400', bg: 'bg-blue-500/20' },
  food: { icon: Leaf, color: 'text-green-400', bg: 'bg-green-500/20' },
  pressure: { icon: Users, color: 'text-orange-400', bg: 'bg-orange-500/20' },
  access: { icon: MapPin, color: 'text-purple-400', bg: 'bg-purple-500/20' },
  corridor: { icon: GitBranch, color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
  geoform: { icon: Mountain, color: 'text-amber-400', bg: 'bg-amber-500/20' },
  canopy: { icon: Trees, color: 'text-emerald-400', bg: 'bg-emerald-500/20' }
};

const SPECIES_ICONS = {
  moose: { Icon: CircleDot, nameKey: 'animal_moose', name: 'Orignal', color: '#8B4513' },
  deer: { Icon: CircleDot, nameKey: 'animal_deer', name: 'Cerf de Virginie', color: '#D2691E' },
  bear: { Icon: CircleDot, nameKey: 'animal_bear', name: 'Ours noir', color: '#2F4F4F' },
  caribou: { Icon: CircleDot, nameKey: 'animal_caribou', name: 'Caribou', color: '#3b82f6' },
  wolf: { Icon: CircleDot, nameKey: 'animal_wolf', name: 'Loup gris', color: '#6b7280' },
  turkey: { Icon: CircleDot, nameKey: 'animal_turkey', name: 'Dindon sauvage', color: '#ef4444' }
};

const getRatingColor = (rating) => {
  switch (rating) {
    case 'Excellent': return 'bg-green-500/20 text-green-400 border-green-500/50';
    case 'Très bon': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
    case 'Bon': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    case 'Moyen': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
    case 'Faible': return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
    default: return 'bg-red-500/20 text-red-400 border-red-500/50';
  }
};

const getScoreColor = (score) => {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-emerald-400';
  if (score >= 40) return 'text-yellow-400';
  if (score >= 20) return 'text-orange-400';
  return 'text-red-400';
};

// ============================================
// NDVI/NDWI Interpretation Functions
// ============================================

/**
 * Interprétation simple de la valeur NDVI (Verdure)
 * - 0.00–0.20 : Végétation faible (sol visible, début de saison)
 * - 0.20–0.40 : Végétation moyenne (présente mais peu dense)
 * - 0.40–0.60 : Bonne végétation (croissance active)
 * - >0.60 : Végétation dense (habitat optimal)
 */
const getNdviLabel = (ndvi) => {
  if (ndvi === null || ndvi === undefined) return "N/A";
  if (ndvi < 0) return "Sol nu ou eau";
  if (ndvi < 0.20) return "Végétation faible";
  if (ndvi < 0.40) return "Végétation moyenne";
  if (ndvi < 0.60) return "Bonne végétation";
  return "Végétation dense";
};

/**
 * Interprétation simple de la valeur NDWI (Humidité)
 * - <0.00 : Très sec (stress hydrique)
 * - 0.00–0.10 : Sec (humidité faible)
 * - 0.10–0.25 : Humidité normale (conditions correctes)
 * - 0.25–0.40 : Humide (bonne rétention d'eau)
 * - >0.40 : Très humide (sol saturé)
 */
const getNdwiLabel = (ndwi) => {
  if (ndwi === null || ndwi === undefined) return "N/A";
  if (ndwi < 0) return "Très sec";
  if (ndwi < 0.10) return "Sec";
  if (ndwi < 0.25) return "Humidité normale";
  if (ndwi < 0.40) return "Humide";
  return "Très humide";
};

/**
 * Conclusion saisonnière basée sur NDVI et NDWI
 */
const getVegetationConclusion = (ndvi, ndwi) => {
  if (ndvi === null || ndvi === undefined) return "";
  if (ndwi === null || ndwi === undefined) ndwi = 0;
  
  if (ndvi < 0.20 && ndwi < 0) {
    return "Période de dormance ou début de saison";
  } else if (ndvi < 0.20 && ndwi >= 0) {
    return "Début de croissance probable";
  } else if (ndvi >= 0.20 && ndvi < 0.40 && ndwi < 0) {
    return "Stress hydrique détecté";
  } else if (ndvi >= 0.40 && ndvi < 0.60) {
    return "Croissance active - bonnes conditions";
  } else if (ndvi >= 0.60 && ndwi >= 0.10) {
    return "Conditions optimales - habitat de qualité";
  } else if (ndvi >= 0.60 && ndwi < 0.10) {
    return "Végétation dense mais sèche";
  }
  return "Conditions normales pour la saison";
};

// Score Gauge Component
const ScoreGauge = ({ score, size = 'md', label }) => {
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };
  
  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl'
  };

  return (
    <div className={`relative ${sizeClasses[size]} flex items-center justify-center`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-gray-700"
        />
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeDasharray={`${score * 2.83} 283`}
          className={getScoreColor(score)}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold ${textSizes[size]} ${getScoreColor(score)}`}>
          {Math.round(score)}
        </span>
        {label && <span className="text-xs text-gray-400">{label}</span>}
      </div>
    </div>
  );
};

// Module Card Component
const ModuleCard = ({ moduleId, result, onClick }) => {
  const config = MODULE_ICONS[moduleId];
  const Icon = config?.icon || Target;
  
  return (
    <Card 
      className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`w-10 h-10 rounded-lg ${config?.bg} flex items-center justify-center`}>
              <Icon className={`h-5 w-5 ${config?.color}`} />
            </div>
            <div>
              <h4 className="text-white font-medium text-sm">{result.module}</h4>
              <p className="text-gray-500 text-xs">v{result.version}</p>
            </div>
          </div>
          <ScoreGauge score={result.score} size="sm" />
        </div>
        <Badge className={`${getRatingColor(result.rating)} text-xs`}>
          {result.rating}
        </Badge>
        <div className="mt-2 text-xs text-gray-500">
          Confiance: {Math.round(result.confidence * 100)}%
        </div>
      </CardContent>
    </Card>
  );
};

// Species Card Component
const SpeciesCard = ({ speciesId, result, onClick }) => {
  const config = SPECIES_ICONS[speciesId];
  
  return (
    <Card 
      className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {config?.Icon && <config.Icon className="h-8 w-8" style={{ color: config?.color || '#f5a623' }} />}
            <div>
              <h4 className="text-white font-medium">{config?.name}</h4>
              <p className="text-gray-500 text-xs">{result.species}</p>
            </div>
          </div>
          <ScoreGauge score={result.score} size="sm" />
        </div>
        
        <div className="space-y-2 mt-3">
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Habitat</span>
            <span className={getScoreColor(result.habitat_suitability)}>
              {Math.round(result.habitat_suitability)}%
            </span>
          </div>
          <Progress value={result.habitat_suitability} className="h-1" />
          
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Nourriture</span>
            <span className={getScoreColor(result.food_availability)}>
              {Math.round(result.food_availability)}%
            </span>
          </div>
          <Progress value={result.food_availability} className="h-1" />
        </div>
        
        <div className="mt-3 flex items-center justify-between">
          <Badge className={`${getRatingColor(result.rating)} text-xs`}>
            {result.rating}
          </Badge>
          <span className="text-xs text-gray-500">
            {result.hotspots?.length || 0} hotspots
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

// Prediction Card Component
const PredictionCard = ({ predictions }) => {
  if (!predictions) return null;
  
  return (
    <Card className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border-purple-500/30">
      <CardHeader className="pb-2">
        <CardTitle className="text-white flex items-center gap-2 text-lg">
          <Brain className="h-5 w-5 text-purple-400" />
          Prédictions IA
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-purple-400 text-xs mb-1">24h</p>
            {Object.entries(predictions.forecast_24h || {}).slice(0, 3).map(([species, score]) => (
              <div key={species} className="flex items-center justify-between text-xs mt-1">
                <span className="text-gray-400 capitalize">{species}</span>
                <span className={getScoreColor(score)}>{Math.round(score)}</span>
              </div>
            ))}
          </div>
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-blue-400 text-xs mb-1">72h</p>
            {Object.entries(predictions.forecast_72h || {}).slice(0, 3).map(([species, score]) => (
              <div key={species} className="flex items-center justify-between text-xs mt-1">
                <span className="text-gray-400 capitalize">{species}</span>
                <span className={getScoreColor(score)}>{Math.round(score)}</span>
              </div>
            ))}
          </div>
          <div className="text-center p-3 rounded-lg bg-black/20">
            <p className="text-cyan-400 text-xs mb-1">7 jours</p>
            {Object.entries(predictions.forecast_7d || {}).slice(0, 3).map(([species, score]) => (
              <div key={species} className="flex items-center justify-between text-xs mt-1">
                <span className="text-gray-400 capitalize">{species}</span>
                <span className={getScoreColor(score)}>{Math.round(score)}</span>
              </div>
            ))}
          </div>
        </div>
        
        {predictions.movement_prediction && (
          <div className="flex items-center gap-4 p-3 rounded-lg bg-black/20">
            <Compass className="h-5 w-5 text-cyan-400" />
            <div className="flex-1">
              <p className="text-white text-sm">Mouvement prévu</p>
              <p className="text-gray-400 text-xs">
                Direction: {predictions.movement_prediction.primary_direction} • 
                Distance: ~{predictions.movement_prediction.distance_estimate_km} km
              </p>
            </div>
            <Badge className="bg-purple-500/20 text-purple-400">
              {predictions.movement_prediction.activity_peak}
            </Badge>
          </div>
        )}
        
        <div className="text-xs text-gray-500 text-center">
          Confiance: {Math.round((predictions.confidence || 0) * 100)}%
        </div>
      </CardContent>
    </Card>
  );
};

// Main Component
const BionicAnalyzer = ({ territory, onClose, onAnalysisComplete }) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [modules, setModules] = useState([]);
  const [species, setSpecies] = useState([]);
  const [dynamicScores, setDynamicScores] = useState(null);
  
  // Analysis settings
  const [selectedModules, setSelectedModules] = useState([
    'thermal', 'wetness', 'food', 'pressure', 'access', 'corridor', 'geoform', 'canopy'
  ]);
  const [selectedSpecies, setSelectedSpecies] = useState(['moose', 'deer', 'bear']);
  const [includeAI, setIncludeAI] = useState(true);
  const [includeTemporal, setIncludeTemporal] = useState(true);
  
  // Dynamic scoring settings
  const [timeOfDay, setTimeOfDay] = useState('morning');
  const [temperature, setTemperature] = useState(15);
  const [precipitation, setPrecipitation] = useState(0);

  useEffect(() => {
    loadModulesAndSpecies();
  }, []);

  const loadModulesAndSpecies = async () => {
    try {
      const [modulesRes, speciesRes] = await Promise.all([
        axios.get(`${API}/api/bionic/modules`),
        axios.get(`${API}/api/bionic/species`)
      ]);
      setModules(modulesRes.data.modules || []);
      setSpecies(speciesRes.data.species || []);
    } catch (error) {
      console.error('Error loading modules/species:', error);
    }
  };

  const runAnalysis = async () => {
    if (!territory?.coordinates) {
      toast.error('Coordonnées du territoire requises');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await axios.post(`${API}/api/bionic/analyze`, {
        territory_id: territory.id || 'default',
        latitude: territory.coordinates.lat,
        longitude: territory.coordinates.lng,
        radius_km: 5,
        modules: selectedModules,
        species: selectedSpecies,
        include_ai_predictions: includeAI,
        include_temporal: includeTemporal
      });

      if (response.data.success) {
        setAnalysis(response.data.analysis);
        toast.success('Analyse BIONIC™ terminée');
        
        // Appeler le callback pour afficher les couches sur la carte
        if (onAnalysisComplete) {
          console.log('BIONIC: Calling onAnalysisComplete with analysis data', response.data.analysis);
          onAnalysisComplete(response.data.analysis);
        } else {
          console.log('BIONIC: onAnalysisComplete callback is not defined');
        }
      }
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Erreur lors de l\'analyse');
    } finally {
      setAnalyzing(false);
    }
  };

  const runDynamicScoring = async () => {
    if (!territory?.coordinates) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/bionic/ai/dynamic-score`, null, {
        params: {
          territory_id: territory.id || 'default',
          latitude: territory.coordinates.lat,
          longitude: territory.coordinates.lng,
          weather_temp: temperature,
          weather_precip: precipitation,
          time_of_day: timeOfDay
        }
      });

      if (response.data.success) {
        setDynamicScores(response.data.dynamic_scores);
        toast.success('Scores dynamiques calculés');
      }
    } catch (error) {
      console.error('Dynamic scoring error:', error);
      toast.error('Erreur lors du calcul dynamique');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Target className="h-6 w-6 text-[#f5a623]" />
              BIONIC™ Territory Engine
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {territory?.name || 'Analyse avancée du territoire'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={runAnalysis}
              disabled={analyzing}
              className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
            >
              {analyzing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Lancer l'analyse
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="w-full justify-start px-4 pt-2 bg-transparent">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <BarChart3 className="h-4 w-4 mr-2" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="modules" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Target className="h-4 w-4 mr-2" />
            Modules
          </TabsTrigger>
          <TabsTrigger value="species" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Leaf className="h-4 w-4 mr-2" />
            Espèces
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Brain className="h-4 w-4 mr-2" />
            IA & Prédictions
          </TabsTrigger>
          <TabsTrigger value="temporal" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <LineChart className="h-4 w-4 mr-2" />
            Temporel
          </TabsTrigger>
          <TabsTrigger value="settings" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <RefreshCw className="h-4 w-4 mr-2" />
            Paramètres
          </TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1 p-4">
          {/* Overview Tab */}
          <TabsContent value="overview" className="m-0 space-y-4">
            {analysis ? (
              <>
                {/* Overall Score */}
                <Card className="bg-gradient-to-r from-[#f5a623]/10 to-orange-500/10 border-[#f5a623]/30">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-2xl font-bold text-white">Score Global</h3>
                        <p className="text-gray-400">
                          Saison: {analysis.season} • {new Date(analysis.timestamp).toLocaleDateString('fr-CA')}
                        </p>
                        <Badge className={`mt-2 ${getRatingColor(analysis.overall_rating)}`}>
                          {analysis.overall_rating}
                        </Badge>
                      </div>
                      <ScoreGauge score={analysis.overall_score} size="lg" label="/100" />
                    </div>
                  </CardContent>
                </Card>

                {/* Real Conditions - NEW SECTION */}
                {analysis.real_conditions && Object.keys(analysis.real_conditions).length > 0 && (
                  <Card className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border-blue-500/30">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-white text-sm flex items-center gap-2">
                        <Satellite className="h-4 w-4 text-blue-400" />
                        Données en temps réel
                        <Badge className="bg-green-500/20 text-green-400 text-[10px]">LIVE</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {/* Weather */}
                        {analysis.real_conditions.weather && (
                          <div className="bg-black/20 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <Cloud className="h-4 w-4 text-sky-400" />
                              <span className="text-xs text-gray-400">Météo (Open-Meteo)</span>
                            </div>
                            <p className="text-lg font-bold text-white">
                              {analysis.real_conditions.weather.temperature}°C
                            </p>
                            <p className="text-xs text-gray-400">
                              Ressenti: {analysis.real_conditions.weather.feels_like}°C
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {analysis.real_conditions.weather.description}
                            </p>
                            <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-500">
                              <span><Droplets className="h-3 w-3 inline mr-1" />{analysis.real_conditions.weather.humidity}%</span>
                              <span><Wind className="h-3 w-3 inline mr-1" />{analysis.real_conditions.weather.wind_speed} km/h</span>
                            </div>
                          </div>
                        )}
                        
                        {/* Terrain */}
                        {analysis.real_conditions.terrain && (
                          <div className="bg-black/20 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <Mountain className="h-4 w-4 text-amber-400" />
                              <span className="text-xs text-gray-400">Terrain (Open-Elevation)</span>
                            </div>
                            <p className="text-lg font-bold text-white">
                              {analysis.real_conditions.terrain.elevation_m}m
                            </p>
                            <p className="text-xs text-gray-400">
                              Pente: {analysis.real_conditions.terrain.slope_deg?.toFixed(1)}°
                            </p>
                            {analysis.real_conditions.terrain.aspect_deg && (
                              <p className="text-xs text-gray-500 mt-1">
                                Orientation: {analysis.real_conditions.terrain.aspect_deg?.toFixed(0)}°
                              </p>
                            )}
                          </div>
                        )}
                        
                        {/* Vegetation */}
                        {analysis.real_conditions.vegetation && (
                          <div className="bg-black/20 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <TreePine className="h-4 w-4 text-green-400" />
                              <span className="text-xs text-gray-400">Végétation (NASA)</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <div>
                                <p className="text-lg font-bold text-white">
                                  NDVI: {analysis.real_conditions.vegetation.ndvi?.toFixed(2)}
                                </p>
                                <p className="text-xs text-gray-400">
                                  {getNdviLabel(analysis.real_conditions.vegetation.ndvi)}
                                </p>
                              </div>
                              <div className="border-l border-gray-600 pl-3">
                                <p className="text-sm font-medium text-white">
                                  NDWI: {analysis.real_conditions.vegetation.ndwi?.toFixed(2)}
                                </p>
                                <p className="text-xs text-gray-400">
                                  {getNdwiLabel(analysis.real_conditions.vegetation.ndwi)}
                                </p>
                              </div>
                            </div>
                            <div className="mt-2 pt-2 border-t border-gray-700/50">
                              <p className="text-xs text-green-400">
                                {getVegetationConclusion(
                                  analysis.real_conditions.vegetation.ndvi,
                                  analysis.real_conditions.vegetation.ndwi
                                )}
                              </p>
                            </div>
                            <p className="text-[10px] text-gray-500 mt-1 flex items-center gap-1">
                              {analysis.real_conditions.vegetation.source?.includes('AppEEARS') 
                                ? <><Satellite className="h-3 w-3" /> Données satellite NASA</>
                                : <><BarChart3 className="h-3 w-3" /> Estimation saisonnière</>}
                            </p>
                          </div>
                        )}
                      </div>
                      
                      {/* Data Sources */}
                      {analysis.data_sources && analysis.data_sources.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-gray-700/50">
                          <p className="text-[10px] text-gray-500">
                            Sources: {analysis.data_sources.join(' • ')}
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Target className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-white">
                        {Object.keys(analysis.modules || {}).length}
                      </p>
                      <p className="text-xs text-gray-400">Modules analysés</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Leaf className="h-6 w-6 text-green-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-white">
                        {Object.keys(analysis.species || {}).length}
                      </p>
                      <p className="text-xs text-gray-400">Espèces évaluées</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <MapPin className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-white">
                        {Object.values(analysis.species || {}).reduce((acc, s) => acc + (s.hotspots?.length || 0), 0)}
                      </p>
                      <p className="text-xs text-gray-400">Hotspots identifiés</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Brain className="h-6 w-6 text-cyan-400 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-white">
                        {analysis.predictions ? '✓' : '—'}
                      </p>
                      <p className="text-xs text-gray-400">Prédictions IA</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Predictions */}
                {analysis.predictions && (
                  <PredictionCard predictions={analysis.predictions} />
                )}

                {/* Top Species */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">Meilleures espèces</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(analysis.species || {})
                        .sort((a, b) => b[1].score - a[1].score)
                        .slice(0, 3)
                        .map(([speciesId, result]) => {
                          const speciesConfig = SPECIES_ICONS[speciesId];
                          const SpeciesIcon = speciesConfig?.Icon || CircleDot;
                          return (
                            <div key={speciesId} className="flex items-center gap-3 p-2 rounded-lg bg-background">
                              <SpeciesIcon className="h-6 w-6" style={{ color: speciesConfig?.color || '#f5a623' }} />
                              <div className="flex-1">
                                <p className="text-white font-medium">{speciesConfig?.name}</p>
                                <Progress value={result.score} className="h-2 mt-1" />
                              </div>
                              <span className={`text-lg font-bold ${getScoreColor(result.score)}`}>
                                {Math.round(result.score)}
                              </span>
                            </div>
                          );
                        })}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="bg-card border-border">
                <CardContent className="p-8 text-center">
                  <Target className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">
                    Prêt pour l'analyse BIONIC™
                  </h3>
                  <p className="text-gray-400 mb-4">
                    Cliquez sur "Lancer l'analyse" pour obtenir une évaluation complète du territoire
                  </p>
                  <Button
                    onClick={runAnalysis}
                    disabled={analyzing}
                    className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Démarrer
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Modules Tab */}
          <TabsContent value="modules" className="m-0">
            {analysis?.modules ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(analysis.modules).map(([moduleId, result]) => (
                  <ModuleCard key={moduleId} moduleId={moduleId} result={result} />
                ))}
              </div>
            ) : (
              <Card className="bg-card border-border">
                <CardContent className="p-8 text-center">
                  <Info className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Lancez une analyse pour voir les résultats des modules</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Species Tab */}
          <TabsContent value="species" className="m-0">
            {analysis?.species ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(analysis.species).map(([speciesId, result]) => (
                  <SpeciesCard key={speciesId} speciesId={speciesId} result={result} />
                ))}
              </div>
            ) : (
              <Card className="bg-card border-border">
                <CardContent className="p-8 text-center">
                  <Leaf className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Lancez une analyse pour voir les scores des espèces</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* AI Tab */}
          <TabsContent value="ai" className="m-0 space-y-4">
            {/* Dynamic Scoring Card */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-400" />
                  Scoring Dynamique
                </CardTitle>
                <CardDescription>
                  Ajustez les conditions pour voir les scores en temps réel
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label className="text-gray-300">Moment de la journée</Label>
                    <Select value={timeOfDay} onValueChange={setTimeOfDay}>
                      <SelectTrigger className="bg-background">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dawn">Aube</SelectItem>
                        <SelectItem value="morning">Matin</SelectItem>
                        <SelectItem value="midday">Midi</SelectItem>
                        <SelectItem value="afternoon">Après-midi</SelectItem>
                        <SelectItem value="dusk">Crépuscule</SelectItem>
                        <SelectItem value="night">Nuit</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-300">Température: {temperature}°C</Label>
                    <Slider
                      value={[temperature]}
                      onValueChange={(v) => setTemperature(v[0])}
                      min={-30}
                      max={40}
                      step={1}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-300">Précipitations: {precipitation}%</Label>
                    <Slider
                      value={[precipitation]}
                      onValueChange={(v) => setPrecipitation(v[0])}
                      min={0}
                      max={100}
                      step={5}
                    />
                  </div>
                </div>

                <Button onClick={runDynamicScoring} disabled={loading} className="w-full">
                  {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                  Calculer les scores dynamiques
                </Button>

                {dynamicScores && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                    {Object.entries(dynamicScores).map(([species, data]) => {
                      const speciesConfig = SPECIES_ICONS[species];
                      const SpeciesIcon = speciesConfig?.Icon || CircleDot;
                      return (
                        <Card key={species} className="bg-background border-border">
                          <CardContent className="p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <SpeciesIcon className="h-5 w-5" style={{ color: speciesConfig?.color || '#f5a623' }} />
                              <span className="text-white text-sm capitalize">{species}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400 text-xs">Base</span>
                              <span className="text-gray-300">{Math.round(data.base_score)}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400 text-xs">Ajusté</span>
                              <span className={`font-bold ${getScoreColor(data.adjusted_score)}`}>
                                {Math.round(data.adjusted_score)}
                              </span>
                            </div>
                            <Badge className={`mt-2 text-xs ${getRatingColor(data.activity_level)}`}>
                              {data.activity_level}
                            </Badge>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Predictions */}
            {analysis?.predictions && (
              <PredictionCard predictions={analysis.predictions} />
            )}
          </TabsContent>

          {/* Temporal Tab */}
          <TabsContent value="temporal" className="m-0 space-y-4">
            {analysis?.temporal ? (
              <>
                {/* NDVI Trend */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Leaf className="h-5 w-5 text-green-400" />
                      Tendance NDVI (Végétation)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-end gap-1 h-32">
                      {analysis.temporal.ndvi_trend?.map((point, i) => (
                        <div
                          key={i}
                          className="flex-1 bg-green-500/50 rounded-t"
                          style={{ height: `${point.value}%` }}
                          title={`${point.date}: ${point.value}`}
                        />
                      ))}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>{analysis.temporal.ndvi_trend?.[0]?.date}</span>
                      <span>{analysis.temporal.ndvi_trend?.[analysis.temporal.ndvi_trend.length - 1]?.date}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Phenology */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Clock className="h-5 w-5 text-cyan-400" />
                      Phénologie
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-3 rounded-lg bg-background">
                        <p className="text-green-400 text-xs">Verdissement</p>
                        <p className="text-white font-medium">{analysis.temporal.phenology?.green_up_date}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-background">
                        <p className="text-emerald-400 text-xs">Pic de verdure</p>
                        <p className="text-white font-medium">{analysis.temporal.phenology?.peak_greenness}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-background">
                        <p className="text-orange-400 text-xs">Sénescence</p>
                        <p className="text-white font-medium">{analysis.temporal.phenology?.senescence_start}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-background">
                        <p className="text-blue-400 text-xs">Dormance</p>
                        <p className="text-white font-medium">{analysis.temporal.phenology?.dormancy_start}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Anomalies */}
                {analysis.temporal.anomalies?.length > 0 && (
                  <Card className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-yellow-400" />
                        Anomalies détectées
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {analysis.temporal.anomalies.map((anomaly, i) => (
                          <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                            <AlertTriangle className="h-4 w-4 text-yellow-400" />
                            <div className="flex-1">
                              <p className="text-white text-sm">{anomaly.type}</p>
                              <p className="text-gray-400 text-xs">{anomaly.date}</p>
                            </div>
                            <Badge className={anomaly.severity === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}>
                              {anomaly.severity}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card className="bg-card border-border">
                <CardContent className="p-8 text-center">
                  <LineChart className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Lancez une analyse avec l'option temporelle activée</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="m-0 space-y-4">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Paramètres d'analyse</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Modules Selection */}
                <div>
                  <Label className="text-gray-300 mb-3 block">Modules à analyser</Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(MODULE_ICONS).map(([id, config]) => {
                      const Icon = config.icon;
                      const isSelected = selectedModules.includes(id);
                      return (
                        <Button
                          key={id}
                          variant={isSelected ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => {
                            if (isSelected) {
                              setSelectedModules(selectedModules.filter(m => m !== id));
                            } else {
                              setSelectedModules([...selectedModules, id]);
                            }
                          }}
                          className={isSelected ? 'bg-[#f5a623] text-black' : ''}
                        >
                          <Icon className="h-4 w-4 mr-1" />
                          {id}
                        </Button>
                      );
                    })}
                  </div>
                </div>

                {/* Species Selection */}
                <div>
                  <Label className="text-gray-300 mb-3 block">Espèces à évaluer</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {Object.entries(SPECIES_ICONS).map(([id, config]) => {
                      const isSelected = selectedSpecies.includes(id);
                      const SpeciesIcon = config.Icon || CircleDot;
                      return (
                        <Button
                          key={id}
                          variant={isSelected ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => {
                            if (isSelected) {
                              setSelectedSpecies(selectedSpecies.filter(s => s !== id));
                            } else {
                              setSelectedSpecies([...selectedSpecies, id]);
                            }
                          }}
                          className={isSelected ? 'bg-[#f5a623] text-black' : ''}
                        >
                          <SpeciesIcon className="h-4 w-4 mr-1" style={{ color: isSelected ? 'inherit' : config.color }} />
                          {config.name}
                        </Button>
                      );
                    })}
                  </div>
                </div>

                {/* Options */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-300">Prédictions IA</Label>
                      <p className="text-gray-500 text-xs">Inclure les prévisions 24h, 72h, 7j</p>
                    </div>
                    <Switch checked={includeAI} onCheckedChange={setIncludeAI} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-300">Analyse temporelle</Label>
                      <p className="text-gray-500 text-xs">Tendances NDVI/NDWI sur 12 mois</p>
                    </div>
                    <Switch checked={includeTemporal} onCheckedChange={setIncludeTemporal} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  );
};

export default BionicAnalyzer;
