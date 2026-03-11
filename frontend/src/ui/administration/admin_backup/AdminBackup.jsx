/**
 * AdminBackup - V5-ULTIME Administration Premium
 * ===============================================
 * 
 * Module de gestion des sauvegardes pour l'administration.
 * Fonctionnalités:
 * - Backup de code (versioning)
 * - Backup de prompts
 * - Backup de base de données
 * - Restauration
 * 
 * Phase 2 Migration - Module isolé LEGO.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Archive, Code, FileCode, Database, Search, Plus, 
  Download, Upload, Trash2, Clock, RefreshCw,
  Eye, RotateCcw, Loader2, X, CheckCircle, AlertCircle
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminBackup = () => {
  // State
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Stats state
  const [backupStats, setBackupStats] = useState(null);
  
  // Code backup state
  const [codeFiles, setCodeFiles] = useState([]);
  const [codeSearch, setCodeSearch] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileVersions, setFileVersions] = useState([]);
  const [viewingVersion, setViewingVersion] = useState(null);
  
  // Prompt backup state
  const [promptVersions, setPromptVersions] = useState([]);
  const [promptTypes, setPromptTypes] = useState([]);
  const [selectedPromptType, setSelectedPromptType] = useState('');
  const [viewingPrompt, setViewingPrompt] = useState(null);
  
  // DB backup state
  const [dbBackups, setDbBackups] = useState([]);
  const [creatingBackup, setCreatingBackup] = useState(false);

  // ============ API CALLS ============
  const fetchBackupStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/stats`);
      const data = await response.json();
      if (data.success) {
        setBackupStats(data.stats);
      }
    } catch (err) {
      setError('Erreur lors du chargement des statistiques');
    } finally {
      setLoading(false);
    }
  };

  const fetchCodeFiles = async () => {
    setLoading(true);
    try {
      const url = codeSearch 
        ? `${API_URL}/api/v1/admin/backup/code/files?search=${encodeURIComponent(codeSearch)}`
        : `${API_URL}/api/v1/admin/backup/code/files`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        setCodeFiles(data.files || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des fichiers');
    } finally {
      setLoading(false);
    }
  };

  const fetchFileVersions = async (filePath) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/code/files/${encodeURIComponent(filePath)}/versions`);
      const data = await response.json();
      if (data.success) {
        setFileVersions(data.versions || []);
        setSelectedFile(filePath);
      }
    } catch (err) {
      setError('Erreur lors du chargement des versions');
    }
  };

  const restoreVersion = async (filePath, version) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/code/restore/${encodeURIComponent(filePath)}/${version}`);
      const data = await response.json();
      if (data.success) {
        setViewingVersion(data);
        setSuccess(`Version ${version} restaurée avec succès`);
      }
    } catch (err) {
      setError('Erreur lors de la restauration');
    }
  };

  const fetchPromptVersions = async () => {
    setLoading(true);
    try {
      const url = selectedPromptType 
        ? `${API_URL}/api/v1/admin/backup/prompts?prompt_type=${selectedPromptType}`
        : `${API_URL}/api/v1/admin/backup/prompts`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.success) {
        setPromptVersions(data.versions || []);
        setPromptTypes(data.prompt_types || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des prompts');
    } finally {
      setLoading(false);
    }
  };

  const fetchPromptDetail = async (versionId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/prompts/${versionId}`);
      const data = await response.json();
      if (data.success) {
        setViewingPrompt(data.version);
      }
    } catch (err) {
      setError('Erreur lors du chargement du détail');
    }
  };

  const fetchDbBackups = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/database`);
      const data = await response.json();
      if (data.success) {
        setDbBackups(data.backups || []);
      }
    } catch (err) {
      setError('Erreur lors du chargement des backups DB');
    } finally {
      setLoading(false);
    }
  };

  const createDbBackup = async (backupType = 'manual') => {
    setCreatingBackup(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/database?backup_type=${backupType}&description=Manual backup`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Backup créé avec succès');
        fetchDbBackups();
      }
    } catch (err) {
      setError('Erreur lors de la création du backup');
    } finally {
      setCreatingBackup(false);
    }
  };

  const deleteDbBackup = async (backupId) => {
    if (!window.confirm('Supprimer ce backup ?')) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/admin/backup/database/${backupId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Backup supprimé');
        fetchDbBackups();
      }
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  // ============ EFFECTS ============
  useEffect(() => {
    if (activeTab === 'overview') fetchBackupStats();
    else if (activeTab === 'code') fetchCodeFiles();
    else if (activeTab === 'prompts') fetchPromptVersions();
    else if (activeTab === 'database') fetchDbBackups();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'code') fetchCodeFiles();
  }, [codeSearch]);

  useEffect(() => {
    if (activeTab === 'prompts') fetchPromptVersions();
  }, [selectedPromptType]);

  // Auto-clear messages
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  // ============ HELPERS ============
  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString('fr-CA');
  };

  // ============ RENDER ============
  return (
    <div data-testid="admin-backup-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Archive className="h-6 w-6 text-[#F5A623]" />
            Gestion des Backups
          </h2>
          <p className="text-gray-400 text-sm">Code, Prompts, Base de données</p>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg flex justify-between items-center">
          <span className="flex items-center gap-2"><AlertCircle className="h-4 w-4" />{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}><X className="h-4 w-4" /></Button>
        </div>
      )}
      {success && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-3 rounded-lg flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />{success}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#F5A623]/20 pb-4">
        <Button
          data-testid="backup-tab-overview"
          variant={activeTab === 'overview' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('overview')}
          className={activeTab === 'overview' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <Archive className="h-4 w-4 mr-2" />
          Vue d'ensemble
        </Button>
        <Button
          data-testid="backup-tab-code"
          variant={activeTab === 'code' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('code')}
          className={activeTab === 'code' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <Code className="h-4 w-4 mr-2" />
          Code
        </Button>
        <Button
          data-testid="backup-tab-prompts"
          variant={activeTab === 'prompts' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('prompts')}
          className={activeTab === 'prompts' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <FileCode className="h-4 w-4 mr-2" />
          Prompts
        </Button>
        <Button
          data-testid="backup-tab-database"
          variant={activeTab === 'database' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('database')}
          className={activeTab === 'database' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
        >
          <Database className="h-4 w-4 mr-2" />
          Base de données
        </Button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 text-[#F5A623] animate-spin" />
        </div>
      )}

      {/* Overview Tab */}
      {!loading && activeTab === 'overview' && backupStats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-[#0a0a15] border-[#F5A623]/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400 flex items-center gap-2">
                <Code className="h-4 w-4" />
                Fichiers Code
              </CardDescription>
              <CardTitle className="text-3xl text-white">{backupStats.code_files_tracked}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-purple-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400 flex items-center gap-2">
                <FileCode className="h-4 w-4" />
                Versions Prompts
              </CardDescription>
              <CardTitle className="text-3xl text-purple-400">{backupStats.prompt_versions}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-blue-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400 flex items-center gap-2">
                <Database className="h-4 w-4" />
                Backups DB
              </CardDescription>
              <CardTitle className="text-3xl text-blue-400">{backupStats.db_backups_count}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-[#0a0a15] border-green-500/20">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400 flex items-center gap-2">
                <Archive className="h-4 w-4" />
                Taille Totale
              </CardDescription>
              <CardTitle className="text-3xl text-green-400">{formatSize(backupStats.total_backup_size)}</CardTitle>
            </CardHeader>
          </Card>
          
          {backupStats.last_backup && (
            <Card className="col-span-full bg-[#0a0a15] border-[#F5A623]/20">
              <CardHeader>
                <CardTitle className="text-white text-lg">Dernier Backup</CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <span className="text-gray-300">{formatDate(backupStats.last_backup.created_at)}</span>
                </div>
                <Badge className={backupStats.last_backup.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
                  {backupStats.last_backup.status}
                </Badge>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Code Tab */}
      {!loading && activeTab === 'code' && (
        <div className="space-y-4">
          {/* Search */}
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Rechercher un fichier..."
                value={codeSearch}
                onChange={(e) => setCodeSearch(e.target.value)}
                className="pl-10 bg-[#050510] border-[#F5A623]/30 text-white"
              />
            </div>
            <Button onClick={fetchCodeFiles} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          {/* Files List or Versions */}
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-medium">Versions de: {selectedFile}</h3>
                <Button variant="ghost" onClick={() => { setSelectedFile(null); setFileVersions([]); }} className="text-gray-400">
                  <X className="h-4 w-4 mr-2" />
                  Fermer
                </Button>
              </div>
              
              {fileVersions.map((version) => (
                <Card key={version.id} className="bg-[#0a0a15] border-[#F5A623]/10">
                  <CardContent className="py-4 flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">Version {version.version}</p>
                      <p className="text-gray-500 text-sm">{version.commit_message}</p>
                      <p className="text-gray-600 text-xs mt-1">{formatDate(version.created_at)} • {formatSize(version.size)}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => restoreVersion(selectedFile, version.version)} className="text-[#F5A623]">
                        <RotateCcw className="h-4 w-4 mr-1" />
                        Restaurer
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {fileVersions.length === 0 && (
                <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                  <CardContent className="py-8 text-center text-gray-500">
                    Aucune version trouvée pour ce fichier.
                  </CardContent>
                </Card>
              )}

              {/* Restored Version View */}
              {viewingVersion && (
                <Card className="bg-[#0a0a15] border-green-500/20">
                  <CardHeader>
                    <CardTitle className="text-green-400 text-lg flex items-center gap-2">
                      <CheckCircle className="h-5 w-5" />
                      Contenu Restauré (v{viewingVersion.version})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-[#050510] p-4 rounded-lg text-gray-300 text-sm overflow-x-auto max-h-96">
                      {viewingVersion.content}
                    </pre>
                    <Button variant="ghost" onClick={() => setViewingVersion(null)} className="mt-4 text-gray-400">
                      Fermer
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="grid gap-3">
              {codeFiles.map((file) => (
                <Card 
                  key={file.file_path}
                  data-testid={`code-file-${file.file_path}`}
                  className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all cursor-pointer"
                  onClick={() => fetchFileVersions(file.file_path)}
                >
                  <CardContent className="py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Code className="h-5 w-5 text-[#F5A623]" />
                      <div>
                        <p className="text-white font-medium">{file.file_path}</p>
                        <p className="text-gray-500 text-sm">
                          v{file.latest_version || 1} • {file.total_versions || 1} versions • {formatSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-[#F5A623]/20 text-[#F5A623]">
                      <Eye className="h-3 w-3 mr-1" />
                      Voir
                    </Badge>
                  </CardContent>
                </Card>
              ))}
              {codeFiles.length === 0 && (
                <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                  <CardContent className="py-8 text-center text-gray-500">
                    Aucun fichier de code sauvegardé.
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {/* Prompts Tab */}
      {!loading && activeTab === 'prompts' && (
        <div className="space-y-4">
          {/* Filter by type */}
          <div className="flex gap-2 flex-wrap">
            <Button
              size="sm"
              variant={selectedPromptType === '' ? 'default' : 'ghost'}
              onClick={() => setSelectedPromptType('')}
              className={selectedPromptType === '' ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
            >
              Tous
            </Button>
            {promptTypes.map((type) => (
              <Button
                key={type}
                size="sm"
                variant={selectedPromptType === type ? 'default' : 'ghost'}
                onClick={() => setSelectedPromptType(type)}
                className={selectedPromptType === type ? 'bg-[#F5A623]/20 text-[#F5A623]' : 'text-gray-400'}
              >
                {type}
              </Button>
            ))}
          </div>

          {/* Prompt Versions List */}
          <div className="grid gap-3">
            {promptVersions.map((pv) => (
              <Card 
                key={pv.id}
                data-testid={`prompt-version-${pv.id}`}
                className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all"
              >
                <CardContent className="py-4 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <Badge className="bg-purple-500/20 text-purple-400">{pv.prompt_type}</Badge>
                      <span className="text-white font-medium">Version {pv.version}</span>
                    </div>
                    <p className="text-gray-500 text-sm mt-1">{formatDate(pv.created_at)}</p>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => fetchPromptDetail(pv.id)} className="text-[#F5A623]">
                    <Eye className="h-4 w-4 mr-1" />
                    Voir
                  </Button>
                </CardContent>
              </Card>
            ))}
            {promptVersions.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucune version de prompt sauvegardée.
                </CardContent>
              </Card>
            )}
          </div>

          {/* Viewing Prompt Detail */}
          {viewingPrompt && (
            <Card className="bg-[#0a0a15] border-purple-500/20">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-purple-400 text-lg">
                  {viewingPrompt.prompt_type} - v{viewingPrompt.version}
                </CardTitle>
                <Button variant="ghost" onClick={() => setViewingPrompt(null)} className="text-gray-400">
                  <X className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                <pre className="bg-[#050510] p-4 rounded-lg text-gray-300 text-sm overflow-x-auto max-h-96 whitespace-pre-wrap">
                  {viewingPrompt.content}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Database Tab */}
      {!loading && activeTab === 'database' && (
        <div className="space-y-4">
          {/* Actions */}
          <div className="flex gap-2">
            <Button
              data-testid="btn-create-backup"
              onClick={() => createDbBackup('manual')}
              disabled={creatingBackup}
              className="bg-[#F5A623] text-black hover:bg-[#F5A623]/80"
            >
              {creatingBackup ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Plus className="h-4 w-4 mr-2" />
              )}
              Nouveau Backup
            </Button>
            <Button onClick={fetchDbBackups} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          {/* Backups List */}
          <div className="grid gap-3">
            {dbBackups.map((backup) => (
              <Card 
                key={backup.id}
                data-testid={`db-backup-${backup.id}`}
                className="bg-[#0a0a15] border-[#F5A623]/10 hover:border-[#F5A623]/30 transition-all"
              >
                <CardContent className="py-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Database className="h-5 w-5 text-blue-400" />
                    <div>
                      <div className="flex items-center gap-3">
                        <p className="text-white font-medium">{backup.description || `Backup ${backup.backup_type}`}</p>
                        <Badge className={backup.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
                          {backup.status}
                        </Badge>
                      </div>
                      <p className="text-gray-500 text-sm mt-1">
                        {formatDate(backup.created_at)} • {backup.collections?.length || 0} collections • {formatSize(backup.size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => deleteDbBackup(backup.id)} className="text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            {dbBackups.length === 0 && (
              <Card className="bg-[#0a0a15] border-[#F5A623]/10">
                <CardContent className="py-8 text-center text-gray-500">
                  Aucun backup de base de données. Créez-en un maintenant !
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminBackup;
