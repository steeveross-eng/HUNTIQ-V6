/**
 * PartnershipAdmin - Admin panel for managing partner requests and official partners
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Handshake,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Eye,
  Mail,
  Phone,
  Globe,
  Building2,
  FileText,
  RefreshCw,
  UserCheck,
  UserX,
  ExternalLink,
  AlertTriangle,
  TrendingUp,
  Star,
  MessageSquare,
  MoreVertical,
  Send,
  ArrowUpRight,
  Settings,
  MailCheck,
  MailX,
  Bell,
  BellOff,
  ArrowLeft,
  Home,
  ArrowUpDown,
  Database,
  TreePine,
  Target,
  MapPin,
  Tent,
  Lock,
  CircleDot
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Status badge colors
const STATUS_STYLES = {
  pending: { bg: 'bg-yellow-500/20', text: 'text-yellow-500', label: 'En attente' },
  reviewed: { bg: 'bg-blue-500/20', text: 'text-blue-500', label: 'En révision' },
  approved: { bg: 'bg-green-500/20', text: 'text-green-500', label: 'Approuvé' },
  rejected: { bg: 'bg-red-500/20', text: 'text-red-500', label: 'Refusé' },
  converted: { bg: 'bg-purple-500/20', text: 'text-purple-500', label: 'Converti' }
};

// Partner type icons - BIONIC Design System (Lucide icons)
const PARTNER_TYPE_ICONS = {
  marques: { Icon: Building2, color: '#f5a623' },
  pourvoiries: { Icon: Home, color: '#22c55e' },
  proprietaires: { Icon: TreePine, color: '#10b981' },
  guides: { Icon: Target, color: '#ef4444' },
  boutiques: { Icon: Building2, color: '#8b5cf6' },
  services: { Icon: Settings, color: '#6b7280' },
  fabricants: { Icon: Building2, color: '#64748b' },
  zec: { Icon: MapPin, color: '#3b82f6' },
  clubs: { Icon: Users, color: '#06b6d4' },
  particuliers: { Icon: UserCheck, color: '#a855f7' },
  autres: { Icon: FileText, color: '#9ca3af' }
};

// Type icons for territories - BIONIC Design System (Lucide icons)
const TYPE_ICONS = {
  pourvoirie: { Icon: Home, color: '#3b82f6' },
  pourvoiries: { Icon: Home, color: '#3b82f6' },
  sepaq: { Icon: TreePine, color: '#22c55e' },
  zec: { Icon: Tent, color: '#22c55e' },
  club: { Icon: Target, color: '#ef4444' },
  clubs: { Icon: Target, color: '#ef4444' },
  outfitter: { Icon: Home, color: '#3b82f6' },
  reserve: { Icon: TreePine, color: '#10b981' },
  anticosti: { Icon: Globe, color: '#06b6d4' },
  private: { Icon: Lock, color: '#f59e0b' },
  proprietaires: { Icon: UserCheck, color: '#a855f7' }
};

const PartnershipAdmin = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('requests');
  const [requests, setRequests] = useState([]);
  const [partners, setPartners] = useState([]);
  const [territoryPartners, setTerritoryPartners] = useState([]);
  const [territoryStats, setTerritoryStats] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showPartnerModal, setShowPartnerModal] = useState(false);
  const [importingTerritories, setImportingTerritories] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [syncingAll, setSyncingAll] = useState(false);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Admin notes
  const [adminNotes, setAdminNotes] = useState('');
  
  // Email settings
  const [emailSettings, setEmailSettings] = useState({
    acknowledgment_enabled: true,
    admin_notification_enabled: true,
    approval_enabled: true,
    rejection_enabled: true
  });
  const [emailSettingsLoading, setEmailSettingsLoading] = useState(false);

  // Helper function declaration first
  const formatDate = (date) => {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('fr-CA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Load functions - declared before useEffect
  const loadSyncStatus = async () => {
    try {
      const response = await axios.get(`${API}/api/territories/sync/status`);
      if (response.data.success) {
        setSyncStatus(response.data.status);
      }
    } catch (error) {
      console.error('Error loading sync status:', error);
    }
  };

  const loadRequests = async () => {
    try {
      const params = {};
      if (statusFilter !== 'all') params.status = statusFilter;
      if (typeFilter !== 'all') params.partner_type = typeFilter;
      if (searchQuery) params.search = searchQuery;
      
      const response = await axios.get(`${API}/api/partnership/requests`, { params });
      setRequests(response.data);
    } catch (error) {
      console.error('Error loading requests:', error);
    }
  };

  const loadPartners = async () => {
    try {
      const params = {};
      if (typeFilter !== 'all') params.partner_type = typeFilter;
      if (searchQuery) params.search = searchQuery;
      
      const response = await axios.get(`${API}/api/partnership/partners`, { params });
      setPartners(response.data);
    } catch (error) {
      console.error('Error loading partners:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/api/partnership/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadEmailSettings = async () => {
    try {
      const response = await axios.get(`${API}/api/partnership/admin/email-settings`);
      if (response.data.success) {
        setEmailSettings(response.data.settings);
      }
    } catch (error) {
      console.error('Error loading email settings:', error);
    }
  };

  const loadTerritoryPartners = async () => {
    try {
      const params = {};
      if (typeFilter !== 'all') params.type = typeFilter;
      if (searchQuery) params.search = searchQuery;
      
      const response = await axios.get(`${API}/api/territories/partnership/list`, { params });
      if (response.data.success) {
        setTerritoryPartners(response.data.territories);
        setTerritoryStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error loading territory partners:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([loadRequests(), loadPartners(), loadStats(), loadEmailSettings(), loadTerritoryPartners(), loadSyncStatus()]);
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  // useEffect hooks - after function declarations
  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeTab === 'requests') {
      loadRequests();
    } else if (activeTab === 'partners') {
      loadPartners();
    } else if (activeTab === 'territories') {
      loadTerritoryPartners();
    } else if (activeTab === 'settings') {
      loadEmailSettings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, typeFilter, searchQuery, activeTab]);

  // Sync functions
  const syncAllToPartnership = async () => {
    setSyncingAll(true);
    try {
      const response = await axios.post(`${API}/api/territories/sync/all-to-partnership`);
      if (response.data.success) {
        toast.success(`${response.data.synced} territoires synchronisés vers partenariats`);
        await loadSyncStatus();
        await loadTerritoryPartners();
      } else {
        toast.error(t('toast_sync_error'));
      }
    } catch (error) {
      console.error('Error syncing all:', error);
      toast.error(t('toast_sync_error'));
    }
    setSyncingAll(false);
  };

  const syncAllFromPartnership = async () => {
    setSyncingAll(true);
    try {
      const response = await axios.post(`${API}/api/territories/sync/all-from-partnership`);
      if (response.data.success) {
        toast.success(`${response.data.synced} partenariats synchronisés vers territoires`);
        await loadSyncStatus();
      } else {
        toast.error(t('toast_sync_reverse_error'));
      }
    } catch (error) {
      console.error('Error syncing from partnership:', error);
      toast.error(t('toast_sync_reverse_error'));
    }
    setSyncingAll(false);
  };

  const importTerritories = async () => {
    setImportingTerritories(true);
    try {
      const response = await axios.post(`${API}/api/territories/import-from-inventory`);
      if (response.data.success) {
        toast.success(`${response.data.imported} territoires importés`);
        await loadTerritoryPartners();
        await loadSyncStatus();
      }
    } catch (error) {
      console.error('Error importing territories:', error);
      toast.error('Erreur lors de l\'import des territoires');
    }
    setImportingTerritories(false);
  };

  const handleToggleEmailSetting = async (settingType) => {
    setEmailSettingsLoading(true);
    try {
      const response = await axios.post(`${API}/api/partnership/admin/email-settings/toggle/${settingType}`);
      if (response.data.success) {
        setEmailSettings(prev => ({
          ...prev,
          [`${settingType}_enabled`]: response.data.enabled
        }));
        toast.success(response.data.message);
      }
    } catch (error) {
      toast.error('Erreur lors de la modification');
      console.error('Error toggling email setting:', error);
    }
    setEmailSettingsLoading(false);
  };

  const handleUpdateRequest = async (requestId, status) => {
    try {
      await axios.put(`${API}/api/partnership/requests/${requestId}`, {
        status,
        admin_notes: adminNotes
      });
      toast.success(status === 'approved' ? 'Demande approuvée!' : status === 'rejected' ? 'Demande refusée' : 'Demande mise à jour');
      loadData();
      setShowRequestModal(false);
      setAdminNotes('');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleConvertToPartner = async (requestId) => {
    try {
      await axios.post(`${API}/api/partnership/requests/${requestId}/convert`);
      toast.success('Partenaire créé avec succès!');
      loadData();
      setShowRequestModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la conversion');
    }
  };

  const handleTogglePartnerStatus = async (partnerId) => {
    try {
      const response = await axios.post(`${API}/api/partnership/partners/${partnerId}/toggle-status`);
      toast.success(response.data.message);
      loadPartners();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleApprove = async (partnerId) => {
    try {
      const response = await axios.post(`${API}/api/territories/partnership/${partnerId}/approve`);
      if (response.data.success) {
        toast.success('Partenaire approuvé avec succès');
        await loadTerritoryPartners();
      } else {
        toast.error('Erreur lors de l\'approbation');
      }
    } catch (error) {
      console.error('Error approving partner:', error);
      toast.error('Erreur lors de l\'approbation');
    }
  };

  const viewRequest = (request) => {
    setSelectedRequest(request);
    setAdminNotes(request.admin_notes || '');
    setShowRequestModal(true);
  };

  const viewPartner = (partner) => {
    setSelectedPartner(partner);
    setShowPartnerModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-yellow-500/10 border-yellow-500/30">
            <CardContent className="p-4 text-center">
              <Clock className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-yellow-500">{stats.requests.pending}</p>
              <p className="text-xs text-gray-400">En attente</p>
            </CardContent>
          </Card>
          <Card className="bg-green-500/10 border-green-500/30">
            <CardContent className="p-4 text-center">
              <CheckCircle className="h-6 w-6 text-green-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-500">{stats.requests.approved}</p>
              <p className="text-xs text-gray-400">Approuvées</p>
            </CardContent>
          </Card>
          <Card className="bg-purple-500/10 border-purple-500/30">
            <CardContent className="p-4 text-center">
              <UserCheck className="h-6 w-6 text-purple-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-purple-500">{stats.partners.active}</p>
              <p className="text-xs text-gray-400">Partenaires actifs</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-500/10 border-blue-500/30">
            <CardContent className="p-4 text-center">
              <Handshake className="h-6 w-6 text-blue-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-blue-500">{stats.partners.total}</p>
              <p className="text-xs text-gray-400">Total partenaires</p>
            </CardContent>
          </Card>
          <Card className="bg-red-500/10 border-red-500/30">
            <CardContent className="p-4 text-center">
              <XCircle className="h-6 w-6 text-red-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-red-500">{stats.requests.rejected}</p>
              <p className="text-xs text-gray-400">Refusées</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between mb-4">
          <TabsList className="bg-card border border-border">
            <TabsTrigger value="requests" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <FileText className="h-4 w-4 mr-2" />
              Demandes ({stats?.requests.pending || 0})
            </TabsTrigger>
            <TabsTrigger value="partners" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Users className="h-4 w-4 mr-2" />
              Partenaires ({stats?.partners.total || 0})
            </TabsTrigger>
            <TabsTrigger value="territories" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Building2 className="h-4 w-4 mr-2" />
              Pourvoyeurs ({territoryStats?.total || 0})
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Settings className="h-4 w-4 mr-2" />
              Paramètres
            </TabsTrigger>
          </TabsList>
          <Button variant="outline" onClick={loadData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {t('common_refresh')}
          </Button>
        </div>

        {/* Filters */}
        <Card className="bg-card border-border mb-4">
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                  <Input
                    placeholder="Rechercher..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-background pl-10"
                  />
                </div>
              </div>
              {activeTab === 'requests' && (
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px] bg-background">
                    <SelectValue placeholder="Statut" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les statuts</SelectItem>
                    <SelectItem value="pending">En attente</SelectItem>
                    <SelectItem value="reviewed">En révision</SelectItem>
                    <SelectItem value="approved">Approuvées</SelectItem>
                    <SelectItem value="rejected">Refusées</SelectItem>
                    <SelectItem value="converted">Converties</SelectItem>
                  </SelectContent>
                </Select>
              )}
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[200px] bg-background">
                  <SelectValue placeholder="Type de partenaire" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les types</SelectItem>
                  <SelectItem value="marques">
                    <span className="flex items-center gap-2"><Building2 className="h-4 w-4" style={{ color: '#f5a623' }} /> Marques</span>
                  </SelectItem>
                  <SelectItem value="pourvoiries">
                    <span className="flex items-center gap-2"><Home className="h-4 w-4" style={{ color: '#22c55e' }} /> Pourvoiries</span>
                  </SelectItem>
                  <SelectItem value="proprietaires">
                    <span className="flex items-center gap-2"><TreePine className="h-4 w-4" style={{ color: '#10b981' }} /> Propriétaires</span>
                  </SelectItem>
                  <SelectItem value="guides">
                    <span className="flex items-center gap-2"><Target className="h-4 w-4" style={{ color: '#ef4444' }} /> Guides</span>
                  </SelectItem>
                  <SelectItem value="boutiques">
                    <span className="flex items-center gap-2"><Building2 className="h-4 w-4" style={{ color: '#8b5cf6' }} /> Boutiques</span>
                  </SelectItem>
                  <SelectItem value="services">
                    <span className="flex items-center gap-2"><Settings className="h-4 w-4" style={{ color: '#6b7280' }} /> Services</span>
                  </SelectItem>
                  <SelectItem value="fabricants">
                    <span className="flex items-center gap-2"><Building2 className="h-4 w-4" style={{ color: '#64748b' }} /> Fabricants</span>
                  </SelectItem>
                  <SelectItem value="zec">
                    <span className="flex items-center gap-2"><MapPin className="h-4 w-4" style={{ color: '#3b82f6' }} /> ZEC</span>
                  </SelectItem>
                  <SelectItem value="clubs">
                    <span className="flex items-center gap-2"><Users className="h-4 w-4" style={{ color: '#06b6d4' }} /> Clubs privés</span>
                  </SelectItem>
                  <SelectItem value="particuliers">
                    <span className="flex items-center gap-2"><UserCheck className="h-4 w-4" style={{ color: '#a855f7' }} /> Particuliers</span>
                  </SelectItem>
                  <SelectItem value="autres">
                    <span className="flex items-center gap-2"><FileText className="h-4 w-4" style={{ color: '#9ca3af' }} /> Autres</span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Requests Tab */}
        <TabsContent value="requests">
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Entreprise</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Contact</TableHead>
                    <TableHead className="text-gray-400">Date</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requests.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                        Aucune demande trouvée
                      </TableCell>
                    </TableRow>
                  ) : (
                    requests.map((request) => (
                      <TableRow key={request.id} className="hover:bg-background/50">
                        <TableCell>
                          <div>
                            <p className="text-white font-medium">{request.company_name}</p>
                            <p className="text-gray-500 text-xs">{request.email}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-[#f5a623]/50 text-[#f5a623]">
                            {PARTNER_TYPE_ICONS[request.partner_type]} {request.partner_type_label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-gray-300">{request.contact_name}</p>
                            <p className="text-gray-500 text-xs">{request.phone}</p>
                          </div>
                        </TableCell>
                        <TableCell className="text-gray-400 text-sm">
                          {formatDate(request.created_at)}
                        </TableCell>
                        <TableCell>
                          <Badge className={`${STATUS_STYLES[request.status]?.bg} ${STATUS_STYLES[request.status]?.text}`}>
                            {STATUS_STYLES[request.status]?.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm" onClick={() => viewRequest(request)}>
                            <Eye className="h-4 w-4 mr-1" /> Voir
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Partners Tab */}
        <TabsContent value="partners">
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Partenaire</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Contact</TableHead>
                    <TableHead className="text-gray-400">Commission</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {partners.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                        Aucun partenaire trouvé
                      </TableCell>
                    </TableRow>
                  ) : (
                    partners.map((partner) => (
                      <TableRow key={partner.id} className="hover:bg-background/50">
                        <TableCell>
                          <div>
                            <p className="text-white font-medium">{partner.company_name}</p>
                            <p className="text-gray-500 text-xs">{partner.email}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-[#f5a623]/50 text-[#f5a623]">
                            {PARTNER_TYPE_ICONS[partner.partner_type]} {partner.partner_type_label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-gray-300">{partner.contact_name}</p>
                            <p className="text-gray-500 text-xs">{partner.phone}</p>
                          </div>
                        </TableCell>
                        <TableCell className="text-[#f5a623] font-medium">
                          {partner.commission_rate}%
                        </TableCell>
                        <TableCell>
                          <Badge className={partner.is_active ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}>
                            {partner.is_active ? 'Actif' : 'Suspendu'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => viewPartner(partner)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleTogglePartnerStatus(partner.id)}
                            className={partner.is_active ? 'text-red-500' : 'text-green-500'}
                          >
                            {partner.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Mail className="h-5 w-5 text-[#f5a623]" />
                Notifications Email
              </CardTitle>
              <CardDescription>
                Contrôlez l&apos;envoi automatique des emails du système de partenariat
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Email Settings Grid */}
              <div className="grid gap-4">
                {/* Acknowledgment Email */}
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${emailSettings.acknowledgment_enabled ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
                      {emailSettings.acknowledgment_enabled ? (
                        <MailCheck className="h-5 w-5 text-green-500" />
                      ) : (
                        <MailX className="h-5 w-5 text-gray-500" />
                      )}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Accusé de réception</h4>
                      <p className="text-gray-400 text-sm">Email envoyé au partenaire lors de la soumission de sa demande</p>
                    </div>
                  </div>
                  <Switch
                    checked={emailSettings.acknowledgment_enabled}
                    onCheckedChange={() => handleToggleEmailSetting('acknowledgment')}
                    disabled={emailSettingsLoading}
                    data-testid="email-toggle-acknowledgment"
                  />
                </div>

                {/* Admin Notification Email */}
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${emailSettings.admin_notification_enabled ? 'bg-blue-500/20' : 'bg-gray-500/20'}`}>
                      {emailSettings.admin_notification_enabled ? (
                        <Bell className="h-5 w-5 text-blue-500" />
                      ) : (
                        <BellOff className="h-5 w-5 text-gray-500" />
                      )}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Notification administrateur</h4>
                      <p className="text-gray-400 text-sm">Email envoyé à l&apos;admin lorsqu&apos;une nouvelle demande est soumise</p>
                    </div>
                  </div>
                  <Switch
                    checked={emailSettings.admin_notification_enabled}
                    onCheckedChange={() => handleToggleEmailSetting('admin_notification')}
                    disabled={emailSettingsLoading}
                    data-testid="email-toggle-admin"
                  />
                </div>

                {/* Approval Email */}
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${emailSettings.approval_enabled ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
                      {emailSettings.approval_enabled ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <MailX className="h-5 w-5 text-gray-500" />
                      )}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Email d&apos;approbation</h4>
                      <p className="text-gray-400 text-sm">Email envoyé au partenaire lorsque sa demande est approuvée</p>
                    </div>
                  </div>
                  <Switch
                    checked={emailSettings.approval_enabled}
                    onCheckedChange={() => handleToggleEmailSetting('approval')}
                    disabled={emailSettingsLoading}
                    data-testid="email-toggle-approval"
                  />
                </div>

                {/* Rejection Email */}
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${emailSettings.rejection_enabled ? 'bg-red-500/20' : 'bg-gray-500/20'}`}>
                      {emailSettings.rejection_enabled ? (
                        <XCircle className="h-5 w-5 text-red-500" />
                      ) : (
                        <MailX className="h-5 w-5 text-gray-500" />
                      )}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">Email de refus</h4>
                      <p className="text-gray-400 text-sm">Email envoyé au partenaire lorsque sa demande est refusée</p>
                    </div>
                  </div>
                  <Switch
                    checked={emailSettings.rejection_enabled}
                    onCheckedChange={() => handleToggleEmailSetting('rejection')}
                    disabled={emailSettingsLoading}
                    data-testid="email-toggle-rejection"
                  />
                </div>
              </div>

              {/* Status Summary */}
              <div className="p-4 bg-[#f5a623]/10 rounded-lg border border-[#f5a623]/30">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-[#f5a623]" />
                  <span className="text-[#f5a623] font-medium">Résumé</span>
                </div>
                <p className="text-gray-300 text-sm">
                  {Object.values(emailSettings).filter(v => v === true).length} / 4 types d&apos;emails sont actuellement activés.
                  {emailSettings.updated_at && (
                    <span className="text-gray-500 ml-2">
                      Dernière modification: {formatDate(emailSettings.updated_at)}
                    </span>
                  )}
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Territories Tab - Pourvoyeurs from Inventory */}
        <TabsContent value="territories" className="space-y-4">
          {/* Sync Status Card */}
          {syncStatus && (
            <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30">
              <CardContent className="p-4">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Database className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold flex items-center gap-2">
                        <ArrowUpDown className="h-4 w-4 text-blue-400" />
                        Synchronisation Bidirectionnelle
                      </h3>
                      <div className="flex items-center gap-4 mt-1 text-sm">
                        <span className="text-gray-400">
                          <span className="text-blue-400 font-bold">{syncStatus.synced_to_partnership}</span>/{syncStatus.total_territories} synchros
                        </span>
                        <span className="text-gray-400">
                          <span className="text-green-400 font-bold">{syncStatus.territories_as_partners}</span> partenaires actifs
                        </span>
                        <Badge className={`${syncStatus.sync_percentage === 100 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                          {syncStatus.sync_percentage}% synchronisé
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      size="sm"
                      variant="outline"
                      onClick={syncAllToPartnership}
                      disabled={syncingAll}
                      className="border-blue-500/50 text-blue-400 hover:bg-blue-500/10"
                    >
                      {syncingAll ? <RefreshCw className="h-4 w-4 mr-1 animate-spin" /> : <ArrowUpDown className="h-4 w-4 mr-1" />}
                      Terr → Part
                    </Button>
                    <Button 
                      size="sm"
                      variant="outline"
                      onClick={syncAllFromPartnership}
                      disabled={syncingAll}
                      className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
                    >
                      {syncingAll ? <RefreshCw className="h-4 w-4 mr-1 animate-spin" /> : <ArrowUpDown className="h-4 w-4 mr-1" />}
                      Part → Terr
                    </Button>
                  </div>
                </div>
                {syncStatus.last_partner_sync && (
                  <p className="text-gray-500 text-xs mt-2">
                    Dernière sync: {formatDate(syncStatus.last_partner_sync)}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Territory Stats */}
          {territoryStats && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <Card className="bg-[#f5a623]/10 border-[#f5a623]/30">
                <CardContent className="p-3 text-center">
                  <p className="text-2xl font-bold text-[#f5a623]">{territoryStats.total}</p>
                  <p className="text-xs text-gray-400">Total</p>
                </CardContent>
              </Card>
              <Card className="bg-yellow-500/10 border-yellow-500/30">
                <CardContent className="p-3 text-center">
                  <p className="text-2xl font-bold text-yellow-500">{territoryStats.pending}</p>
                  <p className="text-xs text-gray-400">En attente</p>
                </CardContent>
              </Card>
              <Card className="bg-green-500/10 border-green-500/30">
                <CardContent className="p-3 text-center">
                  <p className="text-2xl font-bold text-green-500">{territoryStats.approved}</p>
                  <p className="text-xs text-gray-400">Approuvés</p>
                </CardContent>
              </Card>
              <Card className="bg-purple-500/10 border-purple-500/30">
                <CardContent className="p-3 text-center">
                  <p className="text-2xl font-bold text-purple-500">{territoryStats.by_type?.pourvoiries || 0}</p>
                  <p className="text-xs text-gray-400">Pourvoiries</p>
                </CardContent>
              </Card>
              <Card className="bg-blue-500/10 border-blue-500/30">
                <CardContent className="p-3 text-center">
                  <p className="text-2xl font-bold text-blue-500">{territoryStats.by_type?.zec || 0}</p>
                  <p className="text-xs text-gray-400">ZECs</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Import Button & Info */}
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-semibold flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-[#f5a623]" />
                    Pourvoyeurs depuis l&apos;Inventaire des Territoires
                  </h3>
                  <p className="text-gray-400 text-sm mt-1">
                    Les 78 pourvoyeurs de l&apos;onglet &quot;Analysez&quot; sont synchronisés ici pour une gestion centralisée.
                  </p>
                </div>
                <Button 
                  onClick={importTerritories} 
                  disabled={importingTerritories}
                  className="bg-[#f5a623] text-black hover:bg-[#f5a623]/90"
                >
                  {importingTerritories ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  Synchroniser
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Province Filter */}
          <Card className="bg-card border-border">
            <CardContent className="p-3">
              <div className="flex flex-wrap gap-2">
                <Badge 
                  variant="outline" 
                  className={`cursor-pointer ${typeFilter === 'all' ? 'bg-[#f5a623] text-black' : ''}`}
                  onClick={() => setTypeFilter('all')}
                >
                  Tous ({territoryStats?.total || 0})
                </Badge>
                {Object.entries(territoryStats?.by_type || {}).map(([type, count]) => {
                  const typeConfig = TYPE_ICONS[type];
                  const IconComponent = typeConfig?.Icon || FileText;
                  return (
                    <Badge 
                      key={type}
                      variant="outline" 
                      className={`cursor-pointer ${typeFilter === type ? 'bg-[#f5a623] text-black' : ''}`}
                      onClick={() => setTypeFilter(type)}
                    >
                      <IconComponent className="h-3 w-3 mr-1" style={{ color: typeConfig?.color || '#9ca3af' }} /> {type} ({count})
                    </Badge>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Territory Partners Table */}
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Province</TableHead>
                    <TableHead className="text-gray-400">Score</TableHead>
                    <TableHead className="text-gray-400">Espèces</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {territoryPartners
                    .filter(p => typeFilter === 'all' || p.partner_type === typeFilter)
                    .filter(p => !searchQuery || p.company_name?.toLowerCase().includes(searchQuery.toLowerCase()))
                    .map((partner) => (
                    <TableRow key={partner.id} className="border-border hover:bg-gray-900/50">
                      <TableCell>
                        <div>
                          <p className="text-white font-medium text-sm">{partner.company_name}</p>
                          <p className="text-gray-500 text-xs">{partner.region}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs flex items-center gap-1">
                          {(() => {
                            const typeConfig = TYPE_ICONS[partner.establishment_type];
                            const IconComponent = typeConfig?.Icon || FileText;
                            return <IconComponent className="h-3 w-3" style={{ color: typeConfig?.color || '#9ca3af' }} />;
                          })()}
                          {partner.establishment_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-300 text-sm">{partner.province}</TableCell>
                      <TableCell>
                        <span className={`font-bold ${
                          (partner.scoring?.global_score || 0) >= 70 ? 'text-green-400' :
                          (partner.scoring?.global_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {partner.scoring?.global_score?.toFixed(1) || 'N/D'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-0.5">
                          {(partner.species || []).slice(0, 3).map(s => (
                            <span key={s} className="text-sm flex items-center" title={s}>
                              <CircleDot className="h-4 w-4" style={{ 
                                color: s === 'orignal' ? '#8B4513' : s === 'ours' ? '#2F4F4F' : s === 'chevreuil' ? '#D2691E' : '#ef4444' 
                              }} />
                            </span>
                          ))}
                          {(partner.species?.length || 0) > 3 && (
                            <span className="text-gray-500 text-xs">+{partner.species.length - 3}</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${
                          partner.status === 'approved' ? 'bg-green-500/20 text-green-400' :
                          partner.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {partner.status === 'approved' ? 'Approuvé' : 
                           partner.status === 'pending' ? 'En attente' : partner.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {partner.website && (
                            <Button variant="ghost" size="sm" asChild className="h-7 px-2">
                              <a href={partner.website} target="_blank" rel="noopener noreferrer">
                                <Globe className="h-3 w-3" />
                              </a>
                            </Button>
                          )}
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-7 px-2"
                            onClick={() => {
                              setSelectedRequest(partner);
                              setShowRequestModal(true);
                            }}
                          >
                            <Eye className="h-3 w-3" />
                          </Button>
                          {partner.status === 'pending' && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="h-7 px-2 text-green-400 hover:text-green-300"
                              onClick={() => handleApprove(partner.id)}
                            >
                              <CheckCircle className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {territoryPartners.length === 0 && (
                <div className="p-8 text-center">
                  <Building2 className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">Aucun pourvoyeur importé</p>
                  <Button 
                    onClick={importTerritories} 
                    className="mt-4 bg-[#f5a623] text-black"
                    disabled={importingTerritories}
                  >
                    Importer les territoires
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Request Detail Modal */}
      <Dialog open={showRequestModal} onOpenChange={setShowRequestModal}>
        <DialogContent className="bg-card border-border text-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-[#f5a623]" />
              {selectedRequest?.company_name}
            </DialogTitle>
            <DialogDescription>
              Demande soumise le {formatDate(selectedRequest?.created_at)}
            </DialogDescription>
          </DialogHeader>
          
          {selectedRequest && (
            <div className="space-y-4">
              {/* Status */}
              <div className="flex items-center gap-2">
                <Badge className={`${STATUS_STYLES[selectedRequest.status]?.bg} ${STATUS_STYLES[selectedRequest.status]?.text}`}>
                  {STATUS_STYLES[selectedRequest.status]?.label}
                </Badge>
                <Badge variant="outline" className="border-[#f5a623]/50 text-[#f5a623]">
                  {PARTNER_TYPE_ICONS[selectedRequest.partner_type]} {selectedRequest.partner_type_label}
                </Badge>
              </div>

              {/* Contact Info */}
              <Card className="bg-background/50 border-border">
                <CardContent className="p-4 space-y-3">
                  <h4 className="text-sm font-medium text-gray-400">Informations de contact</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-gray-500" />
                      <a href={`mailto:${selectedRequest.email}`} className="text-[#f5a623] hover:underline">
                        {selectedRequest.email}
                      </a>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-gray-500" />
                      <span>{selectedRequest.phone}</span>
                    </div>
                    {selectedRequest.website && (
                      <div className="flex items-center gap-2 col-span-2">
                        <Globe className="h-4 w-4 text-gray-500" />
                        <a href={selectedRequest.website} target="_blank" rel="noopener noreferrer" className="text-[#f5a623] hover:underline flex items-center gap-1">
                          {selectedRequest.website} <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Description */}
              <Card className="bg-background/50 border-border">
                <CardContent className="p-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Description du partenariat</h4>
                  <p className="text-gray-300 text-sm whitespace-pre-wrap">{selectedRequest.description}</p>
                </CardContent>
              </Card>

              {/* Products/Services */}
              <Card className="bg-background/50 border-border">
                <CardContent className="p-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Produits / Services</h4>
                  <p className="text-gray-300 text-sm whitespace-pre-wrap">{selectedRequest.products_services}</p>
                </CardContent>
              </Card>

              {/* Admin Notes */}
              <div>
                <Label className="text-gray-400">Notes administrateur</Label>
                <Textarea
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Ajouter des notes internes..."
                  className="bg-background mt-1"
                />
              </div>
            </div>
          )}

          <DialogFooter className="flex-wrap gap-2">
            {selectedRequest?.status === 'pending' && (
              <>
                <Button 
                  variant="outline" 
                  className="border-red-500 text-red-500 hover:bg-red-500/10"
                  onClick={() => handleUpdateRequest(selectedRequest.id, 'rejected')}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Refuser
                </Button>
                <Button 
                  className="bg-green-600 hover:bg-green-700"
                  onClick={() => handleUpdateRequest(selectedRequest.id, 'approved')}
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approuver
                </Button>
              </>
            )}
            {selectedRequest?.status === 'approved' && (
              <Button 
                className="btn-golden text-black"
                onClick={() => handleConvertToPartner(selectedRequest.id)}
              >
                <UserCheck className="h-4 w-4 mr-2" />
                Convertir en partenaire
              </Button>
            )}
            <Button variant="outline" onClick={() => setShowRequestModal(false)}>
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Partner Detail Modal */}
      <Dialog open={showPartnerModal} onOpenChange={setShowPartnerModal}>
        <DialogContent className="bg-card border-border text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Handshake className="h-5 w-5 text-[#f5a623]" />
              {selectedPartner?.company_name}
            </DialogTitle>
            <DialogDescription>
              Partenaire depuis le {formatDate(selectedPartner?.created_at)}
            </DialogDescription>
          </DialogHeader>
          
          {selectedPartner && (
            <div className="space-y-4">
              {/* Status & Type */}
              <div className="flex items-center gap-2">
                <Badge className={selectedPartner.is_active ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}>
                  {selectedPartner.is_active ? 'Actif' : 'Suspendu'}
                </Badge>
                <Badge variant="outline" className="border-[#f5a623]/50 text-[#f5a623]">
                  {PARTNER_TYPE_ICONS[selectedPartner.partner_type]} {selectedPartner.partner_type_label}
                </Badge>
                {selectedPartner.is_verified && (
                  <Badge className="bg-blue-500/20 text-blue-500">
                    <CheckCircle className="h-3 w-3 mr-1" /> Vérifié
                  </Badge>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <Card className="bg-background/50 border-border">
                  <CardContent className="p-3 text-center">
                    <p className="text-2xl font-bold text-[#f5a623]">{selectedPartner.commission_rate}%</p>
                    <p className="text-xs text-gray-400">Commission</p>
                  </CardContent>
                </Card>
                <Card className="bg-background/50 border-border">
                  <CardContent className="p-3 text-center">
                    <p className="text-2xl font-bold text-green-500">${selectedPartner.wallet_balance?.toFixed(2) || '0.00'}</p>
                    <p className="text-xs text-gray-400">Solde</p>
                  </CardContent>
                </Card>
                <Card className="bg-background/50 border-border">
                  <CardContent className="p-3 text-center">
                    <p className="text-2xl font-bold text-white">{selectedPartner.stats?.total_reservations || 0}</p>
                    <p className="text-xs text-gray-400">Réservations</p>
                  </CardContent>
                </Card>
              </div>

              {/* Contact Info */}
              <Card className="bg-background/50 border-border">
                <CardContent className="p-4 space-y-3">
                  <h4 className="text-sm font-medium text-gray-400">Contact</h4>
                  <div className="space-y-2">
                    <p className="text-white">{selectedPartner.contact_name}</p>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-gray-500" />
                      <a href={`mailto:${selectedPartner.email}`} className="text-[#f5a623]">{selectedPartner.email}</a>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-gray-500" />
                      <span>{selectedPartner.phone}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Description */}
              <Card className="bg-background/50 border-border">
                <CardContent className="p-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
                  <p className="text-gray-300 text-sm">{selectedPartner.description}</p>
                </CardContent>
              </Card>
            </div>
          )}

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => handleTogglePartnerStatus(selectedPartner?.id)}
              className={selectedPartner?.is_active ? 'border-red-500 text-red-500' : 'border-green-500 text-green-500'}
            >
              {selectedPartner?.is_active ? (
                <><UserX className="h-4 w-4 mr-2" /> Suspendre</>
              ) : (
                <><UserCheck className="h-4 w-4 mr-2" /> Activer</>
              )}
            </Button>
            <Button variant="outline" onClick={() => setShowPartnerModal(false)}>
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PartnershipAdmin;
