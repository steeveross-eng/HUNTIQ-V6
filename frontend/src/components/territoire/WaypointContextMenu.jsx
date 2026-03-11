/**
 * WaypointContextMenu — Menu contextuel BIONIC V5 pour waypoints
 * BIONIC V5 ULTIME 300% — waypoint_contextmenu_v1
 *
 * Clic droit (desktop) ou long press (mobile) sur un waypoint.
 * Options : Analyser | Modifier | Supprimer (avec confirmation)
 * Fade-out 150ms après suppression.
 * z-index élevé, jamais recouvert, modularité absolue.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Pencil, Trash2, X } from 'lucide-react';

const WaypointContextMenu = ({ position, waypoint, onClose, onDelete, onAnalyze, onEdit }) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const menuRef = useRef(null);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose();
      }
    };
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleEsc);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleEsc);
    };
  }, [onClose]);

  const handleDelete = useCallback(async () => {
    setDeleting(true);
    await onDelete(waypoint.id);
    // Fade-out is handled by the parent via animation
    setTimeout(() => {
      onClose();
    }, 150);
  }, [waypoint, onDelete, onClose]);

  if (!position || !waypoint) return null;

  // Prevent menu from going offscreen
  const menuStyle = {
    position: 'fixed',
    left: `${Math.min(position.x, window.innerWidth - 200)}px`,
    top: `${Math.min(position.y, window.innerHeight - (showConfirm ? 200 : 180))}px`,
    zIndex: 99999,
    pointerEvents: 'auto',
  };

  return (
    <div ref={menuRef} style={menuStyle} data-testid="waypoint-context-menu">
      <div
        className="bg-gray-900/95 border border-gray-700 rounded-lg shadow-2xl overflow-hidden backdrop-blur-xl"
        style={{ minWidth: '180px', animation: 'fadeIn 0.1s ease-out' }}
      >
        {/* Header */}
        <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
          <span className="text-xs font-bold text-white truncate max-w-[140px]">{waypoint.name}</span>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300" data-testid="context-menu-close">
            <X className="h-3 w-3" />
          </button>
        </div>

        {!showConfirm ? (
          <div className="py-1">
            {/* Analyser */}
            <button
              onClick={() => { if (onAnalyze) onAnalyze(waypoint); onClose(); }}
              className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-blue-500/15 hover:text-blue-400 flex items-center gap-2 transition-colors"
              data-testid="context-menu-analyze"
            >
              <Search className="h-4 w-4 text-blue-400" />
              Analyser
            </button>

            {/* Modifier */}
            <button
              onClick={() => { if (onEdit) onEdit(waypoint); onClose(); }}
              className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-amber-500/15 hover:text-amber-400 flex items-center gap-2 transition-colors"
              data-testid="context-menu-edit"
            >
              <Pencil className="h-4 w-4 text-amber-400" />
              Modifier
            </button>

            {/* Separator */}
            <div className="mx-2 my-1 border-t border-gray-800" />

            {/* Supprimer */}
            <button
              onClick={() => setShowConfirm(true)}
              className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-red-500/15 flex items-center gap-2 transition-colors"
              data-testid="context-menu-delete"
            >
              <Trash2 className="h-4 w-4" />
              Supprimer
            </button>
          </div>
        ) : (
          <div className="p-3 space-y-3">
            <p className="text-xs text-gray-300 leading-relaxed">
              Supprimer définitivement ce waypoint ?
            </p>
            <p className="text-[10px] text-gray-500 truncate">
              {waypoint.name} ({waypoint.lat?.toFixed(4)}, {waypoint.lng?.toFixed(4)})
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 text-xs py-1.5 px-3 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors border border-gray-700"
                data-testid="context-menu-cancel"
              >
                Annuler
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 text-xs py-1.5 px-3 rounded bg-red-600 text-white hover:bg-red-500 transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                data-testid="context-menu-confirm-delete"
              >
                <Trash2 className="h-3 w-3" />
                {deleting ? '...' : 'Supprimer'}
              </button>
            </div>
          </div>
        )}

        {/* Coords footer */}
        {!showConfirm && (
          <div className="px-3 py-1.5 border-t border-gray-800 text-[9px] text-gray-600">
            {waypoint.lat?.toFixed(5)}, {waypoint.lng?.toFixed(5)}
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default WaypointContextMenu;
