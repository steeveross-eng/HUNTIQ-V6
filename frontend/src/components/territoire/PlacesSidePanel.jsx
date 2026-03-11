/**
 * PlacesSidePanel — Panneau latéral des lieux enregistrés
 * Extrait de MonTerritoireBionicPage.jsx (Phase 3 refactoring)
 */

import React from 'react';
import { BookMarked, Plus, Pin, Navigation2, Edit2, Trash2 } from 'lucide-react';

const PlacesSidePanel = ({
  savedPlaces,
  PLACE_TYPES,
  onAddPlace,
  onAddPlaceWithType,
  onCenterOnPlace,
  onEditPlace,
  onDeletePlace,
}) => (
  <div className="p-4 space-y-3" data-testid="panel-lieux">
    <div className="flex items-center justify-between">
      <h2 className="text-sm font-semibold text-white flex items-center gap-2">
        <BookMarked className="h-4 w-4 text-blue-400" /> Lieux enregistres
      </h2>
      <button onClick={onAddPlace} className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors" data-testid="add-place-btn">
        <Plus className="h-3 w-3" /> Ajouter
      </button>
    </div>
    <div className="flex flex-wrap gap-1">
      {PLACE_TYPES.slice(0, 5).map(type => (
        <button key={type.id} onClick={() => onAddPlaceWithType(type.id)} className="px-2 py-1 rounded-lg text-[10px] bg-[#111118] text-gray-400 hover:text-white hover:bg-[#1a1a2e] transition-colors flex items-center gap-1 border border-[#1a1a2e]">
          {type.Icon && <type.Icon className="h-3 w-3" style={{ color: type.color }} />} {type.name}
        </button>
      ))}
    </div>
    <div className="space-y-2">
      {savedPlaces.length === 0 ? (
        <div className="text-center text-gray-600 py-8">
          <BookMarked className="h-10 w-10 mx-auto mb-2 opacity-20" />
          <p className="text-sm">Aucun lieu enregistre</p>
          <p className="text-xs mt-1">Ajoutez vos ZEC, pourvoiries et territoires</p>
        </div>
      ) : (
        savedPlaces.map(place => {
          const typeInfo = PLACE_TYPES.find(t => t.id === place.type);
          return (
            <div key={place.id} className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e] hover:border-gray-700 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-2.5 flex-1 min-w-0">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${typeInfo?.color}15` }}>
                    {typeInfo?.Icon ? <typeInfo.Icon className="h-4 w-4" style={{ color: typeInfo?.color }} /> : <Pin className="h-4 w-4 text-gray-500" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white font-medium truncate">{place.name}</div>
                    <div className="text-[10px] text-gray-500">{typeInfo?.name} — {place.lat.toFixed(4)}, {place.lng.toFixed(4)}</div>
                    {place.notes && <div className="text-[10px] text-gray-600 mt-0.5 italic truncate">"{place.notes}"</div>}
                  </div>
                </div>
                <div className="flex items-center gap-0.5 flex-shrink-0">
                  <button onClick={() => onCenterOnPlace(place)} className="text-gray-500 hover:text-white h-7 w-7 flex items-center justify-center rounded transition-colors" data-testid={`place-center-${place.id}`}><Navigation2 className="h-3.5 w-3.5" /></button>
                  <button onClick={() => onEditPlace(place)} className="text-gray-500 hover:text-blue-400 h-7 w-7 flex items-center justify-center rounded transition-colors" data-testid={`place-edit-${place.id}`}><Edit2 className="h-3.5 w-3.5" /></button>
                  <button onClick={() => onDeletePlace(place.id)} className="text-gray-500 hover:text-red-400 h-7 w-7 flex items-center justify-center rounded transition-colors" data-testid={`place-delete-${place.id}`}><Trash2 className="h-3.5 w-3.5" /></button>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  </div>
);

export default PlacesSidePanel;
