/**
 * BusinessDashboard - Central dashboard for business modules
 * Phase 9 - Business Modules Integration
 * Version: 1.2.0 - BIONIC Design System Compliance
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { useLanguage } from '../../contexts/LanguageContext';
import { 
  Briefcase, 
  Package, 
  ClipboardList, 
  Users, 
  Factory, 
  BarChart3,
  Loader2
} from 'lucide-react';

// Business Module Imports
import { UserProfile, UserActivity } from '../user';
import { ProductCard, ProductGrid } from '../products';
import { OrderCard, OrdersList } from '../orders';
import { CartWidget } from '../cart';
import { AffiliateStats } from '../affiliate';
import { SupplierCard } from '../suppliers';
import { CustomerCard } from '../customers';

// Weather Module Import
import { AdvancedWeatherWidget } from '../weather';

// Services
import { UserService } from '../user/UserService';
import { ProductsService } from '../products/ProductsService';
import { OrdersService } from '../orders/OrdersService';
import { CartService } from '../cart/CartService';
import { AffiliateService } from '../affiliate/AffiliateService';
import { SuppliersService } from '../suppliers/SuppliersService';
import { CustomersService } from '../customers/CustomersService';

export const BusinessDashboard = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  
  // Data states
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [stats, setStats] = useState({
    products: { total: 0 },
    orders: { total: 0, pending: 0 },
    cart: { items: 0 },
    affiliate: { clicks: 0, conversion: 0 },
    suppliers: { total: 0 },
    customers: { total: 0 }
  });

  // Load dashboard data
  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    
    try {
      // Load in parallel
      const [
        productsData,
        ordersData,
        cartData,
        affiliateStats,
        suppliersData,
        customersData
      ] = await Promise.all([
        ProductsService.getTopProducts(8).catch(() => []),
        OrdersService.getOrders({ limit: 10 }).catch(() => []),
        CartService.getCart(CartService.getSessionId()).catch(() => ({ items: [] })),
        AffiliateService.getStats().catch(() => ({})),
        SuppliersService.getSuppliers().catch(() => []),
        CustomersService.getCustomers().catch(() => [])
      ]);

      setProducts(productsData);
      setOrders(ordersData);
      setCartItems(cartData.items || []);
      setSuppliers(suppliersData);
      setCustomers(customersData);

      setStats({
        products: { total: productsData.length },
        orders: { 
          total: ordersData.length, 
          pending: ordersData.filter(o => o.status === 'pending').length 
        },
        cart: { items: (cartData.items || []).length },
        affiliate: {
          clicks: affiliateStats.total_clicks || 0,
          conversion: affiliateStats.conversion_rate || 0
        },
        suppliers: { total: suppliersData.length },
        customers: { total: customersData.length }
      });

    } catch (error) {
      console.error('Business dashboard load error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Handlers
  const handleAddToCart = async (product) => {
    try {
      await CartService.addItem(CartService.getSessionId(), product.id, 1);
      const cartData = await CartService.getCart(CartService.getSessionId());
      setCartItems(cartData.items || []);
    } catch (error) {
      console.error('Add to cart error:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-[var(--bionic-gold-primary)] mx-auto mb-4" />
          <p className="text-[var(--bionic-text-secondary)]">{t('business_loading') || t('common_loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="business-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--bionic-text-primary)] flex items-center gap-3">
            <Briefcase className="h-7 w-7 text-[var(--bionic-gold-primary)]" />
            {t('business_title')}
          </h1>
          <p className="text-[var(--bionic-text-secondary)] text-sm mt-1">
            {t('business_overview')} • Phase 9
          </p>
        </div>
        
        {/* Quick Stats */}
        <div className="flex items-center gap-3">
          <Badge className="bg-[var(--bionic-blue-muted)] text-[var(--bionic-blue-light)] flex items-center gap-1">
            <Package className="h-3 w-3" /> {stats.products.total} {t('common_products')}
          </Badge>
          <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)] flex items-center gap-1">
            <ClipboardList className="h-3 w-3" /> {stats.orders.total} {t('common_orders')}
          </Badge>
          <Badge className="bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)] flex items-center gap-1">
            <Users className="h-3 w-3" /> {stats.customers.total} {t('common_customers')}
          </Badge>
        </div>
      </div>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-secondary)] w-full justify-start">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <BarChart3 className="h-4 w-4" /> {t('business_overview')}
          </TabsTrigger>
          <TabsTrigger value="products" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Package className="h-4 w-4" /> {t('common_products')}
          </TabsTrigger>
          <TabsTrigger value="orders" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <ClipboardList className="h-4 w-4" /> {t('common_orders')}
          </TabsTrigger>
          <TabsTrigger value="customers" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Users className="h-4 w-4" /> {t('common_customers')}
          </TabsTrigger>
          <TabsTrigger value="suppliers" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Factory className="h-4 w-4" /> {t('common_suppliers')}
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          {/* Weather Widget - Full Width */}
          <div className="mb-6">
            <AdvancedWeatherWidget 
              lat={46.8139} 
              lng={-71.2080}
              showHourly={true}
              showDaily={true}
              compact={false}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Stats Cards */}
            <div className="space-y-4">
              {/* Orders Summary */}
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <ClipboardList className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                    {t('common_orders')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-[var(--bionic-blue-light)]">{stats.orders.total}</div>
                      <div className="text-xs text-[var(--bionic-text-secondary)]">Total</div>
                    </div>
                    <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-[var(--bionic-gold-primary)]">{stats.orders.pending}</div>
                      <div className="text-xs text-[var(--bionic-text-secondary)]">{t('admin_pending')}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Affiliate Stats */}
              <AffiliateStats stats={{
                total_clicks: stats.affiliate.clicks,
                conversion_rate: stats.affiliate.conversion,
                total_sales: Math.floor(stats.affiliate.clicks * stats.affiliate.conversion / 100),
                total_commission: Math.floor(stats.affiliate.clicks * stats.affiliate.conversion / 100) * 5
              }} />

              {/* Quick Cart */}
              <CartWidget 
                items={cartItems}
                compact={true}
              />
            </div>

            {/* Center Column - Recent Orders */}
            <div className="space-y-4">
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <ClipboardList className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                      {t('business_orders_pending') || 'Commandes Récentes'}
                    </span>
                    <Badge className="bg-[var(--bionic-bg-secondary)]">{orders.length}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {orders.length > 0 ? (
                    <div className="space-y-3">
                      {orders.slice(0, 3).map((order) => (
                        <OrderCard key={order.id} order={order} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-[var(--bionic-text-secondary)]">
                      <ClipboardList className="h-8 w-8 mx-auto mb-2 text-[var(--bionic-gray-500)]" />
                      <p className="text-sm">{t('msg_no_results') || 'Aucune commande'}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Top Customers */}
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <Users className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                    {t('common_customers')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {customers.length > 0 ? (
                    <div className="space-y-2">
                      {customers.slice(0, 3).map((customer) => (
                        <CustomerCard key={customer.id} customer={customer} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-[var(--bionic-text-secondary)]">
                      <p className="text-sm">{t('msg_no_results') || 'Aucun client'}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Top Products */}
            <div className="space-y-4">
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Package className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                      {t('common_products')}
                    </span>
                    <Badge className="bg-[var(--bionic-gold-primary)] text-black">{products.length}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {products.length > 0 ? (
                    <div className="space-y-3">
                      {products.slice(0, 4).map((product) => (
                        <ProductCard 
                          key={product.id} 
                          product={product} 
                          compact 
                          onAddToCart={handleAddToCart}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-[var(--bionic-text-secondary)]">
                      <Package className="h-8 w-8 mx-auto mb-2 text-[var(--bionic-gray-500)]" />
                      <p className="text-sm">{t('msg_no_results') || 'Aucun produit'}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Suppliers Quick List */}
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <Factory className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                    {t('common_suppliers')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {suppliers.length > 0 ? (
                    <div className="space-y-2">
                      {suppliers.slice(0, 3).map((supplier) => (
                        <SupplierCard key={supplier.id} supplier={supplier} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-[var(--bionic-text-secondary)]">
                      <p className="text-sm">{t('msg_no_results') || 'Aucun fournisseur'}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Products Tab */}
        <TabsContent value="products" className="mt-6">
          <ProductGrid 
            products={products}
            onAddToCart={handleAddToCart}
            columns={4}
            emptyMessage={t('msg_no_results')}
          />
        </TabsContent>

        {/* Orders Tab */}
        <TabsContent value="orders" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <OrdersList 
                orders={orders}
                emptyMessage={t('msg_no_results')}
              />
            </div>
            <div>
              <CartWidget 
                items={cartItems}
              />
            </div>
          </div>
        </TabsContent>

        {/* Customers Tab */}
        <TabsContent value="customers" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.length > 0 ? (
              customers.map((customer) => (
                <CustomerCard key={customer.id} customer={customer} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <Users className="h-12 w-12 text-[var(--bionic-gray-500)] mx-auto mb-4" />
                <p className="text-[var(--bionic-text-secondary)]">{t('msg_no_results')}</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Suppliers Tab */}
        <TabsContent value="suppliers" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suppliers.length > 0 ? (
              suppliers.map((supplier) => (
                <SupplierCard key={supplier.id} supplier={supplier} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <Factory className="h-12 w-12 text-[var(--bionic-gray-500)] mx-auto mb-4" />
                <p className="text-[var(--bionic-text-secondary)]">{t('msg_no_results')}</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BusinessDashboard;
