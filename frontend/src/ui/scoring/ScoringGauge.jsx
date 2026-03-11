/**
 * ScoringGauge - V5-ULTIME
 * ========================
 */

import React from 'react';

export const ScoringGauge = ({ value, max = 100, size = 'md', label }) => {
  const sizes = {
    sm: { width: 80, stroke: 6, fontSize: 'text-lg' },
    md: { width: 120, stroke: 8, fontSize: 'text-2xl' },
    lg: { width: 160, stroke: 10, fontSize: 'text-3xl' },
  };

  const { width, stroke, fontSize } = sizes[size];
  const radius = (width - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (value / max) * circumference;

  const getColor = () => {
    const percentage = (value / max) * 100;
    if (percentage >= 85) return '#22c55e';
    if (percentage >= 70) return '#F5A623';
    if (percentage >= 50) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width, height: width }}>
        <svg className="transform -rotate-90" width={width} height={width}>
          {/* Background circle */}
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={stroke}
          />
          {/* Progress circle */}
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke={getColor()}
            strokeWidth={stroke}
            strokeDasharray={`${progress} ${circumference}`}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold text-white ${fontSize}`}>{value}</span>
        </div>
      </div>
      {label && <p className="text-gray-400 text-sm mt-2">{label}</p>}
    </div>
  );
};

export default ScoringGauge;
