/**
 * OnboardingFlow - Phase 10
 * 
 * Main onboarding flow orchestrator.
 * Manages navigation between onboarding steps.
 */

import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Crosshair, Sparkles, Check, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import BionicLogo from '@/components/BionicLogo';
import { useOnboarding } from '../hooks/useOnboarding';
import { useUserProfile } from '../hooks/useUserProfile';
import { OnboardingStep } from './OnboardingStep';
import { TerritorySelector } from './TerritorySelector';
import { ExperienceSelector } from './ExperienceSelector';
import { ObjectivesSelector } from './ObjectivesSelector';
import { ONBOARDING_STEPS } from '../constants';

// ============================================
// WELCOME STEP
// ============================================

const WelcomeStep = ({ onNext, onSkip }) => (
  <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6" data-testid="onboarding-welcome">
    {/* Background gradient */}
    <div className="absolute inset-0 bg-gradient-to-br from-[#F5A623]/5 via-transparent to-transparent" />
    
    <div className="relative z-10 text-center max-w-lg">
      {/* Logo */}
      <div className="mb-8">
        <BionicLogo size="lg" />
      </div>
      
      {/* Icon */}
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-[#F5A623]/10 mb-6">
        <Crosshair className="w-10 h-10 text-[#F5A623]" />
      </div>
      
      {/* Title */}
      <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
        Bienvenue sur BIONIC
      </h1>
      
      {/* Subtitle */}
      <p className="text-lg text-gray-400 mb-8">
        Configurons votre expérience de chasse intelligente en quelques étapes.
      </p>
      
      {/* Features */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10 text-left">
        {[
          { icon: '🎯', label: 'Analyse de territoire' },
          { icon: '📊', label: 'Stratégies personnalisées' },
          { icon: '🗺️', label: 'Cartes interactives' }
        ].map((feature, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/10">
            <span className="text-xl">{feature.icon}</span>
            <span className="text-sm text-gray-300">{feature.label}</span>
          </div>
        ))}
      </div>
      
      {/* CTA */}
      <div className="space-y-4">
        <Button
          onClick={onNext}
          size="lg"
          className="w-full sm:w-auto bg-[#F5A623] hover:bg-[#F5A623]/90 text-black font-bold px-8"
          data-testid="start-onboarding"
        >
          Commencer
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
        
        <div>
          <Button
            variant="link"
            onClick={onSkip}
            className="text-gray-500 hover:text-gray-400"
            data-testid="skip-onboarding"
          >
            Passer l'introduction
          </Button>
        </div>
      </div>
    </div>
  </div>
);

// ============================================
// COMPLETE STEP
// ============================================

const CompleteStep = ({ profile, onFinish }) => {
  const navigate = useNavigate();
  
  const handleFinish = () => {
    if (onFinish) onFinish();
    navigate('/dashboard');
  };
  
  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6" data-testid="onboarding-complete">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-transparent" />
      
      <div className="relative z-10 text-center max-w-lg">
        {/* Success icon */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-500/10 mb-6">
          <Check className="w-10 h-10 text-emerald-500" />
        </div>
        
        {/* Title */}
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Profil configuré!
        </h1>
        
        {/* Subtitle */}
        <p className="text-lg text-gray-400 mb-8">
          Votre expérience BIONIC est maintenant personnalisée.
        </p>
        
        {/* Profile summary */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8 text-left">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Votre profil
          </h3>
          
          <div className="space-y-3">
            {profile.territory && (
              <div className="flex justify-between">
                <span className="text-gray-500">Territoire</span>
                <span className="text-white font-medium capitalize">{profile.territory}</span>
              </div>
            )}
            {profile.experience && (
              <div className="flex justify-between">
                <span className="text-gray-500">Expérience</span>
                <span className="text-white font-medium capitalize">{profile.experience}</span>
              </div>
            )}
            {profile.objectives?.length > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-500">Objectifs</span>
                <span className="text-white font-medium">{profile.objectives.length} sélectionnés</span>
              </div>
            )}
          </div>
        </div>
        
        {/* CTA */}
        <Button
          onClick={handleFinish}
          size="lg"
          className="w-full sm:w-auto bg-[#F5A623] hover:bg-[#F5A623]/90 text-black font-bold px-8"
          data-testid="finish-onboarding"
        >
          <Sparkles className="w-5 h-5 mr-2" />
          Accéder à BIONIC
        </Button>
      </div>
    </div>
  );
};

// ============================================
// PROGRESS BAR
// ============================================

const ProgressBar = ({ progress, currentStep, totalSteps }) => (
  <div className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur border-b border-white/10">
    <div className="max-w-lg mx-auto px-4 py-3">
      <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
        <span>Configuration du profil</span>
        <span>{currentStep} / {totalSteps}</span>
      </div>
      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-[#F5A623] transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  </div>
);

// ============================================
// MAIN FLOW COMPONENT
// ============================================

const OnboardingFlow = () => {
  const navigate = useNavigate();
  
  // Hooks
  const {
    currentStep,
    progress,
    currentStepIndex,
    totalSteps,
    nextStep,
    prevStep,
    completeOnboarding,
    skipOnboarding
  } = useOnboarding();
  
  const {
    profile,
    setTerritory,
    setExperience,
    setObjectives,
    saveProfile,
    isProfileValid
  } = useUserProfile();

  // Handle completion
  const handleComplete = useCallback(() => {
    saveProfile();
    completeOnboarding();
  }, [saveProfile, completeOnboarding]);

  // Render current step
  const renderStep = () => {
    switch (currentStep) {
      case ONBOARDING_STEPS.WELCOME:
        return (
          <WelcomeStep 
            onNext={nextStep} 
            onSkip={skipOnboarding}
          />
        );
      
      case ONBOARDING_STEPS.TERRITORY:
        return (
          <TerritorySelector
            selected={profile.territory}
            onSelect={setTerritory}
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      
      case ONBOARDING_STEPS.EXPERIENCE:
        return (
          <ExperienceSelector
            selected={profile.experience}
            onSelect={setExperience}
            onNext={nextStep}
            onBack={prevStep}
          />
        );
      
      case ONBOARDING_STEPS.OBJECTIVES:
        return (
          <ObjectivesSelector
            selected={profile.objectives}
            onSelect={setObjectives}
            onNext={handleComplete}
            onBack={prevStep}
          />
        );
      
      case ONBOARDING_STEPS.COMPLETE:
        return (
          <CompleteStep 
            profile={profile}
            onFinish={() => navigate('/dashboard')}
          />
        );
      
      default:
        return <WelcomeStep onNext={nextStep} onSkip={skipOnboarding} />;
    }
  };

  // Show progress bar except for welcome and complete
  const showProgress = ![ONBOARDING_STEPS.WELCOME, ONBOARDING_STEPS.COMPLETE].includes(currentStep);

  return (
    <div className="min-h-screen bg-black" data-testid="onboarding-flow">
      {showProgress && (
        <ProgressBar 
          progress={progress}
          currentStep={currentStepIndex}
          totalSteps={totalSteps - 1}
        />
      )}
      
      <div className={showProgress ? 'pt-14' : ''}>
        {renderStep()}
      </div>
    </div>
  );
};

export default OnboardingFlow;
