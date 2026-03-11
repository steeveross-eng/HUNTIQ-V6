/**
 * useTutorialProgress Hook - Phase 11
 * 
 * Manages tutorial progress storage and retrieval.
 */

import { useState, useCallback, useEffect } from 'react';
import { STORAGE_KEYS, TUTORIAL_STATUS } from '../constants';
import { getAllTutorialIds } from '../data/tutorials';

const getInitialProgress = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.TUTORIAL_PROGRESS);
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
};

const getInitialDismissed = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.TUTORIAL_DISMISSED);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

export const useTutorialProgress = () => {
  // Progress state: { tutorialId: { status, currentStep, completedAt } }
  const [progress, setProgress] = useState(getInitialProgress);
  
  // Dismissed tutorials (won't show again)
  const [dismissed, setDismissed] = useState(getInitialDismissed);

  // Save progress to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.TUTORIAL_PROGRESS, JSON.stringify(progress));
  }, [progress]);

  // Save dismissed to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.TUTORIAL_DISMISSED, JSON.stringify(dismissed));
  }, [dismissed]);

  /**
   * Get status of a tutorial
   */
  const getTutorialStatus = useCallback((tutorialId) => {
    if (dismissed.includes(tutorialId)) {
      return TUTORIAL_STATUS.DISMISSED;
    }
    return progress[tutorialId]?.status || TUTORIAL_STATUS.NOT_STARTED;
  }, [progress, dismissed]);

  /**
   * Check if tutorial is completed
   */
  const isTutorialCompleted = useCallback((tutorialId) => {
    return getTutorialStatus(tutorialId) === TUTORIAL_STATUS.COMPLETED;
  }, [getTutorialStatus]);

  /**
   * Check if tutorial should show (not completed, not dismissed)
   */
  const shouldShowTutorial = useCallback((tutorialId) => {
    const status = getTutorialStatus(tutorialId);
    return status === TUTORIAL_STATUS.NOT_STARTED || status === TUTORIAL_STATUS.IN_PROGRESS;
  }, [getTutorialStatus]);

  /**
   * Start a tutorial
   */
  const startTutorial = useCallback((tutorialId) => {
    setProgress(prev => ({
      ...prev,
      [tutorialId]: {
        status: TUTORIAL_STATUS.IN_PROGRESS,
        currentStep: 0,
        startedAt: new Date().toISOString()
      }
    }));
  }, []);

  /**
   * Update current step
   */
  const updateStep = useCallback((tutorialId, stepIndex) => {
    setProgress(prev => ({
      ...prev,
      [tutorialId]: {
        ...prev[tutorialId],
        currentStep: stepIndex
      }
    }));
  }, []);

  /**
   * Complete a tutorial
   */
  const completeTutorial = useCallback((tutorialId) => {
    setProgress(prev => ({
      ...prev,
      [tutorialId]: {
        ...prev[tutorialId],
        status: TUTORIAL_STATUS.COMPLETED,
        completedAt: new Date().toISOString()
      }
    }));
  }, []);

  /**
   * Skip a tutorial
   */
  const skipTutorial = useCallback((tutorialId) => {
    setProgress(prev => ({
      ...prev,
      [tutorialId]: {
        ...prev[tutorialId],
        status: TUTORIAL_STATUS.SKIPPED,
        skippedAt: new Date().toISOString()
      }
    }));
  }, []);

  /**
   * Dismiss a tutorial (won't show again)
   */
  const dismissTutorial = useCallback((tutorialId) => {
    setDismissed(prev => [...new Set([...prev, tutorialId])]);
  }, []);

  /**
   * Reset all tutorial progress
   */
  const resetAllProgress = useCallback(() => {
    setProgress({});
    setDismissed([]);
    localStorage.removeItem(STORAGE_KEYS.TUTORIAL_PROGRESS);
    localStorage.removeItem(STORAGE_KEYS.TUTORIAL_DISMISSED);
  }, []);

  /**
   * Get overall completion stats
   */
  const getCompletionStats = useCallback(() => {
    const allIds = getAllTutorialIds();
    const completed = allIds.filter(id => isTutorialCompleted(id));
    const skipped = allIds.filter(id => getTutorialStatus(id) === TUTORIAL_STATUS.SKIPPED);
    const dismissed = allIds.filter(id => getTutorialStatus(id) === TUTORIAL_STATUS.DISMISSED);
    
    return {
      total: allIds.length,
      completed: completed.length,
      skipped: skipped.length,
      dismissed: dismissed.length,
      remaining: allIds.length - completed.length - skipped.length - dismissed.length,
      percentage: Math.round((completed.length / allIds.length) * 100)
    };
  }, [isTutorialCompleted, getTutorialStatus]);

  return {
    // State
    progress,
    dismissed,
    
    // Getters
    getTutorialStatus,
    isTutorialCompleted,
    shouldShowTutorial,
    getCompletionStats,
    
    // Actions
    startTutorial,
    updateStep,
    completeTutorial,
    skipTutorial,
    dismissTutorial,
    resetAllProgress
  };
};

export default useTutorialProgress;
