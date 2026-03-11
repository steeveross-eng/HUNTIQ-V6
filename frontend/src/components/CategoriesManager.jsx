/**
 * CategoriesManager - Admin component for managing analysis categories
 * Extracted from App.js for better maintainability
 */

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Plus, Edit, Trash2, Save, RefreshCw, ChevronRight, FlaskConical, X } from "lucide-react";
import { toast } from "sonner";
import { useLanguage } from '@/contexts/LanguageContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CategoriesManager = () => {
  const { t } = useLanguage();
  const [analysisCategories, setAnalysisCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showAddCategoryDialog, setShowAddCategoryDialog] = useState(false);
  const [showAddSubcategoryDialog, setShowAddSubcategoryDialog] = useState(false);
  const [newCategory, setNewCategory] = useState({ id: "", name: "", icon: "📦", order: 0, subcategories: [] });
  const [newSubcategory, setNewSubcategory] = useState({ id: "", name: "", icon: "📦" });
  const [editingCategory, setEditingCategory] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/analysis-categories`);
      setAnalysisCategories(response.data.categories);
    } catch (error) {
      console.error("Error loading categories:", error);
      toast.error(t('categories_load_error'));
    } finally {
      setLoading(false);
    }
  };

  const handleInitDefaults = async () => {
    try {
      await axios.post(`${API}/admin/analysis-categories/init-defaults`);
      toast.success("Catégories par défaut initialisées!");
      loadCategories();
    } catch (error) {
      toast.error("Erreur lors de l'initialisation");
    }
  };

  const handleAddCategory = async () => {
    if (!newCategory.id || !newCategory.name) {
      toast.error("Veuillez remplir l'ID et le nom");
      return;
    }
    try {
      await axios.post(`${API}/admin/analysis-categories`, newCategory);
      toast.success("Catégorie ajoutée!");
      setShowAddCategoryDialog(false);
      setNewCategory({ id: "", name: "", icon: "📦", order: 0, subcategories: [] });
      loadCategories();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de l'ajout");
    }
  };

  const handleUpdateCategory = async (categoryId) => {
    try {
      await axios.put(`${API}/admin/analysis-categories/${categoryId}`, editForm);
      toast.success("Catégorie mise à jour!");
      setEditingCategory(null);
      loadCategories();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm("Supprimer cette catégorie?")) return;
    try {
      await axios.delete(`${API}/admin/analysis-categories/${categoryId}`);
      toast.success("Catégorie supprimée!");
      loadCategories();
    } catch (error) {
      toast.error("Cette catégorie est protégée ou n'existe pas dans la base");
    }
  };

  const handleAddSubcategory = async () => {
    if (!selectedCategory || !newSubcategory.id || !newSubcategory.name) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }
    try {
      await axios.post(`${API}/admin/analysis-categories/add-subcategory/${selectedCategory.id}`, newSubcategory);
      toast.success("Sous-catégorie ajoutée!");
      setShowAddSubcategoryDialog(false);
      setNewSubcategory({ id: "", name: "", icon: "📦" });
      loadCategories();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de l'ajout");
    }
  };

  const handleDeleteSubcategory = async (categoryId, subcategoryId) => {
    if (!window.confirm("Supprimer cette sous-catégorie?")) return;
    try {
      await axios.delete(`${API}/admin/analysis-categories/${categoryId}/subcategory/${subcategoryId}`);
      toast.success("Sous-catégorie supprimée!");
      loadCategories();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Chargement des catégories...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-card border-border">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <FlaskConical className="h-5 w-5 text-[#f5a623]" /> Gestion des Catégories d'Analyse
            </CardTitle>
            <CardDescription>
              Gérez les catégories et sous-catégories affichées sous le bouton "Analysez"
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleInitDefaults}>
              <RefreshCw className="h-4 w-4 mr-2" />Réinitialiser
            </Button>
            <Button className="btn-golden text-black" onClick={() => setShowAddCategoryDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />Nouvelle catégorie
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {analysisCategories.map((category) => (
          <Card key={category.id} className="bg-card border-border">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center gap-2 text-lg">
                  <span className="text-2xl">{category.icon}</span>
                  {category.name}
                  <Badge variant="outline" className="ml-2">{category.subcategories?.length || 0} sous-cat.</Badge>
                </CardTitle>
                <div className="flex gap-1">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => {
                      setSelectedCategory(category);
                      setShowAddSubcategoryDialog(true);
                    }}
                    className="text-[#f5a623]"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => {
                      setEditingCategory(category.id);
                      setEditForm({ name: category.name, icon: category.icon, order: category.order });
                    }}
                    className="text-blue-400"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => handleDeleteCategory(category.id)}
                    className="text-red-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <p className="text-gray-500 text-xs">ID: {category.id}</p>
            </CardHeader>
            <CardContent>
              {/* Edit Category Form */}
              {editingCategory === category.id && (
                <div className="mb-4 p-3 bg-background rounded-lg space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={editForm.name || ""}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      placeholder="Nom"
                      className="flex-1 bg-card"
                    />
                    <Input
                      value={editForm.icon || ""}
                      onChange={(e) => setEditForm({...editForm, icon: e.target.value})}
                      placeholder="Emoji"
                      className="w-20 bg-card"
                    />
                    <Input
                      type="number"
                      value={editForm.order || 0}
                      onChange={(e) => setEditForm({...editForm, order: parseInt(e.target.value)})}
                      placeholder="Ordre"
                      className="w-20 bg-card"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleUpdateCategory(category.id)} className="btn-golden text-black">
                      <Save className="h-3 w-3 mr-1" />Sauvegarder
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditingCategory(null)}>Annuler</Button>
                  </div>
                </div>
              )}

              {/* Subcategories */}
              <div className="flex flex-wrap gap-2">
                {category.subcategories?.map((sub) => (
                  <div 
                    key={sub.id} 
                    className="flex items-center gap-1 px-2 py-1 bg-background rounded-full text-sm group"
                  >
                    <span>{sub.icon}</span>
                    <span className="text-white">{sub.name}</span>
                    <button
                      onClick={() => handleDeleteSubcategory(category.id, sub.id)}
                      className="ml-1 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                {(!category.subcategories || category.subcategories.length === 0) && (
                  <p className="text-gray-500 text-sm italic">Aucune sous-catégorie</p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Add Category Dialog */}
      <Dialog open={showAddCategoryDialog} onOpenChange={setShowAddCategoryDialog}>
        <DialogContent className="bg-card border-border text-white">
          <DialogHeader>
            <DialogTitle>Ajouter une catégorie</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>ID (unique, sans espaces)</Label>
              <Input 
                value={newCategory.id} 
                onChange={(e) => setNewCategory({...newCategory, id: e.target.value.toLowerCase().replace(/\s/g, '_')})}
                className="bg-background"
                placeholder="ex: nouvelle_categorie"
              />
            </div>
            <div>
              <Label>Nom affiché</Label>
              <Input 
                value={newCategory.name} 
                onChange={(e) => setNewCategory({...newCategory, name: e.target.value})}
                className="bg-background"
                placeholder="Nouvelle Catégorie"
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <Label>Emoji</Label>
                <Input 
                  value={newCategory.icon} 
                  onChange={(e) => setNewCategory({...newCategory, icon: e.target.value})}
                  className="bg-background"
                  placeholder="📦"
                />
              </div>
              <div className="w-24">
                <Label>Ordre</Label>
                <Input 
                  type="number"
                  value={newCategory.order} 
                  onChange={(e) => setNewCategory({...newCategory, order: parseInt(e.target.value)})}
                  className="bg-background"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddCategoryDialog(false)}>Annuler</Button>
            <Button className="btn-golden text-black" onClick={handleAddCategory}>Ajouter</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Subcategory Dialog */}
      <Dialog open={showAddSubcategoryDialog} onOpenChange={setShowAddSubcategoryDialog}>
        <DialogContent className="bg-card border-border text-white">
          <DialogHeader>
            <DialogTitle>Ajouter une sous-catégorie à "{selectedCategory?.name}"</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>ID (unique, sans espaces)</Label>
              <Input 
                value={newSubcategory.id} 
                onChange={(e) => setNewSubcategory({...newSubcategory, id: e.target.value.toLowerCase().replace(/\s/g, '_')})}
                className="bg-background"
                placeholder="ex: nouvelle_sous_categorie"
              />
            </div>
            <div>
              <Label>Nom affiché</Label>
              <Input 
                value={newSubcategory.name} 
                onChange={(e) => setNewSubcategory({...newSubcategory, name: e.target.value})}
                className="bg-background"
                placeholder="Nouvelle Sous-catégorie"
              />
            </div>
            <div>
              <Label>Emoji</Label>
              <Input 
                value={newSubcategory.icon} 
                onChange={(e) => setNewSubcategory({...newSubcategory, icon: e.target.value})}
                className="bg-background"
                placeholder="📦"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddSubcategoryDialog(false)}>Annuler</Button>
            <Button className="btn-golden text-black" onClick={handleAddSubcategory}>Ajouter</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CategoriesManager;
