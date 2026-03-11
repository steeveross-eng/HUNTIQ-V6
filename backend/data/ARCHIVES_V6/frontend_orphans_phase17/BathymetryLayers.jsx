/**
 * BathymetryLayers.jsx
 * 
 * Couches bathymétriques pour les lacs et rivières du Québec
 * Structure préparée pour l'intégration des données de profondeur
 * 
 * Sources prévues:
 * - Données MFFP (lacs publics du Québec)
 * - Données utilisateur (relevés personnels)
 * - Navionics API (si licence disponible)
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Polygon, Polyline, CircleMarker, Tooltip, LayerGroup, useMap } from 'react-leaflet';

// Palette de couleurs bathymétriques (profondeur en mètres)
export const BATHYMETRY_COLORS = {
  depth_0_2: '#B3E5FC',     // Très peu profond - Cyan très pâle
  depth_2_5: '#4FC3F7',     // Peu profond - Cyan clair
  depth_5_10: '#0288D1',    // Moyen - Bleu
  depth_10_20: '#01579B',   // Profond - Bleu foncé
  depth_20_plus: '#0D47A1', // Très profond - Marine
  contour: '#FFFFFF',       // Lignes de contour
  shallow_warning: '#FFEB3B', // Haut-fond danger - Jaune
  deep_point: '#1A237E',    // Point le plus profond - Marine foncé
};

// Configuration des intervalles de profondeur
export const DEPTH_INTERVALS = [
  { min: 0, max: 2, color: BATHYMETRY_COLORS.depth_0_2, label: '0-2m' },
  { min: 2, max: 5, color: BATHYMETRY_COLORS.depth_2_5, label: '2-5m' },
  { min: 5, max: 10, color: BATHYMETRY_COLORS.depth_5_10, label: '5-10m' },
  { min: 10, max: 20, color: BATHYMETRY_COLORS.depth_10_20, label: '10-20m' },
  { min: 20, max: Infinity, color: BATHYMETRY_COLORS.depth_20_plus, label: '20m+' },
];

/**
 * Obtenir la couleur selon la profondeur
 */
export const getDepthColor = (depth) => {
  for (const interval of DEPTH_INTERVALS) {
    if (depth >= interval.min && depth < interval.max) {
      return interval.color;
    }
  }
  return BATHYMETRY_COLORS.depth_20_plus;
};

/**
 * Légende bathymétrique
 */
export const BathymetryLegend = ({ visible = true, language = 'fr' }) => {
  if (!visible) return null;
  
  const labels = {
    fr: {
      title: 'Profondeur',
      shallow: 'Haut-fond',
      deep: 'Point profond'
    },
    en: {
      title: 'Depth',
      shallow: 'Shallow',
      deep: 'Deep point'
    }
  };
  
  const t = labels[language] || labels.fr;
  
  return (
    <div className="absolute bottom-20 left-4 z-[600] bg-black/80 backdrop-blur-xl border border-white/10 rounded-lg p-3 max-w-[180px]">
      <div className="text-white text-xs font-bold uppercase tracking-wider mb-2">
        {t.title}
      </div>
      
      {/* Gradient de profondeur */}
      <div className="space-y-1">
        {DEPTH_INTERVALS.map((interval, index) => (
          <div key={index} className="flex items-center gap-2">
            <div 
              className="w-4 h-3 rounded-sm border border-white/20" 
              style={{ backgroundColor: interval.color }} 
            />
            <span className="text-gray-300 text-[10px]">{interval.label}</span>
          </div>
        ))}
      </div>
      
      {/* Indicateurs spéciaux */}
      <div className="mt-2 pt-2 border-t border-white/10 space-y-1">
        <div className="flex items-center gap-2">
          <div 
            className="w-3 h-3 rounded-full border-2" 
            style={{ 
              backgroundColor: BATHYMETRY_COLORS.shallow_warning,
              borderColor: '#FFA000'
            }} 
          />
          <span className="text-gray-300 text-[10px]">{t.shallow}</span>
        </div>
        <div className="flex items-center gap-2">
          <div 
            className="w-3 h-3 rounded-full" 
            style={{ backgroundColor: BATHYMETRY_COLORS.deep_point }} 
          />
          <span className="text-gray-300 text-[10px]">{t.deep}</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Hook pour gérer les données bathymétriques
 */
export const useBathymetryData = (lakeId = null) => {
  const [bathyData, setBathyData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Charger les données bathymétriques pour un lac
  const loadBathymetryData = useCallback(async (id) => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${API_BASE}/api/bathymetry/${id}`);
      
      if (!response.ok) {
        throw new Error('Données bathymétriques non disponibles');
      }
      
      const data = await response.json();
      setBathyData(data);
    } catch (err) {
      console.warn('Bathymetry load error:', err);
      setError(err.message);
      setBathyData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // Réinitialiser
  const clearBathymetryData = useCallback(() => {
    setBathyData(null);
    setError(null);
  }, []);
  
  return {
    bathyData,
    isLoading,
    error,
    loadBathymetryData,
    clearBathymetryData
  };
};

/**
 * Composant de rendu des courbes bathymétriques
 */
const DepthContours = ({ contours = [], opacity = 0.8 }) => {
  if (!contours || contours.length === 0) return null;
  
  return (
    <>
      {contours.map((contour, index) => (
        <Polyline
          key={`contour-${index}`}
          positions={contour.coordinates}
          pathOptions={{
            color: BATHYMETRY_COLORS.contour,
            weight: contour.depth % 5 === 0 ? 2 : 1, // Lignes plus épaisses tous les 5m
            opacity: opacity,
            dashArray: contour.depth % 10 === 0 ? null : '5,5' // Tirets sauf pour les lignes index
          }}
        >
          <Tooltip permanent={false} direction="center">
            <span className="text-xs font-bold">{contour.depth}m</span>
          </Tooltip>
        </Polyline>
      ))}
    </>
  );
};

/**
 * Composant de rendu des zones de profondeur
 */
const DepthZones = ({ zones = [], opacity = 0.5 }) => {
  if (!zones || zones.length === 0) return null;
  
  return (
    <>
      {zones.map((zone, index) => (
        <Polygon
          key={`zone-${index}`}
          positions={zone.coordinates}
          pathOptions={{
            fillColor: getDepthColor(zone.depth),
            fillOpacity: opacity,
            color: BATHYMETRY_COLORS.contour,
            weight: 1,
            opacity: 0.8
          }}
        >
          <Tooltip>
            <div className="text-xs">
              <strong>Profondeur:</strong> {zone.minDepth}-{zone.maxDepth}m
            </div>
          </Tooltip>
        </Polygon>
      ))}
    </>
  );
};

/**
 * Composant de rendu des points spéciaux (hauts-fonds, points profonds)
 */
const SpecialPoints = ({ points = [] }) => {
  if (!points || points.length === 0) return null;
  
  return (
    <>
      {points.map((point, index) => (
        <CircleMarker
          key={`point-${index}`}
          center={point.coordinates}
          radius={point.type === 'shallow' ? 8 : 6}
          pathOptions={{
            fillColor: point.type === 'shallow' 
              ? BATHYMETRY_COLORS.shallow_warning 
              : BATHYMETRY_COLORS.deep_point,
            fillOpacity: 0.9,
            color: point.type === 'shallow' ? '#FFA000' : '#0D47A1',
            weight: 2
          }}
        >
          <Tooltip>
            <div className="text-xs">
              <strong>{point.type === 'shallow' ? 'Haut-fond' : 'Point profond'}</strong>
              <br />
              Profondeur: {point.depth}m
              {point.name && <><br />{point.name}</>}
            </div>
          </Tooltip>
        </CircleMarker>
      ))}
    </>
  );
};

/**
 * Composant principal des couches bathymétriques
 */
const BathymetryLayers = ({
  enabled = false,
  bathyData = null,
  showContours = true,
  showZones = true,
  showPoints = true,
  showLegend = true,
  opacity = 0.6,
  language = 'fr'
}) => {
  const map = useMap();
  
  // Données simulées pour démonstration (à remplacer par données réelles)
  const demoData = useMemo(() => {
    if (bathyData) return bathyData;
    
    // Retourner null si pas de données - sera remplacé par les vraies données
    return null;
  }, [bathyData]);
  
  if (!enabled) return null;
  
  return (
    <>
      <LayerGroup>
        {/* Zones de profondeur (polygones colorés) */}
        {showZones && demoData?.zones && (
          <DepthZones zones={demoData.zones} opacity={opacity} />
        )}
        
        {/* Courbes de niveau */}
        {showContours && demoData?.contours && (
          <DepthContours contours={demoData.contours} opacity={opacity + 0.2} />
        )}
        
        {/* Points spéciaux */}
        {showPoints && demoData?.points && (
          <SpecialPoints points={demoData.points} />
        )}
      </LayerGroup>
      
      {/* Légende */}
      {showLegend && enabled && (
        <BathymetryLegend visible={true} language={language} />
      )}
      
      {/* Message si pas de données */}
      {enabled && !demoData && (
        <div className="absolute bottom-20 left-4 z-[600] bg-black/80 backdrop-blur-xl border border-[#F5A623]/30 rounded-lg p-3 max-w-[200px]">
          <div className="text-[#F5A623] text-xs font-medium mb-1">
            Bathymétrie
          </div>
          <div className="text-gray-400 text-[10px]">
            En attente des données de profondeur pour ce lac.
          </div>
        </div>
      )}
    </>
  );
};

export default BathymetryLayers;
