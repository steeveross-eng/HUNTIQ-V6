/**
 * OnboardingWizard - V5-ULTIME Monétisation
 * =========================================
 * 
 * Assistant d'accueil en plusieurs étapes.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  User, MapPin, Target, Crown, 
  ChevronRight, ChevronLeft, Check, SkipForward
} from 'lucide-react';
import OnboardingService from './OnboardingService';

const stepIcons = {
  profile: User,
  territory: MapPin,
  objectives: Target,
  plan_maitre: Crown
};

const OnboardingWizard = ({ 
  userId = 'current_user',
  onComplete,
  onSkip
}) => {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [currentStepConfig, setCurrentStepConfig] = useState(null);
  const [formData, setFormData] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Charger le statut
  useEffect(() => {
    const fetchStatus = async () => {
      setLoading(true);
      const result = await OnboardingService.getStatus(userId);
      
      if (result.success) {
        setStatus(result.status);
        setCurrentStepConfig(result.current_step_config);
        
        // Si déjà complété
        if (result.status.completed) {
          onComplete && onComplete();
        }
      }
      setLoading(false);
    };

    fetchStatus();
  }, [userId, onComplete]);

  // Gérer le changement de formulaire
  const handleChange = (questionId, value) => {
    setFormData(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // Soumettre l'étape
  const handleSubmit = async () => {
    if (!status?.current_step) return;

    setSubmitting(true);
    const result = await OnboardingService.submitStep(
      userId,
      status.current_step,
      formData
    );

    if (result.success) {
      if (result.onboarding_completed) {
        onComplete && onComplete();
      } else {
        // Charger la prochaine étape
        const newStatus = await OnboardingService.getStatus(userId);
        if (newStatus.success) {
          setStatus(newStatus.status);
          setCurrentStepConfig(newStatus.current_step_config);
          setFormData({});
        }
      }
    }
    setSubmitting(false);
  };

  // Ignorer l'onboarding
  const handleSkip = async () => {
    await OnboardingService.skip(userId);
    onSkip && onSkip();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  if (!currentStepConfig) {
    return null;
  }

  const StepIcon = stepIcons[status?.current_step] || User;
  const progress = status?.completed_steps?.length 
    ? (status.completed_steps.length / 4) * 100 
    : 0;

  return (
    <div 
      data-testid="onboarding-wizard"
      className="max-w-2xl mx-auto p-6"
    >
      {/* Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">
            Étape {(status?.completed_steps?.length || 0) + 1} / 4
          </span>
          <Badge className="bg-[#F5A623]/20 text-[#F5A623]">
            {Math.round(progress)}% complété
          </Badge>
        </div>
        <Progress value={progress} className="h-2 [&>div]:bg-[#F5A623]" />
      </div>

      {/* Step Card */}
      <Card className="bg-[#1a1a2e] border-white/10">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-[#F5A623]/20 flex items-center justify-center">
              <StepIcon className="h-6 w-6 text-[#F5A623]" />
            </div>
            <div>
              <CardTitle className="text-white text-xl">
                {currentStepConfig.title}
              </CardTitle>
              <p className="text-gray-400 text-sm">
                {currentStepConfig.description}
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {currentStepConfig.questions?.map((question) => (
            <div key={question.id} className="space-y-2">
              <Label className="text-white">{question.label}</Label>
              
              {question.type === 'select' && (
                <Select
                  value={formData[question.id] || ''}
                  onValueChange={(value) => handleChange(question.id, value)}
                >
                  <SelectTrigger 
                    data-testid={`input-${question.id}`}
                    className="bg-white/5 border-white/10 text-white"
                  >
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1a1a2e] border-white/10">
                    {question.options?.map((option) => (
                      <SelectItem 
                        key={option.value} 
                        value={option.value}
                        className="text-white hover:bg-white/10"
                      >
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {question.type === 'multiselect' && (
                <div className="flex flex-wrap gap-2">
                  {question.options?.map((option) => {
                    const isSelected = (formData[question.id] || []).includes(option.value);
                    return (
                      <Badge
                        key={option.value}
                        data-testid={`option-${option.value}`}
                        className={`
                          cursor-pointer transition-colors
                          ${isSelected 
                            ? 'bg-[#F5A623] text-black' 
                            : 'bg-white/10 text-white hover:bg-white/20'
                          }
                        `}
                        onClick={() => {
                          const current = formData[question.id] || [];
                          const newValue = isSelected
                            ? current.filter(v => v !== option.value)
                            : [...current, option.value];
                          handleChange(question.id, newValue);
                        }}
                      >
                        {isSelected && <Check className="h-3 w-3 mr-1" />}
                        {option.label}
                      </Badge>
                    );
                  })}
                </div>
              )}

              {question.type === 'text' && (
                <Input
                  data-testid={`input-${question.id}`}
                  value={formData[question.id] || ''}
                  onChange={(e) => handleChange(question.id, e.target.value)}
                  placeholder={question.placeholder || ''}
                  className="bg-white/5 border-white/10 text-white"
                />
              )}

              {question.type === 'number' && (
                <Input
                  data-testid={`input-${question.id}`}
                  type="number"
                  value={formData[question.id] || ''}
                  onChange={(e) => handleChange(question.id, parseInt(e.target.value))}
                  min={question.min}
                  max={question.max}
                  className="bg-white/5 border-white/10 text-white w-32"
                />
              )}
            </div>
          ))}

          {currentStepConfig.auto_generate && (
            <div className="p-6 bg-white/5 rounded-lg text-center">
              <Crown className="h-12 w-12 text-[#F5A623] mx-auto mb-4" />
              <h3 className="text-white font-medium mb-2">
                Création de votre Plan Maître
              </h3>
              <p className="text-gray-400 text-sm">
                Nous allons créer votre plan personnalisé basé sur vos réponses.
              </p>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between">
          <Button
            variant="ghost"
            onClick={handleSkip}
            className="text-gray-400 hover:text-white"
          >
            <SkipForward className="h-4 w-4 mr-2" />
            Passer
          </Button>

          <Button
            data-testid="next-step-btn"
            onClick={handleSubmit}
            disabled={submitting}
            className="bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
          >
            {submitting ? (
              'Chargement...'
            ) : currentStepConfig.auto_generate ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Terminer
              </>
            ) : (
              <>
                Continuer
                <ChevronRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default OnboardingWizard;
