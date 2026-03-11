/**
 * SiteAccessControl - Admin component for managing site access
 * - Auto-syncs with Feature Controls when entering/exiting maintenance mode
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
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Globe,
  Lock,
  Unlock,
  Construction,
  Wrench,
  CheckCircle,
  AlertTriangle,
  Save,
  RefreshCw,
  Shield,
  Eye,
  Clock,
  Mail,
  Loader2,
  Power,
  PowerOff,
  Zap,
  ZapOff,
  Info
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SiteAccessControl = () => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newIp, setNewIp] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    mode: 'live',
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
      const response = await axios.get(`${API}/site/config`);
      setConfig(response.data);
      setFormData({
        mode: response.data.mode || 'live',
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

  const handleModeChange = async (newMode) => {
    setSaving(true);
    try {
      const response = await axios.put(`${API}/site/mode`, {
        mode: newMode,
        message: formData.message,
        show_progress: formData.show_progress,
        progress_percent: formData.progress_percent,
        estimated_completion: formData.estimated_completion,
        contact_email: formData.contact_email
      });
      
      setFormData(prev => ({ ...prev, mode: newMode }));
      
      const modeLabels = {
        live: 'Site en ligne',
        development: 'Mode développement activé',
        maintenance: 'Mode maintenance activé'
      };
      
      // Show main toast
      toast.success(modeLabels[newMode]);
      
      // Show feature sync toast if applicable
      if (response.data.features_sync) {
        const { action, count, message } = response.data.features_sync;
        setTimeout(() => {
          if (action === 'disabled') {
            toast.warning(`${message}`, {
              description: 'Toutes les actions sont bloquées pendant la maintenance',
              duration: 5000
            });
          } else if (action === 'restored') {
            toast.success(`${message}`, {
              description: 'Les fonctionnalités ont été restaurées à leur état précédent',
              duration: 5000
            });
          }
        }, 500);
      }
      
      loadConfig();
    } catch (error) {
      toast.error('Erreur lors du changement de mode');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/site/mode`, formData);
      toast.success('Paramètres sauvegardés!');
      loadConfig();
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleAddIp = async () => {
    if (!newIp) return;
    try {
      await axios.post(`${API}/site/add-allowed-ip?ip=${encodeURIComponent(newIp)}`);
      toast.success(`IP ${newIp} ajoutée`);
      setNewIp('');
      loadConfig();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout de l\'IP');
    }
  };

  const handleRemoveIp = async (ip) => {
    try {
      await axios.delete(`${API}/site/remove-allowed-ip?ip=${encodeURIComponent(ip)}`);
      toast.success(`IP ${ip} retirée`);
      loadConfig();
    } catch (error) {
      toast.error('Erreur lors du retrait de l\'IP');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  const getModeIcon = (mode) => {
    switch (mode) {
      case 'live': return <Globe className="h-5 w-5" />;
      case 'development': return <Construction className="h-5 w-5" />;
      case 'maintenance': return <Wrench className="h-5 w-5" />;
      default: return <Globe className="h-5 w-5" />;
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case 'live': return 'bg-green-500/20 text-green-400 border-green-500';
      case 'development': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500';
      case 'maintenance': return 'bg-red-500/20 text-red-400 border-red-500';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Status Banner */}
      <Card className={`border-2 ${
        formData.mode === 'live' 
          ? 'border-green-500/50 bg-green-500/5' 
          : formData.mode === 'development'
            ? 'border-yellow-500/50 bg-yellow-500/5'
            : 'border-red-500/50 bg-red-500/5'
      }`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getModeColor(formData.mode)}`}>
                {getModeIcon(formData.mode)}
              </div>
              <div>
                <h3 className="text-white font-semibold text-lg">État actuel du site</h3>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={getModeColor(formData.mode)}>
                    {formData.mode === 'live' && 'En ligne'}
                    {formData.mode === 'development' && 'En développement'}
                    {formData.mode === 'maintenance' && 'En maintenance'}
                  </Badge>
                  {config?.updated_at && (
                    <span className="text-gray-500 text-xs">
                      Modifié: {new Date(config.updated_at).toLocaleString('fr-CA')}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {/* Quick Toggle */}
            <div className="flex items-center gap-2">
              {formData.mode !== 'live' ? (
                <Button 
                  onClick={() => handleModeChange('live')}
                  className="bg-green-600 hover:bg-green-700"
                  disabled={saving}
                >
                  <Power className="h-4 w-4 mr-2" />
                  Mettre en ligne
                </Button>
              ) : (
                <Button 
                  onClick={() => handleModeChange('development')}
                  variant="outline"
                  className="border-yellow-500 text-yellow-400 hover:bg-yellow-500/10"
                  disabled={saving}
                >
                  <PowerOff className="h-4 w-4 mr-2" />
                  Passer en développement
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mode Selection */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-[#f5a623]" />
            Mode du site
          </CardTitle>
          <CardDescription>
            Contrôlez l'accessibilité de votre site
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Live Mode */}
            <button
              onClick={() => handleModeChange('live')}
              disabled={saving}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                formData.mode === 'live'
                  ? 'border-green-500 bg-green-500/10'
                  : 'border-border hover:border-green-500/50'
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Unlock className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <h4 className="text-white font-medium">En ligne</h4>
                  <p className="text-green-400 text-xs">Accessible à tous</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm">
                Le site est accessible à tous les visiteurs sans restriction.
              </p>
            </button>

            {/* Development Mode */}
            <button
              onClick={() => handleModeChange('development')}
              disabled={saving}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                formData.mode === 'development'
                  ? 'border-yellow-500 bg-yellow-500/10'
                  : 'border-border hover:border-yellow-500/50'
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <Construction className="h-5 w-5 text-yellow-400" />
                </div>
                <div>
                  <h4 className="text-white font-medium">Développement</h4>
                  <p className="text-yellow-400 text-xs">Accès limité</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm">
                Affiche une page "En développement" aux visiteurs.
              </p>
            </button>

            {/* Maintenance Mode */}
            <button
              onClick={() => handleModeChange('maintenance')}
              disabled={saving}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                formData.mode === 'maintenance'
                  ? 'border-red-500 bg-red-500/10'
                  : 'border-border hover:border-red-500/50'
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                  <Lock className="h-5 w-5 text-red-400" />
                </div>
                <div>
                  <h4 className="text-white font-medium">Maintenance</h4>
                  <p className="text-red-400 text-xs">Site bloqué</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm">
                Affiche une page de maintenance urgente.
              </p>
              {/* Warning about feature sync */}
              <div className="mt-2 flex items-center gap-1 text-xs text-orange-400">
                <ZapOff className="h-3 w-3" />
                <span>Désactive toutes les fonctionnalités</span>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Feature Sync Warning - Only show when in maintenance */}
      {formData.mode === 'maintenance' && (
        <Card className="border-2 border-orange-500/50 bg-orange-500/5">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center flex-shrink-0">
                <ZapOff className="h-5 w-5 text-orange-400" />
              </div>
              <div>
                <h4 className="text-orange-400 font-semibold flex items-center gap-2">
                  Fonctionnalités désactivées
                </h4>
                <p className="text-gray-400 text-sm mt-1">
                  Toutes les fonctionnalités de l'application sont automatiquement désactivées en mode maintenance 
                  pour bloquer les actions, envois d'emails et accès indésirables.
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/50">
                    <ZapOff className="h-3 w-3 mr-1" />
                    23 fonctionnalités OFF
                  </Badge>
                  <span className="text-gray-500 text-xs">
                    • Les états seront restaurés à la sortie du mode maintenance
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Message Settings (only if not live) */}
      {formData.mode !== 'live' && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Eye className="h-5 w-5 text-[#f5a623]" />
              Page d'attente
            </CardTitle>
            <CardDescription>
              Personnalisez ce que les visiteurs voient
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Message */}
            <div className="space-y-2">
              <Label className="text-white">Message affiché</Label>
              <Textarea
                value={formData.message}
                onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                placeholder="Nous travaillons à améliorer votre expérience..."
                className="bg-gray-900 border-gray-700 text-white min-h-[100px]"
              />
            </div>

            {/* Progress Bar Toggle */}
            <div className="flex items-center justify-between p-4 rounded-lg bg-gray-900/50 border border-border">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Clock className="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Barre de progression</p>
                  <p className="text-gray-400 text-xs">Afficher l'avancement du développement</p>
                </div>
              </div>
              <Switch
                checked={formData.show_progress}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, show_progress: checked }))}
              />
            </div>

            {/* Progress Percentage */}
            {formData.show_progress && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-white">Progression (%)</Label>
                  <span className="text-[#f5a623] font-bold">{formData.progress_percent}%</span>
                </div>
                <Slider
                  value={[formData.progress_percent]}
                  onValueChange={([value]) => setFormData(prev => ({ ...prev, progress_percent: value }))}
                  max={100}
                  step={5}
                  className="w-full"
                />
              </div>
            )}

            {/* Estimated Completion */}
            <div className="space-y-2">
              <Label className="text-white flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Disponibilité estimée
              </Label>
              <Input
                value={formData.estimated_completion}
                onChange={(e) => setFormData(prev => ({ ...prev, estimated_completion: e.target.value }))}
                placeholder="Ex: Janvier 2026, Bientôt, 2 semaines..."
                className="bg-gray-900 border-gray-700 text-white"
              />
            </div>

            {/* Contact Email */}
            <div className="space-y-2">
              <Label className="text-white flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email de contact
              </Label>
              <Input
                type="email"
                value={formData.contact_email}
                onChange={(e) => setFormData(prev => ({ ...prev, contact_email: e.target.value }))}
                placeholder="contact@exemple.com"
                className="bg-gray-900 border-gray-700 text-white"
              />
            </div>

            {/* Save Button */}
            <Button 
              onClick={handleSaveSettings}
              disabled={saving}
              className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Sauvegarder les paramètres
            </Button>
          </CardContent>
        </Card>
      )}

      {/* IP Whitelist (Advanced) */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-[#f5a623]" />
            Liste blanche IP (Avancé)
          </CardTitle>
          <CardDescription>
            Permettre l'accès à certaines IP même en mode développement
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={newIp}
              onChange={(e) => setNewIp(e.target.value)}
              placeholder="192.168.1.1"
              className="bg-gray-900 border-gray-700 text-white"
            />
            <Button onClick={handleAddIp} disabled={!newIp}>
              Ajouter
            </Button>
          </div>
          
          {config?.allowed_ips?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {config.allowed_ips.map((ip, i) => (
                <Badge 
                  key={i} 
                  className="bg-gray-800 text-gray-300 cursor-pointer hover:bg-red-500/20 hover:text-red-400"
                  onClick={() => handleRemoveIp(ip)}
                >
                  {ip} ×
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Aucune IP dans la liste blanche</p>
          )}
        </CardContent>
      </Card>

      {/* Refresh Button */}
      <div className="flex justify-end">
        <Button variant="outline" onClick={loadConfig}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Rafraîchir
        </Button>
      </div>
    </div>
  );
};

export default SiteAccessControl;
