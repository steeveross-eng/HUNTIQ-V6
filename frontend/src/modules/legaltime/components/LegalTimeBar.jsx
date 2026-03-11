/**
 * LegalTimeBar - Compact bar showing current legal status
 * Perfect for headers or navigation areas
 */
import React, { useState, useEffect } from 'react';
import { Badge } from '../../../components/ui/badge';
import { LegalTimeService } from '../LegalTimeService';
import { Sunrise, Sunset, Loader2 } from 'lucide-react';

export const LegalTimeBar = ({ 
  coordinates = { lat: 46.8139, lng: -71.2080 }
}) => {
  const [data, setData] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const loadData = async () => {
      const result = await LegalTimeService.checkLegalNow(
        coordinates.lat, 
        coordinates.lng
      );
      if (result.success) {
        setData(result);
      }
    };

    loadData();
    
    // Refresh every minute
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      loadData();
    }, 60000);

    return () => clearInterval(timer);
  }, [coordinates]);

  if (!data) {
    return (
      <div className="flex items-center gap-2 text-slate-400 text-sm">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Chargement...</span>
      </div>
    );
  }

  const { is_legal, legal_window, sunrise, sunset } = data;

  return (
    <div 
      className="flex items-center gap-4 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700"
      data-testid="legal-time-bar"
    >
      {/* Status Indicator */}
      <div className="flex items-center gap-2">
        <div 
          className={`w-3 h-3 rounded-full ${
            is_legal ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`}
        />
        <span className={`font-medium text-sm ${
          is_legal ? 'text-green-400' : 'text-red-400'
        }`}>
          {is_legal ? 'Chasse légale' : 'Hors période'}
        </span>
      </div>

      <div className="h-4 border-l border-slate-600" />

      {/* Legal Window */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-slate-400">Fenêtre:</span>
        <span className="text-white font-medium">
          {legal_window?.start} - {legal_window?.end}
        </span>
      </div>

      <div className="h-4 border-l border-slate-600" />

      {/* Sun Times */}
80|      <div className="flex items-center gap-3 text-sm">
81|        <span className="flex items-center gap-1">
          <Sunrise className="h-4 w-4 text-amber-400" />
          <span className="text-amber-400">{sunrise}</span>
        </span>
        <span className="flex items-center gap-1">
          <Sunset className="h-4 w-4 text-purple-400" />
          <span className="text-purple-400">{sunset}</span>
        </span>
      </div>

      {/* Current Time */}
      <Badge className="bg-slate-700 text-slate-300 ml-auto">
        {currentTime.toLocaleTimeString('fr-CA', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}
      </Badge>
    </div>
  );
};

export default LegalTimeBar;
