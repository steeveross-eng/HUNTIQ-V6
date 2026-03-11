/**
 * WaypointManager - Waypoint management component
 * Allows users to save and manage hunting waypoints
 * Version: 1.1.0 - BIONIC Design System Compliance
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Input } from '../../../components/ui/input';
import { toast } from 'sonner';
import { useLanguage } from '../../../contexts/LanguageContext';
import { 
  Target, Camera, Eye, ParkingCircle, MapPin, TreePine, 
  Loader2, Plus, Trash2, Edit, Save
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// BIONIC Design System - Lucide icons for waypoint types
const WAYPOINT_TYPES = [
  { id: 'hunting', label: 'Spot de chasse', icon: Target },
  { id: 'stand', label: 'Mirador/Affût', icon: TreePine },
  { id: 'camera', label: 'Caméra trail', icon: Camera },
  { id: 'feeder', label: 'Nourrisseur', icon: Target },
  { id: 'sighting', label: 'Observation', icon: Eye },
  { id: 'parking', label: 'Stationnement', icon: ParkingCircle },
  { id: 'custom', label: 'Autre', icon: MapPin }
];

export const WaypointManager = ({ coordinates = { lat: 46.8139, lng: -71.2080 } }) => {
  const { t } = useLanguage();
  const [waypoints, setWaypoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [newWaypoint, setNewWaypoint] = useState({
    name: '',
    type: 'hunting',
    notes: '',
    lat: coordinates.lat,
    lng: coordinates.lng
  });

  // Load waypoints
  const loadWaypoints = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/user/waypoints`);
      const data = await response.json();
      if (data.success && data.waypoints) {
        setWaypoints(data.waypoints);
      }
    } catch (error) {
      console.error('Error loading waypoints:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWaypoints();
  }, [loadWaypoints]);

  // Save waypoint
  const handleSaveWaypoint = async () => {
    if (!newWaypoint.name.trim()) {
      toast.error('Veuillez entrer un nom pour le waypoint');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/user/waypoints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newWaypoint,
          active: true
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Waypoint enregistré !');
        setWaypoints(prev => [data.waypoint, ...prev]);
        setNewWaypoint({
          name: '',
          type: 'hunting',
          notes: '',
          lat: coordinates.lat,
          lng: coordinates.lng
        });
        setShowForm(false);
      } else {
        toast.error(data.error || 'Erreur lors de l\'enregistrement');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
      console.error('Save waypoint error:', error);
    }
  };

  // Delete waypoint
  const handleDeleteWaypoint = async (waypointId) => {
    try {
      const response = await fetch(`${API_URL}/api/user/waypoints/${waypointId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Waypoint supprimé');
        setWaypoints(prev => prev.filter(w => w.id !== waypointId));
      } else {
        toast.error(data.error || 'Erreur lors de la suppression');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const getTypeInfo = (typeId) => {
    return WAYPOINT_TYPES.find(t => t.id === typeId) || WAYPOINT_TYPES[6];
  };

  return (
    <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center justify-between">
          <span className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
            {t('waypoints_my_waypoints') || 'Mes Waypoints'}
          </span>
          <div className="flex items-center gap-2">
            <Badge className="bg-[var(--bionic-bg-secondary)]">{waypoints.length}</Badge>
            <Button 
              size="sm"
              className="bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-light)] text-black"
              onClick={() => setShowForm(!showForm)}
              data-testid="add-waypoint-btn"
            >
              {showForm ? <><span className="mr-1">×</span> {t('common_cancel')}</> : <><Plus className="h-4 w-4 mr-1" /> {t('common_new')}</>}
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Add Form */}
        {showForm && (
          <div className="mb-4 p-4 bg-[var(--bionic-bg-secondary)] rounded-lg space-y-3" data-testid="waypoint-form">
            <Input
              placeholder={t('waypoint_name_placeholder') || 'Nom du waypoint'}
              value={newWaypoint.name}
              onChange={(e) => setNewWaypoint(prev => ({ ...prev, name: e.target.value }))}
              className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              data-testid="waypoint-name-input"
            />
            
            <div className="flex flex-wrap gap-2">
              {WAYPOINT_TYPES.map(type => {
                const TypeIcon = type.icon;
                return (
                <button
                  key={type.id}
                  onClick={() => setNewWaypoint(prev => ({ ...prev, type: type.id }))}
                  className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1 transition-all ${
                    newWaypoint.type === type.id 
                      ? 'bg-[var(--bionic-gold-primary)] text-black' 
                      : 'bg-[var(--bionic-bg-tertiary)] text-[var(--bionic-text-secondary)] hover:bg-[var(--bionic-bg-primary)]'
                  }`}
                >
                  <TypeIcon className="h-4 w-4" />
                  {type.label}
                </button>
              );
              })}
            </div>
            
            <Input
              placeholder={t('common_notes_optional') || 'Notes (optionnel)'}
              value={newWaypoint.notes}
              onChange={(e) => setNewWaypoint(prev => ({ ...prev, notes: e.target.value }))}
              className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
            />
            
            <div className="grid grid-cols-2 gap-2">
              <Input
                type="number"
                step="0.0001"
                placeholder={t('common_latitude') || 'Latitude'}
                value={newWaypoint.lat}
                onChange={(e) => setNewWaypoint(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
              <Input
                type="number"
                step="0.0001"
                placeholder={t('common_longitude') || 'Longitude'}
                value={newWaypoint.lng}
                onChange={(e) => setNewWaypoint(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            
            <Button 
              className="w-full bg-[var(--bionic-green-primary)] hover:bg-[var(--bionic-green-light)]"
              onClick={handleSaveWaypoint}
              data-testid="save-waypoint-btn"
            >
              <Save className="h-4 w-4 mr-2" /> {t('waypoint_save') || 'Enregistrer le waypoint'}
            </Button>
          </div>
        )}

        {/* Waypoints List */}
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse bg-[var(--bionic-bg-secondary)] rounded-lg h-16" />
            ))}
          </div>
        ) : waypoints.length > 0 ? (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {waypoints.map(waypoint => {
              const typeInfo = getTypeInfo(waypoint.type);
              const WaypointIcon = typeInfo.icon;
              return (
                <div 
                  key={waypoint.id}
                  className="flex items-center justify-between p-3 bg-[var(--bionic-bg-secondary)] rounded-lg hover:bg-[var(--bionic-bg-tertiary)] transition-colors"
                  data-testid={`waypoint-${waypoint.id}`}
                >
                  <div className="flex items-center gap-3">
                    <WaypointIcon className="h-6 w-6 text-[var(--bionic-gold-primary)]" />
                    <div>
                      <p className="text-[var(--bionic-text-primary)] font-medium">{waypoint.name}</p>
                      <p className="text-[var(--bionic-text-muted)] text-xs">
                        {waypoint.lat?.toFixed(4)}, {waypoint.lng?.toFixed(4)}
                        {waypoint.notes && ` • ${waypoint.notes}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-[var(--bionic-bg-tertiary)] text-[var(--bionic-text-secondary)] text-xs">
                      {typeInfo.label}
                    </Badge>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 text-[var(--bionic-red-primary)] hover:text-[var(--bionic-red-light)] hover:bg-[var(--bionic-red-muted)]"
                      onClick={() => handleDeleteWaypoint(waypoint.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <MapPin className="h-10 w-10 text-[var(--bionic-gray-500)] mx-auto mb-2" />
            <p className="text-[var(--bionic-text-secondary)] mt-2">{t('waypoints_none') || 'Aucun waypoint enregistré'}</p>
            <p className="text-[var(--bionic-text-muted)] text-sm">{t('waypoints_add_first') || 'Cliquez sur "+ Nouveau" pour ajouter votre premier spot'}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WaypointManager;
