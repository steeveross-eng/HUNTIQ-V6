/**
 * BionicPrecisionZonesLayer.jsx — BIONIC Territory Engine Layers v3.0
 * 
 * Renders micro-delineated precision zones on the map as polygons.
 * Each zone shows probability, module label, and hover effects.
 * 
 * Phase 2 extraction from TerritoryMap.jsx
 * @module territory/BionicPrecisionZonesLayer
 */

import React from 'react';
import { Polygon, Tooltip, Popup } from 'react-leaflet';
import { Lightbulb } from 'lucide-react';

const BionicPrecisionZonesLayer = ({ zones = [], layersVisible = {}, t = (k) => k }) => {
  if (!zones || zones.length === 0) return null;

  return (
    <>
      {zones
        .filter(zone => layersVisible[zone.moduleKey])
        .map((zone, index) => (
          <Polygon
            key={`bionic-precision-${zone.id}-${index}`}
            positions={zone.polygon}
            pathOptions={{
              color: zone.color,
              fillColor: zone.color,
              fillOpacity: zone.fillOpacity || 0.03,
              weight: zone.strokeWeight || 1.5,
              opacity: zone.strokeOpacity || 0.7,
              dashArray: zone.probability >= 80 ? null : '3, 3'
            }}
            eventHandlers={{
              mouseover: (e) => {
                e.target.setStyle({
                  fillOpacity: Math.min(0.25, (zone.fillOpacity || 0.03) + 0.15),
                  weight: (zone.strokeWeight || 1.5) + 1,
                  opacity: 1
                });
              },
              mouseout: (e) => {
                e.target.setStyle({
                  fillOpacity: zone.fillOpacity || 0.03,
                  weight: zone.strokeWeight || 1.5,
                  opacity: zone.strokeOpacity || 0.7
                });
              }
            }}
          >
            <Tooltip sticky className="bionic-tooltip" direction="auto" offset={[0, -10]}>
              <div className="text-center min-w-[120px]">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <span>{zone.icon}</span>
                  <span className="font-bold text-sm">{zone.probability}%</span>
                </div>
                <div className="text-xs text-gray-600">{zone.label}</div>
                <div className="text-xs font-medium mt-1" style={{ color: zone.color }}>
                  {zone.rating?.text || 'Zone active'}
                </div>
              </div>
            </Tooltip>
            <Popup autoPanPaddingTopLeft={[10, 180]}>
              <div className="min-w-[220px]">
                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200">
                  <span className="text-2xl">{zone.icon}</span>
                  <div>
                    <p className="font-bold text-gray-800">{zone.label}</p>
                    <p className="text-xs text-gray-500">{zone.name}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 text-sm">Probabilite:</span>
                  <span className="font-bold text-xl" style={{ color: zone.color }}>{zone.probability}%</span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-600 text-sm">Evaluation:</span>
                  <span className="font-medium px-2 py-0.5 rounded text-sm" style={{
                    backgroundColor: `${zone.color}20`, color: zone.color
                  }}>
                    {zone.rating?.text || 'Zone active'}
                  </span>
                </div>
                <div className="bg-gray-50 rounded p-2 text-xs">
                  <p className="text-gray-500 mb-1">Niveau de confiance:</p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="h-2 rounded-full transition-all" style={{
                      width: `${zone.probability}%`, backgroundColor: zone.color
                    }} />
                  </div>
                </div>
                {zone.recommendations && zone.recommendations.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1 font-medium flex items-center gap-1">
                      <Lightbulb className="h-3 w-3" /> {t('recommendations')}:
                    </p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {zone.recommendations.slice(0, 2).map((rec, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <span className="text-gray-400">-</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Popup>
          </Polygon>
        ))}
    </>
  );
};

export default BionicPrecisionZonesLayer;
