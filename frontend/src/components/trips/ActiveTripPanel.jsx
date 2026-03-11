/**
 * ActiveTripPanel - Panel for managing an active hunting trip
 * BIONIC Design System compliant
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import {
  Play, Square, Clock, Eye, Footprints, Volume2, Target, MapPin,
  Thermometer, Wind, Cloud, Plus, CheckCircle, XCircle, Loader2,
  AlertTriangle, Crosshair, Sun, CloudSun, CloudRain, Snowflake, CloudFog, CircleDot, Leaf
} from 'lucide-react';
import TripService from '@/services/TripService';

// BIONIC Design System - Weather options with Lucide icons
const WEATHER_OPTIONS = [
  { value: 'sunny', label: 'Ensoleillé', Icon: Sun, color: '#f5a623' },
  { value: 'cloudy', label: 'Nuageux', Icon: Cloud, color: '#9ca3af' },
  { value: 'overcast', label: 'Couvert', Icon: CloudSun, color: '#6b7280' },
  { value: 'rainy', label: 'Pluvieux', Icon: CloudRain, color: '#3b82f6' },
  { value: 'snowy', label: 'Neigeux', Icon: Snowflake, color: '#06b6d4' },
  { value: 'foggy', label: 'Brumeux', Icon: CloudFog, color: '#64748b' },
  { value: 'windy', label: 'Venteux', Icon: Wind, color: '#8b5cf6' }
];

// BIONIC Design System - Observation types with Lucide icons
const OBSERVATION_TYPES = [
  { value: 'sighting', label: 'Observation visuelle', Icon: Eye, color: '#22c55e' },
  { value: 'tracks', label: 'Pistes/Traces', Icon: Footprints, color: '#f59e0b' },
  { value: 'sounds', label: 'Sons entendus', Icon: Volume2, color: '#8b5cf6' },
  { value: 'signs', label: 'Indices (frottoirs, etc.)', Icon: Leaf, color: '#10b981' },
  { value: 'harvest', label: 'Récolte', Icon: Crosshair, color: '#ef4444' }
];

// BIONIC Design System - Species config with colors
const SPECIES_CONFIG = {
  deer: { label: 'Cerf', Icon: CircleDot, color: '#D2691E' },
  moose: { label: 'Orignal', Icon: CircleDot, color: '#8B4513' },
  bear: { label: 'Ours', Icon: CircleDot, color: '#2F4F4F' },
  turkey: { label: 'Dindon', Icon: CircleDot, color: '#ef4444' },
  duck: { label: 'Canard', Icon: CircleDot, color: '#3b82f6' },
  goose: { label: 'Oie', Icon: CircleDot, color: '#6b7280' },
  grouse: { label: 'Gélinotte', Icon: CircleDot, color: '#a855f7' },
  rabbit: { label: 'Lièvre', Icon: CircleDot, color: '#f59e0b' },
  coyote: { label: 'Coyote', Icon: CircleDot, color: '#64748b' },
  other: { label: 'Autre', Icon: Target, color: '#9ca3af' }
};

const ActiveTripPanel = ({ trip, onTripEnded, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [observations, setObservations] = useState([]);
  const [showObservationModal, setShowObservationModal] = useState(false);
  const [showEndTripModal, setShowEndTripModal] = useState(false);
  const [elapsedTime, setElapsedTime] = useState('0:00');

  // Calculate elapsed time
  useEffect(() => {
    if (!trip.start_time) return;

    const updateElapsed = () => {
      const start = new Date(trip.start_time);
      const now = new Date();
      const diff = Math.floor((now - start) / 1000);
      const hours = Math.floor(diff / 3600);
      const minutes = Math.floor((diff % 3600) / 60);
      setElapsedTime(`${hours}:${minutes.toString().padStart(2, '0')}`);
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 60000);
    return () => clearInterval(interval);
  }, [trip.start_time]);

  // Load observations
  useEffect(() => {
    loadObservations();
  }, [trip.trip_id]);

  const loadObservations = async () => {
    const obs = await TripService.listObservations(trip.trip_id);
    setObservations(Array.isArray(obs) ? obs : []);
  };

  const handleObservationAdded = () => {
    setShowObservationModal(false);
    loadObservations();
    onRefresh();
  };

  return (
    <div className="space-y-6">
      {/* Trip Info Card */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                {(() => {
                  const speciesConfig = SPECIES_CONFIG[trip.target_species] || SPECIES_CONFIG.other;
                  const SpeciesIcon = speciesConfig.Icon;
                  return <SpeciesIcon className="h-6 w-6" style={{ color: speciesConfig.color }} />;
                })()}
                {trip.title}
              </CardTitle>
              <p className="text-gray-400 text-sm mt-1">
                Espèce: {SPECIES_CONFIG[trip.target_species]?.label || trip.target_species} • Statut: En cours
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-emerald-400">
                <Clock className="h-5 w-5" />
                <span className="text-2xl font-mono font-bold">{elapsedTime}</span>
              </div>
              <p className="text-xs text-gray-500">Temps écoulé</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Weather Info */}
          {trip.weather && (
            <div className="flex items-center gap-4 mb-4 p-3 bg-slate-700/30 rounded-lg">
              <div className="flex items-center gap-2">
                {(() => {
                  const weatherConfig = WEATHER_OPTIONS.find(w => w.value === trip.weather);
                  const WeatherIcon = weatherConfig?.Icon || Cloud;
                  return <WeatherIcon className="h-4 w-4" style={{ color: weatherConfig?.color || '#9ca3af' }} />;
                })()}
                <span className="text-gray-300">
                  {WEATHER_OPTIONS.find(w => w.value === trip.weather)?.label || trip.weather}
                </span>
              </div>
              {trip.temperature !== null && (
                <div className="flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-orange-400" />
                  <span className="text-gray-300">{trip.temperature}°C</span>
                </div>
              )}
              {trip.wind_speed !== null && (
                <div className="flex items-center gap-2">
                  <Wind className="h-4 w-4 text-cyan-400" />
                  <span className="text-gray-300">{trip.wind_speed} km/h</span>
                </div>
              )}
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-slate-700/30 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-white">{trip.observations_count || 0}</p>
              <p className="text-xs text-gray-400">Observations</p>
            </div>
            <div className="bg-slate-700/30 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-white">{trip.visited_waypoints?.length || 0}</p>
              <p className="text-xs text-gray-400">Waypoints visités</p>
            </div>
            <div className="bg-slate-700/30 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-white">{trip.duration_hours || 0}</p>
              <p className="text-xs text-gray-400">Heures</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={() => setShowObservationModal(true)}
              className="flex-1 bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter Observation
            </Button>
            <Button
              onClick={() => setShowEndTripModal(true)}
              variant="destructive"
              className="flex-1"
            >
              <Square className="h-4 w-4 mr-2" />
              Terminer Sortie
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Observations List */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Eye className="h-5 w-5 text-purple-400" />
            Observations ({observations.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {observations.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Eye className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>Aucune observation encore</p>
              <p className="text-sm">Ajoutez vos premières observations</p>
            </div>
          ) : (
            <div className="space-y-3">
              {observations.map((obs, idx) => {
                const obsTypeConfig = OBSERVATION_TYPES.find(t => t.value === obs.observation_type);
                const ObsIcon = obsTypeConfig?.Icon || Eye;
                const speciesConfig = SPECIES_CONFIG[obs.species] || SPECIES_CONFIG.other;
                const SpeciesIcon = speciesConfig.Icon;
                
                return (
                  <div 
                    key={obs.observation_id || idx}
                    className="flex items-center gap-3 p-3 bg-slate-700/30 rounded-lg"
                  >
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                      <ObsIcon className="h-5 w-5" style={{ color: obsTypeConfig?.color || '#a78bfa' }} />
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-medium flex items-center gap-1">
                        <SpeciesIcon className="h-4 w-4" style={{ color: speciesConfig.color }} /> {speciesConfig.label} x{obs.count}
                      </p>
                      <p className="text-xs text-gray-400">
                        {obsTypeConfig?.label || obs.observation_type}
                        {obs.distance_meters && ` • ${obs.distance_meters}m`}
                        {obs.behavior && ` • ${obs.behavior}`}
                      </p>
                    </div>
                    <Badge 
                      className={obs.observation_type === 'harvest' ? 'bg-amber-600' : 'bg-slate-600'}
                    >
                      {obs.observation_type === 'harvest' ? 'Récolte!' : 'Obs'}
                    </Badge>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Observation Modal */}
      <AddObservationModal
        open={showObservationModal}
        onClose={() => setShowObservationModal(false)}
        tripId={trip.trip_id}
        targetSpecies={trip.target_species}
        onObservationAdded={handleObservationAdded}
      />

      {/* End Trip Modal */}
      <EndTripModal
        open={showEndTripModal}
        onClose={() => setShowEndTripModal(false)}
        trip={trip}
        onTripEnded={onTripEnded}
      />
    </div>
  );
};

// Add Observation Modal Component
const AddObservationModal = ({ open, onClose, tripId, targetSpecies, onObservationAdded }) => {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    observation_type: 'sighting',
    species: targetSpecies,
    count: 1,
    distance_meters: '',
    behavior: '',
    notes: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await TripService.logObservation({
        trip_id: tripId,
        observation_type: form.observation_type,
        species: form.species,
        count: parseInt(form.count) || 1,
        distance_meters: form.distance_meters ? parseFloat(form.distance_meters) : null,
        behavior: form.behavior || null,
        notes: form.notes || null
      });

      if (result.success) {
        toast.success('Observation ajoutée!');
        onObservationAdded();
        // Reset form
        setForm({
          observation_type: 'sighting',
          species: targetSpecies,
          count: 1,
          distance_meters: '',
          behavior: '',
          notes: ''
        });
      } else {
        toast.error(result.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-slate-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-purple-400" />
            Nouvelle Observation
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {/* Type */}
          <div className="space-y-2">
            <Label className="text-gray-300">Type d'observation</Label>
            <Select
              value={form.observation_type}
              onValueChange={(value) => setForm({ ...form, observation_type: value })}
            >
              <SelectTrigger className="bg-slate-800 border-slate-600">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {OBSERVATION_TYPES.map((type) => {
                  const TypeIcon = type.Icon;
                  return (
                    <SelectItem key={type.value} value={type.value} className="text-white">
                      <span className="flex items-center gap-2">
                        <TypeIcon className="h-4 w-4" style={{ color: type.color }} />
                        {type.label}
                      </span>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>

          {/* Species & Count */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-gray-300">Espèce</Label>
              <Input
                value={form.species}
                onChange={(e) => setForm({ ...form, species: e.target.value })}
                className="bg-slate-800 border-slate-600"
                placeholder="Espèce observée"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300">Nombre</Label>
              <Input
                type="number"
                min="1"
                value={form.count}
                onChange={(e) => setForm({ ...form, count: e.target.value })}
                className="bg-slate-800 border-slate-600"
              />
            </div>
          </div>

          {/* Distance & Behavior */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-gray-300">Distance (m)</Label>
              <Input
                type="number"
                value={form.distance_meters}
                onChange={(e) => setForm({ ...form, distance_meters: e.target.value })}
                className="bg-slate-800 border-slate-600"
                placeholder="Optionnel"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300">Comportement</Label>
              <Input
                value={form.behavior}
                onChange={(e) => setForm({ ...form, behavior: e.target.value })}
                className="bg-slate-800 border-slate-600"
                placeholder="Ex: alimentation"
              />
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label className="text-gray-300">Notes</Label>
            <Textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              className="bg-slate-800 border-slate-600 resize-none"
              rows={2}
              placeholder="Détails supplémentaires..."
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-slate-600"
              disabled={loading}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-purple-600 hover:bg-purple-700"
              disabled={loading}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Ajouter'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// End Trip Modal Component
const EndTripModal = ({ open, onClose, trip, onTripEnded }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [notes, setNotes] = useState('');

  const handleEndTrip = async () => {
    setLoading(true);

    try {
      const result = await TripService.endTrip(trip.trip_id, success, notes);

      if (result.success) {
        toast.success(result.message || 'Sortie terminée!');
        onTripEnded();
        onClose();
      } else {
        toast.error(result.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-slate-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Square className="h-5 w-5 text-red-400" />
            Terminer la Sortie
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Résumé de votre sortie de chasse
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Trip Summary */}
          <div className="bg-slate-800/50 rounded-lg p-4">
            <h4 className="text-white font-medium mb-2">{trip.title}</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-gray-400">Espèce:</div>
              <div className="text-white flex items-center gap-1">
                {(() => {
                  const speciesConfig = SPECIES_CONFIG[trip.target_species] || SPECIES_CONFIG.other;
                  const SpeciesIcon = speciesConfig.Icon;
                  return <SpeciesIcon className="h-4 w-4" style={{ color: speciesConfig.color }} />;
                })()}
                {SPECIES_CONFIG[trip.target_species]?.label || trip.target_species}
              </div>
              <div className="text-gray-400">Observations:</div>
              <div className="text-white">{trip.observations_count || 0}</div>
              <div className="text-gray-400">Waypoints:</div>
              <div className="text-white">{trip.visited_waypoints?.length || 0}</div>
            </div>
          </div>

          {/* Success Toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
            <div className="flex items-center gap-3">
              {success ? (
                <CheckCircle className="h-6 w-6 text-emerald-400" />
              ) : (
                <XCircle className="h-6 w-6 text-gray-400" />
              )}
              <div>
                <p className="text-white font-medium">Sortie réussie?</p>
                <p className="text-xs text-gray-400">Avez-vous atteint votre objectif?</p>
              </div>
            </div>
            <Checkbox
              checked={success}
              onCheckedChange={setSuccess}
              className="h-6 w-6"
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label className="text-gray-300">Notes de fin de sortie</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="bg-slate-800 border-slate-600 resize-none"
              rows={3}
              placeholder="Résumé, leçons apprises, etc."
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1 border-slate-600"
              disabled={loading}
            >
              Continuer la sortie
            </Button>
            <Button
              onClick={handleEndTrip}
              variant="destructive"
              className="flex-1"
              disabled={loading}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Terminer'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ActiveTripPanel;
