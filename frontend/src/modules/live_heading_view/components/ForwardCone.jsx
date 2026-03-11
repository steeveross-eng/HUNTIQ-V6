/**
 * ForwardCone - Forward view cone visualization (standalone)
 */
import React from 'react';

export const ForwardCone = ({ 
  aperture = 60, 
  range = 500,
  heading = 0,
  color = '#10b981'
}) => {
  // Calculate cone path
  const halfAperture = aperture / 2;
  const angleRad = halfAperture * Math.PI / 180;
  const coneWidth = Math.tan(angleRad) * 180; // Scale for SVG
  
  return (
    <svg 
      className="w-full h-full"
      viewBox="0 0 400 400"
      style={{ transform: `rotate(${heading}deg)`, transition: 'transform 0.2s ease-out' }}
    >
      <defs>
        <linearGradient id="forwardConeGradient" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stopColor={color} stopOpacity="0.5" />
          <stop offset="100%" stopColor={color} stopOpacity="0.05" />
        </linearGradient>
        
        <filter id="coneShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor={color} floodOpacity="0.3"/>
        </filter>
      </defs>
      
      {/* Cone area */}
      <path
        d={`M 200 300 L ${200 - coneWidth} 100 A 180 180 0 0 1 ${200 + coneWidth} 100 Z`}
        fill="url(#forwardConeGradient)"
        stroke={color}
        strokeWidth="2"
        strokeOpacity="0.6"
        filter="url(#coneShadow)"
      />
      
      {/* Center direction line */}
      <line 
        x1="200" y1="300" 
        x2="200" y2="100" 
        stroke={color} 
        strokeWidth="2" 
        strokeDasharray="10,5"
        opacity="0.8"
      />
      
      {/* Range markers */}
      <circle cx="200" cy="200" r="60" fill="none" stroke={color} strokeWidth="1" strokeDasharray="4,4" opacity="0.3"/>
      <circle cx="200" cy="150" r="90" fill="none" stroke={color} strokeWidth="1" strokeDasharray="4,4" opacity="0.2"/>
      
      {/* Distance labels */}
      <text x="265" y="205" fill={color} fontSize="10" opacity="0.6">{Math.round(range * 0.4)}m</text>
      <text x="295" y="155" fill={color} fontSize="10" opacity="0.4">{Math.round(range * 0.7)}m</text>
      
      {/* Center point */}
      <circle cx="200" cy="300" r="6" fill={color} />
      <circle cx="200" cy="300" r="10" fill="none" stroke={color} strokeWidth="2" opacity="0.5" />
    </svg>
  );
};

export default ForwardCone;
