/**
 * AdminSettings - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Shield, RefreshCw, Key, ToggleLeft, CheckCircle, XCircle } from 'lucide-react';
import AdminService from '../AdminService';

const AdminSettings = () => {
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState(null);
  const [apiKeys, setApiKeys] = useState(null);
  const [toggles, setToggles] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [setResult, keyResult, togResult] = await Promise.all([
      AdminService.getSettings(),
      AdminService.getApiKeysStatus(),
      AdminService.getToggles()
    ]);
    
    if (setResult.success) setSettings(setResult);
    if (keyResult.success) setApiKeys(keyResult.api_keys);
    if (togResult.success) setToggles(togResult.toggles || []);
    setLoading(false);
  };

  const handleToggle = async (id, enabled) => {
    await AdminService.updateToggle(id, !enabled);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const categoryGroups = toggles.reduce((acc, toggle) => {
    if (!acc[toggle.category]) acc[toggle.category] = [];
    acc[toggle.category].push(toggle);
    return acc;
  }, {});

  return (
    <div data-testid="admin-settings" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Shield className="h-6 w-6 text-[#F5A623]" />
          Paramètres Système
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* API Keys Status */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Key className="h-5 w-5 text-[#F5A623]" />
            Clés API
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {apiKeys && Object.entries(apiKeys).map(([key, data]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white text-sm font-mono">{key}</p>
                  {data.preview && (
                    <p className="text-gray-500 text-xs font-mono">{data.preview}</p>
                  )}
                </div>
                {data.configured ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Feature Toggles */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ToggleLeft className="h-5 w-5 text-[#F5A623]" />
            Feature Toggles
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(categoryGroups).map(([category, catToggles]) => (
              <div key={category}>
                <h4 className="text-gray-400 text-sm uppercase mb-3">{category}</h4>
                <div className="space-y-2">
                  {catToggles.map((toggle) => (
                    <div key={toggle.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white">{toggle.name}</p>
                        <p className="text-gray-500 text-xs">{toggle.id}</p>
                      </div>
                      <Switch
                        checked={toggle.enabled}
                        onCheckedChange={() => handleToggle(toggle.id, toggle.enabled)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* App Info */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Informations Application</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {settings?.default_settings && Object.entries(settings.default_settings).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-400">{key}</span>
                <span className="text-white font-medium">{value}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminSettings;
