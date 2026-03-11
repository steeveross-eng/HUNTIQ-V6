/**
 * AdminPage - Comprehensive Admin Dashboard
 * Extracted from App.js for better maintainability
 */

import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  Lock,
  LogOut,
  Edit,
  Save,
  Package,
  Users,
  TrendingUp,
  Store,
  Percent,
  Eye,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Truck,
  RefreshCw,
  Plus,
  Trash2,
  Award,
  FlaskConical,
  Globe,
  FolderOpen,
  Construction,
  MapPin,
  Power,
  Mail,
  ArrowLeft,
  Sparkles,
  Trees,
  Bell,
  DollarSign,
  MousePointer,
  ShoppingCart,
  Link as LinkIcon,
  Palette,
  Handshake
} from "lucide-react";
import { toast } from "sonner";

// Import admin sub-components
import ContentDepot from "@/components/ContentDepot";
import SiteAccessControl from "@/components/SiteAccessControl";
import MaintenanceControl from "@/components/MaintenanceControl";
import LandsPricingAdmin from "@/components/LandsPricingAdmin";
import AdminHotspotsPanel from "@/components/AdminHotspotsPanel";
import NetworkingAdmin from "@/components/NetworkingAdmin";
import EmailAdmin from "@/components/EmailAdmin";
import FeatureControlsAdmin from "@/components/FeatureControlsAdmin";
import BrandIdentityAdmin from "@/components/BrandIdentityAdmin";
import MarketingAIAdmin from "@/components/MarketingAIAdmin";
import CategoriesManager from "@/components/CategoriesManager";
import PromptManager from "@/components/PromptManager";
import BackupManager from "@/components/BackupManager";
import PartnershipAdmin from "@/components/PartnershipAdmin";
import { SaleModeBadge, AutoCategorizeButton } from "@/components/SharedComponents";
import { useLanguage } from "@/contexts/LanguageContext";
import { AnalyticsDashboard } from "@/modules/analytics/components/AnalyticsDashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// BackButton Component
const BackButton = ({ to = "/" }) => {
  const { t } = useLanguage();
  return (
    <Link to={to}>
      <Button variant="ghost" className="text-gray-400 hover:text-white">
        <ArrowLeft className="h-4 w-4 mr-2" />{t('common_home')}
      </Button>
    </Link>
  );
};

const AdminPage = ({ onProductsUpdate }) => {
  const { t } = useLanguage();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [refreshing, setRefreshing] = useState(false);
  
  // Data states
  const [stats, setStats] = useState({});
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [salesReport, setSalesReport] = useState({});
  const [productsReport, setProductsReport] = useState({});
  
  // Edit states
  const [editingProduct, setEditingProduct] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showAddSupplierDialog, setShowAddSupplierDialog] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: "", brand: "", price: 0, score: 0, cost_benefit_score: 0, rank: 1,
    image_url: "", description: "", category: "attractant", animal_type: "", season: "",
    sale_mode: "dropshipping", supplier_id: "", supplier_price: 0, affiliate_commission: 0,
    affiliate_link: "", dropshipping_available: true
  });
  const [newSupplier, setNewSupplier] = useState({
    name: "", contact_name: "", email: "", phone: "", address: "",
    partnership_type: "dropshipping", shipping_delay: 3, partnership_conditions: ""
  });

  const navigate = useNavigate();

  useEffect(() => {
    const auth = localStorage.getItem('admin_authenticated');
    if (auth === 'true') setIsAuthenticated(true);
  }, []);

  useEffect(() => {
    if (isAuthenticated) loadAllData();
  }, [isAuthenticated]);

  const loadAllData = async () => {
    try {
      const [statsRes, productsRes, suppliersRes, ordersRes, customersRes, commissionsRes, alertsRes, salesRes, productsReportRes] = await Promise.all([
        axios.get(`${API}/admin/stats`),
        axios.get(`${API}/admin/products`),
        axios.get(`${API}/suppliers`),
        axios.get(`${API}/orders`),
        axios.get(`${API}/customers`),
        axios.get(`${API}/commissions`),
        axios.get(`${API}/admin/alerts`),
        axios.get(`${API}/admin/reports/sales?period=month`),
        axios.get(`${API}/admin/reports/products`)
      ]);
      setStats(statsRes.data);
      setProducts(productsRes.data);
      setSuppliers(suppliersRes.data);
      setOrders(ordersRes.data);
      setCustomers(customersRes.data);
      setCommissions(commissionsRes.data);
      setAlerts(alertsRes.data);
      setSalesReport(salesRes.data);
      setProductsReport(productsReportRes.data);
    } catch (error) {
      console.error("Error loading admin data:", error);
    }
  };

  // Global refresh function for all admin data
  const handleGlobalRefresh = async () => {
    setRefreshing(true);
    await loadAllData();
    setRefreshing(false);
    toast.success(t('common_refresh') || 'Actualisé');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/admin/login`, { password });
      localStorage.setItem('admin_authenticated', 'true');
      setIsAuthenticated(true);
      toast.success("Connexion réussie!");
    } catch (error) {
      toast.error("Mot de passe incorrect");
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_authenticated');
    setIsAuthenticated(false);
    navigate("/");
  };

  const handleSaveProduct = async (productId) => {
    try {
      await axios.put(`${API}/admin/products/${productId}`, editForm);
      toast.success("Produit mis à jour!");
      setEditingProduct(null);
      loadAllData();
      if (onProductsUpdate) onProductsUpdate();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm("Supprimer ce produit?")) return;
    try {
      await axios.delete(`${API}/admin/products/${productId}`);
      toast.success("Produit supprimé!");
      loadAllData();
      if (onProductsUpdate) onProductsUpdate();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleAddProduct = async () => {
    try {
      await axios.post(`${API}/admin/products`, newProduct);
      toast.success("Produit ajouté!");
      setShowAddDialog(false);
      loadAllData();
      if (onProductsUpdate) onProductsUpdate();
    } catch (error) {
      toast.error("Erreur lors de l'ajout");
    }
  };

  const handleAddSupplier = async () => {
    try {
      await axios.post(`${API}/suppliers`, newSupplier);
      toast.success("Fournisseur ajouté!");
      setShowAddSupplierDialog(false);
      loadAllData();
    } catch (error) {
      toast.error("Erreur lors de l'ajout");
    }
  };

  const handleUpdateOrderStatus = async (orderId, status) => {
    try {
      await axios.put(`${API}/orders/${orderId}`, { status });
      toast.success("Statut mis à jour!");
      loadAllData();
    } catch (error) {
      toast.error("Erreur");
    }
  };

  // Login form
  if (!isAuthenticated) {
    return (
      <main className="pt-20 min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md bg-card border-border">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
              <Lock className="h-8 w-8 text-[#f5a623]" />
            </div>
            <CardTitle className="text-2xl text-white">Administration</CardTitle>
            <CardDescription>Entrez le mot de passe administrateur</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-background border-border text-white"
                placeholder="••••••••"
                data-testid="admin-password-input"
              />
              <Button type="submit" className="w-full btn-golden text-black font-semibold" disabled={loading} data-testid="admin-login-btn">
                {loading ? "Connexion..." : "Se connecter"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    );
  }

  // Admin Dashboard
  return (
    <main className="pt-20 min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <BackButton to="/" />
            <div>
              <h1 className="golden-text text-4xl font-bold">{t('admin_title')}</h1>
              <p className="text-gray-400 mt-2">{t('admin_hybrid_system')}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={handleGlobalRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {t('common_refresh')}
            </Button>
            <Button variant="outline" className="border-red-500 text-red-500" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />{t('common_logout')}
            </Button>
          </div>
        </div>

        {/* PRÉ-GO LIVE: Bannière de migration vers Admin Premium */}
        <Card className="bg-gradient-to-r from-[#f5a623]/20 to-purple-500/20 border-[#f5a623]/50 mb-6">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-[#f5a623]" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Interface Admin Premium disponible !</h3>
                <p className="text-gray-400 text-sm">
                  Accédez au nouveau tableau de bord unifié avec toutes les fonctionnalités X300%
                </p>
              </div>
            </div>
            <Button 
              className="btn-golden text-black font-semibold" 
              onClick={() => navigate('/admin-premium')}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Accéder à Admin Premium
            </Button>
          </CardContent>
        </Card>

        {/* Tabs - Modules essentiels seulement (PRÉ-GO LIVE: Modules redondants masqués) */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-card border border-border flex-wrap h-auto p-1">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <BarChart3 className="h-4 w-4 mr-2" />{t('admin_dashboard')}
            </TabsTrigger>
            <TabsTrigger value="sales" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <TrendingUp className="h-4 w-4 mr-2" />{t('admin_sales')}
            </TabsTrigger>
            <TabsTrigger value="products" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Package className="h-4 w-4 mr-2" />{t('admin_products')}
            </TabsTrigger>
            <TabsTrigger value="suppliers" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Store className="h-4 w-4 mr-2" />{t('admin_suppliers')}
            </TabsTrigger>
            <TabsTrigger value="customers" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Users className="h-4 w-4 mr-2" />{t('admin_customers')}
            </TabsTrigger>
            <TabsTrigger value="commissions" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Percent className="h-4 w-4 mr-2" />{t('admin_commissions')}
            </TabsTrigger>
            <TabsTrigger value="performance" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Award className="h-4 w-4 mr-2" />{t('admin_performance')}
            </TabsTrigger>
            {/* PRÉ-GO LIVE: Modules redondants masqués - Disponibles dans /admin-premium 
            <TabsTrigger value="categories">Catégories</TabsTrigger>
            <TabsTrigger value="content">Contenu</TabsTrigger>
            <TabsTrigger value="backup">Backup</TabsTrigger>
            <TabsTrigger value="access">Accès</TabsTrigger>
            <TabsTrigger value="lands">Terres</TabsTrigger>
            <TabsTrigger value="networking">Réseautage</TabsTrigger>
            <TabsTrigger value="email">Emails</TabsTrigger>
            <TabsTrigger value="marketing">Marketing</TabsTrigger>
            <TabsTrigger value="partnership">Partenaires</TabsTrigger>
            <TabsTrigger value="controls">Contrôles</TabsTrigger>
            <TabsTrigger value="identity">Identité</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            */}
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                      <Package className="h-5 w-5 text-[#f5a623]" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">{t('common_products')}</p>
                      <p className="text-xl font-bold text-white">{stats.products_count || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                      <ShoppingCart className="h-5 w-5 text-green-500" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">{t('common_orders')}</p>
                      <p className="text-xl font-bold text-white">{stats.orders_count || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <DollarSign className="h-5 w-5 text-blue-500" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">{t('admin_total_sales')}</p>
                      <p className="text-xl font-bold text-white">${stats.total_sales || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-purple-500" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">{t('admin_net_margins')}</p>
                      <p className="text-xl font-bold text-white">
                        ${stats.total_margins || 0}
                        <span className="text-sm text-purple-400 ml-1">
                          ({stats.total_sales > 0 ? ((stats.total_margins / stats.total_sales) * 100).toFixed(1) : 0}%)
                        </span>
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sales by Mode */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Truck className="h-5 w-5 text-blue-500" /> {t('admin_dropshipping')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-blue-500">${stats.dropshipping_sales || 0}</p>
                  <p className="text-gray-400 text-sm mt-1">{t('admin_dropshipping_sales')}</p>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <LinkIcon className="h-5 w-5 text-purple-500" /> {t('admin_affiliation')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-purple-500">${stats.affiliate_sales || 0}</p>
                  <p className="text-gray-400 text-sm mt-1">{t('admin_affiliate_sales')}</p>
                </CardContent>
              </Card>
            </div>

            {/* Commissions Overview */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">{t('admin_commissions')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-background rounded-lg">
                    <Clock className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-yellow-500">${stats.pending_commissions || 0}</p>
                    <p className="text-gray-400 text-sm">{t('admin_pending')}</p>
                  </div>
                  <div className="text-center p-4 bg-background rounded-lg">
                    <CheckCircle className="h-6 w-6 text-green-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-green-500">${stats.confirmed_commissions || 0}</p>
                    <p className="text-gray-400 text-sm">{t('admin_confirmed')}</p>
                  </div>
                  <div className="text-center p-4 bg-background rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-blue-500">${stats.paid_commissions || 0}</p>
                    <p className="text-gray-400 text-sm">{t('admin_paid')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Alerts */}
            {alerts.length > 0 && (
              <Card className="bg-card border-border border-yellow-500/50">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Bell className="h-5 w-5 text-yellow-500" /> {t('admin_alerts')} ({alerts.filter(a => !a.is_read).length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {alerts.slice(0, 5).map((alert) => (
                      <div key={alert.id} className={`p-3 rounded-lg flex items-center gap-3 ${alert.is_read ? 'bg-background' : 'bg-yellow-500/10'}`}>
                        <AlertTriangle className="h-5 w-5 text-yellow-500 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-white font-medium">{alert.title}</p>
                          <p className="text-gray-400 text-sm">{alert.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Sales Tab */}
          <TabsContent value="sales" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white">{t('admin_sales_tracking')}</CardTitle>
                <Badge className="bg-[#f5a623] text-black">{orders.length} {t('common_orders').toLowerCase()}</Badge>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-gray-400">ID</TableHead>
                      <TableHead className="text-gray-400">Date</TableHead>
                      <TableHead className="text-gray-400">Client</TableHead>
                      <TableHead className="text-gray-400">Produit</TableHead>
                      <TableHead className="text-gray-400">Mode</TableHead>
                      <TableHead className="text-gray-400">Prix</TableHead>
                      <TableHead className="text-gray-400">Marge</TableHead>
                      <TableHead className="text-gray-400">Statut</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell className="text-white font-mono text-xs">{order.id.slice(0, 8)}...</TableCell>
                        <TableCell className="text-gray-300">{new Date(order.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-gray-300">{order.customer_name || "Anonyme"}</TableCell>
                        <TableCell className="text-white">{order.product_name}</TableCell>
                        <TableCell><SaleModeBadge mode={order.sale_mode} /></TableCell>
                        <TableCell className="text-[#f5a623]">${order.sale_price}</TableCell>
                        <TableCell className="text-green-500">
                          ${order.net_margin?.toFixed(2)}
                          <span className="text-green-400/70 text-xs ml-1">
                            ({order.sale_price > 0 ? ((order.net_margin / order.sale_price) * 100).toFixed(1) : 0}%)
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge className={
                            order.status === "delivered" ? "bg-green-600" :
                            order.status === "shipped" ? "bg-blue-600" :
                            order.status === "processing" ? "bg-yellow-600" :
                            order.status === "cancelled" ? "bg-red-600" : "bg-gray-600"
                          }>{order.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <Select value={order.status} onValueChange={(value) => handleUpdateOrderStatus(order.id, value)}>
                            <SelectTrigger className="w-32 h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="pending">En attente</SelectItem>
                              <SelectItem value="processing">En cours</SelectItem>
                              <SelectItem value="shipped">Expédié</SelectItem>
                              <SelectItem value="delivered">Livré</SelectItem>
                              <SelectItem value="cancelled">Annulé</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Products Tab */}
          <TabsContent value="products" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white">{t('admin_product_management')}</CardTitle>
                <Button className="btn-golden text-black" onClick={() => setShowAddDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />{t('common_add')}
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {products.map((product) => (
                    <div key={product.id} className="flex items-center gap-4 p-4 bg-background rounded-lg">
                      <img src={product.image_url} alt={product.name} className="w-16 h-16 object-cover rounded" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className="rank-badge text-white">#{product.rank}</Badge>
                          <span className="text-[#f5a623] text-sm">{product.brand}</span>
                          <SaleModeBadge mode={product.sale_mode} />
                          {product.analysis_category && (
                            <Badge variant="outline" className="text-purple-400 border-purple-400 text-xs">
                              {product.analysis_category}
                              {product.analysis_subcategory && ` / ${product.analysis_subcategory}`}
                            </Badge>
                          )}
                        </div>
                        <h4 className="text-white font-medium">{product.name}</h4>
                        <div className="flex items-center gap-4 mt-1 text-sm">
                          <span className="text-[#f5a623]">${product.price}</span>
                          <span className="text-gray-400">Fournisseur: ${product.supplier_price || 0}</span>
                          <span className="text-green-500">Marge: ${(product.price - (product.supplier_price || 0)).toFixed(2)}</span>
                          {product.affiliate_commission > 0 && (
                            <span className="text-purple-500">Commission: {product.affiliate_commission}%</span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <AutoCategorizeButton product={product} onCategorized={loadAllData} />
                        <Button size="icon" variant="outline" className="border-[#f5a623] text-[#f5a623]" onClick={() => {
                          setEditingProduct(product.id);
                          setEditForm(product);
                        }}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button size="icon" variant="outline" className="border-red-500 text-red-500" onClick={() => handleDeleteProduct(product.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Edit Product Dialog */}
            <Dialog open={editingProduct !== null} onOpenChange={() => setEditingProduct(null)}>
              <DialogContent className="bg-card border-border text-white max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Modifier le produit</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nom</Label>
                      <Input value={editForm.name || ""} onChange={(e) => setEditForm({...editForm, name: e.target.value})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Marque</Label>
                      <Input value={editForm.brand || ""} onChange={(e) => setEditForm({...editForm, brand: e.target.value})} className="bg-background" />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label>Prix de vente ($)</Label>
                      <Input type="number" value={editForm.price || 0} onChange={(e) => setEditForm({...editForm, price: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Prix fournisseur ($)</Label>
                      <Input type="number" value={editForm.supplier_price || 0} onChange={(e) => setEditForm({...editForm, supplier_price: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Commission affiliée (%)</Label>
                      <Input type="number" value={editForm.affiliate_commission || 0} onChange={(e) => setEditForm({...editForm, affiliate_commission: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Mode de vente</Label>
                      <Select value={editForm.sale_mode || "dropshipping"} onValueChange={(value) => setEditForm({...editForm, sale_mode: value})}>
                        <SelectTrigger className="bg-background">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="dropshipping">Dropshipping</SelectItem>
                          <SelectItem value="affiliation">Affiliation</SelectItem>
                          <SelectItem value="hybrid">Hybride</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Fournisseur</Label>
                      <Select value={editForm.supplier_id || ""} onValueChange={(value) => setEditForm({...editForm, supplier_id: value})}>
                        <SelectTrigger className="bg-background">
                          <SelectValue placeholder="Sélectionner" />
                        </SelectTrigger>
                        <SelectContent>
                          {suppliers.map(s => (
                            <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label>Lien affilié</Label>
                    <Input value={editForm.affiliate_link || ""} onChange={(e) => setEditForm({...editForm, affiliate_link: e.target.value})} className="bg-background" placeholder="https://..." />
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch checked={editForm.dropshipping_available} onCheckedChange={(checked) => setEditForm({...editForm, dropshipping_available: checked})} />
                    <Label>Dropshipping disponible</Label>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setEditingProduct(null)}>Annuler</Button>
                  <Button className="btn-golden text-black" onClick={() => handleSaveProduct(editingProduct)}>Sauvegarder</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Add Product Dialog */}
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogContent className="bg-card border-border text-white max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Ajouter un produit</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nom</Label>
                      <Input value={newProduct.name} onChange={(e) => setNewProduct({...newProduct, name: e.target.value})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Marque</Label>
                      <Input value={newProduct.brand} onChange={(e) => setNewProduct({...newProduct, brand: e.target.value})} className="bg-background" />
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <div>
                      <Label>Prix ($)</Label>
                      <Input type="number" value={newProduct.price} onChange={(e) => setNewProduct({...newProduct, price: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Score</Label>
                      <Input type="number" value={newProduct.score} onChange={(e) => setNewProduct({...newProduct, score: parseInt(e.target.value)})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Rang</Label>
                      <Input type="number" value={newProduct.rank} onChange={(e) => setNewProduct({...newProduct, rank: parseInt(e.target.value)})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Prix fournisseur</Label>
                      <Input type="number" value={newProduct.supplier_price} onChange={(e) => setNewProduct({...newProduct, supplier_price: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                  </div>
                  <div>
                    <Label>URL Image</Label>
                    <Input value={newProduct.image_url} onChange={(e) => setNewProduct({...newProduct, image_url: e.target.value})} className="bg-background" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Mode de vente</Label>
                      <Select value={newProduct.sale_mode} onValueChange={(value) => setNewProduct({...newProduct, sale_mode: value})}>
                        <SelectTrigger className="bg-background">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="dropshipping">Dropshipping</SelectItem>
                          <SelectItem value="affiliation">Affiliation</SelectItem>
                          <SelectItem value="hybrid">Hybride</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Commission affiliée (%)</Label>
                      <Input type="number" value={newProduct.affiliate_commission} onChange={(e) => setNewProduct({...newProduct, affiliate_commission: parseFloat(e.target.value)})} className="bg-background" />
                    </div>
                  </div>
                  <div>
                    <Label>Lien affilié</Label>
                    <Input value={newProduct.affiliate_link} onChange={(e) => setNewProduct({...newProduct, affiliate_link: e.target.value})} className="bg-background" />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAddDialog(false)}>Annuler</Button>
                  <Button className="btn-golden text-black" onClick={handleAddProduct}>Ajouter</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </TabsContent>

          {/* Suppliers Tab */}
          <TabsContent value="suppliers" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white">{t('admin_partner_stores')}</CardTitle>
                <Button className="btn-golden text-black" onClick={() => setShowAddSupplierDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />{t('common_add')}
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {suppliers.map((supplier) => (
                    <div key={supplier.id} className="p-4 bg-background rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                            <Store className="h-6 w-6 text-[#f5a623]" />
                          </div>
                          <div>
                            <h4 className="text-white font-semibold">{supplier.name}</h4>
                            <p className="text-gray-400 text-sm">{supplier.email}</p>
                          </div>
                        </div>
                        <SaleModeBadge mode={supplier.partnership_type} />
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Commandes</p>
                          <p className="text-white font-semibold">{supplier.total_orders || 0}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Revenus fournisseur</p>
                          <p className="text-blue-500 font-semibold">${supplier.total_revenue_supplier?.toFixed(2) || 0}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Revenus Chasse Bionic™</p>
                          <p className="text-green-500 font-semibold">${supplier.total_revenue_scent?.toFixed(2) || 0}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Délai d'expédition</p>
                          <p className="text-white font-semibold">{supplier.shipping_delay} jours</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Add Supplier Dialog */}
            <Dialog open={showAddSupplierDialog} onOpenChange={setShowAddSupplierDialog}>
              <DialogContent className="bg-card border-border text-white">
                <DialogHeader>
                  <DialogTitle>Ajouter un partenaire</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nom du magasin</Label>
                      <Input value={newSupplier.name} onChange={(e) => setNewSupplier({...newSupplier, name: e.target.value})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Contact</Label>
                      <Input value={newSupplier.contact_name} onChange={(e) => setNewSupplier({...newSupplier, contact_name: e.target.value})} className="bg-background" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Email</Label>
                      <Input value={newSupplier.email} onChange={(e) => setNewSupplier({...newSupplier, email: e.target.value})} className="bg-background" />
                    </div>
                    <div>
                      <Label>Téléphone</Label>
                      <Input value={newSupplier.phone} onChange={(e) => setNewSupplier({...newSupplier, phone: e.target.value})} className="bg-background" />
                    </div>
                  </div>
                  <div>
                    <Label>Type de partenariat</Label>
                    <Select value={newSupplier.partnership_type} onValueChange={(value) => setNewSupplier({...newSupplier, partnership_type: value})}>
                      <SelectTrigger className="bg-background">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dropshipping">Dropshipping</SelectItem>
                        <SelectItem value="affiliation">Affiliation</SelectItem>
                        <SelectItem value="hybrid">Hybride</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Délai d'expédition (jours)</Label>
                    <Input type="number" value={newSupplier.shipping_delay} onChange={(e) => setNewSupplier({...newSupplier, shipping_delay: parseInt(e.target.value)})} className="bg-background" />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAddSupplierDialog(false)}>Annuler</Button>
                  <Button className="btn-golden text-black" onClick={handleAddSupplier}>Ajouter</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </TabsContent>

          {/* Customers Tab */}
          <TabsContent value="customers" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">{t('admin_customer_tracking')}</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-gray-400">Client</TableHead>
                      <TableHead className="text-gray-400">Email</TableHead>
                      <TableHead className="text-gray-400">Commandes</TableHead>
                      <TableHead className="text-gray-400">Analysés</TableHead>
                      <TableHead className="text-gray-400">Comparés</TableHead>
                      <TableHead className="text-gray-400">LTV</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {customers.map((customer) => (
                      <TableRow key={customer.id}>
                        <TableCell className="text-white">{customer.name || "Anonyme"}</TableCell>
                        <TableCell className="text-gray-300">{customer.email || "-"}</TableCell>
                        <TableCell className="text-white">{customer.total_orders || 0}</TableCell>
                        <TableCell className="text-gray-300">{customer.products_analyzed?.length || 0}</TableCell>
                        <TableCell className="text-gray-300">{customer.products_compared?.length || 0}</TableCell>
                        <TableCell className="text-[#f5a623] font-semibold">${customer.total_spent?.toFixed(2) || 0}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Commissions Tab */}
          <TabsContent value="commissions" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">{t('admin_commission_tracking')}</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-gray-400">Type</TableHead>
                      <TableHead className="text-gray-400">Produit</TableHead>
                      <TableHead className="text-gray-400">Fournisseur</TableHead>
                      <TableHead className="text-gray-400">Montant</TableHead>
                      <TableHead className="text-gray-400">Statut</TableHead>
                      <TableHead className="text-gray-400">Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {commissions.map((commission) => (
                      <TableRow key={commission.id}>
                        <TableCell>
                          <Badge className={commission.commission_type === "affiliate" ? "bg-purple-600" : "bg-blue-600"}>
                            {commission.commission_type === "affiliate" ? "Affiliation" : "Marge"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-white">{commission.product_name}</TableCell>
                        <TableCell className="text-gray-300">{commission.supplier_name || "-"}</TableCell>
                        <TableCell className="text-green-500 font-semibold">${commission.amount?.toFixed(2)}</TableCell>
                        <TableCell>
                          <Badge className={
                            commission.status === "paid" ? "bg-green-600" :
                            commission.status === "confirmed" ? "bg-blue-600" : "bg-yellow-600"
                          }>{commission.status}</Badge>
                        </TableCell>
                        <TableCell className="text-gray-300">{new Date(commission.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Eye className="h-5 w-5 text-blue-500" /> {t('admin_most_viewed')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {productsReport.most_viewed?.slice(0, 5).map((product, index) => (
                    <div key={product.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <span className="text-white">{index + 1}. {product.name}</span>
                      <span className="text-gray-400">{product.views} {t('admin_views')}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5 text-green-500" /> {t('admin_most_ordered')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {productsReport.most_ordered?.slice(0, 5).map((product, index) => (
                    <div key={product.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <span className="text-white">{index + 1}. {product.name}</span>
                      <span className="text-gray-400">{product.orders} {t('common_orders').toLowerCase()}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-[#f5a623]" /> {t('admin_best_conversion')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {productsReport.best_conversion?.slice(0, 5).map((product, index) => (
                    <div key={product.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <span className="text-white">{index + 1}. {product.name}</span>
                      <span className="text-[#f5a623]">{product.overall_conversion_rate}%</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <MousePointer className="h-5 w-5 text-purple-500" /> {t('admin_most_clicked')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {productsReport.most_clicked?.slice(0, 5).map((product, index) => (
                    <div key={product.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <span className="text-white">{index + 1}. {product.name}</span>
                      <span className="text-gray-400">{product.clicks} {t('admin_clicks')}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Categories Tab */}
          <TabsContent value="categories" className="space-y-6">
            <CategoriesManager />
          </TabsContent>

          {/* Content SEO Tab - Content Depot & SEO */}
          <TabsContent value="content" className="space-y-6">
            <ContentDepot />
          </TabsContent>

          {/* PROMPT Tab - Documentation & Features */}
          {/* Backup Tab (formerly Prompt) */}
          <TabsContent value="backup" className="space-y-6">
            <BackupManager />
          </TabsContent>

          {/* Access Control Tab */}
          <TabsContent value="access" className="space-y-6">
            {/* NEW: Secure Maintenance Control */}
            <MaintenanceControl />
            
            {/* Legacy Site Access Control (for backward compatibility) */}
            <SiteAccessControl />
          </TabsContent>

          {/* Hotspots Tab - All hotspots management */}
          <TabsContent value="lands" className="space-y-6">
            {/* Hotspots Administration Panel - Shows ALL hotspots for admin */}
            <AdminHotspotsPanel />
            
            {/* Separator */}
            <div className="border-t border-slate-700 pt-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Trees className="h-5 w-5" />
                {t('admin_lands_pricing')}
              </h3>
            </div>
            
            {/* Original Lands Pricing */}
            <LandsPricingAdmin />
          </TabsContent>

          {/* Networking Admin Tab */}
          <TabsContent value="networking" className="space-y-6">
            <NetworkingAdmin />
          </TabsContent>

          {/* Email Admin Tab */}
          <TabsContent value="email" className="space-y-6">
            <EmailAdmin />
          </TabsContent>

          {/* Feature Controls Admin Tab */}
          <TabsContent value="controls" className="space-y-6">
            <FeatureControlsAdmin adminEmail="steeve.ross@gmail.com" />
          </TabsContent>

          {/* Marketing AI Tab */}
          <TabsContent value="marketing" className="space-y-6">
            <MarketingAIAdmin />
          </TabsContent>

          {/* Partnership Admin Tab */}
          <TabsContent value="partnership" className="space-y-6">
            <PartnershipAdmin />
          </TabsContent>

          {/* Brand Identity Admin Tab */}
          <TabsContent value="identity" className="space-y-6">
            <BrandIdentityAdmin />
          </TabsContent>
          
          {/* V5-ULTIME-FUSION: Analytics - Module activé */}
          <TabsContent value="analytics" className="space-y-6">
            <AnalyticsDashboard />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
};

export default AdminPage;
