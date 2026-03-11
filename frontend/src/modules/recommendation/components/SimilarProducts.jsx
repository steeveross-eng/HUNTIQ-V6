/**
 * SimilarProducts - Display similar/complementary products
 * Phase 10 - Plan Maître Modules
 * BIONIC Design System compliant - No emojis
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { RecommendationService } from '../RecommendationService';
import { RefreshCw, ShoppingCart } from 'lucide-react';

export const SimilarProducts = ({ 
  productId,
  productName = 'Produit',
  type = 'similar', // 'similar' or 'complementary'
  limit = 4,
  onSelect
}) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadProducts = useCallback(async () => {
    if (!productId) return;
    
    setLoading(true);
    try {
      const result = type === 'similar' 
        ? await RecommendationService.getSimilarProducts(productId, limit)
        : await RecommendationService.getComplementaryProducts(productId, limit);
      
      if (result.success) {
        setProducts(result.similar_products || result.complementary_products || []);
      } else {
        // Placeholder
        setProducts([
          { id: 1, name: 'Produit similaire 1', score: 85, similarity: 0.92 },
          { id: 2, name: 'Produit similaire 2', score: 78, similarity: 0.85 },
          { id: 3, name: 'Produit similaire 3', score: 72, similarity: 0.78 }
        ]);
      }
    } catch (error) {
      console.error('Load products error:', error);
    } finally {
      setLoading(false);
    }
  }, [productId, type, limit]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const title = type === 'similar' ? 'Produits similaires' : 'Souvent achetés ensemble';
  const IconComponent = type === 'similar' ? RefreshCw : ShoppingCart;

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm text-white flex items-center gap-2">
          <IconComponent className="w-4 h-4 text-slate-400" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="animate-pulse space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-12 bg-slate-700 rounded" />
            ))}
          </div>
        ) : products.length > 0 ? (
          <div className="space-y-2">
            {products.map((product, index) => (
              <div 
                key={product.id || index}
                className="flex items-center gap-2 p-2 bg-slate-700/50 rounded hover:bg-slate-600/50 cursor-pointer"
                onClick={() => onSelect?.(product)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm truncate">{product.name}</p>
                </div>
                {product.similarity && (
                  <Badge className="bg-blue-900/50 text-blue-400 text-xs">
                    {Math.round(product.similarity * 100)}%
                  </Badge>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-sm text-center py-4">
            Aucune recommandation
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default SimilarProducts;
