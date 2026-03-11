/**
 * AdminMarketingControls - V5-ULTIME Administration Premium
 * =========================================================
 * 
 * Module de contrôle global ON/OFF pour fonctionnalités marketing.
 * SYNCHRONISÉ avec le Global Master Switch.
 * Architecture LEGO V5 - Module isolé.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Settings, Power, PowerOff, RefreshCw, Megaphone,
  Mail, TrendingUp, Gift, Zap, Layout, Users, TestTube,
  AlertTriangle, CheckCircle, Sparkles, Clock, Lock, Shield
} from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const AdminMarketingControls = () => {
  const [loading, setLoading] = useState(true);
  const [controls, setControls] = useState([]);
  const [stats, setStats] = useState({ total: 0, enabled: 0, disabled: 0 });
  const [updating, setUpdating] = useState(null);
  const [globalSwitch, setGlobalSwitch] = useState(null);

  // Fetch Global Master Switch status
  const fetchGlobalSwitch = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/global-switch/status`);
      const data = await response.json();
      if (data.success) {
        setGlobalSwitch(data.global_switch);
      }
    } catch (error) {
      console.error('Error fetching global switch:', error);
    }
  }, []);

  useEffect(() => {
    loadControls();
    fetchGlobalSwitch();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchGlobalSwitch, 30000);
    return () => clearInterval(interval);
  }, [fetchGlobalSwitch]);

  const loadControls = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/marketing-controls`);
      const data = await response.json();
      if (data.success) {
        setControls(data.controls || []);
        setStats({
          total: data.total || 0,
          enabled: data.enabled || 0,
          disabled: data.disabled || 0
        });
      }
    } catch (error) {
      console.error('Error loading controls:', error);
    }
    setLoading(false);
  };

  // Check if system is locked
  const isSystemLocked = globalSwitch?.status === 'LOCKED' || globalSwitch?.status === 'OFF';

  const toggleControl = async (controlId, currentEnabled) => {
    // Block if Global Master Switch is LOCKED
    if (isSystemLocked) {
      toast.error('🔒 Système verrouillé - Modifications impossibles en mode PRÉ-PRODUCTION');
      return;
    }

    setUpdating(controlId);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/marketing-controls/${controlId}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(!currentEnabled)
      });
      const data = await response.json();
      if (data.success) {
        // Mettre à jour localement
        setControls(prev => prev.map(c => 
          c.id === controlId ? { ...c, enabled: !currentEnabled } : c
        ));
        setStats(prev => ({
          ...prev,
          enabled: prev.enabled + (currentEnabled ? -1 : 1),
          disabled: prev.disabled + (currentEnabled ? 1 : -1)
        }));
        toast.success(`Contrôle ${!currentEnabled ? 'activé' : 'désactivé'}`);
      }
    } catch (error) {
      console.error('Error toggling control:', error);
      toast.error('Erreur lors de la modification');
    }
    setUpdating(null);
  };

  const resetToDefaults = async () => {
    if (isSystemLocked) {
      toast.error('🔒 Système verrouillé - Réinitialisation impossible en mode PRÉ-PRODUCTION');
      return;
    }
    if (!window.confirm('Réinitialiser tous les contrôles aux valeurs par défaut ?')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/marketing-controls/reset`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        await loadControls();
        toast.success('Contrôles réinitialisés');
      }
    } catch (error) {
      console.error('Error resetting:', error);
    }
  };

  const bulkToggle = async (enabled) => {
    if (isSystemLocked) {
      toast.error('🔒 Système verrouillé - Modifications en lot impossibles en mode PRÉ-PRODUCTION');
      return;
    }

    const action = enabled ? 'activer' : 'désactiver';
    if (!window.confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} tous les contrôles marketing ?`)) return;
    
    setLoading(true);
    try {
      const controlIds = controls.map(c => c.id);
      const response = await fetch(`${API_BASE}/api/v1/admin/marketing-controls/bulk-toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ control_ids: controlIds, enabled })
      });
      const data = await response.json();
      if (data.success) {
        await loadControls();
        toast.success(`Tous les contrôles ${enabled ? 'activés' : 'désactivés'}`);
      }
    } catch (error) {
      console.error('Error bulk toggling:', error);
    }
  };

  const getControlIcon = (controlId) => {
    const icons = {
      promotions: Gift,
      campaigns: Mail,
      upsells: TrendingUp,
      popups: Layout,
      banners: Megaphone,
      seasonal_themes: Sparkles,
      referral_program: Users,
      ab_testing: TestTube
    };
    const Icon = icons[controlId] || Settings;
    return <Icon className="h-5 w-5" />;
  };

  const getCategoryBadge = (category) => {
    const styles = {
      sales: 'bg-green-500/20 text-green-400 border-green-500/30',
      outreach: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      capture: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      display: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      growth: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      optimization: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
    };
    return styles[category] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div data-testid="admin-marketing-controls" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Marketing Controls</h2>
            <p className="text-gray-400 text-sm">Contrôle global ON/OFF des fonctionnalités marketing</p>
          </div>
        </div>
        <Badge className="bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30 px-4 py-2">
          LEGO V5 Isolé
        </Badge>
      </div>

      {/* Global Master Switch Sync Banner */}
      {globalSwitch && (
        <Card className={`p-4 border ${
          isSystemLocked 
            ? 'bg-red-500/10 border-red-500/30' 
            : 'bg-green-500/10 border-green-500/30'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isSystemLocked ? (
                <Lock className="h-6 w-6 text-red-400" />
              ) : (
                <Shield className="h-6 w-6 text-green-400" />
              )}
              <div>
                <p className={`font-medium ${isSystemLocked ? 'text-red-400' : 'text-green-400'}`}>
                  Global Master Switch: {globalSwitch.status}
                </p>
                <p className="text-gray-400 text-sm">
                  {isSystemLocked 
                    ? '🔒 Mode PRÉ-PRODUCTION - Toutes les modifications sont bloquées'
                    : '✅ Mode PRODUCTION - Modifications autorisées'
                  }
                </p>
              </div>
            </div>
            <Badge 
              variant="outline"
              className={isSystemLocked 
                ? 'bg-red-500/20 text-red-400 border-red-500' 
                : 'bg-green-500/20 text-green-400 border-green-500'
              }
            >
              {isSystemLocked ? 'VERROUILLÉ' : 'ACTIF'}
            </Badge>
          </div>
        </Card>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Contrôles</p>
              <p className="text-2xl font-bold text-white">{stats.total}</p>
            </div>
            <Settings className="h-8 w-8 text-[#F5A623]" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-green-500/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Activés</p>
              <p className="text-2xl font-bold text-green-400">{stats.enabled}</p>
            </div>
            <Power className="h-8 w-8 text-green-400" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-red-500/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Désactivés</p>
              <p className="text-2xl font-bold text-red-400">{stats.disabled}</p>
            </div>
            <PowerOff className="h-8 w-8 text-red-400" />
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <Button 
          onClick={() => bulkToggle(true)}
          disabled={isSystemLocked}
          className={`${isSystemLocked 
            ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
            : 'bg-green-500/20 text-green-400 hover:bg-green-500/30 border border-green-500/30'
          }`}
        >
          {isSystemLocked && <Lock className="h-4 w-4 mr-2" />}
          <Power className="h-4 w-4 mr-2" />
          Tout activer
        </Button>
        <Button 
          onClick={() => bulkToggle(false)}
          disabled={isSystemLocked}
          className={`${isSystemLocked 
            ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
            : 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30'
          }`}
        >
          {isSystemLocked && <Lock className="h-4 w-4 mr-2" />}
          <PowerOff className="h-4 w-4 mr-2" />
          Tout désactiver
        </Button>
        <Button 
          onClick={resetToDefaults}
          disabled={isSystemLocked}
          variant="outline"
          className={`${isSystemLocked 
            ? 'border-gray-700 text-gray-500 cursor-not-allowed' 
            : 'border-gray-600 text-gray-400 hover:text-white'
          }`}
        >
          {isSystemLocked && <Lock className="h-4 w-4 mr-2" />}
          <RefreshCw className="h-4 w-4 mr-2" />
          Réinitialiser
        </Button>
        <Button 
          onClick={() => { loadControls(); fetchGlobalSwitch(); }}
          variant="outline"
          className="border-[#F5A623]/30 text-[#F5A623]"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Controls List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {controls.map((control) => (
            <Card 
              key={control.id}
              data-testid={`control-${control.id}`}
              className={`bg-[#0f0f1a] border p-4 transition-all ${
                isSystemLocked
                  ? 'border-gray-700 opacity-60'
                  : control.enabled 
                    ? 'border-green-500/30 hover:border-green-500/50' 
                    : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${
                    isSystemLocked 
                      ? 'bg-gray-800'
                      : control.enabled ? 'bg-green-500/20' : 'bg-gray-800'
                  }`}>
                    <span className={isSystemLocked ? 'text-gray-500' : control.enabled ? 'text-green-400' : 'text-gray-500'}>
                      {getControlIcon(control.id)}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-white font-semibold">{control.name_fr}</p>
                      <Badge className={`${getCategoryBadge(control.category)} border text-xs`}>
                        {control.category}
                      </Badge>
                    </div>
                    <p className="text-gray-400 text-sm">{control.description_fr}</p>
                    <div className="flex items-center gap-2 mt-2">
                      {isSystemLocked ? (
                        <span className="flex items-center gap-1 text-red-400 text-xs">
                          <Lock className="h-3 w-3" />
                          Verrouillé
                        </span>
                      ) : control.enabled ? (
                        <span className="flex items-center gap-1 text-green-400 text-xs">
                          <CheckCircle className="h-3 w-3" />
                          Actif
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-gray-500 text-xs">
                          <PowerOff className="h-3 w-3" />
                          Inactif
                        </span>
                      )}
                      <span className="text-gray-600 text-xs">
                        Priorité: {control.priority}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center">
                  <Switch
                    checked={control.enabled}
                    onCheckedChange={() => toggleControl(control.id, control.enabled)}
                    disabled={updating === control.id || isSystemLocked}
                    className={control.enabled && !isSystemLocked ? 'bg-green-500' : ''}
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5" />
          <div>
            <p className="text-white font-medium">Synchronisation Global Master Switch</p>
            <p className="text-gray-400 text-sm mt-1">
              Ce module est synchronisé avec le Global Master Switch (🔴 Gros Bouton Rouge).
              En mode PRÉ-PRODUCTION (LOCKED), toutes les modifications sont bloquées.
              Les contrôles ne seront modifiables qu'après le signal GO LIVE.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export { AdminMarketingControls };
export default AdminMarketingControls;
