/**
 * AdminSuppliers - Gestion des Fournisseurs SEO
 * =============================================
 * 
 * Module d'administration pour visualiser, filtrer
 * et gérer la liste des fournisseurs SEO.
 * 
 * Architecture LEGO V5-ULTIME
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Store, Search, Filter, ExternalLink, Globe, 
  Truck, Package, RefreshCw, Download, ChevronLeft, 
  ChevronRight, BarChart3, MapPin
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminSuppliers = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedCountry, setSelectedCountry] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    loadData();
  }, [page, selectedCategory, selectedCountry, selectedPriority]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load categories
      const catRes = await fetch(`${API}/api/v1/bionic/seo/suppliers/categories`);
      const catData = await catRes.json();
      setCategories(catData.categories || []);

      // Load stats
      const statsRes = await fetch(`${API}/api/v1/bionic/seo/suppliers/stats`);
      const statsData = await statsRes.json();
      setStats(statsData.stats);

      // Build query params
      let url = `${API}/api/v1/bionic/seo/suppliers/?page=${page}&limit=20`;
      if (selectedCategory !== 'all') url += `&category=${selectedCategory}`;
      if (selectedCountry !== 'all') url += `&country=${selectedCountry}`;
      if (selectedPriority !== 'all') url += `&priority=${selectedPriority}`;

      const suppRes = await fetch(url);
      const suppData = await suppRes.json();
      setSuppliers(suppData.suppliers || []);
      setPagination(suppData.pagination || {});
    } catch (error) {
      console.error('Error loading suppliers:', error);
      toast.error('Erreur lors du chargement');
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadData();
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/bionic/seo/suppliers/search?q=${encodeURIComponent(searchQuery)}&limit=50`);
      const data = await res.json();
      setSuppliers(data.results || []);
      setPagination({ page: 1, total: data.count, pages: 1 });
    } catch (error) {
      toast.error('Erreur de recherche');
    }
    setLoading(false);
  };

  const handleExport = async () => {
    try {
      const res = await fetch(`${API}/api/v1/bionic/seo/suppliers/export?format=csv_ready`);
      const data = await res.json();
      
      // Convert to CSV
      const headers = data.columns.join(',');
      const rows = data.data.map(row => 
        data.columns.map(col => `"${row[col] || ''}"`).join(',')
      );
      const csv = [headers, ...rows].join('\n');
      
      // Download
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'fournisseurs_seo_ultime.csv';
      a.click();
      
      toast.success('Export CSV téléchargé');
    } catch (error) {
      toast.error('Erreur d\'export');
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      high: 'bg-green-500/20 text-green-400 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      low: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    };
    return colors[priority] || colors.medium;
  };

  const getShippingBadge = (shipping) => {
    if (shipping === 'Oui') return 'bg-green-500/20 text-green-400';
    if (shipping === 'Parfois') return 'bg-yellow-500/20 text-yellow-400';
    return 'bg-red-500/20 text-red-400';
  };

  return (
    <div className="space-y-6" data-testid="admin-suppliers">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Store className="h-6 w-6 text-[#F5A623]" />
            Fournisseurs SEO
          </h2>
          <p className="text-gray-400 mt-1">
            Liste Fournisseurs Ultime - Base de données exhaustive
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={loadData}
            disabled={loading}
            className="border-[#F5A623]/30 text-[#F5A623]"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          <Button
            onClick={handleExport}
            className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
          >
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#F5A623]/20 flex items-center justify-center">
                  <Store className="h-5 w-5 text-[#F5A623]" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Total Fournisseurs</p>
                  <p className="text-2xl font-bold text-white">{stats.total_suppliers}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <Package className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Catégories</p>
                  <p className="text-2xl font-bold text-white">{stats.categories_count}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <BarChart3 className="h-5 w-5 text-green-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Priorité HIGH</p>
                  <p className="text-2xl font-bold text-white">{stats.by_priority?.high || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <MapPin className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Pays USA</p>
                  <p className="text-2xl font-bold text-white">{stats.by_country?.USA || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-[#0a0a15] border-white/10">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="text-gray-400 text-sm mb-1 block">Recherche</label>
              <div className="flex gap-2">
                <Input
                  placeholder="Nom du fournisseur..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="bg-[#050510] border-white/10"
                />
                <Button onClick={handleSearch} variant="outline" className="border-white/10">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <div className="min-w-[150px]">
              <label className="text-gray-400 text-sm mb-1 block">Catégorie</label>
              <Select value={selectedCategory} onValueChange={(v) => { setSelectedCategory(v); setPage(1); }}>
                <SelectTrigger className="bg-[#050510] border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.name} ({cat.count})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="min-w-[120px]">
              <label className="text-gray-400 text-sm mb-1 block">Pays</label>
              <Select value={selectedCountry} onValueChange={(v) => { setSelectedCountry(v); setPage(1); }}>
                <SelectTrigger className="bg-[#050510] border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="USA">USA</SelectItem>
                  <SelectItem value="Canada">Canada</SelectItem>
                  <SelectItem value="Germany">Germany</SelectItem>
                  <SelectItem value="Austria">Austria</SelectItem>
                  <SelectItem value="Italy">Italy</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="min-w-[120px]">
              <label className="text-gray-400 text-sm mb-1 block">Priorité SEO</label>
              <Select value={selectedPriority} onValueChange={(v) => { setSelectedPriority(v); setPage(1); }}>
                <SelectTrigger className="bg-[#050510] border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card className="bg-[#0a0a15] border-white/10">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="text-gray-400">Fournisseur</TableHead>
                <TableHead className="text-gray-400">Catégorie</TableHead>
                <TableHead className="text-gray-400">Pays</TableHead>
                <TableHead className="text-gray-400">Spécialités</TableHead>
                <TableHead className="text-gray-400">Livraison</TableHead>
                <TableHead className="text-gray-400">Priorité</TableHead>
                <TableHead className="text-gray-400">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {suppliers.map((supplier, idx) => (
                <TableRow key={idx} className="border-white/10 hover:bg-white/5">
                  <TableCell>
                    <div>
                      <p className="text-white font-medium">{supplier.company}</p>
                      <p className="text-gray-500 text-xs">{supplier.type}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
                      {(supplier.category || '').replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-gray-300">
                      <Globe className="h-3 w-3" />
                      {supplier.country}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {(supplier.specialty || []).slice(0, 2).map((spec, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-white/20 text-gray-400">
                          {spec}
                        </Badge>
                      ))}
                      {(supplier.specialty || []).length > 2 && (
                        <Badge variant="outline" className="text-xs border-white/20 text-gray-400">
                          +{supplier.specialty.length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getShippingBadge(supplier.free_shipping)}>
                      <Truck className="h-3 w-3 mr-1" />
                      {supplier.free_shipping}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getPriorityBadge(supplier.seo_priority)}>
                      {supplier.seo_priority?.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => window.open(supplier.official_url, '_blank')}
                      className="text-[#F5A623] hover:text-[#F5A623]/80"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-white/10">
              <p className="text-gray-400 text-sm">
                Page {pagination.page} sur {pagination.pages} ({pagination.total} fournisseurs)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="border-white/10"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
                  disabled={page === pagination.pages}
                  className="border-white/10"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminSuppliers;
