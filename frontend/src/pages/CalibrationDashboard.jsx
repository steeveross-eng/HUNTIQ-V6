/**
 * CalibrationDashboard - Dashboard de Calibration vers BIONIC V5 MASTER
 * ======================================================================
 * CALIBRATION VERS MASTER
 * 
 * Interface de suivi de la calibration pour atteindre 95%+ de précision.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { 
  Target, 
  TrendingUp, 
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  BarChart3,
  Activity,
  Lock,
  Unlock,
  RefreshCw,
  ChevronRight,
  Award,
  Zap,
  MapPin,
  Clock,
  Brain,
  Plus,
  Trash2,
  Upload,
  FileSpreadsheet,
  Download,
  CheckCircle,
  X
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// =============================================================================
// COMPOSANTS UTILITAIRES
// =============================================================================

const PrecisionGauge = ({ value, target, label, color }) => {
  const percentage = Math.min(100, (value / target) * 100);
  const isAboveTarget = value >= target;
  
  return (
    <div className="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-400">{label}</span>
        <span className={`text-lg font-bold ${isAboveTarget ? 'text-emerald-400' : 'text-amber-400'}`}>
          {value.toFixed(1)}%
        </span>
      </div>
      <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
        <div 
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
          style={{ 
            width: `${percentage}%`, 
            backgroundColor: color || (isAboveTarget ? '#00A676' : '#F59E0B')
          }}
        />
        {/* Marqueur objectif */}
        <div 
          className="absolute inset-y-0 w-0.5 bg-white/50"
          style={{ left: `${(target / 100) * 100}%` }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-slate-500">
        <span>0%</span>
        <span>Objectif: {target}%</span>
        <span>100%</span>
      </div>
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, subValue, color }) => (
  <div className="bg-slate-800/60 rounded-xl p-4 border border-slate-700">
    <div className="flex items-center gap-3">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center`} style={{ backgroundColor: `${color}20` }}>
        <Icon className="w-5 h-5" style={{ color }} />
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-xs text-slate-400">{label}</div>
        {subValue && <div className="text-xs text-slate-500">{subValue}</div>}
      </div>
    </div>
  </div>
);

// =============================================================================
// COMPOSANT PRINCIPAL
// =============================================================================

const CalibrationDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [comparisons, setComparisons] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [masterStatus, setMasterStatus] = useState(null);
  const [observations, setObservations] = useState([]);
  const [totalObservations, setTotalObservations] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showObsForm, setShowObsForm] = useState(false);
  const [obsForm, setObsForm] = useState({
    latitude: '', longitude: '', species: 'orignal',
    observed_behavior: '', observation_datetime: new Date().toISOString().slice(0, 16),
    region: 'CA-QC', notes: '', confidence: 0.8
  });
  const [showImportPanel, setShowImportPanel] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [isImporting, setIsImporting] = useState(false);

  // Charger les données
  const fetchData = useCallback(async () => {
    try {
      const [dashboardRes, comparisonsRes, suggestionsRes, masterRes, obsRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/bionic/calibration/dashboard`),
        fetch(`${API_URL}/api/v1/bionic/calibration/comparisons?limit=20`),
        fetch(`${API_URL}/api/v1/bionic/calibration/suggestions`),
        fetch(`${API_URL}/api/v1/bionic/calibration/master-status`),
        fetch(`${API_URL}/api/v1/bionic/calibration/observations?limit=20`)
      ]);

      if (dashboardRes.ok) {
        const data = await dashboardRes.json();
        setDashboardData(data.dashboard);
      }

      if (comparisonsRes.ok) {
        const data = await comparisonsRes.json();
        setComparisons(data.comparisons || []);
      }

      if (suggestionsRes.ok) {
        const data = await suggestionsRes.json();
        setSuggestions(data.suggestions || []);
      }

      if (masterRes.ok) {
        const data = await masterRes.json();
        setMasterStatus(data.master_status);
      }

      if (obsRes.ok) {
        const data = await obsRes.json();
        setObservations(data.observations || []);
        setTotalObservations(data.total || 0);
      }

      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Approuver une suggestion
  const handleApproveSuggestion = async (suggestionId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/bionic/calibration/suggestions/${suggestionId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ validated_by: 'COPILOT_MAITRE', notes: 'Approuvé via dashboard' })
      });

      if (response.ok) {
        toast.success('Suggestion approuvée');
        fetchData();
      }
    } catch (error) {
      toast.error('Erreur lors de l\'approbation');
    }
  };

  // Rejeter une suggestion
  const handleRejectSuggestion = async (suggestionId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/bionic/calibration/suggestions/${suggestionId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ validated_by: 'COPILOT_MAITRE', reason: 'Rejeté via dashboard' })
      });

      if (response.ok) {
        toast.success('Suggestion rejetée');
        fetchData();
      }
    } catch (error) {
      toast.error('Erreur lors du rejet');
    }
  };

  // Soumettre une observation terrain
  const handleSubmitObservation = async (e) => {
    e.preventDefault();
    if (!obsForm.latitude || !obsForm.longitude || !obsForm.observed_behavior) {
      toast.error('Latitude, longitude et comportement sont requis');
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/bionic/calibration/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...obsForm,
          latitude: parseFloat(obsForm.latitude),
          longitude: parseFloat(obsForm.longitude),
          observation_datetime: new Date(obsForm.observation_datetime).toISOString()
        })
      });
      if (res.ok) {
        toast.success('Observation terrain enregistrée');
        setObsForm(f => ({ ...f, latitude: '', longitude: '', observed_behavior: '', notes: '' }));
        setShowObsForm(false);
        fetchData();
      } else {
        toast.error("Erreur lors de l'enregistrement");
      }
    } catch {
      toast.error('Erreur réseau');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Supprimer une observation
  const handleDeleteObservation = async (id) => {
    try {
      const res = await fetch(`${API_URL}/api/v1/bionic/calibration/observations/${id}`, { method: 'DELETE' });
      if (res.ok) {
        toast.success('Observation supprimée');
        fetchData();
      }
    } catch {
      toast.error('Erreur de suppression');
    }
  };

  // Import CSV/Excel
  const handleFileImport = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(ext)) {
      toast.error('Format non supporté. Acceptés: .csv, .xlsx');
      return;
    }

    setIsImporting(true);
    setImportResult(null);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_URL}/api/v1/bionic/calibration/observations/import`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      setImportResult(data);

      if (data.status === 'success') {
        toast.success(`${data.imported} observations importées depuis ${file.name}`);
        fetchData();
      } else {
        toast.error(data.message || "Erreur d'import");
      }
    } catch {
      toast.error("Erreur réseau lors de l'import");
    } finally {
      setIsImporting(false);
      e.target.value = '';
    }
  };

  // Télécharger le template CSV
  const handleDownloadTemplate = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/bionic/calibration/import/template`);
      const data = await res.json();
      const csv = data.csv_example;
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'template_observations_bionic.csv';
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Template CSV téléchargé');
    } catch {
      toast.error('Erreur de téléchargement');
    }
  };

  // Verrouiller comme MASTER
  const handleLockMaster = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir verrouiller le modèle comme BIONIC V5 MASTER ? Cette action est irréversible.')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/bionic/calibration/lock-master`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        toast.success('BIONIC V5 MASTER verrouillé avec succès !');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail?.message || 'Échec du verrouillage');
      }
    } catch (error) {
      toast.error('Erreur lors du verrouillage');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
      </div>
    );
  }

  const precision = dashboardData?.precision || {};
  const statistics = dashboardData?.statistics || {};
  const bySpecies = dashboardData?.by_species || {};
  const byBehavior = dashboardData?.by_behavior || {};

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white p-4 md:p-8" data-testid="calibration-dashboard">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
              <Target className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Dashboard de Calibration</h1>
              <p className="text-slate-400 text-sm">Progression vers BIONIC V5 MASTER — Objectif: 95%+</p>
            </div>
          </div>
          <button
            onClick={fetchData}
            className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            data-testid="refresh-button"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Statut MASTER */}
        {masterStatus && (
          <div className={`rounded-xl p-6 border ${masterStatus.is_ready ? 'bg-emerald-500/10 border-emerald-500' : 'bg-amber-500/10 border-amber-500'}`} data-testid="master-status-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {masterStatus.is_ready ? (
                  <Award className="w-12 h-12 text-emerald-400" />
                ) : (
                  <TrendingUp className="w-12 h-12 text-amber-400" />
                )}
                <div>
                  <h2 className="text-xl font-bold">
                    {masterStatus.is_ready ? 'PRÊT POUR MASTER !' : 'Calibration en cours'}
                  </h2>
                  <p className="text-slate-300">
                    {masterStatus.is_ready 
                      ? `Précision actuelle: ${masterStatus.current_precision?.toFixed(1)}% — Le modèle peut être verrouillé`
                      : `Précision: ${masterStatus.current_precision?.toFixed(1)}% — Objectif: ${masterStatus.target_precision}%`}
                  </p>
                  {!masterStatus.is_ready && masterStatus.estimated_comparisons_needed > 0 && (
                    <p className="text-sm text-slate-400 mt-1">
                      ~{masterStatus.estimated_comparisons_needed} comparaisons supplémentaires estimées
                    </p>
                  )}
                </div>
              </div>
              
              {masterStatus.is_ready && !masterStatus.is_locked && (
                <button
                  onClick={handleLockMaster}
                  className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  data-testid="lock-master-button"
                >
                  <Lock className="w-5 h-5" />
                  Verrouiller MASTER
                </button>
              )}
              
              {masterStatus.is_locked && (
                <div className="flex items-center gap-2 text-emerald-400">
                  <Lock className="w-5 h-5" />
                  <span className="font-medium">MASTER VERROUILLÉ</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Jauges de précision */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <PrecisionGauge 
            value={precision.global || 0} 
            target={95} 
            label="Précision Globale"
            color={precision.global >= 95 ? '#00A676' : '#F59E0B'}
          />
          <PrecisionGauge 
            value={precision.spatial || 0} 
            target={90} 
            label="Précision Spatiale"
            color="#3B82F6"
          />
          <PrecisionGauge 
            value={precision.temporal || 0} 
            target={85} 
            label="Précision Temporelle"
            color="#8B5CF6"
          />
          <PrecisionGauge 
            value={precision.behavioral || 0} 
            target={90} 
            label="Précision Comportementale"
            color="#EC4899"
          />
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard 
            icon={BarChart3} 
            label="Comparaisons" 
            value={statistics.total_comparisons || 0}
            color="#00A676"
          />
          <StatCard 
            icon={Activity} 
            label="Cette semaine" 
            value={statistics.observations_this_week || 0}
            color="#3B82F6"
          />
          <StatCard 
            icon={Zap} 
            label="Suggestions" 
            value={dashboardData?.suggestions?.pending || 0}
            subValue="en attente"
            color="#F59E0B"
          />
          <StatCard 
            icon={Target} 
            label="Gap vers 95%" 
            value={`${(precision.gap || 0).toFixed(1)}%`}
            subValue={precision.gap <= 0 ? "Objectif atteint!" : "à combler"}
            color={precision.gap <= 0 ? '#00A676' : '#EF4444'}
          />
        </div>

        {/* Grille: Observations Terrain + Espèces */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Observations Terrain */}
          <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700" data-testid="observations-terrain-section">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <MapPin className="w-5 h-5 text-amber-400" />
                Observations Terrain
                <span className="text-xs text-slate-400 ml-1">({totalObservations})</span>
              </h3>
              <button
                onClick={() => setShowObsForm(!showObsForm)}
                className="flex items-center gap-1.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 px-3 py-1.5 rounded-lg text-sm transition-colors"
                data-testid="toggle-obs-form-btn"
              >
                <Plus className="w-4 h-4" />
                Nouvelle
              </button>
              <button
                onClick={() => setShowImportPanel(!showImportPanel)}
                className="flex items-center gap-1.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 px-3 py-1.5 rounded-lg text-sm transition-colors"
                data-testid="toggle-import-btn"
              >
                <Upload className="w-4 h-4" />
                Import
              </button>
            </div>
            
            {/* Formulaire d'observation */}
            {showObsForm && (
              <form onSubmit={handleSubmitObservation} className="mb-4 p-4 bg-slate-900/60 rounded-lg border border-slate-600 space-y-3" data-testid="observation-form">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Latitude</label>
                    <input type="number" step="any" value={obsForm.latitude}
                      onChange={e => setObsForm(f => ({ ...f, latitude: e.target.value }))}
                      placeholder="46.8139" className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-latitude" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Longitude</label>
                    <input type="number" step="any" value={obsForm.longitude}
                      onChange={e => setObsForm(f => ({ ...f, longitude: e.target.value }))}
                      placeholder="-71.2080" className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-longitude" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Espèce</label>
                    <select value={obsForm.species}
                      onChange={e => setObsForm(f => ({ ...f, species: e.target.value }))}
                      className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-species">
                      {['orignal', 'cerf_de_virginie', 'ours_noir', 'caribou', 'wapiti'].map(s => (
                        <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Comportement</label>
                    <select value={obsForm.observed_behavior}
                      onChange={e => setObsForm(f => ({ ...f, observed_behavior: e.target.value }))}
                      className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-behavior">
                      <option value="">Sélectionner</option>
                      {['alimentation', 'déplacement', 'repos', 'rut', 'allaitement', 'fuite', 'abreuvement', 'ravage'].map(b => (
                        <option key={b} value={b}>{b}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Date/heure</label>
                    <input type="datetime-local" value={obsForm.observation_datetime}
                      onChange={e => setObsForm(f => ({ ...f, observation_datetime: e.target.value }))}
                      className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-datetime" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Notes</label>
                    <input type="text" value={obsForm.notes}
                      onChange={e => setObsForm(f => ({ ...f, notes: e.target.value }))}
                      placeholder="Description..." className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1.5 text-sm text-white" data-testid="obs-notes" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>Confiance: {(obsForm.confidence * 100).toFixed(0)}%</span>
                    <input type="range" min="0.1" max="1" step="0.1" value={obsForm.confidence}
                      onChange={e => setObsForm(f => ({ ...f, confidence: parseFloat(e.target.value) }))}
                      className="w-24 accent-amber-400" data-testid="obs-confidence" />
                  </div>
                  <button type="submit" disabled={isSubmitting}
                    className="flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 text-black px-4 py-1.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                    data-testid="obs-submit-btn">
                    <Plus className="w-3.5 h-3.5" />
                    {isSubmitting ? 'Envoi...' : 'Enregistrer'}
                  </button>
                </div>
              </form>
            )}
            
            {/* Panneau d'import CSV/Excel */}
            {showImportPanel && (
              <div className="mb-4 p-4 bg-slate-900/60 rounded-lg border border-blue-500/30 space-y-3" data-testid="import-panel">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-medium text-white">Import CSV / Excel</span>
                  </div>
                  <button
                    onClick={handleDownloadTemplate}
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-blue-400 transition-colors"
                    data-testid="download-template-btn"
                  >
                    <Download className="w-3 h-3" />
                    Template CSV
                  </button>
                  <a
                    href="/canvas_donnees_terrain_bionic_v5.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-emerald-400 transition-colors"
                    data-testid="canvas-terrain-link"
                  >
                    <FileSpreadsheet className="w-3 h-3" />
                    Canvas terrain
                  </a>
                </div>

                {/* Zone d'upload */}
                <label
                  className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-600 hover:border-blue-500/50 rounded-lg cursor-pointer transition-colors"
                  data-testid="file-upload-zone"
                >
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileImport}
                    className="hidden"
                    disabled={isImporting}
                    data-testid="file-input"
                  />
                  {isImporting ? (
                    <div className="flex items-center gap-2 text-blue-400">
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span className="text-sm">Import en cours...</span>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-6 h-6 text-slate-500 mb-1" />
                      <span className="text-xs text-slate-400">Glissez ou cliquez pour importer</span>
                      <span className="text-[10px] text-slate-500 mt-0.5">.csv, .xlsx — Max 10 MB, 5000 lignes</span>
                    </>
                  )}
                </label>

                {/* Colonnes requises */}
                <div className="text-[10px] text-slate-500">
                  <span className="font-medium text-slate-400">Colonnes requises:</span>{' '}
                  latitude, longitude, species, observed_behavior, observation_datetime
                </div>

                {/* Résultat d'import */}
                {importResult && (
                  <div className={`p-3 rounded-lg border ${importResult.status === 'success' ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`} data-testid="import-result">
                    <div className="flex items-center gap-2 mb-1">
                      {importResult.status === 'success' ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-red-400" />
                      )}
                      <span className={`text-sm font-medium ${importResult.status === 'success' ? 'text-emerald-400' : 'text-red-400'}`}>
                        {importResult.status === 'success'
                          ? `${importResult.imported} observations importées`
                          : importResult.message}
                      </span>
                    </div>
                    {importResult.batch_id && (
                      <div className="text-[10px] text-slate-500 font-mono">
                        Batch: {importResult.batch_id}
                      </div>
                    )}
                    {importResult.errors_count > 0 && (
                      <div className="mt-2 text-xs text-amber-400">
                        {importResult.errors_count} erreur(s):
                        <ul className="mt-1 text-[10px] text-slate-400 space-y-0.5 max-h-24 overflow-y-auto">
                          {importResult.errors.slice(0, 10).map((err, i) => (
                            <li key={i}>- {err}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
            
            {/* Liste des observations */}
            {observations.length > 0 ? (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {observations.map(obs => (
                  <div key={obs.observation_id} className="flex items-center gap-2 p-2.5 bg-slate-900/60 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors" data-testid={`obs-row-${obs.observation_id}`}>
                    <MapPin className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm text-white capitalize">{obs.species?.replace(/_/g, ' ')}</span>
                        <span className="text-xs text-slate-500">•</span>
                        <span className="text-xs text-slate-400 capitalize">{obs.observed_behavior}</span>
                      </div>
                      <div className="text-xs text-slate-500 font-mono">
                        {obs.latitude?.toFixed(4)}, {obs.longitude?.toFixed(4)} — {new Date(obs.observation_datetime).toLocaleDateString('fr-CA')}
                      </div>
                    </div>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${obs.status === 'compared' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                      {obs.status === 'compared' ? 'Comparée' : 'En attente'}
                    </span>
                    <button onClick={() => handleDeleteObservation(obs.observation_id)}
                      className="p-1 text-slate-500 hover:text-red-400 transition-colors"
                      data-testid={`delete-obs-${obs.observation_id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm text-center py-6">
                Aucune observation. Cliquez "Nouvelle" pour commencer la collecte terrain.
              </p>
            )}
          </div>

          {/* Précision par espèce */}
          <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-400" />
              Précision par Espèce
            </h3>
            {Object.keys(bySpecies).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(bySpecies).map(([species, value]) => (
                  <div key={species} className="flex items-center justify-between">
                    <span className="text-slate-300 capitalize">{species}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all"
                          style={{ 
                            width: `${value}%`, 
                            backgroundColor: value >= 90 ? '#00A676' : value >= 70 ? '#F59E0B' : '#EF4444'
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{value.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">Aucune donnée par espèce disponible</p>
            )}
          </div>

          {/* Précision par comportement */}
          <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              Précision par Comportement
            </h3>
            {Object.keys(byBehavior).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(byBehavior).map(([behavior, value]) => (
                  <div key={behavior} className="flex items-center justify-between">
                    <span className="text-slate-300 capitalize">{behavior}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all"
                          style={{ 
                            width: `${value}%`, 
                            backgroundColor: value >= 90 ? '#00A676' : value >= 70 ? '#F59E0B' : '#EF4444'
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{value.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">Aucune donnée par comportement disponible</p>
            )}
          </div>
        </div>

        {/* Suggestions en attente */}
        {suggestions.filter(s => s.status === 'pending').length > 0 && (
          <div className="bg-slate-800/60 rounded-xl p-6 border border-amber-500/50">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Suggestions en Attente de Validation
            </h3>
            <div className="space-y-4">
              {suggestions.filter(s => s.status === 'pending').map((suggestion) => (
                <div key={suggestion.suggestion_id} className="bg-slate-900/60 rounded-lg p-4 border border-slate-700" data-testid={`suggestion-${suggestion.suggestion_id}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded">
                          {suggestion.adjustment_type}
                        </span>
                        <span className="text-sm text-slate-400">
                          {suggestion.parameter?.category} / {suggestion.parameter?.name}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300 mb-2">{suggestion.analysis?.justification}</p>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span>Actuel: {suggestion.parameter?.current_value?.toFixed(3)}</span>
                        <ChevronRight className="w-4 h-4" />
                        <span className="text-emerald-400">Suggéré: {suggestion.parameter?.suggested_value?.toFixed(3)}</span>
                        <span>Impact estimé: +{suggestion.analysis?.expected_impact?.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => handleApproveSuggestion(suggestion.suggestion_id)}
                        className="p-2 bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-400 rounded-lg transition-colors"
                        data-testid={`approve-${suggestion.suggestion_id}`}
                      >
                        <CheckCircle2 className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleRejectSuggestion(suggestion.suggestion_id)}
                        className="p-2 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg transition-colors"
                        data-testid={`reject-${suggestion.suggestion_id}`}
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Historique des comparaisons récentes */}
        <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Comparaisons Récentes
          </h3>
          {comparisons.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-700">
                    <th className="text-left py-2 px-2">ID</th>
                    <th className="text-left py-2 px-2">Espèce</th>
                    <th className="text-left py-2 px-2">Comportement</th>
                    <th className="text-right py-2 px-2">Erreur Spatiale</th>
                    <th className="text-right py-2 px-2">Erreur Temporelle</th>
                    <th className="text-right py-2 px-2">Concordance</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisons.slice(0, 10).map((comparison) => (
                    <tr key={comparison.comparison_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                      <td className="py-2 px-2 text-slate-400 font-mono text-xs">{comparison.comparison_id}</td>
                      <td className="py-2 px-2 capitalize">{comparison.context?.species || '-'}</td>
                      <td className="py-2 px-2 capitalize">
                        {comparison.errors?.behavior_match ? (
                          <span className="text-emerald-400">{comparison.observation?.behavior}</span>
                        ) : (
                          <span className="text-red-400">{comparison.observation?.behavior}</span>
                        )}
                      </td>
                      <td className="py-2 px-2 text-right">{comparison.errors?.spatial_m?.toFixed(0)}m</td>
                      <td className="py-2 px-2 text-right">{comparison.errors?.temporal_min?.toFixed(0)}min</td>
                      <td className="py-2 px-2 text-right">
                        <span className={`font-medium ${comparison.concordance?.global >= 90 ? 'text-emerald-400' : comparison.concordance?.global >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
                          {comparison.concordance?.global?.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-slate-500 text-sm text-center py-8">
              Aucune comparaison enregistrée. Utilisez l'interface d'observations pour commencer la calibration.
            </p>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-8 text-center text-xs text-slate-500">
        <p>CALIBRATION VERS MASTER — BIONIC V5</p>
        <p>Objectif: ≥95% de précision pour verrouiller la version MASTER</p>
      </div>
    </div>
  );
};

export default CalibrationDashboard;
