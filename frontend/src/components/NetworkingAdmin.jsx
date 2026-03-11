/**
 * NetworkingAdmin - Admin panel for networking ecosystem
 * Displays stats and allows management of referrals
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Users,
  Newspaper,
  Target,
  UsersRound,
  Gift,
  Wallet,
  TrendingUp,
  CheckCircle,
  Clock,
  RefreshCw,
  Loader2,
  DollarSign
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const NetworkingAdmin = () => {
  const [stats, setStats] = useState(null);
  const [pendingReferrals, setPendingReferrals] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [statsRes, referralsRes] = await Promise.all([
        axios.get(`${API}/networking/admin/stats`),
        axios.get(`${API}/networking/admin/pending-referrals`)
      ]);
      setStats(statsRes.data);
      setPendingReferrals(referralsRes.data.referrals || []);
    } catch (error) {
      console.error('Error loading networking admin data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleVerifyReferral = async (referralId) => {
    try {
      await axios.post(`${API}/networking/referral/${referralId}/verify`);
      toast.success('Parrainage vérifié et récompensé!');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la vérification');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="h-6 w-6 text-[#f5a623]" />
            Écosystème de Réseautage
          </h2>
          <p className="text-gray-400">Statistiques et gestion du réseau social</p>
        </div>
        <Button variant="outline" onClick={loadData}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Newspaper className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Publications</p>
                <p className="text-xl font-bold text-white">{stats?.posts?.total || 0}</p>
                <p className="text-xs text-blue-400">+{stats?.posts?.this_week || 0} cette sem.</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                <Target className="h-5 w-5 text-purple-500" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Prospects</p>
                <p className="text-xl font-bold text-white">{stats?.leads?.total || 0}</p>
                <p className="text-xs text-green-400">{stats?.leads?.converted || 0} convertis</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                <Users className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Contacts</p>
                <p className="text-xl font-bold text-white">{stats?.contacts?.total || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                <UsersRound className="h-5 w-5 text-orange-500" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Groupes</p>
                <p className="text-xl font-bold text-white">{stats?.groups?.total || 0}</p>
                <p className="text-xs text-green-400">{stats?.groups?.active || 0} actifs</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center">
                <Gift className="h-5 w-5 text-pink-500" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Parrainages</p>
                <p className="text-xl font-bold text-white">{stats?.referrals?.total || 0}</p>
                <p className="text-xs text-yellow-400">{stats?.referrals?.pending || 0} en attente</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <Wallet className="h-5 w-5 text-[#f5a623]" />
              </div>
              <div>
                <p className="text-gray-400 text-xs">Crédits en circulation</p>
                <p className="text-xl font-bold text-white">{stats?.wallets?.total_credits?.toFixed(0) || 0}</p>
                <p className="text-xs text-gray-500">{stats?.wallets?.total || 0} portefeuilles</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Referrals */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-yellow-500" />
            Parrainages en attente de validation
          </CardTitle>
          <CardDescription>
            Validez les parrainages pour distribuer les récompenses
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingReferrals.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-400">Aucun parrainage en attente</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-gray-400">Parrain</TableHead>
                  <TableHead className="text-gray-400">Filleul</TableHead>
                  <TableHead className="text-gray-400">Code</TableHead>
                  <TableHead className="text-gray-400">Action</TableHead>
                  <TableHead className="text-gray-400">Récompense</TableHead>
                  <TableHead className="text-gray-400">Date</TableHead>
                  <TableHead className="text-gray-400">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingReferrals.map((referral) => (
                  <TableRow key={referral.id}>
                    <TableCell className="text-white">{referral.referrer_id?.slice(0, 8)}...</TableCell>
                    <TableCell className="text-white">{referral.referee_id?.slice(0, 8)}...</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-mono">{referral.referral_code}</Badge>
                    </TableCell>
                    <TableCell className="text-gray-400">{referral.action_type}</TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="text-green-400">Parrain: +{referral.referrer_reward_amount} cr</span>
                        <span className="text-blue-400">Filleul: +{referral.referee_reward_amount} cr</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-gray-400">
                      {new Date(referral.created_at).toLocaleDateString('fr-CA')}
                    </TableCell>
                    <TableCell>
                      <Button 
                        size="sm" 
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => handleVerifyReferral(referral.id)}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Valider
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white">Programme de parrainage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Récompense parrain</span>
              <span className="text-[#f5a623] font-bold">10 crédits</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Récompense filleul</span>
              <span className="text-[#f5a623] font-bold">5 crédits</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Total récompensés</span>
              <span className="text-green-400 font-bold">{stats?.referrals?.rewarded || 0}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white">Économie des crédits</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Portefeuilles actifs</span>
              <span className="text-white font-bold">{stats?.wallets?.total || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Crédits en circulation</span>
              <span className="text-[#f5a623] font-bold">{stats?.wallets?.total_credits?.toFixed(0) || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Valeur estimée</span>
              <span className="text-green-400 font-bold">${((stats?.wallets?.total_credits || 0) * 0.10).toFixed(2)}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NetworkingAdmin;
