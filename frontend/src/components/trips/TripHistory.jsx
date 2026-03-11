/**
 * TripHistory - List and manage past hunting trips
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from '@/components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  Calendar, Clock, Play, CheckCircle, XCircle, Target, Eye,
  Thermometer, Cloud, Loader2, ChevronRight, AlertTriangle,
  Sun, CloudRain, Snowflake, Wind, CloudFog, CloudSun, CircleDot
} from 'lucide-react';
import TripService from '@/services/TripService';
import { useLanguage } from '@/contexts/LanguageContext';

const WEATHER_OPTIONS = [
  { value: 'sunny', label: 'Ensoleillé', icon: Sun },
  { value: 'cloudy', label: 'Nuageux', icon: Cloud },
  { value: 'overcast', label: 'Couvert', icon: CloudSun },
  { value: 'rainy', label: 'Pluvieux', icon: CloudRain },
  { value: 'snowy', label: 'Neigeux', icon: Snowflake },
  { value: 'foggy', label: 'Brumeux', icon: CloudFog },
  { value: 'windy', label: 'Venteux', icon: Wind }
];

// BIONIC Design System - Lucide icons for species
const SPECIES_ICONS = {
  deer: CircleDot,
  moose: CircleDot,
  bear: CircleDot,
  turkey: CircleDot,
  duck: CircleDot,
  goose: CircleDot,
  grouse: CircleDot,
  rabbit: CircleDot,
  coyote: CircleDot,
  other: Target
};

const STATUS_CONFIG = {
  planned: { label: 'Planifiée', color: 'bg-[var(--bionic-blue-light)]', icon: Calendar },
  in_progress: { label: 'En cours', color: 'bg-[var(--bionic-green-primary)]', icon: Play },
  completed: { label: 'Terminée', color: 'bg-[var(--bionic-gray-600)]', icon: CheckCircle },
  cancelled: { label: 'Annulée', color: 'bg-[var(--bionic-red-primary)]', icon: XCircle }
};

const TripHistory = ({ trips, onTripStarted, onRefresh }) => {
  const { t } = useLanguage();
  const [showStartModal, setShowStartModal] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState(null);

  const handleStartClick = (trip) => {
    setSelectedTrip(trip);
    setShowStartModal(true);
  };

  const plannedTrips = trips.filter(t => t.status === 'planned');
  const completedTrips = trips.filter(t => t.status === 'completed');
  const inProgressTrips = trips.filter(t => t.status === 'in_progress');

  return (
    <div className="space-y-6">
      {/* In Progress Trips */}
      {inProgressTrips.length > 0 && (
        <Card className="bg-[var(--bionic-green-muted)] border-[var(--bionic-green-primary)]/50">
          <CardHeader>
            <CardTitle className="text-[var(--bionic-green-primary)] flex items-center gap-2">
              <Play className="h-5 w-5" />
              {t('trips_in_progress') || 'Sorties en cours'} ({inProgressTrips.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {inProgressTrips.map((trip) => (
                <TripCard key={trip.trip_id} trip={trip} t={t} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Planned Trips */}
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <CardHeader>
          <CardTitle className="text-[var(--bionic-blue-light)] flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            {t('trips_planned') || 'Sorties planifiées'} ({plannedTrips.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {plannedTrips.length === 0 ? (
            <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
              <Calendar className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>{t('trips_no_planned') || 'Aucune sortie planifiée'}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {plannedTrips.map((trip) => (
                <TripCard 
                  key={trip.trip_id} 
                  trip={trip} 
                  t={t}
                  onStartClick={() => handleStartClick(trip)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Completed Trips */}
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <CardHeader>
          <CardTitle className="text-[var(--bionic-text-secondary)] flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            {t('trips_history') || 'Historique'} ({completedTrips.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {completedTrips.length === 0 ? (
            <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
              <Target className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>{t('trips_no_completed') || 'Aucune sortie terminée'}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {completedTrips.slice(0, 10).map((trip) => (
                <TripCard key={trip.trip_id} trip={trip} t={t} />
              ))}
              {completedTrips.length > 10 && (
                <p className="text-center text-sm text-[var(--bionic-text-muted)]">
                  {t('trips_and_more') || 'Et'} {completedTrips.length - 10} {t('trips_other_trips') || 'autres sorties...'}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Start Trip Modal */}
      {selectedTrip && (
        <StartTripModal
          open={showStartModal}
          onClose={() => {
            setShowStartModal(false);
            setSelectedTrip(null);
          }}
          trip={selectedTrip}
          onTripStarted={onTripStarted}
        />
      )}
    </div>
  );
};

// Trip Card Component
const TripCard = ({ trip, t, onStartClick }) => {
  const statusConfig = STATUS_CONFIG[trip.status] || STATUS_CONFIG.planned;
  const StatusIcon = statusConfig.icon;
  const plannedDate = trip.planned_date ? new Date(trip.planned_date) : null;
  const SpeciesIcon = SPECIES_ICONS[trip.target_species] || Target;

  return (
    <div className="flex items-center gap-4 p-4 bg-[var(--bionic-bg-secondary)] rounded-lg hover:bg-[var(--bionic-bg-tertiary)] transition-colors">
      <div className="w-10 h-10 rounded-full bg-[var(--bionic-gold-muted)] flex items-center justify-center">
        <SpeciesIcon className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="text-[var(--bionic-text-primary)] font-medium truncate">{trip.title}</h4>
          <Badge className={`${statusConfig.color} text-xs`}>
            {t(`status_${trip.status}`) || statusConfig.label}
          </Badge>
        </div>
        <div className="flex items-center gap-4 text-sm text-[var(--bionic-text-secondary)]">
          {plannedDate && (
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {format(plannedDate, 'dd MMM yyyy', { locale: fr })}
            </span>
          )}
          {trip.duration_hours > 0 && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {trip.duration_hours}h
            </span>
          )}
          {trip.observations_count > 0 && (
            <span className="flex items-center gap-1">
              <Eye className="h-3 w-3" />
              {trip.observations_count} obs.
            </span>
          )}
          {trip.status === 'completed' && (
            trip.success ? (
              <span className="flex items-center gap-1 text-[var(--bionic-green-primary)]">
                <CheckCircle className="h-3 w-3" />
                {t('common_success') || 'Succès'}
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[var(--bionic-text-muted)]">
                <XCircle className="h-3 w-3" />
                {t('trips_no_success') || 'Sans succès'}
              </span>
            )
          )}
        </div>
      </div>

      {trip.status === 'planned' && onStartClick && (
        <Button
          size="sm"
          onClick={onStartClick}
          className="bg-[var(--bionic-green-primary)] hover:bg-[var(--bionic-green-light)]"
        >
          <Play className="h-4 w-4 mr-1" />
          {t('trips_start') || 'Démarrer'}
        </Button>
      )}
    </div>
  );
};

// Start Trip Modal
const StartTripModal = ({ open, onClose, trip, onTripStarted }) => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [weather, setWeather] = useState('cloudy');
  const [temperature, setTemperature] = useState('');

  const handleStart = async () => {
    setLoading(true);

    try {
      const result = await TripService.startTrip(trip.trip_id, {
        actual_weather: weather,
        temperature: temperature ? parseFloat(temperature) : null
      });

      if (result.success) {
        onTripStarted(result.trip);
        onClose();
      } else {
        toast.error(result.detail || t('common_error') || 'Erreur');
      }
    } catch (error) {
      toast.error(t('error_connection') || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] text-[var(--bionic-text-primary)] max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Play className="h-5 w-5 text-[var(--bionic-green-primary)]" />
            {t('trips_start_trip') || 'Démarrer la Sortie'}
          </DialogTitle>
          <DialogDescription className="text-[var(--bionic-text-secondary)]">
            {trip.title}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Weather */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-secondary)]">{t('weather_current_conditions') || 'Conditions météo actuelles'}</Label>
            <Select value={weather} onValueChange={setWeather}>
              <SelectTrigger className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                {WEATHER_OPTIONS.map((w) => {
                  const WeatherIcon = w.icon;
                  return (
                    <SelectItem key={w.value} value={w.value} className="text-[var(--bionic-text-primary)]">
                      <span className="flex items-center gap-2">
                        <WeatherIcon className="h-4 w-4" />
                        {t(`weather_${w.value}`) || w.label}
                      </span>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>

          {/* Temperature */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-secondary)]">{t('weather_temperature') || 'Température'} (°C)</Label>
            <div className="relative">
              <Thermometer className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--bionic-text-muted)]" />
              <Input
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)] pl-10"
                placeholder="Ex: 5"
              />
            </div>
          </div>

          {/* Info */}
          <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-[var(--bionic-gold-primary)] flex-shrink-0 mt-0.5" />
            <div className="text-sm text-[var(--bionic-text-secondary)]">
              <p>{t('trips_start_info') || 'Une fois démarrée, vous pourrez:'}:</p>
              <ul className="list-disc list-inside mt-1">
                <li>{t('trips_add_observations') || 'Ajouter des observations'}</li>
                <li>{t('trips_log_waypoints') || 'Logger vos visites de waypoints'}</li>
                <li>{t('trips_track_time') || 'Suivre le temps écoulé'}</li>
              </ul>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1 border-[var(--bionic-border-secondary)]"
              disabled={loading}
            >
              {t('common_cancel')}
            </Button>
            <Button
              onClick={handleStart}
              className="flex-1 bg-[var(--bionic-green-primary)] hover:bg-[var(--bionic-green-light)]"
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  {t('trips_lets_go') || "C'est parti!"}
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TripHistory;
