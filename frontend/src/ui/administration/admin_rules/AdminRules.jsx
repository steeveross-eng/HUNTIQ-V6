/**
 * AdminRules - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Settings, RefreshCw, Scale } from 'lucide-react';
import AdminService from '../AdminService';

const AdminRules = () => {
  const [loading, setLoading] = useState(true);
  const [rules, setRules] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [rulesResult, statsResult] = await Promise.all([
      AdminService.getRules(),
      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/v1/admin/rules/stats`).then(r => r.json())
    ]);
    
    if (rulesResult.success) setRules(rulesResult.rules || []);
    if (statsResult.success) setStats(statsResult.stats);
    setLoading(false);
  };

  const handleToggle = async (id, enabled) => {
    await AdminService.toggleRule(id, !enabled);
    fetchData();
  };

  const handleWeightChange = async (id, weight) => {
    await AdminService.updateRuleWeight(id, weight);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const categoryColors = {
    weather: 'bg-blue-500/20 text-blue-400',
    timing: 'bg-purple-500/20 text-purple-400',
    territory: 'bg-green-500/20 text-green-400',
    disturbance: 'bg-red-500/20 text-red-400',
    data: 'bg-yellow-500/20 text-yellow-400',
    wildlife: 'bg-orange-500/20 text-orange-400',
    legal: 'bg-gray-500/20 text-gray-400'
  };

  return (
    <div data-testid="admin-rules" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings className="h-6 w-6 text-[#F5A623]" />
          Gestion Règles Plan Maître
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Total règles</p>
            <p className="text-2xl font-bold text-[#F5A623]">{stats?.total_rules || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Stratégies générées</p>
            <p className="text-2xl font-bold text-blue-400">{stats?.strategies_generated || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-purple-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Catégories</p>
            <p className="text-2xl font-bold text-purple-400">{stats?.categories?.length || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Rules List */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Scale className="h-5 w-5 text-[#F5A623]" />
            Configuration des règles
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {rules.map((rule) => (
              <div key={rule.id} className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-white font-medium">{rule.id.replace(/_/g, ' ')}</p>
                    <Badge className={categoryColors[rule.category] || 'bg-gray-500/20 text-gray-400'}>
                      {rule.category}
                    </Badge>
                  </div>
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={() => handleToggle(rule.id, rule.enabled)}
                  />
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-gray-400 text-sm w-16">Poids:</span>
                  <Slider
                    value={[rule.custom_weight * 100]}
                    onValueCommit={([v]) => handleWeightChange(rule.id, v / 100)}
                    max={200}
                    min={-100}
                    step={10}
                    className="flex-1"
                  />
                  <span className={`text-sm w-16 text-right ${rule.custom_weight < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {rule.custom_weight.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminRules;
