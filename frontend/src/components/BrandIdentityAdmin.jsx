/**
 * BrandIdentityAdmin - Admin panel for managing brand visual identity
 * Manages logos, brand assets, and communication headers
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
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
  Palette,
  Image,
  Download,
  Upload,
  RefreshCw,
  Eye,
  Copy,
  FileText,
  Globe,
  Sparkles,
  CheckCircle,
  History,
  Loader2,
  Mail,
  FileSignature,
  Building2,
  Trees,
  AlertTriangle,
  Trash2,
  Plus,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage, BRAND_NAMES } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// BRANCHE 1 POLISH FINAL: Logo variants avec formats optimisés (AVIF/WebP/PNG)
const LOGO_VARIANTS = {
  main: {
    name: "Logo Principal BIONIC™", 
    url: "/logos/bionic-logo-main.png",
    urlWebp: "/logos/bionic-logo-main.webp",
    urlAvif: "/logos/bionic-logo-main.avif",
    description: "Logo unifié Chasse Bionic™ / Bionic Hunt™"
  },
  fr: {
    full: { 
      name: "Logo Complet FR", 
      url: "/logos/bionic-logo-main.png",
      urlWebp: "/logos/bionic-logo-main.webp",
      urlAvif: "/logos/bionic-logo-main.avif",
      description: "Logo Chasse Bionic™"
    }
  },
  en: {
    full: { 
      name: "Full Logo EN", 
      url: "/logos/bionic-logo-main.png",
      urlWebp: "/logos/bionic-logo-main.webp",
      urlAvif: "/logos/bionic-logo-main.avif",
      description: "Bionic Hunt™ logo"
    }
  }
};

// Document templates for headers
const DOCUMENT_TEMPLATES = [
  { id: "letter", name: "Lettre officielle", nameEn: "Official Letter", icon: FileText },
  { id: "email", name: "En-tête Email", nameEn: "Email Header", icon: Mail },
  { id: "contract", name: "Contrat", nameEn: "Contract", icon: FileSignature },
  { id: "invoice", name: "Facture", nameEn: "Invoice", icon: FileText },
  { id: "partner", name: "Document Partenaire", nameEn: "Partner Document", icon: Building2 },
  { id: "zec", name: "Document ZEC/Sépaq", nameEn: "ZEC/Sépaq Document", icon: Trees },
  { id: "press", name: "Communiqué de Presse", nameEn: "Press Release", icon: FileText }
];

const BrandIdentityAdmin = () => {
  const { language, brand, t } = useLanguage();
  const [activeTab, setActiveTab] = useState("logos");
  const [loading, setLoading] = useState(false);
  const [previewLogo, setPreviewLogo] = useState(null);
  const [generatingHeader, setGeneratingHeader] = useState(null);
  const [customLogos, setCustomLogos] = useState([]);
  const [logoHistory, setLogoHistory] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);
  
  // PDF Generator Dialog
  const [pdfDialogOpen, setPdfDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [pdfForm, setPdfForm] = useState({
    language: 'fr',
    title: '',
    content: '',
    recipient_name: '',
    recipient_address: ''
  });

  const fileInputRef = useRef(null);

  // Fetch logos from backend
  const fetchLogos = async () => {
    try {
      const response = await axios.get(`${API}/brand/logos`);
      setCustomLogos(response.data.custom || []);
    } catch (error) {
      console.error('Error fetching logos:', error);
    }
  };

  // Fetch logo history
  const fetchLogoHistory = async () => {
    try {
      const response = await axios.get(`${API}/brand/logo-history`);
      setLogoHistory(response.data.history || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  useEffect(() => {
    fetchLogos();
    fetchLogoHistory();
  }, []);

  // Copy URL to clipboard
  const copyToClipboard = (url) => {
    navigator.clipboard.writeText(window.location.origin + url);
    toast.success("URL copiée!");
  };

  // Download logo
  const downloadLogo = async (url, filename) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success("Téléchargement lancé!");
    } catch (error) {
      toast.error("Erreur lors du téléchargement");
    }
  };

  // Generate document header - connected to real backend
  const generateHeader = async (templateId, lang, customContent = null) => {
    setGeneratingHeader(`${templateId}-${lang}`);
    try {
      let url = `${API}/brand/generate-pdf/${templateId}/${lang}`;
      let response;
      
      if (customContent) {
        // POST with custom content
        response = await axios.post(
          `${API}/brand/generate-pdf`,
          {
            template_type: templateId,
            language: lang,
            title: customContent.title || null,
            content: customContent.content || null,
            recipient_name: customContent.recipient_name || null,
            recipient_address: customContent.recipient_address || null
          },
          { responseType: 'blob' }
        );
      } else {
        // GET for quick download
        response = await axios.get(url, { responseType: 'blob' });
      }
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${templateId}_${lang}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      toast.success(`PDF ${lang === 'fr' ? 'français' : 'anglais'} généré et téléchargé!`);
      setPdfDialogOpen(false);
    } catch (error) {
      console.error('Error generating PDF:', error);
      toast.error("Erreur lors de la génération du PDF");
    } finally {
      setGeneratingHeader(null);
    }
  };

  // Upload custom logo
  const handleLogoUpload = async (file, lang, logoType = 'primary') => {
    if (!file) return;
    
    // Validate file
    const allowedTypes = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Format non supporté. Utilisez PNG, JPEG, WebP ou SVG.");
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Le fichier doit faire moins de 5MB");
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    setUploadProgress({ lang, progress: 0 });
    
    try {
      const response = await axios.post(
        `${API}/brand/upload-logo?language=${lang}&logo_type=${logoType}`,
        formData,
        { 
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress({ lang, progress });
          }
        }
      );
      
      if (response.data.success) {
        toast.success(response.data.message);
        fetchLogos();
        fetchLogoHistory();
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || "Erreur lors de l'upload du logo");
    } finally {
      setUploadProgress(null);
    }
  };

  // Delete custom logo
  const deleteCustomLogo = async (filename) => {
    if (!confirm('Supprimer ce logo?')) return;
    
    try {
      await axios.delete(`${API}/brand/logo/${filename}`);
      toast.success("Logo supprimé");
      fetchLogos();
      fetchLogoHistory();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  // Open PDF dialog with template
  const openPdfDialog = (template) => {
    setSelectedTemplate(template);
    setPdfForm({
      language: 'fr',
      title: '',
      content: '',
      recipient_name: '',
      recipient_address: ''
    });
    setPdfDialogOpen(true);
  };

  return (
    <div className="space-y-6" data-testid="brand-identity-admin">
      {/* Header */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#f5a623]/20 flex items-center justify-center">
                <Palette className="h-6 w-6 text-[#f5a623]" />
              </div>
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  Identité Visuelle Bionic™
                  <Badge className="bg-green-500/20 text-green-400">Actif</Badge>
                </CardTitle>
                <CardDescription>
                  Gérez les logos, assets et en-têtes de communication
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => { fetchLogos(); fetchLogoHistory(); }}>
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
          <TabsTrigger value="logos" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Image className="h-4 w-4 mr-2" />Logos
          </TabsTrigger>
          <TabsTrigger value="headers" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <FileText className="h-4 w-4 mr-2" />En-têtes PDF
          </TabsTrigger>
          <TabsTrigger value="history" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <History className="h-4 w-4 mr-2" />Historique
          </TabsTrigger>
        </TabsList>

        {/* Logos Tab */}
        <TabsContent value="logos" className="space-y-6">
          {/* Brand Names Display */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Globe className="h-5 w-5 text-[#f5a623]" />
                Noms Officiels de la Marque
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-background rounded-lg p-4 border border-border">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">🇫🇷</span>
                    <Badge>Français</Badge>
                  </div>
                  <p className="text-2xl font-bold text-[#f5a623]">{BRAND_NAMES.fr.full}</p>
                  <p className="text-gray-400 text-sm mt-1">{BRAND_NAMES.fr.tagline}</p>
                </div>
                <div className="bg-background rounded-lg p-4 border border-border">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">🇬🇧</span>
                    <Badge>English</Badge>
                  </div>
                  <p className="text-2xl font-bold text-[#f5a623]">{BRAND_NAMES.en.full}</p>
                  <p className="text-gray-400 text-sm mt-1">{BRAND_NAMES.en.tagline}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Main Logo */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Image className="h-5 w-5 text-[#f5a623]" />
                Logo Principal
              </CardTitle>
              <CardDescription>
                Logo unifié utilisé pour les deux langues
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-background rounded-lg p-4 border border-border">
                <div className="bg-black rounded-lg p-8 mb-4 flex items-center justify-center">
                  <img 
                    src={LOGO_VARIANTS.main.url} 
                    alt="BIONIC Logo"
                    className="max-h-40 w-auto"
                  />
                </div>
                <p className="text-gray-400 text-sm mb-4 text-center">{LOGO_VARIANTS.main.description}</p>
                <div className="flex gap-2 justify-center">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setPreviewLogo(LOGO_VARIANTS.main)}
                  >
                    <Eye className="h-4 w-4 mr-1" />Aperçu
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => copyToClipboard(LOGO_VARIANTS.main.url)}
                  >
                    <Copy className="h-4 w-4 mr-1" />Copier URL
                  </Button>
                  <Button 
                    size="sm" 
                    className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
                    onClick={() => downloadLogo(LOGO_VARIANTS.main.url, 'bionic-logo-main.png')}
                  >
                    <Download className="h-4 w-4 mr-1" />Télécharger
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Custom Logos */}
          {customLogos.length > 0 && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white text-lg flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-[#f5a623]" />
                  Logos Personnalisés
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {customLogos.map((logo) => (
                    <div key={logo.filename} className="bg-background rounded-lg p-3 border border-border">
                      <div className="bg-black rounded-lg p-4 mb-2 flex items-center justify-center h-24">
                        <img 
                          src={logo.url} 
                          alt={logo.filename}
                          className="max-h-full max-w-full object-contain"
                        />
                      </div>
                      <p className="text-gray-400 text-xs truncate mb-2">{logo.filename}</p>
                      <div className="flex gap-1">
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="flex-1 h-7 text-xs"
                          onClick={() => downloadLogo(logo.url, logo.filename)}
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="h-7 text-xs text-red-400 hover:bg-red-500/10"
                          onClick={() => deleteCustomLogo(logo.filename)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload Section */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Upload className="h-5 w-5 text-[#f5a623]" />
                Uploader un Nouveau Logo
              </CardTitle>
              <CardDescription>
                Ajoutez des logos personnalisés (PNG, JPEG, WebP, SVG - Max 5MB)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <label className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-[#f5a623]/50 transition-colors cursor-pointer block relative">
                  <input 
                    type="file" 
                    className="hidden" 
                    accept=".png,.jpg,.jpeg,.webp,.svg"
                    onChange={(e) => handleLogoUpload(e.target.files[0], 'fr')}
                  />
                  {uploadProgress?.lang === 'fr' ? (
                    <div className="space-y-2">
                      <Loader2 className="h-8 w-8 text-[#f5a623] mx-auto animate-spin" />
                      <p className="text-white font-medium">{uploadProgress.progress}%</p>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                      <p className="text-white font-medium">Logo FR</p>
                      <p className="text-gray-400 text-xs">Glissez ou cliquez pour uploader</p>
                    </>
                  )}
                </label>
                <label className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-[#f5a623]/50 transition-colors cursor-pointer block">
                  <input 
                    type="file" 
                    className="hidden" 
                    accept=".png,.jpg,.jpeg,.webp,.svg"
                    onChange={(e) => handleLogoUpload(e.target.files[0], 'en')}
                  />
                  {uploadProgress?.lang === 'en' ? (
                    <div className="space-y-2">
                      <Loader2 className="h-8 w-8 text-[#f5a623] mx-auto animate-spin" />
                      <p className="text-white font-medium">{uploadProgress.progress}%</p>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                      <p className="text-white font-medium">Logo EN</p>
                      <p className="text-gray-400 text-xs">Drag or click to upload</p>
                    </>
                  )}
                </label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Headers Tab */}
        <TabsContent value="headers" className="space-y-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <FileSignature className="h-5 w-5 text-[#f5a623]" />
                Générateur d'En-têtes PDF
              </CardTitle>
              <CardDescription>
                Créez des documents PDF officiels avec l'en-tête Bionic™
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {DOCUMENT_TEMPLATES.map((template) => {
                  const IconComponent = template.icon;
                  return (
                    <div 
                      key={template.id}
                      className="bg-background rounded-lg p-4 border border-border flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#f5a623]/20 flex items-center justify-center">
                          <IconComponent className="h-5 w-5 text-[#f5a623]" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{template.name}</p>
                          <p className="text-gray-500 text-xs">{template.nameEn}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {/* Quick download buttons */}
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => generateHeader(template.id, 'fr')}
                          disabled={generatingHeader === `${template.id}-fr`}
                        >
                          {generatingHeader === `${template.id}-fr` ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-1" />
                          ) : (
                            <span className="mr-1">🇫🇷</span>
                          )}
                          FR
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => generateHeader(template.id, 'en')}
                          disabled={generatingHeader === `${template.id}-en`}
                        >
                          {generatingHeader === `${template.id}-en` ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-1" />
                          ) : (
                            <span className="mr-1">🇬🇧</span>
                          )}
                          EN
                        </Button>
                        {/* Custom content button */}
                        <Button 
                          size="sm" 
                          className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
                          onClick={() => openPdfDialog(template)}
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          Personnalisé
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* ZEC/Sépaq Notice */}
              <div className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Trees className="h-5 w-5 text-blue-400 mt-0.5" />
                  <div>
                    <p className="text-blue-400 font-medium">Documents Institutionnels</p>
                    <p className="text-gray-400 text-sm mt-1">
                      Les en-têtes pour ZEC, Sépaq, Clubs privés et Pourvoiries incluent automatiquement 
                      les mentions légales requises et le numéro de marque déposée (™).
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Preview Section */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg">Aperçu d'En-tête Type</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-white rounded-lg p-6 text-black">
                {/* Simulated Header */}
                <div className="border-b-2 border-[#f5a623] pb-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <img 
                        src={LOGO_VARIANTS.main.url}
                        alt="Logo"
                        className="h-12 w-auto"
                      />
                    </div>
                    <div className="text-right text-sm">
                      <p className="font-bold text-[#f5a623]">{brand.full}</p>
                      <p className="text-gray-600">www.chassebionic.ca</p>
                      <p className="text-gray-600">info@chassebionic.ca</p>
                    </div>
                  </div>
                </div>
                <div className="text-gray-400 text-xs text-center py-8">
                  [Contenu du document]
                </div>
                <div className="border-t border-gray-200 mt-4 pt-4 text-center text-xs text-gray-500">
                  © 2025 {brand.full} - La science valide ce que le terrain confirme.™
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <History className="h-5 w-5 text-[#f5a623]" />
                Historique des Uploads
              </CardTitle>
            </CardHeader>
            <CardContent>
              {logoHistory.length === 0 ? (
                <p className="text-gray-400 text-center py-8">Aucun historique disponible</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="border-border">
                      <TableHead className="text-gray-400">Fichier</TableHead>
                      <TableHead className="text-gray-400">Langue</TableHead>
                      <TableHead className="text-gray-400">Type</TableHead>
                      <TableHead className="text-gray-400">Date</TableHead>
                      <TableHead className="text-gray-400">Taille</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logoHistory.map((entry, idx) => (
                      <TableRow key={idx} className="border-border">
                        <TableCell className="text-white font-mono text-xs">
                          {entry.filename}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {entry.language === 'fr' ? '🇫🇷 FR' : '🇬🇧 EN'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-gray-400">{entry.logo_type}</TableCell>
                        <TableCell className="text-gray-400">
                          {new Date(entry.uploaded_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="text-gray-400">
                          {entry.file_size ? `${(entry.file_size / 1024).toFixed(1)} KB` : '-'}
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

      {/* Preview Dialog */}
      <Dialog open={!!previewLogo} onOpenChange={() => setPreviewLogo(null)}>
        <DialogContent className="bg-card border-border max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">{previewLogo?.name}</DialogTitle>
            <DialogDescription>{previewLogo?.description}</DialogDescription>
          </DialogHeader>
          <div className="bg-black rounded-lg p-8 flex items-center justify-center">
            {previewLogo && (
              <img 
                src={previewLogo.url}
                alt={previewLogo.name}
                className="max-h-64 w-auto"
              />
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPreviewLogo(null)}>Fermer</Button>
            <Button 
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
              onClick={() => previewLogo && downloadLogo(previewLogo.url, previewLogo.name.replace(/ /g, '-').toLowerCase() + '.png')}
            >
              <Download className="h-4 w-4 mr-2" />Télécharger
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* PDF Generator Dialog */}
      <Dialog open={pdfDialogOpen} onOpenChange={setPdfDialogOpen}>
        <DialogContent className="bg-card border-border max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <FileSignature className="h-5 w-5 text-[#f5a623]" />
              {selectedTemplate?.name}
            </DialogTitle>
            <DialogDescription>
              Personnalisez le contenu de votre document PDF
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label className="text-gray-400">Langue</Label>
              <Select value={pdfForm.language} onValueChange={(v) => setPdfForm({...pdfForm, language: v})}>
                <SelectTrigger className="bg-background border-border mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">🇫🇷 Français</SelectItem>
                  <SelectItem value="en">🇬🇧 English</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-400">Titre (optionnel)</Label>
              <Input
                value={pdfForm.title}
                onChange={(e) => setPdfForm({...pdfForm, title: e.target.value})}
                placeholder="Titre personnalisé du document"
                className="bg-background border-border mt-1"
              />
            </div>
            
            <div>
              <Label className="text-gray-400">Destinataire (optionnel)</Label>
              <Input
                value={pdfForm.recipient_name}
                onChange={(e) => setPdfForm({...pdfForm, recipient_name: e.target.value})}
                placeholder="Nom du destinataire"
                className="bg-background border-border mt-1"
              />
            </div>
            
            <div>
              <Label className="text-gray-400">Adresse (optionnel)</Label>
              <Textarea
                value={pdfForm.recipient_address}
                onChange={(e) => setPdfForm({...pdfForm, recipient_address: e.target.value})}
                placeholder="Adresse complète"
                className="bg-background border-border mt-1 h-20"
              />
            </div>
            
            <div>
              <Label className="text-gray-400">Contenu (optionnel)</Label>
              <Textarea
                value={pdfForm.content}
                onChange={(e) => setPdfForm({...pdfForm, content: e.target.value})}
                placeholder="Contenu principal du document..."
                className="bg-background border-border mt-1 h-32"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setPdfDialogOpen(false)}>
              Annuler
            </Button>
            <Button 
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
              onClick={() => generateHeader(selectedTemplate?.id, pdfForm.language, pdfForm)}
              disabled={generatingHeader}
            >
              {generatingHeader ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Générer PDF
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BrandIdentityAdmin;
