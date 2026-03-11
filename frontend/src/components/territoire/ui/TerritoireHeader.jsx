/**
 * TerritoireHeader.jsx — Header BIONIC avec score géant, météo, LIVE
 * P0 UX: Score ×3, Waypoint sous le score, fallback "Calcul en cours..."
 */
import React from 'react';
import { ArrowLeft, Thermometer, Wind, Target, Zap, Plus, Edit2, Crosshair, X, LocateFixed, Trash2, ToggleLeft } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';

export const TerritoireHeader = React.memo(({
  navigate,
  displayScore,
  rating,
  weather,
  temperature,
  windInfo,
  huntingScore,
  liveMode,
  setLiveMode,
  isLoadingZones,
  selectedWaypointForZones,
  mapClickMode,
  setMapClickMode,
  setShowAddWaypointDialog,
  onClearWaypoint,
  onDeleteWaypoint,
  onCenterWaypoint,
}) => (
  <header className="flex-shrink-0 min-h-[60px] bg-[#0d0d14] border-b border-[#1a1a2e] px-4 pl-24 flex items-center justify-between relative z-50" data-testid="bionic-header">
    <div className="flex items-center gap-3">
      <button onClick={() => navigate('/')} className="text-gray-500 hover:text-white transition-colors" data-testid="header-back-btn">
        <ArrowLeft className="h-[22px] w-[22px]" />
      </button>
      <div className="h-6 w-px bg-[#1a1a2e]" />
      <h1 className="text-base font-semibold text-white tracking-tight">Mon Territoire BIONIC</h1>
    </div>
    <div className="flex items-center gap-3">
      {/* SCORE ×3 + WAYPOINT sous le score */}
      <div className="flex flex-col items-center gap-1">
        <div className="flex items-center gap-2 bg-[#111118] rounded-lg px-5 py-2 border border-[#1a1a2e]" data-testid="header-score">
          <span className="text-5xl font-black text-white leading-none tracking-tight" data-testid="score-value">{displayScore ?? '—'}</span>
          <span className="text-gray-500 text-2xl font-semibold">/100</span>
          {displayScore ? (
            <Badge className={`${rating.color} text-white text-xs px-2.5 py-1 ml-1`} data-testid="score-badge">{rating.label}</Badge>
          ) : isLoadingZones ? (
            <span className="text-sm text-amber-400 ml-1 animate-pulse" data-testid="score-loading">Calcul...</span>
          ) : (
            <span className="text-sm text-gray-500 ml-1" data-testid="score-waiting">En attente</span>
          )}
        </div>
        {/* + WAYPOINT — directement sous le score */}
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
              <Edit2 className="h-4 w-4 mr-2 text-[#FF9800]" /> Saisir les coordonnées
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
                  <ToggleLeft className="h-4 w-4 mr-2" /> Désélectionner
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
      </div>
      {/* Weather */}
      {weather && (
        <div className="flex items-center gap-3 bg-[#111118] rounded-lg px-3 py-1.5 border border-[#1a1a2e]" data-testid="header-weather">
          <div className="flex items-center gap-1"><Thermometer className="h-4 w-4 text-blue-400" /><span className="text-xs text-white">{Math.round(temperature)}°C</span></div>
          <div className="flex items-center gap-1"><Wind className="h-4 w-4 text-gray-400" /><span className="text-xs text-white">{windInfo?.direction} {Math.round(windInfo?.speed)} km/h</span></div>
          <div className="flex items-center gap-1"><Target className="h-4 w-4 text-[#3CB371]" /><span className="text-xs text-white">Chasse: {huntingScore}/100</span></div>
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
));
