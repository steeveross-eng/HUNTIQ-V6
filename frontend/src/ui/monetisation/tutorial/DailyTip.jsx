/**
 * DailyTip - V5-ULTIME Monétisation
 * ==================================
 * 
 * Affichage du tip du jour.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Wind, Sunrise, Target, MapPin, 
  Thermometer, Clock, X, Lightbulb
} from 'lucide-react';
import TutorialService from './TutorialService';

const iconMap = {
  wind: Wind,
  sunrise: Sunrise,
  target: Target,
  'map-pin': MapPin,
  thermometer: Thermometer,
  clock: Clock
};

const DailyTip = ({ onDismiss }) => {
  const [tip, setTip] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const fetchTip = async () => {
      // Check if already dismissed today
      const dismissedDate = localStorage.getItem('dailyTipDismissed');
      const today = new Date().toDateString();
      
      if (dismissedDate === today) {
        setDismissed(true);
        return;
      }

      const result = await TutorialService.getDailyTip();
      if (result.success && result.tip) {
        setTip(result.tip);
      }
    };

    fetchTip();
  }, []);

  const handleDismiss = () => {
    const today = new Date().toDateString();
    localStorage.setItem('dailyTipDismissed', today);
    setDismissed(true);
    onDismiss && onDismiss();
  };

  if (dismissed || !tip) return null;

  const IconComponent = iconMap[tip.icon] || Lightbulb;

  return (
    <Card 
      data-testid="daily-tip"
      className="bg-gradient-to-r from-[#F5A623]/10 to-purple-500/10 border-[#F5A623]/30"
    >
      <CardContent className="flex items-start gap-4 p-4">
        <div className="p-2 bg-[#F5A623]/20 rounded-lg shrink-0">
          <IconComponent className="h-5 w-5 text-[#F5A623]" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[#F5A623] text-xs font-medium uppercase">
              {tip.title || 'Conseil du jour'}
            </span>
          </div>
          <p className="text-gray-300 text-sm">{tip.content}</p>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleDismiss}
          className="text-gray-500 hover:text-white shrink-0"
        >
          <X className="h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );
};

export default DailyTip;
