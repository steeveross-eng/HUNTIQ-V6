/**
 * 3D Data Layer - V5-ULTIME
 * =========================
 * 
 * Couche de données 3D pour visualisation terrain.
 */

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Box, RotateCcw, ZoomIn, ZoomOut, Move3d } from 'lucide-react';

export const Layers3D = ({ 
  visible = true, 
  elevation = true,
  exaggeration = 1.5,
  terrain = 'satellite'
}) => {
  const containerRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 45, y: 0 });
  const [zoom, setZoom] = useState(1);

  if (!visible) return null;

  return (
    <div 
      ref={containerRef}
      className="layers-3d relative w-full h-full"
      data-testid="layers-3d"
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
    >
      <div 
        className="absolute inset-0"
        style={{
          transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(${zoom})`,
          transformStyle: 'preserve-3d',
          transition: 'transform 0.3s ease-out'
        }}
      >
        {/* 3D terrain would be rendered here via Three.js or similar */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50" />
      </div>
    </div>
  );
};

export const Layers3DControls = ({ 
  onRotationChange,
  onZoomChange,
  onReset,
  onExaggerationChange,
  rotation = { x: 45, y: 0 },
  zoom = 1,
  exaggeration = 1.5,
  className 
}) => {
  return (
    <div className={`bg-black/80 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <h4 className="text-white text-sm font-medium mb-3 flex items-center gap-2">
        <Box className="h-4 w-4 text-[#F5A623]" />
        Vue 3D
      </h4>
      
      {/* Rotation X */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-gray-400 text-xs">Inclinaison</span>
          <span className="text-white text-xs">{rotation.x}°</span>
        </div>
        <Slider
          value={[rotation.x]}
          onValueChange={([v]) => onRotationChange?.({ ...rotation, x: v })}
          min={0}
          max={90}
          step={5}
        />
      </div>
      
      {/* Rotation Y */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-gray-400 text-xs">Rotation</span>
          <span className="text-white text-xs">{rotation.y}°</span>
        </div>
        <Slider
          value={[rotation.y]}
          onValueChange={([v]) => onRotationChange?.({ ...rotation, y: v })}
          min={-180}
          max={180}
          step={15}
        />
      </div>
      
      {/* Exaggeration */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-gray-400 text-xs">Relief</span>
          <span className="text-white text-xs">{exaggeration}x</span>
        </div>
        <Slider
          value={[exaggeration]}
          onValueChange={([v]) => onExaggerationChange?.(v)}
          min={1}
          max={3}
          step={0.25}
        />
      </div>
      
      {/* Zoom controls */}
      <div className="flex items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          className="h-8 w-8 p-0 flex-1"
          onClick={() => onZoomChange?.(Math.max(0.5, zoom - 0.25))}
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="h-8 w-8 p-0 flex-1"
          onClick={onReset}
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="h-8 w-8 p-0 flex-1"
          onClick={() => onZoomChange?.(Math.min(2, zoom + 0.25))}
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default Layers3D;
