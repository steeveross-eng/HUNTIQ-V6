/**
 * PropertyCard - Property display card
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { 
  MapPin, Ruler, DollarSign, TrendingUp, ExternalLink 
} from 'lucide-react';
import PropertySourceBadge from './PropertySourceBadge';

/**
 * Property Card Component
 * 
 * @param {Object} props
 * @param {Object} props.property - Property data
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.compact - Compact mode
 */
const PropertyCard = ({ 
  property = {},
  onClick = null,
  compact = false
}) => {
  const {
    title = 'Propriété',
    price = 0,
    area_m2 = 0,
    bionic_score = null,
    source = 'manual',
    images = [],
    coordinates = {}
  } = property;

  const formatPrice = (price) => {
    if (price >= 1000000) {
      return `${(price / 1000000).toFixed(1)}M$`;
    }
    return `${(price / 1000).toFixed(0)}k$`;
  };

  const formatArea = (area) => {
    if (area >= 10000) {
      return `${(area / 10000).toFixed(1)} ha`;
    }
    return `${area.toLocaleString()} m²`;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-[var(--bionic-green-primary)]';
    if (score >= 60) return 'text-[var(--bionic-gold-primary)]';
    if (score >= 40) return 'text-[var(--bionic-orange-primary)]';
    return 'text-[var(--bionic-text-muted)]';
  };

  if (compact) {
    return (
      <div 
        className="flex items-center gap-3 p-3 bg-[var(--bionic-bg-hover)] rounded-lg cursor-pointer hover:bg-[var(--bionic-bg-card)] transition-colors"
        onClick={onClick}
      >
        <div className="w-12 h-12 bg-[var(--bionic-bg-card)] rounded overflow-hidden flex-shrink-0">
          {images[0] ? (
            <img src={images[0]} alt={title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <MapPin className="w-5 h-5 text-[var(--bionic-text-muted)]" />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-[var(--bionic-text-primary)] truncate">
            {title}
          </p>
          <div className="flex items-center gap-2 text-xs text-[var(--bionic-text-muted)]">
            <span>{formatPrice(price)}</span>
            <span>•</span>
            <span>{formatArea(area_m2)}</span>
          </div>
        </div>
        {bionic_score !== null && (
          <span className={`text-sm font-bold ${getScoreColor(bionic_score)}`}>
            {bionic_score}
          </span>
        )}
      </div>
    );
  }

  return (
    <Card 
      className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] overflow-hidden cursor-pointer hover:border-[var(--bionic-gold-primary)] transition-colors"
      onClick={onClick}
    >
      {/* Image */}
      <div className="h-40 bg-[var(--bionic-bg-hover)] relative">
        {images[0] ? (
          <img src={images[0]} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <MapPin className="w-10 h-10 text-[var(--bionic-text-muted)]" />
          </div>
        )}
        <PropertySourceBadge source={source} className="absolute top-2 left-2" />
        {bionic_score !== null && (
          <Badge 
            className={`absolute top-2 right-2 ${getScoreColor(bionic_score)} bg-black/70`}
          >
            <TrendingUp className="w-3 h-3 mr-1" />
            {bionic_score}
          </Badge>
        )}
      </div>

      <CardContent className="p-4">
        <h3 className="text-[var(--bionic-text-primary)] font-medium mb-2 line-clamp-2">
          {title}
        </h3>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1 text-[var(--bionic-gold-primary)]">
            <DollarSign className="w-4 h-4" />
            <span className="font-bold">{formatPrice(price)}</span>
          </div>
          <div className="flex items-center gap-1 text-[var(--bionic-text-muted)] text-sm">
            <Ruler className="w-4 h-4" />
            <span>{formatArea(area_m2)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PropertyCard;
