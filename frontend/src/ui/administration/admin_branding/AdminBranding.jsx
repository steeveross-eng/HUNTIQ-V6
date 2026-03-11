/**
 * AdminBranding - V5-ULTIME Administration Premium
 * =================================================
 * 
 * Module d'administration de l'identité visuelle (Phase 6 Migration).
 * - Dashboard et statistiques branding
 * - Gestion des logos (principal, FR, EN)
 * - Gestion des couleurs de marque
 * - Types de documents (7 types)
 * - Historique des documents générés
 * - Historique des uploads
 * 
 * Module isolé - Architecture LEGO.
 */

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Palette, LayoutDashboard, Image, Paintbrush, FileText, History,
  RefreshCw, Upload, Trash2, Globe, Copy, Check, RotateCcw, Eye
} from 'lucide-react';
import AdminService from '../AdminService';

const AdminBranding = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [brandConfig, setBrandConfig] = useState(null);
  const [logos, setLogos] = useState({ default: [], custom: [] });
  const [colors, setColors] = useState({});
  const [documentTypes, setDocumentTypes] = useState([]);
  const [documentHistory, setDocumentHistory] = useState([]);
  const [uploadHistory, setUploadHistory] = useState([]);
  const [copiedColor, setCopiedColor] = useState(null);

  // Load data on mount and tab change
  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'dashboard':
          const [statsRes, configRes] = await Promise.all([
            AdminService.brandingGetDashboard(),
            AdminService.brandingGetConfig()
          ]);
          if (statsRes.success) setStats(statsRes.stats);
          if (configRes.success) setBrandConfig(configRes.config);
          break;
        case 'logos':
          const logosRes = await AdminService.brandingGetLogos();
          if (logosRes.success) {
            setLogos({ default: logosRes.default, custom: logosRes.custom });
          }
          break;
        case 'colors':
          const colorsRes = await AdminService.brandingGetColors();
          if (colorsRes.success) setColors(colorsRes.colors);
          break;
        case 'documents':
          const [typesRes, histRes] = await Promise.all([
            AdminService.brandingGetDocumentTypes(),
            AdminService.brandingGetDocumentHistory()
          ]);
          if (typesRes.success) setDocumentTypes(typesRes.document_types);
          if (histRes.success) setDocumentHistory(histRes.history);
          break;
        case 'history':
          const uploadsRes = await AdminService.brandingGetUploadHistory();
          if (uploadsRes.success) setUploadHistory(uploadsRes.history);
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const handleDeleteLogo = async (logoId) => {
    const result = await AdminService.brandingDeleteLogo(logoId);
    if (result.success) loadData();
  };

  const handleResetColors = async () => {
    const result = await AdminService.brandingResetColors();
    if (result.success) loadData();
  };

  const copyColor = (hex) => {
    navigator.clipboard.writeText(hex);
    setCopiedColor(hex);
    setTimeout(() => setCopiedColor(null), 2000);
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'logos', label: 'Logos', icon: Image },
    { id: 'colors', label: 'Couleurs', icon: Paintbrush },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'history', label: 'Historique', icon: History }
  ];

  // ============ DASHBOARD TAB ============
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Logos</p>
              <p className="text-2xl font-bold text-white">{stats?.logos?.total || 0}</p>
            </div>
            <Image className="h-8 w-8 text-[#F5A623]" />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {stats?.logos?.default || 0} par défaut • {stats?.logos?.custom || 0} custom
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Couleurs définies</p>
              <p className="text-2xl font-bold text-[#F5A623]">{stats?.colors || 0}</p>
            </div>
            <Paintbrush className="h-8 w-8 text-[#F5A623]" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Documents générés</p>
              <p className="text-2xl font-bold text-green-400">{stats?.documents?.generated || 0}</p>
            </div>
            <FileText className="h-8 w-8 text-green-400" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Uploads totaux</p>
              <p className="text-2xl font-bold text-blue-400">{stats?.uploads?.total || 0}</p>
            </div>
            <Upload className="h-8 w-8 text-blue-400" />
          </div>
        </Card>
      </div>

      {/* Brand Info */}
      {brandConfig && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Globe className="h-5 w-5 text-[#F5A623]" />
              Marque Française
            </h3>
            <div className="space-y-3">
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Nom</p>
                <p className="text-white font-bold text-lg">{brandConfig.brands?.fr?.full}</p>
              </div>
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Slogan</p>
                <p className="text-[#F5A623] italic">{brandConfig.brands?.fr?.tagline}</p>
              </div>
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Domaine</p>
                <p className="text-white">{brandConfig.brands?.fr?.domain}</p>
              </div>
            </div>
          </Card>

          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-400" />
              English Brand
            </h3>
            <div className="space-y-3">
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Name</p>
                <p className="text-white font-bold text-lg">{brandConfig.brands?.en?.full}</p>
              </div>
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Tagline</p>
                <p className="text-blue-400 italic">{brandConfig.brands?.en?.tagline}</p>
              </div>
              <div className="p-3 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm">Domain</p>
                <p className="text-white">{brandConfig.brands?.en?.domain}</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );

  // ============ LOGOS TAB ============
  const renderLogos = () => (
    <div className="space-y-6">
      {/* Default Logos */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4">Logos par défaut</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {logos.default.map((logo) => (
            <div key={logo.id} className="p-4 bg-[#1a1a2e] rounded-lg border border-[#F5A623]/10">
              <div className="h-24 bg-[#0a0a15] rounded-lg flex items-center justify-center mb-3">
                <Image className="h-12 w-12 text-[#F5A623]/30" />
              </div>
              <p className="text-white font-medium">{logo.name}</p>
              <p className="text-gray-400 text-sm">{logo.description}</p>
              <Badge className="mt-2 bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Système
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Custom Logos */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold">Logos personnalisés</h3>
          <Button className="bg-[#F5A623]/20 text-[#F5A623] hover:bg-[#F5A623]/30">
            <Upload className="h-4 w-4 mr-2" />
            Uploader
          </Button>
        </div>
        {logos.custom.length === 0 ? (
          <div className="text-center py-8">
            <Image className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">Aucun logo personnalisé</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {logos.custom.map((logo) => (
              <div key={logo.id} className="p-4 bg-[#1a1a2e] rounded-lg border border-[#F5A623]/10">
                <div className="h-24 bg-[#0a0a15] rounded-lg flex items-center justify-center mb-3">
                  <Image className="h-12 w-12 text-[#F5A623]/30" />
                </div>
                <p className="text-white font-medium">{logo.filename}</p>
                <p className="text-gray-400 text-sm">{logo.language} • {logo.logo_type}</p>
                <div className="flex items-center justify-between mt-3">
                  <Badge className="bg-green-500/20 text-green-400 border border-green-500/30">
                    Custom
                  </Badge>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => handleDeleteLogo(logo.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );

  // ============ COLORS TAB ============
  const renderColors = () => (
    <div className="space-y-6">
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Paintbrush className="h-5 w-5 text-[#F5A623]" />
            Palette de couleurs
          </h3>
          <Button 
            onClick={handleResetColors}
            variant="outline" 
            className="border-gray-600 text-gray-400 hover:text-white"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Réinitialiser
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(colors).map(([key, color]) => (
            <div 
              key={key}
              className="p-4 bg-[#1a1a2e] rounded-lg border border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div 
                  className="w-16 h-16 rounded-lg border-2 border-white/20 shadow-lg"
                  style={{ backgroundColor: color.hex }}
                />
                <div className="flex-1">
                  <p className="text-white font-medium capitalize">{key}</p>
                  <p className="text-gray-400 text-sm">{color.name}</p>
                  <p className="text-gray-500 text-xs mt-1">{color.usage}</p>
                </div>
              </div>
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#F5A623]/10">
                <code className="text-[#F5A623] text-sm font-mono">{color.hex}</code>
                <Button 
                  size="sm" 
                  variant="ghost"
                  onClick={() => copyColor(color.hex)}
                  className="text-gray-400 hover:text-white"
                >
                  {copiedColor === color.hex ? (
                    <Check className="h-4 w-4 text-green-400" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  // ============ DOCUMENTS TAB ============
  const renderDocuments = () => (
    <div className="space-y-6">
      {/* Document Types */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4">Types de documents disponibles</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {documentTypes.map((type) => (
            <div key={type.id} className="p-4 bg-[#1a1a2e] rounded-lg text-center">
              <FileText className="h-8 w-8 text-[#F5A623] mx-auto mb-2" />
              <p className="text-white font-medium">{type.name_fr}</p>
              <p className="text-gray-500 text-xs">{type.name_en}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Document History */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4">Historique des documents générés</h3>
        {documentHistory.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">Aucun document généré</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documentHistory.map((doc) => (
              <div key={doc.id} className="p-4 bg-[#1a1a2e] rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <FileText className="h-8 w-8 text-[#F5A623] p-1 bg-[#F5A623]/10 rounded-lg" />
                  <div>
                    <p className="text-white font-medium">{doc.title || doc.template_type}</p>
                    <p className="text-gray-400 text-sm">
                      {doc.language?.toUpperCase()} • {doc.recipient || 'N/A'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-gray-500 text-sm">
                    {new Date(doc.generated_at).toLocaleDateString('fr-CA')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );

  // ============ HISTORY TAB ============
  const renderHistory = () => (
    <div className="space-y-6">
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <History className="h-5 w-5 text-[#F5A623]" />
          Historique des uploads
        </h3>
        {uploadHistory.length === 0 ? (
          <div className="text-center py-8">
            <Upload className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">Aucun upload enregistré</p>
          </div>
        ) : (
          <div className="space-y-3">
            {uploadHistory.map((upload) => (
              <div key={upload.id} className="p-4 bg-[#1a1a2e] rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Image className="h-8 w-8 text-blue-400 p-1 bg-blue-400/10 rounded-lg" />
                  <div>
                    <p className="text-white font-medium">{upload.filename}</p>
                    <p className="text-gray-400 text-sm">
                      {upload.language?.toUpperCase()} • {upload.logo_type}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-gray-500 text-sm">
                    {new Date(upload.uploaded_at).toLocaleDateString('fr-CA')}
                  </p>
                  <p className="text-gray-600 text-xs">
                    {upload.file_size ? `${(upload.file_size / 1024).toFixed(1)} KB` : ''}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );

  return (
    <div data-testid="admin-branding-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Palette className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Identité Visuelle</h2>
            <p className="text-gray-400 text-sm">Branding & Assets</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#F5A623]/10 pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            data-testid={`branding-tab-${tab.id}`}
            variant="ghost"
            onClick={() => setActiveTab(tab.id)}
            className={`
              ${activeTab === tab.id
                ? 'bg-[#F5A623]/10 text-[#F5A623] border-b-2 border-[#F5A623]'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'logos' && renderLogos()}
          {activeTab === 'colors' && renderColors()}
          {activeTab === 'documents' && renderDocuments()}
          {activeTab === 'history' && renderHistory()}
        </>
      )}
    </div>
  );
};

export { AdminBranding };
export default AdminBranding;
