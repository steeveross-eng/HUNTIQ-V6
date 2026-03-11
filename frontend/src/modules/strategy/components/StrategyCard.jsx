/**
 * StrategyCard - Individual strategy display card
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Sunrise, Sun, Sunset, Moon, Clock, Trophy, Backpack, Lightbulb } from 'lucide-react';

export const StrategyCard = ({ 
  strategy, 
  recommended = false,
  onSelect 
}) => {
  if (!strategy) return null;

  const {
    name = 'Stratégie',
    description = '',
    success_rate = 0,
    difficulty = 'moyen',
    time_of_day = 'all',
    equipment = [],
    tips = []
  } = strategy;

  const getDifficultyColor = (diff) => {
    const colors = {
      facile: 'text-green-400 bg-green-900/30',
      moyen: 'text-amber-400 bg-amber-900/30',
      difficile: 'text-red-400 bg-red-900/30'
    };
    return colors[diff] || colors.moyen;
  };

  const getTimeIcon = (time) => {
    const icons = {
      morning: <Sunrise className="w-4 h-4 text-orange-400" />,
      afternoon: <Sun className="w-4 h-4 text-yellow-400" />,
      evening: <Sunset className="w-4 h-4 text-orange-500" />,
      night: <Moon className="w-4 h-4 text-blue-400" />,
      all: <Clock className="w-4 h-4 text-slate-400" />
    };
    return icons[time] || icons.all;
  };

  return (
    <div 
      className={`
        rounded-lg border p-3 cursor-pointer transition-all hover:scale-[1.02]
        ${recommended 
          ? 'bg-emerald-900/20 border-emerald-700' 
          : 'bg-slate-700/50 border-slate-600 hover:border-slate-500'
        }
      `}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-white font-medium flex items-center gap-2">
          {recommended && <Trophy className="w-4 h-4 text-yellow-400" />}
          {name}
        </h4>
        <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(difficulty)}`}>
          {difficulty}
        </span>
      </div>

      {description && (
        <p className="text-slate-400 text-sm mb-2 line-clamp-2">
          {description}
        </p>
      )}

      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <span className="text-slate-400">
            {getTimeIcon(time_of_day)} {time_of_day}
          </span>
          {success_rate > 0 && (
            <span className="text-emerald-400">
              {success_rate}% succès
            </span>
          )}
        </div>
        
        {equipment.length > 0 && (
          <span className="text-slate-500 flex items-center gap-1">
            <Backpack className="h-3 w-3" /> {equipment.length} équipements
          </span>
        )}
      </div>

      {tips.length > 0 && (
        <div className="mt-2 pt-2 border-t border-slate-600">
          <p className="text-xs text-blue-400 flex items-center gap-1">
            <Lightbulb className="h-3 w-3" /> {tips[0]}
          </p>
        </div>
      )}
    </div>
  );
};

export default StrategyCard;
