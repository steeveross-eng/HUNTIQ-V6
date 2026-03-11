/**
 * WaypointPanel - Waypoint list and management
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MapPin, Edit, Trash2, Navigation, Plus, Save, X, Package, Wheat, Droplet, Camera, Car, AlertTriangle, Crosshair } from 'lucide-react';
import { toast } from 'sonner';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

// Waypoint type configurations - BIONIC Design System Compliant
export const WAYPOINT_TYPES = {
  custom: { icon: MapPin, color: '#f5a623', name: 'Point personnalisé' },
  cache: { icon: Package, color: '#8B5CF6', name: 'Cache/Affût' },
  feeding: { icon: Wheat, color: '#22C55E', name: 'Zone alimentation' },
  water: { icon: Droplet, color: '#3B82F6', name: 'Point d\'eau' },
  crossing: { icon: Crosshair, color: '#EF4444', name: 'Traverse' },
  camera: { icon: Camera, color: '#EC4899', name: 'Caméra' },
  parking: { icon: Car, color: '#6B7280', name: 'Stationnement' },
  danger: { icon: AlertTriangle, color: '#F59E0B', name: 'Zone danger' }
};

const WaypointPanel = ({
  waypoints,
  onAddWaypoint,
  onEditWaypoint,
  onDeleteWaypoint,
  onNavigateToWaypoint,
  onExportGPX,
  pendingWaypoint,
  onConfirmWaypoint,
  onCancelWaypoint
}) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingWaypoint, setEditingWaypoint] = useState(null);
  const [waypointName, setWaypointName] = useState('');
  const [waypointType, setWaypointType] = useState('custom');
  const [waypointNotes, setWaypointNotes] = useState('');

  const handleSaveWaypoint = () => {
    if (!waypointName.trim()) {
      toast.error('Veuillez entrer un nom');
      return;
    }

    if (editingWaypoint) {
      onEditWaypoint({
        ...editingWaypoint,
        name: waypointName,
        type: waypointType,
        notes: waypointNotes
      });
      setEditingWaypoint(null);
    } else if (pendingWaypoint) {
      onConfirmWaypoint({
        ...pendingWaypoint,
        name: waypointName,
        type: waypointType,
        notes: waypointNotes
      });
    }

    setWaypointName('');
    setWaypointType('custom');
    setWaypointNotes('');
    setShowAddModal(false);
  };

  const openEditModal = (waypoint) => {
    setEditingWaypoint(waypoint);
    setWaypointName(waypoint.name);
    setWaypointType(waypoint.type || 'custom');
    setWaypointNotes(waypoint.notes || '');
    setShowAddModal(true);
  };

  // Auto-open modal when pending waypoint is set
  React.useEffect(() => {
    if (pendingWaypoint) {
      setShowAddModal(true);
    }
  }, [pendingWaypoint]);

  return (
    <>
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-sm flex items-center justify-between">
            <span className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-[#f5a623]" />
              Waypoints ({waypoints.length})
            </span>
            <div className="flex gap-1">
              <Button 
                size="icon" 
                variant="ghost" 
                className="h-6 w-6 text-gray-400 hover:text-white"
                onClick={onExportGPX}
                title="Exporter GPX"
                disabled={waypoints.length === 0}
              >
                <Navigation className="h-3 w-3" />
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 max-h-60 overflow-y-auto">
          {waypoints.length === 0 ? (
            <p className="text-gray-500 text-xs text-center py-4 flex items-center justify-center gap-1">
              <MapPin className="h-3 w-3" /> Cliquez sur la carte pour ajouter des waypoints
            </p>
          ) : (
            waypoints.map((waypoint, index) => {
              const typeConfig = WAYPOINT_TYPES[waypoint.type] || WAYPOINT_TYPES.custom;
              return (
                <div 
                  key={waypoint.id || index}
                  className="bg-background rounded-lg p-2 flex items-center justify-between group hover:bg-background/80"
                >
                  <div 
                    className="flex items-center gap-2 flex-1 cursor-pointer"
                    onClick={() => onNavigateToWaypoint(waypoint)}
                  >
                    <span 
                      className="flex items-center justify-center h-6 w-6 rounded"
                      style={{ backgroundColor: `${typeConfig.color}20` }}
                    >
                      <typeConfig.icon className="h-4 w-4" style={{ color: typeConfig.color }} />
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm truncate">{waypoint.name}</p>
                      <p className="text-gray-500 text-xs">
                        {waypoint.lat?.toFixed(5)}, {waypoint.lng?.toFixed(5)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 text-gray-400 hover:text-blue-400"
                      onClick={() => openEditModal(waypoint)}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 text-gray-400 hover:text-red-400"
                      onClick={() => onDeleteWaypoint(waypoint.id || index)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Waypoint Modal */}
      <Dialog open={showAddModal} onOpenChange={(open) => {
        if (!open) {
          setShowAddModal(false);
          setEditingWaypoint(null);
          if (pendingWaypoint) onCancelWaypoint();
        }
      }}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingWaypoint ? 'Modifier le waypoint' : 'Nouveau waypoint'}
            </DialogTitle>
            <DialogDescription>
              {pendingWaypoint && (
                <span className="text-[#f5a623] flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> {pendingWaypoint.lat?.toFixed(5)}, {pendingWaypoint.lng?.toFixed(5)}
                </span>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400">Nom du waypoint</label>
              <Input
                value={waypointName}
                onChange={(e) => setWaypointName(e.target.value)}
                placeholder="Ex: Affût chevreuil nord"
                className="bg-background"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400">Type</label>
              <Select value={waypointType} onValueChange={setWaypointType}>
                <SelectTrigger className="bg-background">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(WAYPOINT_TYPES).map(([key, config]) => {
                    const IconComponent = config.icon;
                    return (
                      <SelectItem key={key} value={key}>
                        <span className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4" style={{ color: config.color }} />
                          <span>{config.name}</span>
                        </span>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm text-gray-400">Notes (optionnel)</label>
              <Input
                value={waypointNotes}
                onChange={(e) => setWaypointNotes(e.target.value)}
                placeholder="Notes additionnelles..."
                className="bg-background"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowAddModal(false);
              setEditingWaypoint(null);
              if (pendingWaypoint) onCancelWaypoint();
            }}>
              <X className="h-4 w-4 mr-1" />
              Annuler
            </Button>
            <Button 
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
              onClick={handleSaveWaypoint}
            >
              <Save className="h-4 w-4 mr-1" />
              {editingWaypoint ? 'Modifier' : 'Ajouter'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default WaypointPanel;
