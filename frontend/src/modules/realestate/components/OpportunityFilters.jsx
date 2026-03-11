/**
 * OpportunityFilters - Filters for opportunity search
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Label } from '../../../components/ui/label';
import { Slider } from '../../../components/ui/slider';
import { Button } from '../../../components/ui/button';
import { 
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue 
} from '../../../components/ui/select';
import { Filter, RefreshCw } from 'lucide-react';

/**
 * Opportunity Filters Component
 * 
 * @param {Object} props
 * @param {Object} props.filters - Current filter values
 * @param {Function} props.onFiltersChange - Filters change callback
 * @param {Function} props.onReset - Reset filters callback
 */
const OpportunityFilters = ({ 
  filters = {},
  onFiltersChange = null,
  onReset = null
}) => {
  const {
    minScore = 0,
    minDiscount = -50,
    propertyType = 'all',
    region = 'quebec'
  } = filters;

  const handleChange = (key, value) => {
    onFiltersChange?.({ ...filters, [key]: value });
  };

  return (
    <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
      <CardContent className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-[var(--bionic-text-primary)] flex items-center gap-2">
            <Filter className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
            Filtres
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-7 text-xs text-[var(--bionic-text-muted)]"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Réinitialiser
          </Button>
        </div>

        {/* Property Type */}
        <div className="space-y-2">
          <Label className="text-xs text-[var(--bionic-text-muted)]">Type de propriété</Label>
          <Select 
            value={propertyType} 
            onValueChange={(v) => handleChange('propertyType', v)}
          >
            <SelectTrigger className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les types</SelectItem>
              <SelectItem value="terrain">Terrain</SelectItem>
              <SelectItem value="chalet">Chalet</SelectItem>
              <SelectItem value="ferme">Ferme</SelectItem>
              <SelectItem value="lot_boise">Lot boisé</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Region */}
        <div className="space-y-2">
          <Label className="text-xs text-[var(--bionic-text-muted)]">Région</Label>
          <Select 
            value={region} 
            onValueChange={(v) => handleChange('region', v)}
          >
            <SelectTrigger className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="quebec">Québec</SelectItem>
              <SelectItem value="mauricie">Mauricie</SelectItem>
              <SelectItem value="laurentides">Laurentides</SelectItem>
              <SelectItem value="outaouais">Outaouais</SelectItem>
              <SelectItem value="saguenay">Saguenay</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Min BIONIC Score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-[var(--bionic-text-muted)]">Score BIONIC minimum</Label>
            <span className="text-xs text-[var(--bionic-gold-primary)] font-medium">{minScore}</span>
          </div>
          <Slider
            value={[minScore]}
            onValueChange={(v) => handleChange('minScore', v[0])}
            min={0}
            max={100}
            step={5}
            className="py-2"
          />
        </div>

        {/* Min Discount */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-[var(--bionic-text-muted)]">Rabais minimum</Label>
            <span className="text-xs text-[var(--bionic-gold-primary)] font-medium">{minDiscount}%</span>
          </div>
          <Slider
            value={[minDiscount]}
            onValueChange={(v) => handleChange('minDiscount', v[0])}
            min={-50}
            max={50}
            step={5}
            className="py-2"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default OpportunityFilters;
