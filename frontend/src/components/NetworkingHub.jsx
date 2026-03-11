/**
 * NetworkingHub - Main networking ecosystem component
 * Includes: Feed, Leads, Contacts, Groups, Referrals, Wallet
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './GlobalAuth';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Newspaper,
  Users,
  UserPlus,
  UsersRound,
  Target,
  Gift,
  Wallet,
  Heart,
  MessageCircle,
  Share2,
  Send,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Trash2,
  Edit,
  Star,
  Phone,
  Mail,
  Building2,
  Briefcase,
  Tag,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Copy,
  ExternalLink,
  ArrowRight,
  DollarSign,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  RefreshCw,
  MapPin,
  Image as ImageIcon,
  Video,
  Link as LinkIcon
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// FEED TAB - Content Sharing
// ============================================

const FeedTab = ({ userId, userName }) => {
  const { t } = useLanguage();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewPost, setShowNewPost] = useState(false);
  const [newPost, setNewPost] = useState({ body: '', title: '', tags: '', location: '', species: '' });
  const [submitting, setSubmitting] = useState(false);

  const loadPosts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/networking/posts`);
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  const handleCreatePost = async () => {
    if (!newPost.body.trim()) {
      toast.error('Le contenu est requis');
      return;
    }
    
    setSubmitting(true);
    try {
      const tags = newPost.tags.split(',').map(t => t.trim()).filter(Boolean);
      await axios.post(`${API}/networking/posts`, null, {
        params: {
          author_id: userId,
          author_name: userName,
          body: newPost.body,
          title: newPost.title || undefined,
          tags: tags,
          location: newPost.location || undefined,
          species: newPost.species || undefined
        }
      });
      toast.success('Publication créée!');
      setShowNewPost(false);
      setNewPost({ body: '', title: '', tags: '', location: '', species: '' });
      loadPosts();
    } catch (error) {
      toast.error('Erreur lors de la création');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      const response = await axios.post(`${API}/networking/like`, null, {
        params: { user_id: userId, user_name: userName, target_type: 'post', target_id: postId }
      });
      toast.success(response.data.action === 'liked' ? t('feed_liked') || 'Aimé!' : t('feed_removed') || 'Retiré');
      loadPosts();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[var(--bionic-gold-primary)]" /></div>;
  }

  return (
    <div className="space-y-4">
      {/* New Post Button */}
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <CardContent className="p-4">
          <div className="flex gap-3">
            <Avatar>
              <AvatarFallback className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">{userName?.charAt(0) || 'U'}</AvatarFallback>
            </Avatar>
            <Button 
              variant="outline" 
              className="flex-1 justify-start text-[var(--bionic-text-secondary)] border-[var(--bionic-border-secondary)]"
              onClick={() => setShowNewPost(true)}
              data-testid="new-post-btn"
            >
              <Plus className="h-4 w-4 mr-2" />
              {t('feed_share_prompt') || 'Partagez votre expérience de chasse...'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      {posts.length === 0 ? (
        <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
          <CardContent className="py-12 text-center">
            <Newspaper className="h-12 w-12 text-[var(--bionic-gray-500)] mx-auto mb-4" />
            <p className="text-[var(--bionic-text-secondary)]">{t('feed_no_posts') || 'Aucune publication pour le moment'}</p>
            <p className="text-sm text-[var(--bionic-text-muted)]">{t('feed_be_first') || 'Soyez le premier à partager!'}</p>
          </CardContent>
        </Card>
      ) : (
        posts.map(post => (
          <Card key={post.id} className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]" data-testid={`post-${post.id}`}>
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">
                      {post.author_name?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-[var(--bionic-text-primary)]">{post.author_name}</p>
                    <p className="text-xs text-[var(--bionic-text-muted)]">
                      {new Date(post.created_at).toLocaleDateString('fr-CA')}
                      {post.location && <span className="ml-2"><MapPin className="h-3 w-3 inline" /> {post.location}</span>}
                    </p>
                  </div>
                </div>
                {post.species && (
                  <Badge variant="outline" className="border-[var(--bionic-gold-primary)] text-[var(--bionic-gold-primary)]">{post.species}</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="pb-2">
              {post.title && <h3 className="font-semibold text-[var(--bionic-text-primary)] mb-2">{post.title}</h3>}
              <p className="text-[var(--bionic-text-secondary)] whitespace-pre-wrap">{post.body}</p>
              {post.tags?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {post.tags.map((tag, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">#{tag}</Badge>
                  ))}
                </div>
              )}
            </CardContent>
            <CardFooter className="pt-2 border-t border-[var(--bionic-border-secondary)]">
              <div className="flex items-center gap-4 w-full">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-red-primary)]"
                  onClick={() => handleLike(post.id)}
                >
                  <Heart className="h-4 w-4 mr-1" />
                  {post.likes_count || 0}
                </Button>
                <Button variant="ghost" size="sm" className="text-[var(--bionic-text-secondary)]">
                  <MessageCircle className="h-4 w-4 mr-1" />
                  {post.comments_count || 0}
                </Button>
                <Button variant="ghost" size="sm" className="text-[var(--bionic-text-secondary)]">
                  <Share2 className="h-4 w-4 mr-1" />
                  {t('common_share') || 'Partager'}
                </Button>
              </div>
            </CardFooter>
          </Card>
        ))
      )}

      {/* New Post Dialog */}
      <Dialog open={showNewPost} onOpenChange={setShowNewPost}>
        <DialogContent className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-[var(--bionic-text-primary)]">{t('feed_new_post') || 'Nouvelle publication'}</DialogTitle>
            <DialogDescription>{t('feed_share_desc') || 'Partagez votre expérience avec la communauté'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('common_title')} ({t('common_optional') || 'optionnel'})</Label>
              <Input
                value={newPost.title}
                onChange={(e) => setNewPost(p => ({ ...p, title: e.target.value }))}
                placeholder={t('feed_title_placeholder') || 'Mon récit de chasse...'}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            <div>
              <Label>{t('common_content')} *</Label>
              <Textarea
                value={newPost.body}
                onChange={(e) => setNewPost(p => ({ ...p, body: e.target.value }))}
                placeholder={t('feed_content_placeholder') || 'Décrivez votre expérience...'}
                rows={5}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>{t('common_location') || 'Emplacement'}</Label>
                <Input
                  value={newPost.location}
                  onChange={(e) => setNewPost(p => ({ ...p, location: e.target.value }))}
                  placeholder={t('location_placeholder') || 'Région, Zone...'}
                  className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
                />
              </div>
              <div>
                <Label>{t('common_species') || 'Espèce'}</Label>
                <Select value={newPost.species} onValueChange={(v) => setNewPost(p => ({ ...p, species: v }))}>
                  <SelectTrigger className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]">
                    <SelectValue placeholder={t('common_select') || 'Sélectionner'} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="orignal">{t('species_moose') || 'Orignal'}</SelectItem>
                    <SelectItem value="chevreuil">{t('species_deer') || 'Chevreuil'}</SelectItem>
                    <SelectItem value="ours">{t('species_bear') || 'Ours noir'}</SelectItem>
                    <SelectItem value="dindon">{t('species_turkey') || 'Dindon'}</SelectItem>
                    <SelectItem value="petit-gibier">{t('species_small_game') || 'Petit gibier'}</SelectItem>
                    <SelectItem value="autre">{t('common_other') || 'Autre'}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>{t('common_tags') || 'Tags'} ({t('common_comma_separated') || 'séparés par virgule'})</Label>
              <Input
                value={newPost.tags}
                onChange={(e) => setNewPost(p => ({ ...p, tags: e.target.value }))}
                placeholder="chasse, orignal, laurentides..."
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewPost(false)} className="border-[var(--bionic-border-secondary)]">{t('common_cancel')}</Button>
            <Button 
              onClick={handleCreatePost}
              disabled={submitting || !newPost.body.trim()}
              className="bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-light)] text-black"
            >
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4 mr-2" />}
              {t('common_publish') || 'Publier'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============================================
// LEADS TAB - Prospect Tracking
// ============================================

const LeadsTab = ({ userId }) => {
  const { t } = useLanguage();
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showNewLead, setShowNewLead] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [filter, setFilter] = useState('all');
  const [newLead, setNewLead] = useState({
    name: '', email: '', phone: '', source: 'direct', interest_type: 'info', estimated_value: 0, tags: ''
  });

  const loadLeads = useCallback(async () => {
    try {
      const params = { owner_id: userId };
      if (filter !== 'all') params.status = filter;
      const response = await axios.get(`${API}/networking/leads`, { params });
      setLeads(response.data.leads || []);
      setStats(response.data.stats || {});
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, filter]);

  useEffect(() => {
    if (userId) loadLeads();
  }, [userId, loadLeads]);

  const handleCreateLead = async () => {
    if (!newLead.name.trim()) {
      toast.error('Le nom est requis');
      return;
    }

    try {
      const tags = newLead.tags.split(',').map(t => t.trim()).filter(Boolean);
      await axios.post(`${API}/networking/leads`, null, {
        params: { owner_id: userId, ...newLead, tags, estimated_value: parseFloat(newLead.estimated_value) || 0 }
      });
      toast.success('Prospect ajouté!');
      setShowNewLead(false);
      setNewLead({ name: '', email: '', phone: '', source: 'direct', interest_type: 'info', estimated_value: 0, tags: '' });
      loadLeads();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleUpdateStatus = async (leadId, newStatus) => {
    try {
      await axios.put(`${API}/networking/leads/${leadId}`, null, {
        params: { owner_id: userId, status: newStatus }
      });
      toast.success('Statut mis à jour!');
      loadLeads();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const statusColors = {
    new: 'bg-blue-500',
    contacted: 'bg-yellow-500',
    interested: 'bg-purple-500',
    negotiating: 'bg-orange-500',
    converted: 'bg-green-500',
    lost: 'bg-red-500'
  };

  const statusLabels = {
    new: 'Nouveau',
    contacted: 'Contacté',
    interested: 'Intéressé',
    negotiating: 'Négociation',
    converted: 'Converti',
    lost: 'Perdu'
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  return (
    <div className="space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total</p>
                <p className="text-2xl font-bold text-white">{stats.total || 0}</p>
              </div>
              <Target className="h-8 w-8 text-[#f5a623]" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Nouveaux</p>
                <p className="text-2xl font-bold text-blue-400">{stats.new || 0}</p>
              </div>
              <UserPlus className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Convertis</p>
                <p className="text-2xl font-bold text-green-400">{stats.converted || 0}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Valeur potentielle</p>
                <p className="text-2xl font-bold text-[#f5a623]">${stats.total_estimated_value?.toFixed(0) || 0}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-[#f5a623]" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-[150px] bg-gray-900 border-gray-700">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous</SelectItem>
              <SelectItem value="new">Nouveaux</SelectItem>
              <SelectItem value="contacted">Contactés</SelectItem>
              <SelectItem value="interested">Intéressés</SelectItem>
              <SelectItem value="negotiating">En négociation</SelectItem>
              <SelectItem value="converted">Convertis</SelectItem>
              <SelectItem value="lost">Perdus</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button onClick={() => setShowNewLead(true)} className="bg-[#f5a623] hover:bg-[#d4891c] text-black" data-testid="new-lead-btn">
          <Plus className="h-4 w-4 mr-2" />
          Nouveau prospect
        </Button>
      </div>

      {/* Leads List */}
      <div className="space-y-3">
        {leads.length === 0 ? (
          <Card className="bg-card border-border">
            <CardContent className="py-12 text-center">
              <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">Aucun prospect trouvé</p>
            </CardContent>
          </Card>
        ) : (
          leads.map(lead => (
            <Card 
              key={lead.id} 
              className="bg-card border-border cursor-pointer hover:border-[#f5a623]/50 transition-colors"
              onClick={() => setSelectedLead(lead)}
              data-testid={`lead-${lead.id}`}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar>
                      <AvatarFallback className="bg-gray-800">{lead.name?.charAt(0) || '?'}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-white">{lead.name}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        {lead.email && <span><Mail className="h-3 w-3 inline mr-1" />{lead.email}</span>}
                        {lead.phone && <span><Phone className="h-3 w-3 inline mr-1" />{lead.phone}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {lead.estimated_value > 0 && (
                      <Badge variant="outline" className="border-green-500 text-green-400">
                        ${lead.estimated_value}
                      </Badge>
                    )}
                    <Badge className={`${statusColors[lead.status]} text-white`}>
                      {statusLabels[lead.status]}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* New Lead Dialog */}
      <Dialog open={showNewLead} onOpenChange={setShowNewLead}>
        <DialogContent className="bg-card border-border max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white">Nouveau prospect</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nom *</Label>
              <Input
                value={newLead.name}
                onChange={(e) => setNewLead(l => ({ ...l, name: e.target.value }))}
                placeholder="Nom du prospect"
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Email</Label>
                <Input
                  type="email"
                  value={newLead.email}
                  onChange={(e) => setNewLead(l => ({ ...l, email: e.target.value }))}
                  placeholder="email@exemple.com"
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              <div>
                <Label>Téléphone</Label>
                <Input
                  value={newLead.phone}
                  onChange={(e) => setNewLead(l => ({ ...l, phone: e.target.value }))}
                  placeholder="514-555-1234"
                  className="bg-gray-900 border-gray-700"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Source</Label>
                <Select value={newLead.source} onValueChange={(v) => setNewLead(l => ({ ...l, source: v }))}>
                  <SelectTrigger className="bg-gray-900 border-gray-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="direct">Direct</SelectItem>
                    <SelectItem value="marketplace">Marketplace</SelectItem>
                    <SelectItem value="lands">Terres à louer</SelectItem>
                    <SelectItem value="referral">Parrainage</SelectItem>
                    <SelectItem value="event">Événement</SelectItem>
                    <SelectItem value="other">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Type d'intérêt</Label>
                <Select value={newLead.interest_type} onValueChange={(v) => setNewLead(l => ({ ...l, interest_type: v }))}>
                  <SelectTrigger className="bg-gray-900 border-gray-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="buy">Achat</SelectItem>
                    <SelectItem value="sell">Vente</SelectItem>
                    <SelectItem value="rent">Location</SelectItem>
                    <SelectItem value="service">Service</SelectItem>
                    <SelectItem value="info">Information</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Valeur estimée ($)</Label>
              <Input
                type="number"
                value={newLead.estimated_value}
                onChange={(e) => setNewLead(l => ({ ...l, estimated_value: e.target.value }))}
                placeholder="0"
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div>
              <Label>Tags (séparés par virgule)</Label>
              <Input
                value={newLead.tags}
                onChange={(e) => setNewLead(l => ({ ...l, tags: e.target.value }))}
                placeholder="vip, urgent, marketplace..."
                className="bg-gray-900 border-gray-700"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewLead(false)}>Annuler</Button>
            <Button onClick={handleCreateLead} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
              <Plus className="h-4 w-4 mr-2" />
              Ajouter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Lead Detail Dialog */}
      {selectedLead && (
        <Dialog open={!!selectedLead} onOpenChange={() => setSelectedLead(null)}>
          <DialogContent className="bg-card border-border max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-white flex items-center gap-2">
                {selectedLead.name}
                <Badge className={`${statusColors[selectedLead.status]} text-white`}>
                  {statusLabels[selectedLead.status]}
                </Badge>
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                {selectedLead.email && (
                  <div>
                    <p className="text-gray-400">Email</p>
                    <p className="text-white">{selectedLead.email}</p>
                  </div>
                )}
                {selectedLead.phone && (
                  <div>
                    <p className="text-gray-400">Téléphone</p>
                    <p className="text-white">{selectedLead.phone}</p>
                  </div>
                )}
                <div>
                  <p className="text-gray-400">Source</p>
                  <p className="text-white">{selectedLead.source}</p>
                </div>
                <div>
                  <p className="text-gray-400">Valeur estimée</p>
                  <p className="text-[#f5a623] font-semibold">${selectedLead.estimated_value || 0}</p>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <Label>Changer le statut</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(statusLabels).map(([key, label]) => (
                    <Button
                      key={key}
                      size="sm"
                      variant={selectedLead.status === key ? "default" : "outline"}
                      className={selectedLead.status === key ? statusColors[key] : ''}
                      onClick={() => {
                        handleUpdateStatus(selectedLead.id, key);
                        setSelectedLead(s => ({ ...s, status: key }));
                      }}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>

              {selectedLead.notes?.length > 0 && (
                <div>
                  <Label>Notes</Label>
                  <div className="mt-2 space-y-2 max-h-32 overflow-y-auto">
                    {selectedLead.notes.map((n, i) => (
                      <div key={i} className="bg-gray-900 p-2 rounded text-sm">
                        <p className="text-gray-300">{n.note}</p>
                        <p className="text-xs text-gray-500 mt-1">{new Date(n.date).toLocaleString('fr-CA')}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// ============================================
// CONTACTS TAB
// ============================================

const ContactsTab = ({ userId }) => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewContact, setShowNewContact] = useState(false);
  const [search, setSearch] = useState('');
  const [newContact, setNewContact] = useState({
    name: '', email: '', phone: '', company: '', relationship: 'other', tags: '', notes: ''
  });

  const loadContacts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/networking/contacts`, {
        params: { owner_id: userId, search: search || undefined }
      });
      setContacts(response.data.contacts || []);
    } catch (error) {
      console.error('Error loading contacts:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, search]);

  useEffect(() => {
    if (userId) loadContacts();
  }, [userId, loadContacts]);

  const handleCreateContact = async () => {
    if (!newContact.name.trim()) {
      toast.error('Le nom est requis');
      return;
    }

    try {
      const tags = newContact.tags.split(',').map(t => t.trim()).filter(Boolean);
      await axios.post(`${API}/networking/contacts`, null, {
        params: { owner_id: userId, ...newContact, tags }
      });
      toast.success('Contact ajouté!');
      setShowNewContact(false);
      setNewContact({ name: '', email: '', phone: '', company: '', relationship: 'other', tags: '', notes: '' });
      loadContacts();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const relationshipLabels = {
    friend: { icon: Users, label: t('relationship_friend') || 'Ami' },
    business: { icon: Briefcase, label: t('relationship_business') || 'Affaires' },
    family: { icon: UsersRound, label: t('relationship_family') || 'Famille' },
    hunting_partner: { icon: Target, label: t('relationship_hunting_partner') || 'Partenaire de chasse' },
    vendor: { icon: Building2, label: t('relationship_vendor') || 'Vendeur' },
    customer: { icon: DollarSign, label: t('relationship_customer') || 'Client' },
    other: { icon: Tag, label: t('common_other') || 'Autre' }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  return (
    <div className="space-y-4">
      {/* Search & Add */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un contact..."
            className="pl-10 bg-gray-900 border-gray-700"
          />
        </div>
        <Button onClick={() => setShowNewContact(true)} className="bg-[#f5a623] hover:bg-[#d4891c] text-black" data-testid="new-contact-btn">
          <UserPlus className="h-4 w-4 mr-2" />
          Ajouter
        </Button>
      </div>

      {/* Contacts Grid */}
      {contacts.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="py-12 text-center">
            <Users className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Aucun contact trouvé</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map(contact => (
            <Card key={contact.id} className="bg-card border-border" data-testid={`contact-${contact.id}`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarFallback className="bg-[#f5a623]/20 text-[#f5a623]">
                      {contact.name?.charAt(0) || '?'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-white truncate">{contact.name}</p>
                      {contact.is_favorite && <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />}
                    </div>
                    <p className="text-sm text-gray-400">{relationshipLabels[contact.relationship]}</p>
                    {contact.company && (
                      <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                        <Building2 className="h-3 w-3" />
                        {contact.company}
                      </p>
                    )}
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  {contact.email && (
                    <Button size="sm" variant="ghost" className="text-gray-400 hover:text-[#f5a623]">
                      <Mail className="h-4 w-4" />
                    </Button>
                  )}
                  {contact.phone && (
                    <Button size="sm" variant="ghost" className="text-gray-400 hover:text-[#f5a623]">
                      <Phone className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* New Contact Dialog */}
      <Dialog open={showNewContact} onOpenChange={setShowNewContact}>
        <DialogContent className="bg-card border-border max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white">Nouveau contact</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Nom *</Label>
              <Input
                value={newContact.name}
                onChange={(e) => setNewContact(c => ({ ...c, name: e.target.value }))}
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Email</Label>
                <Input
                  type="email"
                  value={newContact.email}
                  onChange={(e) => setNewContact(c => ({ ...c, email: e.target.value }))}
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              <div>
                <Label>Téléphone</Label>
                <Input
                  value={newContact.phone}
                  onChange={(e) => setNewContact(c => ({ ...c, phone: e.target.value }))}
                  className="bg-gray-900 border-gray-700"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Entreprise</Label>
                <Input
                  value={newContact.company}
                  onChange={(e) => setNewContact(c => ({ ...c, company: e.target.value }))}
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              <div>
                <Label>Relation</Label>
                <Select value={newContact.relationship} onValueChange={(v) => setNewContact(c => ({ ...c, relationship: v }))}>
                  <SelectTrigger className="bg-gray-900 border-gray-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="friend">Ami</SelectItem>
                    <SelectItem value="business">Affaires</SelectItem>
                    <SelectItem value="family">Famille</SelectItem>
                    <SelectItem value="hunting_partner">Partenaire de chasse</SelectItem>
                    <SelectItem value="vendor">Vendeur</SelectItem>
                    <SelectItem value="customer">Client</SelectItem>
                    <SelectItem value="other">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Notes</Label>
              <Textarea
                value={newContact.notes}
                onChange={(e) => setNewContact(c => ({ ...c, notes: e.target.value }))}
                rows={2}
                className="bg-gray-900 border-gray-700"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewContact(false)}>Annuler</Button>
            <Button onClick={handleCreateContact} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
              <UserPlus className="h-4 w-4 mr-2" />
              Ajouter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============================================
// GROUPS TAB
// ============================================

const GroupsTab = ({ userId, userName }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewGroup, setShowNewGroup] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', description: '', group_type: 'custom', privacy: 'private' });

  const loadGroups = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/networking/groups`, { params: { user_id: userId } });
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Error loading groups:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) loadGroups();
  }, [userId, loadGroups]);

  const handleCreateGroup = async () => {
    if (!newGroup.name.trim()) {
      toast.error('Le nom est requis');
      return;
    }

    try {
      await axios.post(`${API}/networking/groups`, null, {
        params: { owner_id: userId, owner_name: userName, ...newGroup }
      });
      toast.success('Groupe créé!');
      setShowNewGroup(false);
      setNewGroup({ name: '', description: '', group_type: 'custom', privacy: 'private' });
      loadGroups();
    } catch (error) {
      toast.error('Erreur lors de la création');
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await axios.post(`${API}/networking/groups/${groupId}/join`, null, {
        params: { user_id: userId, user_name: userName }
      });
      toast.success('Vous avez rejoint le groupe!');
      loadGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur');
    }
  };

  const groupTypeIcons = {
    hunting_club: Target,
    family: UsersRound,
    business: Building2,
    friends: Users,
    custom: Tag
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[var(--bionic-gold-primary)]" /></div>;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-[var(--bionic-text-secondary)]">{groups.length} {t('common_groups') || 'groupe(s)'}</p>
        <Button onClick={() => setShowNewGroup(true)} className="bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-light)] text-black" data-testid="new-group-btn">
          <Plus className="h-4 w-4 mr-2" />
          {t('network_create_group') || 'Créer un groupe'}
        </Button>
      </div>

      {/* Groups List */}
      {groups.length === 0 ? (
        <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
          <CardContent className="py-12 text-center">
            <UsersRound className="h-12 w-12 text-[var(--bionic-gray-500)] mx-auto mb-4" />
            <p className="text-[var(--bionic-text-secondary)]">{t('network_no_groups') || 'Aucun groupe'}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {groups.map(group => {
            const GroupIcon = groupTypeIcons[group.group_type] || Tag;
            return (
            <Card key={group.id} className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]" data-testid={`group-${group.id}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-[var(--bionic-gold-muted)] flex items-center justify-center">
                      <GroupIcon className="h-6 w-6 text-[var(--bionic-gold-primary)]" />
                    </div>
                    <div>
                      <p className="font-medium text-[var(--bionic-text-primary)]">{group.name}</p>
                      <p className="text-sm text-[var(--bionic-text-secondary)]">{group.member_count} {t('common_members') || 'membre(s)'}</p>
                    </div>
                  </div>
                  <Badge variant={group.privacy === 'public' ? 'default' : 'outline'}>
                    {group.privacy === 'public' ? t('common_public') || 'Public' : group.privacy === 'private' ? t('common_private') || 'Privé' : t('common_invite_only') || 'Sur invitation'}
                  </Badge>
                </div>
                {group.description && (
                  <p className="text-sm text-[var(--bionic-text-secondary)] mt-3 line-clamp-2">{group.description}</p>
                )}
                <div className="mt-4 flex gap-2">
                  {group.member_ids?.includes(userId) ? (
                    <Button size="sm" variant="outline" className="flex-1 border-[var(--bionic-border-secondary)]">
                      <CheckCircle className="h-4 w-4 mr-1 text-[var(--bionic-green-primary)]" />
                      {t('common_member') || 'Membre'}
                    </Button>
                  ) : (
                    <Button 
                      size="sm" 
                      className="flex-1 bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-light)] text-black"
                      onClick={() => handleJoinGroup(group.id)}
                    >
                      <UserPlus className="h-4 w-4 mr-1" />
                      {t('network_join') || 'Rejoindre'}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
            );
          })}
        </div>
      )}

      {/* New Group Dialog */}
      <Dialog open={showNewGroup} onOpenChange={setShowNewGroup}>
        <DialogContent className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-[var(--bionic-text-primary)]">{t('network_create_group') || 'Créer un groupe'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('common_group_name') || 'Nom du groupe'} *</Label>
              <Input
                value={newGroup.name}
                onChange={(e) => setNewGroup(g => ({ ...g, name: e.target.value }))}
                placeholder={t('group_name_placeholder') || 'Club de chasse des Laurentides'}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            <div>
              <Label>{t('common_description') || 'Description'}</Label>
              <Textarea
                value={newGroup.description}
                onChange={(e) => setNewGroup(g => ({ ...g, description: e.target.value }))}
                placeholder={t('group_desc_placeholder') || 'Décrivez votre groupe...'}
                rows={3}
                className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>{t('common_type') || 'Type'}</Label>
                <Select value={newGroup.group_type} onValueChange={(v) => setNewGroup(g => ({ ...g, group_type: v }))}>
                  <SelectTrigger className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hunting_club"><Target className="h-4 w-4 inline mr-2" />{t('group_type_hunting_club') || 'Club de chasse'}</SelectItem>
                    <SelectItem value="family"><UsersRound className="h-4 w-4 inline mr-2" />{t('group_type_family') || 'Famille'}</SelectItem>
                    <SelectItem value="business"><Building2 className="h-4 w-4 inline mr-2" />{t('group_type_business') || 'Affaires'}</SelectItem>
                    <SelectItem value="friends"><Users className="h-4 w-4 inline mr-2" />{t('group_type_friends') || 'Amis'}</SelectItem>
                    <SelectItem value="custom"><Tag className="h-4 w-4 inline mr-2" />{t('group_type_custom') || 'Personnalisé'}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>{t('common_privacy') || 'Confidentialité'}</Label>
                <Select value={newGroup.privacy} onValueChange={(v) => setNewGroup(g => ({ ...g, privacy: v }))}>
                  <SelectTrigger className="bg-[var(--bionic-bg-primary)] border-[var(--bionic-border-secondary)]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="public">Public</SelectItem>
                    <SelectItem value="private">Privé</SelectItem>
                    <SelectItem value="invite_only">Sur invitation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewGroup(false)}>Annuler</Button>
            <Button onClick={handleCreateGroup} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
              <Plus className="h-4 w-4 mr-2" />
              Créer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============================================
// REFERRAL TAB
// ============================================

const ReferralTab = ({ userId }) => {
  const [codeData, setCodeData] = useState(null);
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadReferralData = useCallback(async () => {
    try {
      const [codeRes, referralsRes] = await Promise.all([
        axios.get(`${API}/networking/referral/code/${userId}`),
        axios.get(`${API}/networking/referrals/${userId}`)
      ]);
      setCodeData(codeRes.data);
      setReferrals(referralsRes.data.referrals || []);
    } catch (error) {
      console.error('Error loading referral data:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) loadReferralData();
  }, [userId, loadReferralData]);

  const copyCode = () => {
    if (codeData?.code?.code) {
      navigator.clipboard.writeText(codeData.code.code);
      toast.success('Code copié!');
    }
  };

  const copyLink = () => {
    const link = `${window.location.origin}?ref=${codeData?.code?.code}`;
    navigator.clipboard.writeText(link);
    toast.success('Lien copié!');
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" /></div>;
  }

  const stats = codeData?.stats || {};

  return (
    <div className="space-y-6">
      {/* Referral Code Card */}
      <Card className="bg-gradient-to-r from-[#f5a623]/20 to-transparent border-[#f5a623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Gift className="h-8 w-8 text-[#f5a623]" />
              <div>
                <h3 className="text-xl font-bold text-white">Votre code de parrainage</h3>
                <p className="text-gray-400">Partagez et gagnez des récompenses</p>
              </div>
            </div>
          </div>
          
          <div className="bg-black/50 rounded-lg p-4 flex items-center justify-between">
            <span className="text-3xl font-mono font-bold text-[#f5a623]">{codeData?.code?.code || '...'}</span>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={copyCode}>
                <Copy className="h-4 w-4 mr-1" />
                Copier
              </Button>
              <Button size="sm" className="bg-[#f5a623] hover:bg-[#d4891c] text-black" onClick={copyLink}>
                <Share2 className="h-4 w-4 mr-1" />
                Partager
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{stats.total_referrals || 0}</p>
              <p className="text-sm text-gray-400">Parrainages</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-400">{stats.pending || 0}</p>
              <p className="text-sm text-gray-400">En attente</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">{stats.rewarded || 0}</p>
              <p className="text-sm text-gray-400">Récompensés</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#f5a623]">{stats.total_earned || 0} cr</p>
              <p className="text-sm text-gray-400">Crédits gagnés</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rewards Info */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white">Comment ça fonctionne?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#f5a623]/20 flex items-center justify-center text-[#f5a623] font-bold">1</div>
              <div>
                <p className="font-medium text-white">Partagez votre code</p>
                <p className="text-sm text-gray-400">Envoyez votre code à vos amis chasseurs</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#f5a623]/20 flex items-center justify-center text-[#f5a623] font-bold">2</div>
              <div>
                <p className="font-medium text-white">Ils s'inscrivent</p>
                <p className="text-sm text-gray-400">Ils utilisent votre code lors de leur inscription</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#f5a623]/20 flex items-center justify-center text-[#f5a623] font-bold">3</div>
              <div>
                <p className="font-medium text-white">Gagnez des récompenses</p>
                <p className="text-sm text-gray-400">
                  Vous recevez <span className="text-[#f5a623]">{codeData?.code?.referrer_reward || 10} crédits</span>, 
                  ils reçoivent <span className="text-[#f5a623]">{codeData?.code?.referee_reward || 5} crédits</span>
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Referrals List */}
      {referrals.length > 0 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white">Historique des parrainages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {referrals.map(ref => (
                <div key={ref.id} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-gray-800">?</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-white">Utilisateur parrainé</p>
                      <p className="text-xs text-gray-400">{new Date(ref.created_at).toLocaleDateString('fr-CA')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={ref.status === 'rewarded' ? 'default' : 'outline'} className={ref.status === 'rewarded' ? 'bg-green-500' : ''}>
                      {ref.status === 'pending' ? 'En attente' : ref.status === 'verified' ? 'Vérifié' : 'Récompensé'}
                    </Badge>
                    {ref.status === 'rewarded' && (
                      <span className="text-[#f5a623] font-semibold">+{ref.referrer_reward_amount} cr</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ============================================
// WALLET TAB
// ============================================

const WalletTab = ({ userId }) => {
  const { t } = useLanguage();
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadWalletData = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/networking/wallet/${userId}`);
      setWallet(response.data.wallet);
      setTransactions(response.data.recent_transactions || []);
    } catch (error) {
      console.error('Error loading wallet:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) loadWalletData();
  }, [userId, loadWalletData]);

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-[var(--bionic-gold-primary)]" /></div>;
  }

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <Card className="bg-gradient-to-br from-[var(--bionic-gold-primary)]/30 via-[var(--bionic-gold-primary)]/10 to-transparent border-[var(--bionic-gold-primary)]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-[var(--bionic-gold-muted)] flex items-center justify-center">
                <Wallet className="h-6 w-6 text-[var(--bionic-gold-primary)]" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[var(--bionic-text-primary)]">{t('wallet_title') || 'Mon Portefeuille'}</h3>
                <p className="text-sm text-[var(--bionic-text-secondary)]">{t('wallet_credits_rewards') || 'Crédits & Récompenses'}</p>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={loadWalletData} className="border-[var(--bionic-border-secondary)]">
              <RefreshCw className="h-4 w-4 mr-1" />
              {t('common_refresh')}
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-black/40 rounded-xl p-4">
              <p className="text-sm text-[var(--bionic-text-secondary)] mb-1">{t('wallet_available_credits') || 'Crédits disponibles'}</p>
              <p className="text-3xl font-bold text-[var(--bionic-gold-primary)]">{wallet?.balance_credits?.toFixed(0) || 0}</p>
              <p className="text-xs text-[var(--bionic-text-muted)]">{t('common_credits') || 'crédits'}</p>
            </div>
            <div className="bg-black/40 rounded-xl p-4">
              <p className="text-sm text-[var(--bionic-text-secondary)] mb-1">{t('wallet_balance_cad') || 'Solde CAD'}</p>
              <p className="text-3xl font-bold text-[var(--bionic-green-primary)]">${wallet?.balance_cad?.toFixed(2) || '0.00'}</p>
              <p className="text-xs text-[var(--bionic-text-muted)]">{t('common_cad_dollars') || 'dollars canadiens'}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4 text-center">
            <div>
              <p className="text-lg font-semibold text-[var(--bionic-text-primary)]">{wallet?.total_earned?.toFixed(0) || 0}</p>
              <p className="text-xs text-[var(--bionic-text-secondary)]">{t('wallet_total_earned') || 'Total gagné'}</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-white">{wallet?.total_spent?.toFixed(0) || 0}</p>
              <p className="text-xs text-gray-400">Total dépensé</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-yellow-400">{wallet?.pending_balance?.toFixed(0) || 0}</p>
              <p className="text-xs text-gray-400">En attente</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Button variant="outline" className="h-auto py-4 flex-col gap-2">
          <ArrowUpRight className="h-5 w-5 text-green-400" />
          <span>Ajouter des fonds</span>
        </Button>
        <Button variant="outline" className="h-auto py-4 flex-col gap-2">
          <ArrowDownRight className="h-5 w-5 text-red-400" />
          <span>Retirer</span>
        </Button>
        <Button variant="outline" className="h-auto py-4 flex-col gap-2">
          <Send className="h-5 w-5 text-blue-400" />
          <span>Transférer</span>
        </Button>
        <Button variant="outline" className="h-auto py-4 flex-col gap-2">
          <CreditCard className="h-5 w-5 text-purple-400" />
          <span>Acheter crédits</span>
        </Button>
      </div>

      {/* Transactions */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white">Transactions récentes</CardTitle>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 ? (
            <p className="text-center text-gray-400 py-8">Aucune transaction</p>
          ) : (
            <div className="space-y-3">
              {transactions.map(tx => (
                <div key={tx.id} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      tx.amount > 0 ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}>
                      {tx.amount > 0 ? (
                        <ArrowDownRight className="h-5 w-5 text-green-400" />
                      ) : (
                        <ArrowUpRight className="h-5 w-5 text-red-400" />
                      )}
                    </div>
                    <div>
                      <p className="text-white text-sm">{tx.description}</p>
                      <p className="text-xs text-gray-500">{new Date(tx.created_at).toLocaleDateString('fr-CA')}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount} {tx.currency === 'CAD' ? '$' : 'cr'}
                    </p>
                    <p className="text-xs text-gray-500">Solde: {tx.balance_after}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// MAIN NETWORKING HUB COMPONENT
// ============================================

const NetworkingHub = () => {
  const { user, isAuthenticated, openLoginModal } = useAuth();
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('feed');

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background pt-20">
        <div className="max-w-4xl mx-auto px-4 py-16">
          <Card className="bg-card border-border">
            <CardContent className="py-16 text-center">
              <Users className="h-16 w-16 text-gray-600 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-white mb-4">{t('network_login_required')}</h2>
              <p className="text-gray-400 mb-8 max-w-md mx-auto">
                {t('network_login_desc')}
              </p>
              <Button 
                onClick={openLoginModal}
                className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
                data-testid="login-prompt-btn"
              >
                {t('auth_login')}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pt-20" data-testid="networking-hub">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">{t('network_title')}</h1>
          <p className="text-gray-400">{t('network_subtitle')}</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-card border border-border p-1 h-auto flex-wrap">
            <TabsTrigger value="feed" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Newspaper className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_feed')}</span>
            </TabsTrigger>
            <TabsTrigger value="leads" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Target className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_prospects')}</span>
            </TabsTrigger>
            <TabsTrigger value="contacts" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_contacts')}</span>
            </TabsTrigger>
            <TabsTrigger value="groups" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <UsersRound className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_groups')}</span>
            </TabsTrigger>
            <TabsTrigger value="referral" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Gift className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_referral')}</span>
            </TabsTrigger>
            <TabsTrigger value="wallet" className="gap-2 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
              <Wallet className="h-4 w-4" />
              <span className="hidden sm:inline">{t('network_wallet')}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="feed">
            <FeedTab userId={user?.id} userName={user?.name} />
          </TabsContent>
          
          <TabsContent value="leads">
            <LeadsTab userId={user?.id} />
          </TabsContent>
          
          <TabsContent value="contacts">
            <ContactsTab userId={user?.id} />
          </TabsContent>
          
          <TabsContent value="groups">
            <GroupsTab userId={user?.id} userName={user?.name} />
          </TabsContent>
          
          <TabsContent value="referral">
            <ReferralTab userId={user?.id} />
          </TabsContent>
          
          <TabsContent value="wallet">
            <WalletTab userId={user?.id} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default NetworkingHub;
