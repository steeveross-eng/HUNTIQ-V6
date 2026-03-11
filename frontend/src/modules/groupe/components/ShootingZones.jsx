/**
 * ShootingZones - Composant d'affichage des zones de tir sur la carte
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 4
 * 
 * Affiche les zones de tir (cônes) sur une carte Leaflet.
 */
import React, { useMemo, useCallback } from 'react';
import { Polygon, Circle, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useLanguage } from '../../../contexts/LanguageContext';
import { SHOOTING_ZONE_TYPES, SAFETY_STATUS } from '../hooks/useGroupeSafety';
import { Target, Crosshair, AlertTriangle, User } from 'lucide-react';

/**
 * Calculate cone polygon points from center, direction, aperture, and range
 */
const calculateConePoints = (center, direction, aperture, range, numPoints = 20) => {
  if (!center || !center.lat || !center.lng) return [];
  
  const points = [];
  const halfAperture = aperture / 2;
  const startAngle = direction - halfAperture;
  const endAngle = direction + halfAperture;
  
  // Center point
  points.push([center.lat, center.lng]);
  
  // Arc points
  for (let i = 0; i <= numPoints; i++) {
    const angle = startAngle + (endAngle - startAngle) * (i / numPoints);
    const radians = angle * Math.PI / 180;
    
    // Calculate destination point (simplified for small distances)
    // Using approximate conversion: 1 degree latitude ≈ 111km
    const latOffset = (range / 111000) * Math.cos(radians);
    const lngOffset = (range / (111000 * Math.cos(center.lat * Math.PI / 180))) * Math.sin(radians);
    
    points.push([center.lat + latOffset, center.lng + lngOffset]);
  }
  
  // Close the cone
  points.push([center.lat, center.lng]);
  
  return points;
};

/**
 * Get color values from CSS variable name (fallback to hex)
 */
const getZoneColors = (zoneType) => {
  const config = SHOOTING_ZONE_TYPES[zoneType] || SHOOTING_ZONE_TYPES.active;
  
  // Map CSS variables to hex colors for Leaflet
  const colorMap = {
    'var(--bionic-red-primary)': '#ef4444',
    'var(--bionic-gold-primary)': '#f5a623',
    'var(--bionic-green-primary)': '#10b981'
  };
  
  const color = colorMap[config.colorVar] || '#ef4444';
  
  return {
    color,
    fillColor: color,
    fillOpacity: config.fillOpacity,
    weight: config.strokeWidth
  };
};

/**
 * Single shooting zone component
 */
const ShootingZone = ({ 
  zone, 
  isOwn = false, 
  memberName = 'Unknown',
  onZoneClick = null,
  showLabel = true
}) => {
  const { t } = useLanguage();
  
  // Calculate cone polygon points
  const conePoints = useMemo(() => {
    return calculateConePoints(
      zone.center,
      zone.direction,
      zone.aperture,
      zone.range
    );
  }, [zone.center, zone.direction, zone.aperture, zone.range]);
  
  // Get zone style
  const zoneStyle = useMemo(() => {
    const colors = getZoneColors(zone.type);
    return {
      ...colors,
      dashArray: isOwn ? null : '5, 10'
    };
  }, [zone.type, isOwn]);
  
  // Direction line (center to edge of cone)
  const directionLine = useMemo(() => {
    if (!zone.center) return null;
    
    const radians = zone.direction * Math.PI / 180;
    const latOffset = (zone.range / 111000) * Math.cos(radians);
    const lngOffset = (zone.range / (111000 * Math.cos(zone.center.lat * Math.PI / 180))) * Math.sin(radians);
    
    return [
      [zone.center.lat, zone.center.lng],
      [zone.center.lat + latOffset, zone.center.lng + lngOffset]
    ];
  }, [zone.center, zone.direction, zone.range]);
  
  // Handle click on zone
  const handleClick = useCallback(() => {
    if (onZoneClick) {
      onZoneClick(zone);
    }
  }, [zone, onZoneClick]);
  
  if (conePoints.length === 0) return null;
  
  return (
    <>
      {/* Cone polygon */}
      <Polygon
        positions={conePoints}
        pathOptions={zoneStyle}
        eventHandlers={{ click: handleClick }}
      >
        <Popup className="bionic-popup">
          <div className="min-w-[160px] p-2">
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-gray-700">
              {isOwn ? (
                <Target className="w-5 h-5 text-[var(--bionic-gold-primary)]" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-[var(--bionic-red-primary)]" />
              )}
              <div>
                <p className="text-white font-semibold text-sm">
                  {isOwn ? t('safety_my_zone') : t('safety_danger_zone')}
                </p>
                {!isOwn && (
                  <p className="text-gray-400 text-xs">
                    {memberName}
                  </p>
                )}
              </div>
            </div>
            <div className="space-y-1 text-xs text-gray-300">
              <div className="flex justify-between">
                <span>{t('safety_direction')}:</span>
                <span className="text-[var(--bionic-gold-primary)]">{zone.direction}°</span>
              </div>
              <div className="flex justify-between">
                <span>{t('safety_aperture')}:</span>
                <span className="text-[var(--bionic-gold-primary)]">{zone.aperture}°</span>
              </div>
              <div className="flex justify-between">
                <span>{t('safety_range')}:</span>
                <span className="text-[var(--bionic-gold-primary)]">{zone.range}m</span>
              </div>
              <div className="flex justify-between">
                <span>{t('safety_zone_type')}:</span>
                <span style={{ color: getZoneColors(zone.type).color }}>
                  {t(SHOOTING_ZONE_TYPES[zone.type]?.labelKey || 'zone_type_active')}
                </span>
              </div>
            </div>
          </div>
        </Popup>
      </Polygon>
      
      {/* Direction indicator line */}
      {directionLine && (
        <Polyline
          positions={directionLine}
          pathOptions={{
            color: zoneStyle.color,
            weight: 2,
            dashArray: '5, 5',
            opacity: 0.8
          }}
        />
      )}
      
      {/* Center point */}
      <Circle
        center={[zone.center.lat, zone.center.lng]}
        radius={5}
        pathOptions={{
          color: zoneStyle.color,
          fillColor: zoneStyle.color,
          fillOpacity: 1,
          weight: 2
        }}
      />
      
      {/* Min safe distance circle */}
      {zone.minSafeDistance && zone.type === 'active' && (
        <Circle
          center={[zone.center.lat, zone.center.lng]}
          radius={zone.minSafeDistance}
          pathOptions={{
            color: '#f5a623',
            fillColor: '#f5a623',
            fillOpacity: 0.1,
            weight: 1,
            dashArray: '3, 6'
          }}
        />
      )}
    </>
  );
};

/**
 * Danger indicator marker for members in zones
 */
const DangerIndicator = ({ position, severity = 'danger', distance }) => {
  if (!position || !position.lat || !position.lng) return null;
  
  const config = SAFETY_STATUS[severity] || SAFETY_STATUS.danger;
  const colorMap = {
    'var(--bionic-red-primary)': '#ef4444',
    'var(--bionic-gold-primary)': '#f5a623',
    'var(--bionic-green-primary)': '#10b981',
    'var(--bionic-orange-primary)': '#f97316'
  };
  const color = colorMap[config.colorVar] || '#ef4444';
  
  return (
    <>
      {/* Pulsing danger circle */}
      <Circle
        center={[position.lat, position.lng]}
        radius={20}
        pathOptions={{
          color: color,
          fillColor: color,
          fillOpacity: 0.4,
          weight: 2
        }}
      />
      <Circle
        center={[position.lat, position.lng]}
        radius={40}
        pathOptions={{
          color: color,
          fillColor: 'transparent',
          fillOpacity: 0,
          weight: 1,
          dashArray: '5, 5'
        }}
      />
    </>
  );
};

/**
 * Main ShootingZones component
 */
export const ShootingZones = ({
  zones = [],
  currentUserId = null,
  dangerAlerts = [],
  members = [],
  onZoneClick = null,
  showOwnZone = true,
  showOtherZones = true,
  showDangerIndicators = true
}) => {
  const { t } = useLanguage();
  
  // Filter zones based on settings
  const displayZones = useMemo(() => {
    return zones.filter(zone => {
      if (zone.memberId === currentUserId) {
        return showOwnZone;
      }
      return showOtherZones;
    });
  }, [zones, currentUserId, showOwnZone, showOtherZones]);
  
  // Get member name by ID
  const getMemberName = useCallback((memberId) => {
    const member = members.find(m => m.id === memberId);
    return member?.name || `Member ${memberId?.slice(-4) || '????'}`;
  }, [members]);
  
  // Get positions for danger indicators
  const dangerPositions = useMemo(() => {
    if (!showDangerIndicators) return [];
    
    return dangerAlerts
      .filter(alert => alert.type === 'in_shooting_zone' || alert.type === 'member_in_my_zone')
      .map(alert => {
        const member = members.find(m => m.id === alert.memberId);
        return {
          ...alert,
          position: member?.position
        };
      })
      .filter(alert => alert.position);
  }, [dangerAlerts, members, showDangerIndicators]);
  
  return (
    <>
      {/* Render all shooting zones */}
      {displayZones.map(zone => (
        <ShootingZone
          key={zone.id}
          zone={zone}
          isOwn={zone.memberId === currentUserId}
          memberName={getMemberName(zone.memberId)}
          onZoneClick={onZoneClick}
        />
      ))}
      
      {/* Render danger indicators */}
      {dangerPositions.map(alert => (
        <DangerIndicator
          key={alert.id}
          position={alert.position}
          severity={alert.severity}
          distance={alert.distance}
        />
      ))}
    </>
  );
};

export { ShootingZone, DangerIndicator, calculateConePoints, getZoneColors };
export default ShootingZones;
