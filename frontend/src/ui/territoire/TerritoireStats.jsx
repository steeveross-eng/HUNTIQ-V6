/**
 * TerritoireStats - V5-ULTIME
 * ===========================
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Mountain, Layers, MapPin, Target } from 'lucide-react';

export const TerritoireStats = ({ 
  totalArea = 0, 
  zonesCount = 0, 
  waypointsCount = 0, 
  averageScore = 0 
}) => {
  const stats = [
    { 
      label: 'Surface Totale', 
      value: `${totalArea} ha`, 
      icon: Mountain, 
      color: 'text-[#F5A623]' 
    },
    { 
      label: 'Zones', 
      value: zonesCount, 
      icon: Layers, 
      color: 'text-blue-400' 
    },
    { 
      label: 'Waypoints', 
      value: waypointsCount, 
      icon: MapPin, 
      color: 'text-green-400' 
    },
    { 
      label: 'Score Moyen', 
      value: averageScore, 
      icon: Target, 
      color: 'text-purple-400' 
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <Card key={idx} className="bg-black/40 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-xs">{stat.label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                </div>
                <Icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default TerritoireStats;
