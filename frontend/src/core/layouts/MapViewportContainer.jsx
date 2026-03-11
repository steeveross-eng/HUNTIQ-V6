/**
 * MapViewportContainer - BIONIC™ Full-Viewport Map Layout
 * ===========================================================
 * 
 * Container optimisé pour les pages cartographiques.
 * - Utilise 100% de la hauteur visible (viewport)
 * - Empêche tout scroll vertical inutile
 * - Garde tous les contrôles visibles en permanence
 * - Centre automatiquement la carte dans la fenêtre
 * - Responsive sur toutes les résolutions
 * 
 * Architecture LEGO V5 - Module isolé.
 * 
 * Usage:
 * <MapViewportContainer
 *   header={<MonHeader />}
 *   leftPanel={<PanneauCouches />}
 *   rightPanel={<PanneauAnalyse />}
 *   bottomBar={<BarreOutils />}
 * >
 *   <MapContainer ... />
 * </MapViewportContainer>
 */

import React, { useState, useCallback } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, ChevronUp, X } from 'lucide-react';

// Configuration des hauteurs fixes
const HEADER_HEIGHT = 64; // 4rem - header principal de l'app
const TAB_BAR_HEIGHT = 48; // 3rem - barre d'onglets si présente

/**
 * MapViewportContainer - Container principal full-viewport
 */
export const MapViewportContainer = ({
  children,
  header,
  subHeader,
  leftPanel,
  rightPanel,
  bottomBar,
  floatingControls,
  className = '',
  hasTabBar = false,
  headerHeight = HEADER_HEIGHT,
  tabBarHeight = TAB_BAR_HEIGHT,
}) => {
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);
  const [bottomBarCollapsed, setBottomBarCollapsed] = useState(false);

  // Calculer la hauteur disponible pour le contenu
  const totalHeaderHeight = headerHeight + (hasTabBar ? tabBarHeight : 0);

  return (
    <div 
      className={`fixed inset-0 bg-black overflow-hidden ${className}`}
      style={{ paddingTop: `${headerHeight}px` }}
      data-testid="map-viewport-container"
    >
      {/* Sub-Header / Tab Bar (si fourni) */}
      {subHeader && (
        <div 
          className="w-full bg-gradient-to-r from-black via-gray-900 to-black border-b border-[#f5a623]/30 z-30"
          style={{ height: hasTabBar ? `${tabBarHeight}px` : 'auto' }}
        >
          {subHeader}
        </div>
      )}

      {/* Container principal avec panneau + carte */}
      <div 
        className="flex w-full"
        style={{ height: `calc(100vh - ${totalHeaderHeight}px)` }}
      >
        {/* Panneau gauche (collapsible) */}
        {leftPanel && (
          <CollapsiblePanel
            position="left"
            collapsed={leftPanelCollapsed}
            onToggle={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
          >
            {leftPanel}
          </CollapsiblePanel>
        )}

        {/* Zone centrale - Carte */}
        <div className="flex-1 relative overflow-hidden">
          {/* Contrôles flottants en overlay */}
          {floatingControls && (
            <div className="absolute top-2 left-2 right-2 z-[1000] pointer-events-none">
              <div className="pointer-events-auto">
                {floatingControls}
              </div>
            </div>
          )}

          {/* Carte - prend tout l'espace disponible */}
          <div className="absolute inset-0">
            {children}
          </div>

          {/* Barre inférieure (collapsible) */}
          {bottomBar && (
            <CollapsibleBottomBar
              collapsed={bottomBarCollapsed}
              onToggle={() => setBottomBarCollapsed(!bottomBarCollapsed)}
            >
              {bottomBar}
            </CollapsibleBottomBar>
          )}
        </div>

        {/* Panneau droit (collapsible) */}
        {rightPanel && (
          <CollapsiblePanel
            position="right"
            collapsed={rightPanelCollapsed}
            onToggle={() => setRightPanelCollapsed(!rightPanelCollapsed)}
          >
            {rightPanel}
          </CollapsiblePanel>
        )}
      </div>
    </div>
  );
};

/**
 * CollapsiblePanel - Panneau latéral rétractable
 */
const CollapsiblePanel = ({
  children,
  position = 'left',
  collapsed = false,
  onToggle,
  width = 240,
  collapsedWidth = 40,
}) => {
  const isLeft = position === 'left';
  
  return (
    <div 
      className={`relative bg-gray-900/95 border-gray-800 transition-all duration-300 flex flex-col ${
        isLeft ? 'border-r' : 'border-l'
      }`}
      style={{ width: collapsed ? `${collapsedWidth}px` : `${width}px` }}
    >
      {/* Bouton toggle */}
      <button
        onClick={onToggle}
        className={`absolute top-1/2 -translate-y-1/2 z-50 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-full p-1 border border-gray-700 transition-all ${
          isLeft 
            ? (collapsed ? 'right-[-12px]' : 'right-[-12px]') 
            : (collapsed ? 'left-[-12px]' : 'left-[-12px]')
        }`}
        aria-label={collapsed ? 'Ouvrir le panneau' : 'Fermer le panneau'}
      >
        {isLeft 
          ? (collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />)
          : (collapsed ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />)
        }
      </button>

      {/* Contenu du panneau */}
      <div className={`flex-1 overflow-y-auto overflow-x-hidden ${collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
        {children}
      </div>
    </div>
  );
};

/**
 * CollapsibleBottomBar - Barre inférieure rétractable
 */
const CollapsibleBottomBar = ({
  children,
  collapsed = false,
  onToggle,
  height = 120,
  collapsedHeight = 32,
}) => {
  return (
    <div 
      className="absolute bottom-0 left-0 right-0 bg-gray-900/95 border-t border-gray-800 transition-all duration-300 z-[500]"
      style={{ height: collapsed ? `${collapsedHeight}px` : `${height}px` }}
    >
      {/* Bouton toggle */}
      <button
        onClick={onToggle}
        className="absolute top-[-12px] left-1/2 -translate-x-1/2 z-50 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-full p-1 border border-gray-700 transition-all"
        aria-label={collapsed ? 'Ouvrir la barre' : 'Fermer la barre'}
      >
        {collapsed ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {/* Contenu de la barre */}
      <div className={`h-full overflow-hidden ${collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
        {children}
      </div>
    </div>
  );
};

/**
 * FloatingPanel - Panneau flottant positionné librement
 */
export const FloatingPanel = ({
  children,
  position = 'top-left', // top-left, top-right, bottom-left, bottom-right, top-center, bottom-center
  className = '',
  visible = true,
  onClose,
  draggable = false,
  width = 'auto',
  maxHeight = '50vh',
}) => {
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  if (!visible) return null;

  return (
    <div
      className={`absolute z-[1000] bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-lg shadow-xl overflow-hidden ${positionClasses[position]} ${className}`}
      style={{ width, maxHeight }}
    >
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-2 right-2 z-10 p-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          aria-label="Fermer"
        >
          <X className="h-4 w-4" />
        </button>
      )}
      <div className="overflow-y-auto" style={{ maxHeight }}>
        {children}
      </div>
    </div>
  );
};

/**
 * MapHeader - En-tête compact pour pages cartographiques
 */
export const MapHeader = ({
  title,
  subtitle,
  icon: Icon,
  actions,
  backButton,
  className = '',
}) => {
  return (
    <div className={`flex items-center justify-between px-4 py-2 h-full ${className}`}>
      <div className="flex items-center gap-3">
        {backButton}
        {backButton && <div className="h-5 w-px bg-gray-700" />}
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-5 w-5 text-[#f5a623]" />}
          <div>
            <h1 className="text-base font-bold text-white leading-tight">{title}</h1>
            {subtitle && <p className="text-[10px] text-gray-400 leading-tight">{subtitle}</p>}
          </div>
        </div>
      </div>
      {actions && (
        <div className="flex items-center gap-2">
          {actions}
        </div>
      )}
    </div>
  );
};

/**
 * MapTabBar - Barre d'onglets compacte pour pages cartographiques
 */
export const MapTabBar = ({
  children,
  rightContent,
  className = '',
}) => {
  return (
    <div className={`flex items-center justify-between px-4 py-1 h-full ${className}`}>
      <div className="flex items-center gap-2">
        {children}
      </div>
      {rightContent && (
        <div className="flex items-center gap-2">
          {rightContent}
        </div>
      )}
    </div>
  );
};

/**
 * CoordinatesOverlay - Affichage des coordonnées GPS en overlay
 */
export const CoordinatesOverlay = ({
  lat,
  lng,
  zoom,
  visible = true,
  position = 'bottom-left',
  className = '',
}) => {
  if (!visible || (lat === undefined && lng === undefined)) return null;

  const positionClasses = {
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
  };

  return (
    <div 
      className={`absolute z-[900] bg-black/80 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-gray-700 font-mono text-xs ${positionClasses[position]} ${className}`}
    >
      <div className="flex items-center gap-3 text-gray-300">
        <span>
          <span className="text-gray-500">Lat:</span> {lat?.toFixed(6) || '—'}
        </span>
        <span>
          <span className="text-gray-500">Lng:</span> {lng?.toFixed(6) || '—'}
        </span>
        {zoom !== undefined && (
          <span>
            <span className="text-gray-500">Zoom:</span> {zoom}
          </span>
        )}
      </div>
    </div>
  );
};

/**
 * MapControlsGroup - Groupe de contrôles flottants pour la carte
 */
export const MapControlsGroup = ({
  children,
  position = 'top-right',
  className = '',
}) => {
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
  };

  return (
    <div className={`absolute z-[900] flex flex-col gap-2 ${positionClasses[position]} ${className}`}>
      {children}
    </div>
  );
};

/**
 * MapControlButton - Bouton de contrôle stylisé
 */
export const MapControlButton = ({
  children,
  onClick,
  active = false,
  disabled = false,
  title,
  className = '',
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`
        p-2 rounded-lg border transition-all
        ${active 
          ? 'bg-[#f5a623] text-black border-[#f5a623]' 
          : 'bg-gray-900/90 text-gray-300 border-gray-700 hover:bg-gray-800 hover:text-white'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {children}
    </button>
  );
};

export default MapViewportContainer;
