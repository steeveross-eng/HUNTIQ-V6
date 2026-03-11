// ShopPage.jsx - Page Magasin avec filtres avancés
// BIONIC™ Global Container Applied
import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import AdvancedFilters from "@/components/filters/AdvancedFilters";
import { useLanguage } from "@/contexts/LanguageContext";
import { GlobalContainer } from "@/core/layouts";
import {
  ShoppingCart,
  ExternalLink,
  Star,
  CloudRain,
  Shield,
  Droplet,
  Eye
} from "lucide-react";

// Sale Mode Badge
const SaleModeBadge = ({ mode }) => {
  const { t } = useLanguage();
  const config = {
    dropshipping: { label: t('admin_dropshipping'), color: "bg-blue-600" },
    affiliation: { label: t('common_partners'), color: "bg-purple-600" },
    hybrid: { label: t('admin_hybrid'), color: "bg-[#f5a623]" }
  };
  const { label, color } = config[mode] || config.dropshipping;
  return <Badge className={`${color} text-xs`}>{label}</Badge>;
};

// Product Card Component
const ProductCard = ({ product, onAddToCart, onAffiliateClick, t }) => {
  const pastilleColor = product.score >= 75 ? "bg-[#f5a623]" : 
                        product.score >= 50 ? "bg-yellow-500" : "bg-red-500";
  
  return (
    <Card className="bg-card border-border overflow-hidden group hover:border-[#f5a623]/50 transition-all duration-300 hover:shadow-lg hover:shadow-[#f5a623]/10">
      <div className="relative">
        {/* Product Image */}
        <div className="aspect-square overflow-hidden bg-black/20">
          <img 
            src={product.image_url} 
            alt={product.name} 
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        
        {/* Rank Badge */}
        <div className="absolute top-2 left-2 w-8 h-8 rounded-full bg-[#f5a623] text-black font-bold flex items-center justify-center text-sm">
          #{product.rank}
        </div>
        
        {/* Score Badge */}
        <div className={`absolute top-2 right-2 px-2 py-1 rounded-full ${pastilleColor} text-white font-bold text-xs`}>
          {product.score}/100
        </div>
        
        {/* Feature Badges */}
        <div className="absolute bottom-2 left-2 flex gap-1">
          {product.rainproof && (
            <Badge variant="outline" className="bg-black/60 border-cyan-400 text-cyan-400 text-xs">
              <CloudRain className="h-3 w-3" />
            </Badge>
          )}
          {product.has_pheromones && (
            <Badge variant="outline" className="bg-black/60 border-pink-400 text-pink-400 text-xs">
              <Droplet className="h-3 w-3" />
            </Badge>
          )}
          {product.certified_food && (
            <Badge variant="outline" className="bg-black/60 border-[#f5a623] text-[#f5a623] text-xs">
              <Shield className="h-3 w-3" />
            </Badge>
          )}
        </div>
      </div>
      
      <CardContent className="p-4 space-y-3">
        {/* Brand & Name */}
        <div>
          <p className="text-[#f5a623] text-xs font-medium">{product.brand}</p>
          <h3 className="text-white font-semibold text-sm leading-tight line-clamp-2 min-h-[2.5rem]">
            {product.name}
          </h3>
        </div>
        
        {/* Price & Sale Mode */}
        <div className="flex items-center justify-between">
          <span className="text-white font-bold text-lg">${product.price}</span>
          <SaleModeBadge mode={product.sale_mode} />
        </div>
        
        {/* Stats */}
        <div className="flex items-center gap-3 text-xs text-gray-300">
          <span className="flex items-center gap-1">
            <Eye className="h-3 w-3" />
            {product.views || 0}
          </span>
          <span className="flex items-center gap-1">
            <Star className="h-3 w-3" />
            {product.attraction_days || 7}j
          </span>
        </div>
        
        {/* CTA Button */}
        {product.sale_mode === "affiliation" && product.affiliate_link ? (
          <Button 
            className="w-full bg-purple-600 hover:bg-purple-700 text-white text-sm h-9"
            onClick={() => {
              if (onAffiliateClick) onAffiliateClick(product);
              window.open(product.affiliate_link, '_blank');
            }}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Voir chez partenaire
          </Button>
        ) : (
          <Button 
            className="w-full bg-[#f5a623] hover:bg-[#d4850e] text-black text-sm h-9"
            onClick={() => onAddToCart && onAddToCart(product)}
          >
            <ShoppingCart className="h-4 w-4 mr-2" />
            {t('shop_add_to_cart')}
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

// Main Shop Page Component
const ShopPage = ({ products = [], onAddToCart, onAffiliateClick }) => {
  const { t } = useLanguage();
  const [filters, setFilters] = useState({});
  
  // Apply filters to products
  const filteredProducts = useMemo(() => {
    let result = [...products];
    
    // Search filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(search) ||
        p.brand.toLowerCase().includes(search) ||
        p.description?.toLowerCase().includes(search)
      );
    }
    
    // Category filter
    if (filters.category && filters.category !== "all") {
      result = result.filter(p => p.product_format === filters.category || p.category === filters.category);
    }
    
    // Animal type filter
    if (filters.animal_type && filters.animal_type !== "all") {
      result = result.filter(p => 
        p.animal_type === filters.animal_type ||
        p.target_animals?.includes(filters.animal_type)
      );
    }
    
    // Season filter
    if (filters.season && filters.season !== "all") {
      result = result.filter(p => p.season === filters.season);
    }
    
    // Brand filter
    if (filters.brand && filters.brand !== "all") {
      result = result.filter(p => p.brand === filters.brand);
    }
    
    // Price range filter
    if (filters.min_price > 0) {
      result = result.filter(p => p.price >= filters.min_price);
    }
    if (filters.max_price && filters.max_price < 200) {
      result = result.filter(p => p.price <= filters.max_price);
    }
    
    // Score filter
    if (filters.min_score > 0) {
      result = result.filter(p => p.score >= filters.min_score);
    }
    
    // Feature filters
    if (filters.rainproof) {
      result = result.filter(p => p.rainproof);
    }
    if (filters.has_pheromones) {
      result = result.filter(p => p.has_pheromones);
    }
    if (filters.certified_food) {
      result = result.filter(p => p.certified_food);
    }
    
    // Sorting
    const sortField = filters.sort_by || "rank";
    const sortOrder = filters.sort_order || "asc";
    
    result.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      if (typeof aVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      
      if (sortOrder === "asc") {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
    
    return result;
  }, [products, filters]);

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="py-6 sm:py-8 pb-16">
        {/* Header */}
        <div className="mb-6">
          <h1 className="golden-text text-h1 font-bold mb-2">{t('shop_title')}</h1>
          <p className="text-gray-300 text-body">
            {t('shop_all_products')}
          </p>
        </div>
        
        {/* Filters */}
        <div className="mb-6">
          <AdvancedFilters 
            products={products}
            onFilterChange={setFilters}
          />
        </div>
        
        {/* Results Count */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-gray-300 text-sm">
            {filteredProducts.length} {t('common_products').toLowerCase()}
          </p>
        </div>
        
        {/* Products Grid */}
        {filteredProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
            {filteredProducts.map((product) => (
              <ProductCard 
                key={product.id} 
                product={product} 
                onAddToCart={onAddToCart}
                onAffiliateClick={onAffiliateClick}
                t={t}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
              <ShoppingCart className="h-8 w-8 text-gray-500" />
            </div>
            <h3 className="text-white font-semibold mb-2">{t('msg_no_results')}</h3>
            <p className="text-gray-300 text-sm">
              {t('shop_clear_filters')}
            </p>
          </div>
        )}
      </GlobalContainer>
    </main>
  );
};

export default ShopPage;
