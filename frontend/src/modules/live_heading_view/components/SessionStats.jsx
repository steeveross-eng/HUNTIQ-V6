/**
 * SessionStats - Top stats bar showing session metrics
 */
import React from 'react';
import { Target } from 'lucide-react';

export const SessionStats = ({ 
  distance = 0, 
  duration = 0, 
  poisCount = 0, 
  sessionState = 'active'
}) => {
  // Format duration
  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Format distance
  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
  };
  
  return (
    <div className="bg-slate-800/95 rounded-2xl px-4 py-3 border border-slate-700 shadow-xl">
      <div className="flex items-center justify-between">
        {/* Logo/Title */}
        <div className="flex items-center gap-2">
          <Target className="h-6 w-6 text-[#f5a623]" />
          <div>
            <div className="text-white font-bold text-sm">Live Heading</div>
            <div className="text-emerald-400 text-xs">BIONIC HUNT/Chasse V3</div>
          </div>
        </div>
        
        {/* Stats */}
        <div className="flex items-center gap-6">
          {/* Duration */}
          <div className="text-center">
            <div className="text-xl font-mono font-bold text-white">
              {formatDuration(duration)}
            </div>
            <div className="text-xs text-slate-400">Durée</div>
          </div>
          
          {/* Distance */}
          <div className="text-center">
            <div className="text-xl font-mono font-bold text-emerald-400">
              {formatDistance(distance)}
            </div>
            <div className="text-xs text-slate-400">Distance</div>
          </div>
          
          {/* POIs */}
          <div className="text-center">
            <div className="text-xl font-mono font-bold text-amber-400">
              {poisCount}
            </div>
            <div className="text-xs text-slate-400">POIs</div>
          </div>
        </div>
        
        {/* Recording indicator */}
        {sessionState === 'active' && (
          <div className="flex items-center gap-2 bg-red-900/50 rounded-full px-3 py-1">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-red-400 text-xs font-medium">REC</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionStats;
