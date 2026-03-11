/**
 * NutritionScore - Score visualization component
 */
import React from 'react';

export const NutritionScore = ({ score = 0, maxScore = 100, size = 'md' }) => {
  const percentage = Math.min((score / maxScore) * 100, 100);
  
  const getScoreColor = (pct) => {
    if (pct >= 80) return { color: '#10b981', label: 'Excellent' };
    if (pct >= 60) return { color: '#22c55e', label: 'Bon' };
    if (pct >= 40) return { color: '#f59e0b', label: 'Moyen' };
    if (pct >= 20) return { color: '#f97316', label: 'Faible' };
    return { color: '#ef4444', label: 'Insuffisant' };
  };

  const { color, label } = getScoreColor(percentage);

  const sizeClasses = {
    sm: 'w-16 h-16 text-lg',
    md: 'w-24 h-24 text-2xl',
    lg: 'w-32 h-32 text-3xl'
  };

  const radius = size === 'sm' ? 28 : size === 'md' ? 44 : 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${sizeClasses[size]}`}>
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke="#334155"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${sizeClasses[size].split(' ')[2]}`} style={{ color }}>
            {Math.round(score)}
          </span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <span className="text-sm font-medium" style={{ color }}>
          {label}
        </span>
      </div>
    </div>
  );
};

export default NutritionScore;
