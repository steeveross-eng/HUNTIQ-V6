/**
 * LandsPricingAdmin - Admin component for managing Lands Rental pricing
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  DollarSign,
  Save,
  RefreshCw,
  Loader2,
  Trees,
  Crown,
  Zap,
  Star,
  Users,
  Percent,
  TrendingUp,
  BarChart3,
  CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LandsPricingAdmin = () => {
  const [pricing, setPricing] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pricingRes, statsRes] = await Promise.all([
        axios.get(`${API}/lands/admin/pricing`),
        axios.get(`${API}/lands/admin/stats`)
      ]);
      setPricing(pricingRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
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

  const handleSave = async () => {
    setSaving(true);
    try {
      // Prepare update data
      const updates = {};
      Object.entries(pricing).forEach(([key, value]) => {
        if (value && typeof value === 'object' && 'price' in value) {
          updates[key] = value;
        }
      });

      await axios.put(`${API}/lands/admin/pricing`, updates);
      toast.success('Tarification mise à jour!');
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Trees className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Terres actives</p>
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
                  <p className="text-xl font-bold text-white">{formatCurrency(stats.revenue?.total || 0)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Pricing Management */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-[#f5a623]" />
            Gestion des tarifs - Terres à louer
          </CardTitle>
          <CardDescription>
            Ajustez les prix des services pour la section location de terres
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="publication" className="w-full">
            <TabsList className="bg-gray-900 mb-6">
              <TabsTrigger value="publication">Publication</TabsTrigger>
              <TabsTrigger value="subscriptions">Abonnements</TabsTrigger>
              <TabsTrigger value="extras">Options</TabsTrigger>
              <TabsTrigger value="commissions">Commissions</TabsTrigger>
            </TabsList>

            {/* Publication Tab */}
            <TabsContent value="publication" className="space-y-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Star className="h-4 w-4 text-yellow-400" />
                Frais de publication & visibilité
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {pricing && ['listing_basic', 'listing_featured_7', 'listing_featured_30', 'listing_auto_bump'].map(key => {
                  const item = pricing[key];
                  if (!item) return null;
                  return (
                    <Card key={key} className="bg-gray-900/50 border-border">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
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
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* Subscriptions Tab */}
            <TabsContent value="subscriptions" className="space-y-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Crown className="h-4 w-4 text-purple-400" />
                Abonnements chasseurs
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                {pricing && ['renter_basic', 'renter_pro', 'renter_vip'].map(key => {
                  const item = pricing[key];
                  if (!item) return null;
                  return (
                    <Card key={key} className="bg-gray-900/50 border-border">
                      <CardContent className="p-4">
                        <div className="text-center mb-3">
                          <Crown className={`h-6 w-6 mx-auto ${key === 'renter_vip' ? 'text-amber-400' : 'text-purple-400'}`} />
                          <h4 className="text-white font-medium mt-2">{item.name}</h4>
                          <p className="text-gray-400 text-xs">{item.description}</p>
                        </div>
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
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* Extras Tab */}
            <TabsContent value="extras" className="space-y-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-400" />
                Options à la carte
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {pricing && ['boost_24h', 'badge_premium', 'send_to_hunters', 'generate_agreement', 'ai_analysis'].map(key => {
                  const item = pricing[key];
                  if (!item) return null;
                  return (
                    <Card key={key} className="bg-gray-900/50 border-border">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
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
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* Commissions Tab */}
            <TabsContent value="commissions" className="space-y-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Percent className="h-4 w-4 text-green-400" />
                Frais de mise en relation (commissions)
              </h3>
              <p className="text-gray-400 text-sm">
                Ces frais sont prélevés uniquement lors d'une transaction confirmée entre propriétaire et locataire.
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                {pricing && ['owner_fee_percent', 'renter_fee_percent'].map(key => {
                  const item = pricing[key];
                  if (!item) return null;
                  return (
                    <Card key={key} className="bg-gray-900/50 border-border">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="text-white font-medium">{item.name}</h4>
                            <p className="text-gray-400 text-xs">{item.description}</p>
                          </div>
                        </div>
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
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              <Card className="bg-blue-500/10 border-blue-500/30">
                <CardContent className="p-4">
                  <p className="text-blue-400 text-sm">
                    <strong>Important:</strong> Les commissions sont des frais de mise en relation. 
                    La plateforme ne gère pas le paiement entre les parties - elle facture uniquement 
                    ces frais pour l'utilisation du service de mise en relation.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Save Button */}
          <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-border">
            <Button variant="outline" onClick={loadData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Rafraîchir
            </Button>
            <Button onClick={handleSave} disabled={saving} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
              {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
              Sauvegarder
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Legal Disclaimer */}
      <Card className="bg-green-500/10 border-green-500/30">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
            <div>
              <h4 className="text-green-400 font-medium">Modèle "Zéro responsabilité - 100% revenus"</h4>
              <ul className="text-gray-400 text-sm mt-2 space-y-1">
                <li>✓ Vous mettez en relation propriétaires et chasseurs</li>
                <li>✓ Vous fournissez des outils (ententes, recherche, alertes)</li>
                <li>✓ Vous offrez de la visibilité (mise en vedette, boost)</li>
                <li>✓ Vous automatisez les documents légaux</li>
                <li>✓ Vous ne touchez JAMAIS à l'argent des transactions</li>
                <li>✓ Vous n'êtes JAMAIS partie aux contrats</li>
                <li>✓ Zéro risque légal, zéro implication dans les litiges</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LandsPricingAdmin;
