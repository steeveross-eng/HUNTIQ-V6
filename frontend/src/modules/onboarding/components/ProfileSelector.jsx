/**
 * ProfileSelector - Phase 10
 * 
 * Generic selector card component for onboarding.
 * Supports single and multi-select modes.
 */

import React from 'react';
import { Check } from 'lucide-react';
import * as Icons from 'lucide-react';

// Get icon component by name
const getIcon = (iconName) => {
  if (!iconName) return null;
  return Icons[iconName] || Icons.Circle;
};

export const ProfileSelector = ({
  options = [],
  selected,
  onSelect,
  multiSelect = false,
  columns = 2,
  size = 'default' // 'compact', 'default', 'large'
}) => {
  const handleSelect = (optionId) => {
    if (multiSelect) {
      // Toggle selection
      const currentSelected = Array.isArray(selected) ? selected : [];
      if (currentSelected.includes(optionId)) {
        onSelect(currentSelected.filter(id => id !== optionId));
      } else {
        onSelect([...currentSelected, optionId]);
      }
    } else {
      // Single select
      onSelect(optionId);
    }
  };

  const isSelected = (optionId) => {
    if (multiSelect) {
      return Array.isArray(selected) && selected.includes(optionId);
    }
    return selected === optionId;
  };

  // Grid columns class
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-2 lg:grid-cols-4'
  };

  // Size classes
  const sizeClasses = {
    compact: 'p-3',
    default: 'p-4',
    large: 'p-6'
  };

  return (
    <div className={`grid ${gridCols[columns] || gridCols[2]} gap-3`} data-testid="profile-selector">
      {options.map((option) => {
        const IconComponent = getIcon(option.icon);
        const optionSelected = isSelected(option.id);

        return (
          <button
            key={option.id}
            onClick={() => handleSelect(option.id)}
            className={`
              relative text-left rounded-lg border transition-all duration-200
              ${sizeClasses[size]}
              ${optionSelected 
                ? 'border-[#F5A623] bg-[#F5A623]/10' 
                : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
              }
            `}
            data-testid={`option-${option.id}`}
          >
            {/* Selection indicator */}
            {optionSelected && (
              <div className="absolute top-2 right-2">
                <div className="w-5 h-5 rounded-full bg-[#F5A623] flex items-center justify-center">
                  <Check className="w-3 h-3 text-black" />
                </div>
              </div>
            )}
            
            {/* Icon */}
            {IconComponent && (
              <div className={`
                w-10 h-10 rounded-lg flex items-center justify-center mb-3
                ${optionSelected ? 'bg-[#F5A623]/20' : 'bg-white/10'}
              `}>
                <IconComponent className={`w-5 h-5 ${optionSelected ? 'text-[#F5A623]' : 'text-gray-400'}`} />
              </div>
            )}
            
            {/* Label */}
            <div className={`font-semibold ${optionSelected ? 'text-white' : 'text-gray-300'}`}>
              {option.label}
            </div>
            
            {/* Description */}
            {option.description && (
              <div className="text-sm text-gray-500 mt-1">
                {option.description}
              </div>
            )}
            
            {/* Extra info */}
            {option.years && (
              <div className="text-xs text-gray-600 mt-2">
                {option.years}
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default ProfileSelector;
