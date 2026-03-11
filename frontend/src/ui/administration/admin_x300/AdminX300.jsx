/**
 * AdminX300 - Stratégie X300% Dashboard
 * ======================================
 * 
 * Module de contrôle de la stratégie X300%:
 * - Master Switch (ON/OFF global)
 * - Contact Engine (Captation)
 * - Trigger Engine (Automatisation)
 * - Identity Graph (Scoring)
 * - Calendar Engine (Planification)
 * 
 * Architecture LEGO V5 - Module isolé.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Power, Users, Zap, BarChart3, Calendar, Shield,
  RefreshCw, TrendingUp, Target, Activity, Eye,
  MousePointer, Share2, Mail, Bell, Settings,
  Layers, Brain, Search, Sparkles, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const AdminX300 = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [switches, setSwitches] = useState({});
  const [switchSummary, setSwitchSummary] = useState({});
  const [contactDashboard, setContactDashboard] = useState(null);
  const [triggers, setTriggers] = useState([]);
  const [triggerStats, setTriggerStats] = useState({});

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // Load master switch status
      const switchRes = await fetch(`${API_BASE}/api/v1/master-switch/status`);
      const switchData = await switchRes.json();
      if (switchData.success) {
        setSwitches(switchData.switches || {});
        setSwitchSummary(switchData.summary || {});
      }

      // Load contact engine dashboard
      const contactRes = await fetch(`${API_BASE}/api/v1/contact-engine/dashboard`);
      const contactData = await contactRes.json();
      if (contactData.success) {
        setContactDashboard(contactData.dashboard);
      }

      // Load triggers
      const triggerRes = await fetch(`${API_BASE}/api/v1/trigger-engine/triggers`);
      const triggerData = await triggerRes.json();
      if (triggerData.success) {
        setTriggers(triggerData.triggers || []);
        setTriggerStats(triggerData.stats || {});
      }
    } catch (error) {
      console.error('Error loading X300 data:', error);
      toast.error('Erreur lors du chargement des données');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleSwitch = async (switchId, currentState) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/master-switch/toggle/${switchId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentState })
      });
      const data = await res.json();
      if (data.success) {
        toast.success(data.message);
        loadData();
      } else {
        toast.error(data.error || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const toggleGlobal = async () => {
    const currentGlobal = switches.global?.is_active;
    try {
      const res = await fetch(`${API_BASE}/api/v1/master-switch/toggle-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentGlobal })
      });
      const data = await res.json();
      if (data.success) {
        toast.success(data.message);
        loadData();
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const toggleTrigger = async (triggerId, currentState) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/trigger-engine/triggers/${triggerId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentState })
      });
      const data = await res.json();
      if (data.success) {
        toast.success(`Trigger ${!currentState ? 'activé' : 'désactivé'}`);
        loadData();
      }
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const getSwitchIcon = (key) => {
    const icons = {
      global: Power,
      captation: Eye,
      enrichment: Brain,
      triggers: Zap,
      scoring: BarChart3,
      seo: Search,
      marketing_calendar: Calendar,
      consent_layer: Shield
    };
    return icons[key] || Settings;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const globalActive = switches.global?.is_active;

  return (
    <div data-testid="admin-x300" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-xl ${globalActive ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
            <Power className={`h-8 w-8 ${globalActive ? 'text-green-500' : 'text-red-500'}`} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Stratégie X300%</h2>
            <p className="text-gray-400 text-sm">Captation • Enrichissement • Triggers • Scoring</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={`px-4 py-2 ${globalActive ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30'}`}>
            {globalActive ? '✓ SYSTÈME ACTIF' : '✗ SYSTÈME INACTIF'}
          </Badge>
          <Button 
            onClick={toggleGlobal}
            className={globalActive ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}
          >
            <Power className="h-4 w-4 mr-2" />
            {globalActive ? 'Tout Désactiver' : 'Tout Activer'}
          </Button>
          <Button variant="outline" onClick={loadData} className="border-[#F5A623]/30 text-[#F5A623]">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Master Switches Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(switches).filter(([key]) => key !== 'global').map(([key, sw]) => {
          const Icon = getSwitchIcon(key);
          const isEffectivelyActive = globalActive && sw.is_active;
          return (
            <Card 
              key={key} 
              className={`bg-[#0d0d1a] border transition-all cursor-pointer ${
                isEffectivelyActive 
                  ? 'border-green-500/30 hover:border-green-500/50' 
                  : 'border-red-500/20 hover:border-red-500/40'
              }`}
              onClick={() => toggleSwitch(key, sw.is_active)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`h-6 w-6 ${isEffectivelyActive ? 'text-green-400' : 'text-gray-500'}`} />
                  <Switch 
                    checked={sw.is_active} 
                    disabled={!globalActive}
                    className="data-[state=checked]:bg-green-500"
                  />
                </div>
                <p className="text-white font-medium text-sm">{sw.name}</p>
                <p className="text-gray-500 text-xs mt-1 line-clamp-2">{sw.description}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[#0d0d1a] border border-[#F5A623]/20">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Activity className="h-4 w-4 mr-2" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="contacts" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Users className="h-4 w-4 mr-2" />
            Contacts
          </TabsTrigger>
          <TabsTrigger value="triggers" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Zap className="h-4 w-4 mr-2" />
            Triggers
          </TabsTrigger>
          <TabsTrigger value="scoring" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <BarChart3 className="h-4 w-4 mr-2" />
            Scoring
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Visitors Card */}
            <Card className="bg-[#0d0d1a] border-blue-500/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Eye className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="text-gray-400 text-sm">Visiteurs Trackés</p>
                    <p className="text-2xl font-bold text-blue-400">
                      {contactDashboard?.visitors?.total || 0}
                    </p>
                  </div>
                </div>
                <div className="mt-3 flex gap-2">
                  <Badge variant="outline" className="text-xs border-gray-600">
                    {contactDashboard?.visitors?.anonymous || 0} anonymes
                  </Badge>
                  <Badge variant="outline" className="text-xs border-green-600 text-green-400">
                    {contactDashboard?.visitors?.identified || 0} identifiés
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Conversion Card */}
            <Card className="bg-[#0d0d1a] border-green-500/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-gray-400 text-sm">Taux de Conversion</p>
                    <p className="text-2xl font-bold text-green-400">
                      {contactDashboard?.visitors?.conversion_rate || 0}%
                    </p>
                  </div>
                </div>
                <Progress 
                  value={contactDashboard?.visitors?.conversion_rate || 0} 
                  className="mt-3 h-2"
                />
              </CardContent>
            </Card>

            {/* Events Card */}
            <Card className="bg-[#0d0d1a] border-purple-500/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <MousePointer className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-gray-400 text-sm">Événements Captés</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {contactDashboard?.events?.total || 0}
                    </p>
                  </div>
                </div>
                <div className="mt-3 flex gap-2">
                  <Badge variant="outline" className="text-xs border-orange-600 text-orange-400">
                    {contactDashboard?.events?.ad_clicks || 0} ads
                  </Badge>
                  <Badge variant="outline" className="text-xs border-pink-600 text-pink-400">
                    {contactDashboard?.events?.social_interactions || 0} social
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Triggers Card */}
            <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Zap className="h-8 w-8 text-[#F5A623]" />
                  <div>
                    <p className="text-gray-400 text-sm">Triggers Actifs</p>
                    <p className="text-2xl font-bold text-[#F5A623]">
                      {triggerStats?.active || 0}/{triggerStats?.total || 0}
                    </p>
                  </div>
                </div>
                <Progress 
                  value={triggerStats?.total ? (triggerStats.active / triggerStats.total) * 100 : 0} 
                  className="mt-3 h-2"
                />
              </CardContent>
            </Card>
          </div>

          {/* Average Scores */}
          {contactDashboard?.average_scores && (
            <Card className="bg-[#0d0d1a] border-[#F5A623]/20 mt-4">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-[#F5A623]" />
                  Scores Moyens des Contacts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-gray-400 text-sm">Intérêt</p>
                    <div className="flex items-center gap-2">
                      <Progress value={contactDashboard.average_scores.interest} className="flex-1 h-2" />
                      <span className="text-white font-bold">{contactDashboard.average_scores.interest}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Chaleur</p>
                    <div className="flex items-center gap-2">
                      <Progress value={contactDashboard.average_scores.heat} className="flex-1 h-2" />
                      <span className="text-white font-bold">{contactDashboard.average_scores.heat}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Rétention</p>
                    <div className="flex items-center gap-2">
                      <Progress value={contactDashboard.average_scores.retention} className="flex-1 h-2" />
                      <span className="text-white font-bold">{contactDashboard.average_scores.retention}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Intention d'achat</p>
                    <div className="flex items-center gap-2">
                      <Progress value={contactDashboard.average_scores.purchase_intent} className="flex-1 h-2" />
                      <span className="text-white font-bold">{contactDashboard.average_scores.purchase_intent}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Contacts Tab */}
        <TabsContent value="contacts" className="mt-6">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5 text-[#F5A623]" />
                Contact Engine
              </CardTitle>
              <CardDescription>Captation des visiteurs, publicités et interactions sociales</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-[#1a1a2e] rounded-lg">
                  <Eye className="h-6 w-6 text-blue-400 mb-2" />
                  <h4 className="text-white font-medium">Visitor Tracker</h4>
                  <p className="text-gray-400 text-sm">Tracking des visiteurs anonymes avec création automatique de Shadow Profiles</p>
                  <Badge className="mt-2 bg-blue-500/20 text-blue-400">Actif</Badge>
                </div>
                <div className="p-4 bg-[#1a1a2e] rounded-lg">
                  <MousePointer className="h-6 w-6 text-orange-400 mb-2" />
                  <h4 className="text-white font-medium">Ads Tracker</h4>
                  <p className="text-gray-400 text-sm">Suivi des clics publicitaires (Google, Meta, TikTok) avec enrichissement des profils</p>
                  <Badge className="mt-2 bg-orange-500/20 text-orange-400">Actif</Badge>
                </div>
                <div className="p-4 bg-[#1a1a2e] rounded-lg">
                  <Share2 className="h-6 w-6 text-pink-400 mb-2" />
                  <h4 className="text-white font-medium">Social Tracker</h4>
                  <p className="text-gray-400 text-sm">Tracking des interactions sociales (partages, likes, commentaires)</p>
                  <Badge className="mt-2 bg-pink-500/20 text-pink-400">Actif</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Triggers Tab */}
        <TabsContent value="triggers" className="mt-6">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Zap className="h-5 w-5 text-[#F5A623]" />
                    Marketing Trigger Engine
                  </CardTitle>
                  <CardDescription>Triggers automatiques pour promotions, relances et séquences</CardDescription>
                </div>
                <Badge className="bg-[#F5A623]/20 text-[#F5A623]">
                  {triggerStats?.active || 0} actifs / {triggerStats?.total || 0}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {triggers.map((trigger) => (
                  <div 
                    key={trigger.id} 
                    className={`flex items-center justify-between p-4 rounded-lg border transition-all ${
                      trigger.is_active 
                        ? 'bg-[#1a1a2e] border-green-500/20' 
                        : 'bg-[#0d0d1a] border-gray-700'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${trigger.is_active ? 'bg-green-500/20' : 'bg-gray-700'}`}>
                        <Zap className={`h-5 w-5 ${trigger.is_active ? 'text-green-400' : 'text-gray-500'}`} />
                      </div>
                      <div>
                        <p className="text-white font-medium">{trigger.name_fr || trigger.name}</p>
                        <p className="text-gray-500 text-sm">
                          Type: {trigger.trigger_type} • Action: {trigger.action}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className={`text-xs ${
                        trigger.priority === 1 ? 'border-red-500 text-red-400' :
                        trigger.priority === 2 ? 'border-yellow-500 text-yellow-400' :
                        'border-gray-500 text-gray-400'
                      }`}>
                        P{trigger.priority}
                      </Badge>
                      <Switch 
                        checked={trigger.is_active}
                        onCheckedChange={() => toggleTrigger(trigger.id, trigger.is_active)}
                        className="data-[state=checked]:bg-green-500"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scoring Tab */}
        <TabsContent value="scoring" className="mt-6">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-[#F5A623]" />
                Bionic Identity Graph & Lead Scoring
              </CardTitle>
              <CardDescription>Unification des profils et scoring automatique des contacts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-[#1a1a2e] rounded-lg">
                  <Brain className="h-6 w-6 text-purple-400 mb-2" />
                  <h4 className="text-white font-medium">Identity Graph</h4>
                  <p className="text-gray-400 text-sm mb-3">
                    Unification automatique des visiteurs anonymes, identifiés, sociaux et publicitaires.
                    Fusion des profils après consentement.
                  </p>
                  <div className="flex gap-2">
                    <Badge className="bg-purple-500/20 text-purple-400">Fusion automatique</Badge>
                    <Badge className="bg-blue-500/20 text-blue-400">Multi-touch</Badge>
                  </div>
                </div>
                <div className="p-4 bg-[#1a1a2e] rounded-lg">
                  <Target className="h-6 w-6 text-green-400 mb-2" />
                  <h4 className="text-white font-medium">Lead Scoring</h4>
                  <p className="text-gray-400 text-sm mb-3">
                    Scoring automatique basé sur : Intérêt, Chaleur, Rétention, Intention d'achat.
                    Mise à jour en temps réel.
                  </p>
                  <div className="flex gap-2">
                    <Badge className="bg-green-500/20 text-green-400">Temps réel</Badge>
                    <Badge className="bg-[#F5A623]/20 text-[#F5A623]">4 dimensions</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export { AdminX300 };
export default AdminX300;
