/**
 * LegalTimeWidget - Display legal hunting hours and sun times
 * BIONIC Design System compliant
 * Version: 2.0.0 - Full BIONIC compliance (colors + i18n + Lucide icons) - Lot D Refactor
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { LegalTimeService } from '../LegalTimeService';
import { 
  Clock, Sun, Moon, Sunrise, Sunset, RefreshCw, 
  Check, X, Info, ClipboardList, CircleDot, Timer
} from 'lucide-react';

export const LegalTimeWidget = ({ 
  coordinates = { lat: 46.8139, lng: -71.2080 },
  date = null,
  compact = false,
  showSlots = true
}) => {
  const { t } = useLanguage();
  const [data, setData] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [windowResult, slotsResult] = await Promise.all([
        LegalTimeService.getLegalWindow(date, coordinates.lat, coordinates.lng),
        showSlots ? LegalTimeService.getRecommendedSlots(date, coordinates.lat, coordinates.lng) : { slots: [] }
      ]);
      
      if (windowResult.success) {
        setData(windowResult);
      }
      if (slotsResult.success && slotsResult.slots) {
        setSlots(slotsResult.slots);
      }
    } catch (error) {
      console.error('Error loading legal time data:', error);
    } finally {
      setLoading(false);
    }
  }, [coordinates, date, showSlots]);

  useEffect(() => {
    loadData();
    
    // Update current time every minute
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(timer);
  }, [loadData]);

  const getStatusConfig = (status) => {
    switch (status) {
      case 'legal': 
        return { 
          bgClass: 'bg-[var(--bionic-green-primary)]', 
          labelKey: 'legaltime_status_legal' 
        };
      case 'before_legal': 
        return { 
          bgClass: 'bg-[var(--bionic-gold-primary)]', 
          labelKey: 'legaltime_status_before' 
        };
      case 'after_legal': 
        return { 
          bgClass: 'bg-[var(--bionic-red-primary)]', 
          labelKey: 'legaltime_status_after' 
        };
      default: 
        return { 
          bgClass: 'bg-[var(--bionic-gray-500)]', 
          labelKey: 'legaltime_status_unknown' 
        };
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--bionic-green-primary)';
    if (score >= 60) return 'var(--bionic-green-light)';
    if (score >= 40) return 'var(--bionic-gold-primary)';
    return 'var(--bionic-red-primary)';
  };

  const getLightConditionIcon = (condition) => {
    switch (condition) {
      case 'dawn': return Sunrise;
      case 'dusk': return Sunset;
      default: return Sun;
    }
  };

  if (loading) {
    return (
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-gold-primary)]/50" data-testid="legal-time-loading">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Sun className="h-8 w-8 text-[var(--bionic-gold-primary)] animate-spin" />
            <span className="ml-3 text-[var(--bionic-text-secondary)]">{t('legaltime_loading')}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const { legal_window, status } = data;
  const currentStatus = status?.current_status || 'legal';
  const isLegal = status?.is_currently_legal;
  const statusConfig = getStatusConfig(currentStatus);

  // Compact version
  if (compact) {
    return (
      <div 
        className={`rounded-lg p-4 border ${
          isLegal 
            ? 'bg-[var(--bionic-green-muted)] border-[var(--bionic-green-primary)]/50' 
            : 'bg-[var(--bionic-gold-muted)] border-[var(--bionic-gold-primary)]/50'
        }`}
        data-testid="legal-time-compact"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CircleDot 
              className={`h-6 w-6 ${isLegal ? 'text-[var(--bionic-green-primary)]' : 'text-[var(--bionic-red-primary)]'}`} 
            />
            <div>
              <p className="text-[var(--bionic-text-primary)] font-medium">
                {isLegal ? t('legaltime_hunting_allowed') : t('legaltime_outside_legal')}
              </p>
              <p className="text-[var(--bionic-text-secondary)] text-sm">
                {legal_window?.start_time} - {legal_window?.end_time}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[var(--bionic-text-muted)] text-xs">{t('legaltime_sunrise_sunset')}</p>
            <p className="text-[var(--bionic-text-primary)] text-sm flex items-center gap-2">
              <Sunrise className="h-3 w-3 text-[var(--bionic-gold-primary)]" />
              {legal_window?.sunrise}
              <Moon className="h-3 w-3 text-[var(--bionic-purple-primary)] ml-2" />
              {legal_window?.sunset}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card 
      className="bg-[var(--bionic-bg-card)] border-[var(--bionic-gold-primary)]/50"
      data-testid="legal-time-widget"
    >
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
            {t('legaltime_title')}
          </span>
          <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)] border-0">
            Québec
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Current Status Banner */}
          <div 
            className={`rounded-lg p-4 ${
              isLegal 
                ? 'bg-[var(--bionic-green-muted)] border border-[var(--bionic-green-primary)]/50' 
                : 'bg-[var(--bionic-red-muted)] border border-[var(--bionic-red-primary)]/50'
            }`}
            data-testid="legal-status-banner"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${statusConfig.bgClass} animate-pulse`} />
                <div>
                  <p className={`font-bold text-lg ${isLegal ? 'text-[var(--bionic-green-primary)]' : 'text-[var(--bionic-red-primary)]'}`}>
                    {t(statusConfig.labelKey)}
                  </p>
                  <p className="text-[var(--bionic-text-secondary)] text-sm">
                    {currentTime.toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
              <Badge 
                className={`${isLegal ? 'bg-[var(--bionic-green-primary)] text-white' : 'bg-[var(--bionic-red-primary)] text-white'} border-0`}
              >
                {isLegal ? (
                  <span className="flex items-center gap-1">
                    <Check className="h-3 w-3" /> {t('legaltime_badge_legal')}
                  </span>
                ) : (
                  <span className="flex items-center gap-1">
                    <X className="h-3 w-3" /> {t('legaltime_badge_forbidden')}
                  </span>
                )}
              </Badge>
            </div>
          </div>

          {/* Sun Times Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[var(--bionic-bg-hover)] rounded-lg p-3 text-center" data-testid="legal-start">
              <p className="text-[var(--bionic-text-secondary)] text-xs mb-1">{t('legaltime_start')}</p>
              <p className="text-2xl font-bold text-[var(--bionic-gold-primary)]">
                {legal_window?.start_time}
              </p>
              <p className="text-[var(--bionic-text-muted)] text-xs mt-1">{t('legaltime_before_sunrise')}</p>
            </div>
            <div className="bg-[var(--bionic-bg-hover)] rounded-lg p-3 text-center" data-testid="legal-end">
              <p className="text-[var(--bionic-text-secondary)] text-xs mb-1">{t('legaltime_end')}</p>
              <p className="text-2xl font-bold text-[var(--bionic-purple-primary)]">
                {legal_window?.end_time}
              </p>
              <p className="text-[var(--bionic-text-muted)] text-xs mt-1">{t('legaltime_after_sunset')}</p>
            </div>
          </div>

          {/* Sun Times Row */}
          <div className="bg-[var(--bionic-bg-hover)]/50 rounded-lg p-3">
            <div className="flex justify-around text-center">
              <div>
                <Sunrise className="h-6 w-6 mx-auto text-[var(--bionic-gold-primary)]" />
                <p className="text-[var(--bionic-text-primary)] font-medium">{legal_window?.sunrise}</p>
                <p className="text-[var(--bionic-text-muted)] text-xs">{t('legaltime_sunrise')}</p>
              </div>
              <div className="border-l border-[var(--bionic-border-secondary)]" />
              <div>
                <Timer className="h-6 w-6 mx-auto text-[var(--bionic-blue-light)]" />
                <p className="text-[var(--bionic-text-primary)] font-medium">{legal_window?.duration_hours}h</p>
                <p className="text-[var(--bionic-text-muted)] text-xs">{t('legaltime_duration')}</p>
              </div>
              <div className="border-l border-[var(--bionic-border-secondary)]" />
              <div>
                <Sunset className="h-6 w-6 mx-auto text-[var(--bionic-purple-primary)]" />
                <p className="text-[var(--bionic-text-primary)] font-medium">{legal_window?.sunset}</p>
                <p className="text-[var(--bionic-text-muted)] text-xs">{t('legaltime_sunset')}</p>
              </div>
            </div>
          </div>

          {/* Recommended Slots */}
          {showSlots && slots.length > 0 && (
            <div>
              <p className="text-[var(--bionic-text-secondary)] text-sm mb-2 flex items-center gap-2">
                <ClipboardList className="h-4 w-4 text-[var(--bionic-gold-primary)]" />
                {t('legaltime_recommended_slots')}
              </p>
              <div className="space-y-2">
                {slots.slice(0, 3).map((slot, index) => {
                  const SlotIcon = getLightConditionIcon(slot.light_condition);
                  const scoreColor = getScoreColor(slot.score);
                  return (
                    <div 
                      key={index}
                      className="flex items-center justify-between bg-[var(--bionic-bg-hover)]/50 rounded-lg p-2"
                      data-testid={`slot-${index}`}
                    >
                      <div className="flex items-center gap-2">
                        <SlotIcon className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                        <div>
                          <p className="text-[var(--bionic-text-primary)] text-sm font-medium">{slot.period}</p>
                          <p className="text-[var(--bionic-text-secondary)] text-xs">
                            {slot.start_time} - {slot.end_time}
                          </p>
                        </div>
                      </div>
                      <Badge 
                        className="text-xs border-0"
                        style={{ 
                          backgroundColor: `${scoreColor}20`,
                          color: scoreColor
                        }}
                      >
                        {slot.score}%
                      </Badge>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Regulation Note */}
          <div className="bg-[var(--bionic-blue-muted)] border border-[var(--bionic-blue-primary)]/50 rounded-lg p-3" data-testid="regulation-note">
            <p className="text-[var(--bionic-blue-light)] text-xs flex items-center gap-2">
              <Info className="h-4 w-4 flex-shrink-0" />
              {t('legaltime_regulation_note')}
            </p>
          </div>

          <Button 
            className="w-full bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-dark)] text-[var(--bionic-bg-primary)]"
            onClick={loadData}
            data-testid="refresh-button"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('legaltime_refresh')}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default LegalTimeWidget;
