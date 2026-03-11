/**
 * AdminFreemium - V5-ULTIME Administration Premium
 * =================================================
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Layers, RefreshCw, Users, Target, Zap } from 'lucide-react';
import AdminService from '../AdminService';

const AdminFreemium = () => {
  const [loading, setLoading] = useState(true);
  const [quotas, setQuotas] = useState(null);
  const [distribution, setDistribution] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [quotasResult, distResult] = await Promise.all([
      AdminService.getQuotaOverview(),
      AdminService.getTierDistribution()
    ]);
    
    if (quotasResult.success) setQuotas(quotasResult);
    if (distResult.success) setDistribution(distResult);
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
    <div data-testid="admin-freemium" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Layers className="h-6 w-6 text-[#F5A623]" />
          Gestion Freemium
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Tier Distribution */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-[#F5A623]" />
            Distribution des tiers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {distribution?.distribution && Object.entries(distribution.distribution).map(([tier, count]) => {
              const percent = distribution.percentages?.[tier] || 0;
              return (
                <div key={tier} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge className={`
                      ${tier === 'free' ? 'bg-gray-600' : ''}
                      ${tier === 'premium' ? 'bg-[#F5A623] text-black' : ''}
                      ${tier === 'pro' ? 'bg-purple-500' : ''}
                    `}>
                      {tier.toUpperCase()}
                    </Badge>
                    <span className="text-gray-400">{count} utilisateurs ({percent}%)</span>
                  </div>
                  <Progress 
                    value={percent} 
                    className={`h-2 ${tier === 'premium' ? '[&>div]:bg-[#F5A623]' : tier === 'pro' ? '[&>div]:bg-purple-500' : '[&>div]:bg-gray-500'}`}
                  />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quotas Usage */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-5 w-5 text-[#F5A623]" />
            Utilisation des quotas (aujourd'hui)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {quotas?.quotas_by_feature && Object.keys(quotas.quotas_by_feature).length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(quotas.quotas_by_feature).map(([feature, data]) => (
                <div key={feature} className="p-4 bg-white/5 rounded-lg">
                  <p className="text-white font-medium">{feature}</p>
                  <p className="text-2xl font-bold text-[#F5A623]">{data.total_usage}</p>
                  <p className="text-gray-500 text-sm">{data.users} utilisateurs</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Aucun quota utilisé aujourd'hui</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminFreemium;
