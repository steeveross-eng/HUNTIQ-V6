/**
 * GroupePanel - Panneau principal des fonctionnalités GROUPE
 * BIONIC Design System compliant
 * Version: 1.5.0 - Phase 6
 * 
 * Panneau regroupant les fonctionnalités collaboratives.
 * Intégré avec useGroupeTracking pour le tracking temps réel.
 * Intégré avec GroupChat pour la messagerie temps réel.
 * Intégré avec SafetyStatus pour la gestion de sécurité.
 * Intégré avec SmartAlerts pour les alertes intelligentes.
 * SessionHeatmap (Phase 6) intégré via carte principale.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { 
  Users, MapPin, Radio, Target, Navigation, Binoculars, Coffee,
  AlertTriangle, Activity, Bell, Shield, Clock, X, Maximize2,
  Minimize2, RefreshCw, Settings, ChevronRight, Eye, MessageSquare,
  ShieldCheck
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { useGroupeTracking, TRACKING_STATUS } from '../hooks/useGroupeTracking';
import { useGroupeAlerts } from '../hooks/useGroupeAlerts';
import { GroupChat } from './GroupChat';
import { SafetyStatus } from './SafetyStatus';
import { SmartAlerts } from './SmartAlerts';
import { useGroupeSafety, SAFETY_STATUS } from '../hooks/useGroupeSafety';

// Status configuration with BIONIC colors (using imported TRACKING_STATUS)
const STATUS_CONFIG = TRACKING_STATUS;

// Status icons mapping
const STATUS_ICONS = {
  hunting: Target,
  moving: Navigation,
  observing: Binoculars,
  break: Coffee,
  emergency: AlertTriangle
};

// Member status indicator
const MemberStatusBadge = ({ status, lastUpdate }) => {
  const { t } = useLanguage();
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.moving;
  const StatusIcon = STATUS_ICONS[status] || Navigation;
  
  // Calculate time since last update
  const getTimeSince = (timestamp) => {
    if (!timestamp) return '';
    const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}min`;
    return `${Math.floor(seconds / 3600)}h`;
  };
  
  return (
    <div className="flex items-center gap-2">
      <Badge 
        className="border-0 text-xs"
        style={{ 
          backgroundColor: config.bgVar, 
          color: config.colorVar 
        }}
      >
        <StatusIcon className="h-3 w-3 mr-1" />
        {t(config.labelKey)}
      </Badge>
      {lastUpdate && (
        <span className="text-xs text-[var(--bionic-text-muted)]">
          {getTimeSince(lastUpdate)}
        </span>
      )}
    </div>
  );
};

// Activity indicator (online status)
const OnlineIndicator = ({ isOnline, isRecent }) => {
  if (isOnline) {
    return <span className="w-2 h-2 rounded-full bg-[var(--bionic-green-primary)] animate-pulse" />;
  }
  if (isRecent) {
    return <span className="w-2 h-2 rounded-full bg-[var(--bionic-gold-primary)]" />;
  }
  return <span className="w-2 h-2 rounded-full bg-[var(--bionic-gray-500)]" />;
};

export const GroupePanel = ({ 
  groupId,
  userId,
  userName,
  isShareEnabled = false,
  onShareToggle,
  onClose,
  embedded = false,
  onCenterOnMember = null
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('members');
  const [isExpanded, setIsExpanded] = useState(!embedded);
  const [activities, setActivities] = useState([]);

  // Use the tracking hook for real data
  const {
    members,
    membersWithPositions,
    onlineMembersCount,
    totalMembersCount,
    isTracking,
    loading,
    startTracking,
    stopTracking,
    refreshPositions,
    getMemberCenter
  } = useGroupeTracking(userId, groupId, {
    autoStart: isShareEnabled,
    updateInterval: 30000
  });

  // Use the alerts hook for smart alerts
  const {
    alerts,
    unreadCount: alertUnreadCount,
    settings: alertSettings,
    isMuted,
    visibleAlerts,
    markAsRead: markAlertAsRead,
    markAllAsRead: markAllAlertsAsRead,
    dismissAlert,
    clearAllAlerts,
    toggleMute,
    updateSettings: updateAlertSettings
  } = useGroupeAlerts(userId, groupId, {
    members,
    myPosition: null, // Will be connected to user position later
    checkInterval: 15000
  });

  // Simulated activities
  useEffect(() => {
    setActivities([
      { id: '1', type: 'waypoint', user: 'Jean D.', message: 'groupe_activity_waypoint_added', time: new Date() },
      { id: '2', type: 'movement', user: 'Pierre M.', message: 'groupe_activity_entered_sector', time: new Date(Date.now() - 180000) },
      { id: '3', type: 'observation', user: 'Marc L.', message: 'groupe_activity_observation', time: new Date(Date.now() - 420000) }
    ]);
  }, [groupId]);

  // Handle tracking toggle
  useEffect(() => {
    if (isShareEnabled && !isTracking) {
      startTracking();
    } else if (!isShareEnabled && isTracking) {
      stopTracking();
    }
  }, [isShareEnabled, isTracking, startTracking, stopTracking]);

  // Refresh data
  const handleRefresh = useCallback(async () => {
    await refreshPositions();
  }, [refreshPositions]);

  // Center map on member
  const handleCenterOnMember = useCallback((memberId) => {
    if (onCenterOnMember) {
      const center = getMemberCenter(memberId);
      if (center) {
        onCenterOnMember(memberId, center);
      }
    }
  }, [onCenterOnMember, getMemberCenter]);

  // Container styles based on mode
  const containerClasses = embedded
    ? "bg-[var(--bionic-bg-card)] rounded-lg border border-[var(--bionic-border-primary)]"
    : "fixed inset-y-0 right-0 w-96 bg-[var(--bionic-bg-secondary)] border-l border-[var(--bionic-border-primary)] shadow-xl z-50";

  return (
    <div className={containerClasses} data-testid="groupe-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--bionic-border-secondary)]">
        <div className="flex items-center gap-3">
          <Users className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
          <div>
            <h3 className="text-[var(--bionic-text-primary)] font-semibold">
              {t('groupe_tab_title')}
            </h3>
            <p className="text-xs text-[var(--bionic-text-secondary)]">
              {onlineMembersCount}/{totalMembersCount || members.length} {t('groupe_members_active').toLowerCase()}
              {isTracking && (
                <Badge className="ml-2 bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)] text-[10px] border-0">
                  <Radio className="h-2 w-2 mr-1 animate-pulse" />
                  LIVE
                </Badge>
              )}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={loading}
            className="h-8 w-8 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)] hover:bg-[var(--bionic-bg-hover)]"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          
          {!embedded && (
            <>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-8 w-8 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)] hover:bg-[var(--bionic-bg-hover)]"
              >
                {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
              </Button>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-red-primary)] hover:bg-[var(--bionic-red-muted)]"
              >
                <X className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
        <TabsList className="w-full justify-start px-4 pt-2 bg-transparent border-b border-[var(--bionic-border-secondary)]">
          <TabsTrigger 
            value="members"
            className="data-[state=active]:text-[var(--bionic-gold-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--bionic-gold-primary)] rounded-none"
          >
            <Users className="h-4 w-4 mr-2" />
            {t('groupe_tab_members')}
          </TabsTrigger>
          <TabsTrigger 
            value="chat"
            className="data-[state=active]:text-[var(--bionic-gold-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--bionic-gold-primary)] rounded-none"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            {t('groupe_tab_chat')}
          </TabsTrigger>
          <TabsTrigger 
            value="activity"
            className="data-[state=active]:text-[var(--bionic-gold-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--bionic-gold-primary)] rounded-none"
          >
            <Activity className="h-4 w-4 mr-2" />
            {t('groupe_tab_activity')}
          </TabsTrigger>
          <TabsTrigger 
            value="alerts"
            className="data-[state=active]:text-[var(--bionic-gold-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--bionic-gold-primary)] rounded-none relative"
            data-testid="groupe-tab-alerts"
          >
            <Bell className="h-4 w-4 mr-2" />
            {t('groupe_tab_alerts')}
            {alertUnreadCount > 0 && (
              <Badge className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center bg-[var(--bionic-red-primary)] text-white text-xs">
                {alertUnreadCount}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger 
            value="security"
            className="data-[state=active]:text-[var(--bionic-gold-primary)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--bionic-gold-primary)] rounded-none"
            data-testid="groupe-tab-security"
          >
            <ShieldCheck className="h-4 w-4 mr-2" />
            {t('safety_title')}
          </TabsTrigger>
        </TabsList>

        {/* Members Tab */}
        <TabsContent value="members" className="p-4 m-0">
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {members.length === 0 ? (
                <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
                  <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">{t('groupe_no_members')}</p>
                </div>
              ) : (
                members.map(member => (
                  <Card 
                    key={member.id}
                    className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)] hover:border-[var(--bionic-gold-primary)] transition-colors cursor-pointer"
                    data-testid={`member-${member.id}`}
                  >
                    <CardContent className="p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <div className="w-10 h-10 rounded-full bg-[var(--bionic-gray-700)] flex items-center justify-center text-[var(--bionic-text-primary)] font-medium">
                              {member.name?.charAt(0) || '?'}
                            </div>
                            <span className="absolute bottom-0 right-0">
                              <OnlineIndicator 
                                isOnline={member.isOnline} 
                                isRecent={member.isRecent}
                              />
                            </span>
                          </div>
                          <div>
                            <p className="text-sm text-[var(--bionic-text-primary)] font-medium">
                              {member.name}
                            </p>
                            <MemberStatusBadge status={member.status} lastUpdate={member.lastUpdate} />
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCenterOnMember(member.id)}
                          disabled={!member.position}
                          className="h-8 w-8 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-gold-primary)] disabled:opacity-30"
                          title={member.position ? t('groupe_view_on_map') : t('groupe_no_position')}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Chat Tab */}
        <TabsContent value="chat" className="p-0 m-0">
          <GroupChat
            userId={userId}
            groupId={groupId}
            compact={true}
            maxHeight="400px"
          />
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity" className="p-4 m-0">
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {activities.map(activity => (
                <div 
                  key={activity.id}
                  className="flex items-start gap-3 p-3 bg-[var(--bionic-bg-hover)] rounded-lg"
                  data-testid={`activity-${activity.id}`}
                >
                  <div className="p-2 rounded-full bg-[var(--bionic-gold-muted)]">
                    <Radio className="h-3 w-3 text-[var(--bionic-gold-primary)]" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[var(--bionic-text-primary)]">
                      <span className="font-medium">{activity.user}</span>
                      {' '}{t(activity.message)}
                    </p>
                    <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
                      <Clock className="h-3 w-3 inline mr-1" />
                      {new Date(activity.time).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {activities.length === 0 && (
                <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
                  <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">{t('groupe_no_activity')}</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* Alerts Tab - Phase 5 Smart Alerts */}
        <TabsContent value="alerts" className="p-4 m-0" data-testid="groupe-alerts-content">
          <SmartAlerts
            alerts={visibleAlerts}
            unreadCount={alertUnreadCount}
            settings={alertSettings}
            isMuted={isMuted}
            onMarkAsRead={markAlertAsRead}
            onMarkAllAsRead={markAllAlertsAsRead}
            onDismiss={dismissAlert}
            onClearAll={clearAllAlerts}
            onToggleMute={toggleMute}
            onUpdateSettings={updateAlertSettings}
            onAction={(action, alert) => {
              // Handle alert actions
              if (action === 'view_on_map' && alert.location && onCenterOnMember) {
                onCenterOnMember(alert.memberId, alert.location);
              }
            }}
            compact={false}
            showSettings={true}
            showFilters={true}
            maxHeight="400px"
          />
        </TabsContent>

        {/* Security Tab - Phase 4 */}
        <TabsContent value="security" className="p-4 m-0" data-testid="groupe-security-content">
          <SafetyStatus
            safetyStatus="safe"
            myZone={null}
            dangerAlerts={[]}
            memberNames={{}}
            myPosition={null}
            onCreateZone={null}
            onUpdateZone={null}
            onClearZone={null}
            onSetZoneType={null}
            compact={false}
            showControls={true}
          />
        </TabsContent>
      </Tabs>

      {/* Safety Status Footer (Phase 2+) */}
      <div className="p-4 border-t border-[var(--bionic-border-secondary)]">
        <p className="text-xs text-[var(--bionic-text-muted)] text-center">
          {t('groupe_safety_footer')}
        </p>
      </div>
    </div>
  );
};

export default GroupePanel;
