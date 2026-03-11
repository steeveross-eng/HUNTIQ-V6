/**
 * GroupeTab - Onglet principal GROUPE pour Carte et Territoire
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 1
 * 
 * Onglet conteneur pour toutes les fonctionnalités collaboratives.
 */
import React, { useState, useCallback } from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Users, Radio, Eye, EyeOff, Settings, ChevronDown } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Switch } from '../../../components/ui/switch';
import { Badge } from '../../../components/ui/badge';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator 
} from '../../../components/ui/dropdown-menu';
import { GroupePanel } from './GroupePanel';

export const GroupeTab = ({ 
  groupId = null,
  userId = null,
  userName = null,
  onGroupChange = null,
  compact = false
}) => {
  const { t } = useLanguage();
  const [isShareEnabled, setIsShareEnabled] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const [activeMembers, setActiveMembers] = useState(0);
  const [totalMembers, setTotalMembers] = useState(0);

  // Toggle position sharing
  const handleShareToggle = useCallback((enabled) => {
    setIsShareEnabled(enabled);
    // Future: API call to start/stop sharing
  }, []);

  // Handle panel visibility
  const handleOpenPanel = useCallback(() => {
    setShowPanel(true);
  }, []);

  const handleClosePanel = useCallback(() => {
    setShowPanel(false);
  }, []);

  // Compact mode (for toolbar integration)
  if (compact) {
    return (
      <div className="flex items-center gap-2" data-testid="groupe-tab-compact">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="outline" 
              size="sm"
              className="border-[var(--bionic-border-primary)] bg-[var(--bionic-bg-card)] text-[var(--bionic-text-primary)] hover:bg-[var(--bionic-bg-hover)] hover:border-[var(--bionic-gold-primary)]"
            >
              <Users className="h-4 w-4 mr-2 text-[var(--bionic-gold-primary)]" />
              {t('groupe_tab_title')}
              {activeMembers > 0 && (
                <Badge 
                  variant="secondary" 
                  className="ml-2 bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)]"
                >
                  {activeMembers}
                </Badge>
              )}
              <ChevronDown className="h-3 w-3 ml-1 text-[var(--bionic-text-secondary)]" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent 
            align="end" 
            className="w-56 bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]"
          >
            <div className="px-3 py-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--bionic-text-primary)]">
                  {t('groupe_share_position')}
                </span>
                <Switch
                  checked={isShareEnabled}
                  onCheckedChange={handleShareToggle}
                  className="data-[state=checked]:bg-[var(--bionic-green-primary)]"
                />
              </div>
            </div>
            <DropdownMenuSeparator className="bg-[var(--bionic-border-secondary)]" />
            <DropdownMenuItem 
              onClick={handleOpenPanel}
              className="text-[var(--bionic-text-primary)] focus:bg-[var(--bionic-bg-hover)] cursor-pointer"
            >
              <Users className="h-4 w-4 mr-2 text-[var(--bionic-gold-primary)]" />
              {t('groupe_members_active')} ({activeMembers}/{totalMembers})
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={handleOpenPanel}
              className="text-[var(--bionic-text-primary)] focus:bg-[var(--bionic-bg-hover)] cursor-pointer"
            >
              <Radio className="h-4 w-4 mr-2 text-[var(--bionic-blue-light)]" />
              {t('groupe_activity_feed')}
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-[var(--bionic-border-secondary)]" />
            <DropdownMenuItem 
              onClick={handleOpenPanel}
              className="text-[var(--bionic-text-primary)] focus:bg-[var(--bionic-bg-hover)] cursor-pointer"
            >
              <Settings className="h-4 w-4 mr-2 text-[var(--bionic-text-secondary)]" />
              {t('groupe_settings')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Panel Modal */}
        {showPanel && (
          <GroupePanel
            groupId={groupId}
            userId={userId}
            userName={userName}
            isShareEnabled={isShareEnabled}
            onShareToggle={handleShareToggle}
            onClose={handleClosePanel}
          />
        )}
      </div>
    );
  }

  // Full mode (for tab content)
  return (
    <div className="space-y-4" data-testid="groupe-tab">
      {/* Header with sharing toggle */}
      <div className="flex items-center justify-between p-4 bg-[var(--bionic-bg-card)] rounded-lg border border-[var(--bionic-border-primary)]">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[var(--bionic-gold-muted)]">
            <Users className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
          </div>
          <div>
            <h3 className="text-[var(--bionic-text-primary)] font-medium">
              {t('groupe_tab_title')}
            </h3>
            <p className="text-xs text-[var(--bionic-text-secondary)]">
              {activeMembers}/{totalMembers} {t('groupe_members_active').toLowerCase()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Share toggle */}
          <div className="flex items-center gap-2">
            {isShareEnabled ? (
              <Eye className="h-4 w-4 text-[var(--bionic-green-primary)]" />
            ) : (
              <EyeOff className="h-4 w-4 text-[var(--bionic-text-secondary)]" />
            )}
            <span className="text-sm text-[var(--bionic-text-secondary)]">
              {t('groupe_share_position')}
            </span>
            <Switch
              checked={isShareEnabled}
              onCheckedChange={handleShareToggle}
              className="data-[state=checked]:bg-[var(--bionic-green-primary)]"
            />
          </div>
          
          {/* Status indicator */}
          {isShareEnabled && (
            <Badge className="bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)] border-0">
              <Radio className="h-3 w-3 mr-1 animate-pulse" />
              {t('groupe_status_live')}
            </Badge>
          )}
        </div>
      </div>

      {/* Main Panel Content */}
      <GroupePanel
        groupId={groupId}
        userId={userId}
        userName={userName}
        isShareEnabled={isShareEnabled}
        onShareToggle={handleShareToggle}
        embedded={true}
      />
    </div>
  );
};

export default GroupeTab;
