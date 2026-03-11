/**
 * AdminLogs - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { FileText, RefreshCw, AlertTriangle, Webhook, Activity } from 'lucide-react';
import AdminService from '../AdminService';

const AdminLogs = () => {
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState([]);
  const [webhooks, setWebhooks] = useState([]);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [errResult, webResult, evtResult] = await Promise.all([
      AdminService.getErrorLogs(50),
      AdminService.getWebhookLogs(50),
      AdminService.getEventLogs(50)
    ]);
    
    if (errResult.success) setErrors(errResult.errors || []);
    if (webResult.success) setWebhooks(webResult.webhooks || []);
    if (evtResult.success) setEvents(evtResult.events || []);
    setLoading(false);
  };

  const severityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'error': return 'bg-orange-500/20 text-orange-400';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-blue-500/20 text-blue-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-logs" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileText className="h-6 w-6 text-[#F5A623]" />
          Logs Système
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      <Tabs defaultValue="errors" className="space-y-4">
        <TabsList className="bg-[#0d0d1a] border border-[#F5A623]/20">
          <TabsTrigger value="errors" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <AlertTriangle className="h-4 w-4 mr-2" />
            Erreurs ({errors.length})
          </TabsTrigger>
          <TabsTrigger value="webhooks" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Webhook className="h-4 w-4 mr-2" />
            Webhooks ({webhooks.length})
          </TabsTrigger>
          <TabsTrigger value="events" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Activity className="h-4 w-4 mr-2" />
            Events ({events.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="errors">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardContent className="p-4">
              {errors.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Aucune erreur récente</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-auto">
                  {errors.map((err, i) => (
                    <div key={i} className="p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={severityColor(err.severity)}>{err.severity}</Badge>
                        <span className="text-gray-500 text-xs">
                          {err.timestamp ? new Date(err.timestamp).toLocaleString('fr-CA') : 'N/A'}
                        </span>
                      </div>
                      <p className="text-white text-sm font-mono">{err.message}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="webhooks">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardContent className="p-4">
              {webhooks.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Aucun webhook récent</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-auto">
                  {webhooks.map((wh, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white text-sm">{wh.event_type || wh.type}</p>
                        <p className="text-gray-500 text-xs">{wh.source || 'stripe'}</p>
                      </div>
                      <Badge className={wh.status === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                        {wh.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardContent className="p-4">
              {events.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Aucun événement récent</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-auto">
                  {events.map((evt, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white text-sm">{evt.event_type}</p>
                        <p className="text-gray-500 text-xs">
                          {evt.timestamp ? new Date(evt.timestamp).toLocaleString('fr-CA') : 'N/A'}
                        </p>
                      </div>
                      <Badge className="bg-blue-500/20 text-blue-400">{evt.source || 'system'}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminLogs;
