/**
 * ProductCard - Product display card component
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Package, ShoppingCart, Microscope, Scale } from 'lucide-react';

export const ProductCard = ({ 
  product, 
  onAddToCart,
  onAnalyze,
  onCompare,
  compact = false
}) => {
  if (!product) return null;

  const getScoreColor = (score) => {
    if (score >= 8) return '#10b981';
    if (score >= 6) return '#22c55e';
    if (score >= 4) return '#f59e0b';
    return '#ef4444';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-slate-800 rounded-lg p-3 border border-slate-700">
        {product.image_url && (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-12 h-12 object-cover rounded"
          />
        )}
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium truncate">{product.name}</p>
          <p className="text-[#f5a623] text-sm font-bold">${product.price}</p>
        </div>
        <Badge style={{ backgroundColor: `${getScoreColor(product.score)}20`, color: getScoreColor(product.score) }}>
          {product.score}
        </Badge>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden hover:border-[#f5a623]/50 transition-all">
      {/* Image */}
      <div className="relative">
        {product.rank && (
          <div className="absolute top-3 left-3 z-10">
            <Badge className="bg-[#f5a623] text-black font-bold px-3 py-1">
              #{product.rank}
            </Badge>
          </div>
        )}
        {product.image_url ? (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-full aspect-square object-cover"
          />
        ) : (
          <div className="w-full aspect-square bg-slate-700 flex items-center justify-center">
            <Package className="w-12 h-12 text-slate-500" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Brand & Name */}
        <div>
          {product.brand && (
            <p className="text-[#f5a623] text-sm">{product.brand}</p>
          )}
          <h3 className="text-white font-semibold truncate">{product.name}</h3>
        </div>

        {/* Score & Category */}
        <div className="flex items-center gap-2 flex-wrap">
          <Badge 
            className="font-bold"
            style={{ backgroundColor: `${getScoreColor(product.score)}20`, color: getScoreColor(product.score) }}
          >
            Score: {product.score}/10
          </Badge>
          {product.category && (
            <Badge className="bg-slate-700 text-slate-300">
              {product.category}
            </Badge>
          )}
        </div>

        {/* Price */}
        <p className="text-[#f5a623] font-bold text-xl">${product.price}</p>

        {/* Actions */}
        <div className="flex gap-2">
          {onAddToCart && (
            <Button 
              className="flex-1 bg-[#f5a623] hover:bg-[#d4890e] text-black font-semibold"
              onClick={() => onAddToCart(product)}
            >
              <ShoppingCart className="w-4 h-4 mr-1" /> Ajouter
            </Button>
          )}
          {onAnalyze && (
            <Button 
              variant="outline" 
              size="icon"
              className="border-slate-600"
              onClick={() => onAnalyze(product)}
            >
              <Microscope className="w-4 h-4" />
            </Button>
          )}
          {onCompare && (
            <Button 
              variant="outline" 
              size="icon"
              className="border-slate-600"
              onClick={() => onCompare(product)}
            >
              <Scale className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
