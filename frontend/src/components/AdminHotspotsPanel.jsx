/**
 * AdminHotspotsPanel - Hotspots Administration Panel
 * Phase P6.5 - Integrated in Admin "Hotspots" tab
 * 
 * ADMIN SEULEMENT - Cette section affiche TOUS les hotspots de TOUS les membres
 * pour la gestion, modération et supervision globale.
 * Ces données ne sont jamais partagées ni accessibles aux utilisateurs.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { MapPin, ExternalLink, Filter, RefreshCw, ChevronDown, ChevronUp, Shield, Star, Home, Building, TreeDeciduous, User, PauseCircle, Flame } from 'lucide-react';
import { useAuth } from './GlobalAuth';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Hotspot category colors
const CATEGORY_COLORS = {
  standard: 'bg-gray-500',
  premium: 'bg-amber-500',
  land_rental: 'bg-emerald-500',
  chalet: 'bg-orange-500',
  environmental: 'bg-blue-500',
  user_personal: 'bg-purple-500',
  inactive: 'bg-red-500'
};

// Category labels in French
const CATEGORY_LABELS = {
  standard: 'Standard',
  premium: 'Premium',
  land_rental: 'Terre à louer',
  chalet: 'Chalet',
  environmental: 'Environnemental',
  user_personal: 'Personnel (membre)',
  inactive: 'Inactif'
};

// Category icons - Map to Lucide components
const CategoryIconComponent = ({ category, className = "h-6 w-6" }) => {
  const icons = {
    standard: MapPin,
    premium: Star,
    land_rental: Home,
    chalet: Building,
    environmental: TreeDeciduous,
    user_personal: User,
    inactive: PauseCircle
  };
  const IconComp = icons[category] || MapPin;
  return <IconComp className={className} />;
};

// Category icons - Using Lucide icon names
const CATEGORY_ICONS = {
  standard: 'mapPin',
  premium: 'star',
  land_rental: 'home',
  chalet: 'building',
  environmental: 'treeDeciduous',
  user_personal: 'user',
  inactive: 'pauseCircle'
};

const AdminHotspotsPanel = () => {
  const navigate = useNavigate();
  const { token: authToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [hotspots, setHotspots] = useState([]);
  const [hotspotStats, setHotspotStats] = useState({});
  const [categoryFilter, setCategoryFilter] = useState('');
  const [expanded, setExpanded] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Get token from auth context or localStorage
  const token = authToken || localStorage.getItem('auth_token');

  // Load hotspots (ALL hotspots for admin)
  const loadHotspots = useCallback(async () => {
    if (!token) {
      setAuthError('Veuillez vous connecter à votre compte BIONIC™ pour accéder aux données des hotspots.');
      setLoading(false);
      return;
    }
    
    setAuthError(null);
    
    try {
      setLoading(true);
      let url = `${API_URL}/api/admin/geo/hotspots?limit=200`;
      if (categoryFilter) {
        url += `&category=${categoryFilter}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        setAuthError('Session expirée. Veuillez vous reconnecter à votre compte BIONIC™.');
        return;
      }
      
      if (response.status === 403) {
        setAuthError('Accès réservé aux administrateurs avec compte BIONIC™ admin.');
        return;
      }
      
      const data = await response.json();
      setHotspots(data.hotspots || []);
      setHotspotStats(data.by_category || {});
    } catch (error) {
      console.error('Error loading hotspots:', error);
      toast.error('Erreur lors du chargement des hotspots');
    } finally {
      setLoading(false);
    }
  }, [categoryFilter, token]);

  // Initial load
  useEffect(() => {
    loadHotspots();
  }, [loadHotspots]);

  // Navigate to map centered on hotspot
  const viewOnMap = (hotspot) => {
    if (hotspot.latitude && hotspot.longitude) {
      navigate(`/map?lat=${hotspot.latitude}&lng=${hotspot.longitude}&zoom=17`);
    } else {
      toast.error('Coordonnées non disponibles');
    }
  };

  // Open full admin page
  const openFullAdmin = () => {
    navigate('/admin/geo');
  };

  // Calculate total
  const totalHotspots = Object.values(hotspotStats).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Header with admin warning */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Flame className="h-6 w-6 text-orange-500" />
              Gestion des Hotspots
              <Badge className="bg-red-600 ml-2">
                <Shield className="h-3 w-3 mr-1" />
                ADMIN
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={openFullAdmin}
                className="text-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="h-4 w-4 mr-1" />
                Vue complète
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          
          {/* Admin Warning Banner */}
          <div className="mt-3 p-3 bg-amber-900/30 border border-amber-500/50 rounded-lg">
            <p className="text-amber-300 text-sm flex items-start gap-2">
              <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>
                <strong>Section strictement réservée aux administrateurs.</strong><br />
                Tous les hotspots de tous les membres y sont visibles pour gestion, modération et supervision globale.<br />
                Ces données ne sont jamais partagées ni accessibles aux utilisateurs.
              </span>
            </p>
          </div>
        </CardHeader>
      </Card>

      {expanded && (
        <>
          {/* Auth Error Banner */}
          {authError && (
            <Card className="bg-red-900/30 border-red-500/50">
              <CardContent className="p-4">
                <p className="text-red-300 text-sm flex items-start gap-2">
                  <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Authentification requise</strong><br />
                    {authError}<br />
                    <span className="text-xs text-red-400 mt-1 block">
                      Cliquez sur "Connexion" en haut de page pour vous authentifier avec votre compte admin BIONIC™.
                    </span>
                  </span>
                </p>
              </CardContent>
            </Card>
          )}

          {/* Quick Stats - All categories */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <Card 
                key={key} 
                className={`bg-slate-800/50 border-slate-700 cursor-pointer hover:border-slate-500 transition-colors ${categoryFilter === key ? 'ring-2 ring-blue-500' : ''}`}
                onClick={() => setCategoryFilter(categoryFilter === key ? '' : key)}
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-xs">{label}</p>
                      <p className="text-xl font-bold text-white">{hotspotStats[key] || 0}</p>
                    </div>
                    <CategoryIconComponent category={key} className="h-6 w-6 text-slate-400" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Hotspots List */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-lg">
                  Tous les Hotspots ({totalHotspots})
                  {categoryFilter && (
                    <Badge className={`ml-2 ${CATEGORY_COLORS[categoryFilter]}`}>
                      Filtre: {CATEGORY_LABELS[categoryFilter]}
                    </Badge>
                  )}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-slate-400" />
                  <select
                    className="bg-slate-700 text-white px-2 py-1 rounded text-sm"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <option value="">Toutes catégories</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                    <option value="land_rental">Terre à louer</option>
                    <option value="chalet">Chalet</option>
                    <option value="environmental">Environnemental</option>
                    <option value="user_personal">Personnel (membres)</option>
                    <option value="inactive">Inactif</option>
                  </select>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={loadHotspots}
                    disabled={loading}
                  >
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-slate-400">Chargement...</div>
              ) : hotspots.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  Aucun hotspot trouvé pour ce filtre.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-slate-400 pb-2 font-medium">Nom</th>
                        <th className="text-slate-400 pb-2 font-medium">Catégorie</th>
                        <th className="text-slate-400 pb-2 font-medium">Propriétaire</th>
                        <th className="text-slate-400 pb-2 font-medium">GPS</th>
                        <th className="text-slate-400 pb-2 font-medium">Statut</th>
                        <th className="text-slate-400 pb-2 font-medium">Confiance</th>
                        <th className="text-slate-400 pb-2 font-medium">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {hotspots.slice(0, 15).map((hotspot) => (
                        <tr key={hotspot.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              <CategoryIconComponent category={hotspot.category} className="h-4 w-4 text-slate-400" />
                              <span className="text-white">{hotspot.name}</span>
                            </div>
                          </td>
                          <td className="py-3">
                            <Badge className={CATEGORY_COLORS[hotspot.category]}>
                              {hotspot.category_label}
                            </Badge>
                          </td>
                          <td className="py-3 text-slate-400 text-xs">
                            {hotspot.user_id === 'system' ? (
                              <span className="text-blue-400">Système</span>
                            ) : (
                              <span>{hotspot.user_id?.substring(0, 15)}...</span>
                            )}
                          </td>
                          <td className="py-3 text-slate-400 font-mono text-xs">
                            {hotspot.latitude?.toFixed(4)}, {hotspot.longitude?.toFixed(4)}
                          </td>
                          <td className="py-3">
                            <span className={hotspot.active !== false ? 'text-emerald-400' : 'text-red-400'}>
                              {hotspot.status}
                            </span>
                          </td>
                          <td className="py-3">
                            {hotspot.confidence ? (
                              <Badge className={hotspot.confidence > 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}>
                                {(hotspot.confidence * 100).toFixed(0)}%
                              </Badge>
                            ) : '-'}
                          </td>
                          <td className="py-3">
                            <Button 
                              size="sm" 
                              variant="ghost"
                              className="text-blue-400 hover:text-blue-300 h-7 px-2"
                              onClick={() => viewOnMap(hotspot)}
                            >
                              <MapPin className="h-3 w-3 mr-1" />
                              Carte
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {hotspots.length > 15 && (
                    <div className="mt-4 text-center">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={openFullAdmin}
                      >
                        Voir les {hotspots.length - 15} autres hotspots
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default AdminHotspotsPanel;
