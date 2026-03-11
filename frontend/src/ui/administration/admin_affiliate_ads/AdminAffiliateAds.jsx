/**
 * AdminAffiliateAds - Affiliate Ad Automation Dashboard
 * ======================================================
 * 
 * Interface d'administration pour le cycle de vente publicitaire:
 * - Opportunités publicitaires
 * - Checkout tracking
 * - Campagnes actives
 * - Performance (impressions, clics, CTR)
 * - Renouvellements
 * - Dashboard revenus BIONIC
 * 
 * Architecture LEGO V5-ULTIME
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Megaphone, DollarSign, Eye, MousePointer, TrendingUp,
  RefreshCw, Mail, Clock, CheckCircle, XCircle, Play,
  Calendar, BarChart3, Target, Zap, Send, CreditCard,
  Globe, Package, AlertCircle, ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminAffiliateAds = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [bionicDashboard, setBionicDashboard] = useState(null);
  const [pendingRenewals, setPendingRenewals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedOpp, setSelectedOpp] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    loadData();
  }, [page, statusFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load BIONIC dashboard
      const dashRes = await fetch(`${API}/api/v1/affiliate-ads/dashboard/bionic`);
      const dashData = await dashRes.json();
      setBionicDashboard(dashData.dashboard);

      // Load opportunities
      let url = `${API}/api/v1/affiliate-ads/opportunities?page=${page}&limit=20`;
      if (statusFilter !== 'all') url += `&status=${statusFilter}`;
      
      const oppRes = await fetch(url);
      const oppData = await oppRes.json();
      setOpportunities(oppData.opportunities || []);
      setPagination(oppData.pagination || {});

      // Load pending renewals
      const renewRes = await fetch(`${API}/api/v1/affiliate-ads/renewals/pending`);
      const renewData = await renewRes.json();
      setPendingRenewals(renewData.pending_renewals || []);

    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Erreur lors du chargement');
    }
    setLoading(false);
  };

  const handleSendEmail = async (opportunityId) => {
    try {
      const res = await fetch(`${API}/api/v1/affiliate-ads/opportunities/${opportunityId}/resend-email`, {
        method: 'POST'
      });
      const data = await res.json();
      if (data.success) {
        toast.success('Email envoyé avec succès');
        loadData();
      } else {
        toast.error(data.error || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    }
  };

  const handleSendRenewalReminder = async (opportunityId) => {
    try {
      const res = await fetch(`${API}/api/v1/affiliate-ads/renewals/${opportunityId}/send-reminder`, {
        method: 'POST'
      });
      const data = await res.json();
      if (data.success) {
        toast.success('Rappel envoyé');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const viewOpportunityDetails = async (opportunityId) => {
    try {
      const res = await fetch(`${API}/api/v1/affiliate-ads/opportunities/${opportunityId}`);
      const data = await res.json();
      if (data.success) {
        setSelectedOpp({ ...data.opportunity, logs: data.logs });
        setShowDetailDialog(true);
      }
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: { bg: 'bg-gray-500/20 text-gray-400', icon: Clock },
      email_sent: { bg: 'bg-blue-500/20 text-blue-400', icon: Mail },
      checkout_started: { bg: 'bg-yellow-500/20 text-yellow-400', icon: Target },
      payment_pending: { bg: 'bg-orange-500/20 text-orange-400', icon: CreditCard },
      paid: { bg: 'bg-purple-500/20 text-purple-400', icon: CheckCircle },
      active: { bg: 'bg-green-500/20 text-green-400', icon: Play },
      expired: { bg: 'bg-red-500/20 text-red-400', icon: XCircle },
      cancelled: { bg: 'bg-red-500/20 text-red-400', icon: XCircle }
    };
    const { bg, icon: Icon } = styles[status] || styles.pending;
    return (
      <Badge className={`${bg} flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {status?.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(amount || 0);
  };

  return (
    <div className="space-y-6" data-testid="admin-affiliate-ads">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Megaphone className="h-6 w-6 text-[#F5A623]" />
            Affiliate Ad Automation
          </h2>
          <p className="text-gray-400 mt-1">
            Cycle de vente publicitaire 100% automatisé
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

      {/* BIONIC Revenue Dashboard */}
      {bionicDashboard && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-gradient-to-br from-[#F5A623]/20 to-transparent border-[#F5A623]/30">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-[#F5A623]/20 flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-[#F5A623]" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Revenus Totaux</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(bionicDashboard.totals.total_revenue)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Play className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Pubs Actives</p>
                  <p className="text-2xl font-bold text-white">{bionicDashboard.active_ads_count}</p>
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
                  <p className="text-2xl font-bold text-white">{bionicDashboard.totals.total_impressions.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <MousePointer className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Clics</p>
                  <p className="text-2xl font-bold text-white">{bionicDashboard.totals.total_clicks.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-yellow-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-yellow-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">CTR Global</p>
                  <p className="text-2xl font-bold text-white">{bionicDashboard.totals.overall_ctr}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Pending Renewals Alert */}
      {pendingRenewals.length > 0 && (
        <Card className="bg-orange-500/10 border-orange-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-orange-400" />
                <div>
                  <p className="text-white font-medium">
                    {pendingRenewals.length} campagne(s) expirent dans les 7 prochains jours
                  </p>
                  <p className="text-orange-400/70 text-sm">
                    Envoyez des rappels de renouvellement
                  </p>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="border-orange-500/30 text-orange-400"
                onClick={() => {
                  pendingRenewals.forEach(opp => handleSendRenewalReminder(opp.opportunity_id));
                }}
              >
                <Send className="h-4 w-4 mr-2" />
                Envoyer tous les rappels
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="opportunities" className="space-y-4">
        <TabsList className="bg-[#0a0a15] border border-white/10">
          <TabsTrigger value="opportunities" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Target className="h-4 w-4 mr-2" />
            Opportunités
          </TabsTrigger>
          <TabsTrigger value="active" className="data-[state=active]:bg-green-500 data-[state=active]:text-white">
            <Play className="h-4 w-4 mr-2" />
            Campagnes Actives
          </TabsTrigger>
          <TabsTrigger value="placements" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <Globe className="h-4 w-4 mr-2" />
            Placements
          </TabsTrigger>
        </TabsList>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities">
          {/* Filters */}
          <Card className="bg-[#0a0a15] border-white/10 mb-4">
            <CardContent className="p-4">
              <div className="flex gap-4 items-end">
                <div className="w-[200px]">
                  <label className="text-gray-400 text-sm mb-1 block">Statut</label>
                  <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
                    <SelectTrigger className="bg-[#050510] border-white/10">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tous</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="email_sent">Email envoyé</SelectItem>
                      <SelectItem value="checkout_started">Checkout démarré</SelectItem>
                      <SelectItem value="payment_pending">Paiement en attente</SelectItem>
                      <SelectItem value="paid">Payé</SelectItem>
                      <SelectItem value="active">Actif</SelectItem>
                      <SelectItem value="expired">Expiré</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Table */}
          <Card className="bg-[#0a0a15] border-white/10">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-white/10 hover:bg-transparent">
                    <TableHead className="text-gray-400">Affilié</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Package</TableHead>
                    <TableHead className="text-gray-400">Placement</TableHead>
                    <TableHead className="text-gray-400">Prix</TableHead>
                    <TableHead className="text-gray-400">Performance</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {opportunities.map((opp) => (
                    <TableRow key={opp.opportunity_id} className="border-white/10 hover:bg-white/5">
                      <TableCell>
                        <div>
                          <p className="text-white font-medium">{opp.company_name}</p>
                          <p className="text-gray-500 text-xs">{opp.category}</p>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(opp.status)}</TableCell>
                      <TableCell>
                        {opp.selected_package ? (
                          <Badge variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
                            <Package className="h-3 w-3 mr-1" />
                            {opp.selected_package?.replace('_', ' ')}
                          </Badge>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {opp.selected_placement ? (
                          <span className="text-gray-300">{opp.selected_placement?.replace('_', ' ')}</span>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {opp.final_price ? (
                          <span className="text-green-400 font-medium">{formatCurrency(opp.final_price)}</span>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {opp.status === 'active' ? (
                          <div className="text-sm">
                            <span className="text-blue-400">{opp.impressions || 0}</span>
                            <span className="text-gray-500"> / </span>
                            <span className="text-purple-400">{opp.clicks || 0}</span>
                            <span className="text-gray-500"> / </span>
                            <span className="text-yellow-400">{opp.ctr || 0}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => viewOpportunityDetails(opp.opportunity_id)}
                            className="text-[#F5A623]"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {!opp.email_sent && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleSendEmail(opp.opportunity_id)}
                              className="text-blue-400"
                            >
                              <Mail className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {opportunities.length === 0 && !loading && (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-gray-400 py-8">
                        Aucune opportunité publicitaire. Activez des affiliés pour créer des opportunités.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Active Campaigns Tab */}
        <TabsContent value="active">
          <Card className="bg-[#0a0a15] border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Play className="h-5 w-5 text-green-400" />
                Campagnes Actives
              </CardTitle>
              <CardDescription className="text-gray-400">
                Publicités actuellement en diffusion sur les pages BIONIC
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {opportunities.filter(o => o.status === 'active').map((opp) => (
                  <div key={opp.opportunity_id} className="p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="text-white font-medium">{opp.company_name}</h4>
                        <p className="text-gray-400 text-sm">{opp.selected_placement?.replace('_', ' ')}</p>
                      </div>
                      <Badge className="bg-green-500/20 text-green-400">ACTIVE</Badge>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <p className="text-2xl font-bold text-blue-400">{opp.impressions || 0}</p>
                        <p className="text-gray-500 text-xs">Impressions</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-purple-400">{opp.clicks || 0}</p>
                        <p className="text-gray-500 text-xs">Clics</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-yellow-400">{opp.ctr || 0}%</p>
                        <p className="text-gray-500 text-xs">CTR</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-400">{formatCurrency(opp.final_price)}</p>
                        <p className="text-gray-500 text-xs">Revenu</p>
                      </div>
                    </div>
                    {opp.campaign_end && (
                      <div className="mt-3">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>Progression</span>
                          <span>Expire: {new Date(opp.campaign_end).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <Progress 
                          value={Math.min(100, Math.max(0, 
                            ((new Date() - new Date(opp.campaign_start)) / 
                            (new Date(opp.campaign_end) - new Date(opp.campaign_start))) * 100
                          ))} 
                          className="h-2"
                        />
                      </div>
                    )}
                  </div>
                ))}
                {opportunities.filter(o => o.status === 'active').length === 0 && (
                  <p className="text-center text-gray-400 py-8">
                    Aucune campagne active pour le moment
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Placements Tab */}
        <TabsContent value="placements">
          <Card className="bg-[#0a0a15] border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Globe className="h-5 w-5 text-purple-400" />
                Emplacements Publicitaires
              </CardTitle>
              <CardDescription className="text-gray-400">
                Distribution des publicités par emplacement
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bionicDashboard && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(bionicDashboard.by_placement || {}).map(([placement, count]) => (
                    <div key={placement} className="p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">{placement.replace('_', ' ')}</span>
                        <Badge className="bg-purple-500/20 text-purple-400">{count}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="bg-[#0a0a15] border-white/10 text-white max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-[#F5A623]" />
              {selectedOpp?.company_name}
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              Détails de l'opportunité publicitaire
            </DialogDescription>
          </DialogHeader>

          {selectedOpp && (
            <div className="space-y-4">
              {/* Status */}
              <div className="flex items-center justify-between p-3 bg-white/5 rounded">
                <span className="text-gray-400">Statut</span>
                {getStatusBadge(selectedOpp.status)}
              </div>

              {/* Package & Placement */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-white/5 rounded">
                  <p className="text-gray-400 text-sm">Package</p>
                  <p className="text-white">{selectedOpp.selected_package?.replace('_', ' ') || 'Non sélectionné'}</p>
                </div>
                <div className="p-3 bg-white/5 rounded">
                  <p className="text-gray-400 text-sm">Placement</p>
                  <p className="text-white">{selectedOpp.selected_placement?.replace('_', ' ') || 'Non sélectionné'}</p>
                </div>
              </div>

              {/* Pricing */}
              {selectedOpp.final_price && (
                <div className="p-3 bg-white/5 rounded">
                  <p className="text-gray-400 text-sm">Prix Final</p>
                  <p className="text-2xl font-bold text-green-400">{formatCurrency(selectedOpp.final_price)}</p>
                </div>
              )}

              {/* Campaign Dates */}
              {selectedOpp.campaign_start && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-white/5 rounded">
                    <p className="text-gray-400 text-sm">Début</p>
                    <p className="text-white">{new Date(selectedOpp.campaign_start).toLocaleDateString('fr-FR')}</p>
                  </div>
                  <div className="p-3 bg-white/5 rounded">
                    <p className="text-gray-400 text-sm">Fin</p>
                    <p className="text-white">{new Date(selectedOpp.campaign_end).toLocaleDateString('fr-FR')}</p>
                  </div>
                </div>
              )}

              {/* Performance */}
              {selectedOpp.status === 'active' && (
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 bg-blue-500/10 rounded text-center">
                    <p className="text-2xl font-bold text-blue-400">{selectedOpp.impressions || 0}</p>
                    <p className="text-gray-400 text-xs">Impressions</p>
                  </div>
                  <div className="p-3 bg-purple-500/10 rounded text-center">
                    <p className="text-2xl font-bold text-purple-400">{selectedOpp.clicks || 0}</p>
                    <p className="text-gray-400 text-xs">Clics</p>
                  </div>
                  <div className="p-3 bg-yellow-500/10 rounded text-center">
                    <p className="text-2xl font-bold text-yellow-400">{selectedOpp.ctr || 0}%</p>
                    <p className="text-gray-400 text-xs">CTR</p>
                  </div>
                </div>
              )}

              {/* Logs */}
              {selectedOpp.logs && selectedOpp.logs.length > 0 && (
                <div>
                  <h4 className="text-white font-medium mb-2">Historique</h4>
                  <div className="space-y-2 max-h-[200px] overflow-y-auto">
                    {selectedOpp.logs.map((log, idx) => (
                      <div key={idx} className="flex items-start gap-2 p-2 bg-white/5 rounded text-sm">
                        <ArrowRight className="h-4 w-4 text-gray-400 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-white">{log.action}</p>
                          <p className="text-gray-500 text-xs">
                            {new Date(log.timestamp).toLocaleString('fr-FR')} - {log.source}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminAffiliateAds;
