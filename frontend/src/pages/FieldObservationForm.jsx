/**
 * FieldObservationForm - Formulaire de saisie des observations terrain
 * =====================================================================
 * PHASE F — GPS ULTIMATE
 * 
 * Interface pour capturer les observations de faune sur le terrain.
 * Ces données alimentent le CalibrationRegistry pour atteindre 95%+ de précision.
 */

import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  MapPin, 
  Calendar, 
  Compass, 
  Eye, 
  Cloud, 
  Thermometer,
  Wind,
  Send,
  ChevronLeft,
  Check,
  AlertCircle,
  Target,
  Camera,
  Radio,
  Footprints,
  Volume2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// =============================================================================
// CONFIGURATION
// =============================================================================

const SPECIES_OPTIONS = [
  { value: 'moose', label: 'Orignal', icon: '🦌' },
  { value: 'deer', label: 'Cerf de Virginie', icon: '🦌' },
  { value: 'mule_deer', label: 'Cerf-mulet', icon: '🦌' },
  { value: 'bear', label: 'Ours noir', icon: '🐻' },
  { value: 'elk', label: 'Wapiti', icon: '🦌' },
  { value: 'other', label: 'Autre', icon: '❓' }
];

const BEHAVIOR_OPTIONS = [
  { value: 'feeding', label: 'Alimentation', description: 'L\'animal mange ou broute' },
  { value: 'resting', label: 'Repos', description: 'L\'animal est couché ou immobile' },
  { value: 'moving', label: 'Déplacement', description: 'L\'animal se déplace activement' },
  { value: 'drinking', label: 'Abreuvement', description: 'L\'animal boit à un point d\'eau' },
  { value: 'rut_activity', label: 'Activité de rut', description: 'Comportement de reproduction' },
  { value: 'alert', label: 'Vigilance', description: 'L\'animal est aux aguets' },
  { value: 'grooming', label: 'Toilettage', description: 'L\'animal se nettoie' },
  { value: 'social', label: 'Interaction sociale', description: 'Interaction avec d\'autres animaux' },
  { value: 'unknown', label: 'Inconnu', description: 'Comportement non identifié' }
];

const WEATHER_OPTIONS = [
  { value: 'clear', label: 'Dégagé', icon: '☀️' },
  { value: 'cloudy', label: 'Nuageux', icon: '☁️' },
  { value: 'rain', label: 'Pluie', icon: '🌧️' },
  { value: 'snow', label: 'Neige', icon: '❄️' },
  { value: 'fog', label: 'Brouillard', icon: '🌫️' },
  { value: 'wind', label: 'Venteux', icon: '💨' }
];

const SOURCE_OPTIONS = [
  { value: 'direct_visual', label: 'Observation directe', icon: Eye },
  { value: 'trail_camera', label: 'Caméra de trail', icon: Camera },
  { value: 'gps_collar', label: 'Collier GPS', icon: Radio },
  { value: 'tracks', label: 'Traces/Indices', icon: Footprints },
  { value: 'audio', label: 'Vocalisation', icon: Volume2 },
  { value: 'other', label: 'Autre', icon: Target }
];

const CONFIDENCE_OPTIONS = [
  { value: 'high', label: 'Élevée', color: '#00A676', description: 'Observation claire et directe' },
  { value: 'medium', label: 'Moyenne', color: '#FFA500', description: 'Observation partielle' },
  { value: 'low', label: 'Faible', color: '#B91C1C', description: 'Indices indirects' }
];

// =============================================================================
// COMPOSANT PRINCIPAL
// =============================================================================

const FieldObservationForm = () => {
  // État du formulaire
  const [formData, setFormData] = useState({
    species: 'moose',
    species_count: 1,
    latitude: '',
    longitude: '',
    observation_datetime: new Date().toISOString().slice(0, 16),
    behavior: 'unknown',
    behavior_details: '',
    weather: 'clear',
    temperature_c: '',
    wind_speed_kmh: '',
    source: 'direct_visual',
    confidence: 'medium',
    notes: '',
    observer_name: '',
    habitat_observed: '',
    terrain_type: '',
    vegetation_type: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [stats, setStats] = useState(null);

  // Charger les statistiques au montage
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/bionic/observations/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data.statistics);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des stats:', error);
    }
  };

  // Obtenir la position GPS actuelle
  const getCurrentPosition = () => {
    if (!navigator.geolocation) {
      toast.error('Géolocalisation non supportée par votre navigateur');
      return;
    }

    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData(prev => ({
          ...prev,
          latitude: position.coords.latitude.toFixed(6),
          longitude: position.coords.longitude.toFixed(6)
        }));
        setGpsLoading(false);
        toast.success('Position GPS obtenue');
      },
      (error) => {
        setGpsLoading(false);
        toast.error(`Erreur GPS: ${error.message}`);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  // Gestion des changements de champs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Validation
    if (!formData.latitude || !formData.longitude) {
      toast.error('Position GPS requise');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        species_count: parseInt(formData.species_count) || 1,
        temperature_c: formData.temperature_c ? parseFloat(formData.temperature_c) : null,
        wind_speed_kmh: formData.wind_speed_kmh ? parseFloat(formData.wind_speed_kmh) : null,
        observation_datetime: formData.observation_datetime ? new Date(formData.observation_datetime).toISOString() : null
      };

      const response = await fetch(`${API_URL}/api/v1/bionic/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'envoi');
      }

      const data = await response.json();
      
      setSubmitSuccess(true);
      toast.success('Observation enregistrée avec succès !');
      
      // Rafraîchir les stats
      fetchStats();

      // Reset après 3 secondes
      setTimeout(() => {
        setSubmitSuccess(false);
        setCurrentStep(1);
        setFormData(prev => ({
          ...prev,
          species_count: 1,
          behavior: 'unknown',
          behavior_details: '',
          notes: '',
          observation_datetime: new Date().toISOString().slice(0, 16)
        }));
      }, 3000);

    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de l\'envoi de l\'observation');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Rendu des étapes
  const totalSteps = 4;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white p-4 md:p-8">
      {/* Header */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
            <Target className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Observation Terrain</h1>
            <p className="text-slate-400 text-sm">PHASE F — Calibration BIONIC V5 MASTER</p>
          </div>
        </div>

        {/* Stats globales */}
        {stats && (
          <div className="grid grid-cols-3 gap-3 mb-6">
            <div className="bg-slate-800/60 rounded-lg p-3 border border-slate-700">
              <div className="text-2xl font-bold text-emerald-400">{stats.total_observations || 0}</div>
              <div className="text-xs text-slate-400">Observations</div>
            </div>
            <div className="bg-slate-800/60 rounded-lg p-3 border border-slate-700">
              <div className="text-2xl font-bold text-amber-400">{stats.validated_observations || 0}</div>
              <div className="text-xs text-slate-400">Validées</div>
            </div>
            <div className="bg-slate-800/60 rounded-lg p-3 border border-slate-700">
              <div className="text-2xl font-bold text-blue-400">{stats.validation_rate || 0}%</div>
              <div className="text-xs text-slate-400">Taux validation</div>
            </div>
          </div>
        )}

        {/* Progress bar */}
        <div className="flex items-center gap-2 mb-6">
          {[1, 2, 3, 4].map((step) => (
            <React.Fragment key={step}>
              <div 
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all
                  ${currentStep >= step 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-slate-700 text-slate-400'}`}
              >
                {currentStep > step ? <Check className="w-4 h-4" /> : step}
              </div>
              {step < 4 && (
                <div className={`flex-1 h-1 rounded ${currentStep > step ? 'bg-emerald-500' : 'bg-slate-700'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Formulaire */}
      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
        {/* Étape 1: Espèce et Position */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fadeIn" data-testid="step-1-species-position">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-400" />
              Espèce et Position
            </h2>

            {/* Sélection espèce */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Espèce observée *</label>
              <div className="grid grid-cols-3 gap-2">
                {SPECIES_OPTIONS.map((species) => (
                  <button
                    key={species.value}
                    type="button"
                    data-testid={`species-${species.value}`}
                    onClick={() => setFormData(prev => ({ ...prev, species: species.value }))}
                    className={`p-3 rounded-lg border transition-all text-center
                      ${formData.species === species.value 
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' 
                        : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'}`}
                  >
                    <span className="text-2xl block mb-1">{species.icon}</span>
                    <span className="text-xs">{species.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Nombre d'individus */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Nombre d'individus</label>
              <input
                type="number"
                name="species_count"
                value={formData.species_count}
                onChange={handleChange}
                min="1"
                max="50"
                data-testid="species-count-input"
                className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            {/* Position GPS */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Position GPS *</label>
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  name="latitude"
                  value={formData.latitude}
                  onChange={handleChange}
                  placeholder="Latitude"
                  data-testid="latitude-input"
                  className="bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
                />
                <input
                  type="text"
                  name="longitude"
                  value={formData.longitude}
                  onChange={handleChange}
                  placeholder="Longitude"
                  data-testid="longitude-input"
                  className="bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <button
                type="button"
                onClick={getCurrentPosition}
                disabled={gpsLoading}
                data-testid="get-gps-button"
                className="mt-3 w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 rounded-lg px-4 py-3 transition-colors"
              >
                <Compass className={`w-5 h-5 ${gpsLoading ? 'animate-spin' : ''}`} />
                {gpsLoading ? 'Obtention de la position...' : 'Utiliser ma position actuelle'}
              </button>
            </div>

            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              disabled={!formData.latitude || !formData.longitude}
              data-testid="next-step-1-button"
              className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:opacity-50 rounded-lg px-6 py-4 font-medium transition-colors"
            >
              Continuer
            </button>
          </div>
        )}

        {/* Étape 2: Comportement */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fadeIn" data-testid="step-2-behavior">
            <div className="flex items-center gap-2 mb-4">
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Eye className="w-5 h-5 text-amber-400" />
                Comportement observé
              </h2>
            </div>

            {/* Date/heure */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Date et heure de l'observation</label>
              <input
                type="datetime-local"
                name="observation_datetime"
                value={formData.observation_datetime}
                onChange={handleChange}
                data-testid="datetime-input"
                className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Sélection comportement */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Type de comportement</label>
              <div className="grid grid-cols-1 gap-2">
                {BEHAVIOR_OPTIONS.map((behavior) => (
                  <button
                    key={behavior.value}
                    type="button"
                    data-testid={`behavior-${behavior.value}`}
                    onClick={() => setFormData(prev => ({ ...prev, behavior: behavior.value }))}
                    className={`p-3 rounded-lg border transition-all text-left
                      ${formData.behavior === behavior.value 
                        ? 'bg-amber-500/20 border-amber-500' 
                        : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'}`}
                  >
                    <span className="font-medium">{behavior.label}</span>
                    <span className="text-xs text-slate-400 block mt-1">{behavior.description}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Détails comportement */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Détails du comportement</label>
              <textarea
                name="behavior_details"
                value={formData.behavior_details}
                onChange={handleChange}
                rows={3}
                placeholder="Décrivez ce que vous avez observé..."
                data-testid="behavior-details-input"
                className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500 resize-none"
              />
            </div>

            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              data-testid="next-step-2-button"
              className="w-full bg-emerald-500 hover:bg-emerald-600 rounded-lg px-6 py-4 font-medium transition-colors"
            >
              Continuer
            </button>
          </div>
        )}

        {/* Étape 3: Conditions */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fadeIn" data-testid="step-3-conditions">
            <div className="flex items-center gap-2 mb-4">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Cloud className="w-5 h-5 text-blue-400" />
                Conditions et Source
              </h2>
            </div>

            {/* Météo */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Conditions météo</label>
              <div className="grid grid-cols-3 gap-2">
                {WEATHER_OPTIONS.map((weather) => (
                  <button
                    key={weather.value}
                    type="button"
                    data-testid={`weather-${weather.value}`}
                    onClick={() => setFormData(prev => ({ ...prev, weather: weather.value }))}
                    className={`p-3 rounded-lg border transition-all text-center
                      ${formData.weather === weather.value 
                        ? 'bg-blue-500/20 border-blue-500' 
                        : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'}`}
                  >
                    <span className="text-2xl block mb-1">{weather.icon}</span>
                    <span className="text-xs">{weather.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Température et vent */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">
                  <Thermometer className="w-4 h-4 inline mr-1" />
                  Température (°C)
                </label>
                <input
                  type="number"
                  name="temperature_c"
                  value={formData.temperature_c}
                  onChange={handleChange}
                  placeholder="-10"
                  data-testid="temperature-input"
                  className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">
                  <Wind className="w-4 h-4 inline mr-1" />
                  Vent (km/h)
                </label>
                <input
                  type="number"
                  name="wind_speed_kmh"
                  value={formData.wind_speed_kmh}
                  onChange={handleChange}
                  placeholder="15"
                  data-testid="wind-input"
                  className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            {/* Source */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Source de l'observation</label>
              <div className="grid grid-cols-2 gap-2">
                {SOURCE_OPTIONS.map((source) => {
                  const Icon = source.icon;
                  return (
                    <button
                      key={source.value}
                      type="button"
                      data-testid={`source-${source.value}`}
                      onClick={() => setFormData(prev => ({ ...prev, source: source.value }))}
                      className={`p-3 rounded-lg border transition-all flex items-center gap-3
                        ${formData.source === source.value 
                          ? 'bg-purple-500/20 border-purple-500' 
                          : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'}`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-sm">{source.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Confiance */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Niveau de confiance</label>
              <div className="grid grid-cols-3 gap-2">
                {CONFIDENCE_OPTIONS.map((conf) => (
                  <button
                    key={conf.value}
                    type="button"
                    data-testid={`confidence-${conf.value}`}
                    onClick={() => setFormData(prev => ({ ...prev, confidence: conf.value }))}
                    className={`p-3 rounded-lg border transition-all text-center
                      ${formData.confidence === conf.value 
                        ? `bg-opacity-20 border-2` 
                        : 'bg-slate-800/60 border-slate-700 hover:border-slate-600'}`}
                    style={formData.confidence === conf.value ? { 
                      backgroundColor: `${conf.color}20`, 
                      borderColor: conf.color 
                    } : {}}
                  >
                    <span className="font-medium">{conf.label}</span>
                    <span className="text-xs text-slate-400 block mt-1">{conf.description}</span>
                  </button>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              data-testid="next-step-3-button"
              className="w-full bg-emerald-500 hover:bg-emerald-600 rounded-lg px-6 py-4 font-medium transition-colors"
            >
              Continuer
            </button>
          </div>
        )}

        {/* Étape 4: Récapitulatif et envoi */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fadeIn" data-testid="step-4-summary">
            <div className="flex items-center gap-2 mb-4">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Send className="w-5 h-5 text-emerald-400" />
                Notes et envoi
              </h2>
            </div>

            {/* Observateur */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Nom de l'observateur</label>
              <input
                type="text"
                name="observer_name"
                value={formData.observer_name}
                onChange={handleChange}
                placeholder="Votre nom (optionnel)"
                data-testid="observer-name-input"
                className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-300">Notes supplémentaires</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                placeholder="Toute information complémentaire utile pour la calibration..."
                data-testid="notes-input"
                className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-emerald-500 resize-none"
              />
            </div>

            {/* Habitat (optionnel) */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Habitat</label>
                <input
                  type="text"
                  name="habitat_observed"
                  value={formData.habitat_observed}
                  onChange={handleChange}
                  placeholder="Ex: Lisière"
                  data-testid="habitat-input"
                  className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Terrain</label>
                <input
                  type="text"
                  name="terrain_type"
                  value={formData.terrain_type}
                  onChange={handleChange}
                  placeholder="Ex: Plat"
                  data-testid="terrain-input"
                  className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-300">Végétation</label>
                <input
                  type="text"
                  name="vegetation_type"
                  value={formData.vegetation_type}
                  onChange={handleChange}
                  placeholder="Ex: Mixte"
                  data-testid="vegetation-input"
                  className="w-full bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            {/* Récapitulatif */}
            <div className="bg-slate-800/60 rounded-lg p-4 border border-slate-700">
              <h3 className="font-medium mb-3 text-emerald-400">Récapitulatif</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-slate-400">Espèce:</div>
                <div>{SPECIES_OPTIONS.find(s => s.value === formData.species)?.label} ({formData.species_count})</div>
                <div className="text-slate-400">Position:</div>
                <div>{formData.latitude}, {formData.longitude}</div>
                <div className="text-slate-400">Comportement:</div>
                <div>{BEHAVIOR_OPTIONS.find(b => b.value === formData.behavior)?.label}</div>
                <div className="text-slate-400">Conditions:</div>
                <div>{WEATHER_OPTIONS.find(w => w.value === formData.weather)?.label} {formData.temperature_c && `${formData.temperature_c}°C`}</div>
                <div className="text-slate-400">Source:</div>
                <div>{SOURCE_OPTIONS.find(s => s.value === formData.source)?.label}</div>
                <div className="text-slate-400">Confiance:</div>
                <div>{CONFIDENCE_OPTIONS.find(c => c.value === formData.confidence)?.label}</div>
              </div>
            </div>

            {/* Succès */}
            {submitSuccess && (
              <div className="bg-emerald-500/20 border border-emerald-500 rounded-lg p-4 flex items-center gap-3" data-testid="success-message">
                <Check className="w-6 h-6 text-emerald-400" />
                <div>
                  <div className="font-medium text-emerald-400">Observation enregistrée !</div>
                  <div className="text-sm text-slate-300">Cette donnée contribue à la calibration BIONIC V5 MASTER.</div>
                </div>
              </div>
            )}

            {/* Bouton envoi */}
            <button
              type="submit"
              disabled={isSubmitting || submitSuccess}
              data-testid="submit-observation-button"
              className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 disabled:from-slate-600 disabled:to-slate-600 rounded-lg px-6 py-4 font-medium transition-all flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Envoi en cours...
                </>
              ) : submitSuccess ? (
                <>
                  <Check className="w-5 h-5" />
                  Enregistré !
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Envoyer l'observation
                </>
              )}
            </button>
          </div>
        )}
      </form>

      {/* Info footer */}
      <div className="max-w-2xl mx-auto mt-8 text-center text-xs text-slate-500">
        <p>PHASE F — GPS ULTIMATE</p>
        <p>Les observations validées contribuent à atteindre 95%+ de précision pour BIONIC V5 MASTER</p>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default FieldObservationForm;
