/**
 * AdminPartners - V5-ULTIME Administration Premium
 * =================================================
 * 
 * Module d'administration des partenaires (Phase 6 Migration).
 * - Dashboard et statistiques partenaires
 * - Gestion des demandes de partenariat
 * - Gestion des partenaires officiels
 * - Types de partenaires (11 catégories)
 * - Paramètres emails partenaires
 * 
 * Module isolé - Architecture LEGO.
 */

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Handshake, LayoutDashboard, Inbox, Users, Settings,
  Search, RefreshCw, CheckCircle, XCircle, Clock,
  Mail, Building2, Phone, Globe, FileText, Star,
  ChevronRight, ToggleLeft, ToggleRight, BadgeCheck
} from 'lucide-react';
import AdminService from '../AdminService';

const AdminPartners = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [partnerTypes, setPartnerTypes] = useState([]);
  const [requests, setRequests] = useState([]);
  const [partners, setPartners] = useState([]);
  const [emailSettings, setEmailSettings] = useState({});
  const [filters, setFilters] = useState({ status: 'all', type: 'all', search: '' });
  const [selectedItem, setSelectedItem] = useState(null);

  // Load data on mount and tab change
  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'dashboard':
          const [statsRes, typesRes] = await Promise.all([
            AdminService.partnersGetDashboard(),
            AdminService.partnersGetTypes()
          ]);
          if (statsRes.success) setStats(statsRes.stats);
          if (typesRes.success) setPartnerTypes(typesRes.types);
          break;
        case 'requests':
          const reqRes = await AdminService.partnersGetRequests(
            filters.status !== 'all' ? filters.status : null,
            filters.type !== 'all' ? filters.type : null,
            filters.search || null
          );
          if (reqRes.success) setRequests(reqRes.requests);
          break;
        case 'partners':
          const partRes = await AdminService.partnersGetList(
            filters.type !== 'all' ? filters.type : null,
            null,
            filters.search || null
          );
          if (partRes.success) setPartners(partRes.partners);
          break;
        case 'settings':
          const emailRes = await AdminService.partnersGetEmailSettings();
          if (emailRes.success) setEmailSettings(emailRes.settings);
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const handleUpdateRequestStatus = async (requestId, status) => {
    const result = await AdminService.partnersUpdateRequestStatus(requestId, status);
    if (result.success) {
      loadData();
      setSelectedItem(null);
    }
  };

  const handleConvertToPartner = async (requestId) => {
    const result = await AdminService.partnersConvertRequest(requestId);
    if (result.success) {
      loadData();
      setSelectedItem(null);
    }
  };

  const handleTogglePartner = async (partnerId) => {
    const result = await AdminService.partnersToggleStatus(partnerId);
    if (result.success) loadData();
  };

  const handleVerifyPartner = async (partnerId, verified) => {
    const result = await AdminService.partnersVerify(partnerId, verified);
    if (result.success) loadData();
  };

  const handleToggleEmailSetting = async (settingType) => {
    const result = await AdminService.partnersToggleEmailSetting(settingType);
    if (result.success) loadData();
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'requests', label: 'Demandes', icon: Inbox },
    { id: 'partners', label: 'Partenaires', icon: Users },
    { id: 'settings', label: 'Paramètres', icon: Settings }
  ];

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      approved: 'bg-green-500/20 text-green-400 border-green-500/30',
      rejected: 'bg-red-500/20 text-red-400 border-red-500/30',
      converted: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      reviewed: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
    };
    return (
      <Badge className={`${styles[status] || styles.pending} border`}>
        {status?.toUpperCase()}
      </Badge>
    );
  };

  // ============ DASHBOARD TAB ============
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Partenaires</p>
              <p className="text-2xl font-bold text-white">{stats?.partners?.total || 0}</p>
            </div>
            <Users className="h-8 w-8 text-[#F5A623]" />
          </div>
          <p className="text-xs text-green-400 mt-2">
            {stats?.partners?.active || 0} actifs
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Demandes en attente</p>
              <p className="text-2xl font-bold text-yellow-400">{stats?.requests?.pending || 0}</p>
            </div>
            <Clock className="h-8 w-8 text-yellow-400" />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {stats?.requests?.total || 0} total
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Partenaires vérifiés</p>
              <p className="text-2xl font-bold text-green-400">{stats?.partners?.verified || 0}</p>
            </div>
            <BadgeCheck className="h-8 w-8 text-green-400" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Taux commission moy.</p>
              <p className="text-2xl font-bold text-[#F5A623]">{stats?.financial?.avg_commission || 10}%</p>
            </div>
            <Star className="h-8 w-8 text-[#F5A623]" />
          </div>
        </Card>
      </div>

      {/* Types de partenaires */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Building2 className="h-5 w-5 text-[#F5A623]" />
          Répartition par type
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {partnerTypes.map((type) => (
            <div key={type.id} className="p-3 bg-[#1a1a2e] rounded-lg border border-[#F5A623]/10">
              <p className="text-white font-medium">{type.label_fr}</p>
              <p className="text-[#F5A623] text-lg font-bold">
                {stats?.by_type?.[type.id]?.count || 0}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Statistiques demandes */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4">Statistiques des demandes</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['pending', 'reviewed', 'approved', 'rejected', 'converted'].map((status) => (
            <div key={status} className="text-center p-3 bg-[#1a1a2e] rounded-lg">
              <p className="text-gray-400 text-sm capitalize">{status}</p>
              <p className="text-white text-xl font-bold">
                {stats?.requests?.[status] || 0}
              </p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  // ============ REQUESTS TAB ============
  const renderRequests = () => (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="pl-10 bg-[#1a1a2e] border-[#F5A623]/20 text-white"
          />
        </div>
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Tous statuts</option>
          <option value="pending">En attente</option>
          <option value="reviewed">Examiné</option>
          <option value="approved">Approuvé</option>
          <option value="rejected">Rejeté</option>
          <option value="converted">Converti</option>
        </select>
        <select
          value={filters.type}
          onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Tous types</option>
          {partnerTypes.map((t) => (
            <option key={t.id} value={t.id}>{t.label_fr}</option>
          ))}
        </select>
        <Button onClick={loadData} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Requests list */}
      <div className="space-y-3">
        {requests.length === 0 ? (
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
            <Inbox className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">Aucune demande trouvée</p>
          </Card>
        ) : (
          requests.map((req) => (
            <Card 
              key={req.id} 
              className="bg-[#0f0f1a] border-[#F5A623]/20 p-4 hover:border-[#F5A623]/40 transition-colors cursor-pointer"
              onClick={() => setSelectedItem(req)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Building2 className="h-10 w-10 text-[#F5A623] p-2 bg-[#F5A623]/10 rounded-lg" />
                  <div>
                    <p className="text-white font-medium">{req.company_name}</p>
                    <p className="text-gray-400 text-sm">{req.contact_name} • {req.email}</p>
                    <p className="text-gray-500 text-xs mt-1">{req.partner_type_label}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(req.status)}
                  <ChevronRight className="h-5 w-5 text-gray-500" />
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Request detail modal */}
      {selectedItem && selectedItem.status && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Détail de la demande</h3>
              <Button variant="ghost" onClick={() => setSelectedItem(null)} className="text-gray-400">
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Building2 className="h-12 w-12 text-[#F5A623] p-2 bg-[#F5A623]/10 rounded-lg" />
                <div>
                  <p className="text-white font-bold text-lg">{selectedItem.company_name}</p>
                  <p className="text-gray-400">{selectedItem.partner_type_label}</p>
                </div>
                {getStatusBadge(selectedItem.status)}
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="p-3 bg-[#1a1a2e] rounded-lg">
                  <p className="text-gray-400 text-sm flex items-center gap-2">
                    <Users className="h-4 w-4" /> Contact
                  </p>
                  <p className="text-white">{selectedItem.contact_name}</p>
                </div>
                <div className="p-3 bg-[#1a1a2e] rounded-lg">
                  <p className="text-gray-400 text-sm flex items-center gap-2">
                    <Mail className="h-4 w-4" /> Email
                  </p>
                  <p className="text-white">{selectedItem.email}</p>
                </div>
                <div className="p-3 bg-[#1a1a2e] rounded-lg">
                  <p className="text-gray-400 text-sm flex items-center gap-2">
                    <Phone className="h-4 w-4" /> Téléphone
                  </p>
                  <p className="text-white">{selectedItem.phone || 'N/A'}</p>
                </div>
                <div className="p-3 bg-[#1a1a2e] rounded-lg">
                  <p className="text-gray-400 text-sm flex items-center gap-2">
                    <Globe className="h-4 w-4" /> Site web
                  </p>
                  <p className="text-white">{selectedItem.website || 'N/A'}</p>
                </div>
              </div>

              {selectedItem.description && (
                <div className="p-3 bg-[#1a1a2e] rounded-lg">
                  <p className="text-gray-400 text-sm mb-2 flex items-center gap-2">
                    <FileText className="h-4 w-4" /> Description
                  </p>
                  <p className="text-white text-sm">{selectedItem.description}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-wrap gap-3 mt-6 pt-4 border-t border-[#F5A623]/10">
                {selectedItem.status === 'pending' && (
                  <>
                    <Button 
                      onClick={() => handleUpdateRequestStatus(selectedItem.id, 'approved')}
                      className="bg-green-500/20 text-green-400 hover:bg-green-500/30"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" /> Approuver
                    </Button>
                    <Button 
                      onClick={() => handleUpdateRequestStatus(selectedItem.id, 'rejected')}
                      className="bg-red-500/20 text-red-400 hover:bg-red-500/30"
                    >
                      <XCircle className="h-4 w-4 mr-2" /> Rejeter
                    </Button>
                  </>
                )}
                {selectedItem.status === 'approved' && (
                  <Button 
                    onClick={() => handleConvertToPartner(selectedItem.id)}
                    className="bg-[#F5A623]/20 text-[#F5A623] hover:bg-[#F5A623]/30"
                  >
                    <Handshake className="h-4 w-4 mr-2" /> Convertir en partenaire
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );

  // ============ PARTNERS TAB ============
  const renderPartners = () => (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="pl-10 bg-[#1a1a2e] border-[#F5A623]/20 text-white"
          />
        </div>
        <select
          value={filters.type}
          onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Tous types</option>
          {partnerTypes.map((t) => (
            <option key={t.id} value={t.id}>{t.label_fr}</option>
          ))}
        </select>
        <Button onClick={loadData} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Partners list */}
      <div className="space-y-3">
        {partners.length === 0 ? (
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
            <Users className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">Aucun partenaire trouvé</p>
          </Card>
        ) : (
          partners.map((partner) => (
            <Card 
              key={partner.id} 
              className="bg-[#0f0f1a] border-[#F5A623]/20 p-4 hover:border-[#F5A623]/40 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Building2 className="h-10 w-10 text-[#F5A623] p-2 bg-[#F5A623]/10 rounded-lg" />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-white font-medium">{partner.company_name}</p>
                      {partner.is_verified && (
                        <BadgeCheck className="h-4 w-4 text-blue-400" />
                      )}
                    </div>
                    <p className="text-gray-400 text-sm">{partner.contact_name} • {partner.email}</p>
                    <p className="text-gray-500 text-xs mt-1">{partner.partner_type_label}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge className={partner.is_active 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }>
                    {partner.is_active ? 'Actif' : 'Suspendu'}
                  </Badge>
                  <span className="text-[#F5A623] font-medium">{partner.commission_rate}%</span>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => handleTogglePartner(partner.id)}
                    className="text-gray-400 hover:text-white"
                  >
                    {partner.is_active ? <ToggleRight className="h-5 w-5" /> : <ToggleLeft className="h-5 w-5" />}
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => handleVerifyPartner(partner.id, !partner.is_verified)}
                    className={partner.is_verified ? 'text-blue-400' : 'text-gray-400'}
                  >
                    <BadgeCheck className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );

  // ============ SETTINGS TAB ============
  const renderSettings = () => (
    <div className="space-y-6">
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Mail className="h-5 w-5 text-[#F5A623]" />
          Paramètres des emails partenaires
        </h3>
        <div className="space-y-4">
          {[
            { key: 'acknowledgment', label: 'Email d\'accusé de réception', desc: 'Envoyé lors de la soumission' },
            { key: 'admin_notification', label: 'Notification admin', desc: 'Alerter l\'admin des nouvelles demandes' },
            { key: 'approval', label: 'Email d\'approbation', desc: 'Envoyé lors de l\'approbation' },
            { key: 'rejection', label: 'Email de rejet', desc: 'Envoyé lors du rejet' }
          ].map((setting) => (
            <div 
              key={setting.key}
              className="flex items-center justify-between p-4 bg-[#1a1a2e] rounded-lg"
            >
              <div>
                <p className="text-white font-medium">{setting.label}</p>
                <p className="text-gray-400 text-sm">{setting.desc}</p>
              </div>
              <Button
                variant="ghost"
                onClick={() => handleToggleEmailSetting(setting.key)}
                className={emailSettings[`${setting.key}_enabled`] 
                  ? 'text-green-400' 
                  : 'text-gray-500'
                }
              >
                {emailSettings[`${setting.key}_enabled`] 
                  ? <ToggleRight className="h-6 w-6" />
                  : <ToggleLeft className="h-6 w-6" />
                }
              </Button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  return (
    <div data-testid="admin-partners-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Handshake className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Partenaires</h2>
            <p className="text-gray-400 text-sm">Gestion des partenariats</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#F5A623]/10 pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            data-testid={`partners-tab-${tab.id}`}
            variant="ghost"
            onClick={() => setActiveTab(tab.id)}
            className={`
              ${activeTab === tab.id
                ? 'bg-[#F5A623]/10 text-[#F5A623] border-b-2 border-[#F5A623]'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'requests' && renderRequests()}
          {activeTab === 'partners' && renderPartners()}
          {activeTab === 'settings' && renderSettings()}
        </>
      )}
    </div>
  );
};

export { AdminPartners };
export default AdminPartners;
