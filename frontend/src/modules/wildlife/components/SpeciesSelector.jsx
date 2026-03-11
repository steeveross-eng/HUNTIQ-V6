/**
 * SpeciesSelector - Species selection component
 * BIONIC Design System compliant - No emojis
 * Phase 10 - Plan Maître Modules
 */
import React from 'react';
import { Badge } from '../../../components/ui/badge';
import { WildlifeService } from '../WildlifeService';
import { SpeciesIcon } from '../../../components/bionic/SpeciesIcon';
import { Target, Crosshair, Bird } from 'lucide-react';

export const SpeciesSelector = ({ 
  selected = 'deer',
  onSelect,
  showCategories = true
}) => {
  const species = WildlifeService.getPlaceholderSpecies();
  
  const categories = {
    big_game: { label: 'Gros gibier', Icon: Target },
    small_game: { label: 'Petit gibier', Icon: Crosshair },
    waterfowl: { label: 'Sauvagine', Icon: Bird }
  };

  const groupedSpecies = species.reduce((acc, s) => {
    if (!acc[s.category]) acc[s.category] = [];
    acc[s.category].push(s);
    return acc;
  }, {});

  if (!showCategories) {
    return (
      <div className="flex flex-wrap gap-2">
        {species.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect?.(s.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              selected === s.id 
                ? 'bg-[#f5a623] text-black' 
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <SpeciesIcon species={s.id} size="sm" rounded />
            <span className="text-sm font-medium">{s.name}</span>
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {Object.entries(groupedSpecies).map(([category, speciesList]) => {
        const CategoryIcon = categories[category]?.Icon || Target;
        return (
          <div key={category}>
            <div className="flex items-center gap-2 mb-2">
              <CategoryIcon className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
              <span className="text-slate-400 text-sm">{categories[category]?.label}</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {speciesList.map((s) => (
                <button
                  key={s.id}
                  onClick={() => onSelect?.(s.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                    selected === s.id 
                      ? 'bg-[#f5a623] text-black' 
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <SpeciesIcon species={s.id} size="sm" rounded />
                  <span className="text-sm">{s.name}</span>
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SpeciesSelector;
