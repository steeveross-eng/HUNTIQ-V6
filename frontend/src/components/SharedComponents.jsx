/**
 * SharedComponents - Small reusable UI components
 * Used across multiple pages
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FlaskConical, Loader2, Sparkles, CheckCircle, ArrowLeft, Home } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================
// BACK BUTTON - Reusable navigation component
// ============================================

/**
 * BackButton - Bouton de retour réutilisable
 * @param {string} label - Texte du bouton (défaut: "Retour")
 * @param {string} to - Destination (défaut: "/" pour accueil)
 * @param {string} variant - Style du bouton: "default", "ghost", "outline"
 * @param {string} className - Classes CSS additionnelles
 * @param {boolean} showIcon - Afficher l'icône (défaut: true)
 */
export const BackButton = ({ 
  label = "Retour", 
  to = "/", 
  variant = "ghost",
  className = "",
  showIcon = true,
  iconType = "arrow" // "arrow" ou "home"
}) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    if (to === "back") {
      // Go back in browser history
      window.history.back();
    } else {
      navigate(to);
    }
  };
  
  const Icon = iconType === "home" ? Home : ArrowLeft;
  
  return (
    <Button 
      variant={variant} 
      onClick={handleClick}
      className={`text-gray-400 hover:text-white hover:bg-gray-800/50 ${className}`}
      data-testid="back-button"
    >
      {showIcon && <Icon className="h-4 w-4 mr-2" />}
      {label}
    </Button>
  );
};

// ============================================
// PAGE HEADER WITH BACK BUTTON
// ============================================

/**
 * PageHeaderWithBack - En-tête de page avec bouton retour intégré
 * @param {string} title - Titre de la page
 * @param {string} subtitle - Sous-titre optionnel
 * @param {ReactNode} icon - Icône à afficher
 * @param {string} backTo - Destination du retour
 * @param {string} backLabel - Texte du bouton retour
 */
export const PageHeaderWithBack = ({
  title,
  subtitle,
  icon,
  backTo = "/",
  backLabel = "Retour à l'accueil",
  children
}) => {
  return (
    <div className="mb-6">
      <BackButton label={backLabel} to={backTo} className="mb-4" />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="bg-[#f5a623]/20 p-2.5 rounded-xl">
              {icon}
            </div>
          )}
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">{title}</h1>
            {subtitle && <p className="text-gray-400 text-sm mt-1">{subtitle}</p>}
          </div>
        </div>
        {children}
      </div>
    </div>
  );
};

// SaleModeBadge - Display product sale mode (dropshipping/affiliation/hybrid)
export const SaleModeBadge = ({ mode }) => {
  const config = {
    dropshipping: { color: "bg-blue-600", label: "Dropshipping" },
    affiliation: { color: "bg-purple-600", label: "Affiliation" },
    hybrid: { color: "bg-gradient-to-r from-blue-600 to-purple-600", label: "Hybride" }
  };
  const { color, label } = config[mode] || config.dropshipping;
  return <Badge className={`${color} text-white text-xs`}>{label}</Badge>;
};

// AutoCategorizeButton - AI-powered product categorization
export const AutoCategorizeButton = ({ product, onCategorized }) => {
  const [loading, setLoading] = useState(false);
  const [showDialog, setShowDialog] = useState(false);
  const [suggestion, setSuggestion] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedSubcategory, setSelectedSubcategory] = useState("");

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await axios.get(`${API}/analysis-categories`);
        setCategories(response.data.categories);
      } catch (error) {
        console.error("Error loading categories:", error);
      }
    };
    if (showDialog) loadCategories();
  }, [showDialog]);

  const handleAutoCategorize = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/admin/products/auto-categorize`, {
        product_name: product.name,
        product_description: product.description || "",
        brand: product.brand || ""
      });
      setSuggestion(response.data);
      setSelectedCategory(response.data.suggested_category);
      setSelectedSubcategory(response.data.suggested_subcategory || "");
      setShowDialog(true);
    } catch (error) {
      toast.error("Erreur lors de la catégorisation automatique");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyCategory = async () => {
    if (!selectedCategory) {
      toast.error("Veuillez sélectionner une catégorie");
      return;
    }
    try {
      await axios.put(`${API}/admin/products/${product.id}/categorize?category_id=${selectedCategory}${selectedSubcategory ? `&subcategory_id=${selectedSubcategory}` : ''}`);
      toast.success("Catégorie appliquée avec succès!");
      setShowDialog(false);
      if (onCategorized) onCategorized();
    } catch (error) {
      toast.error("Erreur lors de l'application de la catégorie");
    }
  };

  const currentCategorySubcategories = categories.find(c => c.id === selectedCategory)?.subcategories || [];
  const confidenceColors = { high: "text-green-500", medium: "text-yellow-500", low: "text-red-500" };

  return (
    <>
      <Button 
        size="icon" 
        variant="outline" 
        className="border-purple-500 text-purple-500"
        onClick={handleAutoCategorize}
        disabled={loading}
        title="Catégoriser automatiquement"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FlaskConical className="h-4 w-4" />}
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="bg-card border-border max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              Catégorisation IA
            </DialogTitle>
          </DialogHeader>
          
          {suggestion && (
            <div className="space-y-4">
              <div className="bg-background rounded-lg p-4 space-y-2">
                <p className="text-white font-medium">{product.name}</p>
                <p className="text-gray-400 text-sm">{product.brand}</p>
              </div>

              <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                <p className="text-purple-400 text-sm font-medium mb-2">Suggestion IA:</p>
                <p className="text-white">{suggestion.suggested_category_name}</p>
                {suggestion.suggested_subcategory_name && (
                  <p className="text-gray-400 text-sm">→ {suggestion.suggested_subcategory_name}</p>
                )}
                <p className={`text-sm mt-2 ${confidenceColors[suggestion.confidence]}`}>
                  Confiance: {suggestion.confidence === 'high' ? 'Élevée' : suggestion.confidence === 'medium' ? 'Moyenne' : 'Faible'}
                </p>
                <p className="text-gray-500 text-xs mt-1">{suggestion.reasoning}</p>
              </div>

              <div className="space-y-3">
                <div>
                  <Label className="text-white">Catégorie</Label>
                  <Select value={selectedCategory} onValueChange={(v) => { setSelectedCategory(v); setSelectedSubcategory(""); }}>
                    <SelectTrigger className="bg-background border-border">
                      <SelectValue placeholder="Sélectionner..." />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id}>
                          {cat.icon} {cat.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {currentCategorySubcategories.length > 0 && (
                  <div>
                    <Label className="text-white">Sous-catégorie</Label>
                    <Select value={selectedSubcategory} onValueChange={setSelectedSubcategory}>
                      <SelectTrigger className="bg-background border-border">
                        <SelectValue placeholder="Optionnel..." />
                      </SelectTrigger>
                      <SelectContent>
                        {currentCategorySubcategories.map((sub) => (
                          <SelectItem key={sub.id} value={sub.id}>
                            {sub.icon} {sub.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>Annuler</Button>
            <Button className="bg-purple-600 hover:bg-purple-700" onClick={handleApplyCategory}>
              <CheckCircle className="h-4 w-4 mr-2" />Appliquer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default SaleModeBadge;
