/**
 * AdminAffiliateSwitch - Affiliate Switch Engine Interface
 * ========================================================
 * 
 * Interface d'administration pour gérer les switches d'affiliation:
 * - Switch individuel ON/OFF
 * - Statut et validation
 * - Notes internes
 * - Historique des actions
 * - Actions marketing ciblées
 * 
 * Architecture LEGO V5-ULTIME
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
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
  Power, Users, Check, X, Clock, AlertTriangle,
  RefreshCw, Download, Search, Filter, Eye, Edit,
  FileCheck, Shield, Copy, ChevronRight, History,
  Zap, Mail, Globe, ExternalLink, BarChart3, Target
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminAffiliateSwitch = () => {
  const [affiliates, setAffiliates] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedAffiliate, setSelectedAffiliate] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    loadData();
  }, [page, statusFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load dashboard
      const dashRes = await fetch(`${API}/api/v1/affiliate-switch/dashboard`);
      const dashData = await dashRes.json();
      setDashboard(dashData.dashboard);

      // Load affiliates
      let url = `${API}/api/v1/affiliate-switch/affiliates?page=${page}&limit=20`;
      if (statusFilter !== 'all') url += `&status=${statusFilter}`;

      const affRes = await fetch(url);
      const affData = await affRes.json();
      setAffiliates(affData.affiliates || []);
      setPagination(affData.pagination || {});
    } catch (error) {
      console.error('Error loading affiliate data:', error);
      toast.error('Erreur lors du chargement');
    }
    setLoading(false);
  };

  const handleToggleSwitch = async (affiliateId, currentState) => {
    try {
      const res = await fetch(`${API}/api/v1/affiliate-switch/affiliates/${affiliateId}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          is_active: !currentState,
          reason: 'Activation manuelle admin',
          admin_user: 'admin'
        })
      });
      const data = await res.json();
      
      if (data.success) {
        toast.success(data.message);
        loadData();
      } else {
        toast.error(data.error || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur lors du toggle');
    }
  };

  const handleImportFromSuppliers = async () => {
    setImporting(true);
    try {
      const res = await fetch(`${API}/api/v1/affiliate-switch/bulk/import-from-suppliers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      
      if (data.success) {
        toast.success(data.message);
        loadData();
      } else {
        toast.error(data.error || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'import');
    }
    setImporting(false);
  };

  const viewAffiliateDetails = async (affiliateId) => {
    try {
      const res = await fetch(`${API}/api/v1/affiliate-switch/affiliates/${affiliateId}`);
      const data = await res.json();
      
      if (data.success) {
        setSelectedAffiliate({ ...data.affiliate, logs: data.logs });
        setShowDetailDialog(true);
      }
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      active: 'bg-green-500/20 text-green-400 border-green-500/30',
      inactive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      revoked: 'bg-red-500/20 text-red-400 border-red-500/30'
    };
    const icons = {
      pending: <Clock className="h-3 w-3 mr-1" />,
      active: <Check className="h-3 w-3 mr-1" />,
      inactive: <X className="h-3 w-3 mr-1" />,
      revoked: <AlertTriangle className="h-3 w-3 mr-1" />
    };
    return (
      <Badge className={`${styles[status] || styles.pending} flex items-center`}>
        {icons[status]}
        {status?.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="space-y-6" data-testid="admin-affiliate-switch">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Power className="h-6 w-6 text-[#F5A623]" />
            Affiliate Switch Engine
          </h2>
          <p className="text-gray-400 mt-1">
            Gestion des switches d'affiliation - Activation/désactivation automatique et manuelle
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleImportFromSuppliers}
            disabled={importing}
            className="border-purple-500/30 text-purple-400"
          >
            <Download className={`h-4 w-4 mr-2 ${importing ? 'animate-spin' : ''}`} />
            Import Fournisseurs SEO
          </Button>
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
      </div>

      {/* Dashboard Stats */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#F5A623]/20 flex items-center justify-center">
                  <Users className="h-5 w-5 text-[#F5A623]" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Total Affiliés</p>
                  <p className="text-2xl font-bold text-white">{dashboard.totals.total_affiliates}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Check className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Switches ON</p>
                  <p className="text-2xl font-bold text-white">{dashboard.switches.on}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-yellow-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-yellow-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Pending</p>
                  <p className="text-2xl font-bold text-white">{dashboard.totals.by_status.pending}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Shield className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Validés</p>
                  <p className="text-2xl font-bold text-white">{dashboard.validation.fully_validated}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <BarChart3 className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Taux Activation</p>
                  <p className="text-2xl font-bold text-white">{dashboard.switches.activation_rate}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-[#0a0a15] border-white/10">
        <CardContent className="p-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-gray-400 text-sm mb-1 block">Recherche</label>
              <Input
                placeholder="Nom de l'affilié..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#050510] border-white/10"
              />
            </div>
            <div className="w-[150px]">
              <label className="text-gray-400 text-sm mb-1 block">Statut</label>
              <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
                <SelectTrigger className="bg-[#050510] border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="revoked">Revoked</SelectItem>
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
                <TableHead className="text-gray-400 w-[60px]">Switch</TableHead>
                <TableHead className="text-gray-400">Affilié</TableHead>
                <TableHead className="text-gray-400">Catégorie</TableHead>
                <TableHead className="text-gray-400">Pays</TableHead>
                <TableHead className="text-gray-400">Statut</TableHead>
                <TableHead className="text-gray-400">Validation</TableHead>
                <TableHead className="text-gray-400">SEO</TableHead>
                <TableHead className="text-gray-400">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {affiliates.map((affiliate) => (
                <TableRow key={affiliate.affiliate_id} className="border-white/10 hover:bg-white/5">
                  <TableCell>
                    <Switch
                      checked={affiliate.switch_active}
                      onCheckedChange={() => handleToggleSwitch(affiliate.affiliate_id, affiliate.switch_active)}
                      className="data-[state=checked]:bg-green-500"
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-white font-medium">{affiliate.company_name}</p>
                      {affiliate.email && (
                        <p className="text-gray-500 text-xs">{affiliate.email}</p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
                      {(affiliate.category || 'N/A').replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-gray-300">
                      <Globe className="h-3 w-3" />
                      {affiliate.country || 'N/A'}
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(affiliate.status)}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {affiliate.validation?.identity_verified && <Check className="h-4 w-4 text-green-400" />}
                      {affiliate.validation?.category_verified && <Check className="h-4 w-4 text-green-400" />}
                      {affiliate.validation?.duplication_checked && <Check className="h-4 w-4 text-green-400" />}
                      {affiliate.validation?.compliance_passed && <Check className="h-4 w-4 text-green-400" />}
                      {!affiliate.validation?.all_validated && (
                        <span className="text-yellow-400 text-xs ml-1">
                          {Object.values(affiliate.validation || {}).filter(Boolean).length - 1}/4
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {affiliate.seo_integration?.satellite_page_active ? (
                      <Badge className="bg-green-500/20 text-green-400">
                        <Globe className="h-3 w-3 mr-1" /> Active
                      </Badge>
                    ) : (
                      <Badge className="bg-gray-500/20 text-gray-400">
                        Inactive
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => viewAffiliateDetails(affiliate.affiliate_id)}
                        className="text-[#F5A623] hover:text-[#F5A623]/80"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {affiliate.website && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => window.open(affiliate.website, '_blank')}
                          className="text-blue-400 hover:text-blue-300"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {affiliates.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-gray-400 py-8">
                    Aucun affilié trouvé. Utilisez "Import Fournisseurs SEO" pour commencer.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="bg-[#0a0a15] border-white/10 text-white max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Power className="h-5 w-5 text-[#F5A623]" />
              {selectedAffiliate?.company_name}
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              Détails de l'affilié et historique des actions
            </DialogDescription>
          </DialogHeader>

          {selectedAffiliate && (
            <Tabs defaultValue="info" className="mt-4">
              <TabsList className="bg-white/5">
                <TabsTrigger value="info">Informations</TabsTrigger>
                <TabsTrigger value="validation">Validation</TabsTrigger>
                <TabsTrigger value="sync">Synchronisation</TabsTrigger>
                <TabsTrigger value="history">Historique</TabsTrigger>
              </TabsList>

              <TabsContent value="info" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-sm">Email</p>
                    <p className="text-white">{selectedAffiliate.email || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Contact</p>
                    <p className="text-white">{selectedAffiliate.contact_name || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Site Web</p>
                    <p className="text-blue-400">{selectedAffiliate.website || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Catégorie</p>
                    <p className="text-white">{selectedAffiliate.category || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Pays</p>
                    <p className="text-white">{selectedAffiliate.country || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Statut</p>
                    {getStatusBadge(selectedAffiliate.status)}
                  </div>
                </div>
                {selectedAffiliate.admin_notes && (
                  <div>
                    <p className="text-gray-400 text-sm">Notes Admin</p>
                    <p className="text-white bg-white/5 p-2 rounded mt-1">{selectedAffiliate.admin_notes}</p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="validation" className="space-y-4 mt-4">
                <div className="space-y-3">
                  {[
                    { key: 'identity_verified', label: 'Vérification identité', icon: Shield },
                    { key: 'category_verified', label: 'Vérification catégorie', icon: Target },
                    { key: 'duplication_checked', label: 'Détection duplication', icon: Copy },
                    { key: 'compliance_passed', label: 'Conformité', icon: FileCheck }
                  ].map(({ key, label, icon: Icon }) => (
                    <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded">
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4 text-gray-400" />
                        <span className="text-white">{label}</span>
                      </div>
                      {selectedAffiliate.validation?.[key] ? (
                        <Badge className="bg-green-500/20 text-green-400">
                          <Check className="h-3 w-3 mr-1" /> Validé
                        </Badge>
                      ) : (
                        <Badge className="bg-yellow-500/20 text-yellow-400">
                          <Clock className="h-3 w-3 mr-1" /> En attente
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="sync" className="space-y-4 mt-4">
                <div className="space-y-3">
                  {[
                    { key: 'seo_engine', label: 'SEO Engine' },
                    { key: 'contact_engine', label: 'Contact Engine' },
                    { key: 'trigger_engine', label: 'Trigger Engine' },
                    { key: 'calendar_engine', label: 'Calendar Engine' },
                    { key: 'marketing_engine', label: 'Marketing Engine' }
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded">
                      <span className="text-white">{label}</span>
                      {selectedAffiliate.engine_sync?.[key] ? (
                        <Badge className="bg-green-500/20 text-green-400">
                          <Zap className="h-3 w-3 mr-1" /> Synchronisé
                        </Badge>
                      ) : (
                        <Badge className="bg-gray-500/20 text-gray-400">
                          Non synchronisé
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="history" className="space-y-4 mt-4">
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {(selectedAffiliate.logs || []).map((log, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-2 bg-white/5 rounded text-sm">
                      <History className="h-4 w-4 text-gray-400 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-white">{log.action}</p>
                        <p className="text-gray-500 text-xs">
                          {new Date(log.timestamp).toLocaleString('fr-FR')} - {log.source}
                        </p>
                      </div>
                    </div>
                  ))}
                  {(selectedAffiliate.logs || []).length === 0 && (
                    <p className="text-gray-400 text-center py-4">Aucun historique</p>
                  )}
                </div>
              </TabsContent>
            </Tabs>
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

export default AdminAffiliateSwitch;
