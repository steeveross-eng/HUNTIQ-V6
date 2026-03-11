/**
 * PopupManager - Phase 8 Popup Management System
 * 
 * Centralized popup/modal management for consistent UX.
 * Prevents multiple popups from overlapping.
 * 
 * @version 1.0.0
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// ============================================
// POPUP TYPES
// ============================================

export const POPUP_TYPES = {
  MODAL: 'modal',
  SHEET: 'sheet',
  DIALOG: 'dialog',
  DRAWER: 'drawer',
  TOOLTIP: 'tooltip',
  NOTIFICATION: 'notification'
};

export const POPUP_PRIORITY = {
  LOW: 1,
  NORMAL: 5,
  HIGH: 10,
  CRITICAL: 100
};

// ============================================
// POPUP CONTEXT
// ============================================

const PopupContext = createContext(null);

// ============================================
// POPUP PROVIDER
// ============================================

export const PopupProvider = ({ children }) => {
  const [popups, setPopups] = useState([]);
  const [activePopup, setActivePopup] = useState(null);

  /**
   * Open a popup
   * @param {string} id - Unique popup identifier
   * @param {string} type - Popup type from POPUP_TYPES
   * @param {Object} data - Popup data/content
   * @param {Object} options - Additional options (priority, onClose, etc.)
   */
  const openPopup = useCallback((id, type, data = {}, options = {}) => {
    const popup = {
      id,
      type,
      data,
      priority: options.priority || POPUP_PRIORITY.NORMAL,
      onClose: options.onClose,
      timestamp: Date.now()
    };

    setPopups(prev => {
      // Remove existing popup with same ID
      const filtered = prev.filter(p => p.id !== id);
      return [...filtered, popup];
    });

    // Set as active if highest priority
    setActivePopup(current => {
      if (!current || popup.priority >= current.priority) {
        return popup;
      }
      return current;
    });

    return popup.id;
  }, []);

  /**
   * Close a popup by ID
   */
  const closePopup = useCallback((id) => {
    setPopups(prev => {
      const popup = prev.find(p => p.id === id);
      if (popup?.onClose) {
        popup.onClose();
      }
      return prev.filter(p => p.id !== id);
    });

    setActivePopup(current => {
      if (current?.id === id) {
        // Find next highest priority popup
        return popups
          .filter(p => p.id !== id)
          .sort((a, b) => b.priority - a.priority)[0] || null;
      }
      return current;
    });
  }, [popups]);

  /**
   * Close all popups
   */
  const closeAllPopups = useCallback(() => {
    popups.forEach(popup => {
      if (popup.onClose) {
        popup.onClose();
      }
    });
    setPopups([]);
    setActivePopup(null);
  }, [popups]);

  /**
   * Check if a popup is open
   */
  const isPopupOpen = useCallback((id) => {
    return popups.some(p => p.id === id);
  }, [popups]);

  /**
   * Get popup by ID
   */
  const getPopup = useCallback((id) => {
    return popups.find(p => p.id === id) || null;
  }, [popups]);

  const value = {
    popups,
    activePopup,
    openPopup,
    closePopup,
    closeAllPopups,
    isPopupOpen,
    getPopup
  };

  return (
    <PopupContext.Provider value={value}>
      {children}
    </PopupContext.Provider>
  );
};

// ============================================
// CUSTOM HOOK
// ============================================

export const usePopups = () => {
  const context = useContext(PopupContext);
  if (!context) {
    throw new Error('usePopups must be used within a PopupProvider');
  }
  return context;
};

// ============================================
// POPUP WRAPPER COMPONENT
// ============================================

export const PopupWrapper = ({ 
  id, 
  type = POPUP_TYPES.MODAL,
  priority = POPUP_PRIORITY.NORMAL,
  children,
  onClose
}) => {
  const { openPopup, closePopup, isPopupOpen } = usePopups();

  React.useEffect(() => {
    if (children) {
      openPopup(id, type, { children }, { priority, onClose });
    }
    return () => closePopup(id);
  }, [id, type, children, priority, onClose, openPopup, closePopup]);

  return null;
};

export default PopupContext;
