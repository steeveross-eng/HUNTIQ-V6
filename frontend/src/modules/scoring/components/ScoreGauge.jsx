/**
 * ScoreGauge - Animated gauge score visualization
 */
import React, { useEffect, useState } from 'react';

export const ScoreGauge = ({ 
  value = 0, 
  maxValue = 100, 
  label = '',
  color = '#10b981',
  size = 120
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const percentage = Math.min((animatedValue / maxValue) * 100, 100);
  const angle = (percentage / 100) * 180 - 90; // -90 to 90 degrees

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <svg 
        viewBox="0 0 120 70" 
        className="w-full"
        style={{ height: size * 0.58 }}
      >
        {/* Background arc */}
        <path
          d="M 10 60 A 50 50 0 0 1 110 60"
          fill="none"
          stroke="#334155"
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Value arc */}
        <path
          d="M 10 60 A 50 50 0 0 1 110 60"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${percentage * 1.57} 157`}
          style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
        />
        
        {/* Needle */}
        <g 
          transform={`rotate(${angle} 60 60)`}
          style={{ transition: 'transform 0.8s ease-out' }}
        >
          <line
            x1="60"
            y1="60"
            x2="60"
            y2="20"
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx="60" cy="60" r="6" fill={color} />
          <circle cx="60" cy="60" r="3" fill="#1e293b" />
        </g>
        
        {/* Min/Max labels */}
        <text x="10" y="68" fill="#64748b" fontSize="8" textAnchor="middle">0</text>
        <text x="110" y="68" fill="#64748b" fontSize="8" textAnchor="middle">{maxValue}</text>
      </svg>
      
      {/* Value display */}
      <div className="text-center -mt-2">
        <span className="text-2xl font-bold" style={{ color }}>
          {Math.round(animatedValue)}
        </span>
        {label && (
          <span className="block text-xs text-slate-400 mt-1">{label}</span>
        )}
      </div>
    </div>
  );
};

export default ScoreGauge;
