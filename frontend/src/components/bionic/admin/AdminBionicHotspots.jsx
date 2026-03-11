/**
 * AdminBionicHotspots - Module d'Administration des Hotspots BIONIC
 * ==================================================================
 * BIONIC V5 ULTIME - PHASE 5.7
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher la liste des hotspots analytiques BIONIC
 * - Permettre l'édition des métadonnées et scores
 * - Ajustement manuel des facteurs contributifs
 * - Visualisation en temps réel de l'impact sur le score final
 * - Sélection multiple pour affichage sur carte
 * - Préparation des hotspots pour la Marketplace
 * 
 * ISOLATION:
 * - Composant 100% présentationnel
 * - Aucune logique métier interne
 * - Toutes les actions via callbacks (props)
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  MapPin,
  Navigation,
  Target,
  Edit3,
  Save,
  X,
  Map,
  ShoppingBag,
  CheckSquare,
  Square,
  Filter,
  Search,
  RefreshCw,
  ChevronRight,
  Compass,
  Building,
  TreePine,
  Mountain,
  Waves,
  Home,
  Globe,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  Info,
  Eye,
  Loader2
} from 'lucide-react';

import { BIONIC_COLORS } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS - PALETTE BIONIC & CONFIGURATION
// =============================================================================

/**
 * Palette de couleurs BIONIC pour les scores (échelle 0-10)
 */
const SCORE_COLOR_PALETTE = {
  EXCELLENT: '#00A676',    // 9-10 : Vert analytique
  GOOD: '#C9A86A',         // 7-8  : Doré premium
  MODERATE: '#1E3A8A',     // 5-6  : Bleu profond
  POOR: '#C26A2E',         // 3-4  : Orange sobre
  CRITICAL: '#B91C1C'      // 0-2  : Rouge scientifique
};

/**
 * Facteurs contributifs au score
 */
const SCORE_FACTORS = [
  { key: 'habitat', label: 'Habitat', description: 'Qualité de l\'habitat naturel', icon: TreePine },
  { key: 'pressure', label: 'Pression', description: 'Niveau de pression de chasse', icon: AlertTriangle },
  { key: 'coverage', label: 'Couverture', description: 'Couverture végétale', icon: Mountain },
  { key: 'water', label: 'Eau', description: 'Proximité de sources d\'eau', icon: Waves },
  { key: 'accessibility', label: 'Accessibilité', description: 'Facilité d\'accès', icon: Navigation },
  { key: 'attractivity', label: 'Attractivité', description: 'Potentiel d\'attraction du gibier', icon: Target }
];

/**
 * Types de terrain
 */
const TERRAIN_TYPES = [
  { value: 'private', label: 'Terrain privé', icon: Home },
  { value: 'public', label: 'Terre publique', icon: Globe },
  { value: 'zec', label: 'ZEC', icon: TreePine },
  { value: 'pourvoirie', label: 'Pourvoirie', icon: Building },
  { value: 'reserve', label: 'Réserve faunique', icon: Mountain },
  { value: 'unknown', label: 'Inconnu', icon: MapPin }
];

/**
 * Obtenir la couleur pour un score donné (sur 10)
 */
const getScoreColor = (score) => {
  if (score >= 9) return SCORE_COLOR_PALETTE.EXCELLENT;
  if (score >= 7) return SCORE_COLOR_PALETTE.GOOD;
  if (score >= 5) return SCORE_COLOR_PALETTE.MODERATE;
  if (score >= 3) return SCORE_COLOR_PALETTE.POOR;
  return SCORE_COLOR_PALETTE.CRITICAL;
};

/**
 * Obtenir la catégorie qualitative
 */
const getScoreCategory = (score) => {
  if (score >= 7) return { label: 'FAVORABLE', color: SCORE_COLOR_PALETTE.EXCELLENT };
  if (score >= 5) return { label: 'MODÉRÉ', color: SCORE_COLOR_PALETTE.MODERATE };
  return { label: 'DÉFAVORABLE', color: SCORE_COLOR_PALETTE.CRITICAL };
};

/**
 * Icône de tendance
 */
const TrendIcon = ({ current, previous }) => {
  if (current > previous) return <TrendingUp className="w-3 h-3 text-green-400" />;
  if (current < previous) return <TrendingDown className="w-3 h-3 text-red-400" />;
  return <Minus className="w-3 h-3 text-gray-500" />;
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Barre de score visuelle
 */
const ScoreBar = ({ score, maxScore = 10, showLabel = true }) => {
  const percentage = (score / maxScore) * 100;
  const color = getScoreColor(score);
  
  return (
    <div className="flex items-center gap-2">
      <div 
        className="flex-1 h-2 rounded-full overflow-hidden"
        style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
      >
        <div 
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      {showLabel && (
        <span 
          className="text-sm font-mono font-semibold min-w-[2.5rem] text-right"
          style={{ color }}
        >
          {score.toFixed(1)}
        </span>
      )}
    </div>
  );
};

/**
 * Ligne d'information
 */
const InfoRow = ({ icon: Icon, label, value, valueColor }) => (
  <div className="flex items-center justify-between py-1.5">
    <div className="flex items-center gap-2 text-gray-400">
      <Icon className="w-3.5 h-3.5" />
      <span className="text-xs">{label}</span>
    </div>
    <span 
      className="text-xs font-medium"
      style={{ color: valueColor || 'white' }}
    >
      {value}
    </span>
  </div>
);

/**
 * Card d'un hotspot dans la liste
 */
const HotspotCard = ({
  hotspot,
  isSelected,
  isEditing,
  onSelect,
  onEdit,
  onViewOnMap,
  onSell,
  waypointDistance
}) => {
  const category = getScoreCategory(hotspot.score);
  const TerrainIcon = TERRAIN_TYPES.find(t => t.value === hotspot.terrainType)?.icon || MapPin;
  
  return (
    <Card 
      className={`border transition-all duration-200 ${
        isSelected 
          ? 'ring-2' 
          : 'hover:border-gray-600'
      }`}
      style={{ 
        backgroundColor: BIONIC_COLORS.black.elevated,
        borderColor: isSelected ? BIONIC_COLORS.gold.primary : BIONIC_COLORS.gray[800],
        ringColor: isSelected ? BIONIC_COLORS.gold.primary : 'transparent'
      }}
    >
      <CardContent className="p-4">
        {/* Header avec checkbox et nom */}
        <div className="flex items-start gap-3 mb-3">
          <Checkbox
            checked={isSelected}
            onCheckedChange={() => onSelect(hotspot.id)}
            className="mt-1 border-gray-600 data-[state=checked]:bg-[#C9A86A] data-[state=checked]:border-[#C9A86A]"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-white font-medium text-sm truncate">
                {hotspot.name}
              </h4>
              <Badge 
                className="text-[10px] px-1.5 py-0"
                style={{ 
                  backgroundColor: `${category.color}20`,
                  color: category.color
                }}
              >
                {category.label}
              </Badge>
            </div>
            <p className="text-gray-500 text-xs truncate">
              {hotspot.address || 'Adresse non disponible'}
            </p>
          </div>
          <div className="flex flex-col items-end">
            <span 
              className="text-lg font-bold font-mono"
              style={{ color: getScoreColor(hotspot.score) }}
            >
              {hotspot.score.toFixed(1)}
            </span>
            <span className="text-[10px] text-gray-500">/10</span>
          </div>
        </div>
        
        {/* Informations GPS et contextuelles */}
        <div 
          className="rounded-lg p-2.5 mb-3 space-y-1"
          style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
        >
          <InfoRow 
            icon={MapPin} 
            label="GPS" 
            value={`${hotspot.latitude?.toFixed(5)}, ${hotspot.longitude?.toFixed(5)}`} 
          />
          <InfoRow 
            icon={Globe} 
            label="Lieu" 
            value={`${hotspot.city || '—'}, ${hotspot.province || '—'}`} 
          />
          <InfoRow 
            icon={TerrainIcon} 
            label="Terrain" 
            value={TERRAIN_TYPES.find(t => t.value === hotspot.terrainType)?.label || 'Inconnu'} 
          />
          {hotspot.owner && (
            <InfoRow 
              icon={Home} 
              label="Propriétaire" 
              value={hotspot.owner} 
            />
          )}
          {waypointDistance !== null && (
            <InfoRow 
              icon={Navigation} 
              label="Distance waypoint" 
              value={`${waypointDistance.toFixed(1)} km`}
              valueColor={waypointDistance < 5 ? SCORE_COLOR_PALETTE.EXCELLENT : SCORE_COLOR_PALETTE.MODERATE}
            />
          )}
        </div>
        
        {/* Barre de score */}
        <div className="mb-3">
          <ScoreBar score={hotspot.score} />
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(hotspot)}
            className="flex-1 h-8 text-xs text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <Edit3 className="w-3.5 h-3.5 mr-1.5" />
            Modifier
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onViewOnMap(hotspot)}
            className="flex-1 h-8 text-xs text-gray-300 hover:text-white hover:bg-gray-800"
          >
            <Map className="w-3.5 h-3.5 mr-1.5" />
            Carte
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onSell(hotspot)}
            className="flex-1 h-8 text-xs hover:bg-gray-800"
            style={{ color: BIONIC_COLORS.gold.primary }}
          >
            <ShoppingBag className="w-3.5 h-3.5 mr-1.5" />
            Vendre
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Panneau d'édition de hotspot (Sheet)
 */
const HotspotEditSheet = ({
  hotspot,
  isOpen,
  onClose,
  onApply
}) => {
  const [editedFactors, setEditedFactors] = useState({});
  const [editedMetadata, setEditedMetadata] = useState({
    name: '',
    terrainType: 'unknown',
    owner: '',
    notes: ''
  });
  
  // Réinitialiser les valeurs quand le hotspot change
  React.useEffect(() => {
    if (hotspot) {
      setEditedFactors(hotspot.factors || SCORE_FACTORS.reduce((acc, f) => ({ ...acc, [f.key]: 5 }), {}));
      setEditedMetadata({
        name: hotspot.name || '',
        terrainType: hotspot.terrainType || 'unknown',
        owner: hotspot.owner || '',
        notes: hotspot.notes || ''
      });
    }
  }, [hotspot]);
  
  // Calcul du score recalculé (moyenne des facteurs)
  const recalculatedScore = useMemo(() => {
    const values = Object.values(editedFactors);
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }, [editedFactors]);
  
  const originalScore = hotspot?.score || 0;
  const scoreDelta = recalculatedScore - originalScore;
  
  const handleFactorChange = (key, value) => {
    setEditedFactors(prev => ({ ...prev, [key]: value[0] }));
  };
  
  const handleApply = () => {
    onApply({
      ...hotspot,
      ...editedMetadata,
      factors: editedFactors,
      score: recalculatedScore
    });
    onClose();
  };
  
  if (!hotspot) return null;
  
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent 
        className="w-full sm:max-w-lg border-l overflow-y-auto"
        style={{ 
          backgroundColor: BIONIC_COLORS.black.base,
          borderColor: BIONIC_COLORS.gray[800]
        }}
      >
        <SheetHeader className="pb-4">
          <SheetTitle className="text-white flex items-center gap-2">
            <Edit3 className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
            Modifier le Hotspot
          </SheetTitle>
          <SheetDescription className="text-gray-400">
            Ajustez les facteurs contributifs et visualisez l'impact en temps réel
          </SheetDescription>
        </SheetHeader>
        
        {/* Score comparison */}
        <div 
          className="rounded-lg p-4 mb-6"
          style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Score actuel</p>
              <span 
                className="text-2xl font-bold font-mono"
                style={{ color: getScoreColor(originalScore) }}
              >
                {originalScore.toFixed(1)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <ChevronRight className="w-5 h-5 text-gray-600" />
              {scoreDelta !== 0 && (
                <Badge 
                  className="text-xs"
                  style={{ 
                    backgroundColor: scoreDelta > 0 ? `${SCORE_COLOR_PALETTE.EXCELLENT}20` : `${SCORE_COLOR_PALETTE.CRITICAL}20`,
                    color: scoreDelta > 0 ? SCORE_COLOR_PALETTE.EXCELLENT : SCORE_COLOR_PALETTE.CRITICAL
                  }}
                >
                  {scoreDelta > 0 ? '+' : ''}{scoreDelta.toFixed(1)}
                </Badge>
              )}
            </div>
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Score recalculé</p>
              <span 
                className="text-2xl font-bold font-mono"
                style={{ color: getScoreColor(recalculatedScore) }}
              >
                {recalculatedScore.toFixed(1)}
              </span>
            </div>
          </div>
          <ScoreBar score={recalculatedScore} />
        </div>
        
        {/* Metadata editing */}
        <div className="space-y-4 mb-6">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <Info className="w-4 h-4 text-gray-400" />
            Métadonnées
          </h3>
          
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-gray-400">Nom du hotspot</Label>
              <Input
                value={editedMetadata.name}
                onChange={(e) => setEditedMetadata(prev => ({ ...prev, name: e.target.value }))}
                className="mt-1 bg-gray-900 border-gray-700 text-white"
              />
            </div>
            
            <div>
              <Label className="text-xs text-gray-400">Type de terrain</Label>
              <Select
                value={editedMetadata.terrainType}
                onValueChange={(value) => setEditedMetadata(prev => ({ ...prev, terrainType: value }))}
              >
                <SelectTrigger className="mt-1 bg-gray-900 border-gray-700 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-gray-900 border-gray-700">
                  {TERRAIN_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value} className="text-white">
                      <div className="flex items-center gap-2">
                        <type.icon className="w-4 h-4 text-gray-400" />
                        {type.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-xs text-gray-400">Propriétaire (si connu)</Label>
              <Input
                value={editedMetadata.owner}
                onChange={(e) => setEditedMetadata(prev => ({ ...prev, owner: e.target.value }))}
                placeholder="Non spécifié"
                className="mt-1 bg-gray-900 border-gray-700 text-white placeholder:text-gray-600"
              />
            </div>
          </div>
        </div>
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
        
        {/* Factors adjustment */}
        <div className="space-y-4 py-6">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <Target className="w-4 h-4 text-gray-400" />
            Facteurs contributifs
          </h3>
          
          <div className="space-y-5">
            {SCORE_FACTORS.map(factor => {
              const FactorIcon = factor.icon;
              const value = editedFactors[factor.key] || 5;
              
              return (
                <div key={factor.key}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FactorIcon className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-white">{factor.label}</span>
                    </div>
                    <span 
                      className="text-sm font-mono font-semibold"
                      style={{ color: getScoreColor(value) }}
                    >
                      {value.toFixed(1)}
                    </span>
                  </div>
                  <Slider
                    value={[value]}
                    onValueChange={(val) => handleFactorChange(factor.key, val)}
                    min={0}
                    max={10}
                    step={0.5}
                    className="cursor-pointer"
                  />
                  <p className="text-[10px] text-gray-500 mt-1">{factor.description}</p>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t" style={{ borderColor: BIONIC_COLORS.gray[800] }}>
          <Button
            variant="ghost"
            onClick={onClose}
            className="flex-1 text-gray-400 hover:text-white hover:bg-gray-800"
          >
            <X className="w-4 h-4 mr-2" />
            Annuler
          </Button>
          <Button
            onClick={handleApply}
            className="flex-1 text-black font-semibold"
            style={{ backgroundColor: BIONIC_COLORS.gold.primary }}
          >
            <Save className="w-4 h-4 mr-2" />
            Appliquer
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * AdminBionicHotspots
 * 
 * Module d'administration des hotspots analytiques BIONIC.
 * Permet la gestion, l'édition des scores et la préparation pour Marketplace.
 * 
 * @param {Array} hotspots - Liste des hotspots à afficher
 * @param {Object} activeWaypoint - Waypoint actif pour calcul de distance
 * @param {boolean} loading - État de chargement
 * @param {Function} onRefresh - Callback pour rafraîchir les données
 * @param {Function} onHotspotUpdate - Callback lors de la mise à jour d'un hotspot
 * @param {Function} onViewOnMap - Callback pour afficher un hotspot sur la carte
 * @param {Function} onViewSelectedOnMap - Callback pour afficher les hotspots sélectionnés
 * @param {Function} onSellHotspot - Callback pour préparer la vente sur Marketplace
 * @param {string} className - Classes CSS additionnelles
 */
const AdminBionicHotspots = ({
  hotspots = [],
  activeWaypoint = null,
  loading = false,
  onRefresh,
  onHotspotUpdate,
  onViewOnMap,
  onViewSelectedOnMap,
  onSellHotspot,
  className = ''
}) => {
  // State
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [editingHotspot, setEditingHotspot] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [terrainFilter, setTerrainFilter] = useState('all');
  
  // Filtrage des hotspots
  const filteredHotspots = useMemo(() => {
    return hotspots.filter(h => {
      // Filtre de recherche
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!h.name?.toLowerCase().includes(query) && 
            !h.address?.toLowerCase().includes(query) &&
            !h.city?.toLowerCase().includes(query)) {
          return false;
        }
      }
      
      // Filtre par catégorie
      if (categoryFilter !== 'all') {
        const category = getScoreCategory(h.score);
        if (categoryFilter === 'favorable' && category.label !== 'FAVORABLE') return false;
        if (categoryFilter === 'moderate' && category.label !== 'MODÉRÉ') return false;
        if (categoryFilter === 'unfavorable' && category.label !== 'DÉFAVORABLE') return false;
      }
      
      // Filtre par terrain
      if (terrainFilter !== 'all' && h.terrainType !== terrainFilter) {
        return false;
      }
      
      return true;
    });
  }, [hotspots, searchQuery, categoryFilter, terrainFilter]);
  
  // Calcul de la distance au waypoint actif
  const getWaypointDistance = (hotspot) => {
    if (!activeWaypoint || !hotspot.latitude || !hotspot.longitude) return null;
    
    // Formule de Haversine simplifiée
    const R = 6371; // km
    const dLat = (activeWaypoint.latitude - hotspot.latitude) * Math.PI / 180;
    const dLon = (activeWaypoint.longitude - hotspot.longitude) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(hotspot.latitude * Math.PI / 180) * Math.cos(activeWaypoint.latitude * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };
  
  // Handlers
  const handleSelectHotspot = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };
  
  const handleSelectAll = () => {
    if (selectedIds.size === filteredHotspots.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredHotspots.map(h => h.id)));
    }
  };
  
  const handleViewSelectedOnMap = () => {
    const selected = hotspots.filter(h => selectedIds.has(h.id));
    onViewSelectedOnMap?.(selected.length > 0 ? selected : hotspots);
  };
  
  const handleApplyEdit = (updatedHotspot) => {
    onHotspotUpdate?.(updatedHotspot);
  };
  
  // Stats
  const stats = useMemo(() => {
    const favorable = hotspots.filter(h => h.score >= 7).length;
    const moderate = hotspots.filter(h => h.score >= 5 && h.score < 7).length;
    const unfavorable = hotspots.filter(h => h.score < 5).length;
    return { favorable, moderate, unfavorable, total: hotspots.length };
  }, [hotspots]);
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Target className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
              Administration Hotspots BIONIC
            </CardTitle>
            <CardDescription className="text-gray-400 text-sm mt-1">
              Gestion des hotspots analytiques et préparation Marketplace
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onRefresh}
            disabled={loading}
            className="text-gray-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        
        {/* Stats summary */}
        <div className="grid grid-cols-4 gap-2 mt-4">
          <div 
            className="p-2.5 rounded-lg text-center"
            style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
          >
            <p className="text-xl font-bold text-white">{stats.total}</p>
            <p className="text-[10px] text-gray-500 uppercase">Total</p>
          </div>
          <div 
            className="p-2.5 rounded-lg text-center cursor-pointer transition-opacity hover:opacity-80"
            style={{ backgroundColor: `${SCORE_COLOR_PALETTE.EXCELLENT}15` }}
            onClick={() => setCategoryFilter(categoryFilter === 'favorable' ? 'all' : 'favorable')}
          >
            <p className="text-xl font-bold" style={{ color: SCORE_COLOR_PALETTE.EXCELLENT }}>{stats.favorable}</p>
            <p className="text-[10px] text-gray-500 uppercase">Favorable</p>
          </div>
          <div 
            className="p-2.5 rounded-lg text-center cursor-pointer transition-opacity hover:opacity-80"
            style={{ backgroundColor: `${SCORE_COLOR_PALETTE.MODERATE}15` }}
            onClick={() => setCategoryFilter(categoryFilter === 'moderate' ? 'all' : 'moderate')}
          >
            <p className="text-xl font-bold" style={{ color: SCORE_COLOR_PALETTE.MODERATE }}>{stats.moderate}</p>
            <p className="text-[10px] text-gray-500 uppercase">Modéré</p>
          </div>
          <div 
            className="p-2.5 rounded-lg text-center cursor-pointer transition-opacity hover:opacity-80"
            style={{ backgroundColor: `${SCORE_COLOR_PALETTE.CRITICAL}15` }}
            onClick={() => setCategoryFilter(categoryFilter === 'unfavorable' ? 'all' : 'unfavorable')}
          >
            <p className="text-xl font-bold" style={{ color: SCORE_COLOR_PALETTE.CRITICAL }}>{stats.unfavorable}</p>
            <p className="text-[10px] text-gray-500 uppercase">Défavorable</p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Waypoint actif indicator */}
        {activeWaypoint && (
          <div 
            className="flex items-center gap-2 p-2.5 rounded-lg mb-4"
            style={{ backgroundColor: `${BIONIC_COLORS.gold.primary}10` }}
          >
            <Compass className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
            <span className="text-xs text-gray-300">
              Waypoint actif: <span className="text-white font-medium">{activeWaypoint.name}</span>
            </span>
          </div>
        )}
        
        {/* Search and filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              placeholder="Rechercher un hotspot..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-gray-900 border-gray-700 text-white placeholder:text-gray-500"
            />
          </div>
          <Select value={terrainFilter} onValueChange={setTerrainFilter}>
            <SelectTrigger className="w-full sm:w-40 bg-gray-900 border-gray-700 text-white">
              <Filter className="w-4 h-4 mr-2 text-gray-500" />
              <SelectValue placeholder="Terrain" />
            </SelectTrigger>
            <SelectContent className="bg-gray-900 border-gray-700">
              <SelectItem value="all" className="text-white">Tous terrains</SelectItem>
              {TERRAIN_TYPES.map(type => (
                <SelectItem key={type.value} value={type.value} className="text-white">
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Selection toolbar */}
        <div 
          className="flex items-center justify-between p-3 rounded-lg mb-4"
          style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
        >
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSelectAll}
              className="h-8 text-xs text-gray-300 hover:text-white"
            >
              {selectedIds.size === filteredHotspots.length ? (
                <>
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  Tout désélectionner
                </>
              ) : (
                <>
                  <Square className="w-4 h-4 mr-1.5" />
                  Tout sélectionner
                </>
              )}
            </Button>
            {selectedIds.size > 0 && (
              <Badge className="bg-gray-700 text-gray-300">
                {selectedIds.size} sélectionné{selectedIds.size > 1 ? 's' : ''}
              </Badge>
            )}
          </div>
          <Button
            size="sm"
            onClick={handleViewSelectedOnMap}
            className="h-8 text-xs text-black font-medium"
            style={{ backgroundColor: BIONIC_COLORS.gold.primary }}
          >
            <Map className="w-4 h-4 mr-1.5" />
            {selectedIds.size > 0 ? 'Afficher sélection' : 'Afficher tout'}
          </Button>
        </div>
        
        {/* Hotspots list */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-gray-500" />
          </div>
        ) : filteredHotspots.length === 0 ? (
          <div className="text-center py-12">
            <MapPin className="w-10 h-10 mx-auto mb-3 text-gray-600" />
            <p className="text-gray-400 text-sm">Aucun hotspot trouvé</p>
            <p className="text-gray-500 text-xs mt-1">
              {searchQuery || categoryFilter !== 'all' || terrainFilter !== 'all'
                ? 'Modifiez vos filtres pour voir plus de résultats'
                : 'Les hotspots analytiques apparaîtront ici'}
            </p>
          </div>
        ) : (
          <ScrollArea className="h-[500px] pr-3">
            <div className="space-y-3">
              {filteredHotspots.map(hotspot => (
                <HotspotCard
                  key={hotspot.id}
                  hotspot={hotspot}
                  isSelected={selectedIds.has(hotspot.id)}
                  isEditing={editingHotspot?.id === hotspot.id}
                  onSelect={handleSelectHotspot}
                  onEdit={setEditingHotspot}
                  onViewOnMap={onViewOnMap}
                  onSell={onSellHotspot}
                  waypointDistance={getWaypointDistance(hotspot)}
                />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
      
      {/* Edit Sheet */}
      <HotspotEditSheet
        hotspot={editingHotspot}
        isOpen={!!editingHotspot}
        onClose={() => setEditingHotspot(null)}
        onApply={handleApplyEdit}
      />
    </Card>
  );
};

// =============================================================================
// EXPORTS
// =============================================================================

export default AdminBionicHotspots;

// Export des utilitaires pour usage externe
export {
  getScoreColor,
  getScoreCategory,
  SCORE_FACTORS,
  TERRAIN_TYPES
};
