// TerritoryAnalysisModule.jsx - Module d'analyse de territoire avec IA
// BIONIC Design System compliant
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Target,
  Map,
  Camera,
  Crosshair,
  Eye,
  FileText,
  Sparkles,
  ChevronRight,
  MapPin,
  Droplet,
  TreePine,
  Mountain,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Download,
  Plus,
  Settings,
  Wifi,
  WifiOff,
  Sun,
  Moon,
  Sunrise,
  Sunset,
  BarChart3,
  Layers,
  Navigation,
  CircleDot,
  Shirt,
  Binoculars,
  Building,
  Users,
  Car,
  ThumbsUp,
  Info,
  Tent,
  Flag,
  Leaf,
  TrendingUp,
  Brain
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================
// ANALYSIS CATEGORIES DATA - BIONIC Design System
// ============================================

const ANALYSIS_CATEGORIES = {
  produits: {
    name: "Produits de chasse",
    Icon: Target,
    description: "Analysez et comparez les produits de chasse",
    color: "from-[#f5a623] to-[#d4850e]",
    subcategories: [
      { id: "attractants", name: "Attractants & Leurres", Icon: Droplet, description: "Urines, gels, blocs, appâts" },
      { id: "cameras", name: "Caméras de chasse", Icon: Camera, description: "Trail cameras, détection" },
      { id: "equipement", name: "Équipement", Icon: Shirt, description: "Bottes, vêtements" },
      { id: "optiques", name: "Optiques & Viseurs", Icon: Binoculars, description: "Jumelles, lunettes" },
      { id: "appels", name: "Appels & Sons", Icon: CircleDot, description: "Appels originaux" }
    ]
  },
  territoire: {
    name: "Analyse de territoire",
    Icon: Map,
    description: "Analysez votre territoire avec l'IA",
    color: "from-blue-600 to-blue-800",
    subcategories: [
      { id: "cartographie", name: "Cartographie IA", Icon: MapPin, description: "Zones de probabilité" },
      { id: "cameras_territoire", name: "Réseau de caméras", Icon: Camera, description: "Connectez vos caméras" },
      { id: "evenements", name: "Événements", Icon: Eye, description: "Observations, tirs" },
      { id: "plan_action", name: "Plan d'action", Icon: FileText, description: "Plan personnalisé" }
    ]
  },
  especes: {
    name: "Espèces cibles",
    Icon: CircleDot,
    description: "Analyse par espèce",
    color: "from-purple-600 to-purple-800",
    subcategories: [
      { id: "orignal", name: "Orignal", Icon: CircleDot, color: "#8B4513", description: "Proximité eau, forêt mature" },
      { id: "chevreuil", name: "Chevreuil", Icon: CircleDot, color: "#D2691E", description: "Lisières, friches" },
      { id: "ours", name: "Ours noir", Icon: CircleDot, color: "#2F4F4F", description: "Zones isolées, nourriture" }
    ]
  }
};

const TIME_PERIODS = [
  { id: "tous", name: "Toute la journée", Icon: Clock },
  { id: "matin", name: "Matin (5h-10h)", Icon: Sunrise },
  { id: "jour", name: "Jour (10h-16h)", Icon: Sun },
  { id: "soir", name: "Soir (16h-21h)", Icon: Sunset },
  { id: "nuit", name: "Nuit (21h-5h)", Icon: Moon }
];

const SPECIES_INFO = {
  orignal: {
    name: "Orignal",
    Icon: CircleDot,
    color: "#8B4513",
    bgClass: "bg-amber-600",
    rules: [
      "Proximité eau (< 300m optimal)",
      "Forêt mature ou mixte",
      "Pentes douces, vallons",
      "Éloignement des chemins sous pression"
    ],
    attractants: ["Saline BIONIC™", "Urine femelle", "Appel"]
  },
  chevreuil: {
    name: "Chevreuil",
    Icon: CircleDot,
    color: "#D2691E",
    bgClass: "bg-orange-600",
    rules: [
      "Lisières (< 150m)",
      "Friches et régénération",
      "Coupes récentes",
      "Distance chemins 200-600m"
    ],
    attractants: ["Maïs", "Pommes", "Urine doe", "Sel BIONIC™"]
  },
  ours: {
    name: "Ours noir",
    Icon: CircleDot,
    color: "#2F4F4F",
    bgClass: "bg-gray-700",
    rules: [
      "Zones à baies/fruits",
      "Éloignement humain (> 500m)",
      "Proximité eau (< 500m)",
      "Coupes et friches"
    ],
    attractants: ["Appât sucré BIONIC™", "Miel", "Bacon", "Poisson"]
  }
};

// ============================================
// CATEGORY CARD COMPONENT - BIONIC Design System
// ============================================

const CategoryCard = ({ category, categoryKey, onSelect, isSelected }) => {
  const CategoryIcon = category.Icon || Target;
  return (
    <Card 
      className={`cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
        isSelected 
          ? "border-[#f5a623] bg-[#f5a623]/10 shadow-lg shadow-[#f5a623]/20" 
          : "border-border hover:border-[#f5a623]/50"
      }`}
      onClick={() => onSelect(categoryKey)}
    >
      <CardContent className="p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${category.color} flex items-center justify-center`}>
            <CategoryIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-white font-semibold">{category.name}</h3>
            <p className="text-gray-400 text-sm">{category.description}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-1">
          {category.subcategories.slice(0, 3).map(sub => {
            const SubIcon = sub.Icon || Target;
            return (
              <Badge key={sub.id} variant="outline" className="text-xs flex items-center gap-1">
                <SubIcon className="h-3 w-3" style={{ color: sub.color || '#f5a623' }} /> {sub.name}
              </Badge>
            );
          })}
          {category.subcategories.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{category.subcategories.length - 3}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// SPECIES SELECTOR COMPONENT - BIONIC Design System
// ============================================

const SpeciesSelector = ({ selectedSpecies, onSelect }) => (
  <div className="grid grid-cols-3 gap-3">
    {Object.entries(SPECIES_INFO).map(([key, species]) => {
      const SpeciesIcon = species.Icon || CircleDot;
      return (
        <button
          key={key}
          onClick={() => onSelect(key)}
          className={`p-4 rounded-xl border-2 transition-all duration-300 ${
            selectedSpecies === key
              ? "border-[#f5a623] bg-[#f5a623]/10 scale-105"
              : "border-border hover:border-[#f5a623]/50 hover:bg-white/5"
          }`}
        >
          <SpeciesIcon className="h-10 w-10 mx-auto mb-2" style={{ color: species.color || '#f5a623' }} />
          <p className="text-white font-semibold text-sm">{species.name}</p>
          <Badge className={`${species.bgClass} mt-2 text-xs`}>
            {selectedSpecies === key ? "Sélectionné" : "Choisir"}
          </Badge>
        </button>
      );
    })}
  </div>
);

// ============================================
// PROBABILITY RESULT CARD
// ============================================

const ProbabilityResultCard = ({ result }) => {
  if (!result) return null;
  
  const probColor = result.probability >= 0.7 ? "text-[#f5a623]" :
                    result.probability >= 0.5 ? "text-yellow-400" : "text-red-400";
  
  return (
    <Card className="bg-gradient-to-br from-black/80 to-gray-900/80 border-[#f5a623]/30">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-white font-semibold flex items-center gap-2">
              <Target className="h-5 w-5 text-[#f5a623]" />
              Probabilité de présence
            </h3>
            <p className="text-gray-400 text-sm">{result.species_name}</p>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${probColor}`}>
              {result.probability_percent}%
            </p>
            <Badge className={result.confidence === "high" ? "bg-[#f5a623]" : "bg-yellow-600"}>
              Confiance {result.confidence === "high" ? "élevée" : "moyenne"}
            </Badge>
          </div>
        </div>
        
        <Progress value={result.probability_percent} className="h-3 mb-4" />
        
        {/* Factors */}
        <div className="space-y-2 mb-4">
          <p className="text-gray-400 text-sm font-medium">Facteurs analysés:</p>
          {result.factors?.map((factor, i) => (
            <div key={i} className="flex items-center justify-between text-sm bg-black/30 p-2 rounded">
              <span className="text-gray-300">{factor.name}</span>
              <span className={factor.impact >= 1 ? "text-[#f5a623]" : "text-red-400"}>
                {factor.impact >= 1 ? "+" : ""}{Math.round((factor.impact - 1) * 100)}%
              </span>
            </div>
          ))}
        </div>
        
        {/* Recommendations */}
        {result.recommendations?.length > 0 && (
          <div className="space-y-2">
            <p className="text-gray-400 text-sm font-medium">Recommandations:</p>
            {result.recommendations.map((rec, i) => (
              <div key={i} className={`p-2 rounded text-sm flex items-start gap-2 ${
                rec.priority === "high" ? "bg-[#f5a623]/20 text-[#f5a623]" : "bg-blue-500/20 text-blue-300"
              }`}>
                <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>{rec.text}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ============================================
// ACTION PLAN CARD
// ============================================

const ActionPlanCard = ({ plan }) => {
  if (!plan) return null;
  
  const speciesInfo = SPECIES_INFO[plan.species_target] || {};
  
  return (
    <Card className="bg-gradient-to-br from-black/80 to-gray-900/80 border-[#f5a623]/30">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <FileText className="h-5 w-5 text-[#f5a623]" />
          Plan d'action - {speciesInfo.name}
        </CardTitle>
        <CardDescription>
          Généré le {new Date(plan.generated_at).toLocaleDateString('fr-CA')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-black/30 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-[#f5a623]">
              {plan.probability_summary?.high_prob_area_percent || 0}%
            </p>
            <p className="text-gray-400 text-xs">Zone haute probabilité</p>
          </div>
          <div className="bg-black/30 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-white">
              {plan.camera_placements?.length || 0}
            </p>
            <p className="text-gray-400 text-xs">Caméras suggérées</p>
          </div>
          <div className="bg-black/30 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-white">
              {plan.attractant_placements?.length || 0}
            </p>
            <p className="text-gray-400 text-xs">Attractants</p>
          </div>
        </div>
        
        {/* Recommendations */}
        <Accordion type="single" collapsible className="space-y-2">
          <AccordionItem value="cameras" className="border-border">
            <AccordionTrigger className="text-white hover:text-[#f5a623]">
              <div className="flex items-center gap-2">
                <Camera className="h-4 w-4 text-[#f5a623]" />
                Placements caméras ({plan.camera_placements?.length || 0})
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                {plan.camera_placements?.map((cam, i) => (
                  <div key={i} className="bg-black/30 p-3 rounded flex justify-between items-center">
                    <div>
                      <p className="text-white text-sm font-medium">Emplacement #{i + 1}</p>
                      <p className="text-gray-400 text-xs">
                        Orientation: {cam.orientation} | Probabilité: {Math.round(cam.probability * 100)}%
                      </p>
                    </div>
                    <Badge className={cam.priority === "high" ? "bg-[#f5a623]" : "bg-blue-600"}>
                      {cam.priority === "high" ? "Prioritaire" : "Secondaire"}
                    </Badge>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
          
          <AccordionItem value="attractants" className="border-border">
            <AccordionTrigger className="text-white hover:text-[#f5a623]">
              <div className="flex items-center gap-2">
                <Droplet className="h-4 w-4 text-[#f5a623]" />
                Attractants recommandés ({plan.attractant_placements?.length || 0})
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                {plan.attractant_placements?.map((attr, i) => (
                  <div key={i} className="bg-black/30 p-3 rounded">
                    <div className="flex justify-between items-center">
                      <p className="text-white text-sm font-medium">{attr.product_bionic}</p>
                      <Badge variant="outline" className="text-[#f5a623] border-[#f5a623]">
                        {attr.estimated_cost}
                      </Badge>
                    </div>
                    <p className="text-gray-400 text-xs mt-1">
                      Quantité: {attr.quantity}
                    </p>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
          
          <AccordionItem value="caches" className="border-border">
            <AccordionTrigger className="text-white hover:text-[#f5a623]">
              <div className="flex items-center gap-2">
                <TreePine className="h-4 w-4 text-[#f5a623]" />
                Caches recommandées ({plan.cache_recommendations?.length || 0})
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                {plan.cache_recommendations?.map((cache, i) => (
                  <div key={i} className="bg-black/30 p-3 rounded">
                    <p className="text-white text-sm font-medium">
                      Cache {cache.type} {cache.height_m > 0 && `(${cache.height_m}m)`}
                    </p>
                    <p className="text-gray-400 text-xs mt-1">
                      Visibilité: {cache.visibility_rating} | {cache.wind_consideration}
                    </p>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
        
        {/* General Tips */}
        <div className="bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-lg p-4">
          <h4 className="text-[#f5a623] font-semibold mb-2 flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Conseils BIONIC™
          </h4>
          <ul className="space-y-1 text-sm text-gray-300">
            {plan.recommendations?.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <ChevronRight className="h-4 w-4 text-[#f5a623] mt-0.5 flex-shrink-0" />
                <span>{rec.text}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// MAIN TERRITORY ANALYSIS MODULE
// ============================================

const TerritoryAnalysisModule = () => {
  const [activeCategory, setActiveCategory] = useState(null);
  const [selectedSpecies, setSelectedSpecies] = useState("chevreuil");
  const [selectedPeriod, setSelectedPeriod] = useState("tous");
  const [loading, setLoading] = useState(false);
  const [probabilityResult, setProbabilityResult] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  const [locationInput, setLocationInput] = useState({ lat: 46.8, lng: -71.2 });
  
  // Test probability calculation
  const calculateProbability = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/territory/probability`, {
        species: selectedSpecies,
        location: locationInput,
        time_period: selectedPeriod,
        terrain_data: {
          water_distance: Math.random() * 500,
          road_distance: 200 + Math.random() * 400,
          hunting_pressure: Math.random() * 0.6
        }
      });
      setProbabilityResult(response.data);
      toast.success("Analyse de probabilité terminée!");
    } catch (error) {
      toast.error("Erreur lors de l'analyse");
      console.error(error);
    }
    setLoading(false);
  };
  
  // Generate action plan
  const generateActionPlan = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/territory/action-plan`, {
        species_target: selectedSpecies,
        zone_center: locationInput,
        zone_radius_km: 5.0,
        time_period: selectedPeriod
      });
      setActionPlan(response.data.plan);
      toast.success("Plan d'action généré!");
    } catch (error) {
      toast.error("Erreur lors de la génération");
      console.error(error);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header with guidance */}
      <div className="bg-gradient-to-r from-[#f5a623]/20 to-blue-600/20 rounded-xl p-6 border border-[#f5a623]/30">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-[#f5a623]" />
          Que souhaitez-vous analyser?
        </h2>
        <p className="text-gray-300">
          Sélectionnez une catégorie pour commencer votre analyse guidée par SCENT SCIENCE™
        </p>
      </div>
      
      {/* Category Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(ANALYSIS_CATEGORIES).map(([key, category]) => (
          <CategoryCard
            key={key}
            category={category}
            categoryKey={key}
            onSelect={setActiveCategory}
            isSelected={activeCategory === key}
          />
        ))}
      </div>
      
      {/* Active Category Content */}
      {activeCategory && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <span className="text-2xl">{ANALYSIS_CATEGORIES[activeCategory].icon}</span>
              {ANALYSIS_CATEGORIES[activeCategory].name}
            </CardTitle>
            <CardDescription>
              Sélectionnez une sous-catégorie pour continuer
            </CardDescription>
          </CardHeader>
          <CardContent>
            {activeCategory === "produits" && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {ANALYSIS_CATEGORIES.produits.subcategories.map(sub => (
                  <Button
                    key={sub.id}
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center gap-2 hover:border-[#f5a623] hover:bg-[#f5a623]/10"
                    onClick={() => {
                      if (sub.id === "attractants") {
                        window.location.href = "/shop";
                      } else if (sub.id === "cameras") {
                        setActiveCategory("territoire");
                      }
                    }}
                  >
                    <span className="text-2xl">{sub.icon}</span>
                    <span className="text-sm text-center">{sub.name}</span>
                  </Button>
                ))}
              </div>
            )}
            
            {activeCategory === "especes" && (
              <div className="space-y-6">
                <SpeciesSelector 
                  selectedSpecies={selectedSpecies} 
                  onSelect={setSelectedSpecies} 
                />
                
                {/* Species Rules Display */}
                <div className="bg-black/30 rounded-lg p-4">
                  <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4 text-[#f5a623]" />
                    Règles métier - {SPECIES_INFO[selectedSpecies]?.name}
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {SPECIES_INFO[selectedSpecies]?.rules.map((rule, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                        <CheckCircle className="h-4 w-4 text-[#f5a623]" />
                        {rule}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-4 border-t border-border">
                    <p className="text-gray-400 text-sm mb-2">Attractants recommandés:</p>
                    <div className="flex flex-wrap gap-2">
                      {SPECIES_INFO[selectedSpecies]?.attractants.map((attr, i) => (
                        <Badge key={i} className="bg-[#f5a623] text-black">
                          {attr}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {activeCategory === "territoire" && (
              <Tabs defaultValue="analyse" className="space-y-4">
                <TabsList className="grid grid-cols-4 bg-black/30">
                  <TabsTrigger value="analyse" className="flex items-center gap-1"><MapPin className="h-3 w-3" /> Analyse</TabsTrigger>
                  <TabsTrigger value="cameras" className="flex items-center gap-1"><Camera className="h-3 w-3" /> Caméras</TabsTrigger>
                  <TabsTrigger value="events" className="flex items-center gap-1"><Eye className="h-3 w-3" /> Événements</TabsTrigger>
                  <TabsTrigger value="plan" className="flex items-center gap-1"><FileText className="h-3 w-3" /> Plan</TabsTrigger>
                </TabsList>
                
                <TabsContent value="analyse" className="space-y-4">
                  {/* Species & Period Selection */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-white">Espèce cible</Label>
                      <Select value={selectedSpecies} onValueChange={setSelectedSpecies}>
                        <SelectTrigger className="bg-background border-border">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="orignal"><span className="flex items-center gap-2"><CircleDot className="h-3 w-3" style={{color: '#8B4513'}} /> Orignal</span></SelectItem>
                          <SelectItem value="chevreuil"><span className="flex items-center gap-2"><CircleDot className="h-3 w-3" style={{color: '#D2691E'}} /> Chevreuil</span></SelectItem>
                          <SelectItem value="ours"><span className="flex items-center gap-2"><CircleDot className="h-3 w-3" style={{color: '#2F4F4F'}} /> Ours noir</span></SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-white">Période de chasse</Label>
                      <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                        <SelectTrigger className="bg-background border-border">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {TIME_PERIODS.map(period => (
                            <SelectItem key={period.id} value={period.id}>
                              {period.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  {/* Location Input */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-white">Latitude</Label>
                      <Input
                        type="number"
                        step="0.001"
                        value={locationInput.lat}
                        onChange={(e) => setLocationInput({...locationInput, lat: parseFloat(e.target.value)})}
                        className="bg-background border-border"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-white">Longitude</Label>
                      <Input
                        type="number"
                        step="0.001"
                        value={locationInput.lng}
                        onChange={(e) => setLocationInput({...locationInput, lng: parseFloat(e.target.value)})}
                        className="bg-background border-border"
                      />
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <Button
                      onClick={calculateProbability}
                      disabled={loading}
                      className="flex-1 bg-[#f5a623] hover:bg-[#d4850e] text-black"
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <Target className="h-4 w-4 mr-2" />
                      )}
                      Analyser probabilité
                    </Button>
                    <Button
                      onClick={generateActionPlan}
                      disabled={loading}
                      variant="outline"
                      className="flex-1 border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10"
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <FileText className="h-4 w-4 mr-2" />
                      )}
                      Générer plan d'action
                    </Button>
                  </div>
                  
                  {/* Results */}
                  {probabilityResult && (
                    <ProbabilityResultCard result={probabilityResult} />
                  )}
                </TabsContent>
                
                <TabsContent value="cameras" className="space-y-4">
                  <div className="text-center py-8">
                    <Camera className="h-16 w-16 mx-auto text-gray-500 mb-4" />
                    <h3 className="text-white font-semibold mb-2">Connectez vos caméras</h3>
                    <p className="text-gray-400 text-sm mb-4">
                      GardePro, WingHome, SOVACAM, Reconyx, Bushnell, Moultrie
                    </p>
                    <Button className="bg-[#f5a623] hover:bg-[#d4850e] text-black">
                      <Plus className="h-4 w-4 mr-2" />
                      Ajouter une caméra
                    </Button>
                  </div>
                </TabsContent>
                
                <TabsContent value="events" className="space-y-4">
                  <div className="text-center py-8">
                    <Eye className="h-16 w-16 mx-auto text-gray-500 mb-4" />
                    <h3 className="text-white font-semibold mb-2">Enregistrez vos observations</h3>
                    <p className="text-gray-400 text-sm mb-4">
                      Tirs, observations visuelles, traces, frottages
                    </p>
                    <Button className="bg-[#f5a623] hover:bg-[#d4850e] text-black">
                      <Plus className="h-4 w-4 mr-2" />
                      Ajouter un événement
                    </Button>
                  </div>
                </TabsContent>
                
                <TabsContent value="plan" className="space-y-4">
                  {actionPlan ? (
                    <ActionPlanCard plan={actionPlan} />
                  ) : (
                    <div className="text-center py-8">
                      <FileText className="h-16 w-16 mx-auto text-gray-500 mb-4" />
                      <h3 className="text-white font-semibold mb-2">Générez votre plan d'action</h3>
                      <p className="text-gray-400 text-sm mb-4">
                        Sélectionnez une espèce et une zone dans l'onglet Analyse
                      </p>
                      <Button 
                        onClick={generateActionPlan}
                        className="bg-[#f5a623] hover:bg-[#d4850e] text-black"
                      >
                        <Sparkles className="h-4 w-4 mr-2" />
                        Générer maintenant
                      </Button>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Quick Links */}
      {!activeCategory && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Button
            variant="outline"
            className="h-auto py-4 flex flex-col items-center gap-2 border-[#f5a623]/30 hover:border-[#f5a623] hover:bg-[#f5a623]/10"
            onClick={() => {
              setActiveCategory("territoire");
              setSelectedSpecies("orignal");
            }}
          >
            <CircleDot className="h-8 w-8" style={{color: '#8B4513'}} />
            <span className="text-sm">Analyser Orignal</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 flex flex-col items-center gap-2 border-[#f5a623]/30 hover:border-[#f5a623] hover:bg-[#f5a623]/10"
            onClick={() => {
              setActiveCategory("territoire");
              setSelectedSpecies("chevreuil");
            }}
          >
            <CircleDot className="h-8 w-8" style={{color: '#D2691E'}} />
            <span className="text-sm">Analyser Chevreuil</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 flex flex-col items-center gap-2 border-[#f5a623]/30 hover:border-[#f5a623] hover:bg-[#f5a623]/10"
            onClick={() => {
              setActiveCategory("territoire");
              setSelectedSpecies("ours");
            }}
          >
            <CircleDot className="h-8 w-8" style={{color: '#2F4F4F'}} />
            <span className="text-sm">Analyser Ours</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 flex flex-col items-center gap-2 border-[#f5a623]/30 hover:border-[#f5a623] hover:bg-[#f5a623]/10"
            onClick={() => window.location.href = "/shop"}
          >
            <Target className="h-8 w-8 text-[#f5a623]" />
            <span className="text-sm">Voir Attractants</span>
          </Button>
        </div>
      )}
    </div>
  );
};

export default TerritoryAnalysisModule;
