/**
 * GeoSyncToggle - Real-time WebSocket Synchronization Toggle
 * Phase P6.4 - WebSocket Integration
 * P0.3 BIONIC V5 - Correction wss:// production
 * 
 * Provides a toggle to enable/disable real-time sync with hunting group members.
 * 
 * CONFIDENTIALITÉ:
 * - Les HOTSPOTS et CORRIDORS sont EXCLUS de la synchronisation
 * - Ces données sensibles restent 100% privées
 * - Seuls les waypoints, zones et POI non-sensibles peuvent être synchronisés
 * - Aucune notification de localisation automatique
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Génère l'URL WebSocket correcte selon l'environnement
 * P0.3: Support obligatoire de wss:// en production
 */
const getWebSocketUrl = () => {
  if (!API_URL) return null;
  
  // En production (HTTPS), utiliser wss://
  if (API_URL.startsWith('https://')) {
    return API_URL.replace('https://', 'wss://');
  }
  
  // En développement (HTTP), utiliser ws://
  if (API_URL.startsWith('http://')) {
    return API_URL.replace('http://', 'ws://');
  }
  
  // Fallback: détecter depuis window.location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = API_URL.replace(/^https?:\/\//, '');
  return `${protocol}//${host}`;
};

const WS_URL = getWebSocketUrl();

// Types d'entités PRIVÉES - jamais synchronisées
const PRIVATE_ENTITY_TYPES = new Set(['hotspot', 'corridor']);

const GeoSyncToggle = ({ 
  groupId = 'default_group',
  userId = 'default_user',
  onEntityReceived,
  onMemberJoined,
  onMemberLeft
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isEnabled, setIsEnabled] = useState(false);
  const [activeMembers, setActiveMembers] = useState([]);
  const [lastSync, setLastSync] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Vérifier que l'URL WebSocket est disponible
    if (!WS_URL) {
      console.error('[GeoSync] WebSocket URL not configured');
      toast.error('URL WebSocket non configurée');
      return;
    }

    try {
      const wsUrl = `${WS_URL}/ws/geo-sync?token=user:${userId}&group_id=${groupId}`;
      console.log('[GeoSync] Connecting to WebSocket:', wsUrl);
      console.log('[GeoSync] Protocol:', wsUrl.startsWith('wss://') ? 'WSS (secure)' : 'WS (insecure)');
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('[GeoSync] WebSocket connected successfully');
        setIsConnected(true);
        toast.success('Synchronisation temps réel activée');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (e) {
          console.error('[GeoSync] Error parsing message:', e);
        }
      };
      
      ws.onclose = (event) => {
        console.log('[GeoSync] WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        
        // Messages d'erreur spécifiques selon le code
        if (event.code === 1006) {
          console.warn('[GeoSync] Connection lost unexpectedly (code 1006)');
          toast.error('Connexion WebSocket interrompue');
        }
        
        // Reconnect if still enabled
        if (isEnabled && event.code !== 4001 && event.code !== 4003 && event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('[GeoSync] Attempting reconnection...');
            connect();
          }, 3000);
        }
      };
      
      ws.onerror = (error) => {
        console.error('[GeoSync] WebSocket error:', error);
        // Ne pas afficher de toast ici car onclose sera appelé après
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('[GeoSync] Failed to create WebSocket:', error);
      toast.error('Impossible de se connecter au serveur temps réel');
    }
  }, [groupId, userId, isEnabled]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disabled sync');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setActiveMembers([]);
    toast.info('Synchronisation désactivée');
  }, []);

  // Handle incoming messages
  const handleMessage = useCallback((data) => {
    const { type, user_id, entity, entity_id, timestamp, active_members, location } = data;
    
    setLastSync(new Date(timestamp));
    
    switch (type) {
      case 'geo.created':
        if (onEntityReceived) {
          onEntityReceived({ action: 'created', entity, userId: user_id });
        }
        toast.info(`${user_id} a créé: ${entity?.name || 'un élément'}`);
        break;
        
      case 'geo.updated':
        if (onEntityReceived) {
          onEntityReceived({ action: 'updated', entity, entityId: entity_id, userId: user_id });
        }
        toast.info(`${user_id} a modifié: ${entity?.name || entity_id}`);
        break;
        
      case 'geo.deleted':
        if (onEntityReceived) {
          onEntityReceived({ action: 'deleted', entityId: entity_id, userId: user_id });
        }
        toast.info(`${user_id} a supprimé un élément`);
        break;
        
      case 'member.joined':
        setActiveMembers(active_members || []);
        if (onMemberJoined) {
          onMemberJoined(user_id);
        }
        toast.success(`${user_id} a rejoint le groupe`);
        break;
        
      case 'member.left':
        setActiveMembers(active_members || []);
        if (onMemberLeft) {
          onMemberLeft(user_id);
        }
        toast.info(`${user_id} a quitté le groupe`);
        break;
        
      case 'location.update':
        // Handle member location updates (for live tracking)
        console.log(`Location update from ${user_id}:`, location);
        break;
        
      case 'pong':
        // Keep-alive response
        break;
        
      case 'error':
        toast.error(`Erreur sync: ${data.message}`);
        break;
        
      default:
        console.log('Unknown message type:', type);
    }
  }, [onEntityReceived, onMemberJoined, onMemberLeft]);

  // Toggle sync on/off
  const toggleSync = () => {
    if (isEnabled) {
      setIsEnabled(false);
      disconnect();
    } else {
      setIsEnabled(true);
      connect();
    }
  };

  // Send geo event to group (with privacy check)
  const broadcastEvent = useCallback((eventType, entity = null, entityId = null) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot broadcast');
      return false;
    }
    
    // VÉRIFICATION DE CONFIDENTIALITÉ: Bloquer les types privés
    if (entity && PRIVATE_ENTITY_TYPES.has(entity.entity_type)) {
      console.warn('CONFIDENTIALITÉ: Les hotspots/corridors ne peuvent pas être synchronisés');
      toast.error('Cette entité est privée et ne peut pas être partagée');
      return false;
    }
    
    const message = {
      type: eventType,
      entity,
      entity_id: entityId
    };
    
    wsRef.current.send(JSON.stringify(message));
    return true;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Keep-alive ping every 30 seconds
  useEffect(() => {
    if (!isConnected) return;
    
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
    
    return () => clearInterval(pingInterval);
  }, [isConnected]);

  return (
    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
      {/* Sync Toggle Button */}
      <Button
        onClick={toggleSync}
        variant={isEnabled ? "default" : "outline"}
        size="sm"
        className={isEnabled ? "bg-green-600 hover:bg-green-700" : ""}
        data-testid="geo-sync-toggle"
      >
        {isEnabled ? "Sync ON" : "Sync OFF"}
      </Button>
      
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        <div 
          className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-slate-500'}`}
        />
        <span className="text-sm text-slate-400">
          {isConnected ? 'Connecté' : 'Déconnecté'}
        </span>
      </div>
      
      {/* Active Members */}
      {isConnected && activeMembers.length > 0 && (
        <div className="flex items-center gap-2 ml-4">
          <span className="text-sm text-slate-400">Membres:</span>
          <Badge variant="secondary">{activeMembers.length}</Badge>
        </div>
      )}
      
      {/* Last Sync Time */}
      {lastSync && (
        <span className="text-xs text-slate-500 ml-auto">
          Dernière sync: {lastSync.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};

// Export the component and a hook for broadcasting events
export { GeoSyncToggle };

// Custom hook for using geo sync in other components
export const useGeoSync = (groupId, userId) => {
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  
  const broadcast = useCallback((eventType, entity, entityId) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    
    ws.send(JSON.stringify({
      type: eventType,
      entity,
      entity_id: entityId
    }));
    return true;
  }, [ws]);
  
  return { isConnected, broadcast };
};

export default GeoSyncToggle;
