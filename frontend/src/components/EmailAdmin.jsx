/**
 * EmailAdmin - Admin panel for email notifications
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Mail,
  Send,
  Settings,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  Calendar,
  Users
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const EmailAdmin = () => {
  const { t } = useLanguage();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sendingTest, setSendingTest] = useState(false);
  const [sendingBulk, setSendingBulk] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [digestPeriod, setDigestPeriod] = useState('daily');

  const loadConfig = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/email/config`);
      setConfig(response.data);
    } catch (error) {
      console.error('Error loading email config:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const sendTestEmail = async () => {
    if (!testEmail.trim()) {
      toast.error('Veuillez entrer une adresse email');
      return;
    }

    setSendingTest(true);
    try {
      const response = await axios.post(`${API}/email/test`, {
        recipient_email: testEmail,
        subject: 'Test Email - BIONIC Territoire de Chasse'
      });
      
      if (response.data.status === 'success') {
        toast.success('Email de test envoyé!');
      } else {
        toast.error(response.data.reason || 'Erreur lors de l\'envoi');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi');
    } finally {
      setSendingTest(false);
    }
  };

  const sendBulkDigest = async () => {
    setSendingBulk(true);
    try {
      const response = await axios.post(`${API}/email/send-bulk-digest`, {
        period: digestPeriod,
        limit: 100
      });
      
      if (response.data.status === 'processing') {
        toast.success(`${response.data.users_queued} emails en cours d'envoi...`);
      } else if (response.data.status === 'no_users') {
        toast.info('Aucun utilisateur avec des notifications non lues');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setSendingBulk(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mail className="h-6 w-6 text-[#f5a623]" />
            Notifications Email
          </h2>
          <p className="text-gray-400">Gérer les emails de notification aux utilisateurs</p>
        </div>
        <Button variant="outline" onClick={loadConfig}>
          <RefreshCw className="h-4 w-4 mr-2" />
          {t('common_refresh')}
        </Button>
      </div>

      {/* Configuration Status */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
              <div className="flex items-center gap-3">
                {config?.resend_configured ? (
                  <CheckCircle className="h-5 w-5 text-green-400" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-400" />
                )}
                <span className="text-white">Service Resend</span>
              </div>
              <Badge variant={config?.resend_configured ? 'default' : 'destructive'}>
                {config?.resend_configured ? 'Configuré' : 'Non configuré'}
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
              <span className="text-gray-400">Email expéditeur</span>
              <span className="text-white font-mono text-sm">{config?.sender_email || 'Non défini'}</span>
            </div>
          </div>
          
          {!config?.resend_configured && (
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <p className="text-yellow-400 text-sm flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Pour activer les emails, ajoutez RESEND_API_KEY dans le fichier .env du backend
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Email */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white">Envoyer un email de test</CardTitle>
          <CardDescription>Testez la configuration email en envoyant un email</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="test-email">Adresse email</Label>
              <Input
                id="test-email"
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="test@exemple.com"
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={sendTestEmail}
                disabled={sendingTest || !config?.resend_configured}
                className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
              >
                {sendingTest ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Envoyer
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bulk Digest */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5" />
            Envoyer un résumé de masse
          </CardTitle>
          <CardDescription>
            Envoyer un email de résumé à tous les utilisateurs ayant des notifications non lues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="w-48">
              <Label>Période</Label>
              <Select value={digestPeriod} onValueChange={setDigestPeriod}>
                <SelectTrigger className="bg-gray-900 border-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      Quotidien
                    </div>
                  </SelectItem>
                  <SelectItem value="weekly">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      Hebdomadaire
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={sendBulkDigest}
              disabled={sendingBulk || !config?.resend_configured}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
            >
              {sendingBulk ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Envoyer à tous
                </>
              )}
            </Button>
          </div>
          
          <p className="text-sm text-gray-500 mt-4">
            Note: Seuls les utilisateurs avec les notifications email activées recevront l'email.
          </p>
        </CardContent>
      </Card>

      {/* Email Types Info */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white">Types d'emails automatiques</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-white font-medium">Email de bienvenue</p>
                <p className="text-xs text-gray-500">Envoyé à l'inscription</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Mail className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-white font-medium">Résumé des notifications</p>
                <p className="text-xs text-gray-500">Quotidien ou hebdomadaire</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EmailAdmin;
