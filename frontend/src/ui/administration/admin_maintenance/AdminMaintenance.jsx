/**
 * AdminMaintenance - V5-ULTIME Administration Premium
 * ====================================================
 * 
 * Module de gestion de l'infrastructure et maintenance.
 * Fonctionnalités:
 * - Mode maintenance (toggle)
 * - Règles d'accès
 * - IPs autorisées
 * - Maintenances planifiées
 * - Logs maintenance
 * 
 * Phase 3 Migration - Module isolé LEGO.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Settings, Shield, Power, Globe, Clock, Plus, Edit, Trash2, 
  CheckCircle, XCircle, AlertTriangle, RefreshCw, Calendar,
  Loader2, X, Lock, Unlock, Eye
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminMaintenance = () => {
  // State
  const [activeTab, setActiveTab] = useState('status');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Maintenance status
  const [maintenanceStatus, setMaintenanceStatus] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  
  // Access rules
  const [accessRules, setAccessRules] = useState([]);
  const [newRule, setNewRule] = useState({ name: '', type: 'ip', action: 'allow', condition: {}, priority: 100 });
  const [showNewRuleForm, setShowNewRuleForm] = useState(false);
  
  // Allowed IPs
  const [allowedIps, setAllowedIps] = useState([]);
  const [newIp, setNewIp] = useState({ ip: '', label: '' });
  
  // Scheduled maintenance
  const [scheduledMaintenances, setScheduledMaintenances] = useState([]);
  const [newSchedule, setNewSchedule] = useState({ title: '', description: '', start_time: '', end_time: '' });
  const [showNewScheduleForm, setShowNewScheduleForm] = useState(false);
  
  // Logs
  const [maintenanceLogs, setMaintenanceLogs] = useState([]);

  // ============ API CALLS ============
  const fetchMaintenanceStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/status`);
      const data = await response.json();
      if (data.success) {
        setMaintenanceStatus(data.maintenance);
      }
    } catch (err) {
      setError('Erreur lors du chargement du statut');
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/system-status`);
      const data = await response.json();
      if (data.success) {
        setSystemStatus(data.status);
      }
    } catch (err) {
      console.error('Error fetching system status:', err);
    }
  };

  const toggleMaintenanceMode = async (enabled) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/toggle?enabled=${enabled}`, {
        method: 'PUT'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        fetchMaintenanceStatus();
        fetchSystemStatus();
      }
    } catch (err) {
      setError('Erreur lors du changement de mode');
    }
  };

  const fetchAccessRules = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/access-rules`);
      const data = await response.json();
      if (data.success) {
        setAccessRules(data.rules || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des règles');
    } finally {
      setLoading(false);
    }
  };

  const createAccessRule = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/access-rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newRule)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Règle créée');
        setShowNewRuleForm(false);
        setNewRule({ name: '', type: 'ip', action: 'allow', condition: {}, priority: 100 });
        fetchAccessRules();
      }
    } catch (err) {
      setError('Erreur lors de la création');
    }
  };

  const toggleAccessRule = async (ruleId, enabled) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/access-rules/${ruleId}/toggle?enabled=${enabled}`, {
        method: 'PUT'
      });
      const data = await response.json();
      if (data.success) {
        fetchAccessRules();
      }
    } catch (err) {
      setError('Erreur lors du toggle');
    }
  };

  const deleteAccessRule = async (ruleId) => {
    if (!window.confirm('Supprimer cette règle ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/access-rules/${ruleId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Règle supprimée');
        fetchAccessRules();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const fetchAllowedIps = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/allowed-ips`);
      const data = await response.json();
      if (data.success) {
        setAllowedIps(data.allowed_ips || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des IPs');
    }
  };

  const addAllowedIp = async () => {
    if (!newIp.ip) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/allowed-ips?ip=${newIp.ip}&label=${newIp.label}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('IP ajoutée');
        setNewIp({ ip: '', label: '' });
        fetchAllowedIps();
      }
    } catch (err) {
      setError('Erreur lors de l\'ajout');
    }
  };

  const removeAllowedIp = async (ip) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/allowed-ips/${encodeURIComponent(ip)}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('IP retirée');
        fetchAllowedIps();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const fetchScheduledMaintenances = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/scheduled`);
      const data = await response.json();
      if (data.success) {
        setScheduledMaintenances(data.schedules || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const createScheduledMaintenance = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/scheduled`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSchedule)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Maintenance planifiée');
        setShowNewScheduleForm(false);
        setNewSchedule({ title: '', description: '', start_time: '', end_time: '' });
        fetchScheduledMaintenances();
      }
    } catch (err) {
      setError('Erreur lors de la planification');
    }
  };

  const deleteScheduledMaintenance = async (scheduleId) => {
    if (!window.confirm('Supprimer cette planification ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/scheduled/${scheduleId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Planification supprimée');
        fetchScheduledMaintenances();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const fetchMaintenanceLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/maintenance/logs`);
      const data = await response.json();
      if (data.success) {
        setMaintenanceLogs(data.logs || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des logs');
    } finally {
      setLoading(false);
    }
  };

  // ============ EFFECTS ============
  useEffect(() => {
    if (activeTab === 'status') {
      fetchMaintenanceStatus();
      fetchSystemStatus();
    } else if (activeTab === 'rules') {
      fetchAccessRules();
    } else if (activeTab === 'ips') {
      fetchAllowedIps();
    } else if (activeTab === 'scheduled') {
      fetchScheduledMaintenances();
    } else if (activeTab === 'logs') {
      fetchMaintenanceLogs();
    }
  }, [activeTab]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  // ============ HELPERS ============
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString('fr-CA');
  };

  // ============ RENDER ============
  return (
    <div data-testid="admin-maintenance-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Settings className="h-6 w-6 text-[#F5A623]" />
            Maintenance & Infrastructure
          </h2>
          <p className="text-gray-400 text-sm">Contrôle d'accès, mode maintenance, planification</p>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg flex justify-between items-center">
          <span className="flex items-center gap-2"><XCircle className="h-4 w-4" />{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}><X className="h-4 w-4" /></Button>
        </div>
      )}
      {success && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-3 rounded-lg flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />{success}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#F5A623]/20 pb-4 flex-wrap">
        {[
          { id: 'status', label: 'Statut', icon: Power },
          { id: 'rules', label: 'Règles d\'accès', icon: Shield },
          { id: 'ips', label: 'IPs Autorisées', icon: Globe },
          { id: 'scheduled', label: 'Planification', icon: Calendar },
          { id: 'logs', label: 'Logs', icon: Eye }
        ].map(tab => (
          <Button
            key={tab.id}
            data-testid={`maintenance-tab-${tab.id}`}
            variant={activeTab === tab.id ? 'default' : 'ghost'}
            onClick={() => setActiveTab(tab.id)}
            className={activeTab === tab.id ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      )}

      {/* Status Tab */}
      {!loading && activeTab === 'status' && maintenanceStatus && (
        <div className="space-y-6">
          {/* Main Toggle Card */}
          <Card className={`bg-[#0a0a15] border-2 ${maintenanceStatus.enabled ? 'border-red-500/50' : 'border-green-500/50'}`}>
            <CardContent className="py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {maintenanceStatus.enabled ? (
                    <div className="p-4 bg-red-500/20 rounded-full">
                      <Lock className="h-8 w-8 text-red-400" />
                    </div>
                  ) : (
                    <div className="p-4 bg-green-500/20 rounded-full">
                      <Unlock className="h-8 w-8 text-green-400" />
                    </div>
                  )}
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Mode Maintenance: {maintenanceStatus.enabled ? 'ACTIVÉ' : 'DÉSACTIVÉ'}
                    </h3>
                    <p className="text-gray-400">{maintenanceStatus.message}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Switch
                    checked={maintenanceStatus.enabled}
                    onCheckedChange={toggleMaintenanceMode}
                  />
                  <span className={maintenanceStatus.enabled ? 'text-red-400' : 'text-green-400'}>
                    {maintenanceStatus.enabled ? 'ON' : 'OFF'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Status Cards */}
          {systemStatus && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-[#0a0a15] border-[#F5A623]/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-gray-400">Règles Actives</CardDescription>
                  <CardTitle className="text-2xl text-white">
                    {systemStatus.access_rules?.active || 0} / {systemStatus.access_rules?.total || 0}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="bg-[#0a0a15] border-purple-500/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-gray-400">Maintenances Planifiées</CardDescription>
                  <CardTitle className="text-2xl text-purple-400">
                    {systemStatus.scheduled_maintenances || 0}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="bg-[#0a0a15] border-blue-500/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-gray-400">Dernière Vérification</CardDescription>
                  <CardTitle className="text-lg text-blue-400">
                    {formatDate(systemStatus.last_check)}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className={`bg-[#0a0a15] ${maintenanceStatus.enabled ? 'border-red-500/20' : 'border-green-500/20'}`}>
                <CardHeader className="pb-2">
                  <CardDescription className="text-gray-400">Statut Site</CardDescription>
                  <CardTitle className={`text-2xl ${maintenanceStatus.enabled ? 'text-red-400' : 'text-green-400'}`}>
                    {maintenanceStatus.enabled ? 'FERMÉ' : 'OUVERT'}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Rules Tab */}
      {!loading && activeTab === 'rules' && (
        <div className="space-y-4">
          <Button
            data-testid="btn-new-rule"
            onClick={() => setShowNewRuleForm(!showNewRuleForm)}
            className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle Règle
          </Button>

          {showNewRuleForm && (
            <Card className="bg-[#0a0a15] border-[#F5A623]/20">
              <CardContent className="pt-4 space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <Input
                    placeholder="Nom de la règle"
                    value={newRule.name}
                    onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                    className="bg-[#050510] border-[#F5A623]/30 text-white"
                  />
                  <select
                    value={newRule.type}
                    onChange={(e) => setNewRule({ ...newRule, type: e.target.value })}
                    className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
                  >
                    <option value="ip">IP</option>
                    <option value="role">Rôle</option>
                    <option value="time">Horaire</option>
                    <option value="geo">Géo</option>
                  </select>
                  <select
                    value={newRule.action}
                    onChange={(e) => setNewRule({ ...newRule, action: e.target.value })}
                    className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
                  >
                    <option value="allow">Autoriser</option>
                    <option value="deny">Bloquer</option>
                    <option value="redirect">Rediriger</option>
                  </select>
                </div>
                <div className="flex gap-2">
                  <Button onClick={createAccessRule} className="bg-[#F5A623] text-black">Créer</Button>
                  <Button variant="ghost" onClick={() => setShowNewRuleForm(false)} className="text-gray-400">Annuler</Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-3">
            {accessRules.map((rule) => (
              <Card key={rule.id} data-testid={`rule-item-${rule.id}`} className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Shield className={`h-5 w-5 ${rule.enabled ? 'text-green-400' : 'text-gray-500'}`} />
                    <div>
                      <p className="text-white font-medium">{rule.name}</p>
                      <p className="text-gray-500 text-sm">Type: {rule.type} | Action: {rule.action} | Priorité: {rule.priority}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Switch checked={rule.enabled} onCheckedChange={(checked) => toggleAccessRule(rule.id, checked)} />
                    <Button size="sm" variant="ghost" onClick={() => deleteAccessRule(rule.id)} className="text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            {accessRules.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucune règle d'accès configurée.
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* IPs Tab */}
      {!loading && activeTab === 'ips' && (
        <div className="space-y-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardContent className="pt-4">
              <p className="text-gray-400 text-sm mb-4">IPs autorisées à accéder au site en mode maintenance :</p>
              <div className="flex gap-4">
                <Input
                  placeholder="Adresse IP (ex: 192.168.1.1)"
                  value={newIp.ip}
                  onChange={(e) => setNewIp({ ...newIp, ip: e.target.value })}
                  className="bg-[#050510] border-[#F5A623]/30 text-white flex-1"
                />
                <Input
                  placeholder="Label (optionnel)"
                  value={newIp.label}
                  onChange={(e) => setNewIp({ ...newIp, label: e.target.value })}
                  className="bg-[#050510] border-[#F5A623]/30 text-white w-48"
                />
                <Button onClick={addAllowedIp} className="bg-[#F5A623] text-black">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-3">
            {allowedIps.map((item, idx) => (
              <Card key={idx} className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Globe className="h-5 w-5 text-blue-400" />
                    <div>
                      <p className="text-white font-mono">{item.ip}</p>
                      {item.label && <p className="text-gray-500 text-sm">{item.label}</p>}
                    </div>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => removeAllowedIp(item.ip)} className="text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
            {allowedIps.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucune IP autorisée. Ajoutez des IPs pour permettre l'accès en mode maintenance.
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Scheduled Tab */}
      {!loading && activeTab === 'scheduled' && (
        <div className="space-y-4">
          <Button
            data-testid="btn-new-schedule"
            onClick={() => setShowNewScheduleForm(!showNewScheduleForm)}
            className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
          >
            <Plus className="h-4 w-4 mr-2" />
            Planifier Maintenance
          </Button>

          {showNewScheduleForm && (
            <Card className="bg-[#0a0a15] border-[#F5A623]/20">
              <CardContent className="pt-4 space-y-4">
                <Input
                  placeholder="Titre"
                  value={newSchedule.title}
                  onChange={(e) => setNewSchedule({ ...newSchedule, title: e.target.value })}
                  className="bg-[#050510] border-[#F5A623]/30 text-white"
                />
                <Input
                  placeholder="Description"
                  value={newSchedule.description}
                  onChange={(e) => setNewSchedule({ ...newSchedule, description: e.target.value })}
                  className="bg-[#050510] border-[#F5A623]/30 text-white"
                />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-400 text-sm">Début</label>
                    <Input
                      type="datetime-local"
                      value={newSchedule.start_time}
                      onChange={(e) => setNewSchedule({ ...newSchedule, start_time: e.target.value })}
                      className="bg-[#050510] border-[#F5A623]/30 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 text-sm">Fin</label>
                    <Input
                      type="datetime-local"
                      value={newSchedule.end_time}
                      onChange={(e) => setNewSchedule({ ...newSchedule, end_time: e.target.value })}
                      className="bg-[#050510] border-[#F5A623]/30 text-white"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={createScheduledMaintenance} className="bg-[#F5A623] text-black">Planifier</Button>
                  <Button variant="ghost" onClick={() => setShowNewScheduleForm(false)} className="text-gray-400">Annuler</Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-3">
            {scheduledMaintenances.map((schedule) => (
              <Card key={schedule.id} data-testid={`schedule-item-${schedule.id}`} className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Calendar className="h-5 w-5 text-purple-400" />
                    <div>
                      <p className="text-white font-medium">{schedule.title}</p>
                      <p className="text-gray-500 text-sm">{schedule.description}</p>
                      <p className="text-gray-600 text-xs mt-1">
                        {formatDate(schedule.start_time)} → {formatDate(schedule.end_time)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge className={schedule.status === 'scheduled' ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-500/20 text-gray-400'}>
                      {schedule.status}
                    </Badge>
                    <Button size="sm" variant="ghost" onClick={() => deleteScheduledMaintenance(schedule.id)} className="text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            {scheduledMaintenances.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucune maintenance planifiée.
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Logs Tab */}
      {!loading && activeTab === 'logs' && (
        <div className="space-y-4">
          <Button onClick={fetchMaintenanceLogs} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>

          <div className="grid gap-3">
            {maintenanceLogs.map((log, idx) => (
              <Card key={idx} className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-3 flex items-center gap-4">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <div className="flex-1">
                    <p className="text-white text-sm">{log.action}</p>
                    <p className="text-gray-500 text-xs">{formatDate(log.timestamp)}</p>
                  </div>
                  {log.enabled !== undefined && (
                    <Badge className={log.enabled ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}>
                      {log.enabled ? 'Activé' : 'Désactivé'}
                    </Badge>
                  )}
                </CardContent>
              </Card>
            ))}
            {maintenanceLogs.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucun log de maintenance.
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMaintenance;
