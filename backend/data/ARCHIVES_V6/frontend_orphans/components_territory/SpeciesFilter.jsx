/**
 * SpeciesFilter - Species filter panel
 * BIONIC Design System compliant - No emojis
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Filter } from 'lucide-react';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

// Species Configuration - No emojis, using images
export const SPECIES_CONFIG = {
  orignal: { color: '#8B4513', label: 'Orignal', heatColor: 'brown', speciesId: 'moose' },
  chevreuil: { color: '#D2691E', label: 'Chevreuil', heatColor: 'orange', speciesId: 'deer' },
  ours: { color: '#2F4F4F', label: 'Ours', heatColor: 'darkslategray', speciesId: 'bear' },
  autre: { color: '#808080', label: 'Autre', heatColor: 'gray', speciesId: 'other' }
};

// Time window options (kept for backward compatibility)
export const TIME_WINDOWS = [
  { value: 24, label: '24 heures' },
  { value: 72, label: '72 heures' },
  { value: 168, label: '7 jours' },
  { value: 720, label: '30 jours' }
];

const SpeciesFilter = ({
  selectedSpecies,
  onSpeciesChange
}) => {
  return (
    <Card className="bg-background border-border mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center gap-2">
          <Filter className="h-4 w-4 text-[#f5a623]" />
          Filtre
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div>
          <Label className="text-gray-400 text-xs">Espèce</Label>
          <Select value={selectedSpecies} onValueChange={onSpeciesChange}>
            <SelectTrigger className="bg-card border-border mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les espèces</SelectItem>
              {Object.entries(SPECIES_CONFIG).filter(([key]) => key !== 'autre').map(([key, config]) => (
                <SelectItem key={key} value={key}>
                  <span className="flex items-center gap-2">
                    <SpeciesIcon species={config.speciesId} size="xs" rounded />
                    {config.label}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
};

export default SpeciesFilter;
