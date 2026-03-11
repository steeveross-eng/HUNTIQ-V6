/**
 * AdminMessaging - Messaging Engine V2 avec modes TOUS/UN PAR UN
 * ==============================================================
 * 
 * Interface complète pour le système de messagerie bilingue Premium BIONIC.
 * 
 * Features:
 * - Mode TOUS: Envoi massif personnalisé
 * - Mode UN PAR UN: Envoi individuel avec validation manuelle
 * - Pré-visuel obligatoire avant envoi
 * - Personnalisation des variables
 * - Journalisation complète
 * 
 * Architecture: LEGO V5-ULTIME
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Mail, Send, Users, User, Eye, Check, X, RefreshCw,
  FileText, CheckCircle, AlertTriangle, Clock, Zap,
  Globe, LayoutTemplate, ChevronRight, Loader2, Shield
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export const AdminMessaging = () => {
  // State
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [affiliates, setAffiliates] = useState([]);
  
  // Send flow state
  const [sendMode, setSendMode] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [currentBatchId, setCurrentBatchId] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(1);
  
  // UI state
  const [actionLoading, setActionLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('compose');

  // Fetch data
  const fetchDashboard = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/dashboard`);
      const data = await response.json();
      if (data.success) {
        setDashboard(data.dashboard);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  }, []);

  const fetchTemplates = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/templates`);
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  }, []);

  const fetchAffiliates = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/affiliate-switch/affiliates?limit=200`);
      const data = await response.json();
      if (data.success || data.affiliates) {
        setAffiliates(data.affiliates || []);
      }
    } catch (error) {
      console.error('Error fetching affiliates:', error);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDashboard(), fetchTemplates(), fetchAffiliates()]);
      setLoading(false);
    };
    loadData();
  }, [fetchDashboard, fetchTemplates, fetchAffiliates]);

  // Reset flow
  const resetFlow = () => {
    setSendMode('');
    setSelectedTemplate('');
    setSelectedRecipients([]);
    setPreviews([]);
    setCurrentBatchId(null);
    setPipelineStep(1);
  };

  // Toggle recipient selection
  const toggleRecipient = (affiliate) => {
    if (sendMode === 'UN_PAR_UN') {
      // Only one at a time for UN_PAR_UN mode
      setSelectedRecipients([affiliate]);
    } else {
      // Multiple for TOUS mode
      const exists = selectedRecipients.find(r => r.affiliate_id === affiliate.affiliate_id);
      if (exists) {
        setSelectedRecipients(selectedRecipients.filter(r => r.affiliate_id !== affiliate.affiliate_id));
      } else {
        setSelectedRecipients([...selectedRecipients, affiliate]);
      }
    }
  };

  // Select all recipients
  const selectAll = () => {
    if (selectedRecipients.length === affiliates.length) {
      setSelectedRecipients([]);
    } else {
      setSelectedRecipients([...affiliates]);
    }
  };

  // Generate preview
  const generatePreview = async () => {
    if (!sendMode) {
      toast.error('Veuillez sélectionner un mode d\'envoi');
      return;
    }
    if (!selectedTemplate) {
      toast.error('Veuillez sélectionner un template');
      return;
    }
    if (selectedRecipients.length === 0) {
      toast.error('Veuillez sélectionner au moins un destinataire');
      return;
    }

    setActionLoading(true);
    try {
      const recipients = selectedRecipients.map(a => ({
        affiliate_id: a.affiliate_id,
        company_name: a.company_name,
        contact_name: a.company_name,
        email: a.email || `contact@${(a.website || '').replace('https://', '').replace('http://', '').split('/')[0]}`,
        category: a.category || '',
        country: a.country || ''
      }));

      const response = await fetch(`${API_URL}/api/v1/messaging/preview/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template: selectedTemplate,
          send_mode: sendMode,
          recipients,
          created_by: 'COPILOT_MAITRE'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setPreviews(data.previews || []);
        setCurrentBatchId(data.batch_id);
        setPipelineStep(4);
        toast.success(`✅ ${data.previews_generated} pré-visuel(s) généré(s)`);
      } else {
        toast.error(data.error || 'Erreur lors de la génération');
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      toast.error('Erreur lors de la génération du pré-visuel');
    } finally {
      setActionLoading(false);
    }
  };

  // Validate preview
  const validatePreview = async (previewId) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/preview/${previewId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_user: 'COPILOT_MAITRE' })
      });

      const data = await response.json();
      
      if (data.success) {
        // Update local state
        setPreviews(previews.map(p => 
          p.preview_id === previewId ? { ...p, validated: true } : p
        ));
        setPipelineStep(5);
        toast.success('✅ Pré-visuel validé');
      }
    } catch (error) {
      toast.error('Erreur lors de la validation');
    } finally {
      setActionLoading(false);
    }
  };

  // Validate all previews
  const validateAllPreviews = async () => {
    if (!currentBatchId) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/batch/${currentBatchId}/validate-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_user: 'COPILOT_MAITRE' })
      });

      const data = await response.json();
      
      if (data.success) {
        setPreviews(previews.map(p => ({ ...p, validated: true })));
        setPipelineStep(5);
        toast.success(`✅ ${data.validated_count} pré-visuels validés`);
      }
    } catch (error) {
      toast.error('Erreur lors de la validation');
    } finally {
      setActionLoading(false);
    }
  };

  // Send one message
  const sendOneMessage = async (previewId) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/send/one`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preview_id: previewId,
          admin_user: 'COPILOT_MAITRE'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setPreviews(previews.map(p => 
          p.preview_id === previewId ? { ...p, sent: true } : p
        ));
        setPipelineStep(7);
        toast.success(`✅ Message envoyé à ${data.recipient}`);
        fetchDashboard();
      } else {
        toast.error(data.error || 'Erreur lors de l\'envoi');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setActionLoading(false);
    }
  };

  // Send all messages
  const sendAllMessages = async () => {
    if (!currentBatchId) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/messaging/send/all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batch_id: currentBatchId,
          admin_user: 'COPILOT_MAITRE'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setPreviews(previews.map(p => ({ ...p, sent: true })));
        setPipelineStep(7);
        toast.success(`✅ ${data.sent_count} messages envoyés`);
        fetchDashboard();
      } else {
        toast.error(data.error || 'Erreur lors de l\'envoi');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setActionLoading(false);
    }
  };

  // Pipeline steps
  const pipelineSteps = [
    { id: 1, name: 'Mode', icon: Zap },
    { id: 2, name: 'Template', icon: LayoutTemplate },
    { id: 3, name: 'Destinataires', icon: Users },
    { id: 4, name: 'Pré-visuel', icon: Eye },
    { id: 5, name: 'Validation', icon: CheckCircle },
    { id: 6, name: 'Envoi', icon: Send },
    { id: 7, name: 'Journalisé', icon: FileText }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="admin-messaging">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Mail className="h-8 w-8 text-[#F5A623]" />
            Messaging Engine V2
          </h2>
          <p className="text-gray-400 mt-1">
            Communications bilingues Premium (FR/EN) avec modes TOUS / UN PAR UN
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            <Globe className="h-3 w-3 mr-1" />
            Bilingue FR/EN
          </Badge>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchDashboard}
            className="border-[#F5A623]/30 text-[#F5A623]"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-[#0a0a15] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Messages Envoyés</p>
                <p className="text-2xl font-bold text-white">
                  {dashboard?.messages?.sent || 0}
                </p>
              </div>
              <Send className="h-8 w-8 text-[#F5A623]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0a0a15] border-blue-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Mode TOUS</p>
                <p className="text-2xl font-bold text-blue-400">
                  {dashboard?.send_modes?.TOUS || 0}
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0a0a15] border-purple-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Mode UN PAR UN</p>
                <p className="text-2xl font-bold text-purple-400">
                  {dashboard?.send_modes?.UN_PAR_UN || 0}
                </p>
              </div>
              <User className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0a0a15] border-yellow-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">En Attente Validation</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {dashboard?.previews?.pending_validation || 0}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[#0a0a15] border border-[#F5A623]/20">
          <TabsTrigger value="compose" className="data-[state=active]:bg-[#F5A623]/20">
            <Mail className="h-4 w-4 mr-2" />
            Composer
          </TabsTrigger>
          <TabsTrigger value="history" className="data-[state=active]:bg-[#F5A623]/20">
            <FileText className="h-4 w-4 mr-2" />
            Historique
          </TabsTrigger>
        </TabsList>

        {/* Compose Tab */}
        <TabsContent value="compose" className="mt-4">
          {/* Pipeline Progress */}
          <Card className="bg-[#0a0a15] border-[#F5A623]/20 mb-6">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Zap className="h-5 w-5 text-[#F5A623]" />
                Pipeline Automatisé
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                {pipelineSteps.map((step, index) => (
                  <React.Fragment key={step.id}>
                    <div className={`flex flex-col items-center ${pipelineStep >= step.id ? 'text-[#F5A623]' : 'text-gray-500'}`}>
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        pipelineStep >= step.id ? 'bg-[#F5A623]/20 border-2 border-[#F5A623]' : 'bg-gray-800 border border-gray-600'
                      }`}>
                        <step.icon className="h-5 w-5" />
                      </div>
                      <span className="text-xs mt-1">{step.name}</span>
                    </div>
                    {index < pipelineSteps.length - 1 && (
                      <ChevronRight className={`h-4 w-4 ${pipelineStep > step.id ? 'text-[#F5A623]' : 'text-gray-600'}`} />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Configuration */}
            <div className="space-y-4">
              {/* Step 1: Mode Selection */}
              <Card className="bg-[#0a0a15] border-[#F5A623]/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-[#F5A623] text-black text-sm flex items-center justify-center font-bold">1</span>
                    Mode d'Envoi
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Sélection obligatoire avant tout envoi
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div 
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      sendMode === 'TOUS' 
                        ? 'border-blue-500 bg-blue-500/10' 
                        : 'border-gray-700 hover:border-gray-500'
                    }`}
                    onClick={() => { setSendMode('TOUS'); setPipelineStep(Math.max(pipelineStep, 1)); }}
                    data-testid="send-mode-tous"
                  >
                    <div className="flex items-center gap-3">
                      <Users className={`h-6 w-6 ${sendMode === 'TOUS' ? 'text-blue-400' : 'text-gray-400'}`} />
                      <div>
                        <p className={`font-medium ${sendMode === 'TOUS' ? 'text-blue-400' : 'text-white'}`}>
                          Envoyer à TOUS
                        </p>
                        <p className="text-gray-500 text-sm">
                          Envoi massif personnalisé (chaque message est unique)
                        </p>
                      </div>
                    </div>
                  </div>

                  <div 
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      sendMode === 'UN_PAR_UN' 
                        ? 'border-purple-500 bg-purple-500/10' 
                        : 'border-gray-700 hover:border-gray-500'
                    }`}
                    onClick={() => { setSendMode('UN_PAR_UN'); setSelectedRecipients([]); setPipelineStep(Math.max(pipelineStep, 1)); }}
                    data-testid="send-mode-un-par-un"
                  >
                    <div className="flex items-center gap-3">
                      <User className={`h-6 w-6 ${sendMode === 'UN_PAR_UN' ? 'text-purple-400' : 'text-gray-400'}`} />
                      <div>
                        <p className={`font-medium ${sendMode === 'UN_PAR_UN' ? 'text-purple-400' : 'text-white'}`}>
                          Envoyer UN PAR UN
                        </p>
                        <p className="text-gray-500 text-sm">
                          Sélection manuelle, validation individuelle
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Step 2: Template Selection */}
              <Card className="bg-[#0a0a15] border-[#F5A623]/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-[#F5A623] text-black text-sm flex items-center justify-center font-bold">2</span>
                    Template Bilingue
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Select 
                    value={selectedTemplate} 
                    onValueChange={(v) => { setSelectedTemplate(v); setPipelineStep(Math.max(pipelineStep, 2)); }}
                  >
                    <SelectTrigger className="bg-[#0f0f1a] border-gray-700 text-white" data-testid="template-select">
                      <SelectValue placeholder="Sélectionner un template" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0f0f1a] border-gray-700">
                      {templates.map(t => (
                        <SelectItem key={t.id} value={t.id} className="text-white hover:bg-[#F5A623]/20">
                          <div className="flex items-center gap-2">
                            <LayoutTemplate className="h-4 w-4 text-[#F5A623]" />
                            <span>{t.name_fr}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {selectedTemplate && (
                    <div className="mt-3 p-3 bg-[#0f0f1a] rounded border border-gray-700">
                      <p className="text-gray-400 text-xs mb-2">Variables disponibles:</p>
                      <div className="flex flex-wrap gap-1">
                        {templates.find(t => t.id === selectedTemplate)?.variables?.map(v => (
                          <Badge key={v} variant="outline" className="text-xs bg-[#F5A623]/10 text-[#F5A623] border-[#F5A623]/30">
                            {`{{${v}}}`}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Step 3: Recipients */}
              <Card className="bg-[#0a0a15] border-[#F5A623]/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-[#F5A623] text-black text-sm flex items-center justify-center font-bold">3</span>
                    Destinataires ({selectedRecipients.length})
                  </CardTitle>
                  {sendMode === 'TOUS' && (
                    <Button variant="ghost" size="sm" onClick={selectAll} className="text-[#F5A623]">
                      {selectedRecipients.length === affiliates.length ? 'Désélectionner tout' : 'Sélectionner tout'}
                    </Button>
                  )}
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-48">
                    <div className="space-y-2">
                      {affiliates.map(affiliate => (
                        <div 
                          key={affiliate.affiliate_id}
                          className={`flex items-center gap-3 p-2 rounded cursor-pointer transition-all ${
                            selectedRecipients.find(r => r.affiliate_id === affiliate.affiliate_id)
                              ? 'bg-[#F5A623]/20 border border-[#F5A623]/50'
                              : 'bg-[#0f0f1a] border border-transparent hover:border-gray-600'
                          }`}
                          onClick={() => { toggleRecipient(affiliate); setPipelineStep(Math.max(pipelineStep, 3)); }}
                        >
                          <Checkbox 
                            checked={!!selectedRecipients.find(r => r.affiliate_id === affiliate.affiliate_id)}
                            className="border-gray-600"
                          />
                          <div className="flex-1">
                            <p className="text-white text-sm">{affiliate.company_name}</p>
                            <p className="text-gray-500 text-xs">{affiliate.category}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* Generate Preview Button */}
              <Button 
                onClick={generatePreview}
                disabled={!sendMode || !selectedTemplate || selectedRecipients.length === 0 || actionLoading}
                className="w-full bg-[#F5A623] hover:bg-[#F5A623]/80 text-black"
                data-testid="generate-preview-btn"
              >
                {actionLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Eye className="h-4 w-4 mr-2" />
                )}
                Générer Pré-visuel (Étape 4)
              </Button>
            </div>

            {/* Right: Preview & Actions */}
            <div className="space-y-4">
              {previews.length > 0 ? (
                <>
                  {/* Preview Display */}
                  <Card className="bg-[#0a0a15] border-green-500/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Eye className="h-5 w-5 text-green-400" />
                        Pré-visuel FR/EN
                        <Badge className="ml-2 bg-green-500/20 text-green-400 border-green-500/30">
                          OBLIGATOIRE
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-96">
                        {previews.map((preview, idx) => (
                          <div key={preview.preview_id || idx} className="mb-4 p-3 bg-[#0f0f1a] rounded border border-gray-700">
                            <div className="flex items-center justify-between mb-2">
                              <p className="text-white font-medium">
                                {preview.recipient?.company_name}
                              </p>
                              <div className="flex items-center gap-2">
                                {preview.validated ? (
                                  <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                    <Check className="h-3 w-3 mr-1" />
                                    Validé
                                  </Badge>
                                ) : (
                                  <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                                    <Clock className="h-3 w-3 mr-1" />
                                    En attente
                                  </Badge>
                                )}
                                {preview.sent && (
                                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                                    <Send className="h-3 w-3 mr-1" />
                                    Envoyé
                                  </Badge>
                                )}
                              </div>
                            </div>

                            {/* FR Preview */}
                            <div className="mb-2">
                              <p className="text-[#F5A623] text-xs mb-1">🇫🇷 VERSION FRANÇAISE</p>
                              <pre className="text-gray-300 text-xs bg-[#1a1a2e] p-2 rounded overflow-x-auto whitespace-pre-wrap">
                                {preview.fr_preview?.substring(0, 500)}...
                              </pre>
                            </div>

                            {/* EN Preview */}
                            <div className="mb-3">
                              <p className="text-[#F5A623] text-xs mb-1">🇺🇸 ENGLISH VERSION</p>
                              <pre className="text-gray-300 text-xs bg-[#1a1a2e] p-2 rounded overflow-x-auto whitespace-pre-wrap">
                                {preview.en_preview?.substring(0, 500)}...
                              </pre>
                            </div>

                            {/* Actions */}
                            {!preview.sent && (
                              <div className="flex gap-2">
                                {!preview.validated && (
                                  <Button 
                                    size="sm"
                                    onClick={() => validatePreview(preview.preview_id)}
                                    disabled={actionLoading}
                                    className="bg-green-600 hover:bg-green-700 text-white"
                                  >
                                    <Check className="h-3 w-3 mr-1" />
                                    Valider
                                  </Button>
                                )}
                                {preview.validated && sendMode === 'UN_PAR_UN' && (
                                  <Button 
                                    size="sm"
                                    onClick={() => sendOneMessage(preview.preview_id)}
                                    disabled={actionLoading}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                  >
                                    <Send className="h-3 w-3 mr-1" />
                                    Envoyer
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </ScrollArea>
                    </CardContent>
                  </Card>

                  {/* Batch Actions (TOUS mode) */}
                  {sendMode === 'TOUS' && (
                    <Card className="bg-[#0a0a15] border-[#F5A623]/20">
                      <CardContent className="p-4">
                        <div className="flex gap-3">
                          {!previews.every(p => p.validated) && (
                            <Button 
                              onClick={validateAllPreviews}
                              disabled={actionLoading}
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                              data-testid="validate-all-btn"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Valider TOUS ({previews.filter(p => !p.validated).length})
                            </Button>
                          )}
                          {previews.every(p => p.validated) && !previews.every(p => p.sent) && (
                            <Button 
                              onClick={sendAllMessages}
                              disabled={actionLoading}
                              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                              data-testid="send-all-btn"
                            >
                              <Send className="h-4 w-4 mr-2" />
                              Envoyer TOUS ({previews.filter(p => !p.sent).length})
                            </Button>
                          )}
                          <Button 
                            variant="outline"
                            onClick={resetFlow}
                            className="border-gray-600 text-gray-400"
                          >
                            <X className="h-4 w-4 mr-2" />
                            Annuler
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </>
              ) : (
                <Card className="bg-[#0a0a15] border-gray-700 h-full flex items-center justify-center">
                  <CardContent className="text-center py-16">
                    <Eye className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 text-lg">Pré-visuel</p>
                    <p className="text-gray-500 text-sm mt-2">
                      Sélectionnez un mode, un template et des destinataires<br />
                      pour générer le pré-visuel obligatoire
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Warning */}
              <Card className="bg-yellow-500/10 border-yellow-500/30">
                <CardContent className="p-4 flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-yellow-400 font-medium">Zéro envoi sans pré-visuel</p>
                    <p className="text-gray-400 text-sm">
                      Conformément aux directives BIONIC, aucun message ne peut être envoyé sans pré-visuel généré et validé manuellement.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="mt-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardHeader>
              <CardTitle className="text-white">Messages Envoyés</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboard?.recent_messages?.length > 0 ? (
                <div className="space-y-3">
                  {dashboard.recent_messages.map((msg, idx) => (
                    <div key={msg.message_id || idx} className="p-3 bg-[#0f0f1a] rounded border border-gray-700">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {msg.send_mode === 'TOUS' ? (
                            <Users className="h-5 w-5 text-blue-400" />
                          ) : (
                            <User className="h-5 w-5 text-purple-400" />
                          )}
                          <div>
                            <p className="text-white">{msg.recipient?.company_name}</p>
                            <p className="text-gray-500 text-xs">{msg.template}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={msg.send_mode === 'TOUS' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-purple-500/20 text-purple-400 border-purple-500/30'}>
                            {msg.send_mode}
                          </Badge>
                          <p className="text-gray-500 text-xs mt-1">
                            {new Date(msg.sent_at).toLocaleString('fr-CA')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Aucun message envoyé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminMessaging;
