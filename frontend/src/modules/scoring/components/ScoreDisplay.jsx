/**
 * ScoreDisplay - Main score display component
 */
import React from 'react';

export const ScoreDisplay = ({ 
  score = 0, 
  label = 'Score Bionic™',
  size = 'md',
  showLabel = true,
  animated = true
}) => {
  const getScoreInfo = (s) => {
    if (s >= 90) return { grade: 'S', color: '#a855f7', bg: 'from-purple-900/50 to-purple-800/30' };
    if (s >= 80) return { grade: 'A', color: '#10b981', bg: 'from-emerald-900/50 to-emerald-800/30' };
    if (s >= 70) return { grade: 'B', color: '#22c55e', bg: 'from-green-900/50 to-green-800/30' };
    if (s >= 60) return { grade: 'C', color: '#84cc16', bg: 'from-lime-900/50 to-lime-800/30' };
    if (s >= 50) return { grade: 'D', color: '#f59e0b', bg: 'from-amber-900/50 to-amber-800/30' };
    return { grade: 'F', color: '#ef4444', bg: 'from-red-900/50 to-red-800/30' };
  };

  const { grade, color, bg } = getScoreInfo(score);

  const sizeClasses = {
    sm: { container: 'w-14 h-14', score: 'text-lg', grade: 'text-xs' },
    md: { container: 'w-20 h-20', score: 'text-2xl', grade: 'text-sm' },
    lg: { container: 'w-28 h-28', score: 'text-3xl', grade: 'text-base' },
    xl: { container: 'w-36 h-36', score: 'text-4xl', grade: 'text-lg' }
  };

  const sizes = sizeClasses[size];

  return (
    <div className="flex flex-col items-center">
      <div 
        className={`${sizes.container} rounded-xl bg-gradient-to-br ${bg} border border-slate-600 
                    flex flex-col items-center justify-center relative overflow-hidden
                    ${animated ? 'transition-all duration-300 hover:scale-105' : ''}`}
      >
        {/* Glow effect */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{ background: `radial-gradient(circle at 50% 50%, ${color}, transparent 70%)` }}
        />
        
        {/* Score */}
        <span 
          className={`${sizes.score} font-bold relative z-10`}
          style={{ color }}
        >
          {Math.round(score)}
        </span>
        
        {/* Grade */}
        <span 
          className={`${sizes.grade} font-medium opacity-80 relative z-10`}
          style={{ color }}
        >
          Grade {grade}
        </span>
      </div>
      
      {showLabel && (
        <span className="mt-2 text-xs text-slate-400 text-center">
          {label}
        </span>
      )}
    </div>
  );
};

export default ScoreDisplay;
