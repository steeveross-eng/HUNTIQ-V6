/**
 * useOpportunities - Hook for managing opportunities
 * Phase 11-15: Module Immobilier
 */
import { useState, useEffect, useCallback } from 'react';
import { OpportunityService } from '../services/OpportunityService';

export const useOpportunities = (initialFilters = {}) => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  const fetchOpportunities = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await OpportunityService.getTopOpportunities(filters);
      if (result.success) {
        setOpportunities(result.opportunities || []);
      } else {
        setError(result.error || 'Failed to fetch opportunities');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const refresh = useCallback(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  return {
    opportunities,
    loading,
    error,
    filters,
    updateFilters,
    resetFilters,
    refresh
  };
};

export default useOpportunities;
