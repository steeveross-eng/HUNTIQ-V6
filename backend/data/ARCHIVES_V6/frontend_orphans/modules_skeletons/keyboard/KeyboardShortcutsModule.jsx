/**
 * KeyboardShortcutsModule - Module de raccourcis clavier BIONIC™
 * ==============================================================
 * 
 * Module isolé, activable par page, sans interférence avec les 
 * interactions cartographiques.
 * 
 * Architecture LEGO V5 - Module autonome.
 * 
 * Raccourcis disponibles:
 * - Escape: Fermer les panneaux ouverts
 * - F: Basculer en mode plein écran
 * - L: Toggle panneau gauche (Layers)
 * - A: Toggle panneau droit (Analysis)
 * - +/-: Zoom in/out sur la carte
 * - Arrow keys: Pan de la carte
 * - Space: Centrer sur position actuelle
 * - M: Basculer entre les modes de carte
 * - H: Afficher/masquer l'aide des raccourcis
 * 
 * STATUS: PRÉPARÉ - En attente d'approbation COPILOT MAÎTRE
 */

import { useEffect, useCallback, useState } from 'react';

// Configuration des raccourcis par page
const PAGE_SHORTCUTS = {
  '/map': ['escape', 'f', 'l', 'a', 'plus', 'minus', 'arrows', 'space', 'm', 'h'],
  '/territoire': ['escape', 'f', 'l', 'a', 'plus', 'minus', 'arrows', 'space', 'm', 'h'],
  '/forecast': ['escape', 'f', 'h'],
  '/analyze': ['escape', 'f', 'h'],
  '/admin-geo': ['escape', 'f', 'l', 'a', 'h'],
};

// Éléments qui doivent capturer les événements clavier (inputs, textareas, etc.)
const CAPTURE_ELEMENTS = ['INPUT', 'TEXTAREA', 'SELECT'];

/**
 * Hook useKeyboardShortcuts
 * 
 * @param {Object} handlers - Objet avec les handlers pour chaque raccourci
 * @param {string} pagePath - Chemin de la page actuelle
 * @param {boolean} enabled - Activer/désactiver les raccourcis
 */
export const useKeyboardShortcuts = (handlers = {}, pagePath = '/', enabled = true) => {
  const [showHelp, setShowHelp] = useState(false);

  const handleKeyDown = useCallback((event) => {
    // Ne pas capturer si désactivé
    if (!enabled) return;

    // Ne pas capturer si focus sur un élément de saisie
    if (CAPTURE_ELEMENTS.includes(event.target.tagName)) return;

    // Vérifier si le raccourci est autorisé pour cette page
    const allowedShortcuts = PAGE_SHORTCUTS[pagePath] || [];
    
    const key = event.key.toLowerCase();
    const isCtrl = event.ctrlKey || event.metaKey;
    const isShift = event.shiftKey;

    // Escape - Fermer les panneaux
    if (key === 'escape' && allowedShortcuts.includes('escape')) {
      event.preventDefault();
      handlers.onEscape?.();
      return;
    }

    // F - Plein écran
    if (key === 'f' && !isCtrl && allowedShortcuts.includes('f')) {
      event.preventDefault();
      handlers.onFullscreen?.();
      return;
    }

    // L - Toggle panneau gauche
    if (key === 'l' && !isCtrl && allowedShortcuts.includes('l')) {
      event.preventDefault();
      handlers.onToggleLeftPanel?.();
      return;
    }

    // A - Toggle panneau droit
    if (key === 'a' && !isCtrl && allowedShortcuts.includes('a')) {
      event.preventDefault();
      handlers.onToggleRightPanel?.();
      return;
    }

    // + - Zoom in
    if ((key === '+' || key === '=') && allowedShortcuts.includes('plus')) {
      event.preventDefault();
      handlers.onZoomIn?.();
      return;
    }

    // - - Zoom out
    if (key === '-' && allowedShortcuts.includes('minus')) {
      event.preventDefault();
      handlers.onZoomOut?.();
      return;
    }

    // Space - Centrer sur position
    if (key === ' ' && allowedShortcuts.includes('space')) {
      event.preventDefault();
      handlers.onCenterPosition?.();
      return;
    }

    // M - Mode carte
    if (key === 'm' && !isCtrl && allowedShortcuts.includes('m')) {
      event.preventDefault();
      handlers.onToggleMapMode?.();
      return;
    }

    // H - Afficher aide
    if (key === 'h' && !isCtrl && allowedShortcuts.includes('h')) {
      event.preventDefault();
      setShowHelp(prev => !prev);
      handlers.onToggleHelp?.();
      return;
    }

    // Arrow keys - Pan
    if (allowedShortcuts.includes('arrows')) {
      if (key === 'arrowup') {
        event.preventDefault();
        handlers.onPanUp?.();
        return;
      }
      if (key === 'arrowdown') {
        event.preventDefault();
        handlers.onPanDown?.();
        return;
      }
      if (key === 'arrowleft') {
        event.preventDefault();
        handlers.onPanLeft?.();
        return;
      }
      if (key === 'arrowright') {
        event.preventDefault();
        handlers.onPanRight?.();
        return;
      }
    }
  }, [enabled, handlers, pagePath]);

  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [enabled, handleKeyDown]);

  return { showHelp, setShowHelp };
};

/**
 * Composant KeyboardShortcutsHelp - Overlay d'aide
 */
export const KeyboardShortcutsHelp = ({ visible, onClose, shortcuts = [] }) => {
  if (!visible) return null;

  const defaultShortcuts = [
    { key: 'Esc', description: 'Fermer les panneaux' },
    { key: 'F', description: 'Mode plein écran' },
    { key: 'L', description: 'Toggle panneau Couches' },
    { key: 'A', description: 'Toggle panneau Analyse' },
    { key: '+/-', description: 'Zoom avant/arrière' },
    { key: '↑↓←→', description: 'Déplacer la carte' },
    { key: 'Espace', description: 'Centrer sur ma position' },
    { key: 'M', description: 'Changer le mode de carte' },
    { key: 'H', description: 'Afficher cette aide' },
  ];

  const displayShortcuts = shortcuts.length > 0 ? shortcuts : defaultShortcuts;

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">Raccourcis Clavier</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Fermer"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-2">
          {displayShortcuts.map((shortcut, index) => (
            <div 
              key={index}
              className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
            >
              <span className="text-gray-300">{shortcut.description}</span>
              <kbd className="bg-gray-800 text-[#f5a623] px-2 py-1 rounded font-mono text-sm">
                {shortcut.key}
              </kbd>
            </div>
          ))}
        </div>
        
        <p className="text-gray-500 text-xs mt-4 text-center">
          Appuyez sur <kbd className="bg-gray-800 px-1 rounded">H</kbd> pour masquer
        </p>
      </div>
    </div>
  );
};

/**
 * Hook utilitaire pour le mode plein écran
 */
export const useFullscreen = (elementRef = null) => {
  const [isFullscreen, setIsFullscreen] = useState(false);

  const toggleFullscreen = useCallback(() => {
    const element = elementRef?.current || document.documentElement;

    if (!document.fullscreenElement) {
      element.requestFullscreen?.().then(() => setIsFullscreen(true));
    } else {
      document.exitFullscreen?.().then(() => setIsFullscreen(false));
    }
  }, [elementRef]);

  useEffect(() => {
    const handleChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleChange);
    return () => document.removeEventListener('fullscreenchange', handleChange);
  }, []);

  return { isFullscreen, toggleFullscreen };
};

export default useKeyboardShortcuts;
