/**
 * TerritoireDialogs.jsx — Dialogues (modales) pour Mon Territoire BIONIC
 * Extrait de MonTerritoireBionicPage.jsx (IM1 Refactorisation)
 * 
 * Inclut: Edit Place, Add Place, Add Waypoint, Share, Create Group, Group Dashboard
 */
import { MapPin, LocateFixed, Lightbulb, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ShareWaypointDialog, CreateGroupDialog } from '@/components/territoire/ShareComponents';
import { GroupDashboard } from '@/components/territoire/GroupDashboard';

// Dialog d'édition de lieu
export const EditPlaceDialog = ({ editingPlace, setEditingPlace, handleUpdatePlace, PLACE_TYPES }) => {
  if (!editingPlace) return null;
  return (
    <Dialog open={!!editingPlace} onOpenChange={() => setEditingPlace(null)}>
      <DialogContent className="bg-[#111118] border-[#1a1a2e]">
        <DialogHeader>
          <DialogTitle className="text-white">Modifier le lieu</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label className="text-gray-400">Nom du lieu</Label>
            <Input value={editingPlace.name} className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" onChange={(e) => setEditingPlace(p => ({ ...p, name: e.target.value }))} />
          </div>
          <div>
            <Label className="text-gray-400">Type</Label>
            <Select value={editingPlace.type} onValueChange={(v) => setEditingPlace(p => ({ ...p, type: v }))}>
              <SelectTrigger className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#111118] border-[#1a1a2e]">
                {PLACE_TYPES.map(type => (
                  <SelectItem key={type.id} value={type.id} className="text-white">
                    <span className="flex items-center gap-2">{type.Icon && <type.Icon className="h-4 w-4" style={{ color: type.color }} />} {type.name}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-gray-400">Notes</Label>
            <Input value={editingPlace.notes || ''} className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" onChange={(e) => setEditingPlace(p => ({ ...p, notes: e.target.value }))} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setEditingPlace(null)} className="border-[#1a1a2e]">Annuler</Button>
          <Button onClick={handleUpdatePlace} className="bg-blue-600 hover:bg-blue-700 text-white">Sauvegarder</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Dialog ajouter un lieu
export const AddPlaceDialog = ({ open, onOpenChange, newPlace, setNewPlace, handleAddPlace, useCurrentPositionForNewPlace, PLACE_TYPES }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="bg-[#111118] border-[#1a1a2e]">
      <DialogHeader>
        <DialogTitle className="text-white">Ajouter un lieu</DialogTitle>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div>
          <Label className="text-gray-400">Nom du lieu *</Label>
          <Input placeholder="Ex: ZEC Batiscan-Neilson" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newPlace.name} onChange={(e) => setNewPlace(p => ({ ...p, name: e.target.value }))} />
        </div>
        <div>
          <Label className="text-gray-400">Type de lieu</Label>
          <Select value={newPlace.type} onValueChange={(v) => setNewPlace(p => ({ ...p, type: v }))}>
            <SelectTrigger className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1"><SelectValue /></SelectTrigger>
            <SelectContent className="bg-[#111118] border-[#1a1a2e]">
              {PLACE_TYPES.map(type => (
                <SelectItem key={type.id} value={type.id} className="text-white">
                  <span className="flex items-center gap-2">{type.Icon && <type.Icon className="h-4 w-4" style={{ color: type.color }} />} {type.name}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label className="text-gray-400">Latitude</Label>
            <Input placeholder="46.8139" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newPlace.lat} onChange={(e) => setNewPlace(p => ({ ...p, lat: e.target.value }))} />
          </div>
          <div>
            <Label className="text-gray-400">Longitude</Label>
            <Input placeholder="-71.2080" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newPlace.lng} onChange={(e) => setNewPlace(p => ({ ...p, lng: e.target.value }))} />
          </div>
        </div>
        <button onClick={useCurrentPositionForNewPlace} className="w-full text-xs px-3 py-2 rounded-lg border border-[#1a1a2e] text-gray-400 hover:text-white hover:bg-[#1a1a2e] transition-colors flex items-center justify-center gap-2">
          <LocateFixed className="h-4 w-4" /> Utiliser ma position actuelle
        </button>
        <div>
          <Label className="text-gray-400">Notes (optionnel)</Label>
          <Input placeholder="Ex: Zone 15, secteur lac Blanc" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newPlace.notes} onChange={(e) => setNewPlace(p => ({ ...p, notes: e.target.value }))} />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={() => onOpenChange(false)} className="border-[#1a1a2e]">Annuler</Button>
        <Button onClick={handleAddPlace} className="bg-blue-600 hover:bg-blue-700 text-white">Enregistrer</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);

// Dialog ajouter un waypoint
export const AddWaypointDialog = ({ open, onOpenChange, newWaypoint, setNewWaypoint, handleAddWaypointFromDialog, useCurrentPositionForNewWaypoint, PLACE_TYPES }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="bg-[#111118] border-[#1a1a2e] !z-[99999]">
      <DialogHeader>
        <DialogTitle className="text-white flex items-center gap-2">
          <MapPin className="h-5 w-5 text-[#3CB371]" />
          Nouveau waypoint
        </DialogTitle>
        <DialogDescription className="text-gray-500">
          Créez un point d'intérêt pour générer automatiquement des zones d'analyse BIONIC™
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div>
          <Label className="text-gray-400">Nom du waypoint</Label>
          <Input placeholder="Ex: Affût secteur nord" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newWaypoint.name} onChange={(e) => setNewWaypoint(p => ({ ...p, name: e.target.value }))} />
        </div>
        <div>
          <Label className="text-gray-400">Type</Label>
          <Select value={newWaypoint.type} onValueChange={(v) => setNewWaypoint(p => ({ ...p, type: v }))}>
            <SelectTrigger className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1"><SelectValue placeholder="Sélectionner un type" /></SelectTrigger>
            <SelectContent className="bg-[#111118] border-[#1a1a2e]">
              {PLACE_TYPES.map(type => (
                <SelectItem key={type.id} value={type.id} className="text-white">
                  <span className="flex items-center gap-2">{type.Icon && <type.Icon className="h-4 w-4" style={{ color: type.color }} />} {type.name}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label className="text-gray-400">Latitude</Label>
            <Input placeholder="46.8139" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newWaypoint.lat} onChange={(e) => setNewWaypoint(p => ({ ...p, lat: e.target.value }))} />
          </div>
          <div>
            <Label className="text-gray-400">Longitude</Label>
            <Input placeholder="-71.2080" className="bg-[#0d0d14] border-[#1a1a2e] text-white mt-1" value={newWaypoint.lng} onChange={(e) => setNewWaypoint(p => ({ ...p, lng: e.target.value }))} />
          </div>
        </div>
        <button onClick={useCurrentPositionForNewWaypoint} className="w-full text-xs px-3 py-2 rounded-lg border border-[#1a1a2e] text-gray-400 hover:text-white hover:bg-[#1a1a2e] transition-colors flex items-center justify-center gap-2">
          <LocateFixed className="h-4 w-4" /> Utiliser ma position actuelle
        </button>
        <div className="bg-[#3CB371]/10 border border-[#3CB371]/20 rounded-lg p-3">
          <p className="text-xs text-[#3CB371] flex items-center gap-2">
            <Lightbulb className="h-4 w-4 flex-shrink-0" />
            Un waypoint actif génère automatiquement des zones d'analyse BIONIC™ autour de sa position.
          </p>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" className="border-[#1a1a2e]" onClick={() => onOpenChange(false)}>Annuler</Button>
        <Button onClick={handleAddWaypointFromDialog} className="bg-[#3CB371] hover:bg-[#3CB371]/90 text-black font-semibold" data-testid="confirm-add-waypoint-btn">
          <Plus className="h-4 w-4 mr-1" /> Ajouter le waypoint
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);

// Dialog de partage (wrapper)
export const ShareDialog = ({ open, onOpenChange, waypoint, userId, onShared }) => (
  <ShareWaypointDialog
    open={open}
    onOpenChange={onOpenChange}
    waypoint={waypoint}
    userId={userId}
    onShared={onShared}
  />
);

// Dialog de création de groupe (wrapper)
export { CreateGroupDialog };

// Dialog tableau de bord du groupe
export const GroupDashboardDialog = ({ open, onOpenChange, group, userId, onClose }) => {
  if (!open || !group) return null;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-gray-900 border-gray-700 max-w-4xl max-h-[90vh] p-0 overflow-hidden">
        <GroupDashboard
          group={group}
          userId={userId}
          onClose={onClose}
          initialTab="map"
        />
      </DialogContent>
    </Dialog>
  );
};


/**
 * TerritoireDialogs — Composant composite regroupant tous les dialogues
 * Extrait pour le refactoring STEEVE-MAX P0.
 */
import WaypointContextMenu from '@/components/territoire/WaypointContextMenu';
import CompareWidget from '@/components/territoire/CompareWidget';

export function TerritoireDialogs({
  editingPlace, setEditingPlace, handleUpdatePlace,
  showAddPlaceDialog, setShowAddPlaceDialog, newPlace, setNewPlace, handleAddPlace, useCurrentPositionForNewPlace,
  showAddWaypointDialog, setShowAddWaypointDialog, newWaypoint, setNewWaypoint, handleAddWaypointWithWind, useCurrentPositionForNewWaypoint,
  showShareDialog, setShowShareDialog, waypointToShare, setWaypointToShare, userId,
  showCreateGroupDialog, setShowCreateGroupDialog, refreshGroups,
  showGroupDashboard, setShowGroupDashboard, selectedGroup, setSelectedGroup,
  contextMenuMT, setContextMenuMT, handleDeleteWaypoint, selectWaypointAsTarget,
  showCompareWidget, compareSelection, handleCloseCompare,
  PLACE_TYPES,
}) {
  return (
    <>
      <EditPlaceDialog editingPlace={editingPlace} setEditingPlace={setEditingPlace} handleUpdatePlace={handleUpdatePlace} PLACE_TYPES={PLACE_TYPES} />
      <AddPlaceDialog open={showAddPlaceDialog} onOpenChange={setShowAddPlaceDialog} newPlace={newPlace} setNewPlace={setNewPlace} handleAddPlace={handleAddPlace} useCurrentPositionForNewPlace={useCurrentPositionForNewPlace} PLACE_TYPES={PLACE_TYPES} />
      <AddWaypointDialog open={showAddWaypointDialog} onOpenChange={setShowAddWaypointDialog} newWaypoint={newWaypoint} setNewWaypoint={setNewWaypoint} handleAddWaypointFromDialog={handleAddWaypointWithWind} useCurrentPositionForNewWaypoint={useCurrentPositionForNewWaypoint} PLACE_TYPES={PLACE_TYPES} />
      <ShareDialog open={showShareDialog} onOpenChange={setShowShareDialog} waypoint={waypointToShare} userId={userId} onShared={() => { setShowShareDialog(false); setWaypointToShare(null); }} />
      <CreateGroupDialog open={showCreateGroupDialog} onOpenChange={setShowCreateGroupDialog} userId={userId} onCreated={() => refreshGroups()} />
      <GroupDashboardDialog open={showGroupDashboard} onOpenChange={setShowGroupDashboard} group={selectedGroup} userId={userId} onClose={() => { setShowGroupDashboard(false); setSelectedGroup(null); }} />
      {contextMenuMT && (
        <WaypointContextMenu
          position={contextMenuMT.position}
          waypoint={contextMenuMT.waypoint}
          onClose={() => setContextMenuMT(null)}
          onDelete={(id) => handleDeleteWaypoint(id)}
          onAnalyze={(wp) => selectWaypointAsTarget(wp)}
          onEdit={(wp) => selectWaypointAsTarget(wp)}
        />
      )}
      {showCompareWidget && compareSelection.length >= 2 && (
        <CompareWidget waypoints={compareSelection} onClose={handleCloseCompare} />
      )}
    </>
  );
}
