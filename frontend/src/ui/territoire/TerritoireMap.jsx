/**
 * TerritoireMap - V5-ULTIME
 * =========================
 */

import React, { useState, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MapPin, Layers, Plus, ZoomIn, ZoomOut } from 'lucide-react';

export const TerritoireMap = ({ 
  zones = [], 
  waypoints = [],
  onZoneClick,
  onWaypointClick,
  onAddWaypoint
}) => {
  const mapRef = useRef(null);
  const [zoom, setZoom] = useState(12);

  return (
    <Card className="bg-black/40 border-white/10 overflow-hidden">
      <div className="relative h-[400px] bg-gray-900">
        {/* Map placeholder - would use Leaflet/Mapbox in production */}
        <div 
          ref={mapRef}
          className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900"
        >
          {/* Zone overlays */}
          {zones.map((zone, idx) => (
            <div
              key={idx}
              className="absolute cursor-pointer"
              style={{
                left: `${20 + idx * 15}%`,
                top: `${20 + idx * 10}%`,
                width: '100px',
                height: '80px',
                backgroundColor: 'rgba(245, 166, 35, 0.3)',
                border: '2px solid rgba(245, 166, 35, 0.6)',
                borderRadius: '8px'
              }}
              onClick={() => onZoneClick?.(zone)}
            >
              <span className="absolute -top-6 left-0 text-xs text-white bg-black/80 px-2 py-0.5 rounded">
                {zone.name}
              </span>
            </div>
          ))}

          {/* Waypoint markers */}
          {waypoints.map((wp, idx) => (
            <div
              key={idx}
              className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-full"
              style={{
                left: `${30 + idx * 12}%`,
                top: `${40 + idx * 8}%`
              }}
              onClick={() => onWaypointClick?.(wp)}
            >
              <MapPin className="h-6 w-6 text-[#F5A623] drop-shadow-lg" />
            </div>
          ))}

          {/* Map controls */}
          <div className="absolute bottom-4 right-4 flex flex-col gap-2">
            <Button 
              size="sm" 
              variant="secondary" 
              className="h-8 w-8 p-0"
              onClick={() => setZoom(z => Math.min(18, z + 1))}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button 
              size="sm" 
              variant="secondary" 
              className="h-8 w-8 p-0"
              onClick={() => setZoom(z => Math.max(8, z - 1))}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
          </div>

          {/* Add waypoint button */}
          <div className="absolute top-4 right-4">
            <Button
              size="sm"
              className="bg-[#F5A623] text-black hover:bg-[#F5A623]/90"
              onClick={onAddWaypoint}
            >
              <Plus className="h-4 w-4 mr-1" />
              Waypoint
            </Button>
          </div>

          {/* Layer toggle */}
          <div className="absolute top-4 left-4">
            <Button size="sm" variant="secondary">
              <Layers className="h-4 w-4 mr-2" />
              Couches
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default TerritoireMap;
