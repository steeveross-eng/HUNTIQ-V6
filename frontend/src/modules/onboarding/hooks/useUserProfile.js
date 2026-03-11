/**
 * useUserProfile Hook - Phase 10
 * 
 * Manages user profile/preferences storage.
 */

import { useState, useCallback, useEffect } from 'react';
import { STORAGE_KEYS } from '../constants';

const DEFAULT_PROFILE = {
  territory: null,
  experience: null,
  objectives: [],
  species: [],
  region: null,
  completedAt: null
};

export const useUserProfile = () => {
  // Profile state
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.USER_PROFILE);
    if (saved) {
      try {
        return { ...DEFAULT_PROFILE, ...JSON.parse(saved) };
      } catch {
        return DEFAULT_PROFILE;
      }
    }
    return DEFAULT_PROFILE;
  });
  
  // Dirty state (unsaved changes)
  const [isDirty, setIsDirty] = useState(false);

  /**
   * Update profile field
   */
  const updateProfile = useCallback((field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
    setIsDirty(true);
  }, []);

  /**
   * Set territory preference
   */
  const setTerritory = useCallback((territoryId) => {
    updateProfile('territory', territoryId);
  }, [updateProfile]);

  /**
   * Set experience level
   */
  const setExperience = useCallback((experienceId) => {
    updateProfile('experience', experienceId);
  }, [updateProfile]);

  /**
   * Toggle objective selection
   */
  const toggleObjective = useCallback((objectiveId) => {
    setProfile(prev => {
      const objectives = prev.objectives || [];
      const newObjectives = objectives.includes(objectiveId)
        ? objectives.filter(id => id !== objectiveId)
        : [...objectives, objectiveId];
      return { ...prev, objectives: newObjectives };
    });
    setIsDirty(true);
  }, []);

  /**
   * Set objectives (replace all)
   */
  const setObjectives = useCallback((objectiveIds) => {
    updateProfile('objectives', objectiveIds);
  }, [updateProfile]);

  /**
   * Toggle species selection
   */
  const toggleSpecies = useCallback((speciesId) => {
    setProfile(prev => {
      const species = prev.species || [];
      const newSpecies = species.includes(speciesId)
        ? species.filter(id => id !== speciesId)
        : [...species, speciesId];
      return { ...prev, species: newSpecies };
    });
    setIsDirty(true);
  }, []);

  /**
   * Set region
   */
  const setRegion = useCallback((regionId) => {
    updateProfile('region', regionId);
  }, [updateProfile]);

  /**
   * Save profile to localStorage
   */
  const saveProfile = useCallback(() => {
    const profileToSave = {
      ...profile,
      completedAt: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(profileToSave));
    setProfile(profileToSave);
    setIsDirty(false);
    return profileToSave;
  }, [profile]);

  /**
   * Clear profile
   */
  const clearProfile = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.USER_PROFILE);
    setProfile(DEFAULT_PROFILE);
    setIsDirty(false);
  }, []);

  /**
   * Check if profile is valid for completion
   */
  const isProfileValid = useCallback(() => {
    return (
      profile.territory !== null &&
      profile.experience !== null &&
      profile.objectives.length > 0
    );
  }, [profile]);

  /**
   * Get profile summary
   */
  const getProfileSummary = useCallback(() => {
    return {
      hasTerritory: profile.territory !== null,
      hasExperience: profile.experience !== null,
      objectiveCount: profile.objectives.length,
      speciesCount: profile.species.length,
      isComplete: isProfileValid()
    };
  }, [profile, isProfileValid]);

  return {
    // State
    profile,
    isDirty,
    
    // Setters
    updateProfile,
    setTerritory,
    setExperience,
    toggleObjective,
    setObjectives,
    toggleSpecies,
    setRegion,
    
    // Actions
    saveProfile,
    clearProfile,
    
    // Validation
    isProfileValid,
    getProfileSummary
  };
};

export default useUserProfile;
