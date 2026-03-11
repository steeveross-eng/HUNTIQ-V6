/**
 * MapPopup - Phase 8 Standardized Map Popup
 * 
 * BIONIC-compliant popup for Leaflet maps.
 * Provides consistent styling and behavior.
 * 
 * @version 1.0.0
 */

import React from 'react';
import { Popup } from 'react-leaflet';
import { X } from 'lucide-react';

// ============================================
// POPUP VARIANTS
// ============================================

export const POPUP_VARIANTS = {
  DEFAULT: 'default',
  WAYPOINT: 'waypoint',
  MARKER: 'marker',
  INFO: 'info',
  ACTION: 'action'
};

// ============================================
// BASE POPUP STYLES
// ============================================

const getPopupClassName = (variant) => {
  const baseClass = 'bionic-map-popup';
  return `${baseClass} ${baseClass}--${variant}`;
};

// ============================================
// MAP POPUP COMPONENT
// ============================================

/**
 * Standardized map popup component
 * 
 * @param {string} variant - Popup variant from POPUP_VARIANTS
 * @param {string} title - Popup title (optional)
 * @param {ReactNode} children - Popup content
 * @param {Function} onClose - Close handler (optional)
 * @param {Object} position - Leaflet position
 * @param {Object} options - Additional Leaflet popup options
 */
export const MapPopup = ({ 
  variant = POPUP_VARIANTS.DEFAULT,
  title,
  children,
  onClose,
  className = '',
  ...leafletOptions
}) => {
  return (
    <Popup 
      className={`${getPopupClassName(variant)} ${className}`}
      closeButton={false}
      {...leafletOptions}
    >
      <div className="bionic-popup-content">
        {/* Header */}
        {(title || onClose) && (
          <div className="bionic-popup-header">
            {title && (
              <h4 className="bionic-popup-title">{title}</h4>
            )}
            {onClose && (
              <button 
                onClick={onClose}
                className="bionic-popup-close"
                aria-label="Fermer"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
        
        {/* Body */}
        <div className="bionic-popup-body">
          {children}
        </div>
      </div>
    </Popup>
  );
};

// ============================================
// WAYPOINT POPUP COMPONENT
// ============================================

/**
 * Specialized popup for waypoints
 */
export const WaypointPopup = ({ 
  waypoint,
  onEdit,
  onDelete,
  onNavigate,
  ...props
}) => {
  return (
    <MapPopup 
      variant={POPUP_VARIANTS.WAYPOINT}
      title={waypoint.name}
      {...props}
    >
      <div className="space-y-2">
        {waypoint.description && (
          <p className="text-sm text-gray-400">{waypoint.description}</p>
        )}
        
        <div className="text-xs text-gray-500">
          {waypoint.latitude?.toFixed(6)}, {waypoint.longitude?.toFixed(6)}
        </div>
        
        {(onEdit || onDelete || onNavigate) && (
          <div className="flex gap-2 pt-2 border-t border-white/10">
            {onNavigate && (
              <button 
                onClick={() => onNavigate(waypoint)}
                className="flex-1 px-2 py-1 text-xs bg-[#F5A623]/10 text-[#F5A623] rounded hover:bg-[#F5A623]/20"
              >
                Naviguer
              </button>
            )}
            {onEdit && (
              <button 
                onClick={() => onEdit(waypoint)}
                className="flex-1 px-2 py-1 text-xs bg-white/10 text-white rounded hover:bg-white/20"
              >
                Modifier
              </button>
            )}
            {onDelete && (
              <button 
                onClick={() => onDelete(waypoint)}
                className="flex-1 px-2 py-1 text-xs bg-red-500/10 text-red-400 rounded hover:bg-red-500/20"
              >
                Supprimer
              </button>
            )}
          </div>
        )}
      </div>
    </MapPopup>
  );
};

// ============================================
// MARKER POPUP COMPONENT
// ============================================

/**
 * Simple marker popup
 */
export const MarkerPopup = ({ 
  label,
  sublabel,
  icon,
  ...props
}) => {
  return (
    <MapPopup variant={POPUP_VARIANTS.MARKER} {...props}>
      <div className="text-center">
        {icon && <div className="mb-1">{icon}</div>}
        <div className="font-bold text-white">{label}</div>
        {sublabel && (
          <div className="text-xs text-gray-400">{sublabel}</div>
        )}
      </div>
    </MapPopup>
  );
};

// ============================================
// INFO POPUP COMPONENT
// ============================================

/**
 * Information popup with structured data
 */
export const InfoPopup = ({ 
  title,
  items = [],
  footer,
  ...props
}) => {
  return (
    <MapPopup variant={POPUP_VARIANTS.INFO} title={title} {...props}>
      <div className="space-y-1">
        {items.map((item, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-gray-400">{item.label}:</span>
            <span className="text-white font-medium">{item.value}</span>
          </div>
        ))}
        
        {footer && (
          <div className="pt-2 mt-2 border-t border-white/10 text-xs text-gray-500">
            {footer}
          </div>
        )}
      </div>
    </MapPopup>
  );
};

export default MapPopup;
