/**
 * WindIndicator - Wind direction and favorability display
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Check, AlertTriangle } from 'lucide-react';

export const WindIndicator = ({ wind, userHeading = 0 }) => {
  if (!wind) return null;
  
  // Calculate relative wind angle
  const relativeWind = (wind.direction - userHeading + 360) % 360;
  
  return (
    <div className="bg-slate-800/90 rounded-lg p-3 border border-slate-600 shadow-lg">
      {/* Wind arrow */}
      <div className="flex items-center gap-3">
        <div 
          className="relative w-10 h-10"
          style={{ 
            transform: `rotate(${relativeWind}deg)`,
            transition: 'transform 0.3s ease-out'
          }}
        >
          <svg viewBox="0 0 40 40" className="w-full h-full">
            <defs>
              <linearGradient id="windGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={wind.favorable ? '#10b981' : '#f59e0b'} />
                <stop offset="100%" stopColor={wind.favorable ? '#059669' : '#d97706'} />
              </linearGradient>
            </defs>
            {/* Wind arrow */}
            <path 
              d="M 20 5 L 28 25 L 20 20 L 12 25 Z"
              fill="url(#windGradient)"
            />
            {/* Wind streaks */}
            <line x1="15" y1="28" x2="15" y2="35" stroke={wind.favorable ? '#10b981' : '#f59e0b'} strokeWidth="2" strokeLinecap="round"/>
            <line x1="20" y1="26" x2="20" y2="35" stroke={wind.favorable ? '#10b981' : '#f59e0b'} strokeWidth="2" strokeLinecap="round"/>
            <line x1="25" y1="28" x2="25" y2="35" stroke={wind.favorable ? '#10b981' : '#f59e0b'} strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>
        
        <div className="text-sm">
          <div className="text-white font-medium">
            {wind.speed_kmh.toFixed(0)} km/h
          </div>
          <div className={`text-xs flex items-center gap-1 ${wind.favorable ? 'text-emerald-400' : 'text-amber-400'}`}>
            {wind.favorable ? <><Check className="w-3 h-3" /> Favorable</> : <><AlertTriangle className="w-3 h-3" /> Attention</>}
          </div>
        </div>
      </div>
      
      {/* Wind notes */}
      {wind.notes && (
        <div className="mt-2 text-xs text-slate-400 max-w-32">
          {wind.notes}
        </div>
      )}
      
      {/* Gusts indicator */}
      {wind.gusts_kmh && wind.gusts_kmh > wind.speed_kmh * 1.2 && (
        <div className="mt-1 text-xs text-amber-400">
          Rafales: {wind.gusts_kmh.toFixed(0)} km/h
        </div>
      )}
    </div>
  );
};

export default WindIndicator;
