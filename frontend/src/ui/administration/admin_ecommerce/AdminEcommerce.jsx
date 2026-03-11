/**
 * AdminEcommerce - V5-ULTIME Administration Premium
 * ==================================================
 * 
 * Module E-Commerce complet pour l'administration:
 * - Dashboard stats
 * - Gestion commandes
 * - Gestion produits
 * - Gestion fournisseurs
 * - Gestion clients
 * - Gestion commissions
 * - Performance / Analytics
 * 
 * Phase 1 Migration /admin → /admin-premium
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { 
  ShoppingCart, Package, Users, Truck, DollarSign, TrendingUp,
  RefreshCw, Plus, Edit, Trash2, Search, Eye, MousePointer,
  CheckCircle, Clock, XCircle, AlertTriangle, BarChart3
} from 'lucide-react';
import AdminService from '../AdminService';

// ============ DASHBOARD TAB ============
const DashboardTab = ({ stats, loading }) => {
  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
    </div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Package className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-gray-400 text-sm">Produits</p>
                <p className="text-2xl font-bold text-blue-400">{stats?.products_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <ShoppingCart className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-gray-400 text-sm">Commandes</p>
                <p className="text-2xl font-bold text-green-400">{stats?.orders_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <DollarSign className="h-8 w-8 text-[#F5A623]" />
              <div>
                <p className="text-gray-400 text-sm">Ventes totales</p>
                <p className="text-2xl font-bold text-[#F5A623]">{stats?.total_sales || 0}$</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-purple-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-purple-500" />
              <div>
                <p className="text-gray-400 text-sm">Marge</p>
                <p className="text-2xl font-bold text-purple-400">{stats?.margin_rate || 0}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sales Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white text-lg">Ventes par canal</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-300">Dropshipping</span>
                <span className="text-[#F5A623] font-bold">{stats?.dropshipping_sales || 0}$</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-300">Affiliation</span>
                <span className="text-[#F5A623] font-bold">{stats?.affiliate_sales || 0}$</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardHeader>
            <CardTitle className="text-white text-lg">Commissions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-300 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-yellow-500" /> En attente
                </span>
                <span className="text-yellow-400 font-bold">{stats?.pending_commissions || 0}$</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-300 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" /> Confirmées
                </span>
                <span className="text-green-400 font-bold">{stats?.confirmed_commissions || 0}$</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-300 flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-blue-500" /> Payées
                </span>
                <span className="text-blue-400 font-bold">{stats?.paid_commissions || 0}$</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
          <Truck className="h-6 w-6 text-[#F5A623]" />
          <div>
            <p className="text-white font-medium">Fournisseurs actifs</p>
            <p className="text-gray-400 text-sm">{stats?.suppliers_count || 0} partenaires</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-4 bg-white/5 rounded-lg">
          <Users className="h-6 w-6 text-[#F5A623]" />
          <div>
            <p className="text-white font-medium">Clients</p>
            <p className="text-gray-400 text-sm">{stats?.customers_count || 0} clients enregistrés</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============ ORDERS TAB ============
const OrdersTab = ({ orders, statusCounts, loading, onRefresh, onUpdateStatus }) => {
  const [filter, setFilter] = useState('');

  const statusIcon = (status) => {
    switch(status) {
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'processing': return <RefreshCw className="h-4 w-4 text-blue-500" />;
      case 'shipped': return <Truck className="h-4 w-4 text-purple-500" />;
      case 'delivered': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const statusColor = (status) => {
    switch(status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'processing': return 'bg-blue-500/20 text-blue-400';
      case 'shipped': return 'bg-purple-500/20 text-purple-400';
      case 'delivered': return 'bg-green-500/20 text-green-400';
      case 'cancelled': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
    </div>;
  }

  return (
    <div className="space-y-4">
      {/* Status Summary */}
      <div className="flex flex-wrap gap-2">
        {statusCounts && Object.entries(statusCounts).map(([status, count]) => (
          <Badge key={status} className={`${statusColor(status)} cursor-pointer`}>
            {statusIcon(status)}
            <span className="ml-1">{status}: {count}</span>
          </Badge>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
        <Input
          placeholder="Rechercher une commande..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="pl-10 bg-[#0d0d1a] border-[#F5A623]/20 text-white"
        />
      </div>

      {/* Orders List */}
      <div className="space-y-2 max-h-96 overflow-auto">
        {orders.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Aucune commande</p>
        ) : (
          orders
            .filter(o => 
              !filter || 
              o.id?.toLowerCase().includes(filter.toLowerCase()) ||
              o.customer_email?.toLowerCase().includes(filter.toLowerCase())
            )
            .map((order, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div className="flex items-center gap-3">
                  {statusIcon(order.status)}
                  <div>
                    <p className="text-white font-medium">{order.id || `Order #${i + 1}`}</p>
                    <p className="text-gray-500 text-sm">{order.customer_email || 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[#F5A623] font-bold">{order.sale_price || 0}$</span>
                  <Badge className={statusColor(order.status)}>{order.status}</Badge>
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
};

// ============ PRODUCTS TAB ============
const ProductsTab = ({ products, categories, loading, onRefresh }) => {
  const [filter, setFilter] = useState('');

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
    </div>;
  }

  return (
    <div className="space-y-4">
      {/* Categories */}
      <div className="flex flex-wrap gap-2">
        {categories?.map((cat) => (
          <Badge key={cat} className="bg-[#F5A623]/20 text-[#F5A623]">{cat}</Badge>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
        <Input
          placeholder="Rechercher un produit..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="pl-10 bg-[#0d0d1a] border-[#F5A623]/20 text-white"
        />
      </div>

      {/* Products List */}
      <div className="space-y-2 max-h-96 overflow-auto">
        {products.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Aucun produit</p>
        ) : (
          products
            .filter(p => 
              !filter || 
              p.name?.toLowerCase().includes(filter.toLowerCase())
            )
            .map((product, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium">{product.name || `Product #${i + 1}`}</p>
                  <p className="text-gray-500 text-sm">{product.category}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-[#F5A623] font-bold">{product.sale_price || 0}$</p>
                    <p className="text-gray-500 text-xs">Marge: {product.net_margin || 0}$</p>
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost" className="text-gray-400 hover:text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
};

// ============ PERFORMANCE TAB ============
const PerformanceTab = ({ performance, loading }) => {
  if (loading || !performance?.report) {
    return <div className="flex items-center justify-center h-64">
      <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
    </div>;
  }

  const { most_viewed, most_ordered, most_clicked, best_conversion } = performance.report;

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Most Viewed */}
      <Card className="bg-[#0d0d1a] border-blue-500/30">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Eye className="h-5 w-5 text-blue-500" />
            Plus vus
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {most_viewed?.slice(0, 5).map((p, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                <span className="text-gray-300 text-sm truncate max-w-[200px]">{p.name}</span>
                <Badge className="bg-blue-500/20 text-blue-400">{p.views} vues</Badge>
              </div>
            )) || <p className="text-gray-500 text-center">Aucune donnée</p>}
          </div>
        </CardContent>
      </Card>

      {/* Most Ordered */}
      <Card className="bg-[#0d0d1a] border-green-500/30">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-green-500" />
            Plus commandés
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {most_ordered?.slice(0, 5).map((p, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                <span className="text-gray-300 text-sm truncate max-w-[200px]">{p.name}</span>
                <Badge className="bg-green-500/20 text-green-400">{p.orders} cmd</Badge>
              </div>
            )) || <p className="text-gray-500 text-center">Aucune donnée</p>}
          </div>
        </CardContent>
      </Card>

      {/* Most Clicked */}
      <Card className="bg-[#0d0d1a] border-purple-500/30">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <MousePointer className="h-5 w-5 text-purple-500" />
            Plus cliqués
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {most_clicked?.slice(0, 5).map((p, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                <span className="text-gray-300 text-sm truncate max-w-[200px]">{p.name}</span>
                <Badge className="bg-purple-500/20 text-purple-400">{p.clicks} clics</Badge>
              </div>
            )) || <p className="text-gray-500 text-center">Aucune donnée</p>}
          </div>
        </CardContent>
      </Card>

      {/* Best Conversion */}
      <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Meilleure conversion
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {best_conversion?.slice(0, 5).map((p, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                <span className="text-gray-300 text-sm truncate max-w-[200px]">{p.name}</span>
                <Badge className="bg-[#F5A623]/20 text-[#F5A623]">
                  {(p.overall_conversion_rate * 100).toFixed(1)}%
                </Badge>
              </div>
            )) || <p className="text-gray-500 text-center">Aucune donnée</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============ MAIN COMPONENT ============
const AdminEcommerce = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [statusCounts, setStatusCounts] = useState({});
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [performance, setPerformance] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    
    try {
      const API_BASE = process.env.REACT_APP_BACKEND_URL;
      
      const [dashRes, ordersRes, productsRes, suppliersRes, customersRes, commissionsRes, perfRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/admin/ecommerce/dashboard`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/orders?limit=50`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/products?limit=50`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/suppliers?limit=50`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/customers?limit=50`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/commissions?limit=50`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/admin/ecommerce/performance`).then(r => r.json())
      ]);

      if (dashRes.success) setStats(dashRes.stats);
      if (ordersRes.success) {
        setOrders(ordersRes.orders || []);
        setStatusCounts(ordersRes.status_counts || {});
      }
      if (productsRes.success) {
        setProducts(productsRes.products || []);
        setCategories(productsRes.categories || []);
      }
      if (suppliersRes.success) setSuppliers(suppliersRes.suppliers || []);
      if (customersRes.success) setCustomers(customersRes.customers || []);
      if (commissionsRes.success) setCommissions(commissionsRes.commissions || []);
      if (perfRes.success) setPerformance(perfRes);
    } catch (error) {
      console.error('Error fetching ecommerce data:', error);
    }
    
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div data-testid="admin-ecommerce" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShoppingCart className="h-6 w-6 text-[#F5A623]" />
          Gestion E-Commerce
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="bg-[#0d0d1a] border border-[#F5A623]/20 flex-wrap h-auto gap-1 p-1">
          <TabsTrigger value="dashboard" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <BarChart3 className="h-4 w-4 mr-2" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="orders" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <ShoppingCart className="h-4 w-4 mr-2" />
            Ventes
          </TabsTrigger>
          <TabsTrigger value="products" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Package className="h-4 w-4 mr-2" />
            Produits
          </TabsTrigger>
          <TabsTrigger value="suppliers" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Truck className="h-4 w-4 mr-2" />
            Fournisseurs
          </TabsTrigger>
          <TabsTrigger value="customers" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <Users className="h-4 w-4 mr-2" />
            Clients
          </TabsTrigger>
          <TabsTrigger value="commissions" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <DollarSign className="h-4 w-4 mr-2" />
            Commissions
          </TabsTrigger>
          <TabsTrigger value="performance" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            <TrendingUp className="h-4 w-4 mr-2" />
            Performance
          </TabsTrigger>
        </TabsList>

        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardContent className="p-6">
            <TabsContent value="dashboard" className="mt-0">
              <DashboardTab stats={stats} loading={loading} />
            </TabsContent>

            <TabsContent value="orders" className="mt-0">
              <OrdersTab 
                orders={orders} 
                statusCounts={statusCounts} 
                loading={loading} 
                onRefresh={fetchData}
              />
            </TabsContent>

            <TabsContent value="products" className="mt-0">
              <ProductsTab 
                products={products} 
                categories={categories} 
                loading={loading} 
                onRefresh={fetchData}
              />
            </TabsContent>

            <TabsContent value="suppliers" className="mt-0">
              <div className="space-y-2 max-h-96 overflow-auto">
                {suppliers.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Aucun fournisseur</p>
                ) : (
                  suppliers.map((s, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white font-medium">{s.name}</p>
                        <p className="text-gray-500 text-sm">{s.partnership_type || 'Standard'}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[#F5A623] font-bold">{s.total_orders || 0} commandes</p>
                        <p className="text-gray-500 text-sm">{s.total_revenue_supplier || 0}$ revenus</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="customers" className="mt-0">
              <div className="space-y-2 max-h-96 overflow-auto">
                {customers.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Aucun client</p>
                ) : (
                  customers.map((c, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white font-medium">{c.email || c.name || `Client #${i + 1}`}</p>
                        <p className="text-gray-500 text-sm">{c.total_orders || 0} commandes</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[#F5A623] font-bold">{c.total_spent || 0}$</p>
                        <Badge className="bg-blue-500/20 text-blue-400">LTV</Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="commissions" className="mt-0">
              <div className="space-y-2 max-h-96 overflow-auto">
                {commissions.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Aucune commission</p>
                ) : (
                  commissions.map((c, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white font-medium">{c.commission_type || 'Commission'}</p>
                        <p className="text-gray-500 text-sm">{c.order_id || `#${i + 1}`}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[#F5A623] font-bold">{c.amount || 0}$</span>
                        <Badge className={`
                          ${c.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' : ''}
                          ${c.status === 'confirmed' ? 'bg-green-500/20 text-green-400' : ''}
                          ${c.status === 'paid' ? 'bg-blue-500/20 text-blue-400' : ''}
                        `}>
                          {c.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="performance" className="mt-0">
              <PerformanceTab performance={performance} loading={loading} />
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
};

export default AdminEcommerce;
