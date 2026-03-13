/**
 * AdminHotspots — Section ADMIN pour les Hotspots BIONIC V3
 * Carte consolidee + Tableau des scores + Filtres + Export
 */
import React, { useState, useCallback } from 'react';
import { MapPin, Download, RefreshCw, Filter, ChevronDown, Shield, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API = process.env.REACT_APP_BACKEND_URL;
const HOTSPOT_API = `${API}/api/v1/admin/bionic-hotspots`;

const CLASSIFICATION_STYLES = {
  MAJEUR: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' },
  FORT: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30' },
  MODERE: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
};

const AdminHotspots = () => {
  const [hotspots, setHotspots] = useState([]);
  const [stats, setStats] = useState(null);
  const [bceReport, setBceReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractionSummary, setExtractionSummary] = useState(null);
  const [filters, setFilters] = useState({ region_id: '', species: '', category: '', classification: '' });
  const [showFilters, setShowFilters] = useState(false);

  const fetchList = useCallback(async () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    params.set('limit', '200');
    try {
      const res = await fetch(`${HOTSPOT_API}/list?${params}`);
      const data = await res.json();
      setHotspots(data.hotspots || []);
    } catch (e) {
      console.error('Fetch list failed:', e);
    }
  }, [filters]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${HOTSPOT_API}/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error('Fetch stats failed:', e);
    }
  }, []);

  const extractAll = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${HOTSPOT_API}/extract`, { method: 'POST' });
      const data = await res.json();
      setExtractionSummary(data);
      await fetchList();
      await fetchStats();
    } catch (e) {
      console.error('Extraction failed:', e);
    } finally {
      setLoading(false);
    }
  }, [fetchList, fetchStats]);

  const fetchBceReport = useCallback(async () => {
    try {
      const res = await fetch(`${HOTSPOT_API}/report/bce4x`);
      const data = await res.json();
      setBceReport(data);
    } catch (e) {
      console.error('Fetch BCE report failed:', e);
    }
  }, []);

  const exportGeoJSON = useCallback(async () => {
    try {
      const res = await fetch(`${HOTSPOT_API}/export/geojson`);
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `hotspots_bionic_v3_${new Date().toISOString().slice(0, 10)}.geojson`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
    }
  }, []);

  const exportJSON = useCallback(async () => {
    try {
      const res = await fetch(`${HOTSPOT_API}/export/json`);
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `hotspots_bionic_v3_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
    }
  }, []);

  return (
    <div className="space-y-6" data-testid="admin-hotspots-section">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="h-5 w-5 text-[#f5a623]" />
            Hotspots BIONIC V3
          </h2>
          <p className="text-sm text-gray-400 mt-1">Extraction et scoring des hotspots de chasse par region</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={extractAll} disabled={loading} className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-bold" data-testid="extract-all-btn">
            {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
            {loading ? 'Extraction...' : 'Extraire toutes les regions'}
          </Button>
        </div>
      </div>

      {/* Extraction Summary */}
      {extractionSummary && (
        <div className="bg-gray-900/50 border border-[#f5a623]/20 rounded-xl p-4" data-testid="extraction-summary">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-bold text-[#f5a623]">Derniere extraction</span>
            <span className="text-[10px] text-gray-500 font-mono">{extractionSummary.extracted_at}</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-black text-white" data-testid="total-hotspots">{extractionSummary.total_hotspots}</div>
              <div className="text-[10px] text-gray-400">Hotspots totaux</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-black text-[#f5a623]">{extractionSummary.total_regions}</div>
              <div className="text-[10px] text-gray-400">Regions couvertes</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-black text-red-400">{extractionSummary.regions_summary?.reduce((a, r) => a + (r.by_classification?.MAJEUR || 0), 0) || 0}</div>
              <div className="text-[10px] text-gray-400">Hotspots MAJEURS</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-black text-orange-400">{extractionSummary.regions_summary?.reduce((a, r) => a + (r.by_classification?.FORT || 0), 0) || 0}</div>
              <div className="text-[10px] text-gray-400">Hotspots FORTS</div>
            </div>
          </div>
          <div className="mt-3 space-y-1 max-h-40 overflow-y-auto">
            {extractionSummary.regions_summary?.map(r => (
              <div key={r.region_id} className="flex items-center justify-between text-xs bg-black/20 rounded px-3 py-1.5">
                <span className="text-gray-300">{r.region_name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-white font-bold">{r.hotspots_count}</span>
                  {Object.entries(r.by_species || {}).map(([sp, count]) => (
                    <span key={sp} className="text-[10px] text-gray-500">{sp}: {count}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      {stats && stats.total_hotspots > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="hotspot-stats">
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Score moyen</div>
            <div className="text-xl font-bold text-white">{stats.score_avg}</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Score max</div>
            <div className="text-xl font-bold text-green-400">{stats.score_max}</div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Par espece</div>
            <div className="space-y-0.5">
              {Object.entries(stats.by_species || {}).slice(0, 4).map(([sp, cnt]) => (
                <div key={sp} className="flex justify-between text-[10px]"><span className="text-gray-400">{sp}</span><span className="text-white font-bold">{cnt}</span></div>
              ))}
            </div>
          </div>
          <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-3">
            <div className="text-[10px] text-gray-500 uppercase mb-1">Par categorie</div>
            <div className="space-y-0.5">
              {Object.entries(stats.by_category || {}).slice(0, 4).map(([cat, cnt]) => (
                <div key={cat} className="flex justify-between text-[10px]"><span className="text-gray-400">{cat}</span><span className="text-white font-bold">{cnt}</span></div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 flex-wrap">
        <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} className="border-gray-700 text-gray-300 hover:text-white" data-testid="toggle-filters-btn">
          <Filter className="h-3.5 w-3.5 mr-1.5" /> Filtres <ChevronDown className={`h-3 w-3 ml-1 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </Button>
        <Button variant="outline" size="sm" onClick={exportGeoJSON} className="border-gray-700 text-gray-300 hover:text-white" data-testid="export-geojson-btn">
          <Download className="h-3.5 w-3.5 mr-1.5" /> GeoJSON
        </Button>
        <Button variant="outline" size="sm" onClick={exportJSON} className="border-gray-700 text-gray-300 hover:text-white" data-testid="export-json-btn">
          <Download className="h-3.5 w-3.5 mr-1.5" /> JSON
        </Button>
        <Button variant="outline" size="sm" onClick={fetchBceReport} className="border-gray-700 text-gray-300 hover:text-white" data-testid="bce-report-btn">
          <Shield className="h-3.5 w-3.5 mr-1.5" /> Rapport BCE-4X
        </Button>
        <Button variant="outline" size="sm" onClick={fetchStats} className="border-gray-700 text-gray-300 hover:text-white">
          <BarChart3 className="h-3.5 w-3.5 mr-1.5" /> Stats
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-900/50 border border-gray-700/30 rounded-lg p-4 grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="filters-panel">
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Region</label>
            <select value={filters.region_id} onChange={e => setFilters(p => ({ ...p, region_id: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              {['laurentides','outaouais','lanaudiere','mauricie','estrie','saguenay','capitale_nationale','chaudiere_appalaches','bas_saint_laurent','abitibi','cote_nord','gaspesie'].map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Espece</label>
            <select value={filters.species} onChange={e => setFilters(p => ({ ...p, species: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              <option value="orignal">Orignal</option>
              <option value="chevreuil">Chevreuil</option>
              <option value="ours_noir">Ours noir</option>
              <option value="dindon_sauvage">Dindon sauvage</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Categorie</label>
            <select value={filters.category} onChange={e => setFilters(p => ({ ...p, category: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              {['alimentation','repos','rut','deplacement','corridors','multi_engines','pression_faible'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-gray-500 uppercase block mb-1">Classification</label>
            <select value={filters.classification} onChange={e => setFilters(p => ({ ...p, classification: e.target.value }))} className="w-full bg-black border border-gray-700 rounded px-2 py-1.5 text-xs text-white">
              <option value="">Toutes</option>
              <option value="MAJEUR">MAJEUR (80+)</option>
              <option value="FORT">FORT (60-79)</option>
            </select>
          </div>
          <Button size="sm" onClick={fetchList} className="bg-[#f5a623] text-black font-bold col-span-2 md:col-span-4" data-testid="apply-filters-btn">Appliquer les filtres</Button>
        </div>
      )}

      {/* BCE-4X Report */}
      {bceReport && (
        <div className={`border rounded-lg p-4 ${bceReport.overall === 'PASS' ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`} data-testid="bce-report-panel">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-bold text-white flex items-center gap-2">
              <Shield className={`h-4 w-4 ${bceReport.overall === 'PASS' ? 'text-green-400' : 'text-red-400'}`} />
              Rapport BCE-4X
            </span>
            <Badge className={bceReport.overall === 'PASS' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}>{bceReport.overall}</Badge>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div><div className="text-lg font-bold text-white">{bceReport.total_checks}</div><div className="text-[10px] text-gray-500">Total</div></div>
            <div><div className="text-lg font-bold text-green-400">{bceReport.passed}</div><div className="text-[10px] text-gray-500">Passes</div></div>
            <div><div className="text-lg font-bold text-red-400">{bceReport.failed}</div><div className="text-[10px] text-gray-500">Echoues</div></div>
          </div>
        </div>
      )}

      {/* Hotspots Table */}
      {hotspots.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-700/30 rounded-xl overflow-hidden" data-testid="hotspots-table">
          <div className="px-4 py-3 border-b border-gray-800">
            <span className="text-sm font-bold text-white">{hotspots.length} hotspots</span>
          </div>
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="bg-black/50 sticky top-0">
                <tr className="text-gray-500 uppercase tracking-wider">
                  <th className="px-3 py-2 text-left">ID</th>
                  <th className="px-3 py-2 text-left">Region</th>
                  <th className="px-3 py-2 text-center">Score</th>
                  <th className="px-3 py-2 text-center">Classification</th>
                  <th className="px-3 py-2 text-left">Categorie</th>
                  <th className="px-3 py-2 text-left">Espece</th>
                  <th className="px-3 py-2 text-center">Accessibilite</th>
                  <th className="px-3 py-2 text-left">Coordonnees</th>
                </tr>
              </thead>
              <tbody>
                {hotspots.map(h => {
                  const cls = CLASSIFICATION_STYLES[h.classification] || CLASSIFICATION_STYLES.FORT;
                  return (
                    <tr key={h.id} className="border-t border-gray-800/50 hover:bg-white/5 transition-colors">
                      <td className="px-3 py-2 font-mono text-gray-400">{h.id}</td>
                      <td className="px-3 py-2 text-gray-300">{h.region_name}</td>
                      <td className="px-3 py-2 text-center"><span className="text-white font-bold">{h.score}</span></td>
                      <td className="px-3 py-2 text-center"><Badge className={`${cls.bg} ${cls.text} border ${cls.border} text-[9px]`}>{h.classification}</Badge></td>
                      <td className="px-3 py-2 text-gray-300">{h.category}</td>
                      <td className="px-3 py-2 text-amber-400">{h.dominant_species}</td>
                      <td className="px-3 py-2 text-center text-gray-300">{h.accessibility}%</td>
                      <td className="px-3 py-2 font-mono text-[10px] text-gray-500">{h.center?.[0]?.toFixed(4)}, {h.center?.[1]?.toFixed(4)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {hotspots.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500" data-testid="empty-state">
          <MapPin className="h-12 w-12 mx-auto mb-3 text-gray-700" />
          <p className="text-sm">Aucun hotspot extrait. Cliquez sur "Extraire toutes les regions" pour commencer.</p>
        </div>
      )}
    </div>
  );
};

export default AdminHotspots;
