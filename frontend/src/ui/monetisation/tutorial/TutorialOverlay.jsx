/**
 * TutorialOverlay - V5-ULTIME Monétisation
 * =========================================
 * 
 * Overlay de tutoriel step-by-step.
 */

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { X, ChevronRight, ChevronLeft, Check, SkipForward } from 'lucide-react';
import TutorialService from './TutorialService';

const TutorialOverlay = ({
  tutorial,
  userId = 'current_user',
  onComplete,
  onSkip,
  onClose
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightPosition, setHighlightPosition] = useState(null);
  const overlayRef = useRef(null);

  const steps = tutorial?.steps || [];
  const step = steps[currentStep];

  // Positionner le highlight
  useEffect(() => {
    if (!step?.target) {
      setHighlightPosition(null);
      return;
    }

    const targetElement = document.querySelector(step.target);
    if (targetElement) {
      const rect = targetElement.getBoundingClientRect();
      setHighlightPosition({
        top: rect.top - 8,
        left: rect.left - 8,
        width: rect.width + 16,
        height: rect.height + 16
      });
    }
  }, [step]);

  // Gérer le passage à l'étape suivante
  const handleNext = async () => {
    await TutorialService.updateProgress(userId, tutorial.id, currentStep + 1);

    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      await TutorialService.updateProgress(userId, tutorial.id, null, true);
      onComplete && onComplete();
    }
  };

  // Étape précédente
  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  // Ignorer
  const handleSkip = async () => {
    await TutorialService.skipTutorial(userId, tutorial.id);
    onSkip && onSkip();
  };

  if (!tutorial || !step) return null;

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div 
      ref={overlayRef}
      data-testid="tutorial-overlay"
      className="fixed inset-0 z-50"
    >
      {/* Backdrop sombre */}
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />

      {/* Zone highlight */}
      {highlightPosition && (
        <div
          className="absolute border-2 border-[#F5A623] rounded-lg shadow-lg shadow-[#F5A623]/30 pointer-events-none transition-all duration-300"
          style={{
            top: highlightPosition.top,
            left: highlightPosition.left,
            width: highlightPosition.width,
            height: highlightPosition.height
          }}
        />
      )}

      {/* Card tutoriel */}
      <Card 
        className={`
          absolute bg-[#1a1a2e] border-[#F5A623]/30 shadow-xl max-w-md
          ${highlightPosition 
            ? highlightPosition.top > window.innerHeight / 2 
              ? 'bottom-auto top-4' 
              : 'top-auto bottom-4'
            : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
          }
          ${highlightPosition ? 'right-4' : ''}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Badge className="bg-[#F5A623] text-black">
              {currentStep + 1}/{steps.length}
            </Badge>
            <span className="text-white font-medium">{tutorial.title}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Progress */}
        <div className="px-4 pt-3">
          <Progress value={progress} className="h-1 [&>div]:bg-[#F5A623]" />
        </div>

        {/* Content */}
        <CardContent className="p-4">
          <h3 className="text-white font-semibold mb-2">{step.title}</h3>
          <p className="text-gray-400 text-sm">{step.content}</p>

          {/* Media si présent */}
          {step.media && (
            <div className="mt-4 rounded-lg overflow-hidden bg-white/5">
              {step.media.type === 'image' && (
                <img 
                  src={step.media.url} 
                  alt={step.title}
                  className="w-full"
                />
              )}
              {step.media.type === 'video' && (
                <video 
                  src={step.media.url} 
                  controls 
                  className="w-full"
                />
              )}
            </div>
          )}
        </CardContent>

        {/* Actions */}
        <div className="flex items-center justify-between p-4 border-t border-white/10">
          <div className="flex gap-2">
            {currentStep > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handlePrev}
                className="text-gray-400 hover:text-white"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Précédent
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSkip}
              className="text-gray-400 hover:text-white"
            >
              <SkipForward className="h-4 w-4 mr-1" />
              Ignorer
            </Button>
          </div>

          <Button
            data-testid="tutorial-next-btn"
            onClick={handleNext}
            className="bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
          >
            {currentStep < steps.length - 1 ? (
              <>
                Suivant
                <ChevronRight className="h-4 w-4 ml-1" />
              </>
            ) : (
              <>
                <Check className="h-4 w-4 mr-1" />
                Terminer
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default TutorialOverlay;
