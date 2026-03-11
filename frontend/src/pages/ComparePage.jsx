// ComparePage.jsx - Page de comparaison avec filtres avancés
// BIONIC™ Global Container Applied
import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import AdvancedFilters from "@/components/filters/AdvancedFilters";
import { GlobalContainer } from "@/core/layouts";
import {
  GitCompare,
  Check,
  X,
  Plus,
  Minus,
  ShoppingCart,
  Star,
  CloudRain,
  Shield,
  Droplet,
  Clock,
  DollarSign,
  Award,
  ExternalLink,
  Trash2
} from "lucide-react";

// Sale Mode Badge
const SaleModeBadge = ({ mode }) => {
  const config = {
    dropshipping: { label: "Direct", color: "bg-blue-600" },
    affiliation: { label: "Partenaire", color: "bg-purple-600" },
    hybrid: { label: "Mixte", color: "bg-[#f5a623]" }
  };
  const { label, color } = config[mode] || config.dropshipping;
  return <Badge className={`${color} text-xs`}>{label}</Badge>;
};

// Comparison criteria
const COMPARISON_CRITERIA = [
  { id: "price", label: "Prix", icon: DollarSign, format: (v) => `$${v}`, better: "lower" },
  { id: "score", label: "Score", icon: Star, format: (v) => `${v}/100`, better: "higher" },
  { id: "attraction_days", label: "Durée d'attraction", icon: Clock, format: (v) => `${v} jours`, better: "higher" },
  { id: "rainproof", label: "Rainproof", icon: CloudRain, format: (v) => v ? "Oui" : "Non", better: "true" },
  { id: "has_pheromones", label: "Phéromones", icon: Droplet, format: (v) => v ? "Oui" : "Non", better: "true" },
  { id: "certified_food", label: "Certifié", icon: Shield, format: (v) => v ? "Oui" : "Non", better: "true" },
  { id: "ingredients_natural", label: "Ingrédients naturels", icon: Award, format: (v) => v ? "Oui" : "Non", better: "true" }
];

// Get best value for a criterion
const getBestValue = (products, criterionId, better) => {
  if (products.length === 0) return null;
  
  const values = products.map(p => p[criterionId]);
  
  if (better === "higher") {
    return Math.max(...values.filter(v => typeof v === "number"));
  } else if (better === "lower") {
    return Math.min(...values.filter(v => typeof v === "number"));
  } else if (better === "true") {
    return values.some(v => v === true);
  }
  return null;
};

// Check if value is best
const isBestValue = (value, bestValue, better) => {
  if (better === "higher" || better === "lower") {
    return value === bestValue;
  } else if (better === "true") {
    return value === true;
  }
  return false;
};

// Product Selection Card
const ProductSelectCard = ({ product, isSelected, onToggle }) => {
  const pastilleColor = product.score >= 75 ? "bg-[#f5a623]" : 
                        product.score >= 50 ? "bg-yellow-500" : "bg-red-500";
  
  return (
    <button
      onClick={() => onToggle(product)}
      className={`relative p-3 rounded-xl border transition-all text-left ${
        isSelected 
          ? "border-[#f5a623] bg-[#f5a623]/10 shadow-lg shadow-[#f5a623]/20" 
          : "border-border hover:border-gray-600 bg-card"
      }`}
    >
      {/* Selection indicator */}
      <div className={`absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center transition-all ${
        isSelected ? "bg-[#f5a623] text-black" : "bg-gray-700 text-gray-400"
      }`}>
        {isSelected ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
      </div>
      
      {/* Product Image */}
      <div className="aspect-square w-full rounded-lg overflow-hidden mb-2 bg-black/20">
        <img 
          src={product.image_url} 
          alt={product.name}
          className="w-full h-full object-cover"
        />
      </div>
      
      {/* Product Info */}
      <p className="text-[#f5a623] text-xs">{product.brand}</p>
      <p className="text-white text-sm font-medium truncate">{product.name}</p>
      <div className="flex items-center justify-between mt-1">
        <span className="text-white font-bold">${product.price}</span>
        <Badge className={`${pastilleColor} text-xs`}>{product.score}</Badge>
      </div>
    </button>
  );
};

// Comparison Table Component
const ComparisonTable = ({ selectedProducts, onRemove }) => {
  if (selectedProducts.length === 0) return null;
  
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border">
              <TableHead className="text-gray-400 w-48">Critère</TableHead>
              {selectedProducts.map((product, index) => (
                <TableHead key={product.id} className="text-center min-w-[200px]">
                  <div className="space-y-2 py-2">
                    <div className="relative">
                      <img 
                        src={product.image_url} 
                        alt={product.name}
                        className={`w-20 h-20 object-cover rounded-lg mx-auto ${
                          index === 0 ? "ring-2 ring-[#f5a623]" : ""
                        }`}
                      />
                      <button
                        onClick={() => onRemove(product)}
                        className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                    <p className="text-[#f5a623] text-xs">{product.brand}</p>
                    <p className="text-white font-semibold text-sm">{product.name}</p>
                    <SaleModeBadge mode={product.sale_mode} />
                  </div>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {COMPARISON_CRITERIA.map((criterion) => {
              const bestValue = getBestValue(selectedProducts, criterion.id, criterion.better);
              
              return (
                <TableRow key={criterion.id} className="border-border">
                  <TableCell className="font-medium text-gray-300">
                    <div className="flex items-center gap-2">
                      <criterion.icon className="h-4 w-4 text-[#f5a623]" />
                      {criterion.label}
                    </div>
                  </TableCell>
                  {selectedProducts.map((product) => {
                    const value = product[criterion.id];
                    const isBest = isBestValue(value, bestValue, criterion.better);
                    
                    return (
                      <TableCell 
                        key={product.id} 
                        className={`text-center ${
                          isBest ? "bg-[#f5a623]/10 text-[#f5a623] font-bold" : "text-gray-300"
                        }`}
                      >
                        <div className="flex items-center justify-center gap-1">
                          {criterion.format(value)}
                          {isBest && <Award className="h-4 w-4 text-[#f5a623]" />}
                        </div>
                      </TableCell>
                    );
                  })}
                </TableRow>
              );
            })}
            
            {/* Action Row */}
            <TableRow className="border-border bg-black/20">
              <TableCell className="font-medium text-gray-300">Action</TableCell>
              {selectedProducts.map((product) => (
                <TableCell key={product.id} className="text-center">
                  {product.sale_mode === "affiliation" && product.affiliate_link ? (
                    <Button 
                      size="sm"
                      className="bg-purple-600 hover:bg-purple-700"
                      onClick={() => window.open(product.affiliate_link, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      Partenaire
                    </Button>
                  ) : (
                    <Button 
                      size="sm"
                      className="bg-[#f5a623] hover:bg-[#d4850e] text-black"
                    >
                      <ShoppingCart className="h-4 w-4 mr-1" />
                      Commander
                    </Button>
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

// Main Compare Page Component
const ComparePage = ({ products = [] }) => {
  const [filters, setFilters] = useState({});
  const [selectedProducts, setSelectedProducts] = useState([]);
  const MAX_COMPARE = 4;
  
  // Apply filters to products
  const filteredProducts = useMemo(() => {
    let result = [...products];
    
    // Search filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(search) ||
        p.brand.toLowerCase().includes(search)
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

  const toggleProduct = (product) => {
    if (selectedProducts.find(p => p.id === product.id)) {
      setSelectedProducts(selectedProducts.filter(p => p.id !== product.id));
    } else if (selectedProducts.length < MAX_COMPARE) {
      setSelectedProducts([...selectedProducts, product]);
    }
  };

  const removeProduct = (product) => {
    setSelectedProducts(selectedProducts.filter(p => p.id !== product.id));
  };

  const clearAll = () => {
    setSelectedProducts([]);
  };

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="py-6 sm:py-8 pb-16">
        {/* Header */}
        <div className="mb-6">
          <h1 className="golden-text text-h1 font-bold mb-2">Comparez</h1>
          <p className="text-gray-400 text-body">
            Sélectionnez jusqu'à {MAX_COMPARE} produits pour les comparer côte à côte.
          </p>
        </div>
        
        {/* Comparison Table (if products selected) */}
        {selectedProducts.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-white font-semibold flex items-center gap-2">
                <GitCompare className="h-5 w-5 text-[#f5a623]" />
                Comparaison ({selectedProducts.length}/{MAX_COMPARE})
              </h2>
              <Button variant="outline" size="sm" onClick={clearAll}>
                <Trash2 className="h-4 w-4 mr-2" />
                Tout effacer
              </Button>
            </div>
            <ComparisonTable 
              selectedProducts={selectedProducts} 
              onRemove={removeProduct}
            />
          </div>
        )}
        
        {/* Filters */}
        <div className="mb-6">
          <AdvancedFilters 
            products={products}
            onFilterChange={setFilters}
          />
        </div>
        
        {/* Selection hint */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-gray-400 text-sm">
            {filteredProducts.length} produit{filteredProducts.length > 1 ? "s" : ""} disponible{filteredProducts.length > 1 ? "s" : ""}
            {selectedProducts.length > 0 && (
              <span className="text-[#f5a623] ml-2">
                • {selectedProducts.length} sélectionné{selectedProducts.length > 1 ? "s" : ""}
              </span>
            )}
          </p>
          {selectedProducts.length >= MAX_COMPARE && (
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
              Maximum atteint
            </Badge>
          )}
        </div>
        
        {/* Products Grid */}
        {filteredProducts.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
            {filteredProducts.map((product) => (
              <ProductSelectCard 
                key={product.id}
                product={product}
                isSelected={selectedProducts.some(p => p.id === product.id)}
                onToggle={toggleProduct}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
              <GitCompare className="h-8 w-8 text-gray-500" />
            </div>
            <h3 className="text-white font-semibold mb-2">Aucun produit trouvé</h3>
            <p className="text-gray-400 text-sm">
              Essayez de modifier vos filtres pour trouver des produits à comparer.
            </p>
          </div>
        )}
      </GlobalContainer>
    </main>
  );
};

export default ComparePage;
