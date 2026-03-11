/**
 * AdminMarketing - Administration du marketing et réseaux sociaux
 * ===============================================================
 * 
 * Module V5-ULTIME - Phase 5 Migration
 * Gestion des campagnes, génération IA, publications et automations.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sparkles,
  Target,
  Calendar,
  Send,
  Copy,
  RefreshCw,
  Loader2,
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  CheckCircle,
  Clock,
  Play,
  Pause,
  Trash2,
  Eye,
  PlusCircle,
  TrendingUp,
  Users,
  Zap,
  BarChart3,
  MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';
import AdminService from '../AdminService';

const CONTENT_TYPES = [
  { id: 'product_promo', name: 'Promotion Produit', icon: Target },
  { id: 'educational', name: 'Contenu Éducatif', icon: MessageSquare },
  { id: 'seasonal', name: 'Publication Saisonnière', icon: Calendar },
  { id: 'testimonial', name: 'Témoignage Client', icon: Users },
  { id: 'tip', name: 'Conseil Expert', icon: Sparkles },
  { id: 'engagement', name: 'Question/Engagement', icon: TrendingUp }
];

const PLATFORMS = [
  { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'text-blue-500' },
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'text-pink-500' },
  { id: 'twitter', name: 'Twitter/X', icon: Twitter, color: 'text-sky-400' },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: 'text-blue-600' }
];

const AdminMarketing = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [posts, setPosts] = useState([]);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [segments, setSegments] = useState([]);
  const [automations, setAutomations] = useState([]);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Generation states
  const [generating, setGenerating] = useState(false);
  const [contentType, setContentType] = useState('product_promo');
  const [targetPlatform, setTargetPlatform] = useState('facebook');
  const [productName, setProductName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [tone, setTone] = useState('professional');
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedHashtags, setGeneratedHashtags] = useState([]);
  
  // Schedule dialog
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [
        statsRes,
        campaignsRes,
        postsRes,
        scheduledRes,
        segmentsRes,
        automationsRes,
        historyRes
      ] = await Promise.all([
        AdminService.marketingGetDashboard(),
        AdminService.marketingGetCampaigns(),
        AdminService.marketingGetPosts(),
        AdminService.marketingGetScheduledPosts(),
        AdminService.marketingGetSegments(),
        AdminService.marketingGetAutomations(),
        AdminService.marketingGetHistory()
      ]);
      
      if (statsRes.success) setStats(statsRes.stats);
      if (campaignsRes.success) setCampaigns(campaignsRes.campaigns || []);
      if (postsRes.success) setPosts(postsRes.posts || []);
      if (scheduledRes.success) setScheduledPosts(scheduledRes.posts || []);
      if (segmentsRes.success) setSegments(segmentsRes.segments || []);
      if (automationsRes.success) setAutomations(automationsRes.automations || []);
      if (historyRes.success) setHistory(historyRes.history || []);
    } catch (error) {
      console.error('Error loading marketing data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleGenerateContent = async () => {
    if (!contentType) {
      toast.error('Sélectionnez un type de contenu');
      return;
    }
    
    setGenerating(true);
    try {
      const result = await AdminService.marketingGenerateContent({
        content_type: contentType,
        platform: targetPlatform,
        product_name: productName || null,
        keywords: keywords ? keywords.split(',').map(k => k.trim()) : [],
        tone: tone,
        brand_name: 'BIONIC HUNT/Chasse'
      });
      
      if (result.success) {
        setGeneratedContent(result.content);
        setGeneratedHashtags(result.hashtags || []);
        toast.success('Contenu généré avec succès!');
      }
    } catch (error) {
      toast.error('Erreur lors de la génération');
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyContent = () => {
    const fullContent = generatedContent + '\n\n' + generatedHashtags.map(h => `#${h}`).join(' ');
    navigator.clipboard.writeText(fullContent);
    toast.success('Contenu copié!');
  };

  const handlePublishNow = async () => {
    if (!generatedContent) {
      toast.error('Générez du contenu d\'abord');
      return;
    }
    
    try {
      const createResult = await AdminService.marketingCreatePost({
        content: generatedContent,
        hashtags: generatedHashtags,
        platform: targetPlatform,
        content_type: contentType,
        status: 'draft'
      });
      
      if (createResult.success) {
        const publishResult = await AdminService.marketingPublishPost(createResult.post.id);
        if (publishResult.success) {
          toast.success('Publication effectuée!');
          setGeneratedContent('');
          setGeneratedHashtags([]);
          loadData();
        }
      }
    } catch (error) {
      toast.error('Erreur lors de la publication');
    }
  };

  const handleSchedulePost = async () => {
    if (!scheduleDate || !scheduleTime || !generatedContent) {
      toast.error('Remplissez tous les champs');
      return;
    }
    
    try {
      const createResult = await AdminService.marketingCreatePost({
        content: generatedContent,
        hashtags: generatedHashtags,
        platform: targetPlatform,
        content_type: contentType,
        status: 'draft'
      });
      
      if (createResult.success) {
        const scheduleResult = await AdminService.marketingSchedulePost(
          createResult.post.id,
          `${scheduleDate}T${scheduleTime}:00`
        );
        if (scheduleResult.success) {
          toast.success('Publication programmée!');
          setScheduleDialogOpen(false);
          setGeneratedContent('');
          setGeneratedHashtags([]);
          loadData();
        }
      }
    } catch (error) {
      toast.error('Erreur lors de la programmation');
    }
  };

  const handleToggleAutomation = async (automationId, currentState) => {
    try {
      const result = await AdminService.marketingToggleAutomation(automationId, !currentState);
      if (result.success) {
        toast.success(!currentState ? 'Automation activée' : 'Automation désactivée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeleteScheduled = async (postId) => {
    if (!window.confirm('Supprimer cette publication programmée ?')) return;
    try {
      const result = await AdminService.marketingDeletePost(postId);
      if (result.success) {
        toast.success('Publication supprimée');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      draft: 'bg-gray-500/20 text-gray-400',
      active: 'bg-green-500/20 text-green-400',
      paused: 'bg-yellow-500/20 text-yellow-400',
      completed: 'bg-blue-500/20 text-blue-400',
      scheduled: 'bg-purple-500/20 text-purple-400',
      published: 'bg-green-500/20 text-green-400'
    };
    return <Badge className={variants[status] || 'bg-gray-500/20'}>{status}</Badge>;
  };

  const getPlatformIcon = (platformId) => {
    const platform = PLATFORMS.find(p => p.id === platformId);
    if (!platform) return null;
    const Icon = platform.icon;
    return <Icon className={`h-4 w-4 ${platform.color}`} />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-marketing" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-purple-500" />
            Marketing & Réseaux Sociaux
          </h2>
          <p className="text-gray-400">Campagnes, génération IA et publications</p>
        </div>
        <Button variant="outline" onClick={loadData} data-testid="refresh-marketing">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[#0a0a15]">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="generate">Générer</TabsTrigger>
          <TabsTrigger value="campaigns">Campagnes</TabsTrigger>
          <TabsTrigger value="scheduled">Programmées ({scheduledPosts.length})</TabsTrigger>
          <TabsTrigger value="segments">Segments</TabsTrigger>
          <TabsTrigger value="automations">Automations</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {stats && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <Target className="h-5 w-5 text-purple-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Campagnes actives</p>
                        <p className="text-xl font-bold text-white">{stats.campaigns?.active || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <Send className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Publications</p>
                        <p className="text-xl font-bold text-white">{stats.posts?.published || 0}</p>
                        <p className="text-xs text-yellow-400">{stats.posts?.scheduled || 0} programmées</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <TrendingUp className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Impressions (30j)</p>
                        <p className="text-xl font-bold text-white">{stats.engagement_30d?.impressions || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                        <Zap className="h-5 w-5 text-[#f5a623]" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Automations</p>
                        <p className="text-xl font-bold text-white">{stats.automations?.active || 0}</p>
                        <p className="text-xs text-gray-500">/{stats.automations?.total || 0} total</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-purple-500" />
                    Publications par plateforme
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-4 gap-4">
                    {PLATFORMS.map(platform => (
                      <div key={platform.id} className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <platform.icon className={`h-8 w-8 ${platform.color} mx-auto mb-2`} />
                        <p className="text-white font-bold">{stats.by_platform?.[platform.id] || 0}</p>
                        <p className="text-gray-400 text-xs">{platform.name}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Generate Tab */}
        <TabsContent value="generate" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Generation Form */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Paramètres de génération</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-gray-400">Type de contenu</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger className="bg-background border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CONTENT_TYPES.map(type => (
                        <SelectItem key={type.id} value={type.id}>
                          <div className="flex items-center gap-2">
                            <type.icon className="h-4 w-4" />
                            {type.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-gray-400">Plateforme cible</Label>
                  <Select value={targetPlatform} onValueChange={setTargetPlatform}>
                    <SelectTrigger className="bg-background border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PLATFORMS.map(platform => (
                        <SelectItem key={platform.id} value={platform.id}>
                          <div className="flex items-center gap-2">
                            <platform.icon className={`h-4 w-4 ${platform.color}`} />
                            {platform.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-gray-400">Produit (optionnel)</Label>
                  <Input
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="Ex: BIONIC HUNT/Chasse™ Premium"
                    className="bg-background border-border mt-1"
                  />
                </div>

                <div>
                  <Label className="text-gray-400">Mots-clés (séparés par virgule)</Label>
                  <Input
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="Ex: chasse, automne, Québec"
                    className="bg-background border-border mt-1"
                  />
                </div>

                <div>
                  <Label className="text-gray-400">Ton</Label>
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger className="bg-background border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professionnel</SelectItem>
                      <SelectItem value="friendly">Amical</SelectItem>
                      <SelectItem value="enthusiastic">Enthousiaste</SelectItem>
                      <SelectItem value="informative">Informatif</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={handleGenerateContent}
                  disabled={generating}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                >
                  {generating ? (
                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Génération...</>
                  ) : (
                    <><Sparkles className="h-4 w-4 mr-2" />Générer avec l'IA</>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Preview */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  Aperçu du contenu
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generatedContent ? (
                  <div className="space-y-4">
                    <div className="bg-background rounded-lg p-4 border border-border">
                      <div className="flex items-center gap-2 mb-3">
                        {getPlatformIcon(targetPlatform)}
                        <span className="text-white font-medium">BIONIC HUNT/Chasse</span>
                      </div>
                      <p className="text-gray-300 whitespace-pre-wrap text-sm">
                        {generatedContent}
                      </p>
                      {generatedHashtags.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1">
                          {generatedHashtags.map((tag, idx) => (
                            <span key={idx} className="text-purple-400 text-xs">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={handleCopyContent}>
                        <Copy className="h-4 w-4 mr-1" />Copier
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setScheduleDialogOpen(true)}>
                        <Calendar className="h-4 w-4 mr-1" />Programmer
                      </Button>
                      <Button 
                        size="sm" 
                        onClick={handlePublishNow}
                        className="bg-gradient-to-r from-purple-500 to-pink-500"
                      >
                        <Send className="h-4 w-4 mr-1" />Publier
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Sparkles className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">
                      Configurez les paramètres et cliquez sur "Générer" pour créer du contenu
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Campaigns Tab */}
        <TabsContent value="campaigns">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Campagnes marketing</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Type</TableHead>
                    <TableHead className="text-gray-400">Plateformes</TableHead>
                    <TableHead className="text-gray-400">Budget</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {campaigns.map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell className="text-white font-medium">{campaign.name}</TableCell>
                      <TableCell className="text-gray-400">{campaign.type}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {(campaign.target_platforms || []).map(p => (
                            <span key={p}>{getPlatformIcon(p)}</span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-[#f5a623]">${campaign.budget || 0}</TableCell>
                      <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {campaigns.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune campagne trouvée</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scheduled Tab */}
        <TabsContent value="scheduled">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Publications programmées</CardTitle>
            </CardHeader>
            <CardContent>
              {scheduledPosts.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Aucune publication programmée</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-gray-400">Plateforme</TableHead>
                      <TableHead className="text-gray-400">Contenu</TableHead>
                      <TableHead className="text-gray-400">Date</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scheduledPosts.map((post) => (
                      <TableRow key={post.id}>
                        <TableCell>{getPlatformIcon(post.platform)}</TableCell>
                        <TableCell className="text-gray-300 max-w-xs truncate">
                          {post.content?.slice(0, 50)}...
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {post.scheduled_at ? new Date(post.scheduled_at).toLocaleString('fr-CA') : '-'}
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className="text-red-400 hover:bg-red-500/10"
                            onClick={() => handleDeleteScheduled(post.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Segments Tab */}
        <TabsContent value="segments">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5 text-green-500" />
                Segments d'audience
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {segments.map((segment) => (
                  <div key={segment.id} className="p-4 bg-gray-900/50 rounded-lg">
                    <h4 className="text-white font-medium">{segment.name}</h4>
                    <p className="text-gray-400 text-sm mt-1">{segment.description || 'Segment d\'audience'}</p>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-2xl font-bold text-[#f5a623]">{segment.count || 0}</span>
                      {segment.is_default && (
                        <Badge variant="outline" className="text-xs">Système</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {segments.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun segment trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Automations Tab */}
        <TabsContent value="automations">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Automations marketing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Déclencheur</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                    <TableHead className="text-gray-400">Exécutions</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Contrôle</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {automations.map((automation) => (
                    <TableRow key={automation.id}>
                      <TableCell className="text-white font-medium">{automation.name}</TableCell>
                      <TableCell className="text-gray-400">{automation.trigger}</TableCell>
                      <TableCell className="text-gray-400">{(automation.actions || []).length} actions</TableCell>
                      <TableCell className="text-white">{automation.runs_count || 0}</TableCell>
                      <TableCell>
                        {automation.is_active ? (
                          <Badge className="bg-green-500/20 text-green-400">Actif</Badge>
                        ) : (
                          <Badge className="bg-gray-500/20 text-gray-400">Inactif</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleToggleAutomation(automation.id, automation.is_active)}
                        >
                          {automation.is_active ? (
                            <Pause className="h-4 w-4 text-yellow-400" />
                          ) : (
                            <Play className="h-4 w-4 text-green-400" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {automations.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucune automation trouvée</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Schedule Dialog */}
      <Dialog open={scheduleDialogOpen} onOpenChange={setScheduleDialogOpen}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-white">Programmer la publication</DialogTitle>
            <DialogDescription>
              Choisissez la date et l'heure de publication
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label className="text-gray-400">Date</Label>
              <Input
                type="date"
                value={scheduleDate}
                onChange={(e) => setScheduleDate(e.target.value)}
                className="bg-background border-border mt-1"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div>
              <Label className="text-gray-400">Heure</Label>
              <Input
                type="time"
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                className="bg-background border-border mt-1"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setScheduleDialogOpen(false)}>
              Annuler
            </Button>
            <Button 
              onClick={handleSchedulePost}
              className="bg-gradient-to-r from-purple-500 to-pink-500"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Programmer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminMarketing;
