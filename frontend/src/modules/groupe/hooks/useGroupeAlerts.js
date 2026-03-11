/**
 * useGroupeAlerts - Hook pour la gestion des alertes intelligentes du groupe
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 5
 * 
 * Gère les alertes de sécurité, proximité, météo et activité pour le groupe de chasse.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';

// Types d'alertes disponibles
export const ALERT_TYPES = {
  safety: {
    id: 'safety',
    labelKey: 'alert_type_safety',
    iconName: 'ShieldAlert',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)',
    priority: 1,
    sound: true,
    vibrate: true
  },
  proximity: {
    id: 'proximity',
    labelKey: 'alert_type_proximity',
    iconName: 'Users',
    colorVar: 'var(--bionic-orange-primary)',
    bgVar: 'var(--bionic-orange-muted)',
    priority: 2,
    sound: true,
    vibrate: true
  },
  weather: {
    id: 'weather',
    labelKey: 'alert_type_weather',
    iconName: 'CloudRain',
    colorVar: 'var(--bionic-blue-primary)',
    bgVar: 'var(--bionic-blue-muted)',
    priority: 3,
    sound: false,
    vibrate: false
  },
  activity: {
    id: 'activity',
    labelKey: 'alert_type_activity',
    iconName: 'Activity',
    colorVar: 'var(--bionic-gold-primary)',
    bgVar: 'var(--bionic-gold-muted)',
    priority: 4,
    sound: false,
    vibrate: false
  },
  game: {
    id: 'game',
    labelKey: 'alert_type_game',
    iconName: 'Target',
    colorVar: 'var(--bionic-green-primary)',
    bgVar: 'var(--bionic-green-muted)',
    priority: 2,
    sound: true,
    vibrate: true
  },
  zone: {
    id: 'zone',
    labelKey: 'alert_type_zone',
    iconName: 'MapPin',
    colorVar: 'var(--bionic-purple-primary)',
    bgVar: 'var(--bionic-purple-muted)',
    priority: 3,
    sound: false,
    vibrate: false
  }
};

// Niveaux de sévérité
export const ALERT_SEVERITY = {
  critical: {
    id: 'critical',
    labelKey: 'alert_severity_critical',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)',
    priority: 1
  },
  warning: {
    id: 'warning',
    labelKey: 'alert_severity_warning',
    colorVar: 'var(--bionic-orange-primary)',
    bgVar: 'var(--bionic-orange-muted)',
    priority: 2
  },
  info: {
    id: 'info',
    labelKey: 'alert_severity_info',
    colorVar: 'var(--bionic-gold-primary)',
    bgVar: 'var(--bionic-gold-muted)',
    priority: 3
  },
  success: {
    id: 'success',
    labelKey: 'alert_severity_success',
    colorVar: 'var(--bionic-green-primary)',
    bgVar: 'var(--bionic-green-muted)',
    priority: 4
  }
};

// Configuration des alertes par défaut
const DEFAULT_ALERT_SETTINGS = {
  soundEnabled: true,
  vibrationEnabled: true,
  proximityThreshold: 200, // mètres
  safetyAlertsEnabled: true,
  weatherAlertsEnabled: true,
  activityAlertsEnabled: true,
  gameAlertsEnabled: true,
  zoneAlertsEnabled: true
};

/**
 * Génère un ID unique pour une alerte
 */
const generateAlertId = () => {
  return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Hook principal pour la gestion des alertes intelligentes
 */
export const useGroupeAlerts = (userId, groupId, options = {}) => {
  const {
    members = [],
    shootingZones = [],
    myPosition = null,
    weatherData = null,
    onAlertReceived = null,
    checkInterval = 10000
  } = options;

  // State
  const [alerts, setAlerts] = useState([]);
  const [settings, setSettings] = useState(DEFAULT_ALERT_SETTINGS);
  const [isMuted, setIsMuted] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);

  // Calculer unreadCount à partir des alertes
  const unreadCount = useMemo(() => {
    return alerts.filter(a => !a.read && !a.dismissed).length;
  }, [alerts]);

  // Ajouter une nouvelle alerte
  const addAlert = useCallback((alertData) => {
    const newAlert = {
      id: generateAlertId(),
      type: alertData.type || 'activity',
      severity: alertData.severity || 'info',
      title: alertData.title,
      message: alertData.message,
      data: alertData.data || {},
      memberId: alertData.memberId || null,
      memberName: alertData.memberName || null,
      location: alertData.location || null,
      timestamp: new Date().toISOString(),
      read: false,
      dismissed: false,
      actionable: alertData.actionable || false,
      actions: alertData.actions || []
    };

    setAlerts(prev => [newAlert, ...prev]);

    // Jouer le son si activé
    const alertConfig = ALERT_TYPES[newAlert.type];
    if (alertConfig?.sound && settings.soundEnabled && !isMuted) {
      playAlertSound(newAlert.severity);
    }

    // Vibrer si activé
    if (alertConfig?.vibrate && settings.vibrationEnabled && !isMuted) {
      triggerVibration(newAlert.severity);
    }

    // Callback externe
    if (onAlertReceived) {
      onAlertReceived(newAlert);
    }

    return newAlert;
  }, [settings, isMuted, onAlertReceived]);

  // Jouer un son d'alerte
  const playAlertSound = useCallback((severity) => {
    try {
      // Utiliser l'API Web Audio ou un fichier audio simple
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Fréquence basée sur la sévérité
      const frequencies = {
        critical: 880,
        warning: 660,
        info: 440,
        success: 520
      };
      
      oscillator.frequency.value = frequencies[severity] || 440;
      oscillator.type = 'sine';
      gainNode.gain.value = 0.1;
      
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15);
    } catch (e) {
      console.log('[useGroupeAlerts] Audio not supported');
    }
  }, []);

  // Déclencher une vibration
  const triggerVibration = useCallback((severity) => {
    if ('vibrate' in navigator) {
      const patterns = {
        critical: [200, 100, 200, 100, 200],
        warning: [150, 100, 150],
        info: [100],
        success: [50, 50, 50]
      };
      navigator.vibrate(patterns[severity] || [100]);
    }
  }, []);

  // Marquer une alerte comme lue
  const markAsRead = useCallback((alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, read: true } : alert
    ));
  }, []);

  // Marquer toutes les alertes comme lues
  const markAllAsRead = useCallback(() => {
    setAlerts(prev => prev.map(alert => ({ ...alert, read: true })));
  }, []);

  // Rejeter une alerte
  const dismissAlert = useCallback((alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, dismissed: true } : alert
    ));
  }, []);

  // Supprimer une alerte
  const removeAlert = useCallback((alertId) => {
    setAlerts(prev => prev.filter(a => a.id !== alertId));
  }, []);

  // Effacer toutes les alertes
  const clearAllAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  // Basculer le mode muet
  const toggleMute = useCallback(() => {
    setIsMuted(prev => !prev);
  }, []);

  // Mettre à jour les paramètres
  const updateSettings = useCallback((newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  // Vérifier les alertes de proximité
  const checkProximityAlerts = useCallback(() => {
    if (!myPosition || !settings.safetyAlertsEnabled) return;

    members.forEach(member => {
      if (member.id === userId || !member.position) return;

      const distance = calculateDistance(myPosition, member.position);
      
      if (distance < settings.proximityThreshold) {
        // Vérifier si une alerte similaire existe déjà récemment
        setAlerts(prevAlerts => {
          const recentSimilar = prevAlerts.find(a => 
            a.type === 'proximity' && 
            a.memberId === member.id &&
            (Date.now() - new Date(a.timestamp).getTime()) < 60000
          );

          if (!recentSimilar) {
            const newAlert = {
              id: generateAlertId(),
              type: 'proximity',
              severity: distance < 50 ? 'critical' : 'warning',
              title: 'alert_proximity_title',
              message: 'alert_proximity_message',
              memberId: member.id,
              memberName: member.name,
              data: { distance: Math.round(distance) },
              location: member.position,
              timestamp: new Date().toISOString(),
              read: false,
              dismissed: false,
              actionable: true,
              actions: ['view_on_map', 'send_message']
            };
            return [newAlert, ...prevAlerts];
          }
          return prevAlerts;
        });
      }
    });
  }, [myPosition, members, userId, settings.safetyAlertsEnabled, settings.proximityThreshold]);

  // Vérifier les alertes de zones de tir
  const checkShootingZoneAlerts = useCallback(() => {
    if (!myPosition || !settings.safetyAlertsEnabled) return;

    shootingZones.forEach(zone => {
      if (zone.memberId === userId) return;
      if (zone.type === 'safe') return;

      const isInZone = isPointInShootingZone(myPosition, zone);
      
      if (isInZone) {
        setAlerts(prevAlerts => {
          const recentSimilar = prevAlerts.find(a => 
            a.type === 'safety' && 
            a.data?.zoneId === zone.id &&
            (Date.now() - new Date(a.timestamp).getTime()) < 30000
          );

          if (!recentSimilar) {
            const newAlert = {
              id: generateAlertId(),
              type: 'safety',
              severity: zone.type === 'active' ? 'critical' : 'warning',
              title: 'alert_shooting_zone_title',
              message: 'alert_shooting_zone_message',
              memberId: zone.memberId,
              data: { zoneId: zone.id, zoneType: zone.type },
              location: zone.center,
              timestamp: new Date().toISOString(),
              read: false,
              dismissed: false,
              actionable: true,
              actions: ['view_on_map', 'contact_member']
            };
            return [newAlert, ...prevAlerts];
          }
          return prevAlerts;
        });
      }
    });
  }, [myPosition, shootingZones, userId, settings.safetyAlertsEnabled]);

  // Vérifier les alertes météo
  const checkWeatherAlerts = useCallback(() => {
    if (!weatherData || !settings.weatherAlertsEnabled) return;

    // Alerte pluie imminente
    if (weatherData.precipitationProbability > 70) {
      setAlerts(prevAlerts => {
        const recentSimilar = prevAlerts.find(a => 
          a.type === 'weather' && 
          a.data?.condition === 'rain' &&
          (Date.now() - new Date(a.timestamp).getTime()) < 1800000 // 30 min
        );

        if (!recentSimilar) {
          const newAlert = {
            id: generateAlertId(),
            type: 'weather',
            severity: 'info',
            title: 'alert_weather_rain_title',
            message: 'alert_weather_rain_message',
            data: { 
              condition: 'rain',
              probability: weatherData.precipitationProbability 
            },
            timestamp: new Date().toISOString(),
            read: false,
            dismissed: false,
            actionable: false,
            actions: []
          };
          return [newAlert, ...prevAlerts];
        }
        return prevAlerts;
      });
    }

    // Alerte vent fort
    if (weatherData.windSpeed > 30) {
      setAlerts(prevAlerts => {
        const recentSimilar = prevAlerts.find(a => 
          a.type === 'weather' && 
          a.data?.condition === 'wind' &&
          (Date.now() - new Date(a.timestamp).getTime()) < 1800000
        );

        if (!recentSimilar) {
          const newAlert = {
            id: generateAlertId(),
            type: 'weather',
            severity: 'warning',
            title: 'alert_weather_wind_title',
            message: 'alert_weather_wind_message',
            data: { 
              condition: 'wind',
              windSpeed: weatherData.windSpeed 
            },
            timestamp: new Date().toISOString(),
            read: false,
            dismissed: false,
            actionable: false,
            actions: []
          };
          return [newAlert, ...prevAlerts];
        }
        return prevAlerts;
      });
    }
  }, [weatherData, settings.weatherAlertsEnabled]);

  // Créer une alerte de gibier repéré
  const createGameAlert = useCallback((gameData) => {
    if (!settings.gameAlertsEnabled) return null;

    return addAlert({
      type: 'game',
      severity: 'success',
      title: 'alert_game_spotted_title',
      message: 'alert_game_spotted_message',
      data: gameData,
      location: gameData.location,
      actionable: true,
      actions: ['view_on_map', 'share_location']
    });
  }, [settings, addAlert]);

  // Créer une alerte d'activité de membre
  const createActivityAlert = useCallback((activityData) => {
    if (!settings.activityAlertsEnabled) return null;

    return addAlert({
      type: 'activity',
      severity: 'info',
      title: activityData.title || 'alert_activity_title',
      message: activityData.message || 'alert_activity_message',
      memberId: activityData.memberId,
      memberName: activityData.memberName,
      data: activityData.data,
      location: activityData.location
    });
  }, [settings, addAlert]);

  // Créer une alerte de zone
  const createZoneAlert = useCallback((zoneData) => {
    if (!settings.zoneAlertsEnabled) return null;

    return addAlert({
      type: 'zone',
      severity: 'info',
      title: zoneData.title || 'alert_zone_title',
      message: zoneData.message || 'alert_zone_message',
      data: zoneData,
      location: zoneData.location
    });
  }, [settings, addAlert]);

  // Alertes filtrées par type
  const alertsByType = useMemo(() => {
    const grouped = {};
    Object.keys(ALERT_TYPES).forEach(type => {
      grouped[type] = alerts.filter(a => a.type === type && !a.dismissed);
    });
    return grouped;
  }, [alerts]);

  // Alertes non lues
  const unreadAlerts = useMemo(() => {
    return alerts.filter(a => !a.read && !a.dismissed);
  }, [alerts]);

  // Alertes critiques non lues
  const criticalAlerts = useMemo(() => {
    return alerts.filter(a => 
      a.severity === 'critical' && 
      !a.read && 
      !a.dismissed
    );
  }, [alerts]);

  // Alertes visibles (non rejetées)
  const visibleAlerts = useMemo(() => {
    return alerts
      .filter(a => !a.dismissed)
      .sort((a, b) => {
        // Trier par priorité puis par date
        const priorityA = ALERT_SEVERITY[a.severity]?.priority || 99;
        const priorityB = ALERT_SEVERITY[b.severity]?.priority || 99;
        if (priorityA !== priorityB) return priorityA - priorityB;
        return new Date(b.timestamp) - new Date(a.timestamp);
      });
  }, [alerts]);

  // Manual check function for alerts (to be called by parent when needed)
  const runAlertChecks = useCallback(() => {
    checkProximityAlerts();
    checkShootingZoneAlerts();
    checkWeatherAlerts();
    setLastCheck(new Date().toISOString());
  }, [checkProximityAlerts, checkShootingZoneAlerts, checkWeatherAlerts]);

  return {
    // State
    alerts,
    unreadCount,
    settings,
    isMuted,
    lastCheck,

    // Computed
    alertsByType,
    unreadAlerts,
    criticalAlerts,
    visibleAlerts,

    // Actions
    addAlert,
    markAsRead,
    markAllAsRead,
    dismissAlert,
    removeAlert,
    clearAllAlerts,
    toggleMute,
    updateSettings,

    // Alert creators
    createGameAlert,
    createActivityAlert,
    createZoneAlert,

    // Manual alert checks
    runAlertChecks,

    // Config
    ALERT_TYPES,
    ALERT_SEVERITY
  };
};

/**
 * Calcule la distance entre deux points en mètres
 */
const calculateDistance = (point1, point2) => {
  if (!point1 || !point2) return Infinity;
  
  const R = 6371000;
  const dLat = (point2.lat - point1.lat) * Math.PI / 180;
  const dLng = (point2.lng - point1.lng) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return R * c;
};

/**
 * Vérifie si un point est dans une zone de tir
 */
const isPointInShootingZone = (point, zone) => {
  if (!point || !zone || !zone.center) return false;
  
  const distance = calculateDistance(point, zone.center);
  if (distance > zone.range) return false;
  
  const y = Math.sin((point.lng - zone.center.lng) * Math.PI / 180) * Math.cos(point.lat * Math.PI / 180);
  const x = Math.cos(zone.center.lat * Math.PI / 180) * Math.sin(point.lat * Math.PI / 180) -
            Math.sin(zone.center.lat * Math.PI / 180) * Math.cos(point.lat * Math.PI / 180) * 
            Math.cos((point.lng - zone.center.lng) * Math.PI / 180);
  let bearing = Math.atan2(y, x) * 180 / Math.PI;
  bearing = (bearing + 360) % 360;
  
  const halfAperture = zone.aperture / 2;
  let angleDiff = Math.abs(bearing - zone.direction);
  if (angleDiff > 180) angleDiff = 360 - angleDiff;
  
  return angleDiff <= halfAperture;
};

export default useGroupeAlerts;
