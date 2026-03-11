/**
 * AdminGlobalSwitch - Gros Bouton ROUGE de Contrôle Global
 * =========================================================
 * 
 * Interface pour le Master Switch Global du système publicitaire BIONIC.
 * Contrôle ON/OFF/LOCKED de tous les engines publicitaires.
 * 
 * Accès: COPILOT MAÎTRE uniquement
 * Architecture: LEGO V5-ULTIME
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Power, Lock, Unlock, AlertTriangle, CheckCircle, 
  Activity, Zap, Shield, Clock, RefreshCw, Server,
  ToggleLeft, ToggleRight, Radio, CircleDot
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export const AdminGlobalSwitch = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDashboard = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/global-switch/dashboard`);
      const data = await response.json();
      if (data.success) {
        setDashboard(data.dashboard);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      toast.error('Erreur lors du chargement du dashboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  const handleToggle = async (newStatus) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/global-switch/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_status: newStatus,
          reason: `Basculement manuel vers ${newStatus}`,
          admin_user: 'COPILOT_MAITRE'
        })
      });
      const data = await response.json();
      
      if (data.success) {
        toast.success(`🔴 Master Switch → ${newStatus}`);
        fetchDashboard();
      } else {
        toast.error(data.error || 'Erreur lors du basculement');
      }
    } catch (error) {
      console.error('Error toggling switch:', error);
      toast.error('Erreur lors du basculement');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLock = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/global-switch/lock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reason: 'Verrouillage manuel - Mode PRÉ-PRODUCTION',
          admin_user: 'COPILOT_MAITRE'
        })
      });
      const data = await response.json();
      
      if (data.success) {
        toast.success('🔒 Système VERROUILLÉ');
        fetchDashboard();
      }
    } catch (error) {
      toast.error('Erreur lors du verrouillage');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnlock = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/global-switch/unlock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_user: 'COPILOT_MAITRE'
        })
      });
      const data = await response.json();
      
      if (data.success) {
        toast.success('🚀 GO LIVE - Système ACTIVÉ');
        fetchDashboard();
      }
    } catch (error) {
      toast.error('Erreur lors du déverrouillage');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const globalSwitch = dashboard?.global_switch || {};
  const isActive = globalSwitch.is_active;
  const status = globalSwitch.status || 'NOT_INITIALIZED';
  const mode = dashboard?.mode || 'PRÉ-PRODUCTION';

  return (
    <div className="space-y-6" data-testid="admin-global-switch">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Power className="h-8 w-8 text-red-500" />
            Master Switch Global
          </h2>
          <p className="text-gray-400 mt-1">
            Contrôle global du système publicitaire BIONIC
          </p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={fetchDashboard}
          className="border-[#F5A623]/30 text-[#F5A623]"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* GROS BOUTON ROUGE */}
      <Card className="bg-gradient-to-br from-[#0a0a15] to-[#1a0a0a] border-red-500/30">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-white text-xl">
            🔴 GROS BOUTON ROUGE
          </CardTitle>
          <CardDescription className="text-gray-400">
            Contrôle global - Accessible par COPILOT MAÎTRE uniquement
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-6 py-8">
          {/* Status Display */}
          <div className="flex items-center gap-4">
            <Badge 
              variant="outline" 
              className={`text-lg px-4 py-2 ${
                status === 'ON' 
                  ? 'bg-green-500/20 text-green-400 border-green-500' 
                  : status === 'LOCKED'
                    ? 'bg-red-500/20 text-red-400 border-red-500'
                    : 'bg-orange-500/20 text-orange-400 border-orange-500'
              }`}
            >
              {status === 'ON' && <CheckCircle className="h-5 w-5 mr-2" />}
              {status === 'OFF' && <Power className="h-5 w-5 mr-2" />}
              {status === 'LOCKED' && <Lock className="h-5 w-5 mr-2" />}
              {status}
            </Badge>
            <Badge 
              variant="outline" 
              className={`text-lg px-4 py-2 ${
                mode === 'PRODUCTION' 
                  ? 'bg-green-500/20 text-green-400 border-green-500' 
                  : 'bg-yellow-500/20 text-yellow-400 border-yellow-500'
              }`}
            >
              {mode}
            </Badge>
          </div>

          {/* Big Button */}
          <div className="relative">
            <button
              onClick={() => status === 'LOCKED' ? handleUnlock() : handleLock()}
              disabled={actionLoading}
              className={`
                w-48 h-48 rounded-full 
                flex items-center justify-center
                transition-all duration-300 transform
                ${actionLoading ? 'scale-95 opacity-50' : 'hover:scale-105'}
                ${status === 'LOCKED' 
                  ? 'bg-gradient-to-br from-red-600 to-red-800 shadow-[0_0_60px_rgba(239,68,68,0.5)]' 
                  : status === 'ON'
                    ? 'bg-gradient-to-br from-green-600 to-green-800 shadow-[0_0_60px_rgba(34,197,94,0.5)]'
                    : 'bg-gradient-to-br from-orange-600 to-orange-800 shadow-[0_0_60px_rgba(249,115,22,0.5)]'
                }
              `}
              data-testid="master-switch-button"
            >
              {status === 'LOCKED' ? (
                <Lock className="h-24 w-24 text-white" />
              ) : status === 'ON' ? (
                <Power className="h-24 w-24 text-white" />
              ) : (
                <Power className="h-24 w-24 text-white opacity-50" />
              )}
            </button>
            
            {/* Pulse animation */}
            {status === 'LOCKED' && (
              <div className="absolute inset-0 rounded-full bg-red-500/20 animate-ping" />
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-4">
            <Button
              onClick={() => handleToggle('ON')}
              disabled={actionLoading || status === 'ON'}
              className="bg-green-600 hover:bg-green-700 text-white px-6"
              data-testid="switch-on-button"
            >
              <Unlock className="h-4 w-4 mr-2" />
              GO LIVE
            </Button>
            <Button
              onClick={() => handleToggle('OFF')}
              disabled={actionLoading || status === 'OFF'}
              variant="outline"
              className="border-orange-500 text-orange-400 hover:bg-orange-500/20 px-6"
              data-testid="switch-off-button"
            >
              <Power className="h-4 w-4 mr-2" />
              OFF
            </Button>
            <Button
              onClick={handleLock}
              disabled={actionLoading || status === 'LOCKED'}
              className="bg-red-600 hover:bg-red-700 text-white px-6"
              data-testid="switch-lock-button"
            >
              <Lock className="h-4 w-4 mr-2" />
              LOCK
            </Button>
          </div>

          {/* Reason */}
          {globalSwitch.reason && (
            <p className="text-gray-400 text-sm text-center max-w-md">
              {globalSwitch.reason}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Opportunities */}
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Opportunités</p>
                <p className="text-2xl font-bold text-white">
                  {dashboard?.opportunities?.total || 0}
                </p>
              </div>
              <Activity className="h-8 w-8 text-[#F5A623]" />
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
                {dashboard?.opportunities?.active || 0} actives
              </Badge>
              <Badge variant="outline" className="bg-orange-500/10 text-orange-400 border-orange-500/30">
                {dashboard?.opportunities?.paused || 0} pausées
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Deployed Ads */}
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Publicités Déployées</p>
                <p className="text-2xl font-bold text-white">
                  {(dashboard?.deployed_ads?.active || 0) + (dashboard?.deployed_ads?.inactive || 0)}
                </p>
              </div>
              <Radio className="h-8 w-8 text-blue-400" />
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
                {dashboard?.deployed_ads?.active || 0} actives
              </Badge>
              <Badge variant="outline" className="bg-gray-500/10 text-gray-400 border-gray-500/30">
                {dashboard?.deployed_ads?.inactive || 0} inactives
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Slots */}
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Slots Publicitaires</p>
                <p className="text-2xl font-bold text-white">
                  {(dashboard?.slots?.active || 0) + (dashboard?.slots?.paused || 0)}
                </p>
              </div>
              <CircleDot className="h-8 w-8 text-purple-400" />
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
                {dashboard?.slots?.active || 0} actifs
              </Badge>
              <Badge variant="outline" className="bg-orange-500/10 text-orange-400 border-orange-500/30">
                {dashboard?.slots?.paused || 0} pausés
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Controlled Engines */}
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Engines Contrôlés</p>
                <p className="text-2xl font-bold text-white">
                  {dashboard?.controlled_engines || 6}
                </p>
              </div>
              <Server className="h-8 w-8 text-cyan-400" />
            </div>
            <div className="mt-2">
              <Badge 
                variant="outline" 
                className={`${isActive ? 'bg-green-500/10 text-green-400 border-green-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}
              >
                {isActive ? 'Tous Actifs' : 'Tous Désactivés'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controlled Engines List */}
      <Card className="bg-[#0a0a15] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-5 w-5 text-[#F5A623]" />
            Engines Contrôlés par le Master Switch
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { name: 'Affiliate Ad Automation Engine', desc: 'Cycle de vente publicitaire' },
              { name: 'Ad Spaces Engine', desc: '18 espaces publicitaires' },
              { name: 'Ad Slot Manager', desc: 'Attribution emplacements' },
              { name: 'Ad Render Engine', desc: 'Injection publicités' },
              { name: 'Marketing Engine', desc: 'Campagnes marketing' },
              { name: 'Calendar Engine', desc: 'Planification campagnes' }
            ].map((engine, idx) => (
              <div 
                key={idx}
                className={`p-3 rounded-lg border ${
                  isActive 
                    ? 'bg-green-500/5 border-green-500/30' 
                    : 'bg-red-500/5 border-red-500/30'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white text-sm font-medium">{engine.name}</p>
                    <p className="text-gray-500 text-xs">{engine.desc}</p>
                  </div>
                  {isActive ? (
                    <ToggleRight className="h-5 w-5 text-green-400" />
                  ) : (
                    <ToggleLeft className="h-5 w-5 text-red-400" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      {dashboard?.recent_activity && dashboard.recent_activity.length > 0 && (
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-[#F5A623]" />
              Activité Récente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {dashboard.recent_activity.slice(0, 5).map((log, idx) => (
                <div 
                  key={idx}
                  className="flex items-center justify-between p-2 bg-white/5 rounded"
                >
                  <div className="flex items-center gap-3">
                    <Shield className="h-4 w-4 text-[#F5A623]" />
                    <div>
                      <p className="text-white text-sm">{log.action}</p>
                      <p className="text-gray-500 text-xs">Par {log.admin_user}</p>
                    </div>
                  </div>
                  <p className="text-gray-500 text-xs">
                    {new Date(log.timestamp).toLocaleString('fr-CA')}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Warning Banner */}
      <Card className="bg-yellow-500/10 border-yellow-500/30">
        <CardContent className="p-4 flex items-center gap-4">
          <AlertTriangle className="h-8 w-8 text-yellow-400 flex-shrink-0" />
          <div>
            <p className="text-yellow-400 font-medium">Mode PRÉ-PRODUCTION</p>
            <p className="text-gray-400 text-sm">
              Le système publicitaire est actuellement désactivé. Aucune publicité n'est diffusée.
              Activez le Master Switch pour passer en mode PRODUCTION (GO LIVE).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminGlobalSwitch;
