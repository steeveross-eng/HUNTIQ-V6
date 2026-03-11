/**
 * AdminContent - V5-ULTIME Administration Premium
 * ================================================
 * 
 * Module de gestion du contenu pour l'administration.
 * Fonctionnalités:
 * - Gestion des catégories d'analyse
 * - Content Depot (SEO/Marketing)
 * - Analytics SEO
 * 
 * Phase 2 Migration - Module isolé LEGO.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  FolderTree, FileText, Search, Plus, Edit, Trash2, 
  CheckCircle, Clock, Send, BarChart3, RefreshCw,
  ArrowUp, ArrowDown, Save, X, Loader2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminContent = () => {
  // State
  const [activeTab, setActiveTab] = useState('categories');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Categories state
  const [categories, setCategories] = useState([]);
  const [editingCategory, setEditingCategory] = useState(null);
  const [newCategory, setNewCategory] = useState({ id: '', name: '', icon: '📦', order: 0 });
  const [showNewCategoryForm, setShowNewCategoryForm] = useState(false);
  
  // Content depot state
  const [contentItems, setContentItems] = useState([]);
  const [contentStats, setContentStats] = useState({});
  const [contentFilter, setContentFilter] = useState('all');
  const [newContent, setNewContent] = useState({ title: '', content_type: 'article', platform: 'website', original_content: '', keywords: [] });
  const [showNewContentForm, setShowNewContentForm] = useState(false);
  
  // SEO Analytics state
  const [seoAnalytics, setSeoAnalytics] = useState(null);

  // ============ API CALLS ============
  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/categories`);
      const data = await response.json();
      if (data.success) {
        setCategories(data.categories || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des catégories');
    } finally {
      setLoading(false);
    }
  };

  const fetchContentItems = async () => {
    setLoading(true);
    try {
      const url = contentFilter === 'all' 
        ? `${API_URL}/api/v1/admin/content/depot`
        : `${API_URL}/api/v1/admin/content/depot?status=${contentFilter}`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        setContentItems(data.items || []);
        setContentStats(data.status_counts || {});
      }
    } catch (err) {
      setError('Erreur lors du chargement du contenu');
    } finally {
      setLoading(false);
    }
  };

  const fetchSeoAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/seo-analytics`);
      const data = await response.json();
      if (data.success) {
        setSeoAnalytics(data.analytics);
      }
    } catch (err) {
      setError('Erreur lors du chargement des analytics SEO');
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCategory)
      });
      const data = await response.json();
      if (data.success) {
        setShowNewCategoryForm(false);
        setNewCategory({ id: '', name: '', icon: '📦', order: 0 });
        fetchCategories();
      } else {
        setError(data.error || 'Erreur lors de la création');
      }
    } catch (err) {
      setError('Erreur réseau');
    }
  };

  const updateCategory = async (categoryId, updates) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/categories/${categoryId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      const data = await response.json();
      if (data.success) {
        setEditingCategory(null);
        fetchCategories();
      }
    } catch (err) {
      setError('Erreur lors de la mise à jour');
    }
  };

  const deleteCategory = async (categoryId) => {
    if (!window.confirm('Supprimer cette catégorie ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/categories/${categoryId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        fetchCategories();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const initDefaultCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/categories/init-defaults`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        fetchCategories();
      }
    } catch (err) {
      setError('Erreur lors de l\'initialisation');
    }
  };

  const createContentItem = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/depot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newContent)
      });
      const data = await response.json();
      if (data.success) {
        setShowNewContentForm(false);
        setNewContent({ title: '', content_type: 'article', platform: 'website', original_content: '', keywords: [] });
        fetchContentItems();
      }
    } catch (err) {
      setError('Erreur lors de la création du contenu');
    }
  };

  const updateContentStatus = async (itemId, newStatus) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/depot/${itemId}/status?status=${newStatus}`, {
        method: 'PUT'
      });
      const data = await response.json();
      if (data.success) {
        fetchContentItems();
      }
    } catch (err) {
      setError('Erreur lors de la mise à jour du statut');
    }
  };

  const deleteContentItem = async (itemId) => {
    if (!window.confirm('Supprimer cet item ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/content/depot/${itemId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        fetchContentItems();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  // ============ EFFECTS ============
  useEffect(() => {
    if (activeTab === 'categories') fetchCategories();
    else if (activeTab === 'depot') fetchContentItems();
    else if (activeTab === 'seo') fetchSeoAnalytics();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'depot') fetchContentItems();
  }, [contentFilter]);

  // ============ HELPERS ============
  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      optimized: 'bg-blue-500/20 text-blue-400',
      accepted: 'bg-green-500/20 text-green-400',
      published: 'bg-purple-500/20 text-purple-400'
    };
    return <Badge className={styles[status] || 'bg-gray-500/20 text-gray-400'}>{status}</Badge>;
  };

  // ============ RENDER ============
  return (
    <div data-testid="admin-content-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <FolderTree className="h-6 w-6 text-[#F5A623]" />
            Gestion du Contenu
          </h2>
          <p className="text-gray-400 text-sm">Catégories, SEO, Content Depot</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#F5A623]/20 pb-4">
        <Button
          data-testid="content-tab-categories"
          variant={activeTab === 'categories' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('categories')}
          className={activeTab === 'categories' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <FolderTree className="h-4 w-4 mr-2" />
          Catégories
        </Button>
        <Button
          data-testid="content-tab-depot"
          variant={activeTab === 'depot' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('depot')}
          className={activeTab === 'depot' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <FileText className="h-4 w-4 mr-2" />
          Content Depot
        </Button>
        <Button
          data-testid="content-tab-seo"
          variant={activeTab === 'seo' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('seo')}
          className={activeTab === 'seo' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          SEO Analytics
        </Button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      )}

      {/* Tab Content */}
      {!loading && activeTab === 'categories' && (
        <div className="space-y-4">
          {/* Actions */}
          <div className="flex gap-2">
            <Button
              data-testid="btn-new-category"
              onClick={() => setShowNewCategoryForm(!showNewCategoryForm)}
              className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
            >
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle Catégorie
            </Button>
            <Button
              data-testid="btn-init-defaults"
              variant="outline"
              onClick={initDefaultCategories}
              className="border-[#F5A623]/30 text-[#F5A623] hover:bg-[#F5A623]/10"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Init. Défauts
            </Button>
          </div>

          {/* New Category Form */}
          {showNewCategoryForm && (
            <Card className="bg-[#0a0a15] border-[#F5A623]/20">
              <CardContent className="pt-4 space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <Input
                    placeholder="ID (ex: chasse)"
                    value={newCategory.id}
                    onChange={(e) => setNewCategory({ ...newCategory, id: e.target.value })}
                    className="bg-[#050510] border-[#F5A623]/30 text-white"
                  />
                  <Input
                    placeholder="Nom"
                    value={newCategory.name}
                    onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                    className="bg-[#050510] border-[#F5A623]/30 text-white"
                  />
                  <Input
                    placeholder="Icon (emoji)"
                    value={newCategory.icon}
                    onChange={(e) => setNewCategory({ ...newCategory, icon: e.target.value })}
                    className="bg-[#050510] border-[#F5A623]/30 text-white"
                  />
                  <Input
                    type="number"
                    placeholder="Ordre"
                    value={newCategory.order}
                    onChange={(e) => setNewCategory({ ...newCategory, order: parseInt(e.target.value) || 0 })}
                    className="bg-[#050510] border-[#F5A623]/30 text-white"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={createCategory} className="bg-[#F5A623] text-black">
                    <Save className="h-4 w-4 mr-2" />
                    Créer
                  </Button>
                  <Button variant="ghost" onClick={() => setShowNewCategoryForm(false)} className="text-gray-400">
                    Annuler
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Categories List */}
          <div className="grid gap-3">
            {categories.map((cat) => (
              <Card 
                key={cat.id} 
                data-testid={`category-item-${cat.id}`}
                className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all"
              >
                <CardContent className="py-4 flex items-center justify-between">
                  {editingCategory === cat.id ? (
                    <div className="flex-1 grid grid-cols-4 gap-4 mr-4">
                      <Input
                        value={cat.name}
                        onChange={(e) => setCategories(categories.map(c => c.id === cat.id ? { ...c, name: e.target.value } : c))}
                        className="bg-[#050510] border-[#F5A623]/30 text-white"
                      />
                      <Input
                        value={cat.icon}
                        onChange={(e) => setCategories(categories.map(c => c.id === cat.id ? { ...c, icon: e.target.value } : c))}
                        className="bg-[#050510] border-[#F5A623]/30 text-white"
                      />
                      <Input
                        type="number"
                        value={cat.order}
                        onChange={(e) => setCategories(categories.map(c => c.id === cat.id ? { ...c, order: parseInt(e.target.value) || 0 } : c))}
                        className="bg-[#050510] border-[#F5A623]/30 text-white"
                      />
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => updateCategory(cat.id, { name: cat.name, icon: cat.icon, order: cat.order })} className="bg-green-500 text-white">
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setEditingCategory(null)} className="text-gray-400">
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-4">
                        <span className="text-2xl">{cat.icon}</span>
                        <div>
                          <p className="text-white font-medium">{cat.name}</p>
                          <p className="text-gray-500 text-xs">ID: {cat.id} | Ordre: {cat.order}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="ghost" onClick={() => setEditingCategory(cat.id)} className="text-[#F5A623]">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => deleteCategory(cat.id)} className="text-red-400">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            ))}
            {categories.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucune catégorie. Cliquez sur "Init. Défauts" pour créer les catégories par défaut.
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {!loading && activeTab === 'depot' && (
        <div className="space-y-4">
          {/* Status Filter */}
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm">Filtrer:</span>
            {['all', 'pending', 'optimized', 'accepted', 'published'].map((status) => (
              <Button
                key={status}
                size="sm"
                variant={contentFilter === status ? 'default' : 'ghost'}
                onClick={() => setContentFilter(status)}
                className={contentFilter === status ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
              >
                {status === 'all' ? 'Tous' : status}
                {contentStats[status] !== undefined && (
                  <Badge className="ml-2 bg-white/10">{contentStats[status]}</Badge>
                )}
              </Button>
            ))}
          </div>

          {/* Actions */}
          <Button
            data-testid="btn-new-content"
            onClick={() => setShowNewContentForm(!showNewContentForm)}
            className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nouveau Contenu
          </Button>

          {/* New Content Form */}
          {showNewContentForm && (
            <Card className="bg-[#0a0a15] border-[#F5A623]/20">
              <CardContent className="pt-4 space-y-4">
                <Input
                  placeholder="Titre"
                  value={newContent.title}
                  onChange={(e) => setNewContent({ ...newContent, title: e.target.value })}
                  className="bg-[#050510] border-[#F5A623]/30 text-white"
                />
                <div className="grid grid-cols-2 gap-4">
                  <select
                    value={newContent.content_type}
                    onChange={(e) => setNewContent({ ...newContent, content_type: e.target.value })}
                    className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
                  >
                    <option value="article">Article</option>
                    <option value="blog">Blog Post</option>
                    <option value="product">Product Description</option>
                    <option value="landing">Landing Page</option>
                  </select>
                  <select
                    value={newContent.platform}
                    onChange={(e) => setNewContent({ ...newContent, platform: e.target.value })}
                    className="bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-2"
                  >
                    <option value="website">Website</option>
                    <option value="social">Social Media</option>
                    <option value="email">Email</option>
                  </select>
                </div>
                <textarea
                  placeholder="Contenu original..."
                  value={newContent.original_content}
                  onChange={(e) => setNewContent({ ...newContent, original_content: e.target.value })}
                  rows={4}
                  className="w-full bg-[#050510] border border-[#F5A623]/30 text-white rounded-md p-3"
                />
                <div className="flex gap-2">
                  <Button onClick={createContentItem} className="bg-[#F5A623] text-black">
                    <Save className="h-4 w-4 mr-2" />
                    Créer
                  </Button>
                  <Button variant="ghost" onClick={() => setShowNewContentForm(false)} className="text-gray-400">
                    Annuler
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Content Items List */}
          <div className="grid gap-3">
            {contentItems.map((item) => (
              <Card 
                key={item.id}
                data-testid={`content-item-${item.id}`}
                className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all"
              >
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-white font-medium">{item.title || 'Sans titre'}</h3>
                        {getStatusBadge(item.status)}
                        <Badge className="bg-white/10 text-gray-400">{item.content_type}</Badge>
                      </div>
                      <p className="text-gray-500 text-sm line-clamp-2">
                        {item.original_content || item.optimized_content || 'Aucun contenu'}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span>Platform: {item.platform}</span>
                        <span>SEO Score: {item.seo_score || 0}</span>
                        <span>Créé: {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}</span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2 ml-4">
                      {item.status !== 'published' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => updateContentStatus(item.id, item.status === 'pending' ? 'optimized' : item.status === 'optimized' ? 'accepted' : 'published')}
                          className="text-green-400"
                        >
                          <ArrowUp className="h-4 w-4 mr-1" />
                          Avancer
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => deleteContentItem(item.id)}
                        className="text-red-400"
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Suppr.
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {contentItems.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucun contenu dans le Depot. Créez votre premier item !
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {!loading && activeTab === 'seo' && seoAnalytics && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Total Contenu</CardDescription>
              <CardTitle className="text-3xl text-white">{seoAnalytics.total_content}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Publié</CardDescription>
              <CardTitle className="text-3xl text-green-400">{seoAnalytics.published_content}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-yellow-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">En Attente</CardDescription>
              <CardTitle className="text-3xl text-yellow-400">{seoAnalytics.pending_content}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Score SEO Moyen</CardDescription>
              <CardTitle className="text-3xl text-blue-400">{seoAnalytics.avg_seo_score}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Catégories</CardDescription>
              <CardTitle className="text-3xl text-purple-400">{seoAnalytics.categories_count}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Taux Publication</CardDescription>
              <CardTitle className="text-3xl text-[#F5A623]">{seoAnalytics.publish_rate}%</CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdminContent;
