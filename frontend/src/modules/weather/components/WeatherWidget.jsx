/**
 * WeatherWidget - Compact weather display
 * BIONIC Design System compliant
 * Version: 2.0.0 - Full BIONIC compliance (colors + i18n) - Lot A Refactor
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { WeatherService } from '../WeatherService';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Sun, Cloud, CloudRain, Snowflake, CloudLightning, CloudFog, Wind, CloudSun } from 'lucide-react';

// Weather icons - BIONIC Design System (Lucide components + CSS variables)
const WeatherIcon = ({ condition, className = "h-8 w-8" }) => {
  const conditionLower = condition?.toLowerCase() || '';
  
  const iconMap = {
    clear: { Icon: Sun, colorClass: 'text-[var(--bionic-gold-primary)]' },
    sunny: { Icon: Sun, colorClass: 'text-[var(--bionic-gold-primary)]' },
    cloudy: { Icon: Cloud, colorClass: 'text-[var(--bionic-gray-400)]' },
    partly_cloudy: { Icon: CloudSun, colorClass: 'text-[var(--bionic-gold-light)]' },
    rain: { Icon: CloudRain, colorClass: 'text-[var(--bionic-blue-light)]' },
    snow: { Icon: Snowflake, colorClass: 'text-[var(--bionic-cyan-primary)]' },
    storm: { Icon: CloudLightning, colorClass: 'text-[var(--bionic-purple-primary)]' },
    fog: { Icon: CloudFog, colorClass: 'text-[var(--bionic-gray-500)]' },
    wind: { Icon: Wind, colorClass: 'text-[var(--bionic-gray-400)]' }
  };
  
  const { Icon, colorClass } = iconMap[conditionLower] || { Icon: CloudSun, colorClass: 'text-[var(--bionic-gold-light)]' };
  return <Icon className={`${className} ${colorClass}`} />;
};

export const WeatherWidget = ({ 
  lat, 
  lng, 
  compact = false,
  onWeatherLoad
}) => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { t } = useLanguage();

  useEffect(() => {
    const fetchWeather = async () => {
      if (!lat || !lng) {
        setLoading(false);
        return;
      }

      try {
        const data = await WeatherService.getCurrentWeather(lat, lng);
        setWeather(data);
        onWeatherLoad?.(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [lat, lng, onWeatherLoad]);

  if (loading) {
    return (
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]" data-testid="weather-widget-loading">
        <CardContent className="p-4">
          <div className="animate-pulse flex items-center gap-3">
            <div className="w-12 h-12 bg-[var(--bionic-gray-700)] rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-[var(--bionic-gray-700)] rounded w-24" />
              <div className="h-3 bg-[var(--bionic-gray-700)] rounded w-16" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !weather) {
    return (
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]" data-testid="weather-widget-error">
        <CardContent className="p-4 text-center text-[var(--bionic-text-secondary)]">
          <CloudSun className="h-8 w-8 text-[var(--bionic-gold-primary)] mx-auto" />
          <p className="text-sm mt-2">{t('weather_unavailable')}</p>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2 bg-[var(--bionic-bg-card)]/80 rounded-lg px-3 py-2" data-testid="weather-widget-compact">
        <WeatherIcon condition={weather.condition} className="h-6 w-6" />
        <div>
          <span className="text-[var(--bionic-text-primary)] font-bold">{weather.temperature || '--'}°C</span>
          <span className="text-[var(--bionic-text-secondary)] text-xs ml-2">{weather.condition}</span>
        </div>
      </div>
    );
  }

  return (
    <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]" data-testid="weather-widget">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <WeatherIcon condition={weather.condition} className="h-10 w-10" />
            <div>
              <div className="text-3xl font-bold text-[var(--bionic-text-primary)]">
                {weather.temperature || '--'}°C
              </div>
              <div className="text-[var(--bionic-text-secondary)] text-sm capitalize">
                {weather.condition || 'N/A'}
              </div>
            </div>
          </div>
          
          <div className="text-right space-y-1">
            {weather.humidity !== undefined && (
              <div className="text-sm">
                <span className="text-[var(--bionic-text-secondary)]">{t('weather_humidity_label')}:</span>
                <span className="text-[var(--bionic-blue-light)] ml-2">{weather.humidity}%</span>
              </div>
            )}
            {weather.wind_speed !== undefined && (
              <div className="text-sm">
                <span className="text-[var(--bionic-text-secondary)]">{t('weather_wind_label')}:</span>
                <span className="text-[var(--bionic-cyan-primary)] ml-2">{weather.wind_speed} km/h</span>
              </div>
            )}
            {weather.pressure !== undefined && (
              <div className="text-sm">
                <span className="text-[var(--bionic-text-secondary)]">{t('weather_pressure_label')}:</span>
                <span className="text-[var(--bionic-purple-primary)] ml-2">{weather.pressure} hPa</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default WeatherWidget;
