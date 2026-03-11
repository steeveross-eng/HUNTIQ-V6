/**
 * MeteoCard - V5-ULTIME
 * =====================
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Cloud, Sun, CloudRain, Snowflake } from 'lucide-react';

const WeatherIcons = {
  clear: Sun,
  clouds: Cloud,
  rain: CloudRain,
  snow: Snowflake,
};

export const MeteoCard = ({ 
  temperature, 
  condition = 'clear', 
  humidity, 
  wind,
  compact = false 
}) => {
  const Icon = WeatherIcons[condition] || Cloud;

  if (compact) {
    return (
      <div className="flex items-center gap-2 p-2 bg-white/5 rounded-lg">
        <Icon className="h-5 w-5 text-[#F5A623]" />
        <span className="text-white font-bold">{temperature}°</span>
      </div>
    );
  }

  return (
    <Card className="bg-black/40 border-white/10">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-4xl font-bold text-white">{temperature}°C</p>
            <p className="text-gray-400 text-sm capitalize mt-1">{condition}</p>
          </div>
          <Icon className="h-12 w-12 text-[#F5A623]" />
        </div>
        <div className="flex gap-4 mt-4 text-sm text-gray-400">
          {humidity && <span>Humidité: {humidity}%</span>}
          {wind && <span>Vent: {wind} km/h</span>}
        </div>
      </CardContent>
    </Card>
  );
};

export default MeteoCard;
