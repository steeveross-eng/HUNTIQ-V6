/**
 * AdminNetworking - Administration du réseau social
 * ==================================================
 * 
 * Module V5-ULTIME - Phase 4 Migration
 * Gestion des publications, groupes, leads, parrainages et wallets.
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
  Users,
  Newspaper,
  Target,
  UsersRound,
  Gift,
  Wallet,
  RefreshCw,
  Loader2,
  Star,
  StarOff,
  Pin,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  MessageSquare,
  Heart,
  DollarSign
} from 'lucide-react';
import { toast } from 'sonner';
import AdminService from '../AdminService';

const AdminNetworking = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [posts, setPosts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [leads, setLeads] = useState([]);
  const [referrals, setReferrals] = useState([]);
  const [pendingReferrals, setPendingReferrals] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [referralCodes, setReferralCodes] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [
        statsRes,
        postsRes,
        groupsRes,
        leadsRes,
        referralsRes,
        pendingRes,
        walletsRes,
        codesRes
      ] = await Promise.all([
        AdminService.networkingGetStats(),
        AdminService.networkingGetPosts(),
        AdminService.networkingGetGroups(),
        AdminService.networkingGetLeads(),
        AdminService.networkingGetReferrals(),
        AdminService.networkingGetPendingReferrals(),
        AdminService.networkingGetWallets(),
        AdminService.networkingGetReferralCodes()
      ]);
      
      if (statsRes.success) setStats(statsRes.stats);
      if (postsRes.success) setPosts(postsRes.posts || []);
      if (groupsRes.success) setGroups(groupsRes.groups || []);
      if (leadsRes.success) setLeads(leadsRes.leads || []);
      if (referralsRes.success) setReferrals(referralsRes.referrals || []);
      if (pendingRes.success) setPendingReferrals(pendingRes.referrals || []);
      if (walletsRes.success) setWallets(walletsRes.wallets || []);
      if (codesRes.success) setReferralCodes(codesRes.codes || []);
    } catch (error) {
      console.error('Error loading networking data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTogglePostFeatured = async (postId, currentState) => {
    try {
      const result = await AdminService.networkingTogglePostFeatured(postId, !currentState);
      if (result.success) {
        toast.success(result.is_featured ? 'Publication mise en vedette' : 'Mise en vedette retirée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleTogglePostPinned = async (postId, currentState) => {
    try {
      const result = await AdminService.networkingTogglePostPinned(postId, !currentState);
      if (result.success) {
        toast.success(result.is_pinned ? 'Publication épinglée' : 'Épingle retirée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Supprimer cette publication ?')) return;
    try {
      const result = await AdminService.networkingDeletePost(postId);
      if (result.success) {
        toast.success('Publication supprimée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleVerifyReferral = async (referralId) => {
    try {
      const result = await AdminService.networkingVerifyReferral(referralId);
      if (result.success) {
        toast.success('Parrainage vérifié et récompensé!');
        loadData();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la vérification');
    }
  };

  const handleRejectReferral = async (referralId) => {
    try {
      const result = await AdminService.networkingRejectReferral(referralId);
      if (result.success) {
        toast.success('Parrainage rejeté');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors du rejet');
    }
  };

  const handleToggleGroupActive = async (groupId, currentState) => {
    try {
      const result = await AdminService.networkingToggleGroupActive(groupId, !currentState);
      if (result.success) {
        toast.success(result.is_active ? 'Groupe activé' : 'Groupe désactivé');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      new: 'bg-blue-500/20 text-blue-400',
      contacted: 'bg-yellow-500/20 text-yellow-400',
      interested: 'bg-purple-500/20 text-purple-400',
      negotiating: 'bg-orange-500/20 text-orange-400',
      converted: 'bg-green-500/20 text-green-400',
      lost: 'bg-red-500/20 text-red-400',
      pending: 'bg-yellow-500/20 text-yellow-400',
      rewarded: 'bg-green-500/20 text-green-400',
      expired: 'bg-gray-500/20 text-gray-400'
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
    <div data-testid="admin-networking" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="h-6 w-6 text-[#f5a623]" />
            Écosystème de Réseautage
          </h2>
          <p className="text-gray-400">Gestion du réseau social et des programmes de fidélité</p>
        </div>
        <Button variant="outline" onClick={loadData} data-testid="refresh-networking">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[#0a0a15]">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="posts">Publications</TabsTrigger>
          <TabsTrigger value="groups">Groupes</TabsTrigger>
          <TabsTrigger value="leads">Leads</TabsTrigger>
          <TabsTrigger value="referrals">Parrainages</TabsTrigger>
          <TabsTrigger value="wallets">Portefeuilles</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {stats && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <Newspaper className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Publications</p>
                        <p className="text-xl font-bold text-white">{stats.posts?.total || 0}</p>
                        <p className="text-xs text-blue-400">+{stats.posts?.this_week || 0} cette sem.</p>
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
                        <p className="text-gray-400 text-xs">Leads</p>
                        <p className="text-xl font-bold text-white">{stats.leads?.total || 0}</p>
                        <p className="text-xs text-green-400">{stats.leads?.converted || 0} convertis</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <UsersRound className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Groupes</p>
                        <p className="text-xl font-bold text-white">{stats.groups?.total || 0}</p>
                        <p className="text-xs text-green-400">{stats.groups?.active || 0} actifs</p>
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
                        <p className="text-xl font-bold text-white">{stats.referrals?.total || 0}</p>
                        <p className="text-xs text-yellow-400">{stats.referrals?.pending || 0} en attente</p>
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
                        <p className="text-gray-400 text-xs">Crédits</p>
                        <p className="text-xl font-bold text-white">{stats.wallets?.total_credits?.toFixed(0) || 0}</p>
                        <p className="text-xs text-gray-500">{stats.wallets?.total || 0} wallets</p>
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
                        <p className="text-xl font-bold text-white">{stats.contacts?.total || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Pending Referrals Alert */}
              {pendingReferrals.length > 0 && (
                <Card className="bg-yellow-500/10 border-yellow-500/30">
                  <CardHeader>
                    <CardTitle className="text-yellow-400 flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      {pendingReferrals.length} parrainage(s) en attente de validation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Button 
                      variant="outline" 
                      className="border-yellow-500/50 text-yellow-400"
                      onClick={() => setActiveTab('referrals')}
                    >
                      Voir les parrainages
                    </Button>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>

        {/* Posts Tab */}
        <TabsContent value="posts">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Publications</CardTitle>
              <CardDescription>Gérer les publications du réseau social</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Auteur</TableHead>
                    <TableHead className="text-gray-400">Contenu</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Likes</TableHead>
                    <TableHead className="text-gray-400">Commentaires</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {posts.slice(0, 20).map((post) => (
                    <TableRow key={post.id}>
                      <TableCell className="text-white font-medium">{post.author_name}</TableCell>
                      <TableCell className="text-gray-400 max-w-xs truncate">{post.body?.slice(0, 50)}...</TableCell>
                      <TableCell>
                        <Badge className="bg-blue-500/20 text-blue-400">{post.content_type}</Badge>
                      </TableCell>
                      <TableCell className="text-white">
                        <span className="flex items-center gap-1">
                          <Heart className="h-3 w-3 text-red-400" />
                          {post.likes_count || 0}
                        </span>
                      </TableCell>
                      <TableCell className="text-white">
                        <span className="flex items-center gap-1">
                          <MessageSquare className="h-3 w-3 text-blue-400" />
                          {post.comments_count || 0}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleTogglePostFeatured(post.id, post.is_featured)}
                            title={post.is_featured ? 'Retirer vedette' : 'Mettre en vedette'}
                          >
                            {post.is_featured ? <Star className="h-4 w-4 text-yellow-500 fill-current" /> : <StarOff className="h-4 w-4" />}
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleTogglePostPinned(post.id, post.is_pinned)}
                            title={post.is_pinned ? 'Désépingler' : 'Épingler'}
                          >
                            <Pin className={`h-4 w-4 ${post.is_pinned ? 'text-blue-400' : ''}`} />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-400"
                            onClick={() => handleDeletePost(post.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {posts.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune publication trouvée</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Groups Tab */}
        <TabsContent value="groups">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Groupes</CardTitle>
              <CardDescription>Gérer les communautés et groupes</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Confidentialité</TableHead>
                    <TableHead className="text-gray-400">Membres</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {groups.slice(0, 20).map((group) => (
                    <TableRow key={group.id}>
                      <TableCell className="text-white font-medium">{group.name}</TableCell>
                      <TableCell className="text-gray-400">{group.group_type}</TableCell>
                      <TableCell>
                        <Badge className={
                          group.privacy === 'public' ? 'bg-green-500/20 text-green-400' :
                          group.privacy === 'private' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }>
                          {group.privacy}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white">{group.member_count || 0}</TableCell>
                      <TableCell>
                        {group.is_active ? (
                          <Badge className="bg-green-500/20 text-green-400">Actif</Badge>
                        ) : (
                          <Badge className="bg-red-500/20 text-red-400">Inactif</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleToggleGroupActive(group.id, group.is_active)}
                        >
                          {group.is_active ? <XCircle className="h-4 w-4 text-red-400" /> : <CheckCircle className="h-4 w-4 text-green-400" />}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {groups.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun groupe trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Leads Tab */}
        <TabsContent value="leads">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Leads / Prospects</CardTitle>
              <CardDescription>Suivi des prospects et opportunités</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Source</TableHead>
                    <TableHead className="text-gray-400">Intérêt</TableHead>
                    <TableHead className="text-gray-400">Valeur estimée</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leads.slice(0, 20).map((lead) => (
                    <TableRow key={lead.id}>
                      <TableCell className="text-white font-medium">{lead.name}</TableCell>
                      <TableCell className="text-gray-400">{lead.source}</TableCell>
                      <TableCell className="text-gray-400">{lead.interest_type}</TableCell>
                      <TableCell className="text-[#f5a623]">${lead.estimated_value || 0}</TableCell>
                      <TableCell>{getStatusBadge(lead.status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {leads.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun lead trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Referrals Tab */}
        <TabsContent value="referrals" className="space-y-6">
          {/* Pending Referrals */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-yellow-500" />
                Parrainages en attente de validation
              </CardTitle>
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
                      <TableHead className="text-gray-400">Récompenses</TableHead>
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
                        <TableCell>
                          <div className="flex flex-col text-xs">
                            <span className="text-green-400">Parrain: +{referral.referrer_reward_amount} cr</span>
                            <span className="text-blue-400">Filleul: +{referral.referee_reward_amount} cr</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {new Date(referral.created_at).toLocaleDateString('fr-CA')}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button 
                              size="sm" 
                              className="bg-green-600 hover:bg-green-700"
                              onClick={() => handleVerifyReferral(referral.id)}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Valider
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleRejectReferral(referral.id)}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Rejeter
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* All Referrals */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Historique des parrainages</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Parrain</TableHead>
                    <TableHead className="text-gray-400">Filleul</TableHead>
                    <TableHead className="text-gray-400">Code</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {referrals.slice(0, 20).map((referral) => (
                    <TableRow key={referral.id}>
                      <TableCell className="text-white">{referral.referrer_id?.slice(0, 8)}...</TableCell>
                      <TableCell className="text-white">{referral.referee_id?.slice(0, 8)}...</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono">{referral.referral_code}</Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(referral.status)}</TableCell>
                      <TableCell className="text-gray-400">
                        {new Date(referral.created_at).toLocaleDateString('fr-CA')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {referrals.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun parrainage trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Wallets Tab */}
        <TabsContent value="wallets">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Wallet className="h-5 w-5 text-[#f5a623]" />
                Portefeuilles virtuels
              </CardTitle>
              <CardDescription>Gestion des crédits et soldes utilisateurs</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Utilisateur</TableHead>
                    <TableHead className="text-gray-400">Solde crédits</TableHead>
                    <TableHead className="text-gray-400">Total gagné</TableHead>
                    <TableHead className="text-gray-400">Total dépensé</TableHead>
                    <TableHead className="text-gray-400">Créé le</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {wallets.slice(0, 20).map((wallet) => (
                    <TableRow key={wallet.id}>
                      <TableCell className="text-white font-medium">{wallet.user_id?.slice(0, 12)}...</TableCell>
                      <TableCell className="text-[#f5a623] font-bold">{wallet.balance_credits?.toFixed(2) || 0} cr</TableCell>
                      <TableCell className="text-green-400">{wallet.total_earned?.toFixed(2) || 0} cr</TableCell>
                      <TableCell className="text-red-400">{wallet.total_spent?.toFixed(2) || 0} cr</TableCell>
                      <TableCell className="text-gray-400">
                        {wallet.created_at ? new Date(wallet.created_at).toLocaleDateString('fr-CA') : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {wallets.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun portefeuille trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminNetworking;
