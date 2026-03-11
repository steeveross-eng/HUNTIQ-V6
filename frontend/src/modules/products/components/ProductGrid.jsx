/**
 * ProductGrid - Grid display for products
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { ProductCard } from './ProductCard';
import { Package } from 'lucide-react';

export const ProductGrid = ({ 
  products = [], 
  onAddToCart,
  onAnalyze,
  onCompare,
  columns = 4,
  loading = false,
  emptyMessage = 'Aucun produit disponible'
}) => {
  if (loading) {
    return (
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-${columns} gap-6`}>
        {[...Array(columns * 2)].map((_, i) => (
          <div key={i} className="animate-pulse bg-slate-800 rounded-xl">
            <div className="aspect-square bg-slate-700 rounded-t-xl" />
            <div className="p-4 space-y-3">
              <div className="h-4 bg-slate-700 rounded w-3/4" />
              <div className="h-3 bg-slate-700 rounded w-1/2" />
              <div className="h-6 bg-slate-700 rounded w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!products.length) {
    return (
      <div className="text-center py-12">
        <Package className="w-16 h-16 text-slate-500 mx-auto" />
        <p className="text-slate-400 mt-4">{emptyMessage}</p>
      </div>
    );
  }

  const gridCols = {
    2: 'sm:grid-cols-2',
    3: 'sm:grid-cols-2 lg:grid-cols-3',
    4: 'sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    5: 'sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5'
  };

  return (
    <div className={`grid grid-cols-1 ${gridCols[columns] || gridCols[4]} gap-6`}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
          onAnalyze={onAnalyze}
          onCompare={onCompare}
        />
      ))}
    </div>
  );
};

export default ProductGrid;
