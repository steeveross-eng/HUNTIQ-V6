/**
 * ScoringCard - V5-ULTIME
 * =======================
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export const ScoringCard = ({ score, label, trend, icon: Icon }) => {
  const getScoreColor = (score) => {
    if (score >= 85) return '#22c55e';
    if (score >= 70) return '#F5A623';
    if (score >= 50) return '#eab308';
    return '#ef4444';
  };

  return (
    <Card className="bg-black/40 border-white/10">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-gray-400 text-xs">{label}</p>
            <p className="text-2xl font-bold text-white mt-1">{score}</p>
            {trend && (
              <Badge 
                variant="outline" 
                className={trend > 0 ? 'text-green-400' : 'text-red-400'}
              >
                {trend > 0 ? '+' : ''}{trend}%
              </Badge>
            )}
          </div>
          {Icon && (
            <div 
              className="p-2 rounded-lg"
              style={{ backgroundColor: `${getScoreColor(score)}20` }}
            >
              <Icon 
                className="h-5 w-5" 
                style={{ color: getScoreColor(score) }}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ScoringCard;
