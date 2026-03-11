/**
 * useSharing - Hook pour le partage de waypoints et la gestion des groupes de chasse
 */

import { useState, useEffect, useCallback } from 'react';
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

/**
 * Hook pour le partage de waypoints
 */
export const useWaypointSharing = (userId) => {
  const [loading, setLoading] = useState(false);
  const [receivedShares, setReceivedShares] = useState([]);
  const [sentShares, setSentShares] = useState({ email_shares: [], link_shares: [] });

  // Partager par email
  const shareByEmail = useCallback(async (waypointId, waypointName, emails, message = null) => {
    if (!userId) {
      toast.error('Vous devez être connecté pour partager');
      return null;
    }
    
    setLoading(true);
    try {
      const result = await apiRequest(`/api/sharing/email/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          waypoint_id: waypointId,
          waypoint_name: waypointName,
          emails: emails,
          message: message,
          permission: 'collaborate'
        })
      });
      
      toast.success('Waypoint partagé !', {
        description: `${result.shares_created} invitation(s) envoyée(s)`
      });
      
      return result;
    } catch (e) {
      toast.error('Erreur de partage', { description: e.message });
      return null;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Créer un lien de partage
  const createShareLink = useCallback(async (waypointId, waypointName, expiresInDays = 30) => {
    if (!userId) {
      toast.error('Vous devez être connecté');
      return null;
    }
    
    setLoading(true);
    try {
      const result = await apiRequest(`/api/sharing/link/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          waypoint_id: waypointId,
          waypoint_name: waypointName,
          expires_in_days: expiresInDays,
          permission: 'collaborate'
        })
      });
      
      // Copier le lien dans le presse-papier
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(result.share_url);
        toast.success('Lien copié !', {
          description: 'Le lien de partage est dans votre presse-papier'
        });
      } else {
        toast.success('Lien créé !', {
          description: result.share_url
        });
      }
      
      return result;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return null;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Récupérer les partages reçus
  const fetchReceivedShares = useCallback(async () => {
    if (!userId) return;
    
    try {
      const result = await apiRequest(`/api/sharing/received/${userId}`);
      setReceivedShares(result.shares || []);
    } catch (e) {
      console.error('Error fetching received shares:', e);
    }
  }, [userId]);

  // Récupérer les partages envoyés
  const fetchSentShares = useCallback(async () => {
    if (!userId) return;
    
    try {
      const result = await apiRequest(`/api/sharing/sent/${userId}`);
      setSentShares(result);
    } catch (e) {
      console.error('Error fetching sent shares:', e);
    }
  }, [userId]);

  // Révoquer un lien
  const revokeShareLink = useCallback(async (linkId) => {
    if (!userId) return false;
    
    try {
      await apiRequest(`/api/sharing/link/${userId}/${linkId}`, {
        method: 'DELETE'
      });
      toast.success('Lien révoqué');
      fetchSentShares();
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    }
  }, [userId, fetchSentShares]);

  // Charger les données au montage
  useEffect(() => {
    if (userId) {
      fetchReceivedShares();
      fetchSentShares();
    }
  }, [userId, fetchReceivedShares, fetchSentShares]);

  return {
    loading,
    receivedShares,
    sentShares,
    shareByEmail,
    createShareLink,
    revokeShareLink,
    refreshShares: () => {
      fetchReceivedShares();
      fetchSentShares();
    }
  };
};

/**
 * Hook pour les groupes de chasse
 */
export const useHuntingGroups = (userId) => {
  const [loading, setLoading] = useState(false);
  const [myGroups, setMyGroups] = useState({ owned_groups: [], member_groups: [] });
  const [publicGroups, setPublicGroups] = useState([]);

  // Créer un groupe
  const createGroup = useCallback(async (name, description = '', isPublic = false) => {
    if (!userId) {
      toast.error('Vous devez être connecté');
      return null;
    }
    
    setLoading(true);
    try {
      const result = await apiRequest(`/api/groups/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          name,
          description,
          is_public: isPublic,
          max_members: 20
        })
      });
      
      toast.success('Groupe créé !', {
        description: `"${name}" est prêt`
      });
      
      fetchMyGroups();
      return result.group;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return null;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Récupérer mes groupes
  const fetchMyGroups = useCallback(async () => {
    if (!userId) return;
    
    try {
      const result = await apiRequest(`/api/groups/${userId}/my-groups`);
      setMyGroups(result);
    } catch (e) {
      console.error('Error fetching groups:', e);
    }
  }, [userId]);

  // Découvrir les groupes publics
  const discoverGroups = useCallback(async (search = '') => {
    try {
      const endpoint = search 
        ? `/api/groups/discover/public?search=${encodeURIComponent(search)}`
        : '/api/groups/discover/public';
      const result = await apiRequest(endpoint);
      setPublicGroups(result.groups || []);
    } catch (e) {
      console.error('Error discovering groups:', e);
    }
  }, []);

  // Rejoindre un groupe
  const joinGroup = useCallback(async (groupId, inviteCode = null) => {
    if (!userId) {
      toast.error('Vous devez être connecté');
      return false;
    }
    
    setLoading(true);
    try {
      const params = new URLSearchParams({ user_id: userId });
      if (inviteCode) params.append('invite_code', inviteCode);
      
      const result = await apiRequest(`/api/groups/${groupId}/join?${params}`, {
        method: 'POST'
      });
      
      toast.success('Groupe rejoint !', {
        description: result.message
      });
      
      fetchMyGroups();
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    } finally {
      setLoading(false);
    }
  }, [userId, fetchMyGroups]);

  // Rejoindre par code
  const joinByCode = useCallback(async (inviteCode) => {
    try {
      // D'abord récupérer les infos du groupe
      const groupInfo = await apiRequest(`/api/groups/join-by-code/${inviteCode}`);
      
      if (groupInfo.is_full) {
        toast.error('Groupe complet', {
          description: 'Ce groupe a atteint sa limite de membres'
        });
        return false;
      }
      
      // Rejoindre le groupe
      return await joinGroup(groupInfo.id, inviteCode);
    } catch (e) {
      toast.error('Code invalide', { description: e.message });
      return false;
    }
  }, [joinGroup]);

  // Quitter un groupe
  const leaveGroup = useCallback(async (groupId) => {
    if (!userId) return false;
    
    try {
      await apiRequest(`/api/groups/${groupId}/members/${userId}?requester_id=${userId}`, {
        method: 'DELETE'
      });
      
      toast.success('Vous avez quitté le groupe');
      fetchMyGroups();
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    }
  }, [userId, fetchMyGroups]);

  // Inviter des membres
  const inviteMembers = useCallback(async (groupId, emails, message = null) => {
    if (!userId) return false;
    
    setLoading(true);
    try {
      const result = await apiRequest(`/api/groups/${groupId}/invite?owner_id=${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          emails,
          message
        })
      });
      
      toast.success('Invitations envoyées !', {
        description: result.message
      });
      
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Partager un waypoint avec un groupe
  const shareWaypointWithGroup = useCallback(async (groupId, waypointId, waypointName) => {
    if (!userId) return false;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        user_id: userId,
        waypoint_id: waypointId,
        waypoint_name: waypointName
      });
      
      const result = await apiRequest(`/api/groups/${groupId}/share-waypoint?${params}`, {
        method: 'POST'
      });
      
      toast.success('Partagé avec le groupe !', {
        description: result.message
      });
      
      return true;
    } catch (e) {
      toast.error('Erreur', { description: e.message });
      return false;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Charger les groupes au montage
  useEffect(() => {
    if (userId) {
      fetchMyGroups();
    }
  }, [userId, fetchMyGroups]);

  return {
    loading,
    myGroups,
    publicGroups,
    allGroups: [...myGroups.owned_groups, ...myGroups.member_groups],
    createGroup,
    joinGroup,
    joinByCode,
    leaveGroup,
    inviteMembers,
    shareWaypointWithGroup,
    discoverGroups,
    refresh: fetchMyGroups
  };
};

/**
 * Hook pour les notifications
 */
export const useNotifications = (userId, options = {}) => {
  const { pollInterval = 30000, autoFetch = true } = options;
  
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async (unreadOnly = false) => {
    if (!userId) return;
    
    try {
      const params = unreadOnly ? '?unread_only=true' : '';
      const result = await apiRequest(`/api/sharing/notifications/${userId}${params}`);
      setNotifications(result.notifications || []);
      setUnreadCount(result.unread_count || 0);
    } catch (e) {
      console.error('Error fetching notifications:', e);
    }
  }, [userId]);

  const markAsRead = useCallback(async (notificationId) => {
    if (!userId) return;
    
    try {
      await apiRequest(`/api/sharing/notifications/${userId}/${notificationId}/read`, {
        method: 'PATCH'
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {
      console.error('Error marking notification read:', e);
    }
  }, [userId]);

  const markAllAsRead = useCallback(async () => {
    if (!userId) return;
    
    try {
      await apiRequest(`/api/sharing/notifications/${userId}/read-all`, {
        method: 'PATCH'
      });
      
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (e) {
      console.error('Error marking all notifications read:', e);
    }
  }, [userId]);

  // Fetch initial et polling
  useEffect(() => {
    if (userId && autoFetch) {
      fetchNotifications();
      
      const interval = setInterval(fetchNotifications, pollInterval);
      return () => clearInterval(interval);
    }
  }, [userId, autoFetch, pollInterval, fetchNotifications]);

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  };
};

export default useWaypointSharing;
