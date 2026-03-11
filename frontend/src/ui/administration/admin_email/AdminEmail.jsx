/**
 * AdminEmail - Administration des emails et templates
 * ===================================================
 * 
 * Module V5-ULTIME - Phase 5 Migration
 * Gestion des templates email, variables dynamiques, tests et historique.
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
  Mail,
  FileText,
  Send,
  Settings,
  RefreshCw,
  Loader2,
  CheckCircle,
  AlertCircle,
  XCircle,
  Eye,
  Edit,
  Trash2,
  PlusCircle,
  Clock,
  BarChart3,
  Variable,
  History
} from 'lucide-react';
import { toast } from 'sonner';
import AdminService from '../AdminService';

const AdminEmail = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [variables, setVariables] = useState({ system: [], custom: [] });
  const [logs, setLogs] = useState([]);
  const [config, setConfig] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Modal states
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [testEmail, setTestEmail] = useState('');
  const [sendingTest, setSendingTest] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [statsRes, templatesRes, variablesRes, logsRes, configRes] = await Promise.all([
        AdminService.emailGetDashboard(),
        AdminService.emailGetTemplates(),
        AdminService.emailGetVariables(),
        AdminService.emailGetLogs(),
        AdminService.emailGetConfig()
      ]);
      
      if (statsRes.success) setStats(statsRes.stats);
      if (templatesRes.success) setTemplates(templatesRes.templates || []);
      if (variablesRes.success) setVariables({
        system: variablesRes.system_variables || [],
        custom: variablesRes.custom_variables || []
      });
      if (logsRes.success) setLogs(logsRes.logs || []);
      if (configRes.success) setConfig(configRes.config);
    } catch (error) {
      console.error('Error loading email data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleToggleTemplate = async (templateId, currentState) => {
    try {
      const result = await AdminService.emailToggleTemplate(templateId, !currentState);
      if (result.success) {
        toast.success(!currentState ? 'Template activé' : 'Template désactivé');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleSendTest = async () => {
    if (!testEmail || !selectedTemplate) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }
    
    setSendingTest(true);
    try {
      const result = await AdminService.emailSendTest(selectedTemplate.id, testEmail);
      if (result.success) {
        toast.success(`Email de test envoyé à ${testEmail}!`);
        setTestDialogOpen(false);
        setTestEmail('');
        loadData();
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setSendingTest(false);
    }
  };

  const openTestDialog = (template) => {
    setSelectedTemplate(template);
    setTestDialogOpen(true);
  };

  const getStatusBadge = (status) => {
    const variants = {
      delivered: 'bg-green-500/20 text-green-400',
      sent: 'bg-blue-500/20 text-blue-400',
      bounced: 'bg-red-500/20 text-red-400',
      failed: 'bg-red-600/20 text-red-500',
      simulated: 'bg-yellow-500/20 text-yellow-400'
    };
    return <Badge className={variants[status] || 'bg-gray-500/20'}>{status}</Badge>;
  };

  const getCategoryBadge = (category) => {
    const variants = {
      transactional: 'bg-blue-500/20 text-blue-400',
      notification: 'bg-purple-500/20 text-purple-400',
      marketing: 'bg-pink-500/20 text-pink-400'
    };
    return <Badge className={variants[category] || 'bg-gray-500/20'}>{category}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-email" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mail className="h-6 w-6 text-blue-500" />
            Gestion des Emails
          </h2>
          <p className="text-gray-400">Templates email, variables et historique d'envoi</p>
        </div>
        <Button variant="outline" onClick={loadData} data-testid="refresh-email">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Configuration Status Alert */}
      {config && !config.is_configured && (
        <Card className="bg-yellow-500/10 border-yellow-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <div>
                <p className="text-yellow-400 font-medium">Service email non configuré</p>
                <p className="text-gray-400 text-sm">Ajoutez RESEND_API_KEY dans le fichier .env pour activer l'envoi d'emails</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[#0a0a15]">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="variables">Variables</TabsTrigger>
          <TabsTrigger value="logs">Historique</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {stats && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Templates actifs</p>
                        <p className="text-xl font-bold text-white">{stats.templates?.active || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                        <Send className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Emails envoyés</p>
                        <p className="text-xl font-bold text-white">{stats.sending?.total || 0}</p>
                        <p className="text-xs text-green-400">+{stats.sending?.today || 0} aujourd'hui</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <CheckCircle className="h-5 w-5 text-purple-500" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Taux de livraison</p>
                        <p className="text-xl font-bold text-white">{stats.delivery?.delivery_rate || 0}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                        <Eye className="h-5 w-5 text-[#f5a623]" />
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">Taux d'ouverture</p>
                        <p className="text-xl font-bold text-white">{stats.engagement?.open_rate || 0}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-blue-500" />
                      Emails par catégorie
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(stats.by_category || {}).map(([category, count]) => (
                        <div key={category} className="flex items-center justify-between">
                          {getCategoryBadge(category)}
                          <span className="text-white font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Settings className="h-5 w-5 text-gray-400" />
                      Configuration du service
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Provider</span>
                        <Badge variant="outline">{stats.config?.provider || 'Resend'}</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Email expéditeur</span>
                        <span className="text-white text-sm font-mono">{stats.config?.sender_email}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Statut</span>
                        {stats.config?.service_configured ? (
                          <Badge className="bg-green-500/20 text-green-400">Configuré</Badge>
                        ) : (
                          <Badge className="bg-red-500/20 text-red-400">Non configuré</Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Templates Email</CardTitle>
              <CardDescription>Gérer les modèles d'emails automatiques</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Nom</TableHead>
                    <TableHead className="text-gray-400">Sujet</TableHead>
                    <TableHead className="text-gray-400">Catégorie</TableHead>
                    <TableHead className="text-gray-400">Variables</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                    <TableHead className="text-gray-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {templates.map((template) => (
                    <TableRow key={template.id}>
                      <TableCell className="text-white font-medium">{template.name}</TableCell>
                      <TableCell className="text-gray-400 max-w-xs truncate">{template.subject}</TableCell>
                      <TableCell>{getCategoryBadge(template.category)}</TableCell>
                      <TableCell className="text-gray-400">{template.variables?.length || 0} vars</TableCell>
                      <TableCell>
                        {template.is_active ? (
                          <Badge className="bg-green-500/20 text-green-400">Actif</Badge>
                        ) : (
                          <Badge className="bg-gray-500/20 text-gray-400">Inactif</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openTestDialog(template)}
                            title="Envoyer un test"
                          >
                            <Send className="h-4 w-4 text-blue-400" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleToggleTemplate(template.id, template.is_active)}
                            title={template.is_active ? 'Désactiver' : 'Activer'}
                          >
                            {template.is_active ? (
                              <XCircle className="h-4 w-4 text-red-400" />
                            ) : (
                              <CheckCircle className="h-4 w-4 text-green-400" />
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {templates.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun template trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Variables Tab */}
        <TabsContent value="variables">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Variable className="h-5 w-5 text-purple-500" />
                Variables disponibles
              </CardTitle>
              <CardDescription>Variables utilisables dans les templates avec la syntaxe {'{{variable}}'}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-white font-semibold mb-4">Variables système</h3>
                  <div className="space-y-2">
                    {variables.system.map((v, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                        <div>
                          <code className="text-purple-400 text-sm">{`{{${v.name}}}`}</code>
                          <p className="text-gray-400 text-xs">{v.description}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">{v.category}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-white font-semibold mb-4">Variables personnalisées</h3>
                  {variables.custom.length === 0 ? (
                    <div className="text-center py-8 bg-gray-900/30 rounded-lg">
                      <p className="text-gray-500">Aucune variable personnalisée</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {variables.custom.map((v, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                          <code className="text-green-400 text-sm">{`{{${v.name}}}`}</code>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <History className="h-5 w-5 text-gray-400" />
                Historique des envois
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-gray-400">Destinataire</TableHead>
                    <TableHead className="text-gray-400">Template</TableHead>
                    <TableHead className="text-gray-400">Sujet</TableHead>
                    <TableHead className="text-gray-400">Date</TableHead>
                    <TableHead className="text-gray-400">Statut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.slice(0, 20).map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="text-white">{log.recipient}</TableCell>
                      <TableCell className="text-gray-400">{log.template_id}</TableCell>
                      <TableCell className="text-gray-400 max-w-xs truncate">{log.subject}</TableCell>
                      <TableCell className="text-gray-400">
                        {log.sent_at ? new Date(log.sent_at).toLocaleString('fr-CA') : '-'}
                      </TableCell>
                      <TableCell>{getStatusBadge(log.status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {logs.length === 0 && (
                <p className="text-center text-gray-500 py-8">Aucun email envoyé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Config Tab */}
        <TabsContent value="config">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuration du service email
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {config && (
                <>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-900/50 rounded-lg">
                      <Label className="text-gray-400">Provider</Label>
                      <p className="text-white font-medium mt-1">{config.provider || 'Resend'}</p>
                    </div>
                    <div className="p-4 bg-gray-900/50 rounded-lg">
                      <Label className="text-gray-400">Email expéditeur</Label>
                      <p className="text-white font-mono text-sm mt-1">{config.sender_email || 'Non configuré'}</p>
                    </div>
                    <div className="p-4 bg-gray-900/50 rounded-lg">
                      <Label className="text-gray-400">Limite journalière</Label>
                      <p className="text-white font-medium mt-1">{config.daily_limit || 1000} emails/jour</p>
                    </div>
                    <div className="p-4 bg-gray-900/50 rounded-lg">
                      <Label className="text-gray-400">Rate limit</Label>
                      <p className="text-white font-medium mt-1">{config.rate_limit_per_minute || 60}/minute</p>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                    <p className="text-blue-400 text-sm">
                      <AlertCircle className="h-4 w-4 inline mr-2" />
                      Pour modifier la configuration email, mettez à jour les variables d'environnement dans le fichier .env du backend.
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Test Email Dialog */}
      <Dialog open={testDialogOpen} onOpenChange={setTestDialogOpen}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-white">Envoyer un email de test</DialogTitle>
            <DialogDescription>
              {selectedTemplate?.name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label className="text-gray-400">Adresse email</Label>
              <Input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="test@exemple.com"
                className="bg-background border-border mt-1"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setTestDialogOpen(false)}>
              Annuler
            </Button>
            <Button 
              onClick={handleSendTest}
              disabled={sendingTest}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
            >
              {sendingTest ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Envoyer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminEmail;
