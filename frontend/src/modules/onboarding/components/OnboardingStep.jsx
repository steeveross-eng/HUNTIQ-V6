/**
 * OnboardingStep - Phase 10
 * 
 * Base component for onboarding step UI.
 * BIONIC design system compliant.
 */

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const OnboardingStep = ({
  title,
  subtitle,
  icon: Icon,
  children,
  onNext,
  onBack,
  onSkip,
  canGoNext = true,
  canGoBack = true,
  showSkip = false,
  nextLabel = 'Continuer',
  backLabel = 'Retour',
  skipLabel = 'Passer'
}) => {
  return (
    <div className="min-h-screen bg-black flex flex-col" data-testid="onboarding-step">
      {/* Content */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          {/* Header */}
          <div className="text-center mb-8">
            {Icon && (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#F5A623]/10 mb-4">
                <Icon className="w-8 h-8 text-[#F5A623]" />
              </div>
            )}
            
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
              {title}
            </h1>
            
            {subtitle && (
              <p className="text-gray-400 text-lg">
                {subtitle}
              </p>
            )}
          </div>
          
          {/* Step Content */}
          <div className="space-y-6">
            {children}
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="border-t border-white/10 p-4 bg-black/50 backdrop-blur">
        <div className="max-w-lg mx-auto flex items-center justify-between gap-4">
          {/* Back Button */}
          <div className="w-28">
            {canGoBack && onBack && (
              <Button
                variant="ghost"
                onClick={onBack}
                className="text-gray-400 hover:text-white"
                data-testid="onboarding-back"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                {backLabel}
              </Button>
            )}
          </div>
          
          {/* Skip Button */}
          <div className="flex-1 text-center">
            {showSkip && onSkip && (
              <Button
                variant="link"
                onClick={onSkip}
                className="text-gray-500 hover:text-gray-400"
                data-testid="onboarding-skip"
              >
                {skipLabel}
              </Button>
            )}
          </div>
          
          {/* Next Button */}
          <div className="w-28 text-right">
            {onNext && (
              <Button
                onClick={onNext}
                disabled={!canGoNext}
                className="bg-[#F5A623] hover:bg-[#F5A623]/90 text-black font-semibold"
                data-testid="onboarding-next"
              >
                {nextLabel}
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingStep;
