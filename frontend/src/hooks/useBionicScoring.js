/**
 * useBionicScoring Hook
 * Calcule les scores BIONIC pour un waypoint ou une position
 */

import { useState, useCallback, useRef } from 'react';
import { 
  getScoresForWaypoint, 
  calculateHybridScore,
  adaptWaypointData 
} from '@/core/bionic';

const useBionicScoring = () => {
  const [scores, setScores] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [lastCalculation, setLastCalculation] = useState(null);
  
  // Cache pour éviter les recalculs inutiles
  const cacheRef = useRef(new Map());
  
  /**
   * Calcule les scores pour un waypoint (version simple)
   */
  const calculateScores = useCallback((waypointData, contextData = {}) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      // Adapter les données
      const adaptedData = adaptWaypointData(waypointData, contextData);
      
      // Calculer les scores
      const result = getScoresForWaypoint(adaptedData);
      
      setScores(result);
      setLastCalculation(new Date().toISOString());
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error('Scoring error:', err);
      return null;
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Calcule les scores avec le modèle hybride (règles + IA)
   */
  const calculateHybridScores = useCallback(async (waypointData, weather = null, useAI = true) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      // Vérifier le cache
      const cacheKey = `${waypointData.latitude}_${waypointData.longitude}_${useAI}`;
      const cached = cacheRef.current.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < 60000) { // Cache de 1 minute
        setScores(cached.result);
        return cached.result;
      }
      
      // Adapter les données
      const adaptedData = adaptWaypointData(waypointData);
      
      // Calculer avec le modèle hybride
      const result = await calculateHybridScore(adaptedData, weather, useAI);
      
      // Mettre en cache
      cacheRef.current.set(cacheKey, {
        result,
        timestamp: Date.now()
      });
      
      // Nettoyer le cache si trop grand
      if (cacheRef.current.size > 100) {
        const firstKey = cacheRef.current.keys().next().value;
        cacheRef.current.delete(firstKey);
      }
      
      setScores(result);
      setLastCalculation(new Date().toISOString());
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error('Hybrid scoring error:', err);
      return null;
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Calcule les scores pour plusieurs waypoints
   */
  const calculateBatchScores = useCallback(async (waypoints, contextData = {}) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      const results = await Promise.all(
        waypoints.map(async (wp) => {
          const adaptedData = adaptWaypointData(wp, contextData);
          return {
            waypointId: wp.id,
            ...getScoresForWaypoint(adaptedData)
          };
        })
      );
      
      return results;
    } catch (err) {
      setError(err.message);
      console.error('Batch scoring error:', err);
      return [];
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Réinitialise les scores
   */
  const resetScores = useCallback(() => {
    setScores(null);
    setError(null);
    setLastCalculation(null);
  }, []);
  
  /**
   * Vide le cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current.clear();
  }, []);
  
  return {
    // État
    scores,
    isCalculating,
    error,
    lastCalculation,
    
    // Actions
    calculateScores,
    calculateHybridScores,
    calculateBatchScores,
    resetScores,
    clearCache,
    
    // Raccourcis pour les scores individuels
    habitatScore: scores?.score_H,
    rutScore: scores?.score_R,
    salinesScore: scores?.score_S,
    affutsScore: scores?.score_A,
    trajetsScore: scores?.score_T,
    peuplementsScore: scores?.score_P,
    globalScore: scores?.score_Bionic_final || scores?.score_Bionic
  };
};

export default useBionicScoring;
