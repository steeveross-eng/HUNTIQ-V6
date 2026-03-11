/**
 * useGroupeTracking - Hook wrapper pour le tracking du module GROUPE
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 3
 * 
 * Encapsule useLiveTracking avec la logique spécifique au module GROUPE
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import { useLiveTracking } from '../../../hooks/useLiveTracking';

// Status types avec leurs configurations BIONIC
export const TRACKING_STATUS = {
  hunting: { 
    id: 'hunting',
    labelKey: 'groupe_status_hunting',
    colorVar: 'var(--bionic-gold-primary)',
    bgVar: 'var(--bionic-gold-muted)'
  },
  moving: { 
    id: 'moving',
    labelKey: 'groupe_status_moving',
    colorVar: 'var(--bionic-blue-light)',
    bgVar: 'var(--bionic-blue-muted)'
  },
  observing: { 
    id: 'observing',
    labelKey: 'groupe_status_observing',
    colorVar: 'var(--bionic-green-primary)',
    bgVar: 'var(--bionic-green-muted)'
  },
  break: { 
    id: 'break',
    labelKey: 'groupe_status_break',
    colorVar: 'var(--bionic-gray-400)',
    bgVar: 'var(--bionic-bg-hover)'
  },
  emergency: { 
    id: 'emergency',
    labelKey: 'groupe_status_emergency',
    colorVar: 'var(--bionic-red-primary)',
    bgVar: 'var(--bionic-red-muted)'
  }
};

// Determine online status based on last update time
const getOnlineStatus = (lastUpdate) => {
  if (!lastUpdate) return { isOnline: false, isRecent: false };
  
  const now = Date.now();
  const lastTime = new Date(lastUpdate).getTime();
  const diffMs = now - lastTime;
  
  // Online: less than 2 minutes
  if (diffMs < 120000) return { isOnline: true, isRecent: true };
  // Recent: less than 5 minutes
  if (diffMs < 300000) return { isOnline: false, isRecent: true };
  // Offline
  return { isOnline: false, isRecent: false };
};

// Format time since last update
const formatTimeSince = (timestamp) => {
  if (!timestamp) return '';
  
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}min`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}j`;
};

export const useGroupeTracking = (userId, groupId, options = {}) => {
  const {
    autoStart = false,
    updateInterval = 30000,
    onMemberUpdate = null,
    onMemberEnterZone = null,
    onMemberExitZone = null
  } = options;

  // Use the existing live tracking hook
  const liveTracking = useLiveTracking(userId, groupId, {
    autoStart,
    updateInterval,
    onMemberUpdate: (members) => {
      // Transform members data for GROUPE module
      const transformedMembers = members.map(transformMemberData);
      if (onMemberUpdate) onMemberUpdate(transformedMembers);
    }
  });

  // Local state for enhanced member data
  const [myStatus, setMyStatus] = useState('moving');
  const [memberHistory, setMemberHistory] = useState({});

  // Transform raw member data to GROUPE format
  const transformMemberData = useCallback((member) => {
    const onlineStatus = getOnlineStatus(member.last_update || member.timestamp);
    const statusConfig = TRACKING_STATUS[member.status] || TRACKING_STATUS.moving;
    
    return {
      id: member.user_id || member.id,
      name: member.user_name || member.name || `User ${member.user_id?.slice(-4) || '????'}`,
      position: member.position || (member.lat && member.lng ? { lat: member.lat, lng: member.lng } : null),
      status: member.status || 'moving',
      statusConfig,
      lastUpdate: member.last_update || member.timestamp,
      timeSince: formatTimeSince(member.last_update || member.timestamp),
      accuracy: member.accuracy,
      heading: member.heading,
      speed: member.speed,
      ...onlineStatus
    };
  }, []);

  // Enhanced members positions with GROUPE formatting
  const members = useMemo(() => {
    return (liveTracking.membersPositions || []).map(transformMemberData);
  }, [liveTracking.membersPositions, transformMemberData]);

  // Members with valid positions (for map display)
  const membersWithPositions = useMemo(() => {
    return members.filter(m => m.position && m.position.lat && m.position.lng);
  }, [members]);

  // Online members count
  const onlineMembersCount = useMemo(() => {
    return members.filter(m => m.isOnline).length;
  }, [members]);

  // Update my status
  const updateMyStatus = useCallback(async (newStatus) => {
    if (!TRACKING_STATUS[newStatus]) return;
    
    setMyStatus(newStatus);
    
    // Send status update via tracking API
    try {
      await liveTracking.updateSettings({ status: newStatus });
    } catch (e) {
      console.error('Error updating status:', e);
    }
  }, [liveTracking]);

  // Get member position history (for trails)
  const getMemberTrail = useCallback(async (memberId, hours = 2) => {
    if (memberHistory[memberId]) {
      return memberHistory[memberId];
    }
    
    const history = await liveTracking.getPositionHistory(memberId, hours);
    
    setMemberHistory(prev => ({
      ...prev,
      [memberId]: history
    }));
    
    return history;
  }, [liveTracking, memberHistory]);

  // Clear member history cache
  const clearHistoryCache = useCallback(() => {
    setMemberHistory({});
  }, []);

  // Center map on member
  const getMemberCenter = useCallback((memberId) => {
    const member = members.find(m => m.id === memberId);
    if (member?.position) {
      return [member.position.lat, member.position.lng];
    }
    return null;
  }, [members]);

  return {
    // From useLiveTracking
    isTracking: liveTracking.isTracking,
    myPosition: liveTracking.myPosition,
    loading: liveTracking.loading,
    sessionId: liveTracking.sessionId,
    trackingMode: liveTracking.trackingMode,
    shareExactPosition: liveTracking.shareExactPosition,
    
    // Enhanced data
    members,
    membersWithPositions,
    onlineMembersCount,
    totalMembersCount: members.length,
    myStatus,
    memberHistory,
    
    // Actions from useLiveTracking
    startTracking: liveTracking.startTracking,
    stopTracking: liveTracking.stopTracking,
    sendManualPosition: liveTracking.sendManualPosition,
    refreshPositions: liveTracking.refreshPositions,
    updateSettings: liveTracking.updateSettings,
    setTrackingMode: liveTracking.setTrackingMode,
    setShareExactPosition: liveTracking.setShareExactPosition,
    
    // GROUPE specific actions
    updateMyStatus,
    getMemberTrail,
    getMemberCenter,
    clearHistoryCache,
    
    // Status config
    TRACKING_STATUS
  };
};

export default useGroupeTracking;
