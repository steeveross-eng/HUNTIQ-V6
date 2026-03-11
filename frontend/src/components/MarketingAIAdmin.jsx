/**
 * MarketingAIAdmin - AI Marketing content generation and social media publishing
 * Generates promotional content and manages social media publications
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Sparkles,
  Share2,
  Instagram,
  Facebook,
  Send,
  Copy,
  RefreshCw,
  Image,
  FileText,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Edit,
  Trash2,
  Eye,
  PlusCircle,
  TrendingUp,
  Target,
  Users,
  MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Content types for generation
const CONTENT_TYPES = [
  { id: 'product_promo', name: 'Promotion Produit', icon: Target },
  { id: 'educational', name: 'Contenu Éducatif', icon: FileText },
  { id: 'seasonal', name: 'Publication Saisonnière', icon: Calendar },
  { id: 'testimonial', name: 'Témoignage Client', icon: MessageSquare },
  { id: 'tip', name: 'Conseil de Chasse', icon: TrendingUp },
  { id: 'engagement', name: 'Question/Engagement', icon: Users }
];

// Social platforms
const PLATFORMS = [
  { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'text-blue-500', maxLength: 63206 },
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'text-pink-500', maxLength: 2200 },
];

const MarketingAIAdmin = () => {
  const { language, brand, t } = useLanguage();
  const [activeTab, setActiveTab] = useState('generate');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  
  // Generation form
  const [contentType, setContentType] = useState('product_promo');
  const [targetPlatform, setTargetPlatform] = useState('facebook');
  const [productName, setProductName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [tone, setTone] = useState('professional');
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedHashtags, setGeneratedHashtags] = useState([]);
  
  // Scheduling
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  
  // History
  const [publishHistory, setPublishHistory] = useState([]);

  // Fetch scheduled posts and history
  const fetchData = async () => {
    try {
      const [schedResponse, histResponse] = await Promise.all([
        axios.get(`${API}/marketing/scheduled`).catch(() => ({ data: { posts: [] } })),
        axios.get(`${API}/marketing/history`).catch(() => ({ data: { history: [] } }))
      ]);
      setScheduledPosts(schedResponse.data.posts || []);
      setPublishHistory(histResponse.data.history || []);
    } catch (error) {
      console.error('Error fetching marketing data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Generate content with AI
  const generateContent = async () => {
    if (!contentType) {
      toast.error('Sélectionnez un type de contenu');
      return;
    }
    
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/marketing/generate`, {
        content_type: contentType,
        platform: targetPlatform,
        product_name: productName || null,
        keywords: keywords ? keywords.split(',').map(k => k.trim()) : [],
        tone: tone,
        language: language,
        brand_name: brand.full
      });
      
      if (response.data.success) {
        setGeneratedContent(response.data.content);
        setGeneratedHashtags(response.data.hashtags || []);
        toast.success('Contenu généré avec succès!');
      }
    } catch (error) {
      console.error('Generation error:', error);
      // Fallback to mock content if API not available
      const mockContent = generateMockContent(contentType, targetPlatform, productName);
      setGeneratedContent(mockContent.content);
      setGeneratedHashtags(mockContent.hashtags);
      toast.success('Contenu généré (mode démo)');
    } finally {
      setGenerating(false);
    }
  };

  // Mock content generator for demo
  const generateMockContent = (type, platform, product) => {
    const contents = {
      product_promo: {
        content: `🎯 ${product || 'BIONIC™ Attractif Premium'}\n\nDécouvrez notre solution scientifiquement prouvée pour attirer votre gibier préféré. Testé sur le terrain par des chasseurs professionnels du Québec.\n\n✅ Formule exclusive\n✅ Résultats garantis\n✅ Livraison rapide\n\n👉 Commandez maintenant sur chassebionic.ca`,
        hashtags: ['ChasseBionic', 'ChasseQuebec', 'Orignal', 'Chevreuil', 'AttractifChasse']
      },
      educational: {
        content: `📚 Le saviez-vous?\n\nL'orignal peut détecter des odeurs jusqu'à 2km de distance par temps humide. C'est pourquoi le choix de votre attractif est crucial!\n\nNos experts ont analysé plus de 50 produits pour vous aider à faire le meilleur choix.\n\n🔬 Découvrez notre analyse complète sur chassebionic.ca`,
        hashtags: ['ChasseBionic', 'ConseilChasse', 'ScienceChasse', 'Orignal']
      },
      seasonal: {
        content: `🍂 La saison approche!\n\nPréparez-vous pour la chasse ${new Date().getMonth() >= 8 ? 'automnale' : 'printanière'}. Nos produits sont prêts, et vous?\n\n📦 Stock limité - Commandez maintenant\n🚚 Livraison express disponible\n\nchassebonic.ca`,
        hashtags: ['SaisonChasse', 'ChasseBionic', 'ChasseAutomne', 'Préparation']
      },
      tip: {
        content: `💡 Conseil du pro\n\nPour maximiser l'efficacité de votre attractif:\n\n1️⃣ Appliquez contre le vent\n2️⃣ Renouvelez toutes les 48h\n3️⃣ Combinez avec des leurres visuels\n\nPlus de conseils sur chassebionic.ca 🎯`,
        hashtags: ['ConseilChasse', 'ChasseBionic', 'TechniquesChasse', 'ProTip']
      },
      engagement: {
        content: `🤔 Question du jour!\n\nQuel est votre gibier préféré cette saison?\n\n🫎 Orignal\n🦌 Chevreuil\n🐻 Ours\n\nRépondez en commentaire! 👇\n\n#ChasseBionic #Sondage`,
        hashtags: ['ChasseBionic', 'Sondage', 'CommunautéChasse']
      },
      testimonial: {
        content: `⭐⭐⭐⭐⭐\n\n"Meilleur attractif que j'ai utilisé en 20 ans de chasse. J'ai eu mon orignal en moins de 2 heures!"\n\n- Marc T., Lac-Saint-Jean\n\nMerci à nos clients pour leur confiance! 🙏\n\nchassebonic.ca`,
        hashtags: ['Témoignage', 'ChasseBionic', 'ClientSatisfait', 'ChasseQuebec']
      }
    };
    
    return contents[type] || contents.product_promo;
  };

  // Copy content to clipboard
  const copyContent = () => {
    const fullContent = generatedContent + '\n\n' + generatedHashtags.map(h => `#${h}`).join(' ');
    navigator.clipboard.writeText(fullContent);
    toast.success('Contenu copié!');
  };

  // Schedule post
  const schedulePost = async () => {
    if (!scheduleDate || !scheduleTime || !generatedContent) {
      toast.error('Remplissez tous les champs');
      return;
    }
    
    try {
      await axios.post(`${API}/marketing/schedule`, {
        content: generatedContent,
        hashtags: generatedHashtags,
        platform: targetPlatform,
        scheduled_at: `${scheduleDate}T${scheduleTime}:00`,
        content_type: contentType
      });
      
      toast.success('Publication programmée!');
      setScheduleDialogOpen(false);
      fetchData();
    } catch (error) {
      // Mock scheduling for demo
      const newPost = {
        id: Date.now(),
        content: generatedContent.substring(0, 50) + '...',
        platform: targetPlatform,
        scheduled_at: `${scheduleDate}T${scheduleTime}:00`,
        status: 'scheduled'
      };
      setScheduledPosts([...scheduledPosts, newPost]);
      toast.success('Publication programmée (mode démo)');
      setScheduleDialogOpen(false);
    }
  };

  // Publish now
  const publishNow = async () => {
    if (!generatedContent) {
      toast.error('Générez du contenu d\'abord');
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/marketing/publish`, {
        content: generatedContent,
        hashtags: generatedHashtags,
        platform: targetPlatform
      });
      
      toast.success(`Publié sur ${targetPlatform}!`);
      fetchData();
    } catch (error) {
      toast.info('Publication simulée (connectez vos réseaux sociaux pour publier réellement)');
      // Add to mock history
      setPublishHistory([{
        id: Date.now(),
        content: generatedContent.substring(0, 50) + '...',
        platform: targetPlatform,
        published_at: new Date().toISOString(),
        status: 'published'
      }, ...publishHistory]);
    } finally {
      setLoading(false);
    }
  };

  // Delete scheduled post
  const deleteScheduledPost = async (postId) => {
    try {
      await axios.delete(`${API}/marketing/scheduled/${postId}`);
      toast.success('Publication supprimée');
      fetchData();
    } catch (error) {
      setScheduledPosts(scheduledPosts.filter(p => p.id !== postId));
      toast.success('Publication supprimée');
    }
  };

  return (
    <div className="space-y-6" data-testid="marketing-ai-admin">
      {/* Header */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  Marketing IA & Réseaux Sociaux
                  <Badge className="bg-purple-500/20 text-purple-400">Beta</Badge>
                </CardTitle>
                <CardDescription>
                  Générez du contenu avec l'IA et publiez sur vos réseaux sociaux
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={fetchData}>
                <RefreshCw className="h-4 w-4 mr-1" />
                {t('common_refresh')}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-card border border-border">
          <TabsTrigger value="generate" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <Sparkles className="h-4 w-4 mr-2" />Générer
          </TabsTrigger>
          <TabsTrigger value="scheduled" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <Calendar className="h-4 w-4 mr-2" />Programmées ({scheduledPosts.length})
          </TabsTrigger>
          <TabsTrigger value="history" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white">
            <Clock className="h-4 w-4 mr-2" />Historique
          </TabsTrigger>
        </TabsList>

        {/* Generate Tab */}
        <TabsContent value="generate" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Generation Form */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white text-lg">Paramètres de génération</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-gray-400">Type de contenu</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger className="bg-background border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CONTENT_TYPES.map((type) => {
                        const Icon = type.icon;
                        return (
                          <SelectItem key={type.id} value={type.id}>
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4" />
                              {type.name}
                            </div>
                          </SelectItem>
                        );
                      })}
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
                      {PLATFORMS.map((platform) => {
                        const Icon = platform.icon;
                        return (
                          <SelectItem key={platform.id} value={platform.id}>
                            <div className="flex items-center gap-2">
                              <Icon className={`h-4 w-4 ${platform.color}`} />
                              {platform.name}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-gray-400">Produit (optionnel)</Label>
                  <Input
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="Ex: BIONIC™ Attractif Orignal"
                    className="bg-background border-border mt-1"
                  />
                </div>

                <div>
                  <Label className="text-gray-400">Mots-clés (séparés par virgule)</Label>
                  <Input
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="Ex: orignal, automne, Québec"
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
                  onClick={generateContent}
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
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  Aperçu du contenu
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generatedContent ? (
                  <div className="space-y-4">
                    <div className="bg-background rounded-lg p-4 border border-border">
                      <div className="flex items-center gap-2 mb-3">
                        {targetPlatform === 'facebook' ? (
                          <Facebook className="h-5 w-5 text-blue-500" />
                        ) : (
                          <Instagram className="h-5 w-5 text-pink-500" />
                        )}
                        <span className="text-white font-medium">{brand.full}</span>
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
                      <Button variant="outline" size="sm" onClick={copyContent}>
                        <Copy className="h-4 w-4 mr-1" />Copier
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setScheduleDialogOpen(true)}>
                        <Calendar className="h-4 w-4 mr-1" />Programmer
                      </Button>
                      <Button 
                        size="sm" 
                        onClick={publishNow}
                        disabled={loading}
                        className="bg-gradient-to-r from-purple-500 to-pink-500"
                      >
                        {loading ? (
                          <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                        ) : (
                          <Send className="h-4 w-4 mr-1" />
                        )}
                        Publier
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

        {/* Scheduled Tab */}
        <TabsContent value="scheduled">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg">Publications programmées</CardTitle>
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
                    <TableRow className="border-border">
                      <TableHead className="text-gray-400">Plateforme</TableHead>
                      <TableHead className="text-gray-400">Contenu</TableHead>
                      <TableHead className="text-gray-400">Date</TableHead>
                      <TableHead className="text-gray-400">Statut</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scheduledPosts.map((post) => (
                      <TableRow key={post.id} className="border-border">
                        <TableCell>
                          {post.platform === 'facebook' ? (
                            <Facebook className="h-5 w-5 text-blue-500" />
                          ) : (
                            <Instagram className="h-5 w-5 text-pink-500" />
                          )}
                        </TableCell>
                        <TableCell className="text-gray-300 max-w-xs truncate">
                          {post.content}
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {new Date(post.scheduled_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-yellow-500/20 text-yellow-400">
                            <Clock className="h-3 w-3 mr-1" />
                            Programmée
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className="text-red-400 hover:bg-red-500/10"
                            onClick={() => deleteScheduledPost(post.id)}
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

        {/* History Tab */}
        <TabsContent value="history">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg">Historique des publications</CardTitle>
            </CardHeader>
            <CardContent>
              {publishHistory.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Aucune publication dans l'historique</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="border-border">
                      <TableHead className="text-gray-400">Plateforme</TableHead>
                      <TableHead className="text-gray-400">Contenu</TableHead>
                      <TableHead className="text-gray-400">Publié le</TableHead>
                      <TableHead className="text-gray-400">Statut</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {publishHistory.map((post) => (
                      <TableRow key={post.id} className="border-border">
                        <TableCell>
                          {post.platform === 'facebook' ? (
                            <Facebook className="h-5 w-5 text-blue-500" />
                          ) : (
                            <Instagram className="h-5 w-5 text-pink-500" />
                          )}
                        </TableCell>
                        <TableCell className="text-gray-300 max-w-xs truncate">
                          {post.content}
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {new Date(post.published_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-green-500/20 text-green-400">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Publié
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
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
              onClick={schedulePost}
              className="bg-gradient-to-r from-purple-500 to-pink-500"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Programmer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Info Notice */}
      <Card className="bg-purple-500/10 border-purple-500/30">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Share2 className="h-5 w-5 text-purple-400 mt-0.5" />
            <div>
              <p className="text-purple-400 font-medium">Connexion aux réseaux sociaux</p>
              <p className="text-gray-400 text-sm mt-1">
                Pour publier directement sur Facebook et Instagram, connectez vos comptes professionnels 
                dans les paramètres. En attendant, vous pouvez copier le contenu généré.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MarketingAIAdmin;
