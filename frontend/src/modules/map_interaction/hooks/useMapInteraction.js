/**
 * useMapInteraction - Hook for Map Interaction
 * =============================================
 * 
 * Hook pour gérer les interactions cartographiques.
 * Architecture LEGO V5 - Module métier isolé.
 * 
 * @module modules/map_interaction/hooks
 */
import { useState, useCallback, useEffect } from 'react';
import { WaypointService } from '../services/WaypointService';

/**
 * useMapInteraction hook
 * @param {Object} options - Hook options
 * @param {string} options.userId - User ID
 * @param {boolean} options.autoLoadWaypoints - Auto-load user waypoints
 */
export const useMapInteraction = ({ userId, autoLoadWaypoints = false } = {}) => {
  const [waypoints, setWaypoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load waypoints
  const loadWaypoints = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const result = await WaypointService.getWaypoints(userId);
      setWaypoints(result.waypoints || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Create waypoint
  const createWaypoint = useCallback(async (data) => {
    setLoading(true);
    setError(null);

    try {
      const result = await WaypointService.createWaypoint({
        ...data,
        user_id: userId
      });

      if (result.success) {
        setWaypoints(prev => [...prev, result.waypoint]);
      }

      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Delete waypoint
  const deleteWaypoint = useCallback(async (waypointId) => {
    setLoading(true);
    setError(null);

    try {
      const result = await WaypointService.deleteWaypoint(waypointId);

      if (result.success) {
        setWaypoints(prev => prev.filter(wp => wp.id !== waypointId));
      }

      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-load on mount
  useEffect(() => {
    if (autoLoadWaypoints && userId) {
      loadWaypoints();
    }
  }, [autoLoadWaypoints, userId, loadWaypoints]);

  return {
    waypoints,
    loading,
    error,
    loadWaypoints,
    createWaypoint,
    deleteWaypoint
  };
};

export default useMapInteraction;
