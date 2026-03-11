/**
 * ScoreBreakdown - Detailed score breakdown visualization
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { BarChart3 } from 'lucide-react';

export const ScoreBreakdown = ({ breakdown = [], title = 'Détails du Score' }) => {
  if (!breakdown || breakdown.length === 0) {
    return (
      <div className="text-center text-slate-400 py-4">
        Aucune donnée disponible
      </div>
    );
  }

  const maxScore = Math.max(...breakdown.map(b => b.value || 0));

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <h3 className="text-white font-medium mb-4 flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-[var(--bionic-gold-primary)]" />
        {title}
      </h3>
      
      <div className="space-y-3">
        {breakdown.map((item, index) => {
          const percentage = maxScore > 0 ? (item.value / maxScore) * 100 : 0;
          
          return (
            <div key={item.name || index}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-300">{item.name}</span>
                <span className="text-emerald-400 font-medium">
                  {item.value}{item.unit || ''}
                </span>
              </div>
              <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: item.color || '#10b981'
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ScoreBreakdown;
