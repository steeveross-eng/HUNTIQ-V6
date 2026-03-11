/**
 * SafetyStatus - Composant de statut de sécurité pour le module GROUPE
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 4
 * 
 * Affiche le statut de sécurité actuel et les contrôles de zone de tir.
 */
import React, { useState, useCallback } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { 
  Shield, ShieldAlert, ShieldCheck, AlertTriangle, AlertCircle,
  Target, Crosshair, Navigation, RefreshCw, Settings,
  ChevronDown, ChevronUp, Eye, EyeOff, Trash2
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Card, CardContent } from '../../../components/ui/card';
import { Slider } from '../../../components/ui/slider';
import { SAFETY_STATUS, SHOOTING_ZONE_TYPES } from '../hooks/useGroupeSafety';

// Icon mapping for safety status
const STATUS_ICONS = {
  safe: ShieldCheck,
  caution: AlertCircle,
  warning: AlertTriangle,
  danger: ShieldAlert
};

/**
 * Safety status badge component
 */
const SafetyStatusBadge = ({ status, compact = false }) => {
  const { t } = useLanguage();
  const config = SAFETY_STATUS[status] || SAFETY_STATUS.safe;
  const StatusIcon = STATUS_ICONS[status] || Shield;
  
  if (compact) {
    return (
      <div 
        className="flex items-center justify-center w-8 h-8 rounded-full"
        style={{ backgroundColor: config.bgVar }}
        title={t(config.labelKey)}
      >
        <StatusIcon className="w-4 h-4" style={{ color: config.colorVar }} />
      </div>
    );
  }
  
  return (
    <Badge
      className="flex items-center gap-1.5 px-3 py-1 border-0"
      style={{ 
        backgroundColor: config.bgVar, 
        color: config.colorVar 
      }}
    >
      <StatusIcon className="w-4 h-4" />
      <span className="text-xs font-semibold uppercase">{t(config.labelKey)}</span>
    </Badge>
  );
};

/**
 * Zone type selector
 */
const ZoneTypeSelector = ({ currentType, onTypeChange, disabled = false }) => {
  const { t } = useLanguage();
  
  return (
    <div className="flex gap-1">
      {Object.values(SHOOTING_ZONE_TYPES).map(type => (
        <Button
          key={type.id}
          variant="ghost"
          size="sm"
          disabled={disabled}
          onClick={() => onTypeChange(type.id)}
          className={`
            h-7 px-2 text-xs rounded
            ${currentType === type.id 
              ? 'border' 
              : 'opacity-60 hover:opacity-100'
            }
          `}
          style={currentType === type.id ? {
            backgroundColor: `${type.colorVar}20`,
            borderColor: type.colorVar,
            color: type.colorVar
          } : {}}
        >
          {t(type.labelKey)}
        </Button>
      ))}
    </div>
  );
};

/**
 * Alert item component
 */
const AlertItem = ({ alert, memberNames = {} }) => {
  const { t } = useLanguage();
  const config = SAFETY_STATUS[alert.severity] || SAFETY_STATUS.warning;
  const AlertIcon = STATUS_ICONS[alert.severity] || AlertTriangle;
  
  const getMemberName = (memberId) => {
    return memberNames[memberId] || `Member ${memberId.slice(-4)}`;
  };
  
  const getMessage = () => {
    switch (alert.type) {
      case 'in_shooting_zone':
        return t('safety_alert_in_zone').replace('{member}', getMemberName(alert.memberId)).replace('{distance}', alert.distance);
      case 'too_close':
        return t('safety_alert_too_close').replace('{member}', getMemberName(alert.memberId)).replace('{distance}', alert.distance);
      case 'member_in_my_zone':
        return t('safety_alert_member_in_my_zone').replace('{member}', alert.memberName || getMemberName(alert.memberId)).replace('{distance}', alert.distance);
      default:
        return t('safety_alert_generic');
    }
  };
  
  return (
    <div 
      className="flex items-start gap-2 p-2 rounded-lg"
      style={{ backgroundColor: config.bgVar }}
    >
      <AlertIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: config.colorVar }} />
      <div className="flex-1 min-w-0">
        <p className="text-xs" style={{ color: config.colorVar }}>
          {getMessage()}
        </p>
      </div>
    </div>
  );
};

/**
 * Main SafetyStatus component
 */
export const SafetyStatus = ({
  safetyStatus = 'safe',
  myZone = null,
  dangerAlerts = [],
  memberNames = {},
  myPosition = null,
  onCreateZone = null,
  onUpdateZone = null,
  onClearZone = null,
  onSetZoneType = null,
  compact = false,
  showControls = true
}) => {
  const { t } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(false);
  const [showZoneSettings, setShowZoneSettings] = useState(false);
  const [zoneParams, setZoneParams] = useState({
    direction: myZone?.direction || 0,
    aperture: myZone?.aperture || 45,
    range: myZone?.range || 300
  });

  // Handle zone parameter change
  const handleParamChange = useCallback((param, value) => {
    const newParams = { ...zoneParams, [param]: value };
    setZoneParams(newParams);
    
    if (myZone && onUpdateZone) {
      onUpdateZone(newParams);
    }
  }, [zoneParams, myZone, onUpdateZone]);

  // Handle create/toggle zone
  const handleToggleZone = useCallback(() => {
    if (myZone) {
      if (onClearZone) onClearZone();
    } else if (myPosition && onCreateZone) {
      onCreateZone(myPosition, zoneParams);
    }
  }, [myZone, myPosition, onCreateZone, onClearZone, zoneParams]);

  // Compact mode
  if (compact) {
    return (
      <div className="flex items-center gap-2" data-testid="safety-status-compact">
        <SafetyStatusBadge status={safetyStatus} compact />
        {dangerAlerts.length > 0 && (
          <Badge className="bg-[var(--bionic-red-primary)] text-white text-xs h-5 min-w-[20px] flex items-center justify-center">
            {dangerAlerts.length}
          </Badge>
        )}
      </div>
    );
  }

  return (
    <Card 
      className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]"
      data-testid="safety-status"
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
            <span className="text-sm font-semibold text-[var(--bionic-text-primary)]">
              {t('safety_title')}
            </span>
          </div>
          <SafetyStatusBadge status={safetyStatus} />
        </div>

        {/* Active alerts */}
        {dangerAlerts.length > 0 && (
          <div className="space-y-2 mb-4">
            {dangerAlerts.slice(0, 3).map(alert => (
              <AlertItem 
                key={alert.id} 
                alert={alert} 
                memberNames={memberNames}
              />
            ))}
            {dangerAlerts.length > 3 && (
              <p className="text-xs text-[var(--bionic-text-muted)] text-center">
                +{dangerAlerts.length - 3} {t('safety_more_alerts')}
              </p>
            )}
          </div>
        )}

        {/* No alerts message */}
        {dangerAlerts.length === 0 && safetyStatus === 'safe' && (
          <div className="flex items-center gap-2 p-3 bg-[var(--bionic-green-muted)] rounded-lg mb-4">
            <ShieldCheck className="w-4 h-4 text-[var(--bionic-green-primary)]" />
            <span className="text-xs text-[var(--bionic-green-primary)]">
              {t('safety_all_clear')}
            </span>
          </div>
        )}

        {/* Zone controls */}
        {showControls && (
          <>
            <div className="border-t border-[var(--bionic-border-secondary)] pt-3">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center justify-between w-full text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)] transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Crosshair className="w-4 h-4" />
                  <span className="text-xs font-medium">{t('safety_my_zone')}</span>
                </div>
                <div className="flex items-center gap-2">
                  {myZone && (
                    <Badge 
                      className="text-[10px] border-0"
                      style={{ 
                        backgroundColor: SHOOTING_ZONE_TYPES[myZone.type]?.colorVar + '20',
                        color: SHOOTING_ZONE_TYPES[myZone.type]?.colorVar
                      }}
                    >
                      {t(SHOOTING_ZONE_TYPES[myZone.type]?.labelKey || 'zone_type_active')}
                    </Badge>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </button>
            </div>

            {isExpanded && (
              <div className="mt-3 space-y-3">
                {/* Toggle zone button */}
                <div className="flex items-center gap-2">
                  <Button
                    onClick={handleToggleZone}
                    disabled={!myPosition && !myZone}
                    className={`flex-1 h-9 ${
                      myZone 
                        ? 'bg-[var(--bionic-red-primary)] hover:bg-[var(--bionic-red-dark)] text-white'
                        : 'bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-dark)] text-[var(--bionic-bg-primary)]'
                    }`}
                  >
                    {myZone ? (
                      <>
                        <EyeOff className="w-4 h-4 mr-2" />
                        {t('safety_deactivate_zone')}
                      </>
                    ) : (
                      <>
                        <Target className="w-4 h-4 mr-2" />
                        {t('safety_activate_zone')}
                      </>
                    )}
                  </Button>
                  
                  {myZone && (
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => setShowZoneSettings(!showZoneSettings)}
                      className="h-9 w-9 border-[var(--bionic-border-secondary)]"
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Zone type selector */}
                {myZone && (
                  <div>
                    <p className="text-[10px] text-[var(--bionic-text-muted)] uppercase mb-1.5">
                      {t('safety_zone_type')}
                    </p>
                    <ZoneTypeSelector
                      currentType={myZone.type}
                      onTypeChange={(type) => onSetZoneType?.(type)}
                    />
                  </div>
                )}

                {/* Zone settings */}
                {(myZone || showZoneSettings) && showZoneSettings && (
                  <div className="space-y-4 p-3 bg-[var(--bionic-bg-hover)] rounded-lg">
                    {/* Direction */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[var(--bionic-text-secondary)]">
                          {t('safety_direction')}
                        </span>
                        <span className="text-xs font-medium text-[var(--bionic-gold-primary)]">
                          {zoneParams.direction}°
                        </span>
                      </div>
                      <Slider
                        value={[zoneParams.direction]}
                        onValueChange={([val]) => handleParamChange('direction', val)}
                        min={0}
                        max={359}
                        step={5}
                        className="w-full"
                      />
                      <div className="flex justify-between text-[10px] text-[var(--bionic-text-muted)] mt-1">
                        <span>N</span>
                        <span>E</span>
                        <span>S</span>
                        <span>W</span>
                      </div>
                    </div>

                    {/* Aperture */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[var(--bionic-text-secondary)]">
                          {t('safety_aperture')}
                        </span>
                        <span className="text-xs font-medium text-[var(--bionic-gold-primary)]">
                          {zoneParams.aperture}°
                        </span>
                      </div>
                      <Slider
                        value={[zoneParams.aperture]}
                        onValueChange={([val]) => handleParamChange('aperture', val)}
                        min={15}
                        max={120}
                        step={5}
                        className="w-full"
                      />
                    </div>

                    {/* Range */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[var(--bionic-text-secondary)]">
                          {t('safety_range')}
                        </span>
                        <span className="text-xs font-medium text-[var(--bionic-gold-primary)]">
                          {zoneParams.range}m
                        </span>
                      </div>
                      <Slider
                        value={[zoneParams.range]}
                        onValueChange={([val]) => handleParamChange('range', val)}
                        min={50}
                        max={500}
                        step={25}
                        className="w-full"
                      />
                    </div>
                  </div>
                )}

                {/* Help text */}
                {!myPosition && !myZone && (
                  <p className="text-[10px] text-[var(--bionic-text-muted)] text-center">
                    {t('safety_position_required')}
                  </p>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export { SafetyStatusBadge, ZoneTypeSelector, AlertItem };
export default SafetyStatus;
