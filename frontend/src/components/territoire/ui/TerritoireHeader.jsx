/**
 * TerritoireHeader.jsx — Header BIONIC epure
 * =============================================
 * Section 4: Aucun score meteo ou opportunite dans le header.
 * Section 5: Temperature officielle du cockpit INTELLIGENCE uniquement.
 * Seul score global autorise: Score Consolide INTELLIGENCE (dans le cockpit).
 */
import React from 'react';
import { ArrowLeft, Thermometer, Wind, Zap, Plus, Edit2, Crosshair, X, LocateFixed, Trash2, ToggleLeft } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import useBionicStore from '@/stores/useBionicStore';

export const TerritoireHeader = React.memo(({
  navigate,
  liveMode,
  setLiveMode,
  selectedWaypointForZones,
  mapClickMode,
  setMapClickMode,
  setShowAddWaypointDialog,
  onClearWaypoint,
  onDeleteWaypoint,
  onCenterWaypoint,
}) => {
  const intelligenceWeather = useBionicStore(s => s.intelligenceWeather);
  const temp = intelligenceWeather?.temperature;
  const windDir = intelligenceWeather?.wind_direction_deg;
  const windSpeed = intelligenceWeather?.wind_speed_kmh;

  return (
    <header className="flex-shrink-0 min-h-[60px] bg-[#0d0d14] border-b border-[#1a1a2e] px-4 pl-24 flex items-center justify-between relative z-50" data-testid="bionic-header">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/')} className="text-gray-500 hover:text-white transition-colors" data-testid="header-back-btn">
          <ArrowLeft className="h-[22px] w-[22px]" />
        </button>
        <div className="h-6 w-px bg-[#1a1a2e]" />
        <h1 className="text-base font-semibold text-white tracking-tight">Mon Territoire BIONIC</h1>
      </div>
      <div className="flex items-center gap-3">
        {/* + WAYPOINT — bouton principal */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className={`h-9 px-6 flex items-center gap-2 rounded-lg font-bold text-sm uppercase tracking-wider transition-all duration-150 ${
                mapClickMode
                  ? 'bg-green-500/20 border-2 border-green-500/60 text-green-400'
                  : 'bg-[#FF9800]/15 border-2 border-[#FF9800]/50 hover:bg-[#FF9800]/25 text-[#FF9800]'
              }`}
              data-testid="add-waypoint-main-btn"
            >
              <Plus className="h-5 w-5" />
              <span className="text-sm">{mapClickMode ? 'Cliquez...' : 'Waypoint'}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl min-w-[220px]" side="bottom" align="center">
            <DropdownMenuItem onClick={() => setShowAddWaypointDialog(true)} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-coords">
              <Edit2 className="h-4 w-4 mr-2 text-[#FF9800]" /> Saisir les coordonnees
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setMapClickMode(true)} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-click">
              <Crosshair className="h-4 w-4 mr-2 text-green-500" /> Cliquer sur la carte
            </DropdownMenuItem>
            {selectedWaypointForZones && (
              <>
                <DropdownMenuSeparator className="bg-gray-700/50" />
                <DropdownMenuItem onClick={onCenterWaypoint} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-center">
                  <LocateFixed className="h-4 w-4 mr-2 text-blue-400" /> Centrer sur ce waypoint
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onClearWaypoint} className="text-amber-400 hover:bg-white/10 cursor-pointer" data-testid="wp-action-deselect">
                  <ToggleLeft className="h-4 w-4 mr-2" /> Deselectionner
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    if (window.confirm(`Supprimer le waypoint "${selectedWaypointForZones.name}" ?`)) {
                      onDeleteWaypoint(selectedWaypointForZones.id);
                    }
                  }}
                  className="text-red-400 hover:bg-white/10 cursor-pointer"
                  data-testid="wp-action-delete"
                >
                  <Trash2 className="h-4 w-4 mr-2" /> Supprimer waypoint
                </DropdownMenuItem>
              </>
            )}
            {mapClickMode && (
              <>
                <DropdownMenuSeparator className="bg-gray-700/50" />
                <DropdownMenuItem onClick={() => setMapClickMode(false)} className="text-red-400 hover:bg-white/10 cursor-pointer" data-testid="wp-action-cancel">
                  <X className="h-4 w-4 mr-2" /> Annuler
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
        {/* Section 5: Temperature officielle INTELLIGENCE */}
        {temp != null && (
          <div className="flex items-center gap-3 bg-[#111118] rounded-lg px-3 py-1.5 border border-[#1a1a2e]" data-testid="header-weather-official">
            <div className="flex items-center gap-1">
              <Thermometer className="h-4 w-4" style={{ color: '#4A7A2E' }} />
              <span className="text-xs text-white font-mono">{temp}°C</span>
            </div>
            {windSpeed != null && (
              <div className="flex items-center gap-1">
                <Wind className="h-4 w-4" style={{ color: '#8B6F47' }} />
                <span className="text-xs text-white font-mono">{windDir}° {windSpeed} km/h</span>
              </div>
            )}
          </div>
        )}
        {/* LIVE */}
        <div className="flex items-center gap-1.5 bg-[#111118] rounded-lg px-2.5 py-1.5 border border-[#1a1a2e]" data-testid="header-live">
          <Zap className={`h-4 w-4 ${liveMode ? 'text-green-400' : 'text-gray-600'}`} />
          <span className="text-[10px] text-gray-500 uppercase">LIVE</span>
          <Switch checked={liveMode} onCheckedChange={setLiveMode} className="data-[state=checked]:bg-green-500 scale-75" />
        </div>
      </div>
    </header>
  );
});
