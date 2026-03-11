/**
 * useGroupeChat - Hook pour le chat du module GROUPE
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 3.5
 * 
 * Gère les messages, alertes et communications temps réel du groupe.
 * Wrapper autour de l'infrastructure chat existante dans useLiveTracking.
 */
import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { toast } from 'sonner';

// API helper
const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const apiRequest = async (endpoint, options = {}) => {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
};

// Message types configuration
export const MESSAGE_TYPES = {
  text: {
    id: 'text',
    labelKey: 'chat_type_text',
    icon: 'MessageSquare'
  },
  alert: {
    id: 'alert',
    labelKey: 'chat_type_alert',
    icon: 'AlertTriangle'
  },
  location: {
    id: 'location',
    labelKey: 'chat_type_location',
    icon: 'MapPin'
  },
  observation: {
    id: 'observation',
    labelKey: 'chat_type_observation',
    icon: 'Eye'
  },
  waypoint: {
    id: 'waypoint',
    labelKey: 'chat_type_waypoint',
    icon: 'Target'
  }
};

// Alert types configuration with BIONIC colors
export const ALERT_TYPES = {
  emergency: {
    id: 'emergency',
    labelKey: 'chat_alert_emergency',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)',
    icon: 'AlertTriangle',
    vibrate: true,
    priority: 1
  },
  danger: {
    id: 'danger',
    labelKey: 'chat_alert_danger',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)',
    icon: 'ShieldAlert',
    vibrate: true,
    priority: 2
  },
  warning: {
    id: 'warning',
    labelKey: 'chat_alert_warning',
    colorVar: 'var(--bionic-gold-primary)',
    bgVar: 'var(--bionic-gold-muted)',
    icon: 'AlertCircle',
    vibrate: true,
    priority: 3
  },
  game_spotted: {
    id: 'game_spotted',
    labelKey: 'chat_alert_game_spotted',
    colorVar: 'var(--bionic-green-primary)',
    bgVar: 'var(--bionic-green-muted)',
    icon: 'Target',
    vibrate: false,
    priority: 4
  },
  position_update: {
    id: 'position_update',
    labelKey: 'chat_alert_position',
    colorVar: 'var(--bionic-blue-light)',
    bgVar: 'var(--bionic-blue-muted)',
    icon: 'MapPin',
    vibrate: false,
    priority: 5
  },
  break: {
    id: 'break',
    labelKey: 'chat_alert_break',
    colorVar: 'var(--bionic-gray-400)',
    bgVar: 'var(--bionic-bg-hover)',
    icon: 'Coffee',
    vibrate: false,
    priority: 6
  }
};

// Quick messages for fast communication
export const QUICK_MESSAGES = [
  { id: 'ok', textKey: 'chat_quick_ok', icon: 'ThumbsUp' },
  { id: 'wait', textKey: 'chat_quick_wait', icon: 'Hand' },
  { id: 'coming', textKey: 'chat_quick_coming', icon: 'Navigation' },
  { id: 'stay', textKey: 'chat_quick_stay', icon: 'Pause' },
  { id: 'quiet', textKey: 'chat_quick_quiet', icon: 'VolumeX' },
  { id: 'game_seen', textKey: 'chat_quick_game_seen', icon: 'Eye' }
];

export const useGroupeChat = (userId, groupId, options = {}) => {
  const {
    autoLoad = true,
    messageLimit = 50,
    onNewMessage = null,
    onAlert = null,
    enableVibration = true
  } = options;

  // State
  const [messages, setMessages] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [vibrationEnabled, setVibrationEnabled] = useState(() => {
    const saved = localStorage.getItem('bionic_chat_vibration');
    return saved !== null ? JSON.parse(saved) : enableVibration;
  });

  // Refs
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Vibration helper
  const triggerVibration = useCallback((pattern = [200, 100, 200]) => {
    if (vibrationEnabled && 'vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  }, [vibrationEnabled]);

  // Toggle vibration
  const toggleVibration = useCallback((enabled) => {
    setVibrationEnabled(enabled);
    localStorage.setItem('bionic_chat_vibration', JSON.stringify(enabled));
  }, []);

  // Fetch messages
  const fetchMessages = useCallback(async (limit = messageLimit) => {
    if (!userId || !groupId) return;
    
    setLoading(true);
    try {
      const result = await apiRequest(
        `/api/chat/${groupId}/messages?user_id=${userId}&limit=${limit}`
      );
      setMessages(result.messages || []);
      return result.messages;
    } catch (e) {
      console.error('Error fetching messages:', e);
      // Return empty array on error to avoid breaking the UI
      return [];
    } finally {
      setLoading(false);
    }
  }, [userId, groupId, messageLimit]);

  // Send text message
  const sendMessage = useCallback(async (content, options = {}) => {
    if (!userId || !groupId || !content.trim()) return null;
    
    setSending(true);
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
      
      const newMessage = result.message || {
        id: Date.now().toString(),
        user_id: userId,
        content: content.trim(),
        message_type: options.type || 'text',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, newMessage]);
      
      if (onNewMessage) onNewMessage(newMessage);
      
      return newMessage;
    } catch (e) {
      // Create local message on API failure for offline support
      const localMessage = {
        id: `local_${Date.now()}`,
        user_id: userId,
        content: content.trim(),
        message_type: options.type || 'text',
        timestamp: new Date().toISOString(),
        pending: true
      };
      
      setMessages(prev => [...prev, localMessage]);
      toast.error('Message en attente', { description: 'Sera envoyé quand la connexion sera rétablie' });
      
      return localMessage;
    } finally {
      setSending(false);
    }
  }, [userId, groupId, onNewMessage]);

  // Send quick message
  const sendQuickMessage = useCallback(async (quickId) => {
    const quick = QUICK_MESSAGES.find(q => q.id === quickId);
    if (!quick) return null;
    
    return sendMessage(`[QUICK:${quickId}]`, { type: 'quick' });
  }, [sendMessage]);

  // Send alert
  const sendAlert = useCallback(async (alertType, message = null, location = null) => {
    if (!userId || !groupId) return null;
    
    const alertConfig = ALERT_TYPES[alertType];
    if (!alertConfig) {
      console.error('Unknown alert type:', alertType);
      return null;
    }
    
    setSending(true);
    try {
      const result = await apiRequest(`/api/chat/${groupId}/alert/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          alert_type: alertType,
          message: message,
          location: location
        })
      });
      
      const newAlert = result.message || {
        id: Date.now().toString(),
        user_id: userId,
        message_type: 'alert',
        alert_type: alertType,
        content: message,
        location: location,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, newAlert]);
      
      // Trigger vibration for high priority alerts
      if (alertConfig.vibrate) {
        triggerVibration([300, 100, 300, 100, 300]);
      }
      
      if (onAlert) onAlert(newAlert);
      
      toast.success('Alerte envoyée', {
        description: alertConfig.labelKey
      });
      
      return newAlert;
    } catch (e) {
      toast.error('Erreur d\'envoi', { description: e.message });
      return null;
    } finally {
      setSending(false);
    }
  }, [userId, groupId, triggerVibration, onAlert]);

  // Send location
  const sendLocation = useCallback(async (location, message = null) => {
    if (!location || !location.lat || !location.lng) return null;
    
    return sendMessage(message || 'Position partagée', {
      type: 'location',
      location: location
    });
  }, [sendMessage]);

  // Mark messages as read
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

  // Set typing indicator
  const setTypingStatus = useCallback((typing) => {
    setIsTyping(typing);
    
    // Auto-clear typing after 3 seconds
    if (typing) {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
      }, 3000);
    }
  }, []);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Add incoming message (for WebSocket integration)
  const addIncomingMessage = useCallback((message) => {
    setMessages(prev => {
      // Avoid duplicates
      if (prev.find(m => m.id === message.id)) {
        return prev;
      }
      return [...prev, message];
    });
    
    // Increment unread if not from current user
    if (message.user_id !== userId) {
      setUnreadCount(prev => prev + 1);
      
      // Vibrate for alerts
      if (message.message_type === 'alert' && ALERT_TYPES[message.alert_type]?.vibrate) {
        triggerVibration([200, 100, 200]);
      }
      
      if (onNewMessage) onNewMessage(message);
    }
  }, [userId, triggerVibration, onNewMessage]);

  // Filter messages by type
  const messagesByType = useMemo(() => {
    return {
      all: messages,
      text: messages.filter(m => m.message_type === 'text'),
      alerts: messages.filter(m => m.message_type === 'alert'),
      locations: messages.filter(m => m.message_type === 'location'),
      quick: messages.filter(m => m.message_type === 'quick')
    };
  }, [messages]);

  // Recent alerts (last 5)
  const recentAlerts = useMemo(() => {
    return messages
      .filter(m => m.message_type === 'alert')
      .slice(-5)
      .reverse();
  }, [messages]);

  // Auto-load messages
  useEffect(() => {
    if (autoLoad && userId && groupId) {
      fetchMessages();
    }
  }, [autoLoad, userId, groupId, fetchMessages]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return {
    // State
    messages,
    unreadCount,
    loading,
    sending,
    isTyping,
    typingUsers,
    vibrationEnabled,
    
    // Filtered messages
    messagesByType,
    recentAlerts,
    
    // Actions
    fetchMessages,
    sendMessage,
    sendQuickMessage,
    sendAlert,
    sendLocation,
    markAsRead,
    setTypingStatus,
    scrollToBottom,
    toggleVibration,
    addIncomingMessage,
    
    // Refs
    messagesEndRef,
    
    // Config
    MESSAGE_TYPES,
    ALERT_TYPES,
    QUICK_MESSAGES
  };
};

export default useGroupeChat;
