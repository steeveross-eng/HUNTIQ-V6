/**
 * AutoCategorizeButton - Admin Module Component
 * ==============================================
 * AI-powered product categorization button.
 * Architecture LEGO V5 - Business Module (Admin)
 * 
 * @module modules/admin/components
 */
import React, { useState, useEffect } from "react";
import axios from "axios";
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
import { FlaskConical, Loader2, Sparkles, CheckCircle } from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/**
 * AutoCategorizeButton - AI-powered product categorization
 * @param {object} product - Product to categorize
 * @param {function} onCategorized - Callback after categorization
 */
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

export default AutoCategorizeButton;
