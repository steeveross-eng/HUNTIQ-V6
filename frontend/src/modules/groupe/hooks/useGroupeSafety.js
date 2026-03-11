/**
 * useGroupeSafety - Hook pour la gestion de la sécurité du groupe
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 4
 * 
 * Gère les zones de tir, les périmètres de sécurité et les alertes de danger.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';

// Safety status configuration with BIONIC colors
export const SAFETY_STATUS = {
  safe: {
    id: 'safe',
    labelKey: 'safety_status_safe',
    colorVar: 'var(--bionic-green-primary)',
    bgVar: 'var(--bionic-green-muted)',
    icon: 'Shield',
    priority: 0
  },
  caution: {
    id: 'caution',
    labelKey: 'safety_status_caution',
    colorVar: 'var(--bionic-gold-primary)',
    bgVar: 'var(--bionic-gold-muted)',
    icon: 'AlertCircle',
    priority: 1
  },
  warning: {
    id: 'warning',
    labelKey: 'safety_status_warning',
    colorVar: 'var(--bionic-orange-primary)',
    bgVar: 'var(--bionic-orange-muted)',
    icon: 'AlertTriangle',
    priority: 2
  },
  danger: {
    id: 'danger',
    labelKey: 'safety_status_danger',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)',
    icon: 'ShieldAlert',
    priority: 3
  }
};

// Shooting zone types
export const SHOOTING_ZONE_TYPES = {
  active: {
    id: 'active',
    labelKey: 'zone_type_active',
    colorVar: 'var(--bionic-red-primary)',
    fillOpacity: 0.3,
    strokeWidth: 2
  },
  standby: {
    id: 'standby',
    labelKey: 'zone_type_standby',
    colorVar: 'var(--bionic-gold-primary)',
    fillOpacity: 0.2,
    strokeWidth: 1.5
  },
  safe: {
    id: 'safe',
    labelKey: 'zone_type_safe',
    colorVar: 'var(--bionic-green-primary)',
    fillOpacity: 0.15,
    strokeWidth: 1
  }
};

// Default shooting zone parameters
const DEFAULT_ZONE_PARAMS = {
  direction: 0,      // Direction in degrees (0-360)
  aperture: 45,      // Cone aperture in degrees
  range: 300,        // Range in meters
  minSafeDistance: 100 // Minimum safe distance in meters
};

/**
 * Calculate if a point is inside a shooting zone (cone)
 */
const isPointInShootingZone = (point, zone) => {
  if (!point || !zone || !zone.center) return false;
  
  const { lat: pLat, lng: pLng } = point;
  const { lat: cLat, lng: cLng } = zone.center;
  
  // Calculate distance using Haversine formula
  const R = 6371000; // Earth radius in meters
  const dLat = (pLat - cLat) * Math.PI / 180;
  const dLng = (pLng - cLng) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(cLat * Math.PI / 180) * Math.cos(pLat * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c;
  
  // Check if within range
  if (distance > zone.range) return false;
  
  // Calculate bearing from zone center to point
  const y = Math.sin((pLng - cLng) * Math.PI / 180) * Math.cos(pLat * Math.PI / 180);
  const x = Math.cos(cLat * Math.PI / 180) * Math.sin(pLat * Math.PI / 180) -
            Math.sin(cLat * Math.PI / 180) * Math.cos(pLat * Math.PI / 180) * Math.cos((pLng - cLng) * Math.PI / 180);
  let bearing = Math.atan2(y, x) * 180 / Math.PI;
  bearing = (bearing + 360) % 360;
  
  // Check if within cone aperture
  const halfAperture = zone.aperture / 2;
  let angleDiff = Math.abs(bearing - zone.direction);
  if (angleDiff > 180) angleDiff = 360 - angleDiff;
  
  return angleDiff <= halfAperture;
};

/**
 * Calculate distance between two points
 */
const calculateDistance = (point1, point2) => {
  if (!point1 || !point2) return Infinity;
  
  const R = 6371000; // Earth radius in meters
  const dLat = (point2.lat - point1.lat) * Math.PI / 180;
  const dLng = (point2.lng - point1.lng) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return R * c;
};

export const useGroupeSafety = (userId, groupId, options = {}) => {
  const {
    members = [],
    onDangerAlert = null,
    onSafetyChange = null,
    checkInterval = 5000
  } = options;

  // State
  const [shootingZones, setShootingZones] = useState([]);
  const [myZone, setMyZone] = useState(null);
  const [safetyStatus, setSafetyStatus] = useState(SAFETY_STATUS.safe);
  const [dangerAlerts, setDangerAlerts] = useState([]);
  const [memberDistances, setMemberDistances] = useState({});

  // Create a shooting zone for a member
  const createShootingZone = useCallback((memberId, position, params = {}) => {
    const zoneParams = { ...DEFAULT_ZONE_PARAMS, ...params };
    
    const newZone = {
      id: `zone_${memberId}_${Date.now()}`,
      memberId,
      center: position,
      direction: zoneParams.direction,
      aperture: zoneParams.aperture,
      range: zoneParams.range,
      minSafeDistance: zoneParams.minSafeDistance,
      type: 'active',
      createdAt: new Date().toISOString()
    };
    
    setShootingZones(prev => {
      // Remove existing zone for this member
      const filtered = prev.filter(z => z.memberId !== memberId);
      return [...filtered, newZone];
    });
    
    if (memberId === userId) {
      setMyZone(newZone);
    }
    
    return newZone;
  }, [userId]);

  // Update my shooting zone
  const updateMyZone = useCallback((params) => {
    if (!myZone) return;
    
    const updatedZone = {
      ...myZone,
      ...params,
      updatedAt: new Date().toISOString()
    };
    
    setMyZone(updatedZone);
    setShootingZones(prev => 
      prev.map(z => z.memberId === userId ? updatedZone : z)
    );
    
    return updatedZone;
  }, [myZone, userId]);

  // Remove a shooting zone
  const removeShootingZone = useCallback((memberId) => {
    setShootingZones(prev => prev.filter(z => z.memberId !== memberId));
    
    if (memberId === userId) {
      setMyZone(null);
    }
  }, [userId]);

  // Clear my zone
  const clearMyZone = useCallback(() => {
    removeShootingZone(userId);
  }, [removeShootingZone, userId]);

  // Set zone type (active, standby, safe)
  const setZoneType = useCallback((memberId, type) => {
    if (!SHOOTING_ZONE_TYPES[type]) return;
    
    setShootingZones(prev => 
      prev.map(z => z.memberId === memberId ? { ...z, type } : z)
    );
    
    if (memberId === userId && myZone) {
      setMyZone({ ...myZone, type });
    }
  }, [userId, myZone]);

  // Check safety for all members
  const checkSafety = useCallback(() => {
    const alerts = [];
    const distances = {};
    let worstStatus = SAFETY_STATUS.safe;
    
    // Get my position
    const myMember = members.find(m => m.id === userId);
    const myPosition = myMember?.position;
    
    if (!myPosition) {
      setSafetyStatus(SAFETY_STATUS.safe);
      setDangerAlerts([]);
      return;
    }
    
    // Check against all shooting zones (except my own)
    shootingZones.forEach(zone => {
      if (zone.memberId === userId) return;
      if (zone.type === 'safe') return; // Safe zones don't trigger alerts
      
      const isInZone = isPointInShootingZone(myPosition, zone);
      const distance = calculateDistance(myPosition, zone.center);
      
      distances[zone.memberId] = distance;
      
      if (isInZone) {
        const alert = {
          id: `alert_${zone.id}_${Date.now()}`,
          type: 'in_shooting_zone',
          memberId: zone.memberId,
          zoneId: zone.id,
          distance: Math.round(distance),
          severity: zone.type === 'active' ? 'danger' : 'warning',
          timestamp: new Date().toISOString()
        };
        alerts.push(alert);
        
        if (zone.type === 'active') {
          worstStatus = SAFETY_STATUS.danger;
        } else if (worstStatus.priority < SAFETY_STATUS.warning.priority) {
          worstStatus = SAFETY_STATUS.warning;
        }
      } else if (distance < zone.minSafeDistance) {
        const alert = {
          id: `alert_proximity_${zone.memberId}_${Date.now()}`,
          type: 'too_close',
          memberId: zone.memberId,
          distance: Math.round(distance),
          minSafe: zone.minSafeDistance,
          severity: 'caution',
          timestamp: new Date().toISOString()
        };
        alerts.push(alert);
        
        if (worstStatus.priority < SAFETY_STATUS.caution.priority) {
          worstStatus = SAFETY_STATUS.caution;
        }
      }
    });
    
    // Check if any member is in MY zone
    if (myZone && myZone.type !== 'safe') {
      members.forEach(member => {
        if (member.id === userId) return;
        if (!member.position) return;
        
        const isInMyZone = isPointInShootingZone(member.position, myZone);
        const distance = calculateDistance(myPosition, member.position);
        
        distances[member.id] = distance;
        
        if (isInMyZone) {
          const alert = {
            id: `alert_member_in_my_zone_${member.id}_${Date.now()}`,
            type: 'member_in_my_zone',
            memberId: member.id,
            memberName: member.name,
            distance: Math.round(distance),
            severity: myZone.type === 'active' ? 'danger' : 'warning',
            timestamp: new Date().toISOString()
          };
          alerts.push(alert);
          
          if (myZone.type === 'active') {
            worstStatus = SAFETY_STATUS.danger;
          } else if (worstStatus.priority < SAFETY_STATUS.warning.priority) {
            worstStatus = SAFETY_STATUS.warning;
          }
        }
      });
    }
    
    // Update state
    setMemberDistances(distances);
    setDangerAlerts(alerts);
    
    if (worstStatus.id !== safetyStatus.id) {
      setSafetyStatus(worstStatus);
      if (onSafetyChange) {
        onSafetyChange(worstStatus);
      }
    }
    
    // Trigger danger alert callback for new critical alerts
    if (alerts.length > 0 && onDangerAlert) {
      const criticalAlerts = alerts.filter(a => a.severity === 'danger');
      if (criticalAlerts.length > 0) {
        onDangerAlert(criticalAlerts);
      }
    }
    
    return { status: worstStatus, alerts, distances };
  }, [members, userId, shootingZones, myZone, safetyStatus, onDangerAlert, onSafetyChange]);

  // Compute active zones with member info
  const activeZonesWithInfo = useMemo(() => {
    return shootingZones.map(zone => {
      const member = members.find(m => m.id === zone.memberId);
      return {
        ...zone,
        memberName: member?.name || 'Unknown',
        memberStatus: member?.status || 'unknown'
      };
    });
  }, [shootingZones, members]);

  // Get zone for a specific member
  const getMemberZone = useCallback((memberId) => {
    return shootingZones.find(z => z.memberId === memberId) || null;
  }, [shootingZones]);

  // Get all danger zones (active type)
  const dangerZones = useMemo(() => {
    return shootingZones.filter(z => z.type === 'active');
  }, [shootingZones]);

  // Auto-check safety periodically
  useEffect(() => {
    if (members.length === 0) return;
    
    const interval = setInterval(checkSafety, checkInterval);
    checkSafety(); // Initial check
    
    return () => clearInterval(interval);
  }, [checkSafety, checkInterval, members.length]);

  return {
    // State
    shootingZones,
    myZone,
    safetyStatus,
    dangerAlerts,
    memberDistances,
    
    // Computed
    activeZonesWithInfo,
    dangerZones,
    
    // Actions
    createShootingZone,
    updateMyZone,
    removeShootingZone,
    clearMyZone,
    setZoneType,
    checkSafety,
    getMemberZone,
    
    // Config
    SAFETY_STATUS,
    SHOOTING_ZONE_TYPES,
    DEFAULT_ZONE_PARAMS
  };
};

export default useGroupeSafety;
