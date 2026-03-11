/**
 * AdminCategories - V5-ULTIME Administration Premium
 * ===================================================
 * 
 * Module de gestion des catégories d'analyse.
 * Migré depuis CategoriesManager de /admin.
 * 
 * Fonctionnalités:
 * - CRUD catégories d'analyse
 * - CRUD sous-catégories
 * - Réinitialisation par défaut
 * 
 * Architecture LEGO V5 - Module isolé.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { 
  FlaskConical, Plus, Edit, Trash2, Save, RefreshCw, 
  X, FolderTree, Layers, AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const AdminCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showAddCategoryDialog, setShowAddCategoryDialog] = useState(false);
  const [showAddSubcategoryDialog, setShowAddSubcategoryDialog] = useState(false);
  const [newCategory, setNewCategory] = useState({ id: '', name: '', icon: '📦', order: 0, subcategories: [] });
  const [newSubcategory, setNewSubcategory] = useState({ id: '', name: '', icon: '📦' });
  const [editingCategory, setEditingCategory] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/analysis-categories`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error loading categories:', error);
      toast.error('Erreur lors du chargement des catégories');
    } finally {
      setLoading(false);
    }
  };

  const handleInitDefaults = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/analysis-categories/init-defaults`, {
        method: 'POST'
      });
      if (response.ok) {
        toast.success('Catégories par défaut initialisées!');
        loadCategories();
      } else {
        toast.error('Erreur lors de l\'initialisation');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'initialisation');
    }
  };

  const handleAddCategory = async () => {
    if (!newCategory.id || !newCategory.name) {
      toast.error('Veuillez remplir l\'ID et le nom');
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/admin/analysis-categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCategory)
      });
      if (response.ok) {
        toast.success('Catégorie ajoutée!');
        setShowAddCategoryDialog(false);
        setNewCategory({ id: '', name: '', icon: '📦', order: 0, subcategories: [] });
        loadCategories();
      } else {
        const err = await response.json();
        toast.error(err.detail || 'Erreur lors de l\'ajout');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleUpdateCategory = async (categoryId) => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/analysis-categories/${categoryId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm)
      });
      if (response.ok) {
        toast.success('Catégorie mise à jour!');
        setEditingCategory(null);
        loadCategories();
      } else {
        toast.error('Erreur lors de la mise à jour');
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('Supprimer cette catégorie?')) return;
    try {
      const response = await fetch(`${API_BASE}/api/admin/analysis-categories/${categoryId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        toast.success('Catégorie supprimée!');
        loadCategories();
      } else {
        toast.error('Cette catégorie est protégée ou n\'existe pas dans la base');
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleAddSubcategory = async () => {
    if (!selectedCategory || !newSubcategory.id || !newSubcategory.name) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }
    try {
      const response = await fetch(
        `${API_BASE}/api/admin/analysis-categories/add-subcategory/${selectedCategory.id}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newSubcategory)
        }
      );
      if (response.ok) {
        toast.success('Sous-catégorie ajoutée!');
        setShowAddSubcategoryDialog(false);
        setNewSubcategory({ id: '', name: '', icon: '📦' });
        loadCategories();
      } else {
        const err = await response.json();
        toast.error(err.detail || 'Erreur lors de l\'ajout');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleDeleteSubcategory = async (categoryId, subcategoryId) => {
    if (!window.confirm('Supprimer cette sous-catégorie?')) return;
    try {
      const response = await fetch(
        `${API_BASE}/api/admin/analysis-categories/${categoryId}/subcategory/${subcategoryId}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        toast.success('Sous-catégorie supprimée!');
        loadCategories();
      } else {
        toast.error('Erreur lors de la suppression');
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="admin-categories" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FlaskConical className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Catégories d'Analyse</h2>
            <p className="text-gray-400 text-sm">Gérez les catégories affichées sous le bouton "Analysez"</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={handleInitDefaults}
            className="border-[#F5A623]/30 text-[#F5A623]"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Réinitialiser
          </Button>
          <Button 
            onClick={() => setShowAddCategoryDialog(true)}
            className="bg-[#F5A623] hover:bg-[#d4891c] text-black"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle catégorie
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <FolderTree className="h-8 w-8 text-[#F5A623]" />
              <div>
                <p className="text-gray-400 text-sm">Catégories</p>
                <p className="text-2xl font-bold text-[#F5A623]">{categories.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-[#0d0d1a] border-blue-500/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Layers className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-gray-400 text-sm">Sous-catégories</p>
                <p className="text-2xl font-bold text-blue-400">
                  {categories.reduce((acc, cat) => acc + (cat.subcategories?.length || 0), 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {categories.map((category) => (
          <Card key={category.id} className="bg-[#0d0d1a] border-[#F5A623]/20 hover:border-[#F5A623]/40 transition-all">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center gap-2 text-lg">
                  <span className="text-2xl">{category.icon}</span>
                  {category.name}
                  <Badge variant="outline" className="ml-2 border-[#F5A623]/30 text-[#F5A623]">
                    {category.subcategories?.length || 0} sous-cat.
                  </Badge>
                </CardTitle>
                <div className="flex gap-1">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => {
                      setSelectedCategory(category);
                      setShowAddSubcategoryDialog(true);
                    }}
                    className="text-[#F5A623] hover:bg-[#F5A623]/10"
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
                    className="text-blue-400 hover:bg-blue-500/10"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => handleDeleteCategory(category.id)}
                    className="text-red-400 hover:bg-red-500/10"
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
                <div className="mb-4 p-3 bg-[#1a1a2e] rounded-lg space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={editForm.name || ''}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      placeholder="Nom"
                      className="flex-1 bg-[#0d0d1a] border-[#F5A623]/20"
                    />
                    <Input
                      value={editForm.icon || ''}
                      onChange={(e) => setEditForm({...editForm, icon: e.target.value})}
                      placeholder="Emoji"
                      className="w-20 bg-[#0d0d1a] border-[#F5A623]/20"
                    />
                    <Input
                      type="number"
                      value={editForm.order || 0}
                      onChange={(e) => setEditForm({...editForm, order: parseInt(e.target.value)})}
                      placeholder="Ordre"
                      className="w-20 bg-[#0d0d1a] border-[#F5A623]/20"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      onClick={() => handleUpdateCategory(category.id)} 
                      className="bg-[#F5A623] text-black hover:bg-[#d4891c]"
                    >
                      <Save className="h-3 w-3 mr-1" />
                      Sauvegarder
                    </Button>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => setEditingCategory(null)}
                      className="text-gray-400"
                    >
                      Annuler
                    </Button>
                  </div>
                </div>
              )}

              {/* Subcategories */}
              <div className="flex flex-wrap gap-2">
                {category.subcategories?.map((sub) => (
                  <div 
                    key={sub.id} 
                    className="flex items-center gap-1 px-3 py-1.5 bg-[#1a1a2e] rounded-full text-sm group border border-transparent hover:border-red-500/30 transition-all"
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

      {/* Empty State */}
      {categories.length === 0 && (
        <Card className="bg-[#0d0d1a] border-[#F5A623]/20">
          <CardContent className="p-12 text-center">
            <AlertTriangle className="h-16 w-16 text-[#F5A623]/50 mx-auto mb-4" />
            <h3 className="text-white text-lg font-semibold mb-2">Aucune catégorie</h3>
            <p className="text-gray-400 mb-4">Initialisez les catégories par défaut ou créez-en de nouvelles.</p>
            <Button onClick={handleInitDefaults} className="bg-[#F5A623] text-black">
              <RefreshCw className="h-4 w-4 mr-2" />
              Initialiser les catégories par défaut
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Category Dialog */}
      <Dialog open={showAddCategoryDialog} onOpenChange={setShowAddCategoryDialog}>
        <DialogContent className="bg-[#0d0d1a] border-[#F5A623]/20">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Plus className="h-5 w-5 text-[#F5A623]" />
              Ajouter une catégorie
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-gray-300">ID (unique, sans espaces)</Label>
              <Input 
                value={newCategory.id} 
                onChange={(e) => setNewCategory({...newCategory, id: e.target.value.toLowerCase().replace(/\s/g, '_')})}
                className="bg-[#1a1a2e] border-[#F5A623]/20"
                placeholder="ex: nouvelle_categorie"
              />
            </div>
            <div>
              <Label className="text-gray-300">Nom affiché</Label>
              <Input 
                value={newCategory.name} 
                onChange={(e) => setNewCategory({...newCategory, name: e.target.value})}
                className="bg-[#1a1a2e] border-[#F5A623]/20"
                placeholder="Nouvelle Catégorie"
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <Label className="text-gray-300">Emoji</Label>
                <Input 
                  value={newCategory.icon} 
                  onChange={(e) => setNewCategory({...newCategory, icon: e.target.value})}
                  className="bg-[#1a1a2e] border-[#F5A623]/20"
                  placeholder="📦"
                />
              </div>
              <div className="w-24">
                <Label className="text-gray-300">Ordre</Label>
                <Input 
                  type="number"
                  value={newCategory.order} 
                  onChange={(e) => setNewCategory({...newCategory, order: parseInt(e.target.value)})}
                  className="bg-[#1a1a2e] border-[#F5A623]/20"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowAddCategoryDialog(false)}
              className="border-gray-600 text-gray-400"
            >
              Annuler
            </Button>
            <Button 
              onClick={handleAddCategory}
              className="bg-[#F5A623] text-black hover:bg-[#d4891c]"
            >
              Ajouter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Subcategory Dialog */}
      <Dialog open={showAddSubcategoryDialog} onOpenChange={setShowAddSubcategoryDialog}>
        <DialogContent className="bg-[#0d0d1a] border-[#F5A623]/20">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Plus className="h-5 w-5 text-[#F5A623]" />
              Ajouter une sous-catégorie à "{selectedCategory?.name}"
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-gray-300">ID (unique, sans espaces)</Label>
              <Input 
                value={newSubcategory.id} 
                onChange={(e) => setNewSubcategory({...newSubcategory, id: e.target.value.toLowerCase().replace(/\s/g, '_')})}
                className="bg-[#1a1a2e] border-[#F5A623]/20"
                placeholder="ex: nouvelle_sous_categorie"
              />
            </div>
            <div>
              <Label className="text-gray-300">Nom affiché</Label>
              <Input 
                value={newSubcategory.name} 
                onChange={(e) => setNewSubcategory({...newSubcategory, name: e.target.value})}
                className="bg-[#1a1a2e] border-[#F5A623]/20"
                placeholder="Nouvelle Sous-catégorie"
              />
            </div>
            <div>
              <Label className="text-gray-300">Emoji</Label>
              <Input 
                value={newSubcategory.icon} 
                onChange={(e) => setNewSubcategory({...newSubcategory, icon: e.target.value})}
                className="bg-[#1a1a2e] border-[#F5A623]/20"
                placeholder="📦"
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowAddSubcategoryDialog(false)}
              className="border-gray-600 text-gray-400"
            >
              Annuler
            </Button>
            <Button 
              onClick={handleAddSubcategory}
              className="bg-[#F5A623] text-black hover:bg-[#d4891c]"
            >
              Ajouter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export { AdminCategories };
export default AdminCategories;
