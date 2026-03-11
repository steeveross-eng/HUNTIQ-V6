/**
 * AdminPayments - V5-ULTIME Administration Premium
 * =================================================
 * 
 * Gestion des paiements Stripe.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { 
  CreditCard, TrendingUp, RefreshCw, DollarSign,
  Calendar, CheckCircle, XCircle, Clock
} from 'lucide-react';
import AdminService from '../AdminService';

const AdminPayments = () => {
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [revenue, setRevenue] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const [txResult, revResult, subResult] = await Promise.all([
      AdminService.getTransactions(20),
      AdminService.getRevenueStats(30),
      AdminService.getSubscriptions(null, 20)
    ]);
    
    if (txResult.success) setTransactions(txResult.transactions || []);
    if (revResult.success) setRevenue(revResult);
    if (subResult.success) setSubscriptions(subResult.subscriptions || []);
    setLoading(false);
  };

  const statusIcon = (status) => {
    switch(status) {
      case 'paid': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-payments" className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <CreditCard className="h-6 w-6 text-[#F5A623]" />
          Gestion des Paiements
        </h2>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Revenue Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-[#0d0d1a] border-green-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <DollarSign className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-gray-400 text-sm">Revenus (30j)</p>
                <p className="text-2xl font-bold text-green-400">{revenue?.revenue?.total || 0}$</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-[#F5A623]/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CreditCard className="h-8 w-8 text-[#F5A623]" />
              <div>
                <p className="text-gray-400 text-sm">Transactions</p>
                <p className="text-2xl font-bold text-[#F5A623]">{revenue?.revenue?.transaction_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-blue-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-gray-400 text-sm">Premium</p>
                <p className="text-2xl font-bold text-blue-400">{revenue?.by_tier?.premium_monthly?.count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-purple-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Calendar className="h-8 w-8 text-purple-500" />
              <div>
                <p className="text-gray-400 text-sm">Pro</p>
                <p className="text-2xl font-bold text-purple-400">{revenue?.by_tier?.pro_monthly?.count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="transactions" className="space-y-4">
        <TabsList className="bg-[#0d0d1a] border border-[#F5A623]/20">
          <TabsTrigger value="transactions" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            Transactions
          </TabsTrigger>
          <TabsTrigger value="subscriptions" className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black">
            Abonnements
          </TabsTrigger>
        </TabsList>

        <TabsContent value="transactions">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardHeader>
              <CardTitle className="text-white">Dernières transactions</CardTitle>
            </CardHeader>
            <CardContent>
              {transactions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Aucune transaction</p>
              ) : (
                <div className="space-y-2">
                  {transactions.map((tx, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-3">
                        {statusIcon(tx.payment_status)}
                        <div>
                          <p className="text-white text-sm">{tx.user_id}</p>
                          <p className="text-gray-500 text-xs">{tx.package_id}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-green-400 font-medium">{tx.amount}$</p>
                        <Badge className={`
                          ${tx.payment_status === 'paid' ? 'bg-green-500/20 text-green-400' : ''}
                          ${tx.payment_status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' : ''}
                          ${tx.payment_status === 'failed' ? 'bg-red-500/20 text-red-400' : ''}
                        `}>
                          {tx.payment_status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscriptions">
          <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
            <CardHeader>
              <CardTitle className="text-white">Abonnements actifs</CardTitle>
            </CardHeader>
            <CardContent>
              {subscriptions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Aucun abonnement</p>
              ) : (
                <div className="space-y-2">
                  {subscriptions.map((sub, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white text-sm">{sub.user_id}</p>
                        <p className="text-gray-500 text-xs">
                          Depuis: {sub.upgraded_at ? new Date(sub.upgraded_at).toLocaleDateString('fr-CA') : 'N/A'}
                        </p>
                      </div>
                      <Badge className={`
                        ${sub.tier === 'free' ? 'bg-gray-600' : ''}
                        ${sub.tier === 'premium' ? 'bg-[#F5A623] text-black' : ''}
                        ${sub.tier === 'pro' ? 'bg-purple-500' : ''}
                      `}>
                        {sub.tier?.toUpperCase()}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminPayments;
