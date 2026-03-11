/**
 * AdminSEO - V5-ULTIME Administration Premium
 * ============================================
 * 
 * Module d'administration du BIONIC SEO Engine V5.
 * Plan SEO +300% - Architecture LEGO isolée.
 * 
 * Fonctionnalités:
 * - Dashboard SEO global
 * - Gestion des clusters thématiques
 * - Gestion des pages (piliers, satellites, opportunités)
 * - JSON-LD Builder
 * - Analytics et KPIs
 * - Automatisation et suggestions
 * - Content Factory (génération IA)
 * 
 * Module isolé - Aucun import croisé.
 */

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Search, LayoutDashboard, Layers, FileText, Code2,
  BarChart3, Zap, Factory, RefreshCw, Plus, Eye,
  TrendingUp, Target, Globe, Link2, Calendar, Bell,
  ChevronRight, AlertTriangle, CheckCircle, Clock,
  Sparkles, BookOpen, MapPin, Settings, Filter,
  ArrowUp, ArrowDown, Minus, Star, Play, Lightbulb,
  FileDown, X, ExternalLink
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const AdminSEO = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [pages, setPages] = useState([]);
  const [schemas, setSchemas] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [automation, setAutomation] = useState({ rules: [], suggestions: [], alerts: [] });
  const [templates, setTemplates] = useState(null);
  const [filters, setFilters] = useState({ cluster: 'all', pageType: 'all', status: 'all' });
  const [showDocumentation, setShowDocumentation] = useState(false);
  const [documentation, setDocumentation] = useState(null);
  const [loadingDoc, setLoadingDoc] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  // Fonction pour charger la documentation SEO interne
  const loadDocumentation = async () => {
    setLoadingDoc(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/bionic/seo/documentation`);
      const data = await res.json();
      if (data.success) {
        setDocumentation(data.documentation);
        setShowDocumentation(true);
      }
    } catch (error) {
      console.error('Error loading documentation:', error);
    }
    setLoadingDoc(false);
  };

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'dashboard':
          const dashRes = await fetch(`${API_BASE}/api/v1/bionic/seo/dashboard`);
          const dashData = await dashRes.json();
          if (dashData.success) setDashboard(dashData.dashboard);
          break;
        case 'clusters':
          const clustersRes = await fetch(`${API_BASE}/api/v1/bionic/seo/clusters`);
          const clustersData = await clustersRes.json();
          if (clustersData.success) setClusters(clustersData.clusters);
          break;
        case 'pages':
          const pagesRes = await fetch(`${API_BASE}/api/v1/bionic/seo/pages`);
          const pagesData = await pagesRes.json();
          if (pagesData.success) setPages(pagesData.pages);
          // Load templates
          const tplRes = await fetch(`${API_BASE}/api/v1/bionic/seo/pages/templates`);
          const tplData = await tplRes.json();
          if (tplData.success) setTemplates(tplData.templates);
          break;
        case 'jsonld':
          const schemasRes = await fetch(`${API_BASE}/api/v1/bionic/seo/jsonld`);
          const schemasData = await schemasRes.json();
          if (schemasData.success) setSchemas(schemasData.schemas);
          break;
        case 'analytics':
          const analyticsRes = await fetch(`${API_BASE}/api/v1/bionic/seo/analytics/dashboard`);
          const analyticsData = await analyticsRes.json();
          if (analyticsData.success) setAnalytics(analyticsData.stats);
          break;
        case 'automation':
          const [rulesRes, suggestionsRes, alertsRes] = await Promise.all([
            fetch(`${API_BASE}/api/v1/bionic/seo/automation/rules`),
            fetch(`${API_BASE}/api/v1/bionic/seo/automation/suggestions`),
            fetch(`${API_BASE}/api/v1/bionic/seo/automation/alerts?limit=20`)
          ]);
          const rulesData = await rulesRes.json();
          const suggestionsData = await suggestionsRes.json();
          const alertsData = await alertsRes.json();
          setAutomation({
            rules: rulesData.rules || [],
            suggestions: suggestionsData.suggestions || [],
            alerts: alertsData.alerts || []
          });
          break;
      }
    } catch (error) {
      console.error('Error loading SEO data:', error);
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'clusters', label: 'Clusters', icon: Layers },
    { id: 'pages', label: 'Pages', icon: FileText },
    { id: 'jsonld', label: 'JSON-LD', icon: Code2 },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'factory', label: 'Content Factory', icon: Factory }
  ];

  const getClusterTypeIcon = (type) => {
    const icons = {
      species: '🦌',
      region: '🗺️',
      season: '🍂',
      technique: '🎯',
      equipment: '🎒',
      territory: '🏕️',
      behavior: '🧠',
      weather: '⛅'
    };
    return icons[type] || '📂';
  };

  const getPageTypeBadge = (type) => {
    const styles = {
      pillar: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      satellite: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      opportunity: 'bg-green-500/20 text-green-400 border-green-500/30',
      viral: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      interactive: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      tool: 'bg-orange-500/20 text-orange-400 border-orange-500/30'
    };
    return (
      <Badge className={`${styles[type] || styles.satellite} border`}>
        {type?.toUpperCase()}
      </Badge>
    );
  };

  const getStatusBadge = (status) => {
    const styles = {
      published: 'bg-green-500/20 text-green-400 border-green-500/30',
      draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      scheduled: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      review: 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    };
    return (
      <Badge className={`${styles[status] || styles.draft} border`}>
        {status}
      </Badge>
    );
  };

  const getSEOScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  // ============ DASHBOARD ============
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* KPIs principaux */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Clusters actifs</p>
              <p className="text-2xl font-bold text-white">{dashboard?.clusters?.total || 0}</p>
            </div>
            <Layers className="h-8 w-8 text-[#F5A623]" />
          </div>
          <p className="text-xs text-green-400 mt-2">
            {dashboard?.clusters?.active || 0} actifs
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Pages SEO</p>
              <p className="text-2xl font-bold text-white">{dashboard?.pages?.total || 0}</p>
            </div>
            <FileText className="h-8 w-8 text-blue-400" />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {dashboard?.pages?.published || 0} publiées • {dashboard?.pages?.draft || 0} brouillons
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Score santé SEO</p>
              <p className={`text-2xl font-bold ${getSEOScoreColor(dashboard?.overview?.health_score || 0)}`}>
                {dashboard?.overview?.health_score?.toFixed(0) || 0}%
              </p>
            </div>
            <Target className="h-8 w-8 text-green-400" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Schémas JSON-LD</p>
              <p className="text-2xl font-bold text-purple-400">{dashboard?.schemas?.total || 0}</p>
            </div>
            <Code2 className="h-8 w-8 text-purple-400" />
          </div>
        </Card>
      </div>

      {/* Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Performance trafic
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#1a1a2e] rounded-lg">
              <p className="text-2xl font-bold text-blue-400">{dashboard?.overview?.total_clicks?.toLocaleString() || 0}</p>
              <p className="text-gray-400 text-sm">Clicks</p>
            </div>
            <div className="text-center p-4 bg-[#1a1a2e] rounded-lg">
              <p className="text-2xl font-bold text-purple-400">{dashboard?.overview?.total_impressions?.toLocaleString() || 0}</p>
              <p className="text-gray-400 text-sm">Impressions</p>
            </div>
            <div className="text-center p-4 bg-[#1a1a2e] rounded-lg">
              <p className="text-2xl font-bold text-green-400">{dashboard?.overview?.avg_ctr?.toFixed(2) || 0}%</p>
              <p className="text-gray-400 text-sm">CTR moyen</p>
            </div>
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Bell className="h-5 w-5 text-[#F5A623]" />
            Alertes récentes
          </h3>
          {dashboard?.alerts?.recent?.length > 0 ? (
            <div className="space-y-2">
              {dashboard.alerts.recent.map((alert, idx) => (
                <div key={idx} className="p-3 bg-[#1a1a2e] rounded-lg flex items-center gap-3">
                  <AlertTriangle className="h-4 w-4 text-yellow-400" />
                  <p className="text-gray-300 text-sm flex-1">{alert.message}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Aucune alerte récente</p>
          )}
        </Card>
      </div>

      {/* Suggestions */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-[#F5A623]" />
          Suggestions de contenu ({dashboard?.suggestions?.count || 0})
        </h3>
        {dashboard?.suggestions?.top?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {dashboard.suggestions.top.map((suggestion, idx) => (
              <div key={idx} className="p-4 bg-[#1a1a2e] rounded-lg">
                <p className="text-white font-medium">{suggestion.title_fr}</p>
                <p className="text-gray-400 text-sm mt-1">{suggestion.reason}</p>
                <Badge className="mt-2 bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30">
                  {suggestion.priority}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Aucune suggestion disponible</p>
        )}
      </Card>
    </div>
  );

  // ============ CLUSTERS ============
  const renderClusters = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">Clusters SEO thématiques</h3>
        <Button className="bg-[#F5A623] hover:bg-[#F5A623]/80 text-black">
          <Plus className="h-4 w-4 mr-2" />
          Nouveau cluster
        </Button>
      </div>

      {/* Filtres par type */}
      <div className="flex flex-wrap gap-2">
        {['all', 'species', 'region', 'season', 'technique', 'equipment'].map((type) => (
          <Button
            key={type}
            variant="outline"
            size="sm"
            onClick={() => setFilters({ ...filters, cluster: type })}
            className={`
              ${filters.cluster === type
                ? 'bg-[#F5A623]/20 text-[#F5A623] border-[#F5A623]/30'
                : 'text-gray-400 border-gray-600'
              }
            `}
          >
            {type === 'all' ? 'Tous' : type}
          </Button>
        ))}
      </div>

      {/* Liste des clusters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clusters
          .filter(c => filters.cluster === 'all' || c.cluster_type === filters.cluster)
          .map((cluster) => (
          <Card key={cluster.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4 hover:border-[#F5A623]/40 transition-colors">
            <div className="flex items-start gap-4">
              <span className="text-3xl">{getClusterTypeIcon(cluster.cluster_type)}</span>
              <div className="flex-1">
                <p className="text-white font-semibold">{cluster.name_fr}</p>
                <p className="text-gray-400 text-sm mt-1 line-clamp-2">{cluster.description_fr}</p>
                <div className="flex items-center gap-2 mt-3">
                  <Badge variant="outline" className="text-gray-400 border-gray-600">
                    {cluster.cluster_type}
                  </Badge>
                  {cluster.primary_keyword && (
                    <Badge className="bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      {cluster.primary_keyword.search_volume?.toLocaleString()} vol.
                    </Badge>
                  )}
                </div>
                {cluster.species_ids?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {cluster.species_ids.map((sp) => (
                      <Badge key={sp} variant="outline" className="text-xs text-gray-500 border-gray-700">
                        {sp}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // ============ PAGES ============
  const renderPages = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">Pages SEO</h3>
        <Button className="bg-[#F5A623] hover:bg-[#F5A623]/80 text-black">
          <Plus className="h-4 w-4 mr-2" />
          Nouvelle page
        </Button>
      </div>

      {/* Filtres */}
      <div className="flex flex-wrap gap-4 items-center">
        <select
          value={filters.pageType}
          onChange={(e) => setFilters({ ...filters, pageType: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Tous types</option>
          <option value="pillar">Pilier</option>
          <option value="satellite">Satellite</option>
          <option value="opportunity">Opportunité</option>
          <option value="viral">Viral</option>
        </select>
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Tous statuts</option>
          <option value="published">Publié</option>
          <option value="draft">Brouillon</option>
          <option value="scheduled">Planifié</option>
        </select>
        <Button onClick={loadData} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Templates */}
      {templates && (
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <h4 className="text-white font-medium mb-3 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-[#F5A623]" />
            Templates disponibles
          </h4>
          <div className="flex flex-wrap gap-2">
            {templates.pillar?.map((t) => (
              <Badge key={t.id} className="bg-purple-500/20 text-purple-400 border border-purple-500/30 cursor-pointer hover:bg-purple-500/30">
                {t.name_fr}
              </Badge>
            ))}
            {templates.satellite?.map((t) => (
              <Badge key={t.id} className="bg-blue-500/20 text-blue-400 border border-blue-500/30 cursor-pointer hover:bg-blue-500/30">
                {t.name_fr}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Liste des pages */}
      {pages.length > 0 ? (
        <div className="space-y-3">
          {pages
            .filter(p => filters.pageType === 'all' || p.page_type === filters.pageType)
            .filter(p => filters.status === 'all' || p.status === filters.status)
            .map((page) => (
            <Card key={page.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getPageTypeBadge(page.page_type)}
                    {getStatusBadge(page.status)}
                    <p className="text-white font-semibold">{page.title_fr || page.title}</p>
                  </div>
                  <p className="text-gray-400 text-sm">{page.url_path}</p>
                  <div className="flex flex-wrap gap-4 mt-3 text-sm">
                    <span className="text-gray-500">
                      <strong className="text-gray-300">{page.word_count}</strong> mots
                    </span>
                    <span className="text-gray-500">
                      Score SEO: <strong className={getSEOScoreColor(page.seo_score)}>{page.seo_score}</strong>
                    </span>
                    <span className="text-gray-500">
                      {page.clicks} clicks • {page.impressions} impressions
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
          <FileText className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Aucune page SEO créée</p>
          <p className="text-gray-500 text-sm mt-2">Créez votre première page pilier pour commencer</p>
        </Card>
      )}
    </div>
  );

  // ============ JSON-LD ============
  const renderJsonLD = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">Schémas JSON-LD</h3>
        <Button className="bg-[#F5A623] hover:bg-[#F5A623]/80 text-black">
          <Plus className="h-4 w-4 mr-2" />
          Nouveau schéma
        </Button>
      </div>

      {/* Types de schémas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {['Article', 'HowTo', 'FAQPage', 'LocalBusiness', 'BreadcrumbList', 'VideoObject'].map((type) => (
          <Card key={type} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4 cursor-pointer hover:border-[#F5A623]/40 transition-colors">
            <div className="flex items-center gap-3">
              <Code2 className="h-5 w-5 text-purple-400" />
              <div>
                <p className="text-white font-medium">{type}</p>
                <p className="text-gray-500 text-xs">Schéma structuré</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Liste des schémas */}
      {schemas.length > 0 ? (
        <div className="space-y-3">
          {schemas.map((schema) => (
            <Card key={schema.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Code2 className="h-5 w-5 text-purple-400" />
                  <div>
                    <p className="text-white font-medium">{schema.schema_type}</p>
                    <p className="text-gray-400 text-sm">Page: {schema.page_id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {schema.is_valid ? (
                    <Badge className="bg-green-500/20 text-green-400 border border-green-500/30">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Valide
                    </Badge>
                  ) : (
                    <Badge className="bg-red-500/20 text-red-400 border border-red-500/30">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      Erreurs
                    </Badge>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
          <Code2 className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Aucun schéma JSON-LD créé</p>
          <p className="text-gray-500 text-sm mt-2">Les schémas structurés améliorent votre visibilité dans les résultats Google</p>
        </Card>
      )}
    </div>
  );

  // ============ ANALYTICS ============
  const renderAnalytics = () => (
    <div className="space-y-6">
      {analytics ? (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Position moyenne</p>
                  <p className="text-2xl font-bold text-white">{analytics.performance?.avg_position?.toFixed(1) || '-'}</p>
                </div>
                <MapPin className="h-8 w-8 text-blue-400" />
              </div>
            </Card>

            <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Score SEO moyen</p>
                  <p className={`text-2xl font-bold ${getSEOScoreColor(analytics.performance?.avg_seo_score || 0)}`}>
                    {analytics.performance?.avg_seo_score?.toFixed(0) || 0}
                  </p>
                </div>
                <Target className="h-8 w-8 text-green-400" />
              </div>
            </Card>

            <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Conversions</p>
                  <p className="text-2xl font-bold text-purple-400">{analytics.performance?.total_conversions || 0}</p>
                </div>
                <Star className="h-8 w-8 text-purple-400" />
              </div>
            </Card>

            <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Santé technique</p>
                  <p className={`text-2xl font-bold ${getSEOScoreColor(analytics.technical?.health_score || 0)}`}>
                    {analytics.technical?.health_score?.toFixed(0) || 0}%
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-[#F5A623]" />
              </div>
            </Card>
          </div>

          {/* Détails trafic */}
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[#F5A623]" />
              Détails du trafic
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-4 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm mb-2">Total clicks</p>
                <p className="text-3xl font-bold text-blue-400">{analytics.traffic?.total_clicks?.toLocaleString() || 0}</p>
              </div>
              <div className="p-4 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm mb-2">Total impressions</p>
                <p className="text-3xl font-bold text-purple-400">{analytics.traffic?.total_impressions?.toLocaleString() || 0}</p>
              </div>
              <div className="p-4 bg-[#1a1a2e] rounded-lg">
                <p className="text-gray-400 text-sm mb-2">CTR moyen</p>
                <p className="text-3xl font-bold text-green-400">{analytics.traffic?.avg_ctr?.toFixed(2) || 0}%</p>
              </div>
            </div>
          </Card>
        </>
      ) : (
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
          <BarChart3 className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Chargement des analytics...</p>
        </Card>
      )}
    </div>
  );

  // ============ AUTOMATION ============
  const renderAutomation = () => (
    <div className="space-y-6">
      {/* Règles d'automatisation */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-[#F5A623]" />
          Règles d'automatisation
        </h3>
        <div className="space-y-3">
          {automation.rules.map((rule) => (
            <div key={rule.id} className="p-4 bg-[#1a1a2e] rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${rule.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
                <div>
                  <p className="text-white font-medium">{rule.name_fr}</p>
                  <p className="text-gray-400 text-sm">{rule.description}</p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="border-gray-600 text-gray-400">
                {rule.is_active ? 'Désactiver' : 'Activer'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Suggestions de contenu */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-[#F5A623]" />
          Suggestions de contenu ({automation.suggestions.length})
        </h3>
        {automation.suggestions.length > 0 ? (
          <div className="space-y-3">
            {automation.suggestions.map((suggestion, idx) => (
              <div key={idx} className="p-4 bg-[#1a1a2e] rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white font-medium">{suggestion.title_fr}</p>
                    <p className="text-gray-400 text-sm mt-1">{suggestion.reason}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className={`
                        ${suggestion.priority === 'high' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                          suggestion.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                          'bg-gray-500/20 text-gray-400 border-gray-500/30'
                        } border
                      `}>
                        {suggestion.priority}
                      </Badge>
                      <Badge variant="outline" className="text-gray-400 border-gray-600">
                        {suggestion.type}
                      </Badge>
                    </div>
                  </div>
                  <Button size="sm" className="bg-[#F5A623]/20 text-[#F5A623] hover:bg-[#F5A623]/30">
                    <Plus className="h-4 w-4 mr-1" />
                    Créer
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Aucune suggestion disponible</p>
        )}
      </Card>

      {/* Alertes */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Bell className="h-5 w-5 text-[#F5A623]" />
          Alertes SEO ({automation.alerts.length})
        </h3>
        {automation.alerts.length > 0 ? (
          <div className="space-y-2">
            {automation.alerts.map((alert) => (
              <div key={alert.id} className={`p-3 rounded-lg flex items-center gap-3 ${
                alert.is_read ? 'bg-[#1a1a2e]' : 'bg-yellow-500/10 border border-yellow-500/20'
              }`}>
                <AlertTriangle className={`h-4 w-4 ${alert.is_read ? 'text-gray-500' : 'text-yellow-400'}`} />
                <p className={`text-sm flex-1 ${alert.is_read ? 'text-gray-400' : 'text-gray-300'}`}>{alert.message}</p>
                <span className="text-xs text-gray-500">{new Date(alert.created_at).toLocaleDateString('fr-CA')}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">Aucune alerte</p>
        )}
      </Card>
    </div>
  );

  // ============ CONTENT FACTORY ============
  const renderFactory = () => (
    <div className="space-y-6">
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Factory className="h-5 w-5 text-[#F5A623]" />
          Content Factory - Génération IA
        </h3>
        <p className="text-gray-400 mb-6">
          Générez du contenu SEO optimisé en utilisant le Knowledge Layer et l'IA.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-[#1a1a2e] border-[#F5A623]/20 p-4 cursor-pointer hover:border-[#F5A623]/40 transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <FileText className="h-6 w-6 text-purple-400" />
              <h4 className="text-white font-medium">Page Pilier</h4>
            </div>
            <p className="text-gray-400 text-sm">Guide complet (3000+ mots) avec structure optimisée</p>
            <Button className="w-full mt-4 bg-purple-500/20 text-purple-400 hover:bg-purple-500/30">
              <Play className="h-4 w-4 mr-2" />
              Générer
            </Button>
          </Card>

          <Card className="bg-[#1a1a2e] border-[#F5A623]/20 p-4 cursor-pointer hover:border-[#F5A623]/40 transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <Layers className="h-6 w-6 text-blue-400" />
              <h4 className="text-white font-medium">Page Satellite</h4>
            </div>
            <p className="text-gray-400 text-sm">Article ciblé (1000+ mots) pour sous-sujet</p>
            <Button className="w-full mt-4 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30">
              <Play className="h-4 w-4 mr-2" />
              Générer
            </Button>
          </Card>

          <Card className="bg-[#1a1a2e] border-[#F5A623]/20 p-4 cursor-pointer hover:border-[#F5A623]/40 transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <Target className="h-6 w-6 text-green-400" />
              <h4 className="text-white font-medium">Longue traîne</h4>
            </div>
            <p className="text-gray-400 text-sm">Réponse ciblée (500+ mots) pour question spécifique</p>
            <Button className="w-full mt-4 bg-green-500/20 text-green-400 hover:bg-green-500/30">
              <Play className="h-4 w-4 mr-2" />
              Générer
            </Button>
          </Card>
        </div>
      </Card>

      {/* Capsules virales */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-pink-400" />
          Capsules Virales
        </h3>
        <p className="text-gray-400 mb-4">
          Créez du contenu partageable pour les réseaux sociaux basé sur le Knowledge Layer.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['Fait intéressant', 'Quiz', 'Conseil d\'expert', 'Infographie'].map((type) => (
            <Button key={type} variant="outline" className="border-pink-500/30 text-pink-400 hover:bg-pink-500/20">
              {type}
            </Button>
          ))}
        </div>
      </Card>

      {/* JSON-LD Generator */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Code2 className="h-5 w-5 text-purple-400" />
          Générateur JSON-LD
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {['Article', 'HowTo', 'FAQPage', 'LocalBusiness', 'Breadcrumb'].map((schema) => (
            <Button key={schema} variant="outline" className="border-purple-500/30 text-purple-400 hover:bg-purple-500/20">
              <Code2 className="h-4 w-4 mr-2" />
              {schema}
            </Button>
          ))}
        </div>
      </Card>
    </div>
  );

  return (
    <div data-testid="admin-seo-module" className="space-y-6">
      {/* Modal Documentation SEO */}
      {showDocumentation && documentation && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="bg-[#0f0f1a] border border-[#F5A623]/30 rounded-xl w-full max-w-5xl max-h-[90vh] flex flex-col">
            {/* Header du modal */}
            <div className="flex items-center justify-between p-4 border-b border-[#F5A623]/20">
              <div className="flex items-center gap-3">
                <BookOpen className="h-6 w-6 text-[#F5A623]" />
                <div>
                  <h3 className="text-xl font-bold text-white">{documentation.title}</h3>
                  <p className="text-gray-400 text-sm">Version {documentation.version} • {documentation.last_updated}</p>
                </div>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowDocumentation(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            {/* Sommaire */}
            <div className="p-4 border-b border-[#F5A623]/10 bg-[#1a1a2e]/50">
              <p className="text-[#F5A623] text-sm font-medium mb-2">Sommaire ({documentation.sections?.length} sections)</p>
              <div className="flex flex-wrap gap-2">
                {documentation.sections?.map((section, idx) => (
                  <Badge key={idx} variant="outline" className="text-gray-400 border-gray-600 text-xs">
                    {idx + 1}. {section}
                  </Badge>
                ))}
              </div>
            </div>
            
            {/* Contenu de la documentation */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="prose prose-invert max-w-none">
                <pre className="whitespace-pre-wrap text-gray-300 text-sm font-mono bg-[#1a1a2e] p-4 rounded-lg overflow-x-auto">
                  {documentation.content}
                </pre>
              </div>
            </div>
            
            {/* Footer du modal */}
            <div className="p-4 border-t border-[#F5A623]/20 flex justify-end gap-3">
              <Button 
                variant="outline" 
                className="border-gray-600 text-gray-400"
                onClick={() => setShowDocumentation(false)}
              >
                Fermer
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Search className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">SEO Engine V5</h2>
            <p className="text-gray-400 text-sm">Plan SEO BIONIC +300%</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Bouton Documentation SEO Interne */}
          <Button
            data-testid="seo-documentation-btn"
            onClick={loadDocumentation}
            disabled={loadingDoc}
            className="bg-[#1a1a2e] hover:bg-[#2a2a4e] text-[#F5A623] border border-[#F5A623]/30"
          >
            {loadingDoc ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <BookOpen className="h-4 w-4 mr-2" />
            )}
            Documentation SEO interne
          </Button>
          <Badge className="bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30 px-4 py-2">
            <Globe className="h-4 w-4 mr-2 inline" />
            LEGO V5 Isolé
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#F5A623]/10 pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            data-testid={`seo-tab-${tab.id}`}
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
          {activeTab === 'clusters' && renderClusters()}
          {activeTab === 'pages' && renderPages()}
          {activeTab === 'jsonld' && renderJsonLD()}
          {activeTab === 'analytics' && renderAnalytics()}
          {activeTab === 'automation' && renderAutomation()}
          {activeTab === 'factory' && renderFactory()}
        </>
      )}
    </div>
  );
};

export { AdminSEO };
export default AdminSEO;
