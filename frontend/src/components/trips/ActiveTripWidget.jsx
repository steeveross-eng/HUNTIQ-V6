/**
 * ActiveTripWidget - Compact widget showing active hunting trip status
 * BIONIC Design System compliant - No emojis
 * Displays in Dashboard overview for quick access to trip logging
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { 
  Target, Clock, Eye, Play, ChevronRight, Plus, MapPin
} from 'lucide-react';
import TripService from '../../services/TripService';
import { SpeciesIcon } from '../bionic/SpeciesIcon';

const ActiveTripWidget = () => {
  const navigate = useNavigate();
  const [activeTrip, setActiveTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [elapsedTime, setElapsedTime] = useState('0:00');

  useEffect(() => {
    loadActiveTrip();
  }, []);

  // Calculate elapsed time for active trip
  useEffect(() => {
    if (!activeTrip?.start_time) return;

    const updateElapsed = () => {
      const start = new Date(activeTrip.start_time);
      const now = new Date();
      const diff = Math.floor((now - start) / 1000);
      const hours = Math.floor(diff / 3600);
      const minutes = Math.floor((diff % 3600) / 60);
      setElapsedTime(`${hours}:${minutes.toString().padStart(2, '0')}`);
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 60000);
    return () => clearInterval(interval);
  }, [activeTrip?.start_time]);

  const loadActiveTrip = async () => {
    try {
      const result = await TripService.getActiveTrip();
      if (result.active && result.trip) {
        setActiveTrip(result.trip);
      } else {
        setActiveTrip(null);
      }
    } catch (error) {
      console.error('Error loading active trip:', error);
      setActiveTrip(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 animate-pulse">
        <CardContent className="p-4">
          <div className="h-24 bg-slate-700/50 rounded" />
        </CardContent>
      </Card>
    );
  }

  // Active Trip State
  if (activeTrip) {
    return (
      <Card 
        className="bg-gradient-to-br from-emerald-900/40 to-slate-900 border-emerald-700/50 cursor-pointer hover:border-emerald-600/70 transition-all"
        onClick={() => navigate('/trips')}
        data-testid="active-trip-widget"
      >
        <CardContent className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-emerald-400 text-sm font-medium">Sortie en cours</span>
            </div>
            <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">
              <Clock className="h-3 w-3 mr-1" />
              {elapsedTime}
            </Badge>
          </div>

          {/* Trip Info */}
          <div className="flex items-center gap-3 mb-3">
            <SpeciesIcon species={activeTrip.target_species || 'other'} size="lg" rounded />
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{activeTrip.title}</p>
              <p className="text-xs text-slate-400 capitalize">{activeTrip.target_species}</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center justify-between bg-slate-800/50 rounded-lg p-2 mb-3">
            <div className="flex items-center gap-1.5">
              <Eye className="h-3.5 w-3.5 text-purple-400" />
              <span className="text-white text-sm font-medium">{activeTrip.observations_count || 0}</span>
              <span className="text-slate-400 text-xs">obs.</span>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 text-blue-400" />
              <span className="text-white text-sm font-medium">{activeTrip.visited_waypoints?.length || 0}</span>
              <span className="text-slate-400 text-xs">pts</span>
            </div>
          </div>

          {/* Action */}
          <Button 
            size="sm" 
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
            onClick={(e) => {
              e.stopPropagation();
              navigate('/trips');
            }}
          >
            <Plus className="h-4 w-4 mr-1" />
            Ajouter observation
            <ChevronRight className="h-4 w-4 ml-auto" />
          </Button>
        </CardContent>
      </Card>
    );
  }

  // No Active Trip State
  return (
    <Card 
      className="bg-slate-800/50 border-slate-700 hover:border-[#f5a623]/50 transition-all cursor-pointer"
      onClick={() => navigate('/trips')}
      data-testid="no-active-trip-widget"
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <Target className="h-5 w-5 text-[#f5a623]" />
          <span className="text-white font-medium">Sorties de chasse</span>
        </div>

        {/* Empty State */}
        <div className="text-center py-2 mb-3">
          <p className="text-slate-400 text-sm">Aucune sortie en cours</p>
        </div>

        {/* Action */}
        <Button 
          size="sm" 
          className="w-full bg-[#f5a623] hover:bg-[#d4890e] text-black"
          onClick={(e) => {
            e.stopPropagation();
            navigate('/trips');
          }}
        >
          <Play className="h-4 w-4 mr-1" />
          Démarrer une sortie
          <ChevronRight className="h-4 w-4 ml-auto" />
        </Button>
      </CardContent>
    </Card>
  );
};

export default ActiveTripWidget;
