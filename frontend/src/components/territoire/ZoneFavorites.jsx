/**
 * ZoneFavorites.jsx
 * 
 * Composant pour gérer les zones favorites et afficher les alertes de conditions optimales
 * - Ajout/suppression de zones favorites
 * - Affichage des prévisions de conditions optimales
 * - Alertes 3 jours à l'avance
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Star, StarOff, Bell, BellRing, Calendar, Clock, Wind, 
  Thermometer, Moon, Target, ChevronRight, X, RefreshCw,
  AlertTriangle, CheckCircle2, Info, Trash2, Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { BIONIC_MODULES } from './BionicMicroZones';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Hook pour gérer les zones favorites
export const useZoneFavorites = (userId = 'anonymous') => {
  const [favorites, setFavorites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [unreadAlertCount, setUnreadAlertCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchFavorites = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/zones/favorites?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setFavorites(data.favorites || []);
      }
    } catch (error) {
      console.error('Erreur chargement favoris:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const fetchAlerts = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/zones/alerts?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
        setUnreadAlertCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
    }
  }, [userId]);

  const addFavorite = useCallback(async (zone) => {
    try {
      const response = await fetch(`${API_URL}/api/zones/favorites?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(zone)
      });
      
      if (response.ok) {
        const newFavorite = await response.json();
        setFavorites(prev => [...prev, newFavorite]);
        toast.success('Zone ajoutée aux favoris!', {
          description: `${zone.name} - Alertes activées ${zone.alert_days_before} jours avant`
        });
        fetchAlerts(); // Rafraîchir les alertes
        return newFavorite;
      } else {
        const error = await response.json();
        toast.error('Erreur', { description: error.detail });
      }
    } catch (error) {
      console.error('Erreur ajout favori:', error);
      toast.error('Erreur lors de l\'ajout aux favoris');
    }
    return null;
  }, [userId, fetchAlerts]);

  const removeFavorite = useCallback(async (zoneId) => {
    try {
      const response = await fetch(`${API_URL}/api/zones/favorites/${zoneId}?user_id=${userId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setFavorites(prev => prev.filter(f => f.id !== zoneId));
        toast.success('Zone retirée des favoris');
        return true;
      }
    } catch (error) {
      console.error('Erreur suppression favori:', error);
      toast.error('Erreur lors de la suppression');
    }
    return false;
  }, [userId]);

  const updateAlertSettings = useCallback(async (zoneId, alertEnabled, alertDaysBefore) => {
    try {
      const response = await fetch(
        `${API_URL}/api/zones/favorites/${zoneId}/alerts?user_id=${userId}&alert_enabled=${alertEnabled}&alert_days_before=${alertDaysBefore}`,
        { method: 'PUT' }
      );
      
      if (response.ok) {
        setFavorites(prev => prev.map(f => 
          f.id === zoneId ? { ...f, alert_enabled: alertEnabled, alert_days_before: alertDaysBefore } : f
        ));
        toast.success('Paramètres d\'alerte mis à jour');
        return true;
      }
    } catch (error) {
      console.error('Erreur mise à jour alertes:', error);
    }
    return false;
  }, [userId]);

  const markAlertRead = useCallback(async (alertId) => {
    try {
      await fetch(`${API_URL}/api/zones/alerts/${alertId}/read?user_id=${userId}`, {
        method: 'PUT'
      });
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, read: true } : a));
      setUnreadAlertCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Erreur marquage alerte:', error);
    }
  }, [userId]);

  const markAllAlertsRead = useCallback(async () => {
    try {
      await fetch(`${API_URL}/api/zones/alerts/read-all?user_id=${userId}`, {
        method: 'PUT'
      });
      setAlerts(prev => prev.map(a => ({ ...a, read: true })));
      setUnreadAlertCount(0);
    } catch (error) {
      console.error('Erreur marquage alertes:', error);
    }
  }, [userId]);

  const checkOptimalConditions = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/zones/check-optimal-conditions?user_id=${userId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.new_alerts > 0) {
          toast.success(`${data.new_alerts} nouvelle(s) alerte(s)!`, {
            description: 'Conditions optimales détectées'
          });
        }
        fetchAlerts();
        fetchFavorites();
      }
    } catch (error) {
      console.error('Erreur vérification conditions:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, fetchAlerts, fetchFavorites]);

  const getZoneConditions = useCallback(async (zoneId) => {
    try {
      const response = await fetch(`${API_URL}/api/zones/favorites/${zoneId}/conditions?user_id=${userId}&days=7`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Erreur récupération conditions:', error);
    }
    return null;
  }, [userId]);

  useEffect(() => {
    fetchFavorites();
    fetchAlerts();
  }, [fetchFavorites, fetchAlerts]);

  // Vérifier les conditions optimales périodiquement (toutes les 6 heures)
  useEffect(() => {
    const interval = setInterval(checkOptimalConditions, 6 * 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, [checkOptimalConditions]);

  return {
    favorites,
    alerts,
    unreadAlertCount,
    loading,
    addFavorite,
    removeFavorite,
    updateAlertSettings,
    markAlertRead,
    markAllAlertsRead,
    checkOptimalConditions,
    getZoneConditions,
    refresh: () => { fetchFavorites(); fetchAlerts(); }
  };
};

// Composant bouton pour ajouter aux favoris (à utiliser dans les zones)
export const AddToFavoritesButton = ({ 
  zone, 
  onAdd, 
  isFavorite = false, 
  onRemove,
  size = 'sm'
}) => {
  const [showDialog, setShowDialog] = useState(false);
  const [name, setName] = useState('');
  const [alertDays, setAlertDays] = useState(3);
  const [notes, setNotes] = useState('');

  const handleAdd = async () => {
    if (!name.trim()) {
      toast.error('Veuillez donner un nom à cette zone');
      return;
    }

    const favoriteZone = {
      name: name.trim(),
      module_id: zone.moduleId,
      location: {
        lat: zone.center[0],
        lng: zone.center[1],
        radius_meters: zone.radiusMeters
      },
      notes: notes.trim() || null,
      alert_enabled: true,
      alert_days_before: alertDays
    };

    const result = await onAdd(favoriteZone);
    if (result) {
      setShowDialog(false);
      setName('');
      setNotes('');
    }
  };

  if (isFavorite) {
    return (
      <Button
        size={size}
        variant="ghost"
        onClick={onRemove}
        className="text-yellow-400 hover:text-yellow-300 hover:bg-yellow-400/10"
      >
        <Star className="h-4 w-4 fill-yellow-400" />
      </Button>
    );
  }

  return (
    <>
      <Button
        size={size}
        variant="ghost"
        onClick={() => setShowDialog(true)}
        className="text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/10"
        title="Ajouter aux favoris"
      >
        <StarOff className="h-4 w-4" />
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="bg-gray-900 border-gray-700 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-400" />
              Ajouter aux favoris
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: BIONIC_MODULES[zone.moduleId]?.color }}
                />
                <span className="text-sm text-gray-300">
                  {BIONIC_MODULES[zone.moduleId]?.label || zone.moduleId}
                </span>
                <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623]">
                  {zone.percentage}%
                </Badge>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Nom de la zone *</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex: Mon affût principal"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Alerte avant conditions optimales</Label>
              <Select value={String(alertDays)} onValueChange={(v) => setAlertDays(parseInt(v))}>
                <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  <SelectItem value="1">1 jour avant</SelectItem>
                  <SelectItem value="2">2 jours avant</SelectItem>
                  <SelectItem value="3">3 jours avant</SelectItem>
                  <SelectItem value="5">5 jours avant</SelectItem>
                  <SelectItem value="7">7 jours avant</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Notes (optionnel)</Label>
              <Input
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Ex: Meilleur au lever du soleil"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>
          </div>

          <DialogFooter className="gap-2">
            <DialogClose asChild>
              <Button variant="outline" className="border-gray-700">
                Annuler
              </Button>
            </DialogClose>
            <Button onClick={handleAdd} className="bg-[#f5a623] text-black hover:bg-[#f5a623]/90">
              <Star className="h-4 w-4 mr-2" />
              Ajouter aux favoris
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

// Composant panneau des alertes
export const AlertsPanel = ({ 
  alerts, 
  unreadCount, 
  onMarkRead, 
  onMarkAllRead,
  onRefresh,
  loading
}) => {
  const [showAll, setShowAll] = useState(false);

  const displayedAlerts = showAll ? alerts : alerts.slice(0, 5);

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-400 bg-green-400/20';
    if (score >= 75) return 'text-lime-400 bg-lime-400/20';
    if (score >= 65) return 'text-yellow-400 bg-yellow-400/20';
    return 'text-orange-400 bg-orange-400/20';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short' 
    });
  };

  const getDaysUntil = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const diff = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
    if (diff === 0) return "Aujourd'hui";
    if (diff === 1) return "Demain";
    return `Dans ${diff} jours`;
  };

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {unreadCount > 0 ? (
            <BellRing className="h-4 w-4 text-[#f5a623] animate-pulse" />
          ) : (
            <Bell className="h-4 w-4 text-gray-400" />
          )}
          <span className="text-sm font-medium text-white">Alertes conditions</span>
          {unreadCount > 0 && (
            <Badge className="bg-red-500 text-white text-[10px]">{unreadCount}</Badge>
          )}
        </div>
        <div className="flex gap-1">
          <Button size="sm" variant="ghost" onClick={onRefresh} disabled={loading} className="h-7 w-7 p-0">
            <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          {unreadCount > 0 && (
            <Button size="sm" variant="ghost" onClick={onMarkAllRead} className="h-7 text-[10px] px-2">
              Tout lire
            </Button>
          )}
        </div>
      </div>

      {/* Liste des alertes */}
      {displayedAlerts.length === 0 ? (
        <div className="text-center py-4 text-gray-500 text-sm">
          Aucune alerte pour le moment
        </div>
      ) : (
        <div className="space-y-2">
          {displayedAlerts.map(alert => (
            <div 
              key={alert.id}
              onClick={() => !alert.read && onMarkRead(alert.id)}
              className={`p-2 rounded-lg border cursor-pointer transition-all ${
                alert.read 
                  ? 'bg-gray-800/50 border-gray-700/50' 
                  : 'bg-[#f5a623]/10 border-[#f5a623]/30 hover:bg-[#f5a623]/15'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white truncate">
                      {alert.zone_name}
                    </span>
                    {!alert.read && (
                      <div className="w-2 h-2 rounded-full bg-[#f5a623]" />
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(alert.optimal_date)}</span>
                    <span className="text-[#f5a623]">({getDaysUntil(alert.optimal_date)})</span>
                  </div>
                </div>
                <Badge className={`${getScoreColor(alert.score)} text-xs`}>
                  {alert.score}%
                </Badge>
              </div>
              
              {alert.conditions && (
                <div className="mt-2 text-xs text-gray-300 bg-gray-800/50 rounded p-1.5">
                  {alert.conditions.interpretation}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Voir plus */}
      {alerts.length > 5 && (
        <Button 
          size="sm" 
          variant="ghost" 
          onClick={() => setShowAll(!showAll)}
          className="w-full text-xs text-gray-400"
        >
          {showAll ? 'Voir moins' : `Voir toutes (${alerts.length})`}
        </Button>
      )}
    </div>
  );
};

// Composant liste des favoris
export const FavoritesList = ({ 
  favorites, 
  onRemove, 
  onUpdateAlerts,
  onViewConditions
}) => {
  const [selectedZone, setSelectedZone] = useState(null);
  const [conditions, setConditions] = useState(null);
  const [loadingConditions, setLoadingConditions] = useState(false);

  const handleViewConditions = async (zone) => {
    setSelectedZone(zone);
    setLoadingConditions(true);
    const data = await onViewConditions(zone.id);
    setConditions(data);
    setLoadingConditions(false);
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-400';
    if (score >= 75) return 'text-lime-400';
    if (score >= 65) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="space-y-2">
      <div className="text-[10px] text-[#f5a623] uppercase flex items-center gap-1">
        <Star className="h-3 w-3" />
        Zones favorites ({favorites.length})
      </div>

      {favorites.length === 0 ? (
        <div className="text-center py-4 text-gray-500 text-xs">
          Aucune zone favorite
          <div className="text-[10px] mt-1 flex items-center justify-center gap-1">
            Cliquez sur <Star className="h-3 w-3 text-yellow-400" /> pour ajouter une zone
          </div>
        </div>
      ) : (
        <div className="space-y-1">
          {favorites.map(zone => (
            <div 
              key={zone.id}
              className="p-2 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-gray-600"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div 
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: BIONIC_MODULES[zone.module_id]?.color }}
                  />
                  <span className="text-xs text-white truncate">{zone.name}</span>
                </div>
                <div className="flex items-center gap-1">
                  {zone.alert_enabled && (
                    <Bell className="h-3 w-3 text-[#f5a623]" />
                  )}
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => handleViewConditions(zone)}
                    className="h-6 w-6 p-0 text-gray-400 hover:text-white"
                  >
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              </div>

              {zone.next_optimal_window && (
                <div className="mt-1.5 flex items-center gap-2">
                  <Badge className={`${getScoreColor(zone.next_optimal_window.score)} bg-opacity-20 text-[10px]`}>
                    Prochain: {zone.next_optimal_window.score}%
                  </Badge>
                  <span className="text-[10px] text-gray-500">
                    {new Date(zone.next_optimal_window.date).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' })}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Dialog détails conditions */}
      <Dialog open={!!selectedZone} onOpenChange={() => setSelectedZone(null)}>
        <DialogContent className="bg-gray-900 border-gray-700 max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Target className="h-5 w-5 text-[#f5a623]" />
              {selectedZone?.name}
            </DialogTitle>
          </DialogHeader>

          {loadingConditions ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-[#f5a623]" />
            </div>
          ) : conditions ? (
            <div className="space-y-4">
              {/* Meilleur jour */}
              {conditions.best_day && (
                <div className="bg-green-900/30 rounded-lg p-3 border border-green-500/30">
                  <div className="text-xs text-green-400 uppercase mb-1">Meilleur jour</div>
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">
                      {new Date(conditions.best_day.date).toLocaleDateString('fr-FR', { 
                        weekday: 'long', day: 'numeric', month: 'long' 
                      })}
                    </span>
                    <Badge className="bg-green-500 text-white">{conditions.best_day.score}%</Badge>
                  </div>
                  <div className="text-sm text-green-300 mt-1">
                    {conditions.best_day.interpretation}
                  </div>
                </div>
              )}

              {/* Prévisions 7 jours */}
              <div>
                <div className="text-xs text-gray-400 uppercase mb-2">Prévisions 7 jours</div>
                <div className="space-y-2">
                  {conditions.conditions?.map((day, idx) => (
                    <div 
                      key={idx}
                      className="flex items-center gap-3 p-2 rounded bg-gray-800/50"
                    >
                      <div className="text-xs text-gray-400 w-16">
                        {new Date(day.date).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' })}
                      </div>
                      <div className="flex-1 flex items-center gap-2">
                        <div className="h-2 flex-1 bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${
                              day.score >= 75 ? 'bg-green-500' : 
                              day.score >= 60 ? 'bg-yellow-500' : 'bg-orange-500'
                            }`}
                            style={{ width: `${day.score}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium w-10 text-right ${getScoreColor(day.score)}`}>
                          {day.score}%
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-[10px] text-gray-500">
                        <Thermometer className="h-3 w-3" />
                        {Math.round(day.weather.temp_max)}°
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2 border-t border-gray-700">
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => onRemove(selectedZone.id)}
                  className="flex-1 border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Retirer
                </Button>
                <Button 
                  size="sm"
                  className="flex-1 bg-[#f5a623] text-black hover:bg-[#f5a623]/90"
                  onClick={() => {
                    onUpdateAlerts(selectedZone.id, !selectedZone.alert_enabled, selectedZone.alert_days_before);
                    setSelectedZone(prev => ({ ...prev, alert_enabled: !prev.alert_enabled }));
                  }}
                >
                  {selectedZone?.alert_enabled ? (
                    <>
                      <BellRing className="h-4 w-4 mr-2" />
                      Alertes ON
                    </>
                  ) : (
                    <>
                      <Bell className="h-4 w-4 mr-2" />
                      Alertes OFF
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Impossible de charger les conditions
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default { useZoneFavorites, AddToFavoritesButton, AlertsPanel, FavoritesList };
