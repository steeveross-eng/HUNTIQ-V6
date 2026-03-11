// ProductDiscoveryAdmin.jsx - Interface admin pour la découverte automatique de produits
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Search,
  Radar,
  Bot,
  Package,
  Bell,
  BellRing,
  CheckCircle,
  XCircle,
  Clock,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Plus,
  Trash2,
  Eye,
  ExternalLink,
  Languages,
  DollarSign,
  Star,
  Target,
  Loader2,
  AlertTriangle,
  Info,
  Mail,
  Inbox,
  Check,
  X,
  Globe,
  Zap,
  TrendingUp,
  Filter,
  ChevronRight,
  ChevronDown
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================
// SCANNER CONFIG COMPONENT
// ============================================
const ScannerConfigPanel = ({ config, onUpdate, onScan }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [localConfig, setLocalConfig] = useState(config);

  useEffect(() => {
    setLocalConfig(config);
  }, [config]);

  const handleFrequencyChange = async (frequency) => {
    try {
      await axios.put(`${API}/discovery/config`, { frequency });
      onUpdate();
      toast.success(`Fréquence de scan mise à jour: ${frequency}`);
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const handleToggle = async (field, value) => {
    try {
      await axios.put(`${API}/discovery/config`, { [field]: value });
      onUpdate();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const triggerScan = async () => {
    setIsScanning(true);
    try {
      await axios.post(`${API}/discovery/scan`, {
        use_priority_sources: localConfig.priority_sources_enabled,
        use_web_search: localConfig.web_search_enabled
      });
      toast.success("Scan démarré en arrière-plan");
      onScan();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors du scan");
    }
    setIsScanning(false);
  };

  const frequencyLabels = {
    realtime: "Temps réel (continu)",
    daily: "Quotidien (1x/jour)",
    weekly: "Hebdomadaire (1x/semaine)",
    manual: "Manuel uniquement"
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Settings className="h-5 w-5 text-[#f5a623]" />
          Configuration du Scanner
        </CardTitle>
        <CardDescription>
          Paramètres de détection automatique des produits
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Frequency Selector */}
        <div className="space-y-2">
          <Label className="text-white">Fréquence de scan</Label>
          <Select 
            value={localConfig.frequency || "daily"} 
            onValueChange={handleFrequencyChange}
          >
            <SelectTrigger className="bg-background border-border" data-testid="frequency-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="realtime">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  Temps réel (continu)
                </div>
              </SelectItem>
              <SelectItem value="daily">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  Quotidien (1x/jour)
                </div>
              </SelectItem>
              <SelectItem value="weekly">
                <div className="flex items-center gap-2">
                  <RefreshCw className="h-4 w-4 text-green-500" />
                  Hebdomadaire (1x/semaine)
                </div>
              </SelectItem>
              <SelectItem value="manual">
                <div className="flex items-center gap-2">
                  <Play className="h-4 w-4 text-purple-500" />
                  Manuel uniquement
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Toggles */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-background rounded-lg">
            <div className="flex items-center gap-3">
              <Globe className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-white font-medium">Sources prioritaires</p>
                <p className="text-gray-400 text-sm">Scanner les boutiques connues</p>
              </div>
            </div>
            <Switch
              checked={localConfig.priority_sources_enabled}
              onCheckedChange={(checked) => handleToggle("priority_sources_enabled", checked)}
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-background rounded-lg">
            <div className="flex items-center gap-3">
              <Search className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-white font-medium">Recherche web</p>
                <p className="text-gray-400 text-sm">Découvrir de nouvelles sources</p>
              </div>
            </div>
            <Switch
              checked={localConfig.web_search_enabled}
              onCheckedChange={(checked) => handleToggle("web_search_enabled", checked)}
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-background rounded-lg">
            <div className="flex items-center gap-3">
              <Languages className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-white font-medium">Traduction auto FR/EN</p>
                <p className="text-gray-400 text-sm">Utiliser l&apos;IA pour traduire</p>
              </div>
            </div>
            <Switch
              checked={localConfig.auto_translate}
              onCheckedChange={(checked) => handleToggle("auto_translate", checked)}
            />
          </div>
        </div>

        {/* Score Threshold */}
        <div className="space-y-2">
          <Label className="text-white">Score minimum requis</Label>
          <div className="flex items-center gap-4">
            <Input
              type="number"
              min={0}
              max={100}
              value={localConfig.min_score_threshold || 40}
              onChange={(e) => setLocalConfig({...localConfig, min_score_threshold: parseInt(e.target.value)})}
              className="bg-background border-border w-24"
            />
            <span className="text-gray-400">/ 100 points</span>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => handleToggle("min_score_threshold", localConfig.min_score_threshold)}
            >
              Appliquer
            </Button>
          </div>
        </div>

        {/* Last Scan Info */}
        {localConfig.last_scan && (
          <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
            <div className="flex items-center gap-2 text-green-400">
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm">
                Dernier scan: {new Date(localConfig.last_scan).toLocaleString()}
              </span>
            </div>
            <p className="text-gray-400 text-sm mt-1">
              {localConfig.products_found_last_scan} produits trouvés
            </p>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button 
          className="w-full btn-golden text-black"
          onClick={triggerScan}
          disabled={isScanning || config.is_running}
          data-testid="trigger-scan-btn"
        >
          {isScanning || config.is_running ? (
            <><Loader2 className="h-5 w-5 animate-spin mr-2" /> Scan en cours...</>
          ) : (
            <><Radar className="h-5 w-5 mr-2" /> Lancer un scan maintenant</>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
};

// ============================================
// NOTIFICATIONS PANEL (Boîte aux lettres IA)
// ============================================
const NotificationsPanel = ({ notifications, unreadCount, onRefresh, onProductAction }) => {
  const [selectedNotification, setSelectedNotification] = useState(null);

  const markAsRead = async (notificationId) => {
    try {
      await axios.post(`${API}/discovery/notifications/${notificationId}/read`);
      onRefresh();
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  const markAllRead = async () => {
    try {
      await axios.post(`${API}/discovery/notifications/read-all`);
      toast.success("Toutes les notifications marquées comme lues");
      onRefresh();
    } catch (error) {
      toast.error("Erreur");
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case "new_product": return <Package className="h-5 w-5 text-[#f5a623]" />;
      case "scan_complete": return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "error": return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default: return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-white">
            <Mail className="h-5 w-5 text-[#f5a623]" />
            Boîte aux lettres IA
            {unreadCount > 0 && (
              <Badge className="bg-red-500 text-white ml-2">{unreadCount}</Badge>
            )}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={markAllRead}>
            <Check className="h-4 w-4 mr-1" /> Tout lire
          </Button>
        </div>
        <CardDescription>
          Notifications des nouveaux produits détectés
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {notifications.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Inbox className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Aucune notification</p>
            </div>
          ) : (
            <div className="space-y-2">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    notif.is_read 
                      ? "bg-background hover:bg-gray-800" 
                      : "bg-[#f5a623]/10 border border-[#f5a623]/30 hover:bg-[#f5a623]/20"
                  }`}
                  onClick={() => {
                    markAsRead(notif.id);
                    if (notif.product_id) {
                      setSelectedNotification(notif);
                    }
                  }}
                >
                  <div className="flex items-start gap-3">
                    {getIcon(notif.type)}
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium truncate ${notif.is_read ? "text-gray-300" : "text-white"}`}>
                        {notif.title}
                      </p>
                      <p className="text-sm text-gray-400 truncate">{notif.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(notif.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!notif.is_read && (
                      <div className="w-2 h-2 bg-[#f5a623] rounded-full flex-shrink-0" />
                    )}
                  </div>
                  
                  {notif.type === "new_product" && notif.product_id && (
                    <div className="flex gap-2 mt-3">
                      <Button 
                        size="sm" 
                        className="btn-golden text-black flex-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          onProductAction(notif.product_id, "approve");
                        }}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" /> Activer
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        className="flex-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          onProductAction(notif.product_id, "reject");
                        }}
                      >
                        <XCircle className="h-4 w-4 mr-1" /> Rejeter
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

// ============================================
// PENDING PRODUCTS TABLE
// ============================================
const PendingProductsTable = ({ products, onAction, onViewProduct }) => {
  const getScoreColor = (score) => {
    if (score >= 70) return "text-green-500";
    if (score >= 50) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBadge = (score) => {
    if (score >= 70) return "bg-green-500/20 text-green-400 border-green-500/30";
    if (score >= 50) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    return "bg-red-500/20 text-red-400 border-red-500/30";
  };

  if (products.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <Package className="h-16 w-16 mx-auto mb-4 opacity-30" />
        <p className="text-lg">Aucun produit en attente</p>
        <p className="text-sm">Les nouveaux produits détectés apparaîtront ici</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-border">
            <TableHead className="text-gray-400">Produit</TableHead>
            <TableHead className="text-gray-400">Catégorie</TableHead>
            <TableHead className="text-gray-400">Prix</TableHead>
            <TableHead className="text-gray-400 text-center">Score</TableHead>
            <TableHead className="text-gray-400">Source</TableHead>
            <TableHead className="text-gray-400 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.map((product) => (
            <TableRow key={product.id} className="border-border hover:bg-background/50">
              <TableCell>
                <div className="flex items-center gap-3">
                  {product.main_image_url ? (
                    <img 
                      src={product.main_image_url} 
                      alt={product.name_fr}
                      className="w-12 h-12 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center">
                      <Package className="h-6 w-6 text-gray-500" />
                    </div>
                  )}
                  <div>
                    <p className="text-white font-medium truncate max-w-[200px]">
                      {product.name_fr}
                    </p>
                    <p className="text-gray-400 text-sm">{product.brand || "Sans marque"}</p>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="outline" className="capitalize">
                  {product.category}
                </Badge>
              </TableCell>
              <TableCell>
                <span className="text-[#f5a623] font-semibold">
                  ${product.price_regular?.toFixed(2) || "N/A"}
                </span>
              </TableCell>
              <TableCell className="text-center">
                <Badge className={getScoreBadge(product.score_total)}>
                  {Math.round(product.score_total)}/100
                </Badge>
              </TableCell>
              <TableCell>
                <span className="text-gray-400 text-sm">{product.source_name}</span>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button 
                    variant="ghost" 
                    size="icon"
                    onClick={() => onViewProduct(product)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    className="bg-green-600 hover:bg-green-700"
                    onClick={() => onAction(product.id, "approve")}
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="destructive"
                    onClick={() => onAction(product.id, "reject")}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

// ============================================
// SCORE ITEM COMPONENT
// ============================================
const ScoreItem = ({ label, score, maxScore, icon: Icon }) => (
  <div className="flex items-center justify-between p-2 bg-background rounded">
    <div className="flex items-center gap-2">
      <Icon className="h-4 w-4 text-gray-400" />
      <span className="text-gray-300 text-sm">{label}</span>
    </div>
    <div className="flex items-center gap-2">
      <Progress value={(score / maxScore) * 100} className="w-20 h-2" />
      <span className="text-white font-medium text-sm">{score}/{maxScore}</span>
    </div>
  </div>
);

// ============================================
// PRODUCT DETAIL MODAL
// ============================================
const ProductDetailModal = ({ product, isOpen, onClose, onAction }) => {
  if (!product) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border text-white max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Package className="h-5 w-5 text-[#f5a623]" />
            Détails du produit détecté
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-4">
          {/* Left Column - Image & Basic Info */}
          <div className="space-y-4">
            {product.main_image_url ? (
              <img 
                src={product.main_image_url}
                alt={product.name_fr}
                className="w-full h-48 object-cover rounded-lg"
              />
            ) : (
              <div className="w-full h-48 bg-gray-700 rounded-lg flex items-center justify-center">
                <Package className="h-16 w-16 text-gray-500" />
              </div>
            )}

            <div>
              <h3 className="text-xl font-bold text-white">{product.name_fr}</h3>
              {product.name_en && (
                <p className="text-gray-400 text-sm flex items-center gap-1">
                  <Languages className="h-3 w-3" /> {product.name_en}
                </p>
              )}
              <p className="text-[#f5a623]">{product.brand || "Sans marque"}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge className="bg-purple-500/20 text-purple-400">{product.category}</Badge>
              {product.target_species?.map((species, i) => (
                <Badge key={i} variant="outline">{species}</Badge>
              ))}
            </div>

            <div className="p-4 bg-background rounded-lg">
              <p className="text-3xl font-bold text-[#f5a623]">
                ${product.price_regular?.toFixed(2) || "N/A"}
              </p>
              {product.price_with_shipping && (
                <p className="text-sm text-gray-400">
                  ${product.price_with_shipping} avec transport
                </p>
              )}
            </div>

            {product.source_url && (
              <a 
                href={product.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm"
              >
                <ExternalLink className="h-4 w-4" />
                Voir sur {product.source_name}
              </a>
            )}
          </div>

          {/* Right Column - Scores & Details */}
          <div className="space-y-4">
            {/* Score Total */}
            <div className={`p-4 rounded-lg border ${
              product.score_total >= 70 
                ? "bg-green-500/10 border-green-500/30" 
                : product.score_total >= 50 
                  ? "bg-yellow-500/10 border-yellow-500/30"
                  : "bg-red-500/10 border-red-500/30"
            }`}>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Score total</span>
                <span className={`text-3xl font-bold ${
                  product.score_total >= 70 ? "text-green-400" :
                  product.score_total >= 50 ? "text-yellow-400" : "text-red-400"
                }`}>
                  {Math.round(product.score_total)}/100
                </span>
              </div>
              <Progress value={product.score_total} className="mt-2 h-3" />
            </div>

            {/* Score Breakdown */}
            <div className="space-y-2">
              <h4 className="text-white font-medium">Détail du scoring</h4>
              <ScoreItem label="Attractivité chimique" score={product.score_chemical_attraction} maxScore={30} icon={Zap} />
              <ScoreItem label="Pertinence espèce" score={product.score_species_relevance} maxScore={20} icon={Target} />
              <ScoreItem label="Mode application" score={product.score_application_mode} maxScore={15} icon={Settings} />
              <ScoreItem label="Durée & portée" score={product.score_duration_range} maxScore={10} icon={Clock} />
              <ScoreItem label="Valeur économique" score={product.score_economic_value} maxScore={15} icon={DollarSign} />
              <ScoreItem label="Qualité marque" score={product.score_brand_quality} maxScore={5} icon={Star} />
              <ScoreItem label="Données terrain" score={product.score_field_data} maxScore={5} icon={TrendingUp} />
            </div>

            {/* Description */}
            {product.description_fr && (
              <div>
                <h4 className="text-white font-medium mb-2">Description</h4>
                <p className="text-gray-400 text-sm">{product.description_fr}</p>
              </div>
            )}

            {/* Advantages */}
            {product.advantages_fr?.length > 0 && (
              <div>
                <h4 className="text-white font-medium mb-2">Avantages</h4>
                <ul className="space-y-1">
                  {product.advantages_fr.map((adv, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      {adv}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Tags */}
            {product.tags_fr?.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {product.tags_fr.map((tag, i) => (
                  <Badge key={i} variant="outline" className="text-xs">{tag}</Badge>
                ))}
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Fermer
          </Button>
          <Button 
            variant="destructive"
            onClick={() => {
              onAction(product.id, "reject");
              onClose();
            }}
          >
            <XCircle className="h-4 w-4 mr-2" /> Ne pas inclure
          </Button>
          <Button 
            className="btn-golden text-black"
            onClick={() => {
              onAction(product.id, "approve");
              onClose();
            }}
          >
            <CheckCircle className="h-4 w-4 mr-2" /> Inclure / Activer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// QUICK ADD PRODUCT FORM
// ============================================
const QuickAddForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    name_fr: "",
    brand: "",
    category: "attractant",
    description_fr: "",
    price_regular: "",
    image_url: "",
    source_url: "",
    target_species: [],
    auto_translate: true
  });
  const [loading, setLoading] = useState(false);

  const categories = [
    { value: "attractant", label: "Attractant" },
    { value: "urine", label: "Urine / Leurre" },
    { value: "mineral", label: "Bloc minéral" },
    { value: "gel", label: "Gel / Gelée" },
    { value: "powder", label: "Poudre" },
    { value: "liquid", label: "Liquide / Spray" },
    { value: "granules", label: "Granules" },
    { value: "feeder", label: "Mangeoire" }
  ];

  const speciesOptions = ["deer", "moose", "bear", "elk", "multi"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name_fr.trim()) {
      toast.error("Le nom du produit est requis");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/discovery/quick-add`, {
        ...formData,
        price_regular: parseFloat(formData.price_regular) || 0
      });
      
      toast.success("Produit ajouté avec succès!");
      setFormData({
        name_fr: "",
        brand: "",
        category: "attractant",
        description_fr: "",
        price_regular: "",
        image_url: "",
        source_url: "",
        target_species: [],
        auto_translate: true
      });
      onSuccess();
    } catch (error) {
      toast.error("Erreur lors de l'ajout du produit");
    }
    setLoading(false);
  };

  const toggleSpecies = (species) => {
    setFormData(prev => ({
      ...prev,
      target_species: prev.target_species.includes(species)
        ? prev.target_species.filter(s => s !== species)
        : [...prev.target_species, species]
    }));
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Plus className="h-5 w-5 text-[#f5a623]" />
          Ajouter un produit manuellement
        </CardTitle>
        <CardDescription>
          Ajoutez rapidement un produit sans passer par le scanner
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-white">Nom du produit (FR) *</Label>
              <Input
                value={formData.name_fr}
                onChange={(e) => setFormData({...formData, name_fr: e.target.value})}
                className="bg-background border-border"
                placeholder="Ex: Attractant Cerf Pro"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-white">Marque</Label>
              <Input
                value={formData.brand}
                onChange={(e) => setFormData({...formData, brand: e.target.value})}
                className="bg-background border-border"
                placeholder="Ex: Wildlife Research"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-white">Catégorie</Label>
              <Select 
                value={formData.category} 
                onValueChange={(value) => setFormData({...formData, category: value})}
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-white">Prix régulier ($)</Label>
              <Input
                type="number"
                step="0.01"
                value={formData.price_regular}
                onChange={(e) => setFormData({...formData, price_regular: e.target.value})}
                className="bg-background border-border"
                placeholder="29.99"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-white">Espèces ciblées</Label>
            <div className="flex flex-wrap gap-2">
              {speciesOptions.map(species => (
                <button
                  key={species}
                  type="button"
                  onClick={() => toggleSpecies(species)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    formData.target_species.includes(species)
                      ? "bg-[#f5a623] text-black"
                      : "bg-background text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  {species}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-white">Description</Label>
            <Textarea
              value={formData.description_fr}
              onChange={(e) => setFormData({...formData, description_fr: e.target.value})}
              className="bg-background border-border"
              rows={3}
              placeholder="Description du produit..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-white">URL image</Label>
              <Input
                value={formData.image_url}
                onChange={(e) => setFormData({...formData, image_url: e.target.value})}
                className="bg-background border-border"
                placeholder="https://..."
              />
            </div>
            <div className="space-y-2">
              <Label className="text-white">URL source (achat)</Label>
              <Input
                value={formData.source_url}
                onChange={(e) => setFormData({...formData, source_url: e.target.value})}
                className="bg-background border-border"
                placeholder="https://..."
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Switch
              checked={formData.auto_translate}
              onCheckedChange={(checked) => setFormData({...formData, auto_translate: checked})}
            />
            <Label className="text-gray-300">Traduire automatiquement en anglais (IA)</Label>
          </div>

          <Button 
            type="submit" 
            className="w-full btn-golden text-black"
            disabled={loading}
          >
            {loading ? (
              <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Ajout en cours...</>
            ) : (
              <><Plus className="h-4 w-4 mr-2" /> Ajouter le produit</>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================
const ProductDiscoveryAdmin = () => {
  const [activeTab, setActiveTab] = useState("notifications");
  const [config, setConfig] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [pendingProducts, setPendingProducts] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [configRes, notifRes, productsRes] = await Promise.all([
        axios.get(`${API}/discovery/config`),
        axios.get(`${API}/discovery/notifications?limit=50`),
        axios.get(`${API}/discovery/products?status=pending&limit=50`)
      ]);

      setConfig(configRes.data);
      setNotifications(notifRes.data.notifications);
      setUnreadCount(notifRes.data.unread_count);
      setPendingProducts(productsRes.data.products);
      setStats(productsRes.data.stats);
    } catch (error) {
      console.error("Error loading data:", error);
    }
    setLoading(false);
  };

  // Initial load
  useEffect(() => {
    fetchData();
     
  }, []);
  
  // Polling for updates
  useEffect(() => {
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const loadData = fetchData;

  const handleProductAction = async (productId, action) => {
    try {
      await axios.post(`${API}/discovery/products/${productId}/approve`, {
        action: action,
        rejection_reason: action === "reject" ? "Rejeté par l'administrateur" : null
      });
      
      toast.success(action === "approve" 
        ? "Produit activé avec succès!" 
        : "Produit rejeté"
      );
      
      loadData();
    } catch (error) {
      toast.error("Erreur lors de l'action");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Bot className="h-6 w-6 text-[#f5a623]" />
            Découverte Automatique de Produits
          </h2>
          <p className="text-gray-400">
            Système intelligent de détection, classification et intégration
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Badge className="bg-green-500/20 text-green-400 px-3 py-1">
            {stats.active || 0} produits actifs
          </Badge>
          <Badge className="bg-yellow-500/20 text-yellow-400 px-3 py-1">
            {stats.pending || 0} en attente
          </Badge>
          {unreadCount > 0 && (
            <Badge className="bg-red-500 text-white px-3 py-1 animate-pulse">
              <BellRing className="h-4 w-4 mr-1" /> {unreadCount} nouveau(x)
            </Badge>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-background">
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Mail className="h-4 w-4" />
            Boîte aux lettres
            {unreadCount > 0 && (
              <Badge className="bg-red-500 text-white text-xs ml-1">{unreadCount}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            En attente ({stats.pending || 0})
          </TabsTrigger>
          <TabsTrigger value="scanner" className="flex items-center gap-2">
            <Radar className="h-4 w-4" />
            Scanner
          </TabsTrigger>
          <TabsTrigger value="add" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Ajouter
          </TabsTrigger>
        </TabsList>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <NotificationsPanel 
              notifications={notifications}
              unreadCount={unreadCount}
              onRefresh={loadData}
              onProductAction={handleProductAction}
            />
            
            {/* Quick Stats */}
            <div className="space-y-4">
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-[#f5a623]" />
                    Statistiques
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-background rounded-lg text-center">
                    <p className="text-3xl font-bold text-yellow-400">{stats.pending || 0}</p>
                    <p className="text-gray-400 text-sm">En attente</p>
                  </div>
                  <div className="p-4 bg-background rounded-lg text-center">
                    <p className="text-3xl font-bold text-green-400">{stats.approved || 0}</p>
                    <p className="text-gray-400 text-sm">Approuvés</p>
                  </div>
                  <div className="p-4 bg-background rounded-lg text-center">
                    <p className="text-3xl font-bold text-blue-400">{stats.active || 0}</p>
                    <p className="text-gray-400 text-sm">Actifs</p>
                  </div>
                  <div className="p-4 bg-background rounded-lg text-center">
                    <p className="text-3xl font-bold text-red-400">{stats.rejected || 0}</p>
                    <p className="text-gray-400 text-sm">Rejetés</p>
                  </div>
                </CardContent>
              </Card>

              {/* Last Scan Info */}
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      config.is_running ? "bg-yellow-500/20" : "bg-green-500/20"
                    }`}>
                      {config.is_running ? (
                        <Loader2 className="h-6 w-6 text-yellow-500 animate-spin" />
                      ) : (
                        <CheckCircle className="h-6 w-6 text-green-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-white font-medium">
                        {config.is_running ? "Scan en cours..." : "Scanner prêt"}
                      </p>
                      {config.last_scan && (
                        <p className="text-gray-400 text-sm">
                          Dernier scan: {new Date(config.last_scan).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Pending Products Tab */}
        <TabsContent value="pending" className="mt-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Package className="h-5 w-5 text-[#f5a623]" />
                Produits en attente de validation
              </CardTitle>
              <CardDescription>
                Approuvez ou rejetez les produits détectés automatiquement
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PendingProductsTable 
                products={pendingProducts}
                onAction={handleProductAction}
                onViewProduct={setSelectedProduct}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scanner Tab */}
        <TabsContent value="scanner" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ScannerConfigPanel 
              config={config}
              onUpdate={loadData}
              onScan={loadData}
            />

            {/* Sources Panel */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Globe className="h-5 w-5 text-[#f5a623]" />
                  Sources prioritaires
                </CardTitle>
                <CardDescription>
                  Sites scannés en priorité pour la détection
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {[
                    {name: "Zone Écotone", url: "zone-ecotone.com", type: "store"},
                    {name: "Sail Outdoors", url: "sail.ca", type: "store"},
                    {name: "Bass Pro Shops", url: "basspro.com", type: "store"},
                    {name: "Cabela's Canada", url: "cabelas.ca", type: "store"},
                  ].map((source, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-background rounded-lg">
                      <div className="flex items-center gap-3">
                        <Globe className="h-4 w-4 text-blue-500" />
                        <div>
                          <p className="text-white font-medium">{source.name}</p>
                          <p className="text-gray-400 text-sm">{source.url}</p>
                        </div>
                      </div>
                      <Badge variant="outline">{source.type}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Add Product Tab */}
        <TabsContent value="add" className="mt-6">
          <div className="max-w-2xl">
            <QuickAddForm onSuccess={loadData} />
          </div>
        </TabsContent>
      </Tabs>

      {/* Product Detail Modal */}
      <ProductDetailModal
        product={selectedProduct}
        isOpen={!!selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAction={handleProductAction}
      />
    </div>
  );
};

export default ProductDiscoveryAdmin;
