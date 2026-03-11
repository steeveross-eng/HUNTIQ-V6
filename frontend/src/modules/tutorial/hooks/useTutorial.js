/**
 * useTutorial Hook - Phase 11
 * 
 * Main hook for tutorial navigation and control.
 */

import { useState, useCallback, useEffect } from 'react';
import { useTutorialProgress } from './useTutorialProgress';
import { getTutorialById } from '../data/tutorials';
import { STORAGE_KEYS } from '../constants';

export const useTutorial = (tutorialId = null) => {
  // Progress hook
  const progressHook = useTutorialProgress();
  const { 
    startTutorial, 
    updateStep, 
    completeTutorial, 
    skipTutorial,
    shouldShowTutorial,
    progress
  } = progressHook;

  // Current tutorial state
  const [activeTutorial, setActiveTutorial] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isActive, setIsActive] = useState(false);

  // Load tutorial if ID provided
  useEffect(() => {
    if (tutorialId) {
      const tutorial = getTutorialById(tutorialId);
      if (tutorial) {
        setActiveTutorial(tutorial);
        const savedProgress = progress[tutorialId];
        if (savedProgress?.currentStep) {
          setCurrentStepIndex(savedProgress.currentStep);
        }
      }
    }
  }, [tutorialId, progress]);

  // Get current step
  const currentStep = activeTutorial?.steps?.[currentStepIndex] || null;
  const totalSteps = activeTutorial?.steps?.length || 0;
  const isLastStep = currentStepIndex === totalSteps - 1;
  const isFirstStep = currentStepIndex === 0;

  /**
   * Start a tutorial
   */
  const start = useCallback((id = tutorialId) => {
    const tutorial = getTutorialById(id);
    if (!tutorial) return false;

    setActiveTutorial(tutorial);
    setCurrentStepIndex(0);
    setIsActive(true);
    startTutorial(id);
    
    // Save last tutorial
    localStorage.setItem(STORAGE_KEYS.LAST_TUTORIAL, id);
    
    return true;
  }, [tutorialId, startTutorial]);

  /**
   * Go to next step
   */
  const nextStep = useCallback(() => {
    if (!activeTutorial) return;

    if (isLastStep) {
      // Complete tutorial
      completeTutorial(activeTutorial.id);
      setIsActive(false);
    } else {
      const newIndex = currentStepIndex + 1;
      setCurrentStepIndex(newIndex);
      updateStep(activeTutorial.id, newIndex);
    }
  }, [activeTutorial, isLastStep, currentStepIndex, completeTutorial, updateStep]);

  /**
   * Go to previous step
   */
  const prevStep = useCallback(() => {
    if (!activeTutorial || isFirstStep) return;

    const newIndex = currentStepIndex - 1;
    setCurrentStepIndex(newIndex);
    updateStep(activeTutorial.id, newIndex);
  }, [activeTutorial, isFirstStep, currentStepIndex, updateStep]);

  /**
   * Go to specific step
   */
  const goToStep = useCallback((index) => {
    if (!activeTutorial || index < 0 || index >= totalSteps) return;

    setCurrentStepIndex(index);
    updateStep(activeTutorial.id, index);
  }, [activeTutorial, totalSteps, updateStep]);

  /**
   * Skip tutorial
   */
  const skip = useCallback(() => {
    if (!activeTutorial) return;

    skipTutorial(activeTutorial.id);
    setIsActive(false);
    setActiveTutorial(null);
  }, [activeTutorial, skipTutorial]);

  /**
   * Close tutorial (same as skip)
   */
  const close = useCallback(() => {
    setIsActive(false);
    // Don't mark as skipped, allow resuming
  }, []);

  /**
   * Complete tutorial
   */
  const complete = useCallback(() => {
    if (!activeTutorial) return;

    completeTutorial(activeTutorial.id);
    setIsActive(false);
  }, [activeTutorial, completeTutorial]);

  return {
    // State
    activeTutorial,
    currentStep,
    currentStepIndex,
    totalSteps,
    isActive,
    isFirstStep,
    isLastStep,
    
    // Navigation
    start,
    nextStep,
    prevStep,
    goToStep,
    skip,
    close,
    complete,
    
    // Progress
    shouldShowTutorial,
    ...progressHook
  };
};

export default useTutorial;
