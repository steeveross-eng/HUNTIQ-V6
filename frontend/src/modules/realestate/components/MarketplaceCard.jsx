/**
 * MarketplaceCard - Marketplace listing card
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { 
  MapPin, Ruler, DollarSign, Heart, MessageSquare, User, Clock 
} from 'lucide-react';

/**
 * Marketplace Card Component
 * 
 * @param {Object} props
 * @param {Object} props.listing - Listing data
 * @param {Function} props.onClick - Click handler
 * @param {Function} props.onFavorite - Favorite toggle callback
 * @param {Function} props.onContact - Contact seller callback
 */
const MarketplaceCard = ({ 
  listing = {},
  onClick = null,
  onFavorite = null,
  onContact = null
}) => {
  const {
    title = 'Annonce',
    price = 0,
    area_m2 = 0,
    property_type = 'terrain',
    images = [],
    seller_name = 'Vendeur',
    created_at = null,
    is_favorite = false
  } = listing;

  const formatPrice = (price) => {
    if (price >= 1000000) return `${(price / 1000000).toFixed(1)}M$`;
    return `${(price / 1000).toFixed(0)}k$`;
  };

  const formatArea = (area) => {
    if (area >= 10000) return `${(area / 10000).toFixed(1)} ha`;
    return `${area.toLocaleString()} m²`;
  };

  const formatDate = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString('fr-CA');
  };

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
        
        {/* Favorite Button */}
        <Button
          variant="ghost"
          size="icon"
          className={`absolute top-2 right-2 bg-black/50 hover:bg-black/70 ${is_favorite ? 'text-red-500' : 'text-white'}`}
          onClick={(e) => { e.stopPropagation(); onFavorite?.(); }}
        >
          <Heart className="w-4 h-4" fill={is_favorite ? 'currentColor' : 'none'} />
        </Button>

        {/* Type Badge */}
        <Badge className="absolute top-2 left-2 bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">
          {property_type}
        </Badge>
      </div>

      <CardContent className="p-4">
        {/* Title */}
        <h3 className="text-[var(--bionic-text-primary)] font-medium mb-2 line-clamp-2">
          {title}
        </h3>
        
        {/* Price & Area */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1 text-[var(--bionic-gold-primary)]">
            <DollarSign className="w-4 h-4" />
            <span className="font-bold">{formatPrice(price)}</span>
          </div>
          <div className="flex items-center gap-1 text-[var(--bionic-text-muted)] text-sm">
            <Ruler className="w-4 h-4" />
            <span>{formatArea(area_m2)}</span>
          </div>
        </div>

        {/* Seller & Date */}
        <div className="flex items-center justify-between text-xs text-[var(--bionic-text-muted)] pt-3 border-t border-[var(--bionic-border-secondary)]">
          <span className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {seller_name}
          </span>
          {created_at && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDate(created_at)}
            </span>
          )}
        </div>

        {/* Contact Button */}
        <Button
          size="sm"
          className="w-full mt-3 bg-[var(--bionic-gold-primary)] text-black hover:bg-[var(--bionic-gold-secondary)]"
          onClick={(e) => { e.stopPropagation(); onContact?.(); }}
        >
          <MessageSquare className="w-4 h-4 mr-1" />
          Contacter
        </Button>
      </CardContent>
    </Card>
  );
};

export default MarketplaceCard;
