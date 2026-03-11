/**
 * MaintenancePage - Page affichée quand le site est en mode maintenance
 * SÉCURISÉ: Utilise des tokens de contournement stockés côté serveur
 * L'accès admin nécessite le mot de passe administrateur
 */

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { 
  Construction, 
  Wrench, 
  Clock, 
  Mail,
  Rocket,
  Settings,
  Loader2,
  Eye,
  EyeOff,
  Shield,
  Lock
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MaintenancePage = ({ siteStatus, onAdminAccess }) => {
  const isDevelopment = siteStatus?.mode === 'development';
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAdminBypass = async (e) => {
    e.preventDefault();
    
    if (!adminPassword.trim()) {
      toast.error('Mot de passe administrateur requis');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/maintenance/get-bypass-token`, {
        admin_password: adminPassword
      });

      if (response.data.success && response.data.bypass_token) {
        localStorage.setItem('maintenance_bypass_token', response.data.bypass_token);
        toast.success('Accès administrateur accordé! Redirection...');
        
        if (onAdminAccess) {
          onAdminAccess(response.data.bypass_token);
        }
        
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Mot de passe invalide';
      toast.error(errorMsg);
      setAdminPassword('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4 relative">
      {/* Admin Settings Button */}
      <button
        onClick={() => setShowAdminLogin(true)}
        className="fixed top-4 right-4 p-3 rounded-full bg-gray-800/80 hover:bg-gray-700 transition-all duration-300 group z-50 border border-gray-700 hover:border-[#f5a623]"
        title="Accès administrateur"
        data-testid="admin-settings-btn"
      >
        <Settings className="h-5 w-5 text-gray-500 group-hover:text-[#f5a623] group-hover:rotate-90 transition-all duration-300" />
      </button>

      <div className="max-w-2xl w-full">
        <Card className="bg-card border-border overflow-hidden">
          {/* Header Banner */}
          <div className={`p-6 text-center ${
            isDevelopment 
              ? 'bg-gradient-to-r from-yellow-600/30 to-orange-600/30' 
              : 'bg-gradient-to-r from-red-600/30 to-pink-600/30'
          }`}>
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-black/30 flex items-center justify-center">
              {isDevelopment ? (
                <Construction className="h-10 w-10 text-yellow-400" />
              ) : (
                <Wrench className="h-10 w-10 text-red-400" />
              )}
            </div>
            
            <Badge className={`mb-3 ${
              isDevelopment 
                ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' 
                : 'bg-red-500/20 text-red-400 border-red-500/50'
            }`}>
              {isDevelopment ? 'En Développement' : 'Maintenance'}
            </Badge>
            
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
              {isDevelopment ? 'Site en cours de développement' : 'Maintenance en cours'}
            </h1>
            
            <p className="text-gray-300 text-sm md:text-base">
              {siteStatus?.message || 'Nous travaillons à améliorer votre expérience.'}
            </p>
            
            {siteStatus?.activated_at && (
              <p className="text-gray-500 text-xs mt-2">
                Activé le {new Date(siteStatus.activated_at).toLocaleString('fr-CA')}
              </p>
            )}
          </div>

          <CardContent className="p-6 space-y-6">
            {/* Progress Bar */}
            {siteStatus?.show_progress && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400 flex items-center gap-2">
                    <Rocket className="h-4 w-4" />
                    Progression
                  </span>
                  <span className="text-[#f5a623] font-semibold">
                    {siteStatus?.progress_percent || 0}%
                  </span>
                </div>
                <Progress value={siteStatus?.progress_percent || 0} className="h-3 bg-gray-800" />
              </div>
            )}

            {/* Estimated Time */}
            {siteStatus?.estimated_completion && (
              <div className="flex items-center gap-3 p-4 rounded-lg bg-gray-900/50 border border-border">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <Clock className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Disponibilité estimée</p>
                  <p className="text-white font-medium">{siteStatus.estimated_completion}</p>
                </div>
              </div>
            )}

            {/* Contact Info */}
            {siteStatus?.contact_email && (
              <div className="flex items-center gap-3 p-4 rounded-lg bg-gray-900/50 border border-border">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <Mail className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Contact</p>
                  <a href={`mailto:${siteStatus.contact_email}`} className="text-[#f5a623] hover:underline">
                    {siteStatus.contact_email}
                  </a>
                </div>
              </div>
            )}

            {/* Security Notice */}
            <div className="flex items-center gap-2 p-3 rounded-lg bg-green-500/10 border border-green-500/30">
              <Shield className="h-4 w-4 text-green-400" />
              <p className="text-green-400 text-xs">
                Mode maintenance sécurisé et persistant
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Admin Password Dialog */}
      <Dialog open={showAdminLogin} onOpenChange={setShowAdminLogin}>
        <DialogContent className="bg-card border-border max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white">
              <Lock className="h-5 w-5 text-[#f5a623]" />
              Accès Administrateur
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              Entrez le mot de passe administrateur pour contourner le mode maintenance.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleAdminBypass} className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="admin-password" className="text-gray-300">
                Mot de passe administrateur
              </Label>
              <div className="relative">
                <Input
                  id="admin-password"
                  type={showPassword ? "text" : "password"}
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  placeholder="••••••••"
                  className="bg-background pr-10"
                  autoFocus
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

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowAdminLogin(false);
                  setAdminPassword('');
                }}
                className="flex-1"
              >
                Annuler
              </Button>
              <Button
                type="submit"
                disabled={loading || !adminPassword.trim()}
                className="flex-1 bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Vérification...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Accéder
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MaintenancePage;
