/**
 * AdminOnboarding - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Target, RefreshCw, Users, CheckCircle, XCircle } from 'lucide-react';
import AdminService from '../AdminService';

const AdminOnboarding = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [flows, setFlows] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [statsResult, flowsResult] = await Promise.all([
      AdminService.getOnboardingStats(),
      AdminService.getOnboardingFlows()
    ]);
    
    if (statsResult.success) setStats(statsResult);
    if (flowsResult.success) setFlows(flowsResult.flows || []);
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-onboarding" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Target className="h-6 w-6 text-[#F5A623]" />
          Gestion Onboarding
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Total utilisateurs</p>
            <p className="text-2xl font-bold text-blue-400">{stats?.stats?.total_users || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Complétés</p>
            <p className="text-2xl font-bold text-green-400">{stats?.stats?.completed || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-yellow-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">En cours</p>
            <p className="text-2xl font-bold text-yellow-400">{stats?.stats?.in_progress || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Taux de complétion</p>
            <p className="text-2xl font-bold text-[#F5A623]">{stats?.stats?.completion_rate || 0}%</p>
          </CardContent>
        </Card>
      </div>

      {/* Steps Progress */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Progression par étape</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats?.by_step && Object.entries(stats.by_step).map(([step, data]) => (
              <div key={step} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-white capitalize">{step.replace(/_/g, ' ')}</span>
                  <span className="text-gray-400">{data.completed} ({data.rate}%)</span>
                </div>
                <Progress value={data.rate} className="h-2 [&>div]:bg-[#F5A623]" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Flows */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Configuration des flows</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {flows.map((flow, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium">{flow.title}</p>
                  <p className="text-gray-500 text-sm">
                    {flow.auto_generate ? 'Auto-génération' : `${flow.questions} questions`}
                  </p>
                </div>
                <Badge className={flow.required ? 'bg-[#F5A623] text-black' : 'bg-gray-600'}>
                  {flow.required ? 'Requis' : 'Optionnel'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminOnboarding;
