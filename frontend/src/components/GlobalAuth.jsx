/**
 * GlobalAuth - Global authentication component with IP-based auto-login
 * 
 * BLOC 3 OPTIMIZATION:
 * - Added useMemo for context value memoization
 * - Prevents unnecessary re-renders across the app
 * 
 * @module GlobalAuth
 * @version 2.0.0 (BLOC 3)
 */

import React, { useState, useEffect, createContext, useContext, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  User, 
  LogIn, 
  LogOut, 
  UserPlus, 
  Mail, 
  Lock, 
  Phone,
  Shield,
  Smartphone,
  Loader2,
  CheckCircle,
  AlertCircle,
  Monitor,
  Wifi,
  ArrowLeft,
  KeyRound,
  Eye,
  EyeOff
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// AUTH CONTEXT
// ============================================

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// ============================================
// AUTH PROVIDER
// ============================================

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [autoLoginAttempted, setAutoLoginAttempted] = useState(false);
  const [deviceTrusted, setDeviceTrusted] = useState(false);

  // Try auto-login on mount
  useEffect(() => {
    const initAuth = async () => {
      // First, try to verify existing token
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        try {
          const response = await axios.get(`${API}/auth/verify?token=${storedToken}`);
          if (response.data.valid) {
            setUser(response.data.user);
            setToken(storedToken);
            setLoading(false);
            setAutoLoginAttempted(true);
            return;
          }
        } catch (error) {
          console.log('Token verification failed, trying auto-login');
        }
      }

      // Try IP-based auto-login
      try {
        const response = await axios.get(`${API}/auth/auto-login`);
        if (response.data.success && response.data.auto_login) {
          setUser(response.data.user);
          setToken(response.data.token);
          localStorage.setItem('auth_token', response.data.token);
          setDeviceTrusted(true);
          toast.success(`Bienvenue ${response.data.user.name}! (Connexion automatique)`);
        }
      } catch (error) {
        console.log('Auto-login not available');
      }

      setAutoLoginAttempted(true);
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password, rememberDevice = false) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password,
        remember_device: rememberDevice
      });

      if (response.data.success) {
        setUser(response.data.user);
        setToken(response.data.token);
        localStorage.setItem('auth_token', response.data.token);
        setDeviceTrusted(response.data.device_trusted);
        setShowLoginModal(false);
        toast.success(`Bienvenue ${response.data.user.name}!`);
        return { success: true };
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Erreur de connexion';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (name, email, password, phone = null) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        name,
        email,
        password,
        phone
      });

      if (response.data.success) {
        setUser(response.data.user);
        setToken(response.data.token);
        localStorage.setItem('auth_token', response.data.token);
        setShowLoginModal(false);
        toast.success('Compte créé avec succès!');
        return { success: true };
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Erreur d\'inscription';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API}/auth/logout?token=${token}`);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }

    setUser(null);
    setToken(null);
    setDeviceTrusted(false);
    localStorage.removeItem('auth_token');
    toast.success('Déconnexion réussie');
  };

  // BLOC 3: Memoized callbacks
  const openLoginModal = useCallback(() => setShowLoginModal(true), []);
  const closeLoginModal = useCallback(() => setShowLoginModal(false), []);

  // BLOC 3: Memoized context value to prevent re-renders
  const value = useMemo(() => ({
    user,
    token,
    loading,
    isAuthenticated: !!user,
    deviceTrusted,
    login,
    register,
    logout,
    openLoginModal,
    closeLoginModal,
    showLoginModal
  }), [user, token, loading, deviceTrusted, login, register, logout, openLoginModal, closeLoginModal, showLoginModal]);

  return (
    <AuthContext.Provider value={value}>
      {children}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={closeLoginModal}
        onLogin={login}
        onRegister={register}
      />
    </AuthContext.Provider>
  );
};

// ============================================
// LOGIN MODAL
// ============================================

const LoginModal = ({ isOpen, onClose, onLogin, onRegister }) => {
  const [mode, setMode] = useState('login'); // login, register, or forgot
  const [loading, setLoading] = useState(false);
  const [ipInfo, setIpInfo] = useState(null);
  const [forgotEmailSent, setForgotEmailSent] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // Form state
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    rememberDevice: true
  });

  // Load IP info on open
  useEffect(() => {
    if (isOpen) {
      loadIpInfo();
    }
  }, [isOpen]);

  const loadIpInfo = async () => {
    try {
      const response = await axios.get(`${API}/auth/ip-info`);
      setIpInfo(response.data);
    } catch (error) {
      console.error('Error loading IP info:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (mode === 'login') {
        await onLogin(form.email, form.password, form.rememberDevice);
      } else {
        await onRegister(form.name, form.email, form.password, form.phone);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAutoLogin = async () => {
    if (!ipInfo?.is_trusted) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/auth/auto-login`);
      if (response.data.success && response.data.auto_login) {
        window.location.reload(); // Reload to apply auth
      }
    } catch (error) {
      toast.error('Connexion automatique échouée');
    } finally {
      setLoading(false);
    }
  };

  // Handle forgot password
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!form.email.trim()) {
      toast.error('Veuillez entrer votre adresse courriel');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/auth/forgot-password`, { email: form.email });
      setForgotEmailSent(true);
      toast.success('Email envoyé! Vérifiez votre boîte de réception.');
    } catch (error) {
      toast.error('Erreur lors de l\'envoi. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  // Render forgot password view
  if (mode === 'forgot') {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="bg-card border-border max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-[#f5a623]" />
              Mot de passe oublié
            </DialogTitle>
            <DialogDescription>
              Entrez votre adresse courriel pour recevoir un lien de réinitialisation
            </DialogDescription>
          </DialogHeader>

          {forgotEmailSent ? (
            <div className="py-6 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Email envoyé!</h3>
              <p className="text-gray-400 text-sm mb-4">
                Si un compte existe avec l'adresse <span className="text-[#f5a623]">{form.email}</span>, 
                vous recevrez un lien de réinitialisation dans quelques minutes.
              </p>
              <p className="text-gray-500 text-xs mb-6">
                N'oubliez pas de vérifier votre dossier spam.
              </p>
              <Button 
                onClick={() => {
                  setMode('login');
                  setForgotEmailSent(false);
                }}
                variant="outline"
                className="w-full"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Retour à la connexion
              </Button>
            </div>
          ) : (
            <form onSubmit={handleForgotPassword} className="space-y-4">
              <div>
                <Label className="text-white">Adresse courriel</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))}
                    placeholder="vous@exemple.com"
                    required
                    className="bg-gray-900 border-gray-700 pl-10"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Envoyer le lien
                  </>
                )}
              </Button>

              <Button 
                type="button"
                variant="ghost" 
                className="w-full text-gray-400"
                onClick={() => setMode('login')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Retour à la connexion
              </Button>
            </form>
          )}
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <User className="h-5 w-5 text-[#f5a623]" />
            {mode === 'login' ? 'Connexion' : 'Créer un compte'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' 
              ? 'Connectez-vous pour accéder à toutes les fonctionnalités'
              : 'Créez votre compte pour commencer'}
          </DialogDescription>
        </DialogHeader>

        {/* IP Info Banner */}
        {ipInfo && mode === 'login' && (
          <Card className={`${ipInfo.is_trusted ? 'bg-green-500/10 border-green-500/30' : 'bg-gray-900/50 border-border'}`}>
            <CardContent className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Wifi className={`h-4 w-4 ${ipInfo.is_trusted ? 'text-green-400' : 'text-gray-400'}`} />
                  <div>
                    <p className="text-xs text-gray-400">Votre adresse IP</p>
                    <p className={`text-sm font-mono ${ipInfo.is_trusted ? 'text-green-400' : 'text-white'}`}>
                      {ipInfo.ip_address}
                    </p>
                  </div>
                </div>
                {ipInfo.is_trusted && (
                  <Button 
                    size="sm" 
                    onClick={handleAutoLogin}
                    className="bg-green-600 hover:bg-green-700 text-white"
                    disabled={loading}
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : (
                      <>
                        <Shield className="h-3 w-3 mr-1" />
                        Connexion auto
                      </>
                    )}
                  </Button>
                )}
              </div>
              {ipInfo.is_trusted && (
                <p className="text-xs text-green-400 mt-2 flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Appareil reconnu: {ipInfo.device_name || 'Appareil de confiance'}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <Label className="text-white">Nom complet</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  value={form.name}
                  onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
                  placeholder="Jean Dupont"
                  required
                  className="bg-gray-900 border-gray-700 pl-10"
                />
              </div>
            </div>
          )}

          <div>
            <Label className="text-white">Courriel</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type="email"
                value={form.email}
                onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))}
                placeholder="vous@exemple.com"
                required
                className="bg-gray-900 border-gray-700 pl-10"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <Label className="text-white">Mot de passe</Label>
              {mode === 'login' && (
                <button
                  type="button"
                  onClick={() => setMode('forgot')}
                  className="text-xs text-[#f5a623] hover:underline"
                >
                  Mot de passe oublié?
                </button>
              )}
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))}
                placeholder="••••••••"
                required
                minLength={6}
                className="bg-gray-900 border-gray-700 pl-10 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <Label className="text-white">Téléphone (optionnel)</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm(f => ({ ...f, phone: e.target.value }))}
                  placeholder="514-555-1234"
                  className="bg-gray-900 border-gray-700 pl-10"
                />
              </div>
            </div>
          )}

          {mode === 'login' && (
            <div className="flex items-center gap-2">
              <Checkbox
                id="remember"
                checked={form.rememberDevice}
                onCheckedChange={(c) => setForm(f => ({ ...f, rememberDevice: c }))}
              />
              <Label htmlFor="remember" className="text-gray-400 text-sm flex items-center gap-1 cursor-pointer">
                <Smartphone className="h-4 w-4" />
                Se souvenir de cet appareil (connexion auto)
              </Label>
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : mode === 'login' ? (
              <>
                <LogIn className="h-4 w-4 mr-2" />
                Connexion
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4 mr-2" />
                Créer mon compte
              </>
            )}
          </Button>

          {/* Google OAuth Button */}
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-gray-900 px-2 text-gray-400">ou</span>
            </div>
          </div>

          <Button 
            type="button" 
            variant="outline"
            className="w-full bg-white hover:bg-gray-100 text-gray-800 font-medium"
            disabled={loading}
            onClick={() => {
              // Redirect to Emergent Google Auth
              const backendUrl = process.env.REACT_APP_BACKEND_URL;
              const googleAuthUrl = `https://demobackend.emergentagent.com/auth/v1/env/login/google?redirect_url=${encodeURIComponent(backendUrl + '/api/auth/google/callback')}`;
              window.location.href = googleAuthUrl;
            }}
          >
            <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continuer avec Google
          </Button>
        </form>

        <div className="text-center text-sm text-gray-400">
          {mode === 'login' ? (
            <p>
              Pas de compte?{' '}
              <button 
                onClick={() => setMode('register')} 
                className="text-[#f5a623] hover:underline"
              >
                Inscrivez-vous
              </button>
            </p>
          ) : (
            <p>
              Déjà un compte?{' '}
              <button 
                onClick={() => setMode('login')} 
                className="text-[#f5a623] hover:underline"
              >
                Connectez-vous
              </button>
            </p>
          )}
        </div>

        {/* Trust info */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t border-border">
          <Shield className="h-3 w-3 inline mr-1" />
          Vos données sont sécurisées et ne sont jamais partagées
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// USER MENU COMPONENT (for navbar)
// ============================================

export const UserMenu = () => {
  const { user, isAuthenticated, loading, logout, openLoginModal, deviceTrusted } = useAuth();

  if (loading) {
    return (
      <Button variant="ghost" size="sm" className="text-white" disabled>
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  if (!isAuthenticated) {
    return (
      <Button 
        onClick={openLoginModal}
        className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
        data-testid="login-button"
      >
        <LogIn className="h-4 w-4 mr-2" />
        Connexion
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className="text-right hidden sm:block">
        <div className="text-white text-sm font-medium flex items-center gap-1">
          {user.name}
          {deviceTrusted && (
            <Badge className="bg-green-500/20 text-green-400 text-[10px] ml-1">
              <Shield className="h-2 w-2 mr-0.5" />
              Auto
            </Badge>
          )}
        </div>
        <p className="text-gray-500 text-xs">{user.email}</p>
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={logout}
        className="text-white hover:text-red-400"
        title="Déconnexion"
      >
        <LogOut className="h-5 w-5" />
      </Button>
    </div>
  );
};

export default AuthProvider;
