/**
 * WeatherForecast - Multi-day forecast display
 * BIONIC Design System compliant
 * Version: 2.0.0 - Full BIONIC compliance (colors + i18n + Lucide icons) - Lot B Refactor
 */
import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Sun, Cloud, CloudSun, CloudRain, Snowflake, CloudLightning, CloudFog, Calendar } from 'lucide-react';

// Weather icons - BIONIC Design System (Lucide components + CSS variables)
const WeatherIconComponent = ({ condition, className = "h-6 w-6" }) => {
  const conditionLower = condition?.toLowerCase() || '';
  
  const iconMap = {
    clear: { Icon: Sun, colorClass: 'text-[var(--bionic-gold-primary)]' },
    sunny: { Icon: Sun, colorClass: 'text-[var(--bionic-gold-primary)]' },
    cloudy: { Icon: Cloud, colorClass: 'text-[var(--bionic-gray-400)]' },
    partly_cloudy: { Icon: CloudSun, colorClass: 'text-[var(--bionic-gold-light)]' },
    rain: { Icon: CloudRain, colorClass: 'text-[var(--bionic-blue-light)]' },
    snow: { Icon: Snowflake, colorClass: 'text-[var(--bionic-cyan-primary)]' },
    storm: { Icon: CloudLightning, colorClass: 'text-[var(--bionic-purple-primary)]' },
    fog: { Icon: CloudFog, colorClass: 'text-[var(--bionic-gray-500)]' }
  };
  
  const { Icon, colorClass } = iconMap[conditionLower] || { Icon: CloudSun, colorClass: 'text-[var(--bionic-gold-light)]' };
  return <Icon className={`${className} ${colorClass}`} />;
};

export const WeatherForecast = ({ forecast = [], days = 5 }) => {
  const { t } = useLanguage();
  const displayForecast = forecast.slice(0, days);

  if (!displayForecast.length) {
    return (
      <div className="text-center text-[var(--bionic-text-secondary)] py-4" data-testid="weather-forecast-empty">
        {t('forecast_unavailable')}
      </div>
    );
  }

  return (
    <div className="bg-[var(--bionic-bg-card)]/50 rounded-lg p-4 border border-[var(--bionic-border-primary)]" data-testid="weather-forecast">
      <h3 className="text-[var(--bionic-text-primary)] font-medium mb-3 flex items-center gap-2">
        <Calendar className="h-4 w-4 text-[var(--bionic-gold-primary)]" />
        {t('forecast_days_title').replace('{days}', days)}
      </h3>
      
      <div className="grid grid-cols-5 gap-2">
        {displayForecast.map((day, index) => (
          <div 
            key={index}
            className="text-center p-2 rounded-lg bg-[var(--bionic-gray-700)]/50 hover:bg-[var(--bionic-gray-700)] transition-colors"
            data-testid={`forecast-day-${index}`}
          >
            <div className="text-xs text-[var(--bionic-text-secondary)] mb-1">
              {day.day || `${t('forecast_day_prefix')}${index + 1}`}
            </div>
            <div className="flex justify-center mb-1">
              <WeatherIconComponent condition={day.condition} className="h-6 w-6" />
            </div>
            <div className="text-sm text-[var(--bionic-text-primary)] font-medium">
              {day.temp_max || '--'}°
            </div>
            <div className="text-xs text-[var(--bionic-text-secondary)]">
              {day.temp_min || '--'}°
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeatherForecast;
