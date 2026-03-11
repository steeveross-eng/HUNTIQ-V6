/**
 * AdminContacts - V5-ULTIME Administration Premium
 * =================================================
 * 
 * Module de gestion des contacts et entités relationnelles.
 * Source de vérité V5 pour:
 * - Fournisseurs (Suppliers)
 * - Fabricants (Manufacturers)
 * - Partenaires (Partners)
 * - Formateurs / Experts
 * - Contacts internes / externes
 * - Réseau professionnel
 * 
 * Module isolé LEGO - Aucun import croisé.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Users, Building2, Briefcase, GraduationCap, UserCircle, 
  Plus, Edit, Trash2, Search, Filter, Tag, Mail, Phone,
  Globe, MapPin, CheckCircle, XCircle, Loader2, X, Download,
  Upload, BarChart3, RefreshCw
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Types d'entités avec leurs icônes et labels
const ENTITY_TYPES = [
  { id: 'all', label: 'Tous', icon: Users },
  { id: 'supplier', label: 'Fournisseurs', icon: Building2 },
  { id: 'manufacturer', label: 'Fabricants', icon: Building2 },
  { id: 'partner', label: 'Partenaires', icon: Briefcase },
  { id: 'trainer', label: 'Formateurs', icon: GraduationCap },
  { id: 'expert', label: 'Experts', icon: UserCircle },
  { id: 'internal', label: 'Internes', icon: Users },
  { id: 'external', label: 'Externes', icon: Users },
  { id: 'professional', label: 'Réseau Pro', icon: Briefcase },
];

const AdminContacts = () => {
  // State
  const [activeTab, setActiveTab] = useState('list');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Contacts state
  const [contacts, setContacts] = useState([]);
  const [typeCounts, setTypeCounts] = useState({});
  const [selectedType, setSelectedType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [formData, setFormData] = useState({
    entity_type: 'supplier',
    name: '',
    company: '',
    position: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    province: 'QC',
    postal_code: '',
    country: 'Canada',
    website: '',
    notes: '',
    tags: [],
    status: 'active',
    priority: 'normal'
  });
  
  // Stats state
  const [stats, setStats] = useState(null);
  
  // Tags state
  const [allTags, setAllTags] = useState([]);
  const [newTag, setNewTag] = useState('');

  // ============ API CALLS ============
  const fetchContacts = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/v1/admin/contacts?limit=100`;
      if (selectedType !== 'all') url += `&entity_type=${selectedType}`;
      if (statusFilter !== 'all') url += `&status=${statusFilter}`;
      if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;
      
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        setContacts(data.contacts || []);
        setTypeCounts(data.type_counts || {});
      }
    } catch (err) {
      setError('Erreur lors du chargement des contacts');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/tags`);
      const data = await response.json();
      if (data.success) {
        setAllTags(data.tags || []);
      }
    } catch (err) {
      console.error('Error fetching tags:', err);
    }
  };

  const createContact = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Contact créé avec succès');
        resetForm();
        fetchContacts();
        fetchStats();
      } else {
        setError(data.error || 'Erreur lors de la création');
      }
    } catch (err) {
      setError('Erreur réseau');
    }
  };

  const updateContact = async () => {
    if (!editingContact) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/${editingContact.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Contact mis à jour');
        resetForm();
        fetchContacts();
      } else {
        setError(data.error || 'Erreur lors de la mise à jour');
      }
    } catch (err) {
      setError('Erreur réseau');
    }
  };

  const deleteContact = async (contactId) => {
    if (!window.confirm('Supprimer ce contact ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/${contactId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Contact supprimé');
        fetchContacts();
        fetchStats();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const addTagToContact = async (contactId, tag) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/${contactId}/tags?tag=${encodeURIComponent(tag)}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        fetchContacts();
        fetchTags();
      }
    } catch (err) {
      setError('Erreur lors de l\'ajout du tag');
    }
  };

  const removeTagFromContact = async (contactId, tag) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/contacts/${contactId}/tags/${encodeURIComponent(tag)}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        fetchContacts();
        fetchTags();
      }
    } catch (err) {
      setError('Erreur lors du retrait du tag');
    }
  };

  const exportContacts = async () => {
    try {
      const url = selectedType !== 'all' 
        ? `${API_URL}/api/v1/admin/contacts/export/all?entity_type=${selectedType}`
        : `${API_URL}/api/v1/admin/contacts/export/all`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        // Télécharger en JSON
        const blob = new Blob([JSON.stringify(data.contacts, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `contacts_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        setSuccess(`${data.total} contacts exportés`);
      }
    } catch (err) {
      setError('Erreur lors de l\'export');
    }
  };

  // ============ HELPERS ============
  const resetForm = () => {
    setShowForm(false);
    setEditingContact(null);
    setFormData({
      entity_type: 'supplier',
      name: '',
      company: '',
      position: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      province: 'QC',
      postal_code: '',
      country: 'Canada',
      website: '',
      notes: '',
      tags: [],
      status: 'active',
      priority: 'normal'
    });
  };

  const startEdit = (contact) => {
    setEditingContact(contact);
    setFormData({
      entity_type: contact.entity_type || 'supplier',
      name: contact.name || '',
      company: contact.company || '',
      position: contact.position || '',
      email: contact.email || '',
      phone: contact.phone || '',
      address: contact.address || '',
      city: contact.city || '',
      province: contact.province || 'QC',
      postal_code: contact.postal_code || '',
      country: contact.country || 'Canada',
      website: contact.website || '',
      notes: contact.notes || '',
      tags: contact.tags || [],
      status: contact.status || 'active',
      priority: contact.priority || 'normal'
    });
    setShowForm(true);
  };

  const getEntityIcon = (type) => {
    const entity = ENTITY_TYPES.find(e => e.id === type);
    return entity ? entity.icon : Users;
  };

  const getEntityLabel = (type) => {
    const entity = ENTITY_TYPES.find(e => e.id === type);
    return entity ? entity.label : type;
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-400';
      case 'normal': return 'bg-blue-500/20 text-blue-400';
      case 'low': return 'bg-gray-500/20 text-gray-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // ============ EFFECTS ============
  useEffect(() => {
    fetchContacts();
    fetchStats();
    fetchTags();
  }, []);

  useEffect(() => {
    fetchContacts();
  }, [selectedType, statusFilter, searchQuery]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  // ============ RENDER ============
  return (
    <div data-testid="admin-contacts-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="h-6 w-6 text-[#F5A623]" />
            Répertoire des Contacts
          </h2>
          <p className="text-gray-400 text-sm">Fournisseurs, Partenaires, Formateurs, Experts...</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={exportContacts} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
            <Download className="h-4 w-4 mr-2" />
            Exporter
          </Button>
          <Button
            data-testid="btn-new-contact"
            onClick={() => { resetForm(); setShowForm(true); }}
            className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nouveau Contact
          </Button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg flex justify-between items-center">
          <span className="flex items-center gap-2"><XCircle className="h-4 w-4" />{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}><X className="h-4 w-4" /></Button>
        </div>
      )}
      {success && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-3 rounded-lg flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />{success}
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Total Contacts</CardDescription>
              <CardTitle className="text-2xl text-white">{stats.total}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Actifs</CardDescription>
              <CardTitle className="text-2xl text-green-400">{stats.active}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-red-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Priorité Haute</CardDescription>
              <CardTitle className="text-2xl text-red-400">{stats.by_priority?.high || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Fournisseurs</CardDescription>
              <CardTitle className="text-2xl text-blue-400">{stats.by_type?.supplier || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Partenaires</CardDescription>
              <CardTitle className="text-2xl text-purple-400">{stats.by_type?.partner || 0}</CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        {/* Type Filter */}
        <div className="flex gap-1 flex-wrap">
          {ENTITY_TYPES.map(type => (
            <Button
              key={type.id}
              size="sm"
              variant={selectedType === type.id ? 'default' : 'ghost'}
              onClick={() => setSelectedType(type.id)}
              className={selectedType === type.id ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
            >
              <type.icon className="h-3 w-3 mr-1" />
              {type.label}
              {typeCounts[type.id] !== undefined && type.id !== 'all' && (
                <Badge className="ml-1 bg-white/10 text-xs">{typeCounts[type.id]}</Badge>
              )}
            </Button>
          ))}
        </div>
        
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-[#050510] border-[#F5A623]/30 text-white"
          />
        </div>
        
        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
        >
          <option value="all">Tous les statuts</option>
          <option value="active">Actifs</option>
          <option value="inactive">Inactifs</option>
        </select>
      </div>

      {/* Form */}
      {showForm && (
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white">
              {editingContact ? 'Modifier le Contact' : 'Nouveau Contact'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <select
                value={formData.entity_type}
                onChange={(e) => setFormData({ ...formData, entity_type: e.target.value })}
                className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
              >
                {ENTITY_TYPES.filter(t => t.id !== 'all').map(type => (
                  <option key={type.id} value={type.id}>{type.label}</option>
                ))}
              </select>
              <Input
                placeholder="Nom *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <Input
                placeholder="Entreprise"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <Input
                placeholder="Poste"
                value={formData.position}
                onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                placeholder="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <Input
                placeholder="Téléphone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <Input
                placeholder="Site Web"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
              >
                <option value="high">Priorité Haute</option>
                <option value="normal">Priorité Normale</option>
                <option value="low">Priorité Basse</option>
              </select>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                placeholder="Adresse"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white lg:col-span-2"
              />
              <Input
                placeholder="Ville"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
              <Input
                placeholder="Province"
                value={formData.province}
                onChange={(e) => setFormData({ ...formData, province: e.target.value })}
                className="bg-[#050510] border-[#F5A623]/30 text-white"
              />
            </div>
            
            <textarea
              placeholder="Notes..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-3"
            />
            
            <div className="flex gap-2">
              <Button
                onClick={editingContact ? updateContact : createContact}
                className="bg-[#F5A623] text-black"
              >
                {editingContact ? 'Mettre à jour' : 'Créer'}
              </Button>
              <Button variant="ghost" onClick={resetForm} className="text-gray-400">
                Annuler
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      )}

      {/* Contacts List */}
      {!loading && (
        <div className="grid gap-3">
          {contacts.map((contact) => {
            const EntityIcon = getEntityIcon(contact.entity_type);
            return (
              <Card 
                key={contact.id}
                data-testid={`contact-item-${contact.id}`}
                className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all"
              >
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="p-2 bg-[#F5A623]/10 rounded-lg">
                        <EntityIcon className="h-6 w-6 text-[#F5A623]" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-white font-medium">{contact.name}</h3>
                          <Badge className="bg-[#F5A623]/20 text-[#F5A623] text-xs">
                            {getEntityLabel(contact.entity_type)}
                          </Badge>
                          <Badge className={getPriorityColor(contact.priority)}>
                            {contact.priority}
                          </Badge>
                          {contact.status === 'inactive' && (
                            <Badge className="bg-gray-500/20 text-gray-400">Inactif</Badge>
                          )}
                        </div>
                        {contact.company && (
                          <p className="text-gray-400 text-sm flex items-center gap-2">
                            <Building2 className="h-3 w-3" />
                            {contact.company}
                            {contact.position && ` — ${contact.position}`}
                          </p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          {contact.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {contact.email}
                            </span>
                          )}
                          {contact.phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {contact.phone}
                            </span>
                          )}
                          {contact.city && (
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {contact.city}, {contact.province}
                            </span>
                          )}
                        </div>
                        {contact.tags && contact.tags.length > 0 && (
                          <div className="flex gap-1 mt-2 flex-wrap">
                            {contact.tags.map((tag, idx) => (
                              <Badge key={idx} className="bg-purple-500/20 text-purple-400 text-xs">
                                <Tag className="h-2 w-2 mr-1" />
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => startEdit(contact)} className="text-[#F5A623]">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => deleteContact(contact.id)} className="text-red-400">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          {contacts.length === 0 && (
            <Card className="bg-[#0a0a15] border-[#F5A623]/10">
              <CardContent className="py-8 text-center text-gray-500">
                Aucun contact trouvé. Créez votre premier contact !
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminContacts;
