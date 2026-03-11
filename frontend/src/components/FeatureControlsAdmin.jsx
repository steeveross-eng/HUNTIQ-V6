/**
 * FeatureControlsAdmin - Admin panel for controlling application features
 * Allows toggling features ON/OFF with full audit log
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Settings2,
  Power,
  PowerOff,
  History,
  RefreshCw,
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  Filter,
  ToggleLeft,
  ToggleRight,
  Users,
  Bell,
  Megaphone,
  ShoppingCart,
  Gift,
  UserCog,
  Brain,
  Target,
  MessageSquare,
  MessageCircle,
  Heart,
  Mail,
  Newspaper,
  CreditCard,
  MapPin,
  Wallet,
  UserPlus,
  Fingerprint,
  KeyRound,
  Sparkles,
  Tags,
  BookUser,
  Clock,
  User,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Icon mapping
const ICON_MAP = {
  MessageSquare, MessageCircle, Heart, Users, Bell, Mail, Newspaper,
  Megaphone: Megaphone, Search, ShoppingCart: ShoppingCart, CreditCard, MapPin,
  Gift, Wallet, UserPlus, Fingerprint, KeyRound, Sparkles, Brain, Tags,
  Target, BookUser, UserCog, Settings2
};

const getCategoryIcon = (iconName) => {
  const icons = {
    Users, Bell, Megaphone, ShoppingCart, Gift, UserCog, Brain, Target
  };
  return icons[iconName] || Settings2;
};

const FeatureControlsAdmin = ({ adminEmail = "admin@chasse.ca" }) => {
  const [features, setFeatures] = useState({});
  const [categories, setCategories] = useState({});
  const [summary, setSummary] = useState({ total: 0, enabled: 0, disabled: 0 });
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState({});
  const [logs, setLogs] = useState([]);
  const [logsStats, setLogsStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [activeTab, setActiveTab] = useState('controls');

  // Fetch feature status
  const fetchFeatures = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/feature-controls/status`);
      setFeatures(response.data.features);
      setCategories(response.data.categories);
      setSummary(response.data.summary);
      
      // Expand all categories by default
      const expanded = {};
      Object.keys(response.data.categories).forEach(cat => {
        expanded[cat] = true;
      });
      setExpandedCategories(expanded);
    } catch (error) {
      console.error('Error fetching features:', error);
      toast.error('Erreur lors du chargement des fonctionnalités');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch logs
  const fetchLogs = useCallback(async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([
        axios.get(`${API}/feature-controls/logs?limit=100`),
        axios.get(`${API}/feature-controls/logs/stats`)
      ]);
      setLogs(logsRes.data.logs);
      setLogsStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  }, []);

  useEffect(() => {
    fetchFeatures();
    fetchLogs();
  }, [fetchFeatures, fetchLogs]);

  // Toggle single feature
  const handleToggle = async (featureId, currentValue) => {
    setToggling(prev => ({ ...prev, [featureId]: true }));
    
    try {
      const response = await axios.post(
        `${API}/feature-controls/toggle?admin_email=${encodeURIComponent(adminEmail)}`,
        {
          feature_id: featureId,
          enabled: !currentValue
        }
      );
      
      if (response.data.success) {
        toast.success(response.data.message);
        fetchFeatures();
        fetchLogs();
      }
    } catch (error) {
      toast.error('Erreur lors de la modification');
    } finally {
      setToggling(prev => ({ ...prev, [featureId]: false }));
    }
  };

  // Toggle entire category
  const handleToggleCategory = async (category, enable) => {
    const categoryFeatures = Object.entries(features)
      .filter(([_, f]) => f.category === category)
      .map(([id]) => id);
    
    categoryFeatures.forEach(id => {
      setToggling(prev => ({ ...prev, [id]: true }));
    });
    
    try {
      const response = await axios.post(
        `${API}/feature-controls/toggle-category?category=${category}&enabled=${enable}&admin_email=${encodeURIComponent(adminEmail)}`
      );
      
      if (response.data.success) {
        toast.success(response.data.message);
        fetchFeatures();
        fetchLogs();
      }
    } catch (error) {
      toast.error('Erreur lors de la modification');
    } finally {
      categoryFeatures.forEach(id => {
        setToggling(prev => ({ ...prev, [id]: false }));
      });
    }
  };

  // Reset to defaults
  const handleResetDefaults = async () => {
    try {
      const response = await axios.post(
        `${API}/feature-controls/reset-defaults?admin_email=${encodeURIComponent(adminEmail)}`
      );
      
      if (response.data.success) {
        toast.success(response.data.message);
        setShowResetDialog(false);
        fetchFeatures();
        fetchLogs();
      }
    } catch (error) {
      toast.error('Erreur lors de la réinitialisation');
    }
  };

  // Filter features
  const filteredFeatures = Object.entries(features).filter(([id, feature]) => {
    const matchesSearch = searchTerm === '' || 
      feature.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feature.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || feature.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Group features by category
  const featuresByCategory = {};
  filteredFeatures.forEach(([id, feature]) => {
    if (!featuresByCategory[feature.category]) {
      featuresByCategory[feature.category] = [];
    }
    featuresByCategory[feature.category].push({ id, ...feature });
  });

  // Format date for logs
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('fr-CA', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="feature-controls-admin">
      {/* Header */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#f5a623]/20 flex items-center justify-center">
                <Settings2 className="h-6 w-6 text-[#f5a623]" />
              </div>
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  Contrôle des Fonctionnalités
                  <Badge className="bg-blue-500/20 text-blue-400">{summary.total} modules</Badge>
                </CardTitle>
                <CardDescription>
                  Activez ou désactivez les fonctionnalités de l'application en temps réel
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button variant="outline" size="sm" onClick={fetchFeatures}>
                <RefreshCw className="h-4 w-4 mr-1" />
                Actualiser
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-red-400 border-red-400/50 hover:bg-red-400/10"
                onClick={() => setShowResetDialog(true)}
              >
                <AlertTriangle className="h-4 w-4 mr-1" />
                Réinitialiser
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-background rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-white">{summary.total}</p>
              <p className="text-gray-400 text-sm">Total</p>
            </div>
            <div className="bg-green-500/10 rounded-lg p-4 text-center border border-green-500/30">
              <p className="text-3xl font-bold text-green-400">{summary.enabled}</p>
              <p className="text-green-400 text-sm flex items-center justify-center gap-1">
                <Power className="h-4 w-4" /> Activées
              </p>
            </div>
            <div className="bg-red-500/10 rounded-lg p-4 text-center border border-red-500/30">
              <p className="text-3xl font-bold text-red-400">{summary.disabled}</p>
              <p className="text-red-400 text-sm flex items-center justify-center gap-1">
                <PowerOff className="h-4 w-4" /> Désactivées
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-background">
          <TabsTrigger value="controls" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <ToggleLeft className="h-4 w-4 mr-2" />
            Contrôles
          </TabsTrigger>
          <TabsTrigger value="logs" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <History className="h-4 w-4 mr-2" />
            Historique
          </TabsTrigger>
        </TabsList>

        {/* Controls Tab */}
        <TabsContent value="controls" className="space-y-4">
          {/* Filters */}
          <Card className="bg-card border-border">
            <CardContent className="pt-4">
              <div className="flex gap-4 flex-wrap">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Rechercher une fonctionnalité..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="bg-background pl-10"
                    />
                  </div>
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-[200px] bg-background">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Catégorie" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Toutes les catégories</SelectItem>
                    {Object.entries(categories)
                      .sort((a, b) => a[1].order - b[1].order)
                      .map(([catId, cat]) => (
                        <SelectItem key={catId} value={catId}>{cat.name}</SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Features by Category */}
          {Object.entries(categories)
            .sort((a, b) => a[1].order - b[1].order)
            .filter(([catId]) => selectedCategory === 'all' || selectedCategory === catId)
            .filter(([catId]) => featuresByCategory[catId]?.length > 0)
            .map(([catId, category]) => {
              const CategoryIcon = getCategoryIcon(category.icon);
              const categoryFeatures = featuresByCategory[catId] || [];
              const enabledCount = categoryFeatures.filter(f => f.enabled).length;
              const allEnabled = enabledCount === categoryFeatures.length;
              const noneEnabled = enabledCount === 0;
              const isExpanded = expandedCategories[catId];

              return (
                <Card key={catId} className="bg-card border-border overflow-hidden">
                  <CardHeader 
                    className="cursor-pointer hover:bg-background/50 transition-colors"
                    onClick={() => setExpandedCategories(prev => ({ ...prev, [catId]: !prev[catId] }))}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#f5a623]/20 flex items-center justify-center">
                          <CategoryIcon className="h-5 w-5 text-[#f5a623]" />
                        </div>
                        <div>
                          <CardTitle className="text-white text-lg flex items-center gap-2">
                            {category.name}
                            <Badge variant="outline" className="text-xs">
                              {enabledCount}/{categoryFeatures.length}
                            </Badge>
                          </CardTitle>
                          <CardDescription className="text-xs">
                            {category.name_en}
                          </CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Category toggle buttons */}
                        <Button
                          size="sm"
                          variant={allEnabled ? "default" : "outline"}
                          className={allEnabled ? "bg-green-600 hover:bg-green-700" : ""}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleCategory(catId, true);
                          }}
                          disabled={allEnabled}
                        >
                          <Power className="h-3 w-3 mr-1" />
                          Tout activer
                        </Button>
                        <Button
                          size="sm"
                          variant={noneEnabled ? "default" : "outline"}
                          className={noneEnabled ? "bg-red-600 hover:bg-red-700" : ""}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleCategory(catId, false);
                          }}
                          disabled={noneEnabled}
                        >
                          <PowerOff className="h-3 w-3 mr-1" />
                          Tout désactiver
                        </Button>
                        {isExpanded ? (
                          <ChevronUp className="h-5 w-5 text-gray-400" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  
                  {isExpanded && (
                    <CardContent className="pt-0">
                      <div className="space-y-2">
                        {categoryFeatures.map((feature) => {
                          const FeatureIcon = ICON_MAP[feature.icon] || Settings2;
                          const isToggling = toggling[feature.id];
                          
                          return (
                            <div 
                              key={feature.id}
                              className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                                feature.enabled 
                                  ? 'bg-green-500/5 border-green-500/30' 
                                  : 'bg-red-500/5 border-red-500/30'
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                                  feature.enabled ? 'bg-green-500/20' : 'bg-red-500/20'
                                }`}>
                                  <FeatureIcon className={`h-4 w-4 ${
                                    feature.enabled ? 'text-green-400' : 'text-red-400'
                                  }`} />
                                </div>
                                <div>
                                  <p className="text-white font-medium text-sm flex items-center gap-2">
                                    {feature.name}
                                    {feature.is_default && (
                                      <Badge variant="outline" className="text-[10px] text-gray-500">
                                        défaut
                                      </Badge>
                                    )}
                                  </p>
                                  <p className="text-gray-500 text-xs">{feature.description}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-3">
                                <Badge className={feature.enabled 
                                  ? 'bg-green-500/20 text-green-400' 
                                  : 'bg-red-500/20 text-red-400'
                                }>
                                  {feature.enabled ? 'ON' : 'OFF'}
                                </Badge>
                                {isToggling ? (
                                  <Loader2 className="h-5 w-5 animate-spin text-[#f5a623]" />
                                ) : (
                                  <Switch
                                    checked={feature.enabled}
                                    onCheckedChange={() => handleToggle(feature.id, feature.enabled)}
                                    className="data-[state=checked]:bg-green-500"
                                  />
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  )}
                </Card>
              );
            })}
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          {/* Logs Stats */}
          {logsStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-card border-border">
                <CardContent className="pt-4 text-center">
                  <p className="text-2xl font-bold text-white">{logsStats.total_changes}</p>
                  <p className="text-gray-400 text-xs">Modifications totales</p>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-4 text-center">
                  <p className="text-2xl font-bold text-[#f5a623]">{logsStats.changes_last_24h}</p>
                  <p className="text-gray-400 text-xs">Dernières 24h</p>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-4">
                  <p className="text-gray-400 text-xs mb-1">Top fonctionnalité modifiée</p>
                  <p className="text-white text-sm font-medium truncate">
                    {logsStats.by_feature[0]?.feature_id || '-'}
                  </p>
                  <p className="text-[#f5a623] text-xs">
                    {logsStats.by_feature[0]?.count || 0} fois
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-4">
                  <p className="text-gray-400 text-xs mb-1">Admin le plus actif</p>
                  <p className="text-white text-sm font-medium truncate">
                    {logsStats.by_admin[0]?.admin || '-'}
                  </p>
                  <p className="text-[#f5a623] text-xs">
                    {logsStats.by_admin[0]?.count || 0} modifications
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Logs Table */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <History className="h-5 w-5 text-[#f5a623]" />
                Historique des modifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              {logs.length === 0 ? (
                <p className="text-gray-400 text-center py-8">Aucune modification enregistrée</p>
              ) : (
                <div className="max-h-[500px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-border">
                        <TableHead className="text-gray-400">Date</TableHead>
                        <TableHead className="text-gray-400">Fonctionnalité</TableHead>
                        <TableHead className="text-gray-400">Changement</TableHead>
                        <TableHead className="text-gray-400">Admin</TableHead>
                        <TableHead className="text-gray-400">Raison</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {logs.map((log, idx) => (
                        <TableRow key={idx} className="border-border">
                          <TableCell className="text-gray-400 text-xs whitespace-nowrap">
                            <Clock className="h-3 w-3 inline mr-1" />
                            {formatDate(log.changed_at)}
                          </TableCell>
                          <TableCell className="text-white font-medium">
                            {log.feature_name}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Badge className={log.old_value 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-red-500/20 text-red-400'
                              }>
                                {log.old_value ? 'ON' : 'OFF'}
                              </Badge>
                              <span className="text-gray-500">→</span>
                              <Badge className={log.new_value 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-red-500/20 text-red-400'
                              }>
                                {log.new_value ? 'ON' : 'OFF'}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-400 text-xs">
                            <User className="h-3 w-3 inline mr-1" />
                            {log.changed_by}
                          </TableCell>
                          <TableCell className="text-gray-500 text-xs max-w-[200px] truncate">
                            {log.reason || '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Reset Confirmation Dialog */}
      <Dialog open={showResetDialog} onOpenChange={setShowResetDialog}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              Réinitialiser aux valeurs par défaut?
            </DialogTitle>
            <DialogDescription>
              Cette action va réinitialiser toutes les fonctionnalités à leurs valeurs par défaut.
              Les fonctionnalités qui étaient désactivées seront réactivées et vice-versa.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowResetDialog(false)}>
              Annuler
            </Button>
            <Button 
              className="bg-red-600 hover:bg-red-700 text-white"
              onClick={handleResetDefaults}
            >
              Réinitialiser
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FeatureControlsAdmin;
