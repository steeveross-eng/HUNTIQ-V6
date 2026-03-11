/**
 * SmartAlerts - Composant d'alertes intelligentes pour le module GROUPE
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 5
 * 
 * Affiche et gère les alertes de sécurité, proximité, météo et activité.
 */
import React, { useState, useCallback, useMemo } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { 
  Bell, BellOff, ShieldAlert, Users, CloudRain, Activity, Target,
  MapPin, X, Check, ChevronDown, ChevronUp, Eye, MessageSquare,
  Navigation, AlertTriangle, Info, CheckCircle, Filter, Trash2,
  Volume2, VolumeX, Settings, Clock
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Card, CardContent } from '../../../components/ui/card';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { Switch } from '../../../components/ui/switch';
import { ALERT_TYPES, ALERT_SEVERITY } from '../hooks/useGroupeAlerts';

// Mapping des icônes par type d'alerte
const ALERT_ICONS = {
  safety: ShieldAlert,
  proximity: Users,
  weather: CloudRain,
  activity: Activity,
  game: Target,
  zone: MapPin
};

// Mapping des icônes par sévérité
const SEVERITY_ICONS = {
  critical: AlertTriangle,
  warning: AlertTriangle,
  info: Info,
  success: CheckCircle
};

/**
 * Badge de type d'alerte
 */
const AlertTypeBadge = ({ type, compact = false }) => {
  const { t } = useLanguage();
  const config = ALERT_TYPES[type] || ALERT_TYPES.activity;
  const Icon = ALERT_ICONS[type] || Activity;
  
  if (compact) {
    return (
      <div 
        className="w-6 h-6 rounded-full flex items-center justify-center"
        style={{ backgroundColor: config.bgVar }}
        title={t(config.labelKey)}
      >
        <Icon className="w-3 h-3" style={{ color: config.colorVar }} />
      </div>
    );
  }
  
  return (
    <Badge
      className="text-[10px] border-0 font-medium"
      style={{ backgroundColor: config.bgVar, color: config.colorVar }}
    >
      <Icon className="w-3 h-3 mr-1" />
      {t(config.labelKey)}
    </Badge>
  );
};

/**
 * Badge de sévérité
 */
const SeverityBadge = ({ severity }) => {
  const { t } = useLanguage();
  const config = ALERT_SEVERITY[severity] || ALERT_SEVERITY.info;
  const Icon = SEVERITY_ICONS[severity] || Info;
  
  return (
    <Badge
      className="text-[10px] border-0 uppercase font-bold"
      style={{ backgroundColor: config.bgVar, color: config.colorVar }}
    >
      <Icon className="w-3 h-3 mr-1" />
      {t(config.labelKey)}
    </Badge>
  );
};

/**
 * Élément d'alerte individuel
 */
const AlertItem = ({ 
  alert, 
  onRead, 
  onDismiss, 
  onAction,
  compact = false 
}) => {
  const { t } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(false);
  
  const config = ALERT_TYPES[alert.type] || ALERT_TYPES.activity;
  const Icon = ALERT_ICONS[alert.type] || Activity;
  
  // Formater le temps relatif
  const getRelativeTime = (timestamp) => {
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}min`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}j`;
  };
  
  // Construire le message traduit
  const getMessage = () => {
    let message = t(alert.message);
    if (alert.memberName) {
      message = message.replace('{member}', alert.memberName);
    }
    if (alert.data?.distance) {
      message = message.replace('{distance}', `${alert.data.distance}m`);
    }
    if (alert.data?.probability) {
      message = message.replace('{probability}', `${alert.data.probability}%`);
    }
    if (alert.data?.windSpeed) {
      message = message.replace('{speed}', `${alert.data.windSpeed} km/h`);
    }
    return message;
  };
  
  if (compact) {
    return (
      <div 
        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
          alert.read ? 'opacity-60' : ''
        }`}
        style={{ backgroundColor: config.bgVar }}
        onClick={() => !alert.read && onRead?.(alert.id)}
      >
        <Icon className="w-4 h-4 flex-shrink-0" style={{ color: config.colorVar }} />
        <div className="flex-1 min-w-0">
          <p className="text-xs truncate" style={{ color: config.colorVar }}>
            {t(alert.title)}
          </p>
        </div>
        <span className="text-[10px] text-[var(--bionic-text-muted)]">
          {getRelativeTime(alert.timestamp)}
        </span>
      </div>
    );
  }
  
  return (
    <Card 
      className={`border transition-all ${
        alert.read 
          ? 'border-[var(--bionic-border-secondary)] opacity-70' 
          : 'border-l-4'
      }`}
      style={{ 
        borderLeftColor: alert.read ? undefined : config.colorVar,
        backgroundColor: alert.read ? 'var(--bionic-bg-card)' : config.bgVar
      }}
      data-testid={`alert-${alert.id}`}
    >
      <CardContent className="p-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2 flex-1 min-w-0">
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: alert.read ? 'var(--bionic-bg-hover)' : 'rgba(0,0,0,0.1)' }}
            >
              <Icon className="w-4 h-4" style={{ color: config.colorVar }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="text-sm font-medium text-[var(--bionic-text-primary)]">
                  {t(alert.title)}
                </p>
                <SeverityBadge severity={alert.severity} />
              </div>
              <p className="text-xs text-[var(--bionic-text-secondary)] mt-0.5">
                {getMessage()}
              </p>
              {alert.memberName && (
                <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
                  <Users className="w-3 h-3 inline mr-1" />
                  {alert.memberName}
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-[10px] text-[var(--bionic-text-muted)]">
              {getRelativeTime(alert.timestamp)}
            </span>
            {!alert.read && (
              <span className="w-2 h-2 rounded-full bg-[var(--bionic-gold-primary)]" />
            )}
          </div>
        </div>
        
        {/* Actions */}
        {alert.actionable && alert.actions?.length > 0 && (
          <>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-1 text-[10px] text-[var(--bionic-text-muted)] hover:text-[var(--bionic-text-secondary)] mt-2"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  {t('alerts_hide_actions')}
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  {t('alerts_show_actions')}
                </>
              )}
            </button>
            
            {isExpanded && (
              <div className="flex flex-wrap gap-2 mt-2 pt-2 border-t border-[var(--bionic-border-secondary)]">
                {alert.actions.includes('view_on_map') && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onAction?.('view_on_map', alert)}
                    className="h-7 text-xs border-[var(--bionic-border-secondary)]"
                  >
                    <Eye className="w-3 h-3 mr-1" />
                    {t('alerts_action_view_map')}
                  </Button>
                )}
                {alert.actions.includes('send_message') && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onAction?.('send_message', alert)}
                    className="h-7 text-xs border-[var(--bionic-border-secondary)]"
                  >
                    <MessageSquare className="w-3 h-3 mr-1" />
                    {t('alerts_action_message')}
                  </Button>
                )}
                {alert.actions.includes('contact_member') && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onAction?.('contact_member', alert)}
                    className="h-7 text-xs border-[var(--bionic-border-secondary)]"
                  >
                    <Users className="w-3 h-3 mr-1" />
                    {t('alerts_action_contact')}
                  </Button>
                )}
                {alert.actions.includes('share_location') && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onAction?.('share_location', alert)}
                    className="h-7 text-xs border-[var(--bionic-border-secondary)]"
                  >
                    <Navigation className="w-3 h-3 mr-1" />
                    {t('alerts_action_share')}
                  </Button>
                )}
              </div>
            )}
          </>
        )}
        
        {/* Footer actions */}
        <div className="flex items-center justify-end gap-1 mt-2">
          {!alert.read && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRead?.(alert.id)}
              className="h-6 text-[10px] text-[var(--bionic-text-muted)] hover:text-[var(--bionic-green-primary)]"
            >
              <Check className="w-3 h-3 mr-1" />
              {t('alerts_mark_read')}
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDismiss?.(alert.id)}
            className="h-6 text-[10px] text-[var(--bionic-text-muted)] hover:text-[var(--bionic-red-primary)]"
          >
            <X className="w-3 h-3 mr-1" />
            {t('alerts_dismiss')}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Filtre par type d'alerte
 */
const AlertTypeFilter = ({ activeTypes, onToggle }) => {
  const { t } = useLanguage();
  
  return (
    <div className="flex flex-wrap gap-1">
      {Object.entries(ALERT_TYPES).map(([type, config]) => {
        const Icon = ALERT_ICONS[type] || Activity;
        const isActive = activeTypes.includes(type);
        
        return (
          <button
            key={type}
            onClick={() => onToggle(type)}
            className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] transition-all ${
              isActive 
                ? 'border' 
                : 'opacity-50 hover:opacity-75'
            }`}
            style={isActive ? {
              backgroundColor: config.bgVar,
              borderColor: config.colorVar,
              color: config.colorVar
            } : {
              backgroundColor: 'var(--bionic-bg-hover)'
            }}
          >
            <Icon className="w-3 h-3" />
            {t(config.labelKey)}
          </button>
        );
      })}
    </div>
  );
};

/**
 * Composant principal SmartAlerts
 */
export const SmartAlerts = ({
  alerts = [],
  unreadCount = 0,
  settings = {},
  isMuted = false,
  onMarkAsRead,
  onMarkAllAsRead,
  onDismiss,
  onClearAll,
  onToggleMute,
  onUpdateSettings,
  onAction,
  compact = false,
  showSettings = true,
  showFilters = true,
  maxHeight = '400px'
}) => {
  const { t } = useLanguage();
  const [activeFilters, setActiveFilters] = useState(Object.keys(ALERT_TYPES));
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  
  // Filtrer les alertes
  const filteredAlerts = useMemo(() => {
    return alerts.filter(alert => activeFilters.includes(alert.type));
  }, [alerts, activeFilters]);
  
  // Toggle un filtre
  const handleFilterToggle = useCallback((type) => {
    setActiveFilters(prev => {
      if (prev.includes(type)) {
        return prev.filter(t => t !== type);
      }
      return [...prev, type];
    });
  }, []);
  
  // Mode compact
  if (compact) {
    return (
      <div className="space-y-2" data-testid="smart-alerts-compact">
        {/* Header compact */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
            <span className="text-xs font-medium text-[var(--bionic-text-primary)]">
              {t('alerts_title')}
            </span>
            {unreadCount > 0 && (
              <Badge className="bg-[var(--bionic-red-primary)] text-white text-[10px] h-4 min-w-[16px]">
                {unreadCount}
              </Badge>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleMute}
            className="h-6 w-6 p-0"
          >
            {isMuted ? (
              <VolumeX className="w-3 h-3 text-[var(--bionic-red-primary)]" />
            ) : (
              <Volume2 className="w-3 h-3 text-[var(--bionic-text-secondary)]" />
            )}
          </Button>
        </div>
        
        {/* Liste compacte */}
        <div className="space-y-1">
          {filteredAlerts.slice(0, 3).map(alert => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onRead={onMarkAsRead}
              compact
            />
          ))}
          {filteredAlerts.length === 0 && (
            <p className="text-xs text-[var(--bionic-text-muted)] text-center py-2">
              {t('alerts_no_alerts')}
            </p>
          )}
          {filteredAlerts.length > 3 && (
            <p className="text-[10px] text-[var(--bionic-text-muted)] text-center">
              +{filteredAlerts.length - 3} {t('alerts_more')}
            </p>
          )}
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-3" data-testid="smart-alerts">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
          <span className="text-sm font-semibold text-[var(--bionic-text-primary)]">
            {t('alerts_title')}
          </span>
          {unreadCount > 0 && (
            <Badge className="bg-[var(--bionic-red-primary)] text-white text-xs">
              {unreadCount} {t('alerts_unread')}
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {/* Mute toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleMute}
            className="h-7 w-7"
            title={isMuted ? t('alerts_unmute') : t('alerts_mute')}
          >
            {isMuted ? (
              <VolumeX className="w-4 h-4 text-[var(--bionic-red-primary)]" />
            ) : (
              <Volume2 className="w-4 h-4 text-[var(--bionic-text-secondary)]" />
            )}
          </Button>
          
          {/* Settings toggle */}
          {showSettings && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowSettingsPanel(!showSettingsPanel)}
              className="h-7 w-7"
            >
              <Settings className="w-4 h-4 text-[var(--bionic-text-secondary)]" />
            </Button>
          )}
          
          {/* Mark all as read */}
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onMarkAllAsRead}
              className="h-7 text-xs text-[var(--bionic-gold-primary)]"
            >
              <Check className="w-3 h-3 mr-1" />
              {t('alerts_mark_all_read')}
            </Button>
          )}
          
          {/* Clear all */}
          {alerts.length > 0 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClearAll}
              className="h-7 w-7 text-[var(--bionic-text-muted)] hover:text-[var(--bionic-red-primary)]"
              title={t('alerts_clear_all')}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
      
      {/* Settings panel */}
      {showSettingsPanel && (
        <Card className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]">
          <CardContent className="p-3 space-y-3">
            <p className="text-xs font-medium text-[var(--bionic-text-primary)]">
              {t('alerts_settings')}
            </p>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--bionic-text-secondary)]">
                  {t('alerts_sound_enabled')}
                </span>
                <Switch
                  checked={settings.soundEnabled}
                  onCheckedChange={(val) => onUpdateSettings?.({ soundEnabled: val })}
                  className="scale-75"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--bionic-text-secondary)]">
                  {t('alerts_vibration_enabled')}
                </span>
                <Switch
                  checked={settings.vibrationEnabled}
                  onCheckedChange={(val) => onUpdateSettings?.({ vibrationEnabled: val })}
                  className="scale-75"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--bionic-text-secondary)]">
                  {t('alerts_safety_enabled')}
                </span>
                <Switch
                  checked={settings.safetyAlertsEnabled}
                  onCheckedChange={(val) => onUpdateSettings?.({ safetyAlertsEnabled: val })}
                  className="scale-75"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--bionic-text-secondary)]">
                  {t('alerts_weather_enabled')}
                </span>
                <Switch
                  checked={settings.weatherAlertsEnabled}
                  onCheckedChange={(val) => onUpdateSettings?.({ weatherAlertsEnabled: val })}
                  className="scale-75"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Filters */}
      {showFilters && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Filter className="w-3 h-3 text-[var(--bionic-text-muted)]" />
            <span className="text-[10px] text-[var(--bionic-text-muted)]">
              {t('alerts_filter_by_type')}
            </span>
          </div>
          <AlertTypeFilter 
            activeTypes={activeFilters} 
            onToggle={handleFilterToggle} 
          />
        </div>
      )}
      
      {/* Alerts list */}
      <ScrollArea style={{ maxHeight }}>
        <div className="space-y-2 pr-2">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map(alert => (
              <AlertItem
                key={alert.id}
                alert={alert}
                onRead={onMarkAsRead}
                onDismiss={onDismiss}
                onAction={onAction}
              />
            ))
          ) : (
            <div className="text-center py-8">
              <Bell className="w-8 h-8 mx-auto mb-2 text-[var(--bionic-text-muted)] opacity-50" />
              <p className="text-sm text-[var(--bionic-text-secondary)]">
                {t('alerts_no_alerts')}
              </p>
              <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
                {t('alerts_no_alerts_desc')}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Last check indicator */}
      <div className="flex items-center justify-center gap-1 text-[10px] text-[var(--bionic-text-muted)]">
        <Clock className="w-3 h-3" />
        {t('alerts_auto_check')}
      </div>
    </div>
  );
};

export { AlertItem, AlertTypeBadge, SeverityBadge, AlertTypeFilter };
export default SmartAlerts;
