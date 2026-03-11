/**
 * MaintenanceControl - SECURE admin component for managing maintenance mode
 * - Password-protected toggle ON/OFF
 * - Persistent storage in MongoDB
 * - Audit logging of all actions
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Shield,
  ShieldOff,
  Lock,
  Unlock,
  AlertTriangle,
  CheckCircle,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  Clock,
  Mail,
  Loader2,
  Power,
  PowerOff,
  History,
  Key,
  Trash2
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MaintenanceControl = () => {
  const { t } = useLanguage();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);
  
  // Password state
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [pendingAction, setPendingAction] = useState(null); // 'toggle' | 'update' | 'revoke'
  
  // Form state
  const [formData, setFormData] = useState({
    message: '',
    show_progress: true,
    progress_percent: 0,
    estimated_completion: '',
    contact_email: ''
  });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/maintenance/status`);
      setConfig(response.data);
      setFormData({
        message: response.data.message || '',
        show_progress: response.data.show_progress ?? true,
        progress_percent: response.data.progress_percent || 0,
        estimated_completion: response.data.estimated_completion || '',
        contact_email: response.data.contact_email || ''
      });
    } catch (error) {
      console.error('Error loading config:', error);
      toast.error('Erreur lors du chargement de la configuration');
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async (password) => {
    try {
      setLogsLoading(true);
      const response = await axios.get(`${API}/maintenance/logs`, {
        params: { admin_password: password, limit: 50 }
      });
      if (response.data.success) {
        setLogs(response.data.logs);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
    } finally {
      setLogsLoading(false);
    }
  };

  const handleToggleMaintenance = () => {
    setPendingAction('toggle');
    setShowPasswordDialog(true);
  };

  const handleUpdateSettings = () => {
    setPendingAction('update');
    setShowPasswordDialog(true);
  };

  const handleRevokeTokens = () => {
    setPendingAction('revoke');
    setShowPasswordDialog(true);
  };

  const executeAction = async () => {
    if (!adminPassword.trim()) {
      toast.error('Mot de passe requis');
      return;
    }

    setSaving(true);
    try {
      if (pendingAction === 'toggle') {
        const response = await axios.post(`${API}/maintenance/toggle`, {
          admin_password: adminPassword,
          activate: !config?.is_active,
          message: formData.message || undefined,
          progress_percent: formData.progress_percent,
          estimated_completion: formData.estimated_completion || undefined
        });
        
        if (response.data.success) {
          toast.success(response.data.message);
          await loadConfig();
          loadLogs(adminPassword);
        }
      } else if (pendingAction === 'update') {
        const response = await axios.post(`${API}/maintenance/update`, {
          admin_password: adminPassword,
          ...formData
        });
        
        if (response.data.success) {
          toast.success('Paramètres mis à jour');
          await loadConfig();
        }
      } else if (pendingAction === 'revoke') {
        const response = await axios.post(`${API}/maintenance/revoke-all-tokens`, {
          admin_password: adminPassword
        });
        
        if (response.data.success) {
          toast.success('Tous les tokens révoqués');
          loadLogs(adminPassword);
        }
      }
      
      setShowPasswordDialog(false);
      setAdminPassword('');
      setPendingAction(null);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur';
      toast.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('fr-CA');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  const isActive = config?.is_active;

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card className={`border-2 ${isActive ? 'border-red-500/50 bg-red-500/5' : 'border-green-500/50 bg-green-500/5'}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                isActive ? 'bg-red-500/20' : 'bg-green-500/20'
              }`}>
                {isActive ? (
                  <ShieldOff className="h-8 w-8 text-red-400" />
                ) : (
                  <Shield className="h-8 w-8 text-green-400" />
                )}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  Mode Maintenance
                  <Badge className={`ml-2 ${isActive 
                    ? 'bg-red-500/20 text-red-400 border-red-500/50' 
                    : 'bg-green-500/20 text-green-400 border-green-500/50'
                  }`}>
                    {isActive ? '🔒 ACTIVÉ' : '🔓 DÉSACTIVÉ'}
                  </Badge>
                </h2>
                <p className="text-gray-400 mt-1">
                  {isActive 
                    ? 'Le site est actuellement en maintenance. Seuls les administrateurs avec mot de passe peuvent y accéder.'
                    : 'Le site est accessible à tous les visiteurs.'}
                </p>
                {isActive && config?.activated_at && (
                  <p className="text-gray-500 text-sm mt-1">
                    Activé le {formatDate(config.activated_at)}
                  </p>
                )}
              </div>
            </div>
            
            <Button
              size="lg"
              onClick={handleToggleMaintenance}
              className={isActive 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-red-600 hover:bg-red-700 text-white'
              }
            >
              {isActive ? (
                <>
                  <Power className="h-5 w-5 mr-2" />
                  Désactiver Maintenance
                </>
              ) : (
                <>
                  <PowerOff className="h-5 w-5 mr-2" />
                  Activer Maintenance
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Security Notice */}
      <Card className="bg-yellow-500/10 border-yellow-500/30">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5" />
            <div>
              <h4 className="text-yellow-400 font-semibold">Sécurité Persistante</h4>
              <p className="text-gray-400 text-sm mt-1">
                Le mode maintenance est <strong className="text-yellow-400">100% persistant</strong> et stocké en base de données. 
                Il reste actif jusqu'à désactivation explicite avec le mot de passe administrateur, 
                même après fermeture du navigateur ou redémarrage du serveur.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings Form */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-[#f5a623]" />
            Paramètres de Maintenance
          </CardTitle>
          <CardDescription>
            Configurez le message et la progression affichés aux visiteurs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="message" className="text-gray-300">Message affiché</Label>
            <Textarea
              id="message"
              value={formData.message}
              onChange={(e) => setFormData(f => ({ ...f, message: e.target.value }))}
              placeholder="🚧 Site en maintenance. Nous revenons bientôt!"
              className="bg-background"
              rows={3}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label className="text-gray-300">Afficher la progression</Label>
              <p className="text-gray-500 text-xs">Barre de progression visible</p>
            </div>
            <Switch
              checked={formData.show_progress}
              onCheckedChange={(c) => setFormData(f => ({ ...f, show_progress: c }))}
            />
          </div>

          {formData.show_progress && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-gray-300">Progression</Label>
                <span className="text-[#f5a623] font-semibold">{formData.progress_percent}%</span>
              </div>
              <Slider
                value={[formData.progress_percent]}
                onValueChange={(v) => setFormData(f => ({ ...f, progress_percent: v[0] }))}
                max={100}
                step={5}
                className="py-2"
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="estimated" className="text-gray-300">Disponibilité estimée</Label>
            <Input
              id="estimated"
              value={formData.estimated_completion}
              onChange={(e) => setFormData(f => ({ ...f, estimated_completion: e.target.value }))}
              placeholder="Ex: 15 janvier 2026 à 18h00"
              className="bg-background"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-gray-300">Email de contact</Label>
            <Input
              id="email"
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFormData(f => ({ ...f, contact_email: e.target.value }))}
              placeholder="contact@bionic.ca"
              className="bg-background"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button 
              onClick={handleUpdateSettings}
              className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
            >
              <Save className="h-4 w-4 mr-2" />
              Sauvegarder les paramètres
            </Button>
            <Button 
              variant="outline"
              onClick={loadConfig}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Token Management */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Key className="h-5 w-5 text-purple-400" />
            Gestion des Tokens d'Accès
          </CardTitle>
          <CardDescription>
            Les tokens permettent aux administrateurs d'accéder au site pendant la maintenance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            variant="destructive"
            onClick={handleRevokeTokens}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Révoquer tous les tokens
          </Button>
          <p className="text-gray-500 text-xs mt-2">
            Force tous les administrateurs à se reconnecter avec le mot de passe
          </p>
        </CardContent>
      </Card>

      {/* Audit Logs */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <History className="h-5 w-5 text-blue-400" />
            Journal d'Audit
          </CardTitle>
          <CardDescription>
            Historique des actions sur le mode maintenance
          </CardDescription>
        </CardHeader>
        <CardContent>
          {logs.length > 0 ? (
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {logs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-2 rounded bg-background">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      log.action.includes('FAILED') ? 'bg-red-500' : 'bg-green-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{log.action}</p>
                      <p className="text-gray-500 text-xs">{formatDate(log.timestamp)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          ) : (
            <p className="text-gray-500 text-sm">
              Entrez le mot de passe admin pour voir les logs
            </p>
          )}
        </CardContent>
      </Card>

      {/* Password Dialog */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white">
              <Lock className="h-5 w-5 text-[#f5a623]" />
              Confirmation Administrateur
            </DialogTitle>
            <DialogDescription>
              {pendingAction === 'toggle' && (
                isActive 
                  ? 'Entrez le mot de passe pour DÉSACTIVER le mode maintenance.'
                  : 'Entrez le mot de passe pour ACTIVER le mode maintenance.'
              )}
              {pendingAction === 'update' && 'Entrez le mot de passe pour sauvegarder les paramètres.'}
              {pendingAction === 'revoke' && 'Entrez le mot de passe pour révoquer tous les tokens.'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-gray-300">Mot de passe administrateur</Label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  placeholder="••••••••"
                  className="bg-background pr-10"
                  onKeyDown={(e) => e.key === 'Enter' && executeAction()}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowPasswordDialog(false);
                setAdminPassword('');
                setPendingAction(null);
              }}
            >
              Annuler
            </Button>
            <Button
              onClick={executeAction}
              disabled={saving || !adminPassword.trim()}
              className={pendingAction === 'toggle' && !isActive 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-[#f5a623] hover:bg-[#f5a623]/90 text-black'
              }
            >
              {saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Traitement...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Confirmer
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MaintenanceControl;
