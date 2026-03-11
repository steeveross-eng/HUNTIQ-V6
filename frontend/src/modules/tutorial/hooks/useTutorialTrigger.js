/**
 * useTutorialTrigger Hook - Phase 11
 * 
 * Handles automatic tutorial triggering based on context.
 */

import { useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { useTutorialProgress } from './useTutorialProgress';
import { TUTORIAL_TRIGGERS, getTutorialById } from '../data/tutorials';
import { TUTORIAL_CONTEXTS, TRIGGER_CONDITIONS } from '../constants';
import { STORAGE_KEYS as ONBOARDING_KEYS } from '@/modules/onboarding/constants';

// Map routes to contexts
const ROUTE_CONTEXT_MAP = {
  '/dashboard': TUTORIAL_CONTEXTS.DASHBOARD,
  '/map': TUTORIAL_CONTEXTS.MAP,
  '/territoire': TUTORIAL_CONTEXTS.TERRITORY,
  '/analytics': TUTORIAL_CONTEXTS.ANALYTICS,
  '/plan-maitre': TUTORIAL_CONTEXTS.PLAN_MAITRE
};

export const useTutorialTrigger = (onTrigger) => {
  const location = useLocation();
  const { shouldShowTutorial } = useTutorialProgress();

  /**
   * Check if onboarding is complete
   */
  const isOnboardingComplete = useCallback(() => {
    return localStorage.getItem(ONBOARDING_KEYS.ONBOARDING_COMPLETE) === 'true';
  }, []);

  /**
   * Get tutorial to trigger for current context
   */
  const getTutorialForContext = useCallback((context) => {
    const tutorialIds = TUTORIAL_TRIGGERS[context] || [];
    
    for (const id of tutorialIds) {
      const tutorial = getTutorialById(id);
      if (!tutorial) continue;

      // Check if should show
      if (!shouldShowTutorial(id)) continue;

      // Check trigger condition
      if (tutorial.trigger === TRIGGER_CONDITIONS.ON_ONBOARDING_COMPLETE) {
        if (!isOnboardingComplete()) continue;
      }

      // Check if ON_FIRST_VISIT
      if (tutorial.trigger === TRIGGER_CONDITIONS.ON_FIRST_VISIT) {
        const visitKey = `huntiq_visited_${context}`;
        if (localStorage.getItem(visitKey)) continue;
        localStorage.setItem(visitKey, 'true');
      }

      return tutorial;
    }

    return null;
  }, [shouldShowTutorial, isOnboardingComplete]);

  /**
   * Trigger tutorial for current route
   */
  const triggerForCurrentRoute = useCallback(() => {
    const context = ROUTE_CONTEXT_MAP[location.pathname];
    if (!context) return null;

    const tutorial = getTutorialForContext(context);
    if (tutorial && onTrigger) {
      onTrigger(tutorial);
    }
    return tutorial;
  }, [location.pathname, getTutorialForContext, onTrigger]);

  // Auto-trigger on route change
  useEffect(() => {
    // Small delay to let page render first
    const timer = setTimeout(() => {
      triggerForCurrentRoute();
    }, 1000);

    return () => clearTimeout(timer);
  }, [location.pathname]);

  /**
   * Manually trigger tutorial by ID
   */
  const triggerTutorial = useCallback((tutorialId) => {
    const tutorial = getTutorialById(tutorialId);
    if (tutorial && shouldShowTutorial(tutorialId) && onTrigger) {
      onTrigger(tutorial);
      return true;
    }
    return false;
  }, [shouldShowTutorial, onTrigger]);

  return {
    triggerForCurrentRoute,
    triggerTutorial,
    getTutorialForContext,
    isOnboardingComplete
  };
};

export default useTutorialTrigger;
