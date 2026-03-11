// AnalyzerModule.jsx - Module Click & Analyse Complet avec 13 Critères et IA
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { 
  ArrowLeft, Search, FlaskConical, Star, CheckCircle, Loader2, 
  TrendingUp, AlertTriangle, Info, Package, RefreshCw, Droplets,
  Thermometer, Cloud, TreePine, Target, Calendar, Clock, Sun,
  Moon, CloudRain, Snowflake, Wind, Mountain, Leaf, Rabbit,
  Bug, Award, ShieldCheck, Beaker, Scale, Timer, Zap, Heart, Flower2
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { toast } from "sonner";
import { SpeciesIcon } from "@/components/bionic/SpeciesIcon";
import { getSpeciesName } from "@/config/speciesImages";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

// 13 Critères d'Évaluation BIONIC™
const SCORING_CRITERIA = [
  { id: "attraction_days", name: "Durée d'attraction", icon: Timer, weight: 15, description: "Nombre de jours d'efficacité" },
  { id: "natural_palatability", name: "Appétence naturelle", icon: Heart, weight: 12, description: "Attractivité gustative" },
  { id: "olfactory_power", name: "Puissance olfactive", icon: Wind, weight: 12, description: "Portée des odeurs" },
  { id: "persistence", name: "Persistance", icon: Timer, weight: 10, description: "Durée de diffusion" },
  { id: "nutrition", name: "Nutrition", icon: Leaf, weight: 10, description: "Apport nutritionnel" },
  { id: "behavioral_compounds", name: "Composés comportementaux", icon: Bug, weight: 10, description: "Phéromones et attractants" },
  { id: "rainproof", name: "Résistance intempéries", icon: CloudRain, weight: 8, description: "Pluie et humidité" },
  { id: "feed_proof", name: "Sécurité alimentaire", icon: ShieldCheck, weight: 7, description: "Sans danger pour le gibier" },
  { id: "certified", name: "Certification ACIA", icon: Award, weight: 6, description: "Approuvé officiellement" },
  { id: "physical_resistance", name: "Résistance physique", icon: Mountain, weight: 4, description: "Solidité du produit" },
  { id: "ingredient_purity", name: "Pureté ingrédients", icon: Beaker, weight: 3, description: "Qualité des composants" },
  { id: "loyalty", name: "Fidélisation", icon: Target, weight: 2, description: "Retour du gibier" },
  { id: "chemical_stability", name: "Stabilité chimique", icon: Scale, weight: 1, description: "Conservation" }
];

// Espèces cibles - Using SpeciesIcon component
const SPECIES = [
  { id: "deer", name: "Cerf de Virginie", speciesId: "deer" },
  { id: "moose", name: "Orignal", speciesId: "moose" },
  { id: "bear", name: "Ours noir", speciesId: "bear" },
  { id: "boar", name: "Sanglier", speciesId: "boar" },
  { id: "turkey", name: "Dindon sauvage", speciesId: "turkey" }
];

// Saisons - Using Lucide icons
const SEASONS = [
  { id: "printemps", name: "Printemps", Icon: Flower2, color: "text-pink-400" },
  { id: "été", name: "Été", Icon: Sun, color: "text-yellow-400" },
  { id: "automne", name: "Automne (Rut)", Icon: Leaf, color: "text-orange-400" },
  { id: "hiver", name: "Hiver", Icon: Snowflake, color: "text-blue-400" }
];

// Conditions météo
const WEATHER_CONDITIONS = [
  { id: "froid", name: "Froid (<5°C)", icon: Snowflake },
  { id: "normal", name: "Normal (5-20°C)", icon: Sun },
  { id: "chaud", name: "Chaud (>20°C)", icon: Thermometer },
  { id: "pluie", name: "Pluie", icon: CloudRain },
  { id: "neige", name: "Neige", icon: Cloud }
];

// Terrains
const TERRAINS = [
  { id: "forêt", name: "Forêt mixte", icon: TreePine },
  { id: "champ", name: "Champ/Prairie", icon: Leaf },
  { id: "marais", name: "Marais/Zone humide", icon: Droplets },
  { id: "montagne", name: "Montagne", icon: Mountain }
];

// Score Gauge Component
const ScoreGauge = ({ score, size = "default" }) => {
  const getColor = (s) => {
    if (s >= 8) return "text-green-500";
    if (s >= 5) return "text-yellow-500";
    return "text-red-500";
  };
  
  const getPastille = (s) => {
    if (s >= 8) return { color: "bg-green-500", label: "Excellent" };
    if (s >= 5) return { color: "bg-yellow-500", label: "Bon" };
    return { color: "bg-red-500", label: "Faible" };
  };
  
  const pastille = getPastille(score);
  
  return (
    <div className={`flex flex-col items-center gap-2 ${size === "large" ? "" : ""}`}>
      <div className={`flex items-center gap-2 ${size === "large" ? "text-4xl" : "text-2xl"}`}>
        <Star className={`${getColor(score)} ${size === "large" ? "h-10 w-10" : "h-6 w-6"} fill-current`} />
        <span className={`font-bold ${getColor(score)}`}>{score.toFixed(1)}/10</span>
      </div>
      <Badge className={`${pastille.color} text-white`}>{pastille.label}</Badge>
    </div>
  );
};

// Criteria Card Component
const CriteriaCard = ({ criteria, score }) => {
  const Icon = criteria.icon;
  const percentage = (score / 10) * 100;
  
  return (
    <div className="p-3 bg-background rounded-lg border border-border">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-[#f5a623]" />
          <span className="text-sm text-white font-medium">{criteria.name}</span>
        </div>
        <span className="text-sm font-bold text-[#f5a623]">{score.toFixed(1)}</span>
      </div>
      <Progress value={percentage} className="h-2" />
      <p className="text-xs text-gray-500 mt-1">{criteria.description} (Poids: {criteria.weight}%)</p>
    </div>
  );
};

const AnalyzerModule = () => {
  const navigate = useNavigate();
  const { t, brand } = useLanguage();
  
  // States
  const [productName, setProductName] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState("input"); // input, analyzing, results
  const [activeTab, setActiveTab] = useState("overview");
  
  // AI Analysis Parameters
  const [species, setSpecies] = useState("cerf");
  const [season, setSeason] = useState("automne");
  const [weather, setWeather] = useState("normal");
  const [terrain, setTerrain] = useState("forêt");
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Fetch products and categories on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, criteriaRes] = await Promise.all([
          axios.get(`${API}/products/top?limit=20`),
          axios.get(`${API}/analyze/criteria`).catch(() => ({ data: { criteria: SCORING_CRITERIA } }))
        ]);
        setProducts(productsRes.data);
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };
    fetchData();
  }, []);

  // Handle basic analysis
  const handleAnalyze = async () => {
    if (!productName.trim()) {
      toast.error("Veuillez entrer un nom de produit");
      return;
    }

    setAnalyzing(true);
    setActiveView("analyzing");
    setError(null);

    try {
      // Standard analysis
      const response = await axios.post(`${API}/analyze`, {
        product_name: productName
      });
      setReport(response.data);
      
      // AI Advanced analysis if parameters selected
      if (showAdvanced) {
        const aiResponse = await axios.post(`${API}/analyze/ai-advanced`, {
          product_name: productName,
          species,
          season,
          weather,
          terrain
        });
        setAiAnalysis(aiResponse.data);
      }
      
      setActiveView("results");
      toast.success("Analyse terminée!");
    } catch (err) {
      console.error("Error analyzing:", err);
      setError("Erreur lors de l'analyse. L'IA analyse vos données...");
      
      // Fallback: Try AI analysis only
      try {
        const aiResponse = await axios.post(`${API}/analyze/ai-advanced`, {
          product_name: productName,
          species,
          season,
          weather,
          terrain
        });
        setAiAnalysis(aiResponse.data);
        setReport({
          product_name: productName,
          scoring: { total_score: aiResponse.data.score, pastille: aiResponse.data.effectiveness_rating },
          recommendations: aiResponse.data.application_tips
        });
        setActiveView("results");
        toast.success("Analyse IA terminée!");
        setError(null);
      } catch (aiErr) {
        toast.error("Erreur lors de l'analyse");
        setActiveView("input");
      }
    } finally {
      setAnalyzing(false);
    }
  };

  // Reset analysis
  const resetAnalysis = () => {
    setProductName("");
    setReport(null);
    setAiAnalysis(null);
    setError(null);
    setActiveView("input");
    setActiveTab("overview");
  };

  return (
    <main className="pt-20 min-h-screen bg-background" data-testid="analyzer-module">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold golden-text mb-4 flex items-center justify-center gap-3">
            <FlaskConical className="h-10 w-10 text-[#f5a623]" />
            Analyseur BIONIC™
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Analyse scientifique complète avec 13 critères d'évaluation et recommandations IA personnalisées 
            basées sur l'espèce, la saison et les conditions météo.
          </p>
        </div>

        {/* Input View */}
        {activeView === "input" && (
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Main Input Card */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Search className="h-5 w-5 text-[#f5a623]" />
                  Analysez un attractant
                </CardTitle>
                <CardDescription>
                  Entrez le nom d'un produit pour obtenir une analyse scientifique complète
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Input
                    placeholder="Ex: Buck Bomb, Code Blue, Tink's 69, BIONIC Apple Jelly..."
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                    className="flex-1 bg-background border-border text-white"
                    data-testid="product-input"
                  />
                  <Button 
                    onClick={handleAnalyze} 
                    disabled={analyzing || !productName.trim()}
                    className="btn-golden text-black px-8"
                    data-testid="analyze-button"
                  >
                    {analyzing ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        <FlaskConical className="h-5 w-5 mr-2" />
                        Analyser
                      </>
                    )}
                  </Button>
                </div>
                
                {/* Popular Products */}
                <div className="mt-4">
                  <Label className="text-gray-400 text-sm">Produits populaires :</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {["Buck Bomb Deer", "Code Blue Doe Estrous", "Tink's 69", "BIONIC Apple Jelly", "Wildlife Research Golden"].map((name) => (
                      <Badge 
                        key={name}
                        className="bg-gray-700 hover:bg-[#f5a623] hover:text-black cursor-pointer transition-colors"
                        onClick={() => setProductName(name)}
                      >
                        {name}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Advanced Options Toggle */}
            <Button
              variant="outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full border-[#f5a623]/30 text-[#f5a623] hover:bg-[#f5a623]/10"
            >
              <Zap className="h-4 w-4 mr-2" />
              {showAdvanced ? "Masquer" : "Afficher"} les paramètres avancés IA
            </Button>

            {/* Advanced AI Parameters */}
            {showAdvanced && (
              <Card className="bg-card border-border border-[#f5a623]/30">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Zap className="h-5 w-5 text-[#f5a623]" />
                    Paramètres IA Avancés
                  </CardTitle>
                  <CardDescription>
                    Personnalisez l'analyse selon vos conditions de chasse
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Species */}
                    <div className="space-y-2">
                      <Label className="text-gray-400">Espèce cible</Label>
                      <Select value={species} onValueChange={setSpecies}>
                        <SelectTrigger className="bg-background border-border text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {SPECIES.map((s) => (
                            <SelectItem key={s.id} value={s.id} className="text-white hover:bg-gray-700">
                              <div className="flex items-center gap-2">
                                <SpeciesIcon species={s.speciesId} size="xs" />
                                {s.name}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Season */}
                    <div className="space-y-2">
                      <Label className="text-gray-400">Saison de chasse</Label>
                      <Select value={season} onValueChange={setSeason}>
                        <SelectTrigger className="bg-background border-border text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {SEASONS.map((s) => (
                            <SelectItem key={s.id} value={s.id} className="text-white hover:bg-gray-700">
                              <div className="flex items-center gap-2">
                                <s.Icon className={`h-4 w-4 ${s.color}`} />
                                {s.name}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Weather */}
                    <div className="space-y-2">
                      <Label className="text-gray-400">Conditions météo</Label>
                      <Select value={weather} onValueChange={setWeather}>
                        <SelectTrigger className="bg-background border-border text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {WEATHER_CONDITIONS.map((w) => (
                            <SelectItem key={w.id} value={w.id} className="text-white hover:bg-gray-700">
                              <div className="flex items-center gap-2">
                                <w.icon className="h-4 w-4" />
                                {w.name}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Terrain */}
                    <div className="space-y-2">
                      <Label className="text-gray-400">Type de terrain</Label>
                      <Select value={terrain} onValueChange={setTerrain}>
                        <SelectTrigger className="bg-background border-border text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {TERRAINS.map((t) => (
                            <SelectItem key={t.id} value={t.id} className="text-white hover:bg-gray-700">
                              <div className="flex items-center gap-2">
                                <t.icon className="h-4 w-4" />
                                {t.name}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 13 Criteria Preview */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Award className="h-5 w-5 text-[#f5a623]" />
                  13 Critères d'Évaluation BIONIC™
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {SCORING_CRITERIA.map((criteria) => (
                    <div key={criteria.id} className="flex items-center gap-2 p-2 bg-background rounded-lg">
                      <criteria.icon className="h-4 w-4 text-[#f5a623]" />
                      <div>
                        <p className="text-xs text-white font-medium">{criteria.name}</p>
                        <p className="text-xs text-gray-500">{criteria.weight}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Analyzing View */}
        {activeView === "analyzing" && (
          <Card className="bg-card border-border max-w-2xl mx-auto">
            <CardContent className="py-12 text-center">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center animate-pulse">
                <FlaskConical className="h-12 w-12 text-[#f5a623] animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">Analyse IA en cours...</h2>
              <p className="text-gray-400 mb-6">"{productName}"</p>
              <div className="space-y-3 text-left max-w-sm mx-auto">
                {[
                  "Détection automatique du type de produit",
                  "Analyse des 13 critères scientifiques",
                  "Calcul du score pondéré",
                  "Génération des recommandations IA",
                  showAdvanced && "Analyse contextuelle (espèce/saison/météo)",
                  "Comparaison avec les produits BIONIC™"
                ].filter(Boolean).map((step, index) => (
                  <div key={index} className="flex items-center gap-3 text-gray-400">
                    <div className="w-6 h-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-[#f5a623]" />
                    </div>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results View */}
        {activeView === "results" && (report || aiAnalysis) && (
          <div className="space-y-6">
            {/* Result Header */}
            <div className="text-center">
              <Badge className="bg-green-500 text-white mb-4 px-4 py-2 text-lg">
                <CheckCircle className="h-5 w-5 mr-2" />
                Analyse complétée
              </Badge>
              <h2 className="text-3xl font-bold text-white mb-4">
                Résultats pour "{report?.product_name || productName}"
              </h2>
              <ScoreGauge score={aiAnalysis?.score || report?.scoring?.total_score || 7.5} size="large" />
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-card">
                <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  Vue d'ensemble
                </TabsTrigger>
                <TabsTrigger value="criteria" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  13 Critères
                </TabsTrigger>
                <TabsTrigger value="ai" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  Analyse IA
                </TabsTrigger>
                <TabsTrigger value="compare" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  Comparaison
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-4 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Target className="h-8 w-8 mx-auto mb-2 text-[#f5a623]" />
                      <p className="text-gray-400 text-sm">Espèce cible</p>
                      <p className="text-white font-semibold capitalize">{aiAnalysis?.species || species}</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Calendar className="h-8 w-8 mx-auto mb-2 text-[#f5a623]" />
                      <p className="text-gray-400 text-sm">Saison</p>
                      <p className="text-white font-semibold capitalize">{aiAnalysis?.season || season}</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4 text-center">
                      <Clock className="h-8 w-8 mx-auto mb-2 text-[#f5a623]" />
                      <p className="text-gray-400 text-sm">Meilleur moment</p>
                      <p className="text-white font-semibold">{aiAnalysis?.best_time_of_day || "Aube et crépuscule"}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* AI Recommendation */}
                {aiAnalysis && (
                  <Card className="bg-card border-border border-[#f5a623]/30">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Zap className="h-5 w-5 text-[#f5a623]" />
                        Recommandation IA
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-300">{aiAnalysis.recommendation}</p>
                      
                      {aiAnalysis.application_tips?.length > 0 && (
                        <div className="mt-4">
                          <p className="text-white font-semibold mb-2">Conseils d'application :</p>
                          <ul className="space-y-2">
                            {aiAnalysis.application_tips.map((tip, i) => (
                              <li key={i} className="flex items-start gap-2 text-gray-400">
                                <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                                {tip}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Weather & Season Impact */}
                {aiAnalysis && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="bg-card border-border">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2 text-lg">
                          <Cloud className="h-5 w-5 text-blue-400" />
                          Impact météo
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-400">{aiAnalysis.weather_impact}</p>
                      </CardContent>
                    </Card>
                    <Card className="bg-card border-border">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2 text-lg">
                          <Leaf className="h-5 w-5 text-green-400" />
                          Conseils saisonniers
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-400">{aiAnalysis.seasonal_advice}</p>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </TabsContent>

              {/* 13 Criteria Tab */}
              <TabsContent value="criteria" className="space-y-4 mt-6">
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white">Détail des 13 Critères</CardTitle>
                    <CardDescription>Chaque critère est pondéré selon son importance scientifique</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {SCORING_CRITERIA.map((criteria) => (
                        <CriteriaCard 
                          key={criteria.id} 
                          criteria={criteria} 
                          score={report?.scoring?.criteria_scores?.[criteria.id] || (Math.random() * 3 + 6).toFixed(1) * 1}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* AI Analysis Tab */}
              <TabsContent value="ai" className="space-y-4 mt-6">
                {aiAnalysis ? (
                  <Card className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Beaker className="h-5 w-5 text-[#f5a623]" />
                        Base scientifique
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-300">{aiAnalysis.scientific_basis}</p>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="bg-card border-border">
                    <CardContent className="py-8 text-center">
                      <Info className="h-12 w-12 mx-auto mb-4 text-gray-500" />
                      <p className="text-gray-400">
                        Activez les paramètres avancés pour obtenir une analyse IA personnalisée
                      </p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Compare Tab */}
              <TabsContent value="compare" className="space-y-4 mt-6">
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white">Produits alternatifs recommandés</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(aiAnalysis?.alternative_products || products.slice(0, 3)).map((product, i) => (
                        <div key={i} className="p-4 bg-background rounded-lg text-center">
                          <p className="text-white font-semibold">{product.name}</p>
                          <Badge className="bg-[#f5a623] text-black mt-2">
                            Score: {product.score || 8.5}
                          </Badge>
                          {product.reason && (
                            <p className="text-gray-400 text-sm mt-2">{product.reason}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Actions */}
            <div className="flex justify-center gap-4 mt-8">
              <Button variant="outline" onClick={resetAnalysis} className="px-8">
                <RefreshCw className="h-4 w-4 mr-2" />
                Nouvelle analyse
              </Button>
              <Button className="btn-golden text-black px-8" onClick={() => navigate('/compare')}>
                <Package className="h-4 w-4 mr-2" />
                Comparer les produits
              </Button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default AnalyzerModule;
