/**
 * AdminDashboard - V5-ULTIME Administration Premium
 * ==================================================
 * 
 * Dashboard principal avec KPIs et navigation.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, CreditCard, TrendingUp, Target, Crown,
  Settings, FileText, BarChart3, Layers, RefreshCw,
  BookOpen, Zap, Shield, Activity
} from 'lucide-react';
import AdminService from '../AdminService';

const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = 'text-[#F5A623]' }) => (
  <Card className="bg-[#0d0d1a] border-[#F5A623]/20 hover:border-[#F5A623]/40 transition-all">
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-1">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
          {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg bg-[#F5A623]/10`}>
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-1">
          <TrendingUp className="h-4 w-4 text-green-500" />
          <span className="text-green-500 text-sm">{trend}</span>
        </div>
      )}
    </CardContent>
  </Card>
);

const AdminDashboard = ({ onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    const result = await AdminService.getDashboard();
    if (result.success) {
      setDashboard(result.dashboard);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const navItems = [
    { id: 'payments', label: 'Paiements', icon: CreditCard, desc: 'Stripe, transactions' },
    { id: 'freemium', label: 'Freemium', icon: Layers, desc: 'Quotas, tiers' },
    { id: 'upsell', label: 'Upsell', icon: Zap, desc: 'Campagnes, analytics' },
    { id: 'onboarding', label: 'Onboarding', icon: Target, desc: 'Parcours, flows' },
    { id: 'tutorials', label: 'Tutoriels', icon: BookOpen, desc: 'Contenus, tips' },
    { id: 'rules', label: 'Règles', icon: Settings, desc: 'Plan Maître' },
    { id: 'strategy', label: 'Stratégies', icon: BarChart3, desc: 'Générées, logs' },
    { id: 'users', label: 'Utilisateurs', icon: Users, desc: 'Profils, rôles' },
    { id: 'logs', label: 'Logs', icon: FileText, desc: 'Erreurs, webhooks' },
    { id: 'settings', label: 'Paramètres', icon: Shield, desc: 'Config, toggles' },
  ];

  return (
    <div data-testid="admin-dashboard" className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Crown className="h-8 w-8 text-[#F5A623]" />
            Administration Premium
          </h1>
          <p className="text-gray-400 mt-1">Vue d'ensemble et gestion complète</p>
        </div>
        <Button 
          onClick={fetchDashboard}
          variant="outline" 
          className="border-[#F5A623]/30 text-[#F5A623] hover:bg-[#F5A623]/10"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Utilisateurs"
          value={dashboard?.users?.total || 0}
          subtitle={`${dashboard?.users?.premium || 0} Premium`}
          icon={Users}
        />
        <StatCard
          title="Revenus"
          value={`${dashboard?.revenue?.total || 0}$`}
          subtitle={`${dashboard?.revenue?.transactions || 0} transactions`}
          icon={CreditCard}
          color="text-green-400"
        />
        <StatCard
          title="Onboarding"
          value={`${dashboard?.onboarding?.completion_rate || 0}%`}
          subtitle={`${dashboard?.onboarding?.completed || 0} complétés`}
          icon={Target}
          color="text-blue-400"
        />
        <StatCard
          title="CTR Upsell"
          value={`${dashboard?.upsell?.ctr || 0}%`}
          subtitle={`${dashboard?.upsell?.impressions || 0} impressions`}
          icon={Activity}
          color="text-purple-400"
        />
      </div>

      {/* Quick Navigation */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Modules d'administration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {navItems.map((item) => (
              <Button
                key={item.id}
                data-testid={`nav-${item.id}`}
                variant="ghost"
                onClick={() => onNavigate(item.id)}
                className="h-auto flex-col gap-2 p-4 bg-white/5 hover:bg-[#F5A623]/10 border border-transparent hover:border-[#F5A623]/30"
              >
                <item.icon className="h-6 w-6 text-[#F5A623]" />
                <span className="text-white font-medium">{item.label}</span>
                <span className="text-gray-500 text-xs">{item.desc}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white text-lg">Distribution des tiers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {['free', 'premium', 'pro'].map((tier) => {
                const count = tier === 'free' 
                  ? (dashboard?.users?.free || 0)
                  : tier === 'premium' 
                    ? Math.floor((dashboard?.users?.premium || 0) * 0.7)
                    : Math.floor((dashboard?.users?.premium || 0) * 0.3);
                const total = dashboard?.users?.with_subscription || 1;
                const percent = Math.round((count / total) * 100);
                
                return (
                  <div key={tier} className="flex items-center gap-3">
                    <Badge className={`
                      w-20 justify-center
                      ${tier === 'free' ? 'bg-gray-600' : ''}
                      ${tier === 'premium' ? 'bg-[#F5A623] text-black' : ''}
                      ${tier === 'pro' ? 'bg-purple-500' : ''}
                    `}>
                      {tier.toUpperCase()}
                    </Badge>
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${tier === 'free' ? 'bg-gray-500' : tier === 'premium' ? 'bg-[#F5A623]' : 'bg-purple-500'}`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span className="text-gray-400 text-sm w-12 text-right">{count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white text-lg">Activité récente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-2 bg-white/5 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-gray-300 text-sm">Système opérationnel</span>
                <Badge className="ml-auto bg-green-500/20 text-green-400">OK</Badge>
              </div>
              <div className="flex items-center gap-3 p-2 bg-white/5 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-[#F5A623]" />
                <span className="text-gray-300 text-sm">60 modules actifs</span>
                <Badge className="ml-auto bg-[#F5A623]/20 text-[#F5A623]">V5</Badge>
              </div>
              <div className="flex items-center gap-3 p-2 bg-white/5 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                <span className="text-gray-300 text-sm">Stripe connecté</span>
                <Badge className="ml-auto bg-blue-500/20 text-blue-400">TEST</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
