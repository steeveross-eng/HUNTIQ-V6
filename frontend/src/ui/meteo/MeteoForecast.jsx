/**
 * MeteoForecast - V5-ULTIME
 * =========================
 */

import React from 'react';
import { Cloud, Sun, CloudRain, Snowflake } from 'lucide-react';

const WeatherIcons = {
  clear: Sun,
  clouds: Cloud,
  rain: CloudRain,
  snow: Snowflake,
};

export const MeteoForecast = ({ forecast = [], compact = false }) => {
  if (!forecast.length) return null;

  return (
    <div className={`grid ${compact ? 'grid-cols-3' : 'grid-cols-5'} gap-2`}>
      {forecast.slice(0, compact ? 3 : 5).map((day, idx) => {
        const Icon = WeatherIcons[day.condition] || Cloud;
        
        return (
          <div 
            key={idx}
            className="flex flex-col items-center p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
          >
            <p className="text-gray-400 text-xs">{day.day}</p>
            <Icon className="h-6 w-6 my-2 text-gray-300" />
            <p className="text-white font-semibold">{day.high}°</p>
            <p className="text-gray-500 text-xs">{day.low}°</p>
          </div>
        );
      })}
    </div>
  );
};

export default MeteoForecast;
