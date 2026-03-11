/**
 * NotificationCenter - Real-time notification system
 * Dropdown bell icon with notification list
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './GlobalAuth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Bell,
  BellOff,
  Check,
  CheckCheck,
  Trash2,
  Settings,
  Heart,
  MessageCircle,
  Users,
  Gift,
  Wallet,
  Target,
  AlertCircle,
  Megaphone,
  X,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Notification type icons
const notificationIcons = {
  like_post: <Heart className="h-4 w-4 text-red-400" />,
  like_comment: <Heart className="h-4 w-4 text-red-400" />,
  comment: <MessageCircle className="h-4 w-4 text-blue-400" />,
  reply: <MessageCircle className="h-4 w-4 text-blue-400" />,
  follow: <Users className="h-4 w-4 text-green-400" />,
  group_join: <Users className="h-4 w-4 text-purple-400" />,
  group_invite: <Users className="h-4 w-4 text-purple-400" />,
  group_post: <MessageCircle className="h-4 w-4 text-purple-400" />,
  referral_signup: <Gift className="h-4 w-4 text-[#f5a623]" />,
  referral_rewarded: <Gift className="h-4 w-4 text-green-400" />,
  wallet_credit: <Wallet className="h-4 w-4 text-green-400" />,
  wallet_debit: <Wallet className="h-4 w-4 text-red-400" />,
  wallet_transfer: <Wallet className="h-4 w-4 text-blue-400" />,
  lead_update: <Target className="h-4 w-4 text-purple-400" />,
  mention: <AlertCircle className="h-4 w-4 text-blue-400" />,
  system: <Megaphone className="h-4 w-4 text-[#f5a623]" />
};

// Time ago helper
const timeAgo = (dateString) => {
  const now = new Date();
  const date = new Date(dateString);
  const seconds = Math.floor((now - date) / 1000);
  
  if (seconds < 60) return 'à l\'instant';
  if (seconds < 3600) return `il y a ${Math.floor(seconds / 60)} min`;
  if (seconds < 86400) return `il y a ${Math.floor(seconds / 3600)} h`;
  if (seconds < 604800) return `il y a ${Math.floor(seconds / 86400)} j`;
  return date.toLocaleDateString('fr-CA');
};

const NotificationCenter = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState(null);

  // Load notifications
  const loadNotifications = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      const response = await axios.get(`${API}/notifications/${user.id}`);
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  }, [user?.id]);

  // Load preferences
  const loadPreferences = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      const response = await axios.get(`${API}/notifications/preferences/${user.id}`);
      setPreferences(response.data);
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  }, [user?.id]);

  // Poll for new notifications every 30 seconds
  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadNotifications();
      const interval = setInterval(loadNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated, user?.id, loadNotifications]);

  // Mark as seen when dropdown opens
  useEffect(() => {
    if (isOpen && user?.id && unreadCount > 0) {
      axios.post(`${API}/notifications/${user.id}/mark-seen`).catch(console.error);
    }
  }, [isOpen, user?.id, unreadCount]);

  // Mark single notification as read
  const markAsRead = async (notificationId) => {
    try {
      await axios.post(`${API}/notifications/${user.id}/mark-read`, null, {
        params: { notification_ids: [notificationId] }
      });
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      await axios.post(`${API}/notifications/${user.id}/mark-all-read`);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true, is_seen: true })));
      setUnreadCount(0);
      toast.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    try {
      await axios.delete(`${API}/notifications/${user.id}/${notificationId}`);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      toast.success('Notification supprimée');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    
    if (notification.link) {
      setIsOpen(false);
      navigate(notification.link);
    }
  };

  // Update preference
  const updatePreference = async (key, value) => {
    try {
      await axios.put(`${API}/notifications/preferences/${user.id}`, null, {
        params: { [key]: value }
      });
      setPreferences(prev => ({ ...prev, [key]: value }));
      toast.success('Préférences mises à jour');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  if (!isAuthenticated) return null;

  return (
    <>
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className="relative text-gray-300 hover:text-[#f5a623]"
            data-testid="notification-bell"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500 text-white text-xs animate-pulse">
                {unreadCount > 99 ? '99+' : unreadCount}
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        
        <DropdownMenuContent 
          align="end" 
          className="w-[380px] bg-card border-border p-0"
          data-testid="notification-dropdown"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Bell className="h-4 w-4 text-[#f5a623]" />
              Notifications
            </h3>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setIsOpen(false);
                  setShowSettings(true);
                  loadPreferences();
                }}
                className="h-8 w-8 p-0 text-gray-400"
              >
                <Settings className="h-4 w-4" />
              </Button>
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={markAllAsRead}
                  className="text-xs text-[#f5a623] hover:text-[#d4891c]"
                >
                  <CheckCheck className="h-4 w-4 mr-1" />
                  Tout lire
                </Button>
              )}
            </div>
          </div>

          {/* Notifications List */}
          <ScrollArea className="h-[400px]">
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-[#f5a623]" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="py-12 text-center">
                <BellOff className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Aucune notification</p>
                <p className="text-sm text-gray-500">Vous êtes à jour!</p>
              </div>
            ) : (
              <div>
                {notifications.map((notification, index) => (
                  <div key={notification.id}>
                    <div
                      className={`p-4 hover:bg-gray-800/50 cursor-pointer transition-colors ${
                        !notification.is_read ? 'bg-[#f5a623]/5 border-l-2 border-l-[#f5a623]' : ''
                      }`}
                      onClick={() => handleNotificationClick(notification)}
                      data-testid={`notification-${notification.id}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center shrink-0">
                          {notification.icon ? (
                            <span className="text-lg">{notification.icon}</span>
                          ) : (
                            notificationIcons[notification.type] || <Bell className="h-4 w-4 text-gray-400" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-white text-sm">{notification.title}</p>
                          <p className="text-gray-400 text-sm line-clamp-2">{notification.message}</p>
                          <p className="text-gray-500 text-xs mt-1">{timeAgo(notification.created_at)}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-gray-500 hover:text-red-400 shrink-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    {index < notifications.length - 1 && <Separator className="bg-border" />}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-border">
              <Button
                variant="ghost"
                className="w-full text-[#f5a623] hover:text-[#d4891c] hover:bg-[#f5a623]/10"
                onClick={() => {
                  setIsOpen(false);
                  navigate('/network');
                }}
              >
                Voir toutes les notifications
              </Button>
            </div>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="bg-card border-border max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Settings className="h-5 w-5 text-[#f5a623]" />
              Préférences de notification
            </DialogTitle>
            <DialogDescription>
              Personnalisez les notifications que vous recevez
            </DialogDescription>
          </DialogHeader>

          {preferences ? (
            <div className="space-y-6">
              {/* General */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-400 uppercase">Général</h4>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Notifications push</Label>
                    <p className="text-xs text-gray-500">Recevoir des notifications dans l'app</p>
                  </div>
                  <Switch
                    checked={preferences.push_notifications}
                    onCheckedChange={(v) => updatePreference('push_notifications', v)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Notifications email</Label>
                    <p className="text-xs text-gray-500">Recevoir un résumé par email</p>
                  </div>
                  <Switch
                    checked={preferences.email_notifications}
                    onCheckedChange={(v) => updatePreference('email_notifications', v)}
                  />
                </div>
              </div>

              <Separator />

              {/* Types */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-400 uppercase">Types de notification</h4>
                
                <div className="grid gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Heart className="h-4 w-4 text-red-400" />
                      <Label className="text-white">J'aime</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_likes}
                      onCheckedChange={(v) => updatePreference('notify_likes', v)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageCircle className="h-4 w-4 text-blue-400" />
                      <Label className="text-white">Commentaires</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_comments}
                      onCheckedChange={(v) => updatePreference('notify_comments', v)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-purple-400" />
                      <Label className="text-white">Groupes</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_groups}
                      onCheckedChange={(v) => updatePreference('notify_groups', v)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Gift className="h-4 w-4 text-[#f5a623]" />
                      <Label className="text-white">Parrainage</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_referrals}
                      onCheckedChange={(v) => updatePreference('notify_referrals', v)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Wallet className="h-4 w-4 text-green-400" />
                      <Label className="text-white">Portefeuille</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_wallet}
                      onCheckedChange={(v) => updatePreference('notify_wallet', v)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-purple-400" />
                      <Label className="text-white">Prospects</Label>
                    </div>
                    <Switch
                      checked={preferences.notify_leads}
                      onCheckedChange={(v) => updatePreference('notify_leads', v)}
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-[#f5a623]" />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NotificationCenter;
