/**
 * AdminTutorials - V5-ULTIME Administration Premium
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { BookOpen, RefreshCw, CheckCircle, SkipForward } from 'lucide-react';
import AdminService from '../AdminService';

const AdminTutorials = () => {
  const [loading, setLoading] = useState(true);
  const [tutorials, setTutorials] = useState([]);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [tutResult, progResult] = await Promise.all([
      AdminService.getTutorials(),
      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/v1/admin/tutorials/progress`).then(r => r.json())
    ]);
    
    if (tutResult.success) setTutorials(tutResult.tutorials || []);
    if (progResult.success) setProgress(progResult);
    setLoading(false);
  };

  const handleToggle = async (id, enabled) => {
    await AdminService.toggleTutorial(id, !enabled);
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
    <div data-testid="admin-tutorials" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-[#F5A623]" />
          Gestion Tutoriels
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-gray-400 text-sm">Complétés</p>
              <p className="text-2xl font-bold text-green-400">{progress?.stats?.completions || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-yellow-500/30">
          <CardContent className="p-4 flex items-center gap-3">
            <SkipForward className="h-8 w-8 text-yellow-500" />
            <div>
              <p className="text-gray-400 text-sm">Ignorés</p>
              <p className="text-2xl font-bold text-yellow-400">{progress?.stats?.skips || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4 flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-[#F5A623]" />
            <div>
              <p className="text-gray-400 text-sm">Taux complétion</p>
              <p className="text-2xl font-bold text-[#F5A623]">{progress?.stats?.completion_rate || 0}%</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tutorials List */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
        <CardHeader>
          <CardTitle className="text-white">Liste des tutoriels</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {tutorials.map((tut) => (
              <div key={tut.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium">{tut.id.replace(/_/g, ' ')}</p>
                  <div className="flex gap-2 mt-1">
                    <Badge className="bg-blue-500/20 text-blue-400">{tut.type}</Badge>
                    <Badge className="bg-purple-500/20 text-purple-400">{tut.feature}</Badge>
                  </div>
                </div>
                <Switch
                  checked={tut.enabled}
                  onCheckedChange={() => handleToggle(tut.id, tut.enabled)}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminTutorials;
