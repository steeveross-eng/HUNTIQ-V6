/**
 * AdminPremiumPage - V5-ULTIME Administration Premium
 * ====================================================
 * 
 * Page principale d'administration avec navigation intégrée.
 * Thème: Dark Premium avec accents or/bronze.
 * Accès: Admin uniquement.
 * 
 * Phase 1: E-Commerce migré
 * Phase 2: Content & Backup migrés
 * Phase 3: Maintenance & Contacts migrés
 * Phase 4: Hotspots & Networking migrés
 * Phase 5: Email & Marketing migrés
 * Phase 6: Partners & Branding migrés
 * BIONIC Knowledge Layer: Espèces, règles, modèles saisonniers
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import axios from 'axios';
import {
  Crown, ArrowLeft, LayoutDashboard, CreditCard, Layers, 
  Zap, Target, BookOpen, Settings, BarChart3, Users, 
  FileText, Shield, ShoppingCart, FolderTree, Archive,
  Wrench, Contact, Trees, Network, Mail, Sparkles,
  Handshake, Palette, Brain, Search, ToggleLeft, Activity,
  FlaskConical, Power, Store, UserCheck, Megaphone, LayoutGrid, Lock
} from 'lucide-react';

// Import all admin modules
import {
  AdminDashboard,
  AdminPayments,
  AdminFreemium,
  AdminUpsell,
  AdminOnboarding,
  AdminTutorials,
  AdminRules,
  AdminStrategy,
  AdminUsers,
  AdminLogs,
  AdminSettings,
  AdminEcommerce,
  AdminContent,
  AdminBackup,
  AdminMaintenance,
  AdminContacts,
  AdminHotspots,
  AdminNetworking,
  AdminEmail,
  AdminMarketing,
  AdminPartners,
  AdminBranding,
  AdminKnowledge,
  AdminSEO,
  AdminMarketingControls,
  AdminAnalytics,
  AdminCategories,
  AdminX300
} from '@/ui/administration';

// Import new modules - Phase 6+
import { AdminSuppliers } from '@/ui/administration/admin_suppliers';
import { AdminAffiliateSwitch } from '@/ui/administration/admin_affiliate_switch';
import { AdminAffiliateAds } from '@/ui/administration/admin_affiliate_ads';
import { AdminAdSpaces } from '@/ui/administration/admin_ad_spaces';
import { AdminGlobalSwitch } from '@/ui/administration/admin_global_switch';
import { AdminMessaging } from '@/ui/administration/admin_messaging';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'global-switch', label: '🔴 Master Switch', icon: Power, highlight: true },
  { id: 'messaging', label: 'Messaging Engine', icon: Mail, highlight: true },
  { id: 'x300', label: 'X300% Strategy', icon: Power, highlight: true },
  { id: 'affiliate-switch', label: 'Affiliate Switch', icon: UserCheck, highlight: true },
  { id: 'affiliate-ads', label: 'Affiliate Ads', icon: Megaphone, highlight: true },
  { id: 'ad-spaces', label: 'Ad Spaces', icon: LayoutGrid, highlight: true },
  { id: 'suppliers', label: 'Fournisseurs SEO', icon: Store },
  { id: 'analytics', label: 'Analytics', icon: Activity },
  { id: 'knowledge', label: 'Knowledge', icon: Brain },
  { id: 'seo', label: 'SEO Engine', icon: Search },
  { id: 'marketing-controls', label: 'Marketing ON/OFF', icon: ToggleLeft },
  { id: 'categories', label: 'Catégories', icon: FlaskConical },
  { id: 'ecommerce', label: 'E-Commerce', icon: ShoppingCart },
  { id: 'hotspots', label: 'Terres/Hotspots', icon: Trees },
  { id: 'networking', label: 'Réseautage', icon: Network },
  { id: 'email', label: 'Emails', icon: Mail },
  { id: 'marketing', label: 'Marketing', icon: Sparkles },
  { id: 'partners', label: 'Partenaires', icon: Handshake },
  { id: 'branding', label: 'Branding', icon: Palette },
  { id: 'content', label: 'Contenu', icon: FolderTree },
  { id: 'backup', label: 'Backups', icon: Archive },
  { id: 'maintenance', label: 'Maintenance', icon: Wrench },
  { id: 'contacts', label: 'Contacts', icon: Contact },
  { id: 'payments', label: 'Paiements', icon: CreditCard },
  { id: 'freemium', label: 'Freemium', icon: Layers },
  { id: 'upsell', label: 'Upsell', icon: Zap },
  { id: 'onboarding', label: 'Onboarding', icon: Target },
  { id: 'tutorials', label: 'Tutoriels', icon: BookOpen },
  { id: 'rules', label: 'Règles', icon: Settings },
  { id: 'strategy', label: 'Stratégies', icon: BarChart3 },
  { id: 'users', label: 'Utilisateurs', icon: Users },
  { id: 'logs', label: 'Logs', icon: FileText },
  { id: 'settings', label: 'Paramètres', icon: Shield },
];

const AdminPremiumPage = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const auth = localStorage.getItem('admin_premium_authenticated');
    if (auth === 'true') setIsAuthenticated(true);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      await axios.post(`${BACKEND_URL}/api/v1/admin/login`, {
        email: "admin@huntiq.ca",
        password,
      });
      localStorage.setItem('admin_premium_authenticated', 'true');
      setIsAuthenticated(true);
      toast.success("Connexion Admin Premium reussie!");
    } catch {
      toast.error("Mot de passe incorrect");
    }
    setLoginLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_premium_authenticated');
    setIsAuthenticated(false);
    navigate('/');
  };

  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-[#050510] flex items-center justify-center">
        <Card className="w-full max-w-md bg-[#0a0a15] border-[#F5A623]/20 p-8">
          <div className="text-center mb-6">
            <Lock className="h-12 w-12 text-[#F5A623] mx-auto mb-3" />
            <h2 className="text-xl font-bold text-white">Admin Premium</h2>
            <p className="text-gray-500 text-sm mt-1">Acces securise — mot de passe requis</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mot de passe administrateur"
              className="w-full bg-black border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#F5A623] focus:outline-none"
              data-testid="admin-premium-password-input"
            />
            <Button type="submit" className="w-full bg-[#F5A623] text-black font-bold" disabled={loginLoading} data-testid="admin-premium-login-btn">
              {loginLoading ? 'Connexion...' : 'Se connecter'}
            </Button>
          </form>
        </Card>
      </main>
    );
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard': return <AdminDashboard onNavigate={setActiveSection} />;
      case 'global-switch': return <AdminGlobalSwitch />;
      case 'messaging': return <AdminMessaging />;
      case 'x300': return <AdminX300 />;
      case 'affiliate-switch': return <AdminAffiliateSwitch />;
      case 'affiliate-ads': return <AdminAffiliateAds />;
      case 'ad-spaces': return <AdminAdSpaces />;
      case 'suppliers': return <AdminSuppliers />;
      case 'analytics': return <AdminAnalytics />;
      case 'knowledge': return <AdminKnowledge />;
      case 'seo': return <AdminSEO />;
      case 'marketing-controls': return <AdminMarketingControls />;
      case 'categories': return <AdminCategories />;
      case 'ecommerce': return <AdminEcommerce />;
      case 'hotspots': return <AdminHotspots />;
      case 'networking': return <AdminNetworking />;
      case 'email': return <AdminEmail />;
      case 'marketing': return <AdminMarketing />;
      case 'partners': return <AdminPartners />;
      case 'branding': return <AdminBranding />;
      case 'content': return <AdminContent />;
      case 'backup': return <AdminBackup />;
      case 'maintenance': return <AdminMaintenance />;
      case 'contacts': return <AdminContacts />;
      case 'payments': return <AdminPayments />;
      case 'freemium': return <AdminFreemium />;
      case 'upsell': return <AdminUpsell />;
      case 'onboarding': return <AdminOnboarding />;
      case 'tutorials': return <AdminTutorials />;
      case 'rules': return <AdminRules />;
      case 'strategy': return <AdminStrategy />;
      case 'users': return <AdminUsers />;
      case 'logs': return <AdminLogs />;
      case 'settings': return <AdminSettings />;
      default: return <AdminDashboard onNavigate={setActiveSection} />;
    }
  };

  return (
    <main 
      data-testid="admin-premium-page" 
      className="min-h-screen bg-[#050510] pt-20"
    >
      <div className="flex">
        {/* Sidebar */}
        <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-[#0a0a15] border-r border-[#F5A623]/10 p-4 overflow-y-auto">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-6 p-3 bg-gradient-to-r from-[#F5A623]/20 to-transparent rounded-lg">
            <Crown className="h-8 w-8 text-[#F5A623]" />
            <div>
              <h1 className="text-white font-bold">Admin Premium</h1>
              <p className="text-gray-500 text-xs">V5-ULTIME</p>
            </div>
          </div>

          {/* Back Button */}
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="w-full justify-start text-gray-400 hover:text-white hover:bg-white/5 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour à l'app
          </Button>

          {/* Navigation */}
          <nav className="space-y-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                data-testid={`sidebar-${item.id}`}
                variant="ghost"
                onClick={() => setActiveSection(item.id)}
                className={`
                  w-full justify-start transition-all
                  ${activeSection === item.id 
                    ? 'bg-[#F5A623]/10 text-[#F5A623] border-l-2 border-[#F5A623]' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                <item.icon className="h-4 w-4 mr-3" />
                {item.label}
              </Button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <div className="ml-64 flex-1 p-8">
          {renderContent()}
        </div>
      </div>
    </main>
  );
};

export default AdminPremiumPage;
