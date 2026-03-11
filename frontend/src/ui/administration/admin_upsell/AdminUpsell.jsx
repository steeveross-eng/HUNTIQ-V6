/**
 * AdminUpsell - V5-ULTIME Administration Premium
 * ===============================================
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Zap, RefreshCw, TrendingUp, Target, MousePointer } from 'lucide-react';
import AdminService from '../AdminService';

const AdminUpsell = () => {
  const [loading, setLoading] = useState(true);
  const [campaigns, setCampaigns] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [campResult, analResult] = await Promise.all([
      AdminService.getUpsellCampaigns(),
      AdminService.getUpsellAnalytics(30)
    ]);
    
    if (campResult.success) setCampaigns(campResult.campaigns || []);
    if (analResult.success) setAnalytics(analResult);
    setLoading(false);
  };

  const handleToggle = async (name, enabled) => {
    await AdminService.toggleCampaign(name, !enabled);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-upsell" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Zap className="h-6 w-6 text-[#F5A623]" />
          Gestion Upsell
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Analytics */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4 flex items-center gap-3">
            <Target className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-gray-400 text-sm">Impressions</p>
              <p className="text-2xl font-bold text-blue-400">{analytics?.totals?.impressions || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4 flex items-center gap-3">
            <MousePointer className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-gray-400 text-sm">Clics</p>
              <p className="text-2xl font-bold text-green-400">{analytics?.totals?.clicks || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4 flex items-center gap-3">
            <TrendingUp className="h-8 w-8 text-[#F5A623]" />
            <div>
              <p className="text-gray-400 text-sm">CTR moyen</p>
              <p className="text-2xl font-bold text-[#F5A623]">
                {analytics?.totals?.impressions > 0 
                  ? ((analytics.totals.clicks / analytics.totals.impressions) * 100).toFixed(2) 
                  : 0}%
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Campaigns */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Campagnes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {campaigns.map((camp) => (
              <div key={camp.name} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium">{camp.name.replace(/_/g, ' ')}</p>
                  <p className="text-gray-500 text-sm">Priorité: {camp.priority}</p>
                </div>
                <div className="flex items-center gap-4">
                  {analytics?.campaigns?.[camp.name] && (
                    <Badge className="bg-blue-500/20 text-blue-400">
                      CTR: {analytics.campaigns[camp.name].ctr}%
                    </Badge>
                  )}
                  <Switch
                    checked={camp.enabled}
                    onCheckedChange={() => handleToggle(camp.name, camp.enabled)}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminUpsell;
