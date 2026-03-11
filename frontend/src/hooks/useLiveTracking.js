/**
 * useLiveTracking - Hook pour le tracking en temps réel des membres du groupe
 * useGroupChat - Hook pour le chat de groupe
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const apiRequest = async (endpoint, options = {}) => {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur réseau' }));
    throw new Error(error.detail || 'Erreur serveur');
  }
  
  return response.json();
};

// ============================================
// LIVE TRACKING HOOK
// ============================================

export const useLiveTracking = (userId, groupId, options = {}) => {
  const {
    autoStart = false,
    updateInterval = 30000, // 30 secondes
    onMemberUpdate = null,
    onMemberJoin = null,
    onMemberLeave = null
  } = options;

  const [isTracking, setIsTracking] = useState(false);
  const [trackingMode, setTrackingMode] = useState('auto'); // auto ou manual
  const [shareExactPosition, setShareExactPosition] = useState(true);
  const [membersPositions, setMembersPositions] = useState([]);
  const [myPosition, setMyPosition] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  
  const watchIdRef = useRef(null);
  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // Démarrer la session de tracking
  const startTracking = useCallback(async () => {
    if (!userId || !groupId) {
      toast.error('Connexion requise');
      return false;
    }
    
    setLoading(true);
    try {
      const result = await apiRequest(`/api/tracking/session/start/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          group_id: groupId,
          settings: {
            mode: trackingMode,
            share_exact_position: shareExactPosition,
            update_interval: Math.round(updateInterval / 1000)
          }
        })
      });
      
      setSessionId(result.session.id);
      setIsTracking(true);
      
      // Démarrer la géolocalisation
      if ('geolocation' in navigator) {
        watchIdRef.current = navigator.geolocation.watchPosition(
          (position) => {
            const pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
              accuracy: position.coords.accuracy,
              altitude: position.coords.altitude,
              heading: position.coords.heading,
              speed: position.coords.speed
            };
            setMyPosition(pos);
            
            // Envoyer la position si mode auto
            if (trackingMode === 'auto') {
              sendPosition(pos);
            }
          },
          (error) => {
            console.error('Geolocation error:', error);
            toast.error('Erreur de géolocalisation');
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 5000
          }
        );
      }
      
      // Polling des positions des membres
      intervalRef.current = setInterval(fetchMembersPositions, updateInterval);
      fetchMembersPositions();
      
      toast.success('Tracking démarré', {
        description: 'Votre position est partagée avec le groupe'
      });
      
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    } finally {
      setLoading(false);
    }
  }, [userId, groupId, trackingMode, shareExactPosition, updateInterval]);

  // Arrêter le tracking
  const stopTracking = useCallback(async () => {
    if (!userId || !groupId) return;
    
    try {
      await apiRequest(`/api/tracking/session/stop/${userId}?group_id=${groupId}`, {
        method: 'POST'
      });
      
      // Nettoyer
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      
      setIsTracking(false);
      setSessionId(null);
      
      toast.success('Tracking arrêté');
    } catch (e) {
      console.error('Error stopping tracking:', e);
    }
  }, [userId, groupId]);

  // Envoyer la position
  const sendPosition = useCallback(async (position) => {
    if (!userId || !groupId || !isTracking) return;
    
    try {
      await apiRequest(`/api/tracking/position/${userId}?group_id=${groupId}`, {
        method: 'POST',
        body: JSON.stringify(position)
      });
    } catch (e) {
      console.error('Error sending position:', e);
    }
  }, [userId, groupId, isTracking]);

  // Envoyer la position manuellement
  const sendManualPosition = useCallback(() => {
    if (myPosition) {
      sendPosition(myPosition);
      toast.success('Position envoyée');
    }
  }, [myPosition, sendPosition]);

  // Récupérer les positions des membres
  const fetchMembersPositions = useCallback(async () => {
    if (!userId || !groupId) return;
    
    try {
      const result = await apiRequest(`/api/tracking/group/${groupId}/positions?user_id=${userId}`);
      setMembersPositions(result.members || []);
      
      if (onMemberUpdate) {
        onMemberUpdate(result.members);
      }
    } catch (e) {
      console.error('Error fetching positions:', e);
    }
  }, [userId, groupId, onMemberUpdate]);

  // Récupérer l'historique des positions (trajet)
  const getPositionHistory = useCallback(async (targetUserId, hours = 6) => {
    if (!groupId) return [];
    
    try {
      const result = await apiRequest(
        `/api/tracking/history/${targetUserId}?group_id=${groupId}&hours=${hours}`
      );
      return result.positions || [];
    } catch (e) {
      console.error('Error fetching history:', e);
      return [];
    }
  }, [groupId]);

  // Mettre à jour les paramètres
  const updateSettings = useCallback(async (newSettings) => {
    if (!userId || !groupId) return;
    
    try {
      await apiRequest(`/api/tracking/settings/${userId}?group_id=${groupId}`, {
        method: 'PUT',
        body: JSON.stringify(newSettings)
      });
      
      if (newSettings.mode) setTrackingMode(newSettings.mode);
      if (newSettings.share_exact_position !== undefined) {
        setShareExactPosition(newSettings.share_exact_position);
      }
      
      toast.success('Paramètres mis à jour');
    } catch (e) {
      toast.error('Erreur', { description: e.message });
    }
  }, [userId, groupId]);

  // Cleanup au démontage
  useEffect(() => {
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Auto-start si demandé
  useEffect(() => {
    if (autoStart && userId && groupId && !isTracking) {
      startTracking();
    }
  }, [autoStart, userId, groupId]); // eslint-disable-line

  return {
    // État
    isTracking,
    trackingMode,
    shareExactPosition,
    membersPositions,
    myPosition,
    loading,
    sessionId,
    
    // Actions
    startTracking,
    stopTracking,
    sendManualPosition,
    getPositionHistory,
    updateSettings,
    refreshPositions: fetchMembersPositions,
    
    // Setters
    setTrackingMode,
    setShareExactPosition
  };
};

// ============================================
// GROUP CHAT HOOK
// ============================================

export const useGroupChat = (userId, groupId, options = {}) => {
  const {
    autoConnect = true,
    onNewMessage = null,
    onUserTyping = null,
    onAlert = null
  } = options;

  const [messages, setMessages] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alertTypes, setAlertTypes] = useState({});
  const [quickMessages, setQuickMessages] = useState([]);
  const [vibrationEnabled, setVibrationEnabled] = useState(() => {
    // Charger la préférence depuis localStorage
    const saved = localStorage.getItem('bionic_vibration_enabled');
    return saved !== null ? JSON.parse(saved) : true;
  });
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Toggle vibration ON/OFF
  const toggleVibration = useCallback((enabled) => {
    setVibrationEnabled(enabled);
    localStorage.setItem('bionic_vibration_enabled', JSON.stringify(enabled));
    toast.success(enabled ? 'Vibrations activées' : 'Vibrations désactivées');
  }, []);

  // Fonction de vibration conditionnelle
  const triggerVibration = useCallback((pattern = [200, 100, 200]) => {
    if (vibrationEnabled && 'vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  }, [vibrationEnabled]);

  // Charger les types d'alerte
  const fetchAlertTypes = useCallback(async () => {
    try {
      const result = await apiRequest('/api/chat/alert-types');
      setAlertTypes(result.alert_types || {});
      setQuickMessages(result.quick_messages || []);
    } catch (e) {
      console.error('Error fetching alert types:', e);
    }
  }, []);

  // Charger les messages
  const fetchMessages = useCallback(async (limit = 50) => {
    if (!userId || !groupId) return;
    
    setLoading(true);
    try {
      const result = await apiRequest(
        `/api/chat/${groupId}/messages?user_id=${userId}&limit=${limit}`
      );
      setMessages(result.messages || []);
    } catch (e) {
      console.error('Error fetching messages:', e);
    } finally {
      setLoading(false);
    }
  }, [userId, groupId]);

  // Envoyer un message
  const sendMessage = useCallback(async (content, options = {}) => {
    if (!userId || !groupId || !content.trim()) return null;
    
    try {
      const result = await apiRequest(`/api/chat/${groupId}/message/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          content: content.trim(),
          message_type: options.type || 'text',
          alert_type: options.alertType || null,
          location: options.location || null
        })
      });
      
      // Ajouter le message localement
      setMessages(prev => [...prev, result.message]);
      
      return result.message;
    } catch (e) {
      toast.error('Erreur d\'envoi', { description: e.message });
      return null;
    }
  }, [userId, groupId]);

  // Envoyer une alerte
  const sendAlert = useCallback(async (alertType, message = null, location = null) => {
    if (!userId || !groupId) return null;
    
    try {
      const result = await apiRequest(`/api/chat/${groupId}/alert/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          alert_type: alertType,
          message: message,
          location: location
        })
      });
      
      setMessages(prev => [...prev, result.message]);
      
      // Vibrer si activé et type d'alerte le requiert
      if (alertTypes[alertType]?.vibrate) {
        triggerVibration([200, 100, 200]);
      }
      
      toast.success('Alerte envoyée !', {
        description: alertTypes[alertType]?.label || alertType
      });
      
      return result.message;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return null;
    }
  }, [userId, groupId, alertTypes, triggerVibration]);

  // Marquer comme lu
  const markAsRead = useCallback(async () => {
    if (!userId || !groupId) return;
    
    try {
      await apiRequest(`/api/chat/${groupId}/messages/read/${userId}`, {
        method: 'PATCH'
      });
      setUnreadCount(0);
    } catch (e) {
      console.error('Error marking as read:', e);
    }
  }, [userId, groupId]);

  // Compter les non lus
  const fetchUnreadCount = useCallback(async () => {
    if (!userId || !groupId) return;
    
    try {
      const result = await apiRequest(`/api/chat/${groupId}/unread-count/${userId}`);
      setUnreadCount(result.unread_count || 0);
    } catch (e) {
      console.error('Error fetching unread count:', e);
    }
  }, [userId, groupId]);

  // Connexion WebSocket
  const connectWebSocket = useCallback(() => {
    if (!userId || !groupId || wsRef.current) return;
    
    const wsUrl = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/api/chat/ws/${groupId}/${userId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Chat WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message') {
          const msg = data.message;
          setMessages(prev => {
            // Éviter les doublons
            if (prev.some(m => m.id === msg.id)) return prev;
            return [...prev, msg];
          });
          
          if (msg.sender_id !== userId) {
            setUnreadCount(prev => prev + 1);
            
            // Vibration pour les alertes (si activée)
            if (msg.alert_info?.vibrate) {
              triggerVibration([200, 100, 200]);
            }
            
            if (msg.message_type === 'alert' && onAlert) {
              onAlert(msg);
            }
          }
          
          if (onNewMessage) onNewMessage(msg);
        } else if (data.type === 'user_typing' && onUserTyping) {
          onUserTyping(data);
        }
      } catch (e) {
        console.error('Error parsing WS message:', e);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      
      // Reconnexion auto après 3s
      reconnectTimeoutRef.current = setTimeout(() => {
        if (userId && groupId) connectWebSocket();
      }, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('Chat WebSocket error:', error);
    };
    
    wsRef.current = ws;
  }, [userId, groupId, onNewMessage, onUserTyping, onAlert, triggerVibration]);

  // Déconnecter WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
  }, []);

  // Envoyer indicateur de frappe
  const sendTyping = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing' }));
    }
  }, []);

  // Initialisation
  useEffect(() => {
    fetchAlertTypes();
  }, [fetchAlertTypes]);

  useEffect(() => {
    if (userId && groupId) {
      fetchMessages();
      fetchUnreadCount();
      
      if (autoConnect) {
        connectWebSocket();
      }
    }
    
    return () => {
      disconnectWebSocket();
    };
  }, [userId, groupId]); // eslint-disable-line

  return {
    // État
    messages,
    unreadCount,
    isConnected,
    loading,
    alertTypes,
    quickMessages,
    vibrationEnabled,
    
    // Actions
    sendMessage,
    sendAlert,
    markAsRead,
    sendTyping,
    toggleVibration,
    refreshMessages: fetchMessages,
    connect: connectWebSocket,
    disconnect: disconnectWebSocket
  };
};

export default useLiveTracking;
