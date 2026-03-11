/**
 * GroupChat - Composant de chat temps réel pour le module GROUPE
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 3.5
 * 
 * Interface de chat avec messages, alertes rapides et partage de position.
 */
import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { 
  MessageSquare, Send, AlertTriangle, MapPin, Eye, Target,
  ThumbsUp, Hand, Navigation, Pause, VolumeX, Coffee,
  ShieldAlert, AlertCircle, Bell, X, ChevronDown, Clock,
  Vibrate, VibrateOff, MoreHorizontal
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Badge } from '../../../components/ui/badge';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { Card, CardContent } from '../../../components/ui/card';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator 
} from '../../../components/ui/dropdown-menu';
import { useGroupeChat, ALERT_TYPES, QUICK_MESSAGES } from '../hooks/useGroupeChat';

// Icon mapping
const ICON_MAP = {
  MessageSquare, AlertTriangle, MapPin, Eye, Target,
  ThumbsUp, Hand, Navigation, Pause, VolumeX, Coffee,
  ShieldAlert, AlertCircle
};

// Get icon component by name
const getIcon = (iconName) => ICON_MAP[iconName] || MessageSquare;

// Message bubble component
const ChatMessage = ({ message, isOwn, userName }) => {
  const { t } = useLanguage();
  const isAlert = message.message_type === 'alert';
  const isQuick = message.message_type === 'quick';
  const isLocation = message.message_type === 'location';
  
  const alertConfig = isAlert ? ALERT_TYPES[message.alert_type] : null;
  
  // Format time
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' });
  };

  // Quick message display
  if (isQuick) {
    const quickId = message.content?.replace('[QUICK:', '').replace(']', '');
    const quickConfig = QUICK_MESSAGES.find(q => q.id === quickId);
    const QuickIcon = quickConfig ? getIcon(quickConfig.icon) : ThumbsUp;
    
    return (
      <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-2`}>
        <div className={`
          inline-flex items-center gap-2 px-3 py-2 rounded-full
          ${isOwn 
            ? 'bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]' 
            : 'bg-[var(--bionic-bg-hover)] text-[var(--bionic-text-primary)]'
          }
        `}>
          <QuickIcon className="h-4 w-4" />
          <span className="text-sm font-medium">
            {quickConfig ? t(quickConfig.textKey) : quickId}
          </span>
        </div>
      </div>
    );
  }

  // Alert message display
  if (isAlert && alertConfig) {
    const AlertIcon = getIcon(alertConfig.icon);
    
    return (
      <div className="mb-3">
        <Card 
          className="border-2"
          style={{ 
            backgroundColor: alertConfig.bgVar,
            borderColor: alertConfig.colorVar
          }}
        >
          <CardContent className="p-3">
            <div className="flex items-start gap-3">
              <div 
                className="p-2 rounded-lg"
                style={{ backgroundColor: `${alertConfig.colorVar}30` }}
              >
                <AlertIcon 
                  className="h-5 w-5" 
                  style={{ color: alertConfig.colorVar }}
                />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span 
                    className="font-bold text-sm"
                    style={{ color: alertConfig.colorVar }}
                  >
                    {t(alertConfig.labelKey)}
                  </span>
                  <span className="text-xs text-[var(--bionic-text-muted)]">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                {!isOwn && (
                  <p className="text-xs text-[var(--bionic-text-secondary)] mt-1">
                    {userName || message.user_name || 'Membre'}
                  </p>
                )}
                {message.content && (
                  <p className="text-sm text-[var(--bionic-text-primary)] mt-2">
                    {message.content}
                  </p>
                )}
                {message.location && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-[var(--bionic-text-secondary)]">
                    <MapPin className="h-3 w-3" />
                    <span>{message.location.lat?.toFixed(5)}, {message.location.lng?.toFixed(5)}</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Location message display
  if (isLocation) {
    return (
      <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-2`}>
        <div className={`
          max-w-[80%] rounded-lg p-3
          ${isOwn 
            ? 'bg-[var(--bionic-blue-muted)] border border-[var(--bionic-blue-primary)]' 
            : 'bg-[var(--bionic-bg-hover)] border border-[var(--bionic-border-secondary)]'
          }
        `}>
          <div className="flex items-center gap-2 mb-1">
            <MapPin className="h-4 w-4 text-[var(--bionic-blue-light)]" />
            <span className="text-sm font-medium text-[var(--bionic-text-primary)]">
              {t('chat_location_shared')}
            </span>
          </div>
          {message.location && (
            <p className="text-xs text-[var(--bionic-text-secondary)]">
              {message.location.lat?.toFixed(5)}, {message.location.lng?.toFixed(5)}
            </p>
          )}
          <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  // Regular text message
  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-2`}>
      <div className={`
        max-w-[80%] rounded-lg px-4 py-2
        ${isOwn 
          ? 'bg-[var(--bionic-gold-primary)] text-[var(--bionic-bg-primary)]' 
          : 'bg-[var(--bionic-bg-hover)] text-[var(--bionic-text-primary)]'
        }
        ${message.pending ? 'opacity-60' : ''}
      `}>
        {!isOwn && (
          <p className={`text-xs font-medium mb-1 ${isOwn ? 'text-[var(--bionic-bg-primary)]' : 'text-[var(--bionic-gold-primary)]'}`}>
            {userName || message.user_name || 'Membre'}
          </p>
        )}
        <p className="text-sm">{message.content}</p>
        <p className={`text-xs mt-1 ${isOwn ? 'text-[var(--bionic-bg-secondary)]' : 'text-[var(--bionic-text-muted)]'}`}>
          {formatTime(message.timestamp)}
          {message.pending && ' • En attente...'}
        </p>
      </div>
    </div>
  );
};

// Quick actions bar
const QuickActionsBar = ({ onQuickMessage, onAlert, disabled }) => {
  const { t } = useLanguage();
  
  return (
    <div className="flex items-center gap-1 p-2 border-t border-[var(--bionic-border-secondary)] bg-[var(--bionic-bg-hover)]/50 overflow-x-auto">
      {QUICK_MESSAGES.slice(0, 4).map(quick => {
        const QuickIcon = getIcon(quick.icon);
        return (
          <Button
            key={quick.id}
            variant="ghost"
            size="sm"
            onClick={() => onQuickMessage(quick.id)}
            disabled={disabled}
            className="flex-shrink-0 h-8 px-3 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-muted)]"
          >
            <QuickIcon className="h-4 w-4 mr-1" />
            <span className="text-xs">{t(quick.textKey)}</span>
          </Button>
        );
      })}
      
      <div className="w-px h-6 bg-[var(--bionic-border-secondary)] mx-1" />
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            disabled={disabled}
            className="flex-shrink-0 h-8 px-3 text-[var(--bionic-red-primary)] hover:bg-[var(--bionic-red-muted)]"
          >
            <AlertTriangle className="h-4 w-4 mr-1" />
            <span className="text-xs">{t('chat_send_alert')}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent 
          align="end" 
          className="w-48 bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]"
        >
          {Object.values(ALERT_TYPES).map(alert => {
            const AlertIcon = getIcon(alert.icon);
            return (
              <DropdownMenuItem
                key={alert.id}
                onClick={() => onAlert(alert.id)}
                className="cursor-pointer"
                style={{ color: alert.colorVar }}
              >
                <AlertIcon className="h-4 w-4 mr-2" />
                {t(alert.labelKey)}
              </DropdownMenuItem>
            );
          })}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

// Main GroupChat component
export const GroupChat = ({ 
  userId, 
  groupId,
  userName = null,
  memberNames = {},
  compact = false,
  onClose = null,
  maxHeight = '400px'
}) => {
  const { t } = useLanguage();
  const [inputValue, setInputValue] = useState('');
  const [showScrollButton, setShowScrollButton] = useState(false);
  const inputRef = useRef(null);
  const scrollRef = useRef(null);

  const {
    messages,
    unreadCount,
    loading,
    sending,
    vibrationEnabled,
    sendMessage,
    sendQuickMessage,
    sendAlert,
    markAsRead,
    scrollToBottom,
    toggleVibration,
    messagesEndRef
  } = useGroupeChat(userId, groupId, {
    autoLoad: true,
    messageLimit: 50
  });

  // Handle send message
  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || sending) return;
    
    await sendMessage(inputValue);
    setInputValue('');
    inputRef.current?.focus();
    
    // Scroll to bottom after sending
    setTimeout(scrollToBottom, 100);
  }, [inputValue, sending, sendMessage, scrollToBottom]);

  // Handle key press
  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  // Handle scroll
  const handleScroll = useCallback((e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setShowScrollButton(!isNearBottom);
  }, []);

  // Mark as read on focus
  useEffect(() => {
    if (unreadCount > 0) {
      markAsRead();
    }
  }, [messages.length, unreadCount, markAsRead]);

  // Auto-scroll on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages.length, scrollToBottom]);

  // Get member name
  const getMemberName = (memberId) => {
    return memberNames[memberId] || null;
  };

  // Compact mode
  if (compact) {
    return (
      <div 
        className="bg-[var(--bionic-bg-card)] rounded-lg border border-[var(--bionic-border-primary)]"
        data-testid="groupe-chat-compact"
      >
        <div className="flex items-center justify-between p-3 border-b border-[var(--bionic-border-secondary)]">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-[var(--bionic-gold-primary)]" />
            <span className="text-sm font-medium text-[var(--bionic-text-primary)]">
              {t('chat_title')}
            </span>
            {unreadCount > 0 && (
              <Badge className="bg-[var(--bionic-red-primary)] text-white text-xs h-5 w-5 p-0 flex items-center justify-center">
                {unreadCount}
              </Badge>
            )}
          </div>
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-6 w-6 text-[var(--bionic-text-secondary)]"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        
        <ScrollArea 
          className="h-[200px] p-3"
          onScroll={handleScroll}
          ref={scrollRef}
        >
          {messages.length === 0 ? (
            <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">{t('chat_no_messages')}</p>
            </div>
          ) : (
            messages.map(msg => (
              <ChatMessage
                key={msg.id}
                message={msg}
                isOwn={msg.user_id === userId}
                userName={getMemberName(msg.user_id)}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </ScrollArea>
        
        <div className="p-2 border-t border-[var(--bionic-border-secondary)]">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chat_placeholder')}
              disabled={sending}
              className="flex-1 h-9 bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)] text-[var(--bionic-text-primary)]"
            />
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || sending}
              size="icon"
              className="h-9 w-9 bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-dark)] text-[var(--bionic-bg-primary)]"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Full mode
  return (
    <div 
      className="flex flex-col bg-[var(--bionic-bg-card)] rounded-lg border border-[var(--bionic-border-primary)]"
      style={{ maxHeight }}
      data-testid="groupe-chat"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--bionic-border-secondary)]">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
          <div>
            <h3 className="text-[var(--bionic-text-primary)] font-medium">
              {t('chat_title')}
            </h3>
            <p className="text-xs text-[var(--bionic-text-secondary)]">
              {messages.length} {t('chat_messages_count')}
            </p>
          </div>
          {unreadCount > 0 && (
            <Badge className="bg-[var(--bionic-red-primary)] text-white">
              {unreadCount} {t('chat_unread')}
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => toggleVibration(!vibrationEnabled)}
            className={`h-8 w-8 ${vibrationEnabled ? 'text-[var(--bionic-gold-primary)]' : 'text-[var(--bionic-text-secondary)]'}`}
            title={vibrationEnabled ? t('chat_vibration_on') : t('chat_vibration_off')}
          >
            {vibrationEnabled ? <Vibrate className="h-4 w-4" /> : <VibrateOff className="h-4 w-4" />}
          </Button>
          
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-red-primary)]"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Messages area */}
      <ScrollArea 
        className="flex-1 p-4 relative"
        style={{ maxHeight: `calc(${maxHeight} - 180px)` }}
        onScroll={handleScroll}
        ref={scrollRef}
      >
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-[var(--bionic-gold-primary)] border-t-transparent rounded-full" />
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-8 text-[var(--bionic-text-secondary)]">
            <MessageSquare className="h-10 w-10 mx-auto mb-3 opacity-50" />
            <p className="text-sm">{t('chat_no_messages')}</p>
            <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
              {t('chat_start_conversation')}
            </p>
          </div>
        ) : (
          <>
            {messages.map(msg => (
              <ChatMessage
                key={msg.id}
                message={msg}
                isOwn={msg.user_id === userId}
                userName={getMemberName(msg.user_id)}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
        
        {/* Scroll to bottom button */}
        {showScrollButton && (
          <Button
            variant="secondary"
            size="icon"
            onClick={scrollToBottom}
            className="absolute bottom-2 right-2 h-8 w-8 rounded-full bg-[var(--bionic-gold-primary)] text-[var(--bionic-bg-primary)] shadow-lg"
          >
            <ChevronDown className="h-4 w-4" />
          </Button>
        )}
      </ScrollArea>

      {/* Quick actions */}
      <QuickActionsBar
        onQuickMessage={sendQuickMessage}
        onAlert={sendAlert}
        disabled={sending}
      />

      {/* Input area */}
      <div className="p-4 border-t border-[var(--bionic-border-secondary)]">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t('chat_placeholder')}
            disabled={sending}
            className="flex-1 bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)] text-[var(--bionic-text-primary)] placeholder:text-[var(--bionic-text-muted)]"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || sending}
            className="bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-dark)] text-[var(--bionic-bg-primary)]"
          >
            <Send className="h-4 w-4 mr-2" />
            {t('chat_send')}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default GroupChat;
