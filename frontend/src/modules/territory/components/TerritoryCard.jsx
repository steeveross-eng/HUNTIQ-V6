/**
 * TerritoryCard - Territory display card
 * Phase 10 - Plan Maître Modules
 * Version: 1.1.0 - BIONIC Design System Compliance
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { TerritoryService } from '../TerritoryService';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Target, CircleDot, MapPin } from 'lucide-react';

export const TerritoryCard = ({ 
  territory,
  onSelect,
  onViewDetails,
  compact = false
}) => {
  const { t } = useLanguage();
  if (!territory) return null;

  const typeInfo = TerritoryService.getTerritoryTypeInfo(territory.type);

  const getSpeciesCount = (species = []) => {
    return species.slice(0, 4).length;
  };

  if (compact) {
    return (
      <div 
        className="flex items-center gap-3 bg-[var(--bionic-bg-card)] rounded-lg p-3 border border-[var(--bionic-border-secondary)] cursor-pointer hover:border-[var(--bionic-gold-primary)]/50"
        onClick={() => onSelect?.(territory)}
      >
        <Target className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
        <div className="flex-1 min-w-0">
          <p className="text-[var(--bionic-text-primary)] text-sm font-medium truncate">{territory.name}</p>
          <p className="text-[var(--bionic-text-secondary)] text-xs">{territory.region}</p>
        </div>
        <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">
          {typeInfo.label}
        </Badge>
      </div>
    );
  }

  return (
    <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] overflow-hidden hover:border-[var(--bionic-gold-primary)]/50 transition-colors">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <Target className="h-6 w-6 text-[var(--bionic-gold-primary)]" />
            <div>
              <h3 className="text-[var(--bionic-text-primary)] font-semibold">{territory.name}</h3>
              <p className="text-[var(--bionic-text-secondary)] text-sm">{territory.region}</p>
            </div>
          </div>
          <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">
            {typeInfo.label}
          </Badge>
        </div>

        {/* Species */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-[var(--bionic-text-secondary)] text-sm">{t('common_species') || 'Espèces'}:</span>
          <div className="flex items-center gap-1">
            {territory.species?.slice(0, 4).map((s, i) => (
              <CircleDot key={i} className="h-4 w-4 text-[var(--bionic-gold-primary)]" />
            ))}
            {territory.species?.length > 4 && (
              <span className="text-[var(--bionic-text-muted)] text-xs ml-1">+{territory.species.length - 4}</span>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {territory.area_km2 && (
            <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-2 text-center">
              <div className="text-[var(--bionic-text-primary)] font-bold">{territory.area_km2}</div>
              <div className="text-xs text-[var(--bionic-text-muted)]">km²</div>
            </div>
          )}
          <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-2 text-center">
            <div className={`font-bold ${territory.available ? 'text-[var(--bionic-green-primary)]' : 'text-[var(--bionic-red-primary)]'}`}>
              {territory.available ? t('common_available') || 'Disponible' : t('common_unavailable') || 'Indisponible'}
            </div>
            <div className="text-xs text-[var(--bionic-text-muted)]">{t('common_status') || 'Statut'}</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {onViewDetails && (
            <Button 
              className="flex-1 bg-[var(--bionic-gold-primary)] hover:bg-[var(--bionic-gold-light)] text-black"
              onClick={() => onViewDetails(territory)}
            >
              {t('common_view_details') || 'Voir détails'}
            </Button>
          )}
          {onSelect && (
            <Button 
              variant="outline"
              className="border-[var(--bionic-border-secondary)]"
              onClick={() => onSelect(territory)}
            >
              {t('common_select') || 'Sélectionner'}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TerritoryCard;
