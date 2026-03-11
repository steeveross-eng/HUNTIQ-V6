/**
 * HuntPlanAnalysisPanel - Panneau d'Analyse du Plan de Chasse
 * ============================================================
 * BIONIC V5 ULTIME - PHASE 5.1
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Affichage de l'analyse waypoint-centric
 * - Composant PUREMENT PRÉSENTATIONNEL
 * - Aucune logique métier, aucun appel API, aucun calcul
 * 
 * CONTENU:
 * - Score global + niveau de qualité
 * - Badge de conformité légale (sans emoji)
 * - Fenêtre de chasse légale du jour
 * - Breakdown des 9 scores
 * - Top 3 facteurs positifs/négatifs
 * - Recommandations contextuelles
 * 
 * ISOLATION:
 * - Nouveau fichier uniquement
 * - Communication via props
 * - Aucun fichier existant modifié
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Target,
  RefreshCw,
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Sunrise,
  Sunset,
  TrendingUp,
  TrendingDown,
  Activity,
  Thermometer,
  Droplets,
  Users,
  MapPin,
  GitBranch,
  Mountain,
  Trees,
  Brain,
  Shield,
  Gauge,
  Compass,
  Info,
  ChevronRight,
  Zap
} from 'lucide-react';

import { BIONIC_COLORS, SCORE_COLORS, getScoreColor } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const SCORE_LEVEL_LABELS = {
  excellent: { label: 'EXCELLENT', color: '#10B981' },
  good: { label: 'BON', color: '#F5A623' },
  moderate: { label: 'MODÉRÉ', color: '#3B82F6' },
  poor: { label: 'FAIBLE', color: '#F97316' },
  very_poor: { label: 'TRÈS FAIBLE', color: '#EF4444' }
};

const QUALITY_LABELS = {
  exceptional: { label: 'EXCEPTIONNEL', color: '#10B981', icon: Zap },
  favorable: { label: 'FAVORABLE', color: '#F5A623', icon: TrendingUp },
  acceptable: { label: 'ACCEPTABLE', color: '#3B82F6', icon: Activity },
  defavorable: { label: 'DÉFAVORABLE', color: '#F97316', icon: TrendingDown },
  illegal: { label: 'HORS PÉRIODE', color: '#EF4444', icon: XCircle }
};

const CATEGORY_ICONS = {
  probability: Target,
  habitat: Trees,
  pressure: Users,
  weather: Thermometer,
  behavior: Brain,
  multifactor: Activity,
  density: Gauge,
  risk: Shield,
  mobility: Compass
};

const CATEGORY_LABELS = {
  probability: 'Probabilité',
  habitat: 'Habitat',
  pressure: 'Pression',
  weather: 'Météo',
  behavior: 'Comportement',
  multifactor: 'Multi-facteurs',
  density: 'Densité',
  risk: 'Risques',
  mobility: 'Mobilité'
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Badge de conformité légale (sans emoji)
 */
const LegalBadge = ({ isLegal, status }) => {
  if (isLegal) {
    return (
      <div 
        className="flex items-center gap-2 px-3 py-1.5 rounded-md"
        style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)' }}
      >
        <CheckCircle className="w-4 h-4" style={{ color: '#10B981' }} />
        <span 
          className="text-sm font-semibold uppercase tracking-wide"
          style={{ color: '#10B981' }}
        >
          Heures légales
        </span>
      </div>
    );
  }
  
  return (
    <div 
      className="flex items-center gap-2 px-3 py-1.5 rounded-md"
      style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)' }}
    >
      <XCircle className="w-4 h-4" style={{ color: '#EF4444' }} />
      <span 
        className="text-sm font-semibold uppercase tracking-wide"
        style={{ color: '#EF4444' }}
      >
        Hors heures légales
      </span>
    </div>
  );
};

/**
 * Indicateur de score circulaire
 */
const ScoreIndicator = ({ score, level, size = 'large' }) => {
  const levelConfig = SCORE_LEVEL_LABELS[level] || SCORE_LEVEL_LABELS.moderate;
  const scoreColor = getScoreColor(score);
  
  const sizeClasses = {
    large: 'w-24 h-24',
    medium: 'w-16 h-16',
    small: 'w-12 h-12'
  };
  
  const textSizes = {
    large: 'text-3xl',
    medium: 'text-xl',
    small: 'text-lg'
  };
  
  return (
    <div className="flex flex-col items-center gap-2">
      <div 
        className={`${sizeClasses[size]} rounded-full flex items-center justify-center relative`}
        style={{ 
          background: `conic-gradient(${scoreColor} ${score}%, ${BIONIC_COLORS.gray[800]} ${score}%)`,
          padding: '4px'
        }}
      >
        <div 
          className="w-full h-full rounded-full flex items-center justify-center"
          style={{ backgroundColor: BIONIC_COLORS.black.base }}
        >
          <span 
            className={`${textSizes[size]} font-bold`}
            style={{ color: scoreColor }}
          >
            {Math.round(score)}
          </span>
        </div>
      </div>
      <Badge 
        variant="outline" 
        className="uppercase text-xs font-semibold"
        style={{ 
          borderColor: levelConfig.color,
          color: levelConfig.color,
          backgroundColor: `${levelConfig.color}15`
        }}
      >
        {levelConfig.label}
      </Badge>
    </div>
  );
};

/**
 * Carte de fenêtre légale
 */
const LegalWindowCard = ({ legalWindow }) => {
  if (!legalWindow) return null;
  
  return (
    <div 
      className="p-4 rounded-lg"
      style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
        <span className="text-sm font-medium text-white">Fenêtre légale du jour</span>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <Sunrise className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.light }} />
          <div>
            <p className="text-xs text-gray-400">Début</p>
            <p className="text-sm font-semibold text-white">
              {legalWindow.legal_start || legalWindow.start_time?.split('T')[1]?.slice(0, 5) || '--:--'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Sunset className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.dark }} />
          <div>
            <p className="text-xs text-gray-400">Fin</p>
            <p className="text-sm font-semibold text-white">
              {legalWindow.legal_end || legalWindow.end_time?.split('T')[1]?.slice(0, 5) || '--:--'}
            </p>
          </div>
        </div>
      </div>
      
      {legalWindow.duration_hours && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          <p className="text-xs text-gray-400">
            Durée totale: <span className="text-white font-medium">
              {legalWindow.duration_formatted || `${Math.floor(legalWindow.duration_hours)}h${Math.round((legalWindow.duration_hours % 1) * 60)}min`}
            </span>
          </p>
        </div>
      )}
    </div>
  );
};

/**
 * Ligne de score pour le breakdown
 */
const ScoreBreakdownRow = ({ category, score, weight, level }) => {
  const Icon = CATEGORY_ICONS[category] || Activity;
  const label = CATEGORY_LABELS[category] || category;
  const scoreColor = getScoreColor(score);
  
  return (
    <div className="flex items-center gap-3 py-2">
      <div 
        className="w-8 h-8 rounded-lg flex items-center justify-center"
        style={{ backgroundColor: `${scoreColor}20` }}
      >
        <Icon className="w-4 h-4" style={{ color: scoreColor }} />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-gray-300 truncate">{label}</span>
          <span 
            className="text-sm font-semibold ml-2"
            style={{ color: scoreColor }}
          >
            {Math.round(score)}
          </span>
        </div>
        <Progress 
          value={score} 
          className="h-1.5"
          style={{ 
            backgroundColor: BIONIC_COLORS.gray[800],
            '--progress-color': scoreColor
          }}
        />
      </div>
      
      {weight && (
        <span className="text-xs text-gray-500 w-12 text-right">
          {Math.round(weight * 100)}%
        </span>
      )}
    </div>
  );
};

/**
 * Liste de facteurs
 */
const FactorsList = ({ factors, type }) => {
  const isPositive = type === 'positive';
  const Icon = isPositive ? TrendingUp : TrendingDown;
  const color = isPositive ? BIONIC_COLORS.green.primary : BIONIC_COLORS.red.primary;
  const title = isPositive ? 'Points forts' : 'Points faibles';
  
  if (!factors || factors.length === 0) {
    return null;
  }
  
  // Nettoyer les facteurs des emojis potentiels
  const cleanFactors = factors.map(f => 
    f.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]/gu, '').trim()
  ).filter(f => f.length > 0);
  
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4" style={{ color }} />
        <span className="text-sm font-medium text-white">{title}</span>
      </div>
      
      <div className="space-y-1.5">
        {cleanFactors.slice(0, 3).map((factor, index) => (
          <div 
            key={index}
            className="flex items-start gap-2 p-2 rounded-md"
            style={{ backgroundColor: `${color}10` }}
          >
            <ChevronRight 
              className="w-4 h-4 mt-0.5 flex-shrink-0" 
              style={{ color }} 
            />
            <span className="text-sm text-gray-300">{factor}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Section des recommandations
 */
const RecommendationsSection = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }
  
  // Nettoyer les recommandations des emojis
  const cleanRecommendations = recommendations.map(r => 
    r.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[⚠️⛔✅❌⏰📍]/gu, '').trim()
  ).filter(r => r.length > 0);
  
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Info className="w-4 h-4" style={{ color: BIONIC_COLORS.blue.light }} />
        <span className="text-sm font-medium text-white">Recommandations</span>
      </div>
      
      <div className="space-y-2">
        {cleanRecommendations.map((rec, index) => (
          <div 
            key={index}
            className="flex items-start gap-3 p-3 rounded-lg"
            style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
          >
            <div 
              className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: BIONIC_COLORS.blue.muted }}
            >
              <span 
                className="text-xs font-bold"
                style={{ color: BIONIC_COLORS.blue.light }}
              >
                {index + 1}
              </span>
            </div>
            <p className="text-sm text-gray-300 leading-relaxed">{rec}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * État de chargement
 */
const LoadingState = () => (
  <div className="flex flex-col items-center justify-center py-12 gap-4">
    <Loader2 
      className="w-8 h-8 animate-spin" 
      style={{ color: BIONIC_COLORS.gold.primary }} 
    />
    <p className="text-sm text-gray-400">Analyse en cours...</p>
  </div>
);

/**
 * État vide (pas de waypoint sélectionné)
 */
const EmptyState = ({ onWaypointChange }) => (
  <div className="flex flex-col items-center justify-center py-12 gap-4">
    <div 
      className="w-16 h-16 rounded-full flex items-center justify-center"
      style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
    >
      <MapPin className="w-8 h-8" style={{ color: BIONIC_COLORS.gray[500] }} />
    </div>
    <div className="text-center">
      <p className="text-white font-medium mb-1">Aucun waypoint sélectionné</p>
      <p className="text-sm text-gray-400">
        Sélectionnez un waypoint pour voir l'analyse
      </p>
    </div>
    {onWaypointChange && (
      <Button 
        variant="outline" 
        onClick={onWaypointChange}
        className="mt-2"
        style={{ 
          borderColor: BIONIC_COLORS.gold.primary,
          color: BIONIC_COLORS.gold.primary
        }}
      >
        <MapPin className="w-4 h-4 mr-2" />
        Sélectionner un waypoint
      </Button>
    )}
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * HuntPlanAnalysisPanel
 * 
 * Panneau principal d'analyse du plan de chasse.
 * Composant PUREMENT PRÉSENTATIONNEL - aucune logique métier.
 * 
 * @param {string} waypointId - ID du waypoint sélectionné (obligatoire)
 * @param {string} waypointName - Nom du waypoint
 * @param {object} analysisData - Résultat de WaypointAnalysisService
 * @param {boolean} isLoading - État de chargement
 * @param {function} onRefresh - Callback pour rafraîchir l'analyse
 * @param {function} onWaypointChange - Callback pour changer de waypoint
 */
const HuntPlanAnalysisPanel = ({
  waypointId,
  waypointName,
  analysisData,
  isLoading = false,
  onRefresh,
  onWaypointChange
}) => {
  // Si pas de waypoint, afficher l'état vide
  if (!waypointId) {
    return (
      <Card 
        className="border-0"
        style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
      >
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-white">
            <Target className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
            Analyse du Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState onWaypointChange={onWaypointChange} />
        </CardContent>
      </Card>
    );
  }
  
  // Si en chargement
  if (isLoading) {
    return (
      <Card 
        className="border-0"
        style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
      >
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-white">
            <Target className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
            Analyse du Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LoadingState />
        </CardContent>
      </Card>
    );
  }
  
  // Extraire les données de l'analyse
  const {
    analysis_id,
    unified_score = 0,
    unified_level = 'moderate',
    fused_heatmap_score,
    wqs_score,
    is_legal_period = false,
    legal_status,
    legal_window,
    recommendations = [],
    hotspots_nearby = [],
    optimal_windows = [],
    metadata = {}
  } = analysisData || {};
  
  // Extraire les scores du breakdown (si disponible via to_dict())
  const scores = analysisData?.scores || {};
  const scoreBreakdown = analysisData?.score_breakdown || [];
  
  // Extraire les analyses locales
  const localAnalysis = analysisData?.local_analysis || {};
  
  // Facteurs positifs/négatifs (depuis le résultat unifié ou les recommandations)
  const positiveFactors = analysisData?.insights?.positive_factors || 
                          analysisData?.positive_factors || [];
  const negativeFactors = analysisData?.insights?.negative_factors || 
                          analysisData?.negative_factors || [];
  
  // Qualité globale
  const qualityKey = analysisData?.global_summary?.quality || 
                     (is_legal_period ? (unified_score >= 70 ? 'favorable' : 'acceptable') : 'illegal');
  const qualityConfig = QUALITY_LABELS[qualityKey] || QUALITY_LABELS.acceptable;
  const QualityIcon = qualityConfig.icon;
  
  return (
    <Card 
      className="border-0 overflow-hidden"
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      {/* Header */}
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-white">
            <Target className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
            Analyse du Plan
          </CardTitle>
          
          {onRefresh && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
              className="h-8 w-8 p-0"
              style={{ color: BIONIC_COLORS.gray[400] }}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          )}
        </div>
        
        {/* Waypoint info */}
        <div className="flex items-center gap-2 mt-2">
          <MapPin className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
          <span className="text-sm text-gray-300">{waypointName || waypointId}</span>
        </div>
      </CardHeader>
      
      <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
      
      {/* Content */}
      <CardContent className="pt-4">
        <ScrollArea className="h-[calc(100vh-280px)] pr-4">
          <div className="space-y-6">
            
            {/* Score Global + Badge Légal */}
            <div className="flex items-start justify-between gap-4">
              <ScoreIndicator 
                score={unified_score} 
                level={unified_level}
                size="large"
              />
              
              <div className="flex flex-col items-end gap-3">
                <LegalBadge isLegal={is_legal_period} status={legal_status} />
                
                {/* Badge de qualité */}
                <div 
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md"
                  style={{ backgroundColor: `${qualityConfig.color}15` }}
                >
                  <QualityIcon className="w-4 h-4" style={{ color: qualityConfig.color }} />
                  <span 
                    className="text-sm font-semibold"
                    style={{ color: qualityConfig.color }}
                  >
                    {qualityConfig.label}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Fenêtre Légale */}
            {legal_window && (
              <LegalWindowCard legalWindow={legal_window} />
            )}
            
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
            
            {/* Scores WQS et Fusionné */}
            {(wqs_score !== undefined || fused_heatmap_score !== undefined) && (
              <div className="grid grid-cols-2 gap-4">
                {wqs_score !== undefined && (
                  <div 
                    className="p-3 rounded-lg text-center"
                    style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
                  >
                    <p className="text-xs text-gray-400 mb-1">Score WQS</p>
                    <p 
                      className="text-xl font-bold"
                      style={{ color: getScoreColor(wqs_score) }}
                    >
                      {Math.round(wqs_score)}
                    </p>
                  </div>
                )}
                
                {fused_heatmap_score !== undefined && (
                  <div 
                    className="p-3 rounded-lg text-center"
                    style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
                  >
                    <p className="text-xs text-gray-400 mb-1">Score Fusionné</p>
                    <p 
                      className="text-xl font-bold"
                      style={{ color: getScoreColor(fused_heatmap_score) }}
                    >
                      {Math.round(fused_heatmap_score)}
                    </p>
                  </div>
                )}
              </div>
            )}
            
            {/* Breakdown des 9 Scores */}
            {scoreBreakdown.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-white flex items-center gap-2">
                  <Activity className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
                  Détail des Scores
                </h4>
                
                <div 
                  className="p-3 rounded-lg space-y-1"
                  style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
                >
                  {scoreBreakdown.map((item, index) => (
                    <ScoreBreakdownRow
                      key={index}
                      category={item.category}
                      score={item.raw_value || item.score || 50}
                      weight={item.weight}
                      level={item.level}
                    />
                  ))}
                </div>
              </div>
            )}
            
            {/* Analyses Locales (si pas de breakdown détaillé) */}
            {scoreBreakdown.length === 0 && localAnalysis && Object.keys(localAnalysis).length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-white flex items-center gap-2">
                  <Activity className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
                  Analyses Locales
                </h4>
                
                <div 
                  className="p-3 rounded-lg space-y-1"
                  style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
                >
                  {localAnalysis.mobility && (
                    <ScoreBreakdownRow
                      category="mobility"
                      score={localAnalysis.mobility.mobility_score || 50}
                    />
                  )}
                  {localAnalysis.pressure && (
                    <ScoreBreakdownRow
                      category="pressure"
                      score={localAnalysis.pressure.pressure_score || 50}
                    />
                  )}
                  {localAnalysis.density && (
                    <ScoreBreakdownRow
                      category="density"
                      score={localAnalysis.density.density_score || 50}
                    />
                  )}
                  {localAnalysis.risk && (
                    <ScoreBreakdownRow
                      category="risk"
                      score={localAnalysis.risk.safety_score || 50}
                    />
                  )}
                </div>
              </div>
            )}
            
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
            
            {/* Facteurs Positifs / Négatifs */}
            <div className="grid grid-cols-1 gap-4">
              <FactorsList factors={positiveFactors} type="positive" />
              <FactorsList factors={negativeFactors} type="negative" />
            </div>
            
            {/* Recommandations */}
            {recommendations.length > 0 && (
              <>
                <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
                <RecommendationsSection recommendations={recommendations} />
              </>
            )}
            
            {/* Métadonnées */}
            {metadata && (metadata.calculation_time_ms || analysis_id) && (
              <div 
                className="mt-4 p-2 rounded text-center"
                style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
              >
                <p className="text-xs text-gray-500">
                  {analysis_id && `ID: ${analysis_id}`}
                  {analysis_id && metadata.calculation_time_ms && ' | '}
                  {metadata.calculation_time_ms && `Calculé en ${Math.round(metadata.calculation_time_ms)}ms`}
                </p>
              </div>
            )}
            
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default HuntPlanAnalysisPanel;
