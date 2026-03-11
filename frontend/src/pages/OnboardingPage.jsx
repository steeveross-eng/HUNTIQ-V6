/**
 * OnboardingPage - Phase 10
 * 
 * Onboarding page wrapper.
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { OnboardingFlow } from '@/modules/onboarding';
import { STORAGE_KEYS } from '@/modules/onboarding/constants';

const OnboardingPage = () => {
  const navigate = useNavigate();

  // Check if onboarding already completed
  useEffect(() => {
    const isComplete = localStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETE) === 'true';
    if (isComplete) {
      // Redirect to dashboard if already completed
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  return <OnboardingFlow />;
};

export default OnboardingPage;
