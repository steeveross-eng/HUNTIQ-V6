/**
 * ResetPasswordPage - Page pour réinitialiser le mot de passe
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  KeyRound,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  CheckCircle,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenEmail, setTokenEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [form, setForm] = useState({
    password: '',
    confirmPassword: ''
  });

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/verify-reset-token/${token}`);
        if (response.data.valid) {
          setTokenValid(true);
          setTokenEmail(response.data.email);
        }
      } catch (error) {
        console.error('Token verification failed:', error);
      } finally {
        setLoading(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (form.password !== form.confirmPassword) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    if (form.password.length < 6) {
      toast.error('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/auth/reset-password`, {
        token,
        new_password: form.password
      });
      setSuccess(true);
      toast.success('Mot de passe réinitialisé avec succès!');
    } catch (error) {
      const message = error.response?.data?.detail || 'Erreur lors de la réinitialisation';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  // No token provided
  if (!token) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="bg-card border-border max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Lien invalide</h2>
            <p className="text-gray-400 mb-6">
              Ce lien de réinitialisation est invalide ou a expiré.
            </p>
            <Button 
              onClick={() => navigate('/')}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
            >
              Retour à l'accueil
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Token invalid or expired
  if (!tokenValid) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="bg-card border-border max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Lien expiré</h2>
            <p className="text-gray-400 mb-6">
              Ce lien de réinitialisation a expiré ou a déjà été utilisé.
              Veuillez faire une nouvelle demande.
            </p>
            <Button 
              onClick={() => navigate('/')}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
            >
              Retour à l'accueil
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="bg-card border-border max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/20 flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Mot de passe réinitialisé!</h2>
            <p className="text-gray-400 mb-2">
              Votre mot de passe a été modifié avec succès.
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Un email de confirmation avec vos nouveaux identifiants vous a été envoyé.
            </p>
            <Button 
              onClick={() => navigate('/')}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
            >
              <ArrowRight className="h-4 w-4 mr-2" />
              Se connecter
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Reset form
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="bg-card border-border max-w-md w-full">
        <CardHeader className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
            <KeyRound className="h-8 w-8 text-[#f5a623]" />
          </div>
          <CardTitle className="text-white">Nouveau mot de passe</CardTitle>
          <CardDescription>
            Créez un nouveau mot de passe pour <span className="text-[#f5a623]">{tokenEmail}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-white">Nouveau mot de passe</Label>
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
              <p className="text-xs text-gray-500 mt-1">Minimum 6 caractères</p>
            </div>

            <div>
              <Label className="text-white">Confirmer le mot de passe</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={(e) => setForm(f => ({ ...f, confirmPassword: e.target.value }))}
                  placeholder="••••••••"
                  required
                  minLength={6}
                  className="bg-gray-900 border-gray-700 pl-10 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {form.password && form.confirmPassword && form.password !== form.confirmPassword && (
              <p className="text-red-400 text-sm flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                Les mots de passe ne correspondent pas
              </p>
            )}

            <Button 
              type="submit" 
              className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
              disabled={submitting || form.password !== form.confirmPassword}
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <KeyRound className="h-4 w-4 mr-2" />
                  Réinitialiser le mot de passe
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResetPasswordPage;
