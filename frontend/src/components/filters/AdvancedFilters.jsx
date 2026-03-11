// AdvancedFilters.jsx - Composant de filtres avancés pour Shop et Compare
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Slider } from "@/components/ui/slider";
import {
  Search,
  SlidersHorizontal,
  X,
  Filter,
  RotateCcw,
  Check,
  ChevronDown,
  Sparkles,
  DollarSign,
  Star,
  Tag,
  Droplet,
  Shield,
  CloudRain,
  Target,
  Calendar
} from "lucide-react";

// Configuration des catégories et options - IDs are translation keys
const CATEGORIES = [
  { id: "all", nameKey: "filter_all_categories" },
  { id: "urine", nameKey: "filter_urine" },
  { id: "gel", nameKey: "filter_gel" },
  { id: "granules", nameKey: "filter_granules" },
  { id: "bloc", nameKey: "filter_blocks" },
  { id: "liquide", nameKey: "filter_liquids" },
  { id: "poudre", nameKey: "filter_powders" },
  { id: "spray", nameKey: "filter_sprays" }
];

const ANIMALS = [
  { id: "all", nameKey: "filter_all_animals" },
  { id: "deer", nameKey: "filter_deer" },
  { id: "moose", nameKey: "filter_moose" },
  { id: "bear", nameKey: "filter_bear" },
  { id: "wild_boar", nameKey: "filter_wild_boar" },
  { id: "coyote", nameKey: "filter_coyote" },
  { id: "fox", nameKey: "filter_fox" }
];

const SEASONS = [
  { id: "all", nameKey: "filter_all_seasons" },
  { id: "pre_rut", nameKey: "filter_pre_rut" },
  { id: "rut", nameKey: "filter_rut" },
  { id: "post_rut", nameKey: "filter_post_rut" },
  { id: "spring", nameKey: "filter_spring" },
  { id: "summer", nameKey: "filter_summer" },
  { id: "fall", nameKey: "filter_fall" },
  { id: "winter", nameKey: "filter_winter" },
  { id: "year_round", nameKey: "filter_all_seasons" }
];

const SORT_OPTIONS = [
  { id: "rank_asc", nameKey: "sort_rank_best", field: "rank", order: "asc" },
  { id: "rank_desc", nameKey: "sort_rank_low", field: "rank", order: "desc" },
  { id: "score_desc", nameKey: "sort_score_high", field: "score", order: "desc" },
  { id: "score_asc", nameKey: "sort_score_low", field: "score", order: "asc" },
  { id: "price_asc", nameKey: "shop_sort_price_asc", field: "price", order: "asc" },
  { id: "price_desc", nameKey: "shop_sort_price_desc", field: "price", order: "desc" },
  { id: "name_asc", nameKey: "sort_name_az", field: "name", order: "asc" },
  { id: "name_desc", nameKey: "sort_name_za", field: "name", order: "desc" }
];

// Filter chip component
const FilterChip = ({ label, onRemove }) => (
  <Badge 
    variant="outline" 
    className="bg-[#f5a623]/10 border-[#f5a623]/30 text-[#f5a623] px-3 py-1 flex items-center gap-1 cursor-pointer hover:bg-[#f5a623]/20 transition-colors"
    onClick={onRemove}
  >
    {label}
    <X className="h-3 w-3 ml-1" />
  </Badge>
);

// Main AdvancedFilters component
const AdvancedFilters = ({ 
  onFilterChange, 
  products = [], 
  initialFilters = {},
  showSearch = true,
  compact = false 
}) => {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    category: "all",
    animal_type: "all",
    season: "all",
    brand: "all",
    min_price: 0,
    max_price: 200,
    min_score: 0,
    max_score: 100,
    rainproof: false,
    has_pheromones: false,
    certified_food: false,
    sort_by: "rank",
    sort_order: "asc",
    ...initialFilters
  });
  
  // Extract unique brands from products
  const brands = ["all", ...new Set(products.map(p => p.brand).filter(Boolean))];
  
  // Price range from products
  const prices = products.map(p => p.price).filter(Boolean);
  const minProductPrice = Math.min(...prices, 0);
  const maxProductPrice = Math.max(...prices, 200);
  
  // Count active filters
  const activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
    if (key === "search" && value) return true;
    if (key === "category" && value !== "all") return true;
    if (key === "animal_type" && value !== "all") return true;
    if (key === "season" && value !== "all") return true;
    if (key === "brand" && value !== "all") return true;
    if (key === "min_price" && value > 0) return true;
    if (key === "max_price" && value < 200) return true;
    if (key === "min_score" && value > 0) return true;
    if (key === "rainproof" && value) return true;
    if (key === "has_pheromones" && value) return true;
    if (key === "certified_food" && value) return true;
    return false;
  }).length;

  // Apply filters and notify parent
  const applyFilters = useCallback(() => {
    if (onFilterChange) {
      onFilterChange(filters);
    }
  }, [filters, onFilterChange]);

  // Auto-apply on filter change
  useEffect(() => {
    const debounce = setTimeout(() => {
      applyFilters();
    }, 300);
    return () => clearTimeout(debounce);
  }, [filters, applyFilters]);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      search: "",
      category: "all",
      animal_type: "all",
      season: "all",
      brand: "all",
      min_price: 0,
      max_price: 200,
      min_score: 0,
      max_score: 100,
      rainproof: false,
      has_pheromones: false,
      certified_food: false,
      sort_by: "rank",
      sort_order: "asc"
    });
  };

  const removeFilter = (key) => {
    const defaultValues = {
      search: "",
      category: "all",
      animal_type: "all",
      season: "all",
      brand: "all",
      min_price: 0,
      max_price: 200,
      min_score: 0,
      rainproof: false,
      has_pheromones: false,
      certified_food: false
    };
    updateFilter(key, defaultValues[key]);
  };

  // Get active filter labels
  const getActiveFilterLabels = () => {
    const labels = [];
    if (filters.search) labels.push({ key: "search", label: `"${filters.search}"` });
    if (filters.category !== "all") {
      const cat = CATEGORIES.find(c => c.id === filters.category);
      labels.push({ key: "category", label: cat?.name || filters.category });
    }
    if (filters.animal_type !== "all") {
      const animal = ANIMALS.find(a => a.id === filters.animal_type);
      labels.push({ key: "animal_type", label: animal?.name || filters.animal_type });
    }
    if (filters.season !== "all") {
      const season = SEASONS.find(s => s.id === filters.season);
      labels.push({ key: "season", label: season?.name || filters.season });
    }
    if (filters.brand !== "all") labels.push({ key: "brand", label: filters.brand });
    if (filters.min_price > 0) labels.push({ key: "min_price", label: `Min: $${filters.min_price}` });
    if (filters.max_price < 200) labels.push({ key: "max_price", label: `Max: $${filters.max_price}` });
    if (filters.min_score > 0) labels.push({ key: "min_score", label: `Score ≥${filters.min_score}` });
    if (filters.rainproof) labels.push({ key: "rainproof", label: "Rainproof" });
    if (filters.has_pheromones) labels.push({ key: "has_pheromones", label: "Phéromones" });
    if (filters.certified_food) labels.push({ key: "certified_food", label: "Certifié" });
    return labels;
  };

  return (
    <div className="space-y-4">
      {/* Search Bar and Filter Button Row */}
      <div className="flex flex-col sm:flex-row gap-3">
        {showSearch && (
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              value={filters.search}
              onChange={(e) => updateFilter("search", e.target.value)}
              placeholder="Rechercher un produit..."
              className="pl-10 bg-background border-border text-white h-11"
              data-testid="product-search-input"
            />
            {filters.search && (
              <button 
                onClick={() => updateFilter("search", "")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
        
        {/* Quick Sort */}
        <Select 
          value={`${filters.sort_by}_${filters.sort_order}`} 
          onValueChange={(value) => {
            const option = SORT_OPTIONS.find(o => o.id === value);
            if (option) {
              updateFilter("sort_by", option.field);
              updateFilter("sort_order", option.order);
            }
          }}
        >
          <SelectTrigger className="w-full sm:w-48 bg-background border-border h-11">
            <SelectValue placeholder="Trier par" />
          </SelectTrigger>
          <SelectContent>
            {SORT_OPTIONS.map(option => (
              <SelectItem key={option.id} value={option.id}>
                {option.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Filter Sheet Trigger */}
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Button 
              variant="outline" 
              className="relative h-11 px-4 border-border hover:bg-[#f5a623]/10 hover:border-[#f5a623]"
              data-testid="open-filters-btn"
            >
              <SlidersHorizontal className="h-4 w-4 mr-2" />
              Filtres
              {activeFiltersCount > 0 && (
                <Badge className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center bg-[#f5a623] text-black text-xs">
                  {activeFiltersCount}
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          
          <SheetContent className="bg-card border-border text-white w-full sm:max-w-md overflow-y-auto">
            <SheetHeader>
              <SheetTitle className="text-white flex items-center gap-2">
                <Filter className="h-5 w-5 text-[#f5a623]" />
                Filtres avancés
              </SheetTitle>
              <SheetDescription>
                Affinez votre recherche avec les filtres ci-dessous
              </SheetDescription>
            </SheetHeader>

            <div className="py-6 space-y-6">
              <Accordion type="multiple" defaultValue={["category", "price", "features"]} className="space-y-2">
                {/* Category Filter */}
                <AccordionItem value="category" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <Tag className="h-4 w-4 text-[#f5a623]" />
                      Catégorie
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="grid grid-cols-2 gap-2 pt-2">
                      {CATEGORIES.map(cat => (
                        <button
                          key={cat.id}
                          onClick={() => updateFilter("category", cat.id)}
                          className={`p-2 rounded-lg text-sm text-left transition-all ${
                            filters.category === cat.id
                              ? "bg-[#f5a623] text-black font-medium"
                              : "bg-background hover:bg-gray-800 text-gray-300"
                          }`}
                        >
                          {cat.icon} {cat.name}
                        </button>
                      ))}
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Animal Type Filter */}
                <AccordionItem value="animal" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-[#f5a623]" />
                      Animal ciblé
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="space-y-2 pt-2">
                      {ANIMALS.map(animal => (
                        <button
                          key={animal.id}
                          onClick={() => updateFilter("animal_type", animal.id)}
                          className={`w-full p-2 rounded-lg text-sm text-left transition-all ${
                            filters.animal_type === animal.id
                              ? "bg-[#f5a623] text-black font-medium"
                              : "bg-background hover:bg-gray-800 text-gray-300"
                          }`}
                        >
                          {animal.name}
                        </button>
                      ))}
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Season Filter */}
                <AccordionItem value="season" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-[#f5a623]" />
                      Saison
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="grid grid-cols-2 gap-2 pt-2">
                      {SEASONS.map(season => (
                        <button
                          key={season.id}
                          onClick={() => updateFilter("season", season.id)}
                          className={`p-2 rounded-lg text-sm text-left transition-all ${
                            filters.season === season.id
                              ? "bg-[#f5a623] text-black font-medium"
                              : "bg-background hover:bg-gray-800 text-gray-300"
                          }`}
                        >
                          {season.name}
                        </button>
                      ))}
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Brand Filter */}
                {brands.length > 2 && (
                  <AccordionItem value="brand" className="border-border">
                    <AccordionTrigger className="text-white hover:text-[#f5a623]">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-[#f5a623]" />
                        Marque
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <Select 
                        value={filters.brand} 
                        onValueChange={(value) => updateFilter("brand", value)}
                      >
                        <SelectTrigger className="w-full bg-background border-border mt-2">
                          <SelectValue placeholder="Toutes les marques" />
                        </SelectTrigger>
                        <SelectContent>
                          {brands.map(brand => (
                            <SelectItem key={brand} value={brand}>
                              {brand === "all" ? "Toutes les marques" : brand}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Price Range Filter */}
                <AccordionItem value="price" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-[#f5a623]" />
                      Prix
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="space-y-4 pt-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Min: ${filters.min_price}</span>
                        <span className="text-gray-400">Max: ${filters.max_price}</span>
                      </div>
                      <div className="flex gap-4">
                        <Input
                          type="number"
                          value={filters.min_price}
                          onChange={(e) => updateFilter("min_price", Number(e.target.value))}
                          className="bg-background border-border"
                          placeholder="Min"
                          min={0}
                        />
                        <Input
                          type="number"
                          value={filters.max_price}
                          onChange={(e) => updateFilter("max_price", Number(e.target.value))}
                          className="bg-background border-border"
                          placeholder="Max"
                          min={0}
                        />
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Score Filter */}
                <AccordionItem value="score" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-[#f5a623]" />
                      Score minimum
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="space-y-4 pt-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">Score ≥ {filters.min_score}</span>
                        <Badge className={`${
                          filters.min_score >= 75 ? "bg-[#f5a623]" :
                          filters.min_score >= 50 ? "bg-yellow-500" :
                          "bg-gray-500"
                        }`}>
                          {filters.min_score >= 75 ? "Excellent" :
                           filters.min_score >= 50 ? "Bon" : "Tous"}
                        </Badge>
                      </div>
                      <Slider
                        value={[filters.min_score]}
                        onValueChange={([value]) => updateFilter("min_score", value)}
                        max={100}
                        step={5}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>0</span>
                        <span>50</span>
                        <span>75</span>
                        <span>100</span>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>

                {/* Features Filter */}
                <AccordionItem value="features" className="border-border">
                  <AccordionTrigger className="text-white hover:text-[#f5a623]">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-[#f5a623]" />
                      Caractéristiques
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="space-y-3 pt-2">
                      <label className="flex items-center gap-3 p-2 rounded-lg bg-background hover:bg-gray-800 cursor-pointer transition-colors">
                        <Checkbox
                          checked={filters.rainproof}
                          onCheckedChange={(checked) => updateFilter("rainproof", checked)}
                        />
                        <div className="flex items-center gap-2">
                          <CloudRain className="h-4 w-4 text-cyan-400" />
                          <span>Rainproof (résistant à la pluie)</span>
                        </div>
                      </label>
                      
                      <label className="flex items-center gap-3 p-2 rounded-lg bg-background hover:bg-gray-800 cursor-pointer transition-colors">
                        <Checkbox
                          checked={filters.has_pheromones}
                          onCheckedChange={(checked) => updateFilter("has_pheromones", checked)}
                        />
                        <div className="flex items-center gap-2">
                          <Droplet className="h-4 w-4 text-pink-400" />
                          <span>Contient des phéromones</span>
                        </div>
                      </label>
                      
                      <label className="flex items-center gap-3 p-2 rounded-lg bg-background hover:bg-gray-800 cursor-pointer transition-colors">
                        <Checkbox
                          checked={filters.certified_food}
                          onCheckedChange={(checked) => updateFilter("certified_food", checked)}
                        />
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4 text-[#f5a623]" />
                          <span>Certification alimentaire</span>
                        </div>
                      </label>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>

            <SheetFooter className="flex gap-2 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={resetFilters}
                className="flex-1"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Réinitialiser
              </Button>
              <Button 
                onClick={() => setIsOpen(false)}
                className="flex-1 bg-[#f5a623] text-black hover:bg-[#d4850e]"
              >
                <Check className="h-4 w-4 mr-2" />
                Appliquer ({activeFiltersCount})
              </Button>
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>

      {/* Active Filters Display */}
      {getActiveFilterLabels().length > 0 && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-gray-400 text-sm">Filtres actifs:</span>
          {getActiveFilterLabels().map(({ key, label }) => (
            <FilterChip 
              key={key} 
              label={label} 
              onRemove={() => removeFilter(key)} 
            />
          ))}
          <button 
            onClick={resetFilters}
            className="text-gray-400 hover:text-[#f5a623] text-sm flex items-center gap-1 ml-2"
          >
            <RotateCcw className="h-3 w-3" />
            Tout effacer
          </button>
        </div>
      )}
    </div>
  );
};

export default AdvancedFilters;
