/**
 * AdminStrategy - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BarChart3, RefreshCw, Activity, Layers } from 'lucide-react';
import AdminService from '../AdminService';

const AdminStrategy = () => {
  const [loading, setLoading] = useState(true);
  const [strategies, setStrategies] = useState([]);
  const [diagnostics, setDiagnostics] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [stratResult, diagResult] = await Promise.all([
      AdminService.getStrategies(20),
      AdminService.getStrategyDiagnostics()
    ]);
    
    if (stratResult.success) setStrategies(stratResult.strategies || []);
    if (diagResult.success) setDiagnostics(diagResult.diagnostics);
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
    <div data-testid="admin-strategy" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-[#F5A623]" />
          Gestion Stratégies
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Diagnostics */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4 flex items-center gap-3">
            <Activity className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-gray-400 text-sm">Status</p>
              <p className="text-lg font-bold text-green-400">{diagnostics?.engine_status || 'N/A'}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Total plans</p>
            <p className="text-2xl font-bold text-[#F5A623]">{diagnostics?.total_plans || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Aujourd'hui</p>
            <p className="text-2xl font-bold text-blue-400">{diagnostics?.plans_today || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-purple-500/30">
          <CardContent className="p-4">
            <p className="text-gray-400 text-sm">Sources</p>
            <p className="text-2xl font-bold text-purple-400">
              {diagnostics?.by_source ? Object.keys(diagnostics.by_source).length : 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Strategies List */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Stratégies récentes</CardTitle>
        </CardHeader>
        <CardContent>
          {strategies.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Aucune stratégie générée</p>
          ) : (
            <div className="space-y-3">
              {strategies.map((strat, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{strat.name || `Plan #${i + 1}`}</p>
                    <p className="text-gray-500 text-sm">
                      {strat.user_id} • {strat.created_at ? new Date(strat.created_at).toLocaleDateString('fr-CA') : 'N/A'}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {strat.current_phase && (
                      <Badge className="bg-blue-500/20 text-blue-400">{strat.current_phase}</Badge>
                    )}
                    {strat.created_from && (
                      <Badge className="bg-purple-500/20 text-purple-400">{strat.created_from}</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminStrategy;
