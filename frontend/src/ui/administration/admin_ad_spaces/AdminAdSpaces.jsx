/**
 * AdminAdSpaces - Ad Spaces Engine Dashboard
 * ===========================================
 * 
 * Interface d'administration pour la gestion des espaces publicitaires:
 * - Catalogue des emplacements
 * - Réservations et slots
 * - Master Switch Publicitaire
 * - Statut système (PRÉ-PRODUCTION / PRODUCTION)
 * 
 * Architecture LEGO V5-ULTIME
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LayoutGrid, Power, RefreshCw, Eye, Lock, Unlock,
  Monitor, Sidebar, Image, LayoutList, Star, MapPin,
  Search, AlertTriangle, CheckCircle, XCircle, Shield
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminAdSpaces = () => {
  const [dashboard, setDashboard] = useState(null);
  const [catalog, setCatalog] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [activeSlots, setActiveSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load dashboard
      const dashRes = await fetch(`${API}/api/v1/ad-spaces/dashboard`);
      const dashData = await dashRes.json();
      setDashboard(dashData.dashboard);

      // Load catalog
      const catRes = await fetch(`${API}/api/v1/ad-spaces/catalog`);
      const catData = await catRes.json();
      setCatalog(catData.catalog || []);

      // Load system status
      const statusRes = await fetch(`${API}/api/v1/affiliate-ads/system/status`);
      const statusData = await statusRes.json();
      setSystemStatus(statusData.system_status);

      // Load active slots
      const slotsRes = await fetch(`${API}/api/v1/ad-spaces/slots/active`);
      const slotsData = await slotsRes.json();
      setActiveSlots(slotsData.active_slots || []);

    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Erreur lors du chargement');
    }
    setLoading(false);
  };

  const handleToggleMasterSwitch = async (activate) => {
    setToggling(true);
    try {
      if (activate) {
        const res = await fetch(`${API}/api/v1/affiliate-ads/system/reactivate-all`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ admin_user: 'admin' })
        });
        const data = await res.json();
        if (data.success) {
          toast.success('🚀 Système activé - Mode PRODUCTION');
        }
      } else {
        const res = await fetch(`${API}/api/v1/affiliate-ads/system/deactivate-all`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            reason: 'Désactivation manuelle admin',
            admin_user: 'admin'
          })
        });
        const data = await res.json();
        if (data.success) {
          toast.success('🔒 Système désactivé - Mode PRÉ-PRODUCTION');
        }
      }
      loadData();
    } catch (error) {
      toast.error('Erreur');
    }
    setToggling(false);
  };

  const getCategoryIcon = (category) => {
    const icons = {
      banner: Monitor,
      sidebar: Sidebar,
      native: LayoutList,
      carousel: Image,
      featured: Star,
      inline: LayoutGrid
    };
    return icons[category] || LayoutGrid;
  };

  const getPriorityBadge = (priority) => {
    const styles = {
      premium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      standard: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      basic: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    };
    return styles[priority] || styles.standard;
  };

  const isPreProduction = !systemStatus?.master_switch?.is_active;

  return (
    <div className="space-y-6" data-testid="admin-ad-spaces">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <LayoutGrid className="h-6 w-6 text-[#F5A623]" />
            Ad Spaces Engine
          </h2>
          <p className="text-gray-400 mt-1">
            Gestion des espaces publicitaires BIONIC
          </p>
        </div>
        <Button
          variant="outline"
          onClick={loadData}
          disabled={loading}
          className="border-[#F5A623]/30 text-[#F5A623]"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </Button>
      </div>

      {/* Master Switch Card */}
      <Card className={`${isPreProduction ? 'bg-orange-500/10 border-orange-500/30' : 'bg-green-500/10 border-green-500/30'}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center ${isPreProduction ? 'bg-orange-500/20' : 'bg-green-500/20'}`}>
                {isPreProduction ? (
                  <Lock className="h-8 w-8 text-orange-400" />
                ) : (
                  <Unlock className="h-8 w-8 text-green-400" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Master Switch Publicitaire</h3>
                <p className={`text-sm ${isPreProduction ? 'text-orange-400' : 'text-green-400'}`}>
                  Mode: {isPreProduction ? 'PRÉ-PRODUCTION' : 'PRODUCTION'}
                </p>
                {systemStatus?.master_switch?.reason && (
                  <p className="text-gray-400 text-xs mt-1">
                    {systemStatus.master_switch.reason}
                  </p>
                )}
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <div className="flex items-center gap-3">
                <span className="text-gray-400">OFF</span>
                <Switch
                  checked={!isPreProduction}
                  onCheckedChange={(checked) => handleToggleMasterSwitch(checked)}
                  disabled={toggling}
                  className="data-[state=checked]:bg-green-500"
                />
                <span className="text-gray-400">ON</span>
              </div>
              <Badge className={isPreProduction ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}>
                {isPreProduction ? (
                  <><Shield className="h-3 w-3 mr-1" /> Publicités bloquées</>
                ) : (
                  <><CheckCircle className="h-3 w-3 mr-1" /> Publicités actives</>
                )}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#F5A623]/20 flex items-center justify-center">
                  <LayoutGrid className="h-5 w-5 text-[#F5A623]" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Espaces Totaux</p>
                  <p className="text-2xl font-bold text-white">{dashboard.catalog?.total_spaces || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Slots Actifs</p>
                  <p className="text-2xl font-bold text-white">{dashboard.reservations?.by_status?.active || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Eye className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Impressions</p>
                  <p className="text-2xl font-bold text-white">{dashboard.performance?.total_impressions?.toLocaleString() || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <MapPin className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">CTR Global</p>
                  <p className="text-2xl font-bold text-white">{dashboard.performance?.overall_ctr || 0}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="catalog" className="space-y-4">
        <TabsList className="bg-[#0a0a15] border border-white/10">
          <TabsTrigger value="catalog" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <LayoutGrid className="h-4 w-4 mr-2" />
            Catalogue ({catalog.length})
          </TabsTrigger>
          <TabsTrigger value="active" className="data-[state=active]:bg-green-500 data-[state=active]:text-white">
            <CheckCircle className="h-4 w-4 mr-2" />
            Slots Actifs ({activeSlots.length})
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <Shield className="h-4 w-4 mr-2" />
            Statut Système
          </TabsTrigger>
        </TabsList>

        {/* Catalog Tab */}
        <TabsContent value="catalog">
          <Card className="bg-[#0a0a15] border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Catalogue des Espaces Publicitaires</CardTitle>
              <CardDescription className="text-gray-400">
                Tous les emplacements disponibles dans BIONIC
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-white/10 hover:bg-transparent">
                    <TableHead className="text-gray-400">Espace</TableHead>
                    <TableHead className="text-gray-400">Catégorie</TableHead>
                    <TableHead className="text-gray-400">Taille</TableHead>
                    <TableHead className="text-gray-400">Priorité</TableHead>
                    <TableHead className="text-gray-400">Prix x</TableHead>
                    <TableHead className="text-gray-400">Max</TableHead>
                    <TableHead className="text-gray-400">Rotation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {catalog.map((space) => {
                    const Icon = getCategoryIcon(space.category);
                    return (
                      <TableRow key={space.space_id} className="border-white/10 hover:bg-white/5">
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4 text-[#F5A623]" />
                            <div>
                              <p className="text-white font-medium">{space.name}</p>
                              <p className="text-gray-500 text-xs">{space.space_id}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
                            {space.category}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-300">{space.size}</TableCell>
                        <TableCell>
                          <Badge className={getPriorityBadge(space.priority)}>
                            {space.priority?.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-green-400 font-medium">
                          {space.base_price_multiplier}x
                        </TableCell>
                        <TableCell className="text-gray-300">{space.max_concurrent}</TableCell>
                        <TableCell>
                          {space.rotation_enabled ? (
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          ) : (
                            <XCircle className="h-4 w-4 text-gray-500" />
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Active Slots Tab */}
        <TabsContent value="active">
          <Card className="bg-[#0a0a15] border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Slots Actifs</CardTitle>
              <CardDescription className="text-gray-400">
                Réservations actuellement en cours
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activeSlots.length > 0 ? (
                <div className="space-y-3">
                  {activeSlots.map((slot) => (
                    <div key={slot.reservation_id} className="p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-white font-medium">{slot.space_info?.name || slot.space_id}</p>
                          <p className="text-gray-400 text-sm">
                            Affilié: {slot.affiliate_id?.slice(0, 8)}...
                          </p>
                        </div>
                        <Badge className="bg-green-500/20 text-green-400">ACTIVE</Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                        <div>
                          <span className="text-gray-400">Début:</span>
                          <span className="text-white ml-2">{new Date(slot.start_date).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Fin:</span>
                          <span className="text-white ml-2">{new Date(slot.end_date).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Durée:</span>
                          <span className="text-white ml-2">{slot.duration_days} jours</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <AlertTriangle className="h-12 w-12 text-orange-400 mx-auto mb-3" />
                  <p className="text-gray-400">
                    {isPreProduction 
                      ? 'Mode PRÉ-PRODUCTION - Aucun slot actif'
                      : 'Aucune réservation active'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Status Tab */}
        <TabsContent value="system">
          <Card className="bg-[#0a0a15] border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Statut du Système Publicitaire</CardTitle>
              <CardDescription className="text-gray-400">
                Vue d'ensemble de l'état du système
              </CardDescription>
            </CardHeader>
            <CardContent>
              {systemStatus && (
                <div className="space-y-6">
                  {/* Master Switch */}
                  <div className="p-4 bg-white/5 rounded-lg">
                    <h4 className="text-white font-medium mb-3">Master Switch</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-gray-400">État:</span>
                        <Badge className={`ml-2 ${systemStatus.master_switch?.is_active ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'}`}>
                          {systemStatus.master_switch?.is_active ? 'ON' : 'OFF'}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-gray-400">Mode:</span>
                        <span className="text-white ml-2">{systemStatus.mode}</span>
                      </div>
                    </div>
                  </div>

                  {/* Opportunities by Status */}
                  <div className="p-4 bg-white/5 rounded-lg">
                    <h4 className="text-white font-medium mb-3">Opportunités par Statut</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(systemStatus.opportunities_by_status || {}).map(([status, count]) => (
                        <Badge key={status} variant="outline" className="border-white/20">
                          {status}: {count}
                        </Badge>
                      ))}
                      {Object.keys(systemStatus.opportunities_by_status || {}).length === 0 && (
                        <span className="text-gray-400">Aucune opportunité</span>
                      )}
                    </div>
                  </div>

                  {/* Deployed Ads */}
                  <div className="p-4 bg-white/5 rounded-lg">
                    <h4 className="text-white font-medium mb-3">Publicités Déployées</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-green-400">{systemStatus.deployed_ads?.active || 0}</p>
                        <p className="text-gray-400 text-sm">Actives</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-gray-400">{systemStatus.deployed_ads?.inactive || 0}</p>
                        <p className="text-gray-400 text-sm">Inactives</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminAdSpaces;
