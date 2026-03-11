/**
 * Simulation Data Layer - V5-ULTIME
 * ==================================
 * 
 * Couche de simulation de mouvements de faune.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Play, Pause, RotateCcw, FastForward } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const SimulationLayer = ({ mapRef, visible = true, running = false }) => {
  const [isRunning, setIsRunning] = useState(running);
  const [time, setTime] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [entities, setEntities] = useState([]);

  useEffect(() => {
    if (!isRunning || !visible) return;
    
    const interval = setInterval(() => {
      setTime(prev => prev + speed);
      // Update entity positions based on simulation
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isRunning, visible, speed]);

  if (!visible) return null;

  return (
    <div className="simulation-layer" data-testid="simulation-layer">
      {entities.map((entity, idx) => (
        <div
          key={idx}
          className="absolute w-3 h-3 rounded-full bg-[#F5A623] shadow-lg"
          style={{
            transform: `translate(${entity.x}px, ${entity.y}px)`,
            transition: 'transform 0.5s ease-out'
          }}
        />
      ))}
    </div>
  );
};

export const SimulationControls = ({ 
  onPlay, 
  onPause, 
  onReset, 
  onSpeedChange,
  isRunning = false,
  speed = 1,
  className 
}) => {
  return (
    <div className={`bg-black/80 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <h4 className="text-white text-sm font-medium mb-3">Simulation</h4>
      
      <div className="flex items-center gap-2 mb-3">
        <Button
          size="sm"
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={isRunning ? onPause : onPlay}
        >
          {isRunning ? (
            <Pause className="h-4 w-4" />
          ) : (
            <Play className="h-4 w-4" />
          )}
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="h-8 w-8 p-0"
          onClick={onReset}
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
        <div className="flex-1 px-2">
          <Slider
            value={[speed]}
            onValueChange={([v]) => onSpeedChange?.(v)}
            min={0.5}
            max={4}
            step={0.5}
          />
        </div>
        <span className="text-gray-400 text-xs w-8">{speed}x</span>
      </div>
      
      <div className="text-gray-400 text-xs">
        {isRunning ? 'Simulation en cours...' : 'Simulation en pause'}
      </div>
    </div>
  );
};

export default SimulationLayer;
