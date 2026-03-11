/**
 * useProperties - Hook for managing properties
 * Phase 11-15: Module Immobilier
 */
import { useState, useEffect, useCallback } from 'react';
import { RealEstateService } from '../services/RealEstateService';

export const useProperties = (initialFilters = {}) => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [total, setTotal] = useState(0);

  const fetchProperties = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await RealEstateService.getProperties(filters);
      if (result.success) {
        setProperties(result.properties || []);
        setTotal(result.total || 0);
      } else {
        setError(result.error || 'Failed to fetch properties');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const refresh = useCallback(() => {
    fetchProperties();
  }, [fetchProperties]);

  return {
    properties,
    loading,
    error,
    filters,
    total,
    updateFilters,
    resetFilters,
    refresh
  };
};

export default useProperties;
