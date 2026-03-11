// ReferralAdminPanel.jsx - Interface admin pour le système de parrainage
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Users,
  Gift,
  Crown,
  Award,
  DollarSign,
  TrendingUp,
  Settings,
  Calendar,
  Tag,
  Percent,
  Check,
  X,
  Eye,
  Edit,
  Trash2,
  Plus,
  Loader2,
  Save,
  ShoppingCart,
  Star
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tier Badge Component
const TierBadge = ({ tier }) => {
  const tierConfig = {
    bronze: { color: "bg-amber-700", label: "Bronze" },
    silver: { color: "bg-gray-400", label: "Argent" },
    gold: { color: "bg-yellow-500", label: "Or" },
    platinum: { color: "bg-cyan-400", label: "Platine" },
    diamond: { color: "bg-purple-500", label: "Diamant" },
    partner: { color: "bg-gradient-to-r from-[#f5a623] to-purple-600", label: "Partenaire" }
  };
  
  const config = tierConfig[tier] || tierConfig.bronze;
  
  return (
    <Badge className={`${config.color} text-white`}>
      {config.label}
    </Badge>
  );
};

// ============================================
// DISCOUNT TIERS MANAGER
// ============================================
const DiscountTiersManager = () => {
  const [tiers, setTiers] = useState({});
  const [editedTiers, setEditedTiers] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadTiers();
  }, []);

  const loadTiers = async () => {
    try {
      const response = await axios.get(`${API}/referral/admin/tiers`);
      setTiers(response.data.tiers);
      setEditedTiers(response.data.tiers);
    } catch (error) {
      toast.error("Erreur lors du chargement des niveaux");
    }
    setLoading(false);
  };

  const handleTierChange = (tierId, field, value) => {
    setEditedTiers(prev => ({
      ...prev,
      [tierId]: {
        ...prev[tierId],
        [field]: field === "discount_percent" || field === "min_buyers" || field === "max_buyers" 
          ? parseInt(value) || 0 
          : value
      }
    }));
  };

  const saveTiers = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/referral/admin/tiers`, { tiers: editedTiers });
      setTiers(editedTiers);
      toast.success("Niveaux de rabais mis à jour!");
    } catch (error) {
      toast.error("Erreur lors de la sauvegarde");
    }
    setSaving(false);
  };

  if (loading) {
    return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Percent className="h-5 w-5 text-[#f5a623]" />
          Niveaux de rabais escalatoires
        </CardTitle>
        <CardDescription>
          Configurez les rabais selon le nombre d&apos;invités acheteurs
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Object.entries(editedTiers).filter(([id]) => id !== "partner").map(([tierId, tier]) => (
            <div key={tierId} className="flex items-center gap-4 p-4 bg-background rounded-lg">
              <TierBadge tier={tierId} />
              <div className="flex-1 grid grid-cols-4 gap-4">
                <div>
                  <Label className="text-gray-400 text-xs">Min acheteurs</Label>
                  <Input
                    type="number"
                    value={tier.min_buyers}
                    onChange={(e) => handleTierChange(tierId, "min_buyers", e.target.value)}
                    className="bg-card border-border h-8"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Max acheteurs</Label>
                  <Input
                    type="number"
                    value={tier.max_buyers}
                    onChange={(e) => handleTierChange(tierId, "max_buyers", e.target.value)}
                    className="bg-card border-border h-8"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Rabais (%)</Label>
                  <Input
                    type="number"
                    value={tier.discount_percent}
                    onChange={(e) => handleTierChange(tierId, "discount_percent", e.target.value)}
                    className="bg-card border-border h-8"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Label</Label>
                  <Input
                    value={tier.label}
                    onChange={(e) => handleTierChange(tierId, "label", e.target.value)}
                    className="bg-card border-border h-8"
                  />
                </div>
              </div>
            </div>
          ))}
          
          {/* Partner tier */}
          {editedTiers.partner && (
            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <div className="flex items-center gap-4">
                <TierBadge tier="partner" />
                <div className="flex-1">
                  <Label className="text-gray-400 text-xs">Rabais Partenaire (%)</Label>
                  <Input
                    type="number"
                    value={editedTiers.partner.discount_percent}
                    onChange={(e) => handleTierChange("partner", "discount_percent", e.target.value)}
                    className="bg-card border-border h-8 w-32"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={saveTiers} className="btn-golden text-black" disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
          Sauvegarder les niveaux
        </Button>
      </CardFooter>
    </Card>
  );
};

// ============================================
// SEASONAL PROMOTIONS MANAGER
// ============================================
const SeasonalPromotionsManager = () => {
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newPromo, setNewPromo] = useState({
    name: "",
    season_type: "custom",
    start_date: "",
    end_date: "",
    additional_discount_percent: 10,
    applies_to_all: true
  });

  const seasonTypes = [
    { value: "pre_season", label: "Pré-saison" },
    { value: "rut", label: "Rut" },
    { value: "post_rut", label: "Post-rut" },
    { value: "opening", label: "Ouverture de la chasse" },
    { value: "end_season", label: "Fin de saison" },
    { value: "off_peak", label: "Période creuse" },
    { value: "black_friday", label: "Black Friday" },
    { value: "boxing_day", label: "Boxing Day" },
    { value: "custom", label: "Personnalisé" }
  ];

  useEffect(() => {
    loadPromotions();
  }, []);

  const loadPromotions = async () => {
    try {
      const response = await axios.get(`${API}/referral/admin/promotions`);
      setPromotions(response.data.promotions);
    } catch (error) {
      console.error("Error loading promotions:", error);
    }
    setLoading(false);
  };

  const createPromotion = async () => {
    try {
      await axios.post(`${API}/referral/admin/promotions`, newPromo);
      toast.success("Promotion créée!");
      setShowAddModal(false);
      setNewPromo({
        name: "",
        season_type: "custom",
        start_date: "",
        end_date: "",
        additional_discount_percent: 10,
        applies_to_all: true
      });
      loadPromotions();
    } catch (error) {
      toast.error("Erreur lors de la création");
    }
  };

  const togglePromotion = async (promoId, isActive) => {
    try {
      await axios.put(`${API}/referral/admin/promotions/${promoId}?is_active=${!isActive}`);
      loadPromotions();
    } catch (error) {
      toast.error("Erreur");
    }
  };

  const deletePromotion = async (promoId) => {
    if (!confirm("Supprimer cette promotion?")) return;
    try {
      await axios.delete(`${API}/referral/admin/promotions/${promoId}`);
      toast.success("Promotion supprimée");
      loadPromotions();
    } catch (error) {
      toast.error("Erreur");
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <Calendar className="h-5 w-5 text-[#f5a623]" />
              Promotions saisonnières
            </CardTitle>
            <CardDescription>
              Rabais supplémentaires selon les périodes
            </CardDescription>
          </div>
          <Button onClick={() => setShowAddModal(true)} className="btn-golden text-black">
            <Plus className="h-4 w-4 mr-2" /> Nouvelle promotion
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>
        ) : promotions.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Aucune promotion configurée</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-border">
                <TableHead className="text-gray-400">Nom</TableHead>
                <TableHead className="text-gray-400">Type</TableHead>
                <TableHead className="text-gray-400">Période</TableHead>
                <TableHead className="text-gray-400">Rabais</TableHead>
                <TableHead className="text-gray-400">Statut</TableHead>
                <TableHead className="text-gray-400 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {promotions.map((promo) => (
                <TableRow key={promo.id} className="border-border">
                  <TableCell className="text-white font-medium">{promo.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {seasonTypes.find(s => s.value === promo.season_type)?.label || promo.season_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-gray-400 text-sm">
                    {new Date(promo.start_date).toLocaleDateString()} - {new Date(promo.end_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-green-600">+{promo.additional_discount_percent}%</Badge>
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={promo.is_active}
                      onCheckedChange={() => togglePromotion(promo.id, promo.is_active)}
                    />
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => deletePromotion(promo.id)}>
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      {/* Add Promotion Modal */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent className="bg-card border-border text-white">
          <DialogHeader>
            <DialogTitle>Nouvelle promotion saisonnière</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Nom de la promotion</Label>
              <Input
                value={newPromo.name}
                onChange={(e) => setNewPromo({...newPromo, name: e.target.value})}
                className="bg-background border-border"
                placeholder="Ex: Black Friday 2026"
              />
            </div>
            <div>
              <Label>Type de période</Label>
              <Select value={newPromo.season_type} onValueChange={(v) => setNewPromo({...newPromo, season_type: v})}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {seasonTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Date de début</Label>
                <Input
                  type="datetime-local"
                  value={newPromo.start_date}
                  onChange={(e) => setNewPromo({...newPromo, start_date: e.target.value})}
                  className="bg-background border-border"
                />
              </div>
              <div>
                <Label>Date de fin</Label>
                <Input
                  type="datetime-local"
                  value={newPromo.end_date}
                  onChange={(e) => setNewPromo({...newPromo, end_date: e.target.value})}
                  className="bg-background border-border"
                />
              </div>
            </div>
            <div>
              <Label>Rabais supplémentaire (%)</Label>
              <Input
                type="number"
                value={newPromo.additional_discount_percent}
                onChange={(e) => setNewPromo({...newPromo, additional_discount_percent: parseInt(e.target.value) || 0})}
                className="bg-background border-border w-32"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddModal(false)}>Annuler</Button>
            <Button onClick={createPromotion} className="btn-golden text-black">Créer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

// ============================================
// PARTNERS MANAGER
// ============================================
const PartnersManager = () => {
  const [partners, setPartners] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [partnersRes, appsRes] = await Promise.all([
        axios.get(`${API}/referral/admin/partners`),
        axios.get(`${API}/referral/admin/partner-applications?status=pending`)
      ]);
      setPartners(partnersRes.data.partners);
      setApplications(appsRes.data.applications);
    } catch (error) {
      console.error("Error loading partner data:", error);
    }
    setLoading(false);
  };

  const approveApplication = async (appId, commissionRate = 10) => {
    try {
      await axios.post(`${API}/referral/admin/partners/${appId}/approve`, {
        commission_rate: commissionRate
      });
      toast.success("Partenaire approuvé!");
      loadData();
      setSelectedApp(null);
    } catch (error) {
      toast.error("Erreur lors de l'approbation");
    }
  };

  const rejectApplication = async (appId, reason) => {
    try {
      await axios.post(`${API}/referral/admin/partners/${appId}/reject`, { reason });
      toast.success("Demande rejetée");
      loadData();
    } catch (error) {
      toast.error("Erreur");
    }
  };

  if (loading) {
    return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  return (
    <div className="space-y-6">
      {/* Pending Applications */}
      {applications.length > 0 && (
        <Card className="bg-yellow-500/10 border-yellow-500/30">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Crown className="h-5 w-5 text-yellow-500" />
              Demandes en attente ({applications.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {applications.map((app) => (
                <div key={app.id} className="flex items-center justify-between p-4 bg-background rounded-lg">
                  <div>
                    <p className="text-white font-medium">{app.business_name}</p>
                    <p className="text-gray-400 text-sm">
                      {app.business_type} • {app.existing_referrals} référents existants
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => setSelectedApp(app)}>
                      <Eye className="h-4 w-4 mr-1" /> Voir
                    </Button>
                    <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => approveApplication(app.id)}>
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => rejectApplication(app.id, "Non éligible")}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Partners */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Crown className="h-5 w-5 text-[#f5a623]" />
            Partenaires Privilégiés ({partners.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {partners.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Crown className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Aucun partenaire pour le moment</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border">
                  <TableHead className="text-gray-400">Partenaire</TableHead>
                  <TableHead className="text-gray-400">Type</TableHead>
                  <TableHead className="text-gray-400">Acheteurs</TableHead>
                  <TableHead className="text-gray-400">Revenus</TableHead>
                  <TableHead className="text-gray-400">Commission</TableHead>
                  <TableHead className="text-gray-400">Rabais</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {partners.map((partner) => (
                  <TableRow key={partner.id} className="border-border">
                    <TableCell>
                      <div>
                        <p className="text-white font-medium">{partner.name}</p>
                        <p className="text-gray-400 text-sm">{partner.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{partner.partner_type || "N/A"}</Badge>
                    </TableCell>
                    <TableCell className="text-white">{partner.total_buyers}</TableCell>
                    <TableCell className="text-[#f5a623]">${partner.total_revenue_generated?.toFixed(0)}</TableCell>
                    <TableCell>
                      <Badge className="bg-purple-600">{partner.partner_commission_rate}%</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className="bg-green-600">{partner.current_discount_percent}%</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Application Detail Modal */}
      <Dialog open={!!selectedApp} onOpenChange={() => setSelectedApp(null)}>
        <DialogContent className="bg-card border-border text-white">
          <DialogHeader>
            <DialogTitle>Demande de partenariat</DialogTitle>
          </DialogHeader>
          {selectedApp && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-400">Entreprise</Label>
                  <p className="text-white font-medium">{selectedApp.business_name}</p>
                </div>
                <div>
                  <Label className="text-gray-400">Type</Label>
                  <p className="text-white">{selectedApp.business_type}</p>
                </div>
              </div>
              <div>
                <Label className="text-gray-400">Site web</Label>
                <p className="text-white">{selectedApp.website || "Non spécifié"}</p>
              </div>
              <div>
                <Label className="text-gray-400">Volume mensuel estimé</Label>
                <p className="text-white">${selectedApp.estimated_monthly_volume}</p>
              </div>
              <div>
                <Label className="text-gray-400">Référents existants</Label>
                <p className="text-white">{selectedApp.existing_referrals}</p>
              </div>
              <div>
                <Label className="text-gray-400">Motivation</Label>
                <p className="text-gray-300 text-sm">{selectedApp.motivation || "Non spécifiée"}</p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedApp(null)}>Fermer</Button>
            <Button variant="destructive" onClick={() => rejectApplication(selectedApp?.id, "Non éligible")}>
              Rejeter
            </Button>
            <Button className="btn-golden text-black" onClick={() => approveApplication(selectedApp?.id)}>
              Approuver (10% commission)
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============================================
// MAIN ADMIN PANEL
// ============================================
const ReferralAdminPanel = () => {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/referral/admin/dashboard`);
      setStats(response.data);
    } catch (error) {
      console.error("Error loading stats:", error);
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Gift className="h-6 w-6 text-[#f5a623]" />
            Programme de Parrainage
          </h2>
          <p className="text-gray-400">
            Gestion des rabais, promotions et partenaires
          </p>
        </div>
        <div className="flex gap-2">
          <Badge className="bg-blue-500/20 text-blue-400 px-3 py-1">
            {stats.total_users || 0} parrains
          </Badge>
          <Badge className="bg-green-500/20 text-green-400 px-3 py-1">
            {stats.total_buyers || 0} acheteurs
          </Badge>
          <Badge className="bg-[#f5a623]/20 text-[#f5a623] px-3 py-1">
            ${(stats.total_revenue || 0).toFixed(0)} générés
          </Badge>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <p className="text-2xl font-bold text-white">{stats.total_users || 0}</p>
            <p className="text-gray-400 text-sm">Parrains</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Crown className="h-8 w-8 mx-auto mb-2 text-purple-500" />
            <p className="text-2xl font-bold text-white">{stats.total_partners || 0}</p>
            <p className="text-gray-400 text-sm">Partenaires</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-cyan-500" />
            <p className="text-2xl font-bold text-white">{stats.total_invites || 0}</p>
            <p className="text-gray-400 text-sm">Invités</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <ShoppingCart className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <p className="text-2xl font-bold text-white">{stats.total_buyers || 0}</p>
            <p className="text-gray-400 text-sm">Acheteurs</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <DollarSign className="h-8 w-8 mx-auto mb-2 text-[#f5a623]" />
            <p className="text-2xl font-bold text-[#f5a623]">${(stats.total_revenue || 0).toFixed(0)}</p>
            <p className="text-gray-400 text-sm">Revenus</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-background">
          <TabsTrigger value="dashboard">
            <TrendingUp className="h-4 w-4 mr-2" />
            Tableau de bord
          </TabsTrigger>
          <TabsTrigger value="tiers">
            <Percent className="h-4 w-4 mr-2" />
            Niveaux de rabais
          </TabsTrigger>
          <TabsTrigger value="promotions">
            <Calendar className="h-4 w-4 mr-2" />
            Promotions
          </TabsTrigger>
          <TabsTrigger value="partners">
            <Crown className="h-4 w-4 mr-2" />
            Partenaires
            {stats.pending_partner_applications > 0 && (
              <Badge className="bg-red-500 text-white ml-2 text-xs">{stats.pending_partner_applications}</Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Tier Distribution */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Distribution par niveau</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.tier_distribution && Object.entries(stats.tier_distribution).map(([tier, count]) => (
                    <div key={tier} className="flex items-center justify-between">
                      <TierBadge tier={tier} />
                      <span className="text-white font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Referrers */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Top parrains</CardTitle>
              </CardHeader>
              <CardContent>
                {stats.top_referrers?.length > 0 ? (
                  <div className="space-y-3">
                    {stats.top_referrers.slice(0, 5).map((user, idx) => (
                      <div key={user.id} className="flex items-center justify-between p-2 bg-background rounded">
                        <div className="flex items-center gap-3">
                          <span className="text-[#f5a623] font-bold">#{idx + 1}</span>
                          <div>
                            <p className="text-white font-medium">{user.name}</p>
                            <p className="text-gray-400 text-sm">{user.email}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-white font-medium">{user.total_buyers} acheteurs</p>
                          <p className="text-[#f5a623] text-sm">${user.total_revenue_generated?.toFixed(0)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-4">Aucun parrain pour le moment</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tiers Tab */}
        <TabsContent value="tiers" className="mt-6">
          <DiscountTiersManager />
        </TabsContent>

        {/* Promotions Tab */}
        <TabsContent value="promotions" className="mt-6">
          <SeasonalPromotionsManager />
        </TabsContent>

        {/* Partners Tab */}
        <TabsContent value="partners" className="mt-6">
          <PartnersManager />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReferralAdminPanel;
