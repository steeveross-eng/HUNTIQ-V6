/**
 * useOnboarding Hook - Phase 10
 * 
 * Manages onboarding flow state and navigation.
 */

import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ONBOARDING_STEPS, STEP_ORDER, STORAGE_KEYS } from '../constants';

export const useOnboarding = () => {
  const navigate = useNavigate();
  
  // Current step state
  const [currentStep, setCurrentStep] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.ONBOARDING_STEP);
    return saved || ONBOARDING_STEPS.WELCOME;
  });
  
  // Completion state
  const [isComplete, setIsComplete] = useState(() => {
    return localStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETE) === 'true';
  });
  
  // Loading state
  const [isLoading, setIsLoading] = useState(false);

  // Get current step index
  const currentStepIndex = STEP_ORDER.indexOf(currentStep);
  const totalSteps = STEP_ORDER.length - 1; // Exclude 'complete'
  const progress = Math.round((currentStepIndex / totalSteps) * 100);

  // Save step to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.ONBOARDING_STEP, currentStep);
  }, [currentStep]);

  /**
   * Go to next step
   */
  const nextStep = useCallback(() => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEP_ORDER.length) {
      setCurrentStep(STEP_ORDER[nextIndex]);
    }
  }, [currentStepIndex]);

  /**
   * Go to previous step
   */
  const prevStep = useCallback(() => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(STEP_ORDER[prevIndex]);
    }
  }, [currentStepIndex]);

  /**
   * Go to specific step
   */
  const goToStep = useCallback((step) => {
    if (STEP_ORDER.includes(step)) {
      setCurrentStep(step);
    }
  }, []);

  /**
   * Complete onboarding
   */
  const completeOnboarding = useCallback(() => {
    localStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETE, 'true');
    setIsComplete(true);
    setCurrentStep(ONBOARDING_STEPS.COMPLETE);
  }, []);

  /**
   * Reset onboarding (for testing)
   */
  const resetOnboarding = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.ONBOARDING_COMPLETE);
    localStorage.removeItem(STORAGE_KEYS.ONBOARDING_STEP);
    localStorage.removeItem(STORAGE_KEYS.USER_PROFILE);
    setIsComplete(false);
    setCurrentStep(ONBOARDING_STEPS.WELCOME);
  }, []);

  /**
   * Skip onboarding
   */
  const skipOnboarding = useCallback(() => {
    completeOnboarding();
    navigate('/dashboard');
  }, [completeOnboarding, navigate]);

  /**
   * Check if can go back
   */
  const canGoBack = currentStepIndex > 0 && currentStep !== ONBOARDING_STEPS.COMPLETE;

  /**
   * Check if can go next
   */
  const canGoNext = currentStepIndex < STEP_ORDER.length - 1;

  return {
    // State
    currentStep,
    isComplete,
    isLoading,
    progress,
    currentStepIndex,
    totalSteps,
    
    // Navigation
    nextStep,
    prevStep,
    goToStep,
    canGoBack,
    canGoNext,
    
    // Actions
    completeOnboarding,
    resetOnboarding,
    skipOnboarding,
    setIsLoading
  };
};

export default useOnboarding;
