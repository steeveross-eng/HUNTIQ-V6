/**
 * BiologicalSeasonSelector.jsx — Dropdown Compact BIONIC™ V8.2
 *
 * Menu déroulant compact remplaçant les onglets horizontaux.
 * - Un seul bouton montrant la saison active
 * - Dropdown avec les 5 saisons
 * - Icônes + labels
 * - Indicateur saison courante (dot)
 * - Style cohérent bg-black/60 backdrop-blur
 */
import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { Activity, Flame, Moon, Snowflake, Sprout, ChevronDown } from 'lucide-react';
import { BIOLOGICAL_SEASONS, getCurrentBiologicalSeason } from '@/config/biologicalSeasons';

const SEASON_ICONS = {
  activity: Activity,
  flame: Flame,
  moon: Moon,
  snowflake: Snowflake,
  sprout: Sprout,
};

export const BiologicalSeasonSelector = React.memo(({ selectedSeason, onSeasonChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const currentSeason = useMemo(() => getCurrentBiologicalSeason(), []);
  const activeSeason = useMemo(
    () => BIOLOGICAL_SEASONS.find(s => s.id === selectedSeason) || BIOLOGICAL_SEASONS[0],
    [selectedSeason]
  );
  const ActiveIcon = SEASON_ICONS[activeSeason.icon] || Activity;

  const handleSelect = useCallback((seasonId) => {
    onSeasonChange(seasonId);
    setIsOpen(false);
  }, [onSeasonChange]);

  // Fermer le dropdown au clic extérieur
  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef} data-testid="season-selector">
      {/* Bouton principal — saison active */}
      <button
        onClick={() => setIsOpen(prev => !prev)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md
          bg-black/60 backdrop-blur-sm border border-gray-700/40
          text-[11px] font-bold uppercase tracking-wider
          transition-all duration-150 hover:border-gray-600/60"
        style={{ color: activeSeason.color }}
        data-testid="season-dropdown-trigger"
      >
        <ActiveIcon className="h-3.5 w-3.5" />
        <span>{activeSeason.shortLabel}</span>
        <ChevronDown className={`h-3 w-3 transition-transform duration-150 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className="absolute top-full left-0 mt-1 z-[9999]
            bg-[#0d0d14]/95 backdrop-blur-md border border-gray-700/50
            rounded-lg shadow-xl shadow-black/40 overflow-hidden min-w-[180px]"
          data-testid="season-dropdown-menu"
        >
          {BIOLOGICAL_SEASONS.map((season) => {
            const Icon = SEASON_ICONS[season.icon] || Activity;
            const isActive = selectedSeason === season.id;
            const isCurrent = currentSeason.id === season.id;

            return (
              <button
                key={season.id}
                onClick={() => handleSelect(season.id)}
                className={`
                  w-full flex items-center gap-2.5 px-3 py-2
                  text-[11px] font-bold uppercase tracking-wider
                  transition-all duration-100 text-left
                  ${isActive
                    ? 'text-white'
                    : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                  }
                `}
                style={isActive ? { backgroundColor: `${season.color}15`, color: season.color } : undefined}
                data-testid={`season-btn-${season.id}`}
              >
                <Icon className="h-3.5 w-3.5 flex-shrink-0" style={isActive ? { color: season.color } : undefined} />
                <span className="flex-1">{season.label}</span>
                {isCurrent && (
                  <span
                    className="w-2 h-2 rounded-full animate-pulse flex-shrink-0"
                    style={{ backgroundColor: season.color, boxShadow: `0 0 4px ${season.color}` }}
                    title="Saison actuelle"
                  />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
});

BiologicalSeasonSelector.displayName = 'BiologicalSeasonSelector';
