/**
 * AdminKnowledge - V5-ULTIME Administration Premium
 * ==================================================
 * 
 * Module d'administration du BIONIC Knowledge Layer.
 * - Dashboard et statistiques
 * - Gestion des espèces
 * - Gestion des règles comportementales
 * - Gestion des sources
 * - Modèles saisonniers
 * - Pipeline de validation
 * 
 * Module isolé - Architecture LEGO V5.
 */

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Brain, LayoutDashboard, Bug, BookOpen, Calendar,
  CheckCircle, Search, RefreshCw, Leaf, TreePine, Target,
  ThermometerSun, Wind, Droplets, MapPin, Clock, Gauge,
  ChevronRight, AlertTriangle, Shield, Star
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const AdminKnowledge = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [species, setSpecies] = useState([]);
  const [rules, setRules] = useState([]);
  const [sources, setSources] = useState([]);
  const [seasonalModels, setSeasonalModels] = useState([]);
  const [variables, setVariables] = useState([]);
  const [validation, setValidation] = useState(null);
  const [filters, setFilters] = useState({ species: 'all', confidence: 'all', search: '' });

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'dashboard':
          const dashRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/dashboard`);
          const dashData = await dashRes.json();
          if (dashData.success) setStats(dashData.stats);
          break;
        case 'species':
          const speciesRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/species`);
          const speciesData = await speciesRes.json();
          if (speciesData.success) setSpecies(speciesData.species);
          break;
        case 'rules':
          const rulesRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/rules`);
          const rulesData = await rulesRes.json();
          if (rulesData.success) setRules(rulesData.rules);
          break;
        case 'sources':
          const sourcesRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/sources`);
          const sourcesData = await sourcesRes.json();
          if (sourcesData.success) setSources(sourcesData.sources);
          break;
        case 'seasonal':
          const seasonalRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/seasonal`);
          const seasonalData = await seasonalRes.json();
          if (seasonalData.success) setSeasonalModels(seasonalData.models);
          break;
        case 'variables':
          const varsRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/variables`);
          const varsData = await varsRes.json();
          if (varsData.success) setVariables(varsData.variables);
          break;
        case 'validation':
          const validRes = await fetch(`${API_BASE}/api/v1/bionic/knowledge/validation/report`);
          const validData = await validRes.json();
          setValidation(validData);
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'species', label: 'Espèces', icon: Leaf },
    { id: 'rules', label: 'Règles', icon: Target },
    { id: 'sources', label: 'Sources', icon: BookOpen },
    { id: 'seasonal', label: 'Saisonnier', icon: Calendar },
    { id: 'variables', label: 'Variables', icon: Gauge },
    { id: 'validation', label: 'Validation', icon: CheckCircle }
  ];

  const getSpeciesIcon = (category) => {
    const icons = {
      cervidae: '🦌',
      ursidae: '🐻',
      canidae: '🐺',
      anatidae: '🦆'
    };
    return icons[category] || '🦌';
  };

  const getConfidenceBadge = (confidence) => {
    const styles = {
      scientific: 'bg-green-500/20 text-green-400 border-green-500/30',
      empirical: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      theoretical: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      hybrid: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    };
    return (
      <Badge className={`${styles[confidence] || styles.empirical} border`}>
        {confidence?.toUpperCase()}
      </Badge>
    );
  };

  // ============ DASHBOARD ============
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Espèces</p>
              <p className="text-2xl font-bold text-white">{stats?.species?.total || 0}</p>
            </div>
            <Leaf className="h-8 w-8 text-[#F5A623]" />
          </div>
          <p className="text-xs text-green-400 mt-2">
            {stats?.species?.base || 0} base • {stats?.species?.custom || 0} custom
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Règles actives</p>
              <p className="text-2xl font-bold text-green-400">{stats?.rules?.active || 0}</p>
            </div>
            <Target className="h-8 w-8 text-green-400" />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {stats?.rules?.by_confidence?.scientific || 0} scientifiques
          </p>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Sources vérifiées</p>
              <p className="text-2xl font-bold text-blue-400">{stats?.sources?.verified || 0}</p>
            </div>
            <BookOpen className="h-8 w-8 text-blue-400" />
          </div>
        </Card>

        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Santé données</p>
              <p className="text-2xl font-bold text-[#F5A623]">
                {((stats?.validation?.health_score || 0) * 100).toFixed(0)}%
              </p>
            </div>
            <Shield className="h-8 w-8 text-[#F5A623]" />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {stats?.validation?.critical_issues || 0} issues critiques
          </p>
        </Card>
      </div>

      {/* Règles par espèce */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Target className="h-5 w-5 text-[#F5A623]" />
          Règles comportementales par espèce
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(stats?.rules?.by_species || {}).map(([species, count]) => (
            <div key={species} className="p-4 bg-[#1a1a2e] rounded-lg text-center">
              <span className="text-3xl">{getSpeciesIcon(species === 'moose' || species === 'deer' || species === 'caribou' ? 'cervidae' : species === 'bear' ? 'ursidae' : 'cervidae')}</span>
              <p className="text-white font-medium capitalize mt-2">{species}</p>
              <p className="text-[#F5A623] text-xl font-bold">{count}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Modèles saisonniers */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-[#F5A623]" />
          Modèles saisonniers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(stats?.seasonal_models?.by_species || {}).map(([species, count]) => (
            <div key={species} className="p-4 bg-[#1a1a2e] rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getSpeciesIcon(species === 'moose' || species === 'deer' || species === 'caribou' ? 'cervidae' : species === 'bear' ? 'ursidae' : 'cervidae')}</span>
                <p className="text-white font-medium capitalize">{species}</p>
              </div>
              <Badge className="bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30">
                {count} modèle(s)
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  // ============ SPECIES ============
  const renderSpecies = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {species.map((sp) => (
          <Card key={sp.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
            <div className="flex items-center gap-4">
              <span className="text-4xl">{getSpeciesIcon(sp.category)}</span>
              <div className="flex-1">
                <p className="text-white font-bold text-lg">{sp.common_name_fr}</p>
                <p className="text-gray-400 text-sm italic">{sp.scientific_name}</p>
                <p className="text-[#F5A623] text-sm mt-1">{sp.hunting_season_fr}</p>
              </div>
              <Badge className="bg-blue-500/20 text-blue-400 border border-blue-500/30">
                {sp.category}
              </Badge>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {sp.primary_regions?.map((region) => (
                <Badge key={region} variant="outline" className="text-gray-400 border-gray-600">
                  {region}
                </Badge>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // ============ RULES ============
  const renderRules = () => (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <select
          value={filters.species}
          onChange={(e) => setFilters({ ...filters, species: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Toutes espèces</option>
          <option value="moose">Orignal</option>
          <option value="deer">Cerf</option>
          <option value="bear">Ours</option>
        </select>
        <select
          value={filters.confidence}
          onChange={(e) => setFilters({ ...filters, confidence: e.target.value })}
          className="bg-[#1a1a2e] border border-[#F5A623]/20 text-white px-4 py-2 rounded-lg"
        >
          <option value="all">Toutes confiances</option>
          <option value="scientific">Scientifique</option>
          <option value="empirical">Empirique</option>
        </select>
        <Button onClick={loadData} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Rules list */}
      <div className="space-y-3">
        {rules
          .filter(r => filters.species === 'all' || r.species?.includes(filters.species))
          .filter(r => filters.confidence === 'all' || r.confidence === filters.confidence)
          .map((rule) => (
          <Card key={rule.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Target className="h-5 w-5 text-[#F5A623]" />
                  <p className="text-white font-semibold">{rule.name_fr}</p>
                  {getConfidenceBadge(rule.confidence)}
                </div>
                <p className="text-gray-400 text-sm">{rule.description_fr}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {rule.species?.map((sp) => (
                    <Badge key={sp} className="bg-[#1a1a2e] text-gray-300 border border-gray-600">
                      {sp}
                    </Badge>
                  ))}
                  {rule.tags?.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-[#F5A623] border-[#F5A623]/30">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="text-right">
                <p className="text-[#F5A623] font-bold text-lg">
                  {(rule.confidence_score * 100).toFixed(0)}%
                </p>
                <p className="text-gray-500 text-xs">confiance</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // ============ SOURCES ============
  const renderSources = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((source) => (
          <Card key={source.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
            <div className="flex items-start gap-4">
              <BookOpen className="h-8 w-8 text-[#F5A623] flex-shrink-0" />
              <div className="flex-1">
                <p className="text-white font-semibold">{source.name}</p>
                <p className="text-gray-400 text-sm">{source.source_type}</p>
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-400" />
                    <span className="text-white text-sm">{(source.reliability_score * 100).toFixed(0)}%</span>
                  </div>
                  {source.peer_reviewed && (
                    <Badge className="bg-green-500/20 text-green-400 border border-green-500/30">
                      Peer Reviewed
                    </Badge>
                  )}
                  {source.verified && (
                    <Badge className="bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      Vérifié
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // ============ SEASONAL ============
  const renderSeasonal = () => (
    <div className="space-y-4">
      {seasonalModels.map((model) => (
        <Card key={model.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Calendar className="h-6 w-6 text-[#F5A623]" />
              <div>
                <p className="text-white font-semibold capitalize">{model.species_id} - {model.region}</p>
                <p className="text-gray-400 text-sm">Année {model.year}</p>
              </div>
            </div>
            <Badge className="bg-green-500/20 text-green-400 border border-green-500/30">
              {(model.accuracy_score * 100).toFixed(0)}% précision
            </Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
            {model.phases?.map((phase, idx) => (
              <div key={idx} className="p-2 bg-[#1a1a2e] rounded-lg text-center">
                <p className="text-white text-xs font-medium">{phase.name_fr}</p>
                <p className="text-[#F5A623] text-sm font-bold">{(phase.activity_level * 100).toFixed(0)}%</p>
                <p className="text-gray-500 text-xs">{phase.start_month}/{phase.start_day}</p>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );

  // ============ VARIABLES ============
  const renderVariables = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {variables.map((variable) => (
          <Card key={variable.id} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
            <div className="flex items-center gap-3 mb-3">
              {variable.category === 'climate' && <ThermometerSun className="h-5 w-5 text-red-400" />}
              {variable.category === 'terrain' && <MapPin className="h-5 w-5 text-green-400" />}
              {variable.category === 'vegetation' && <TreePine className="h-5 w-5 text-emerald-400" />}
              {variable.category === 'hydrology' && <Droplets className="h-5 w-5 text-blue-400" />}
              {variable.category === 'human_impact' && <AlertTriangle className="h-5 w-5 text-yellow-400" />}
              <div>
                <p className="text-white font-medium">{variable.name_fr}</p>
                <p className="text-gray-400 text-xs">{variable.unit}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-gray-400 border-gray-600">
                {variable.category}
              </Badge>
              <Badge variant="outline" className="text-gray-400 border-gray-600">
                {variable.update_frequency}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  // ============ VALIDATION ============
  const renderValidation = () => (
    <div className="space-y-6">
      {validation && (
        <>
          {/* Health Score */}
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold text-lg">Score de santé global</h3>
                <p className="text-gray-400 text-sm">Dernière validation: {new Date(validation.timestamp).toLocaleString('fr-CA')}</p>
              </div>
              <div className="text-center">
                <p className={`text-4xl font-bold ${validation.overall_health > 0.8 ? 'text-green-400' : validation.overall_health > 0.5 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {(validation.overall_health * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </Card>

          {/* Validation Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {['species', 'rules', 'sources', 'seasonal_models'].map((type) => (
              <Card key={type} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
                <p className="text-white font-medium capitalize mb-2">{type.replace('_', ' ')}</p>
                <div className="flex justify-between">
                  <div>
                    <p className="text-green-400 text-xl font-bold">{validation[type]?.valid || 0}</p>
                    <p className="text-gray-500 text-xs">valides</p>
                  </div>
                  <div>
                    <p className="text-red-400 text-xl font-bold">{validation[type]?.invalid || 0}</p>
                    <p className="text-gray-500 text-xs">invalides</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xl font-bold">{validation[type]?.total || 0}</p>
                    <p className="text-gray-500 text-xs">total</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Critical Issues */}
          {validation.critical_issues?.length > 0 && (
            <Card className="bg-[#0f0f1a] border-red-500/30 p-6">
              <h3 className="text-red-400 font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Issues critiques ({validation.critical_issues.length})
              </h3>
              <div className="space-y-2">
                {validation.critical_issues.map((issue, idx) => (
                  <div key={idx} className="p-3 bg-red-500/10 rounded-lg">
                    <p className="text-gray-300 text-sm">{issue}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );

  return (
    <div data-testid="admin-knowledge-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Knowledge Layer</h2>
            <p className="text-gray-400 text-sm">BIONIC Intelligence scientifique</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#F5A623]/10 pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            data-testid={`knowledge-tab-${tab.id}`}
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
          {activeTab === 'species' && renderSpecies()}
          {activeTab === 'rules' && renderRules()}
          {activeTab === 'sources' && renderSources()}
          {activeTab === 'seasonal' && renderSeasonal()}
          {activeTab === 'variables' && renderVariables()}
          {activeTab === 'validation' && renderValidation()}
        </>
      )}
    </div>
  );
};

export { AdminKnowledge };
export default AdminKnowledge;
