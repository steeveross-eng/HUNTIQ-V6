/**
 * WindRose - Wind direction visualization
 */
import React from 'react';

export const WindRose = ({ 
  direction = 0, 
  speed = 0, 
  size = 100,
  showLabels = true
}) => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  
  // Convert wind direction to compass (wind comes FROM this direction)
  const arrowRotation = direction + 180;

  const getSpeedColor = (s) => {
    if (s < 10) return '#10b981'; // Light wind - good
    if (s < 20) return '#22c55e';
    if (s < 30) return '#f59e0b'; // Moderate
    return '#ef4444'; // Strong
  };

  const color = getSpeedColor(speed);

  return (
    <div className="flex flex-col items-center">
      <div 
        className="relative"
        style={{ width: size, height: size }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Outer ring */}
          <circle 
            cx="50" cy="50" r="48" 
            fill="none" 
            stroke="#334155" 
            strokeWidth="2"
          />
          
          {/* Direction markers */}
          {directions.map((dir, i) => {
            const angle = (i * 45 - 90) * (Math.PI / 180);
            const x1 = 50 + Math.cos(angle) * 40;
            const y1 = 50 + Math.sin(angle) * 40;
            const x2 = 50 + Math.cos(angle) * 48;
            const y2 = 50 + Math.sin(angle) * 48;
            const labelX = 50 + Math.cos(angle) * 35;
            const labelY = 50 + Math.sin(angle) * 35;
            
            return (
              <g key={dir}>
                <line 
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke={dir === 'N' ? '#ef4444' : '#64748b'}
                  strokeWidth={dir === 'N' || i % 2 === 0 ? 2 : 1}
                />
                {showLabels && i % 2 === 0 && (
                  <text
                    x={labelX}
                    y={labelY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill={dir === 'N' ? '#ef4444' : '#94a3b8'}
                    fontSize="8"
                    fontWeight={dir === 'N' ? 'bold' : 'normal'}
                  >
                    {dir}
                  </text>
                )}
              </g>
            );
          })}
          
          {/* Wind arrow */}
          <g transform={`rotate(${arrowRotation} 50 50)`}>
            <polygon
              points="50,15 45,35 50,30 55,35"
              fill={color}
            />
            <line
              x1="50" y1="30" x2="50" y2="65"
              stroke={color}
              strokeWidth="4"
              strokeLinecap="round"
            />
          </g>
          
          {/* Center */}
          <circle cx="50" cy="50" r="8" fill="#1e293b" stroke="#475569" strokeWidth="2"/>
        </svg>
      </div>
      
      {/* Speed display */}
      <div className="mt-2 text-center">
        <span className="text-lg font-bold" style={{ color }}>
          {speed} km/h
        </span>
        <span className="text-xs text-slate-400 block">
          {direction}° ({directions[Math.round(direction / 45) % 8]})
        </span>
      </div>
    </div>
  );
};

export default WindRose;
