/**
 * PartnerDashboard - Partner portal dashboard
 * Allows partners to manage their profile, products, calendar, and reservations
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import {
  Handshake,
  Building2,
  User,
  Mail,
  Phone,
  Globe,
  MapPin,
  DollarSign,
  Calendar,
  Package,
  TrendingUp,
  Eye,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
  Settings,
  LogOut,
  ArrowLeft,
  Wallet,
  FileText,
  BarChart3,
  Bell,
  Edit,
  Save,
  RefreshCw,
  Tent,
  Trees,
  Target,
  Store,
  Wrench,
  Factory,
  Fish,
  Users,
  LayoutList
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

const API = process.env.REACT_APP_BACKEND_URL;

// Partner type icons - using lucide-react components
const PARTNER_TYPE_ICONS = {
  marques: Star,
  pourvoiries: Tent,
  proprietaires: Trees,
  guides: Target,
  boutiques: Store,
  services: Wrench,
  fabricants: Factory,
  zec: Target,
  clubs: Fish,
  particuliers: User,
  autres: LayoutList
};

const PartnerDashboard = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [partner, setPartner] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});

  // For demo purposes - in production, get partner_id from auth context
  const partnerId = localStorage.getItem('partner_id');

  useEffect(() => {
    if (partnerId) {
      loadPartnerData();
    } else {
      // Redirect to login or show error
      toast.error(language === 'fr' ? 'Accès non autorisé' : 'Unauthorized access');
      navigate('/');
    }
  }, [partnerId]);

  const loadPartnerData = async () => {
    setLoading(true);
    try {
      const [partnerRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/partnership/partners/${partnerId}`),
        axios.get(`${API}/api/partnership/dashboard/${partnerId}/stats`)
      ]);
      setPartner(partnerRes.data);
      setStats(statsRes.data);
      setEditForm(partnerRes.data);
    } catch (error) {
      console.error('Error loading partner data:', error);
      toast.error(language === 'fr' ? 'Erreur de chargement' : 'Loading error');
    }
    setLoading(false);
  };

  const handleSaveProfile = async () => {
    try {
      await axios.put(`${API}/api/partnership/partners/${partnerId}`, editForm);
      toast.success(language === 'fr' ? 'Profil mis à jour!' : 'Profile updated!');
      setEditing(false);
      loadPartnerData();
    } catch (error) {
      toast.error(language === 'fr' ? 'Erreur lors de la mise à jour' : 'Update error');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('partner_id');
    navigate('/');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background pt-20 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-[#f5a623] animate-spin mx-auto mb-4" />
          <p className="text-gray-400">{language === 'fr' ? 'Chargement...' : 'Loading...'}</p>
        </div>
      </main>
    );
  }

  if (!partner) {
    return (
      <main className="min-h-screen bg-background pt-20 flex items-center justify-center">
        <Card className="bg-card border-border max-w-md w-full mx-4">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">
              {language === 'fr' ? 'Accès refusé' : 'Access Denied'}
            </h2>
            <p className="text-gray-400 mb-4">
              {language === 'fr' 
                ? 'Vous n\'êtes pas connecté en tant que partenaire.'
                : 'You are not logged in as a partner.'}
            </p>
            <Button onClick={() => navigate('/')} className="btn-golden text-black">
              <ArrowLeft className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Retour à l\'accueil' : 'Back to home'}
            </Button>
          </CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate('/')} className="text-gray-400 hover:text-white">
              <ArrowLeft className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Retour' : 'Back'}
            </Button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl md:text-3xl font-bold text-white">{partner.company_name}</h1>
                {partner.is_verified && (
                  <Badge className="bg-blue-500/20 text-blue-500">
                    <CheckCircle className="h-3 w-3 mr-1" /> {language === 'fr' ? 'Vérifié' : 'Verified'}
                  </Badge>
                )}
              </div>
              <p className="text-gray-400 flex items-center gap-2 mt-1">
                {PARTNER_TYPE_ICONS[partner.partner_type] && 
                  React.createElement(PARTNER_TYPE_ICONS[partner.partner_type], { className: "h-4 w-4" })
                }
                <span>{partner.partner_type_label}</span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={loadPartnerData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="border-red-500 text-red-500" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Déconnexion' : 'Logout'}
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            <Card className="bg-gradient-to-br from-[#f5a623]/20 to-[#f5a623]/5 border-[#f5a623]/30">
              <CardContent className="p-4">
                <Wallet className="h-6 w-6 text-[#f5a623] mb-2" />
                <p className="text-2xl font-bold text-white">${stats.wallet_balance?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'Solde' : 'Balance'}</p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <TrendingUp className="h-6 w-6 text-green-500 mb-2" />
                <p className="text-2xl font-bold text-white">${stats.total_revenue?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'Revenus' : 'Revenue'}</p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <Calendar className="h-6 w-6 text-blue-500 mb-2" />
                <p className="text-2xl font-bold text-white">{stats.total_reservations || 0}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'Réservations' : 'Bookings'}</p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <Clock className="h-6 w-6 text-yellow-500 mb-2" />
                <p className="text-2xl font-bold text-white">{stats.pending_reservations || 0}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'En attente' : 'Pending'}</p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <Eye className="h-6 w-6 text-purple-500 mb-2" />
                <p className="text-2xl font-bold text-white">{stats.total_views || 0}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'Vues' : 'Views'}</p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardContent className="p-4">
                <Star className="h-6 w-6 text-[#f5a623] mb-2" />
                <p className="text-2xl font-bold text-white">{stats.rating?.toFixed(1) || '-'}</p>
                <p className="text-xs text-gray-400">{language === 'fr' ? 'Note' : 'Rating'} ({stats.review_count || 0})</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-card border border-border mb-6">
            <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <BarChart3 className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Aperçu' : 'Overview'}
            </TabsTrigger>
            <TabsTrigger value="profile" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Building2 className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Profil' : 'Profile'}
            </TabsTrigger>
            <TabsTrigger value="calendar" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Calendar className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Calendrier' : 'Calendar'}
            </TabsTrigger>
            <TabsTrigger value="products" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Package className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Offres' : 'Offers'}
            </TabsTrigger>
            <TabsTrigger value="reservations" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <FileText className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Réservations' : 'Reservations'}
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Welcome Card */}
              <Card className="bg-gradient-to-br from-[#f5a623]/10 to-transparent border-[#f5a623]/30">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Handshake className="h-5 w-5 text-[#f5a623]" />
                    {language === 'fr' ? 'Bienvenue, partenaire!' : 'Welcome, partner!'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-400 mb-4">
                    {language === 'fr'
                      ? 'Gérez vos offres, votre calendrier et vos réservations depuis ce tableau de bord.'
                      : 'Manage your offers, calendar and reservations from this dashboard.'}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Badge className="bg-green-500/20 text-green-500">
                      {partner.is_active 
                        ? (language === 'fr' ? 'Compte actif' : 'Active account')
                        : (language === 'fr' ? 'Compte suspendu' : 'Suspended account')}
                    </Badge>
                    <Badge variant="outline" className="text-gray-400">
                      Commission: {stats?.commission_rate || 10}%
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white text-lg">
                    {language === 'fr' ? 'Actions rapides' : 'Quick Actions'}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start" variant="outline" onClick={() => setActiveTab('products')}>
                    <Package className="h-4 w-4 mr-2" />
                    {language === 'fr' ? 'Ajouter une offre' : 'Add an offer'}
                  </Button>
                  <Button className="w-full justify-start" variant="outline" onClick={() => setActiveTab('calendar')}>
                    <Calendar className="h-4 w-4 mr-2" />
                    {language === 'fr' ? 'Gérer les disponibilités' : 'Manage availability'}
                  </Button>
                  <Button className="w-full justify-start" variant="outline" onClick={() => setActiveTab('reservations')}>
                    <Bell className="h-4 w-4 mr-2" />
                    {language === 'fr' ? 'Voir les réservations' : 'View reservations'}
                    {stats?.pending_reservations > 0 && (
                      <Badge className="ml-auto bg-yellow-500 text-black">{stats.pending_reservations}</Badge>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity Placeholder */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white text-lg">
                  {language === 'fr' ? 'Activité récente' : 'Recent Activity'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>{language === 'fr' ? 'Aucune activité récente' : 'No recent activity'}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">
                    {language === 'fr' ? 'Profil de l\'entreprise' : 'Company Profile'}
                  </CardTitle>
                  <CardDescription>
                    {language === 'fr' ? 'Gérez vos informations publiques' : 'Manage your public information'}
                  </CardDescription>
                </div>
                {!editing ? (
                  <Button variant="outline" onClick={() => setEditing(true)}>
                    <Edit className="h-4 w-4 mr-2" />
                    {language === 'fr' ? 'Modifier' : 'Edit'}
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setEditing(false)}>
                      {language === 'fr' ? 'Annuler' : 'Cancel'}
                    </Button>
                    <Button className="btn-golden text-black" onClick={handleSaveProfile}>
                      <Save className="h-4 w-4 mr-2" />
                      {language === 'fr' ? 'Enregistrer' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Nom de l\'entreprise' : 'Company Name'}</Label>
                    <Input
                      value={editing ? editForm.company_name : partner.company_name}
                      onChange={(e) => setEditForm({ ...editForm, company_name: e.target.value })}
                      disabled={!editing}
                      className="bg-background"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Personne contact' : 'Contact Person'}</Label>
                    <Input
                      value={editing ? editForm.contact_name : partner.contact_name}
                      onChange={(e) => setEditForm({ ...editForm, contact_name: e.target.value })}
                      disabled={!editing}
                      className="bg-background"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Courriel' : 'Email'}</Label>
                    <Input value={partner.email} disabled className="bg-background" />
                  </div>
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Téléphone' : 'Phone'}</Label>
                    <Input
                      value={editing ? editForm.phone : partner.phone}
                      onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                      disabled={!editing}
                      className="bg-background"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Site web' : 'Website'}</Label>
                    <Input
                      value={editing ? editForm.website || '' : partner.website || ''}
                      onChange={(e) => setEditForm({ ...editForm, website: e.target.value })}
                      disabled={!editing}
                      className="bg-background"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-400">{language === 'fr' ? 'Adresse' : 'Address'}</Label>
                    <Input
                      value={editing ? editForm.address || '' : partner.address || ''}
                      onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
                      disabled={!editing}
                      className="bg-background"
                    />
                  </div>
                </div>
                <div>
                  <Label className="text-gray-400">Description</Label>
                  <Textarea
                    value={editing ? editForm.description : partner.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    disabled={!editing}
                    className="bg-background min-h-[100px]"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Calendar Tab */}
          <TabsContent value="calendar">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">
                  {language === 'fr' ? 'Calendrier des disponibilités' : 'Availability Calendar'}
                </CardTitle>
                <CardDescription>
                  {language === 'fr' 
                    ? 'Gérez vos disponibilités et bloquez les dates non disponibles'
                    : 'Manage your availability and block unavailable dates'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">
                    {language === 'fr' ? 'Calendrier dynamique' : 'Dynamic Calendar'}
                  </p>
                  <p className="text-sm">
                    {language === 'fr' 
                      ? 'Cette fonctionnalité sera disponible dans la prochaine mise à jour'
                      : 'This feature will be available in the next update'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Products/Offers Tab */}
          <TabsContent value="products">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">
                    {language === 'fr' ? 'Mes offres' : 'My Offers'}
                  </CardTitle>
                  <CardDescription>
                    {language === 'fr' 
                      ? 'Gérez vos produits, services et forfaits'
                      : 'Manage your products, services and packages'}
                  </CardDescription>
                </div>
                <Button className="btn-golden text-black">
                  <Package className="h-4 w-4 mr-2" />
                  {language === 'fr' ? 'Ajouter une offre' : 'Add Offer'}
                </Button>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  <Package className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">
                    {language === 'fr' ? 'Aucune offre pour le moment' : 'No offers yet'}
                  </p>
                  <p className="text-sm">
                    {language === 'fr' 
                      ? 'Créez votre première offre pour commencer à recevoir des réservations'
                      : 'Create your first offer to start receiving bookings'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reservations Tab */}
          <TabsContent value="reservations">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">
                  {language === 'fr' ? 'Réservations' : 'Reservations'}
                </CardTitle>
                <CardDescription>
                  {language === 'fr' 
                    ? 'Gérez vos réservations et confirmez les demandes'
                    : 'Manage your reservations and confirm requests'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">
                    {language === 'fr' ? 'Aucune réservation' : 'No reservations'}
                  </p>
                  <p className="text-sm">
                    {language === 'fr' 
                      ? 'Les réservations apparaîtront ici une fois que vous aurez des offres actives'
                      : 'Reservations will appear here once you have active offers'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
};

export default PartnerDashboard;
