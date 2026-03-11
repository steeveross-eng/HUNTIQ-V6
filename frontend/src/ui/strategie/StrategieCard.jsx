/**
 * StrategieCard - V5-ULTIME
 * =========================
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, Target, Compass, Zap } from 'lucide-react';

const TypeIcons = {
  approach: Compass,
  ambush: Target,
  tracking: Lightbulb,
  call: Zap,
};

export const StrategieCard = ({ 
  name, 
  type, 
  description, 
  successRate,
  isRecommended = false 
}) => {
  const Icon = TypeIcons[type] || Lightbulb;

  return (
    <Card className={`bg-black/40 border-white/10 ${isRecommended ? 'ring-2 ring-[#F5A623]' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-[#F5A623]/20">
            <Icon className="h-5 w-5 text-[#F5A623]" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h4 className="text-white font-medium">{name}</h4>
              {isRecommended && (
                <Badge className="bg-[#F5A623] text-black text-[10px]">
                  Recommandé
                </Badge>
              )}
            </div>
            <p className="text-gray-400 text-xs mt-1 capitalize">{type}</p>
            <p className="text-gray-500 text-sm mt-2">{description}</p>
            {successRate && (
              <p className="text-[#F5A623] text-xs mt-2">
                {successRate}% de réussite
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StrategieCard;
