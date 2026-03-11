/**
 * StrategyTimeline - Hunting day timeline
 */
import React from 'react';
import { Calendar, MapPin } from 'lucide-react';

export const StrategyTimeline = ({ schedule = [] }) => {
  if (!schedule.length) {
    return (
      <div className="text-center text-slate-400 py-4">
        Aucun planning disponible
      </div>
    );
  }

  const getTimeColor = (hour) => {
    if (hour < 6) return '#6366f1'; // Night - indigo
    if (hour < 9) return '#f59e0b'; // Morning - amber
    if (hour < 17) return '#22c55e'; // Day - green
    if (hour < 20) return '#f97316'; // Evening - orange
    return '#6366f1'; // Night - indigo
  };

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <h3 className="text-white font-medium mb-4 flex items-center gap-2">
        <Calendar className="h-5 w-5 text-[#f5a623]" />
        Planning de la Journée
      </h3>
      
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-700" />
        
        {/* Events */}
        <div className="space-y-4">
          {schedule.map((event, index) => {
            const hour = parseInt(event.time?.split(':')[0] || 0);
            const color = getTimeColor(hour);
            
            return (
              <div key={index} className="relative flex items-start gap-4 pl-8">
                {/* Dot */}
                <div 
                  className="absolute left-2.5 w-3 h-3 rounded-full border-2 bg-slate-900"
                  style={{ borderColor: color }}
                />
                
                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span 
                      className="text-sm font-mono font-medium"
                      style={{ color }}
                    >
                      {event.time || '--:--'}
                    </span>
                    <span className="text-white font-medium">
                      {event.activity}
                    </span>
                  </div>
                  {event.notes && (
                    <p className="text-slate-400 text-sm mt-1">
                      {event.notes}
                    </p>
                  )}
                  {event.location && (
                    <span className="text-xs text-blue-400 flex items-center gap-1">
                      <MapPin className="h-3 w-3" /> {event.location}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default StrategyTimeline;
