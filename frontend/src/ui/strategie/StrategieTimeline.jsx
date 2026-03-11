/**
 * StrategieTimeline - V5-ULTIME
 * =============================
 */

import React from 'react';
import { Check, Clock } from 'lucide-react';

export const StrategieTimeline = ({ steps = [] }) => {
  return (
    <div className="space-y-0">
      {steps.map((step, idx) => (
        <div key={idx} className={`flex items-start gap-4 ${step.completed ? 'opacity-60' : ''}`}>
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
            ${step.completed ? 'bg-green-500' : step.active ? 'bg-[#F5A623]' : 'bg-white/10'}
          `}>
            {step.completed ? (
              <Check className="h-4 w-4 text-white" />
            ) : (
              <span className="text-white text-sm">{idx + 1}</span>
            )}
          </div>
          <div className="flex-1 pb-6 border-l border-white/10 pl-4 -ml-4">
            <h4 className="text-white font-medium">{step.title}</h4>
            {step.description && (
              <p className="text-gray-400 text-sm mt-1">{step.description}</p>
            )}
            {step.time && (
              <p className="text-gray-500 text-xs mt-2 flex items-center gap-1">
                <Clock className="h-3 w-3" /> {step.time}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StrategieTimeline;
