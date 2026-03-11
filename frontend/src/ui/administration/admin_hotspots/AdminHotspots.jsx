/**
 * AdminHotspots - Administration des terres et hotspots
 * ======================================================
 * 
 * Module V5-ULTIME - Phase 4 Migration
 * Gestion complète des terres à louer, propriétaires, locataires
 * et ententes de location.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Trees,
  Users,
  Crown,
  DollarSign,
  FileText,
  RefreshCw,
  Loader2,
  Eye,
  Star,
  StarOff,
  Check,
  X,
  MapPin,
  TrendingUp,
  Percent,
  Save,
  BarChart3,
  Target
} from 'lucide-react';
import { toast } from 'sonner';
import AdminService from '../AdminService';

const AdminHotspots = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [listings, setListings] = useState([]);
  const [owners, setOwners] = useState([]);
  const [renters, setRenters] = useState([]);
  const [agreements, setAgreements] = useState([]);
  const [pricing, setPricing] = useState(null);
  const [regions, setRegions] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [savingPricing, setSavingPricing] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [filters, setFilters] = useState({
    status: 'all',
    tier: 'all'
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [
        statsRes,
        listingsRes,
        ownersRes,
        rentersRes,
        agreementsRes,
        pricingRes,
        regionsRes,
        purchasesRes
      ] = await Promise.all([
        AdminService.hotspotsGetStats(),
        AdminService.hotspotsGetListings(filters.status),
        AdminService.hotspotsGetOwners(),
        AdminService.hotspotsGetRenters(filters.tier),
        AdminService.hotspotsGetAgreements(),
        AdminService.hotspotsGetPricing(),
        AdminService.hotspotsGetRegions(),
        AdminService.hotspotsGetPurchases()
      ]);
      
      if (statsRes.success) setStats(statsRes.stats);
      if (listingsRes.success) setListings(listingsRes.listings || []);
      if (ownersRes.success) setOwners(ownersRes.owners || []);
      if (rentersRes.success) setRenters(rentersRes.renters || []);
      if (agreementsRes.success) setAgreements(agreementsRes.agreements || []);
      if (pricingRes.success) setPricing(pricingRes.pricing || {});
      if (regionsRes.success) setRegions(regionsRes.regions || []);
      if (purchasesRes.success) setPurchases(purchasesRes.purchases || []);
    } catch (error) {
      console.error('Error loading hotspots data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleToggleFeatured = async (listingId, currentState) => {
    try {
      const result = await AdminService.hotspotsToggleFeatured(listingId, !currentState);
      if (result.success) {
        toast.success(result.is_featured ? 'Annonce mise en vedette' : 'Mise en vedette retirée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleUpdateStatus = async (listingId, newStatus) => {
    try {
      const result = await AdminService.hotspotsUpdateStatus(listingId, newStatus);
      if (result.success) {
        toast.success(`Statut mis à jour: ${newStatus}`);
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handlePriceChange = (key, value) => {
    setPricing(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        price: parseFloat(value) || 0
      }
    }));
  };

  const handleSavePricing = async () => {
    setSavingPricing(true);
    try {
      const result = await AdminService.hotspotsUpdatePricing(pricing);
      if (result.success) {
        toast.success('Tarification mise à jour!');
      }
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSavingPricing(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(amount || 0);
  };

  const getStatusBadge = (status) => {
    const variants = {
      active: 'bg-green-500/20 text-green-400',
      pending: 'bg-yellow-500/20 text-yellow-400',
      draft: 'bg-gray-500/20 text-gray-400',
      rented: 'bg-blue-500/20 text-blue-400',
      expired: 'bg-red-500/20 text-red-400',
      suspended: 'bg-red-600/20 text-red-500',
      signed: 'bg-green-500/20 text-green-400',
      cancelled: 'bg-gray-600/20 text-gray-500'
    };
    return <Badge className={variants[status] || 'bg-gray-500/20'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-hotspots" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Trees className="h-6 w-6 text-green-500" />
            Gestion des Terres & Hotspots
          </h2>
          <p className="text-gray-400">Administration des annonces de location de terres</p>
        </div>
        <Button variant="outline" onClick={loadData} data-testid="refresh-hotspots">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[#0a0a15]">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="listings">Annonces</TabsTrigger>
          <TabsTrigger value="owners">Propriétaires</TabsTrigger>
          <TabsTrigger value="renters">Locataires</TabsTrigger>
          <TabsTrigger value="agreements">Ententes</TabsTrigger>
          <TabsTrigger value="pricing">Tarification</TabsTrigger>
          <TabsTrigger value="regions">Régions</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {stats && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <Trees className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Annonces actives</p>
                        <p className="text-xl font-bold text-white">{stats.listings?.active || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <Users className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Propriétaires</p>
                        <p className="text-xl font-bold text-white">{stats.users?.owners || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <Crown className="h-5 w-5 text-purple-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Chasseurs Premium</p>
                        <p className="text-xl font-bold text-white">{stats.users?.premium_renters || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                        <DollarSign className="h-5 w-5 text-[#f5a623]" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Revenus totaux</p>
                        <p className="text-xl font-bold text-white">{formatCurrency(stats.revenue?.total)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-[#f5a623]" />
                      Statuts des annonces
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {['active', 'pending', 'draft', 'rented', 'expired', 'suspended'].map(status => (
                        <div key={status} className="flex items-center justify-between">
                          <span className="text-gray-400 capitalize">{status}</span>
                          <span className="text-white font-medium">
                            {stats.listings?.[status] || 0}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Target className="h-5 w-5 text-green-500" />
                      Ententes de location
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Total</span>
                        <span className="text-white font-medium">{stats.agreements?.total || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Signées</span>
                        <span className="text-green-400 font-medium">{stats.agreements?.signed || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Taux de conversion</span>
                        <span className="text-[#f5a623] font-medium">{stats.agreements?.conversion_rate || 0}%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* Listings Tab */}
        <TabsContent value="listings">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Annonces de terres</CardTitle>
              <CardDescription>Gérer les annonces publiées sur la plateforme</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Titre</TableHead>
                    <TableHead className="text-gray-400">Région</TableHead>
                    <TableHead className="text-gray-400">Prix/jour</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Vedette</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {listings.slice(0, 20).map((listing) => (
                    <TableRow key={listing.id}>
                      <TableCell className="text-white font-medium">{listing.title?.slice(0, 40) || 'Sans titre'}...</TableCell>
                      <TableCell className="text-gray-400">{listing.region || '-'}</TableCell>
                      <TableCell className="text-white">{formatCurrency(listing.price_per_day)}</TableCell>
                      <TableCell>{getStatusBadge(listing.status)}</TableCell>
                      <TableCell>
                        {listing.is_featured ? (
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        ) : (
                          <StarOff className="h-4 w-4 text-gray-500" />
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleToggleFeatured(listing.id, listing.is_featured)}
                          >
                            {listing.is_featured ? <StarOff className="h-4 w-4" /> : <Star className="h-4 w-4" />}
                          </Button>
                          {listing.status === 'pending' && (
                            <>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-green-400"
                                onClick={() => handleUpdateStatus(listing.id, 'active')}
                              >
                                <Check className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-400"
                                onClick={() => handleUpdateStatus(listing.id, 'suspended')}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {listings.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune annonce trouvée</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Owners Tab */}
        <TabsContent value="owners">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Propriétaires</CardTitle>
              <CardDescription>Liste des propriétaires inscrits</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Email</TableHead>
                    <TableHead className="text-gray-400">Téléphone</TableHead>
                    <TableHead className="text-gray-400">Vérifié</TableHead>
                    <TableHead className="text-gray-400">Annonces</TableHead>
                    <TableHead className="text-gray-400">Note</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {owners.slice(0, 20).map((owner) => (
                    <TableRow key={owner.id}>
                      <TableCell className="text-white font-medium">{owner.name}</TableCell>
                      <TableCell className="text-gray-400">{owner.email}</TableCell>
                      <TableCell className="text-gray-400">{owner.phone || '-'}</TableCell>
                      <TableCell>
                        {owner.is_verified ? (
                          <Badge className="bg-green-500/20 text-green-400">Vérifié</Badge>
                        ) : (
                          <Badge className="bg-gray-500/20 text-gray-400">Non vérifié</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-white">{owner.total_listings || 0}</TableCell>
                      <TableCell className="text-yellow-400">{owner.rating || 5.0} ⭐</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {owners.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun propriétaire trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Renters Tab */}
        <TabsContent value="renters">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Locataires (Chasseurs)</CardTitle>
              <CardDescription>Chasseurs inscrits pour louer des terres</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Email</TableHead>
                    <TableHead className="text-gray-400">Abonnement</TableHead>
                    <TableHead className="text-gray-400">Permis chasse</TableHead>
                    <TableHead className="text-gray-400">Locations</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {renters.slice(0, 20).map((renter) => (
                    <TableRow key={renter.id}>
                      <TableCell className="text-white font-medium">{renter.name}</TableCell>
                      <TableCell className="text-gray-400">{renter.email}</TableCell>
                      <TableCell>
                        <Badge className={
                          renter.subscription_tier === 'vip' ? 'bg-amber-500/20 text-amber-400' :
                          renter.subscription_tier === 'pro' ? 'bg-purple-500/20 text-purple-400' :
                          renter.subscription_tier === 'basic' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        }>
                          {renter.subscription_tier || 'free'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-400">{renter.hunting_license || '-'}</TableCell>
                      <TableCell className="text-white">{renter.total_rentals || 0}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {renters.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun locataire trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agreements Tab */}
        <TabsContent value="agreements">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Ententes de location</CardTitle>
              <CardDescription>Contrats entre propriétaires et locataires</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Terrain</TableHead>
                    <TableHead className="text-gray-400">Propriétaire</TableHead>
                    <TableHead className="text-gray-400">Locataire</TableHead>
                    <TableHead className="text-gray-400">Montant</TableHead>
                    <TableHead className="text-gray-400">Dates</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agreements.slice(0, 20).map((agreement) => (
                    <TableRow key={agreement.id}>
                      <TableCell className="text-white font-medium">{agreement.land_title?.slice(0, 30) || '-'}...</TableCell>
                      <TableCell className="text-gray-400">{agreement.owner_name || '-'}</TableCell>
                      <TableCell className="text-gray-400">{agreement.renter_name || '-'}</TableCell>
                      <TableCell className="text-white">{formatCurrency(agreement.total_price)}</TableCell>
                      <TableCell className="text-gray-400 text-xs">
                        {agreement.start_date?.slice(0, 10)} → {agreement.end_date?.slice(0, 10)}
                      </TableCell>
                      <TableCell>{getStatusBadge(agreement.status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {agreements.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune entente trouvée</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pricing Tab */}
        <TabsContent value="pricing">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-[#f5a623]" />
                Gestion des tarifs
              </CardTitle>
              <CardDescription>Configurer les prix des services</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {pricing && (
                <>
                  <div>
                    <h3 className="text-white font-semibold mb-4">Frais de publication</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {['listing_basic', 'listing_featured_7', 'listing_featured_30', 'listing_auto_bump'].map(key => {
                        const item = pricing[key];
                        if (!item) return null;
                        return (
                          <div key={key} className="bg-gray-900/50 p-4 rounded-lg">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h4 className="text-white font-medium">{item.name}</h4>
                                <p className="text-gray-400 text-xs">{item.description}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Input
                                type="number"
                                step="0.01"
                                value={item.price}
                                onChange={(e) => handlePriceChange(key, e.target.value)}
                                className="bg-gray-800 border-gray-700 w-24"
                              />
                              <span className="text-gray-400">$</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-white font-semibold mb-4">Abonnements chasseurs</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      {['renter_basic', 'renter_pro', 'renter_vip'].map(key => {
                        const item = pricing[key];
                        if (!item) return null;
                        return (
                          <div key={key} className="bg-gray-900/50 p-4 rounded-lg text-center">
                            <Crown className={`h-6 w-6 mx-auto ${key === 'renter_vip' ? 'text-amber-400' : 'text-purple-400'}`} />
                            <h4 className="text-white font-medium mt-2">{item.name}</h4>
                            <p className="text-gray-400 text-xs mb-3">{item.description}</p>
                            <div className="flex items-center justify-center gap-2">
                              <Input
                                type="number"
                                step="0.01"
                                value={item.price}
                                onChange={(e) => handlePriceChange(key, e.target.value)}
                                className="bg-gray-800 border-gray-700 w-24 text-center"
                              />
                              <span className="text-gray-400">$/mois</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <Percent className="h-4 w-4" />
                      Commissions
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {['owner_fee_percent', 'renter_fee_percent'].map(key => {
                        const item = pricing[key];
                        if (!item) return null;
                        return (
                          <div key={key} className="bg-gray-900/50 p-4 rounded-lg">
                            <h4 className="text-white font-medium">{item.name}</h4>
                            <p className="text-gray-400 text-xs mb-2">{item.description}</p>
                            <div className="flex items-center gap-2">
                              <Input
                                type="number"
                                step="0.5"
                                min="0"
                                max="50"
                                value={item.price}
                                onChange={(e) => handlePriceChange(key, e.target.value)}
                                className="bg-gray-800 border-gray-700 w-24"
                              />
                              <span className="text-gray-400">%</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="flex justify-end pt-4 border-t border-border">
                    <Button onClick={handleSavePricing} disabled={savingPricing} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
                      {savingPricing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                      Sauvegarder la tarification
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Regions Tab */}
        <TabsContent value="regions">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <MapPin className="h-5 w-5 text-green-500" />
                Statistiques par région
              </CardTitle>
              <CardDescription>Distribution des annonces par région du Québec</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Région</TableHead>
                    <TableHead className="text-gray-400">Annonces</TableHead>
                    <TableHead className="text-gray-400">Prix moyen/jour</TableHead>
                    <TableHead className="text-gray-400">Surface moyenne</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {regions.map((region) => (
                    <TableRow key={region.region}>
                      <TableCell className="text-white font-medium">{region.region}</TableCell>
                      <TableCell className="text-white">{region.listings_count}</TableCell>
                      <TableCell className="text-[#f5a623]">{formatCurrency(region.avg_price_per_day)}</TableCell>
                      <TableCell className="text-gray-400">{region.avg_surface_acres} acres</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {regions.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune donnée régionale disponible</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminHotspots;
