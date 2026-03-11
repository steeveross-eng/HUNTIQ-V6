/**
 * PlanMaitreTimeline - V5-ULTIME Plan Maître
 * ==========================================
 * 
 * Timeline interactive du Plan Maître.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Circle, Clock, AlertCircle, ChevronRight } from 'lucide-react';

const PhaseStatus = {
  COMPLETED: 'completed',
  ACTIVE: 'active',
  PENDING: 'pending',
  WARNING: 'warning'
};

const StatusIcon = ({ status }) => {
  const icons = {
    [PhaseStatus.COMPLETED]: <CheckCircle2 className="h-6 w-6 text-green-500" />,
    [PhaseStatus.ACTIVE]: <Circle className="h-6 w-6 text-[#F5A623] fill-[#F5A623]/30 animate-pulse" />,
    [PhaseStatus.PENDING]: <Circle className="h-6 w-6 text-gray-500" />,
    [PhaseStatus.WARNING]: <AlertCircle className="h-6 w-6 text-yellow-500" />
  };
  return icons[status] || icons[PhaseStatus.PENDING];
};

export const PlanMaitreTimeline = ({ phases = [], onPhaseClick, compact = false }) => {
  if (compact) {
    return (
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {phases.map((phase, idx) => (
          <React.Fragment key={idx}>
            <div 
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors
                ${phase.status === 'active' ? 'bg-[#F5A623]/20 border border-[#F5A623]' : 'bg-white/5 hover:bg-white/10'}
              `}
              onClick={() => onPhaseClick?.(phase)}
            >
              <StatusIcon status={phase.status} />
              <span className="text-white text-sm whitespace-nowrap">{phase.name}</span>
            </div>
            {idx < phases.length - 1 && (
              <ChevronRight className="h-4 w-4 text-gray-500 flex-shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  return (
    <Card className="bg-black/40 border-white/10">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Clock className="h-5 w-5 text-[#F5A623]" />
          Timeline du Plan
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-white/10" />
          
          {phases.map((phase, idx) => (
            <div 
              key={idx}
              className={`relative flex items-start gap-4 pb-6 last:pb-0 cursor-pointer
                ${phase.status === 'active' ? 'opacity-100' : phase.status === 'completed' ? 'opacity-70' : 'opacity-50'}
              `}
              onClick={() => onPhaseClick?.(phase)}
            >
              {/* Status icon */}
              <div className="relative z-10 bg-[#0a0a0a] p-1">
                <StatusIcon status={phase.status} />
              </div>
              
              {/* Content */}
              <div className="flex-1 pt-0.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-white font-medium">{phase.name}</h4>
                  {phase.status === 'active' && (
                    <Badge className="bg-[#F5A623] text-black">En cours</Badge>
                  )}
                  {phase.status === 'completed' && (
                    <Badge variant="outline" className="text-green-400 border-green-400">Terminé</Badge>
                  )}
                </div>
                <p className="text-gray-400 text-sm mt-1">{phase.description}</p>
                
                {/* Progress bar for active phase */}
                {phase.status === 'active' && phase.progress !== undefined && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progression</span>
                      <span>{phase.progress}%</span>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-[#F5A623] rounded-full transition-all duration-500"
                        style={{ width: `${phase.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Tasks preview */}
                {phase.tasks && phase.tasks.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {phase.tasks.slice(0, 3).map((task, tIdx) => (
                      <span 
                        key={tIdx}
                        className={`text-xs px-2 py-1 rounded ${
                          task.completed ? 'bg-green-500/20 text-green-400' : 'bg-white/5 text-gray-400'
                        }`}
                      >
                        {task.name}
                      </span>
                    ))}
                    {phase.tasks.length > 3 && (
                      <span className="text-xs px-2 py-1 text-gray-500">
                        +{phase.tasks.length - 3} autres
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default PlanMaitreTimeline;
