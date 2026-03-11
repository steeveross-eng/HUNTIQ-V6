/**
 * CompassWidget - Animated compass display
 */
import React from 'react';

export const CompassWidget = ({ heading = 0 }) => {
  // Get cardinal direction
  const getCardinalDirection = (deg) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(deg / 45) % 8;
    return directions[index];
  };
  
  return (
    <div className="relative w-20 h-20">
      {/* Outer ring */}
      <div className="absolute inset-0 rounded-full bg-slate-800/90 border-2 border-slate-600 shadow-lg">
        {/* Compass rose */}
        <svg 
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 80 80"
          style={{ transform: `rotate(${-heading}deg)`, transition: 'transform 0.2s ease-out' }}
        >
          {/* Cardinal markers */}
          <text x="40" y="14" textAnchor="middle" fill="#ef4444" fontSize="10" fontWeight="bold">N</text>
          <text x="66" y="43" textAnchor="middle" fill="#64748b" fontSize="8">E</text>
          <text x="40" y="72" textAnchor="middle" fill="#64748b" fontSize="8">S</text>
          <text x="14" y="43" textAnchor="middle" fill="#64748b" fontSize="8">W</text>
          
          {/* Tick marks */}
          {[...Array(36)].map((_, i) => (
            <line
              key={i}
              x1="40"
              y1={i % 9 === 0 ? 4 : 6}
              x2="40"
              y2={i % 9 === 0 ? 10 : 8}
              stroke={i === 0 ? '#ef4444' : '#64748b'}
              strokeWidth={i % 9 === 0 ? 2 : 1}
              transform={`rotate(${i * 10} 40 40)`}
            />
          ))}
          
          {/* North pointer */}
          <polygon 
            points="40,18 36,40 40,36 44,40" 
            fill="#ef4444"
          />
          <polygon 
            points="40,62 36,40 40,44 44,40" 
            fill="#64748b"
          />
        </svg>
        
        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-emerald-500 border border-emerald-400"></div>
        </div>
      </div>
      
      {/* Heading display */}
      <div className="absolute -bottom-6 left-0 right-0 text-center">
        <span className="text-white font-mono text-sm font-bold">
          {Math.round(heading)}°
        </span>
        <span className="text-emerald-400 text-xs ml-1">
          {getCardinalDirection(heading)}
        </span>
      </div>
    </div>
  );
};

export default CompassWidget;
