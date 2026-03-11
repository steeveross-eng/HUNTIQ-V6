/**
 * Content Depot - Admin Interface
 * Gestion du contenu marketing avec workflow de validation
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Sparkles,
  Wand2,
  MessageSquare,
  Check,
  Send,
  Image,
  FileText,
  Hash,
  Target,
  TrendingUp,
  BarChart3,
  Eye,
  MousePointer,
  ShoppingCart,
  Video,
  Clock,
  Calendar,
  History,
  Edit,
  Trash2,
  RefreshCw,
  Plus,
  Download,
  Copy,
  ExternalLink,
  Loader2,
  CheckCircle,
  AlertCircle,
  XCircle,
  Zap,
  Globe,
  Facebook,
  Instagram
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Status Badge Colors
const STATUS_CONFIG = {
  pending: { label: 'En attente', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500', icon: Clock },
  optimized: { label: 'Optimisé', color: 'bg-blue-500/20 text-blue-400 border-blue-500', icon: Sparkles },
  accepted: { label: 'Accepté', color: 'bg-green-500/20 text-green-400 border-green-500', icon: Check },
  published: { label: 'Publié', color: 'bg-purple-500/20 text-purple-400 border-purple-500', icon: Send }
};

const ContentDepot = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [analytics, setAnalytics] = useState(null);
  const [generatingText, setGeneratingText] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [optimizing, setOptimizing] = useState(false);

  useEffect(() => {
    loadItems();
    loadAnalytics();
  }, [filterStatus]);

  const loadItems = async () => {
    setLoading(true);
    try {
      const params = filterStatus !== 'all' ? { status: filterStatus } : {};
      const response = await axios.get(`${API}/seo/content/depot`, { params });
      setItems(response.data.items || []);
    } catch (error) {
      console.error('Error loading items:', error);
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/seo/analytics/dashboard`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleOptimize = async (itemId) => {
    setOptimizing(true);
    try {
      const response = await axios.post(`${API}/seo/content/depot/${itemId}/optimize`);
      toast.success('Contenu optimisé par l\'IA!');
      loadItems();
      if (selectedItem?.id === itemId) {
        setSelectedItem({ ...selectedItem, ...response.data });
      }
    } catch (error) {
      toast.error('Erreur lors de l\'optimisation');
    } finally {
      setOptimizing(false);
    }
  };

  const handleSuggest = async (itemId) => {
    try {
      const response = await axios.post(`${API}/seo/content/depot/${itemId}/suggest`);
      toast.success('Suggestions générées!');
      loadItems();
    } catch (error) {
      toast.error('Erreur lors de la génération des suggestions');
    }
  };

  const handleAccept = async (itemId) => {
    try {
      await axios.post(`${API}/seo/content/depot/${itemId}/accept`);
      toast.success('Contenu accepté!');
      loadItems();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handlePublish = async (itemId, platforms = ['internal']) => {
    try {
      await axios.post(`${API}/seo/content/depot/${itemId}/publish`, platforms);
      toast.success('Contenu publié!');
      loadItems();
    } catch (error) {
      toast.error('Erreur lors de la publication');
    }
  };

  const handleDelete = async (itemId) => {
    if (!confirm('Supprimer ce contenu?')) return;
    try {
      await axios.delete(`${API}/seo/content/depot/${itemId}`);
      toast.success('Contenu supprimé');
      loadItems();
      setShowDetailModal(false);
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handleGenerateText = async (context, contentType = 'ad') => {
    setGeneratingText(true);
    try {
      const response = await axios.post(`${API}/seo/content/generate-text`, {
        content_type: contentType,
        context,
        tone: 'professional',
        platform: 'all',
        language: 'fr'
      });
      toast.success('Texte généré!');
      return response.data;
    } catch (error) {
      toast.error('Erreur lors de la génération');
      return null;
    } finally {
      setGeneratingText(false);
    }
  };

  const handleGenerateImage = async (prompt, style = 'hunting') => {
    setGeneratingImage(true);
    try {
      const response = await axios.post(`${API}/seo/content/generate-image`, {
        prompt,
        style,
        format: 'square'
      });
      toast.success('Image générée!');
      return response.data;
    } catch (error) {
      toast.error('Erreur lors de la génération d\'image');
      return null;
    } finally {
      setGeneratingImage(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <Eye className="h-5 w-5 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.summary?.total_page_views || 0}</div>
              <div className="text-gray-500 text-xs">Vues</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <MousePointer className="h-5 w-5 text-green-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.summary?.total_clicks || 0}</div>
              <div className="text-gray-500 text-xs">Clics</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <ShoppingCart className="h-5 w-5 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.summary?.total_conversions || 0}</div>
              <div className="text-gray-500 text-xs">Conversions</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <Video className="h-5 w-5 text-red-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.summary?.total_video_views || 0}</div>
              <div className="text-gray-500 text-xs">Vidéos vues</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <TrendingUp className="h-5 w-5 text-yellow-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.conversion_rate || 0}%</div>
              <div className="text-gray-500 text-xs">Taux conversion</div>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardContent className="p-4 text-center">
              <Globe className="h-5 w-5 text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{analytics.summary?.unique_pages || 0}</div>
              <div className="text-gray-500 text-xs">Pages actives</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Header & Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="h-6 w-6 text-[#f5a623]" />
            Dépôt de Contenu
          </h2>
          <p className="text-gray-400 text-sm">Gérez et publiez votre contenu marketing avec l'IA</p>
        </div>
        <div className="flex gap-2">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[150px] bg-background">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="pending">En attente</SelectItem>
              <SelectItem value="optimized">Optimisé</SelectItem>
              <SelectItem value="accepted">Accepté</SelectItem>
              <SelectItem value="published">Publié</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={() => setShowCreateModal(true)} className="bg-[#f5a623] hover:bg-[#d4891c] text-black">
            <Plus className="h-4 w-4 mr-2" />
            Nouveau contenu
          </Button>
        </div>
      </div>

      {/* Content List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
        </div>
      ) : items.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="p-12 text-center">
            <FileText className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-white text-lg font-semibold mb-2">Aucun contenu</h3>
            <p className="text-gray-400 mb-4">Créez votre premier contenu marketing avec l'IA</p>
            <Button onClick={() => setShowCreateModal(true)} className="bg-[#f5a623] text-black">
              <Plus className="h-4 w-4 mr-2" />
              Créer un contenu
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const statusConfig = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending;
            const StatusIcon = statusConfig.icon;
            
            return (
              <Card key={item.id} className="bg-card border-border hover:border-[#f5a623]/50 transition-all">
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    {/* Visual Preview */}
                    <div className="w-20 h-20 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                      {item.visuals?.[0]?.image_base64 ? (
                        <img 
                          src={`data:image/png;base64,${item.visuals[0].image_base64}`} 
                          alt={item.title || "Aperçu visuel du contenu"} 
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <Image className="h-8 w-8 text-gray-600" />
                      )}
                    </div>

                    {/* Content Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-semibold truncate">{item.title}</h3>
                        <Badge className={`text-[10px] ${statusConfig.color}`}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {statusConfig.label}
                        </Badge>
                        <Badge variant="outline" className="text-[10px]">{item.content_type}</Badge>
                      </div>
                      <p className="text-gray-400 text-sm line-clamp-2">{item.description}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(item.created_at).toLocaleDateString('fr-CA')}
                        </span>
                        <span className="flex items-center gap-1">
                          <History className="h-3 w-3" />
                          v{item.versions?.length || 1}
                        </span>
                        {item.hashtags?.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Hash className="h-3 w-3" />
                            {item.hashtags.length} tags
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {/* Optimize Button */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleOptimize(item.id)}
                        disabled={optimizing}
                        className="text-xs"
                      >
                        <Wand2 className="h-3.5 w-3.5 mr-1" />
                        Optimiser
                      </Button>

                      {/* Suggest Button */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSuggest(item.id)}
                        className="text-xs"
                      >
                        <MessageSquare className="h-3.5 w-3.5 mr-1" />
                        Suggérer
                      </Button>

                      {/* Accept Button */}
                      {item.status !== 'accepted' && item.status !== 'published' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAccept(item.id)}
                          className="text-xs text-green-400 border-green-500/50 hover:bg-green-500/10"
                        >
                          <Check className="h-3.5 w-3.5 mr-1" />
                          Accepter
                        </Button>
                      )}

                      {/* Publish Button */}
                      {(item.status === 'accepted' || item.status === 'optimized') && (
                        <Button
                          size="sm"
                          onClick={() => handlePublish(item.id)}
                          className="text-xs bg-purple-600 hover:bg-purple-700"
                        >
                          <Send className="h-3.5 w-3.5 mr-1" />
                          Publier
                        </Button>
                      )}

                      {/* View Details */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedItem(item); setShowDetailModal(true); }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Content Modal */}
      <CreateContentModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreated={() => { setShowCreateModal(false); loadItems(); }}
        onGenerateText={handleGenerateText}
        onGenerateImage={handleGenerateImage}
        generatingText={generatingText}
        generatingImage={generatingImage}
      />

      {/* Detail Modal */}
      {selectedItem && (
        <ContentDetailModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          item={selectedItem}
          onOptimize={() => handleOptimize(selectedItem.id)}
          onSuggest={() => handleSuggest(selectedItem.id)}
          onAccept={() => handleAccept(selectedItem.id)}
          onPublish={(platforms) => handlePublish(selectedItem.id, platforms)}
          onDelete={() => handleDelete(selectedItem.id)}
          optimizing={optimizing}
        />
      )}
    </div>
  );
};

// ============================================
// CREATE CONTENT MODAL
// ============================================

const CreateContentModal = ({ isOpen, onClose, onCreated, onGenerateText, onGenerateImage, generatingText, generatingImage }) => {
  const [form, setForm] = useState({
    title: '',
    description: '',
    content_type: 'ad',
    platform: 'all',
    format: 'square',
    hashtags: [],
    call_to_action: '',
    target_page: ''
  });
  const [aiContext, setAiContext] = useState('');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateWithAI = async () => {
    if (!aiContext) {
      toast.error('Décrivez le contenu à générer');
      return;
    }
    const result = await onGenerateText(aiContext, form.content_type);
    if (result?.generated) {
      try {
        const parsed = JSON.parse(result.generated);
        setForm(f => ({
          ...f,
          title: parsed.title || f.title,
          description: parsed.description || f.description,
          hashtags: parsed.hashtags || f.hashtags,
          call_to_action: parsed.cta || f.call_to_action
        }));
      } catch {
        // If not JSON, use as description
        setForm(f => ({ ...f, description: result.generated }));
      }
    }
  };

  const handleGenerateImageAI = async () => {
    const prompt = form.title || aiContext || 'Hunting equipment in Canadian wilderness';
    const result = await onGenerateImage(prompt, 'hunting');
    if (result?.image_base64) {
      setGeneratedImage(result.image_base64);
    }
  };

  const handleSubmit = async () => {
    if (!form.title || !form.description) {
      toast.error('Titre et description requis');
      return;
    }
    setLoading(true);
    try {
      const data = { ...form };
      if (typeof data.hashtags === 'string') {
        data.hashtags = data.hashtags.split(',').map(h => h.trim()).filter(Boolean);
      }
      
      await axios.post(`${API}/seo/content/depot`, data);
      toast.success('Contenu créé!');
      onCreated();
      setForm({
        title: '', description: '', content_type: 'ad', platform: 'all',
        format: 'square', hashtags: [], call_to_action: '', target_page: ''
      });
      setGeneratedImage(null);
      setAiContext('');
    } catch (error) {
      toast.error('Erreur lors de la création');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Plus className="h-5 w-5 text-[#f5a623]" />
            Créer un contenu marketing
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* AI Generation Section */}
          <Card className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-purple-500/30">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-5 w-5 text-purple-400" />
                <span className="text-white font-semibold">Génération IA</span>
              </div>
              <Textarea
                placeholder="Décrivez le produit, la promotion ou le contenu à générer..."
                value={aiContext}
                onChange={(e) => setAiContext(e.target.value)}
                className="bg-background mb-3"
              />
              <div className="flex gap-2">
                <Button
                  onClick={handleGenerateWithAI}
                  disabled={generatingText}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {generatingText ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Wand2 className="h-4 w-4 mr-2" />}
                  Générer texte
                </Button>
                <Button
                  onClick={handleGenerateImageAI}
                  disabled={generatingImage}
                  variant="outline"
                  className="border-purple-500/50"
                >
                  {generatingImage ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Image className="h-4 w-4 mr-2" />}
                  Générer image
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Generated Image Preview */}
          {generatedImage && (
            <div className="relative">
              <img 
                src={`data:image/png;base64,${generatedImage}`} 
                alt="Generated" 
                className="w-full h-48 object-cover rounded-lg"
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 bg-black/50"
                onClick={() => setGeneratedImage(null)}
              >
                <XCircle className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Form Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label>Titre *</Label>
              <Input
                value={form.title}
                onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
                placeholder="Titre accrocheur..."
                className="bg-background"
              />
            </div>

            <div>
              <Label>Type de contenu</Label>
              <Select value={form.content_type} onValueChange={(v) => setForm(f => ({ ...f, content_type: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ad">Publicité</SelectItem>
                  <SelectItem value="social">Post social</SelectItem>
                  <SelectItem value="seo">Contenu SEO</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Plateforme</Label>
              <Select value={form.platform} onValueChange={(v) => setForm(f => ({ ...f, platform: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  <SelectItem value="facebook">Facebook</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="tiktok">TikTok</SelectItem>
                  <SelectItem value="youtube">YouTube</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-2">
              <Label>Description *</Label>
              <Textarea
                value={form.description}
                onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                placeholder="Description du contenu..."
                className="bg-background min-h-[100px]"
              />
            </div>

            <div>
              <Label>Hashtags (séparés par virgule)</Label>
              <Input
                value={Array.isArray(form.hashtags) ? form.hashtags.join(', ') : form.hashtags}
                onChange={(e) => setForm(f => ({ ...f, hashtags: e.target.value }))}
                placeholder="#chasse, #quebec, #orignal"
                className="bg-background"
              />
            </div>

            <div>
              <Label>Appel à l'action</Label>
              <Input
                value={form.call_to_action}
                onChange={(e) => setForm(f => ({ ...f, call_to_action: e.target.value }))}
                placeholder="Achetez maintenant!"
                className="bg-background"
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Annuler</Button>
          <Button onClick={handleSubmit} disabled={loading} className="bg-[#f5a623] text-black">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
            Créer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// CONTENT DETAIL MODAL
// ============================================

const ContentDetailModal = ({ isOpen, onClose, item, onOptimize, onSuggest, onAccept, onPublish, onDelete, optimizing }) => {
  if (!item) return null;
  const statusConfig = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-white">{item.title}</DialogTitle>
            <Badge className={statusConfig.color}>{statusConfig.label}</Badge>
          </div>
        </DialogHeader>

        <Tabs defaultValue="content" className="w-full">
          <TabsList className="w-full justify-start bg-gray-900">
            <TabsTrigger value="content">Contenu</TabsTrigger>
            <TabsTrigger value="versions">Versions ({item.versions?.length || 0})</TabsTrigger>
            <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
            <TabsTrigger value="history">Historique</TabsTrigger>
          </TabsList>

          <TabsContent value="content" className="space-y-4 mt-4">
            <div>
              <Label className="text-gray-400">Description</Label>
              <p className="text-white mt-1">{item.description}</p>
            </div>

            {item.hashtags?.length > 0 && (
              <div>
                <Label className="text-gray-400">Hashtags</Label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {item.hashtags.map((tag, i) => (
                    <Badge key={i} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </div>
            )}

            {item.call_to_action && (
              <div>
                <Label className="text-gray-400">Appel à l'action</Label>
                <p className="text-[#f5a623] font-semibold mt-1">{item.call_to_action}</p>
              </div>
            )}

            <div className="flex gap-2 pt-4 border-t border-border">
              <Button onClick={onOptimize} disabled={optimizing} variant="outline">
                {optimizing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Wand2 className="h-4 w-4 mr-2" />}
                Optimiser (IA)
              </Button>
              <Button onClick={onSuggest} variant="outline">
                <MessageSquare className="h-4 w-4 mr-2" />
                Suggérer
              </Button>
              {item.status !== 'published' && (
                <Button onClick={onAccept} className="bg-green-600 hover:bg-green-700">
                  <Check className="h-4 w-4 mr-2" />
                  Accepter
                </Button>
              )}
              {item.status === 'accepted' && (
                <Button onClick={() => onPublish(['internal'])} className="bg-purple-600 hover:bg-purple-700">
                  <Send className="h-4 w-4 mr-2" />
                  Publier
                </Button>
              )}
            </div>
          </TabsContent>

          <TabsContent value="versions" className="mt-4">
            <div className="space-y-3">
              {item.versions?.map((version, i) => (
                <Card key={i} className="bg-gray-900/50 border-border">
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline">Version {version.version}</Badge>
                      <span className="text-gray-500 text-xs">{new Date(version.created_at).toLocaleString('fr-CA')}</span>
                    </div>
                    <p className="text-gray-400 text-sm">{version.action}</p>
                    {version.ai_response && (
                      <div className="mt-2 p-2 bg-purple-900/20 rounded text-xs text-purple-300">
                        <Sparkles className="h-3 w-3 inline mr-1" />
                        Optimisation IA
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="suggestions" className="mt-4">
            {item.suggestions?.length > 0 ? (
              <div className="space-y-3">
                {item.suggestions.map((suggestion, i) => (
                  <Card key={i} className="bg-gray-900/50 border-border">
                    <CardContent className="p-3">
                      <pre className="text-gray-300 text-sm whitespace-pre-wrap">{suggestion.ai_suggestions}</pre>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Aucune suggestion. Cliquez sur "Suggérer" pour générer des recommandations IA.</p>
            )}
          </TabsContent>

          <TabsContent value="history" className="mt-4">
            {item.publish_history?.length > 0 ? (
              <div className="space-y-3">
                {item.publish_history.map((pub, i) => (
                  <Card key={i} className="bg-gray-900/50 border-border">
                    <CardContent className="p-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-white">Publié sur {pub.platforms?.join(', ')}</span>
                      </div>
                      <span className="text-gray-500 text-xs">{new Date(pub.published_at).toLocaleString('fr-CA')}</span>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Pas encore publié</p>
            )}
          </TabsContent>
        </Tabs>

        <DialogFooter className="border-t border-border pt-4">
          <Button variant="ghost" onClick={onDelete} className="text-red-400 hover:text-red-300 mr-auto">
            <Trash2 className="h-4 w-4 mr-2" />
            Supprimer
          </Button>
          <Button variant="outline" onClick={onClose}>Fermer</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ContentDepot;
