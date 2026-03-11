/**
 * useBionicStrategy Hook
 * Combine scoring, météo et stratégie pour des recommandations complètes
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { getStrategyForWaypoint } from '@/core/bionic';
import useBionicScoring from '@/hooks/useBionicScoring';
import useBionicWeather from '@/hooks/useBionicWeather';

const useBionicStrategy = (waypoint, options = {}) => {
  const {
    autoCalculate = false,
    weatherEnabled = true,
    territoryContext = {}
  } = options;
  
  const [strategy, setStrategy] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [strategyLiveEnabled, setStrategyLiveEnabled] = useState(false);
  
  const intervalRef = useRef(null);
  const isMountedRef = useRef(true);
  
  // Hooks de scoring et météo
  const scoring = useBionicScoring();
  const weather = useBionicWeather(
    waypoint?.latitude || waypoint?.lat,
    waypoint?.longitude || waypoint?.lng,
    { enabled: weatherEnabled && strategyLiveEnabled }
  );
  
  /**
   * Calcule la stratégie pour un waypoint
   */
  const calculateStrategy = useCallback(async (wp = waypoint) => {
    if (!wp) return null;
    
    try {
      setIsCalculating(true);
      setError(null);
      
      // D'abord calculer les scores hybrides
      const scores = await scoring.calculateHybridScores(
        wp, 
        weather.weather,
        true // Utiliser l'IA
      );
      
      if (!scores) {
        throw new Error('Impossible de calculer les scores');
      }
      
      // Ensuite générer la stratégie
      const strategyResult = await getStrategyForWaypoint(
        wp,
        scores,
        weather.weather,
        territoryContext
      );
      
      if (isMountedRef.current) {
        setStrategy(strategyResult);
        setLastUpdate(new Date().toISOString());
      }
      
      return strategyResult;
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message);
        console.error('Strategy calculation error:', err);
      }
      return null;
    } finally {
      if (isMountedRef.current) {
        setIsCalculating(false);
      }
    }
  }, [waypoint, weather.weather, territoryContext, scoring]);
  
  /**
   * Active/désactive le mode stratégie LIVE
   */
  const toggleStrategyLive = useCallback((enabled) => {
    setStrategyLiveEnabled(enabled);
    
    if (enabled && waypoint) {
      calculateStrategy();
      // Démarrer le polling météo est géré par le hook useBionicWeather
    }
  }, [waypoint, calculateStrategy]);
  
  /**
   * Démarre les mises à jour LIVE
   */
  const startLiveUpdates = useCallback((intervalMs = 5 * 60 * 1000) => {
    setStrategyLiveEnabled(true);
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Calcul initial
    calculateStrategy();
    
    // Polling régulier
    intervalRef.current = setInterval(() => {
      calculateStrategy();
    }, intervalMs);
  }, [calculateStrategy]);
  
  /**
   * Arrête les mises à jour LIVE
   */
  const stopLiveUpdates = useCallback(() => {
    setStrategyLiveEnabled(false);
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);
  
  /**
   * Force un rafraîchissement
   */
  const refresh = useCallback(async () => {
    await weather.refresh();
    return calculateStrategy();
  }, [weather, calculateStrategy]);
  
  // Effet de nettoyage
  useEffect(() => {
    isMountedRef.current = true;
    
    return () => {
      isMountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);
  
  // Auto-calcul si activé
  useEffect(() => {
    if (autoCalculate && waypoint && weather.hasData) {
      calculateStrategy();
    }
  }, [autoCalculate, waypoint, weather.hasData]);
  
  // Données extraites de la stratégie
  const standScore = strategy?.stand || null;
  const approachPath = strategy?.approachPath || null;
  const gameMovement = strategy?.gameMovement || null;
  const risks = strategy?.risks || null;
  const products = strategy?.products || [];
  const liveFlags = strategy?.liveFlags || {
    isOptimalNow: false,
    willDegradeSoon: false,
    isRiskyNow: false,
    peakWindowActive: false
  };
  const summary = strategy?.summary || '';
  
  return {
    // Stratégie complète
    strategy,
    
    // État
    isCalculating,
    error,
    lastUpdate,
    
    // Composants de la stratégie
    standScore,
    approachPath,
    gameMovement,
    risks,
    products,
    liveFlags,
    summary,
    
    // Scores (du hook scoring)
    scores: scoring.scores,
    globalScore: scoring.globalScore,
    
    // Météo (du hook weather)
    weather: weather.weather,
    weatherInfo: {
      temperature: weather.temperature,
      windInfo: weather.windInfo,
      thermalInfo: weather.thermalInfo,
      huntingScore: weather.huntingScore,
      nextOptimalWindow: weather.nextOptimalWindow
    },
    
    // État LIVE
    strategyLiveEnabled,
    
    // Actions
    calculateStrategy,
    toggleStrategyLive,
    startLiveUpdates,
    stopLiveUpdates,
    refresh,
    
    // Sous-hooks exposés pour usage avancé
    scoringHook: scoring,
    weatherHook: weather
  };
};

export default useBionicStrategy;
