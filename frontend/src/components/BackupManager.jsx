/**
 * BackupManager - Admin component for managing prompts and code backups
 * Features real-time versioning with Git-like history
 */

import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  Database,
  FileCode,
  History,
  Save,
  RefreshCw,
  GitBranch,
  GitCommit,
  Clock,
  Search,
  Download,
  Upload,
  Eye,
  RotateCcw,
  Trash2,
  Plus,
  Minus,
  FileText,
  Code,
  AlertTriangle,
  CheckCircle,
  Copy,
  FolderOpen
} from "lucide-react";
import { toast } from "sonner";
import { useLanguage } from '@/contexts/LanguageContext';
import PromptManager from "./PromptManager";

const API = process.env.REACT_APP_BACKEND_URL;

const BackupManager = () => {
  const { t } = useLanguage();
  const [activeSubTab, setActiveSubTab] = useState("prompts");
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Code backup state
  const [codeFiles, setCodeFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileVersions, setFileVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [showDiffModal, setShowDiffModal] = useState(false);
  const [diffData, setDiffData] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Prompt backup state
  const [promptVersions, setPromptVersions] = useState([]);
  const [selectedPromptVersion, setSelectedPromptVersion] = useState(null);
  const [showPromptVersionModal, setShowPromptVersionModal] = useState(false);

  // Helper functions
  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleString("fr-CA", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const formatBytes = (bytes) => {
    if (!bytes) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  const copyContent = (content) => {
    navigator.clipboard.writeText(typeof content === 'string' ? content : JSON.stringify(content, null, 2));
    toast.success("Contenu copié!");
  };

  // Data loading functions
  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/api/backup/stats`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error("Error loading stats:", error);
    }
    setLoading(false);
  };

  const loadCodeFiles = async () => {
    try {
      const response = await axios.get(`${API}/api/backup/code/files`);
      if (response.data.success) {
        setCodeFiles(response.data.files);
      }
    } catch (error) {
      console.error("Error loading code files:", error);
    }
  };

  const loadPromptVersions = async () => {
    try {
      const response = await axios.get(`${API}/api/backup/prompts/versions`);
      if (response.data.success) {
        setPromptVersions(response.data.versions);
      }
    } catch (error) {
      console.error("Error loading prompt versions:", error);
    }
  };

  const loadFileVersions = async (filePath) => {
    try {
      const response = await axios.get(`${API}/api/backup/code/versions/${encodeURIComponent(filePath)}`);
      if (response.data.success) {
        setFileVersions(response.data.versions);
        setSelectedFile(filePath);
      }
    } catch (error) {
      console.error("Error loading file versions:", error);
      toast.error("Erreur lors du chargement des versions");
    }
  };

  const viewVersion = async (hash, type = "code") => {
    try {
      const endpoint = type === "code" 
        ? `${API}/api/backup/code/version/${hash}`
        : `${API}/api/backup/prompts/versions/${hash}`;
      
      const response = await axios.get(endpoint);
      if (response.data.success) {
        if (type === "code") {
          setSelectedVersion(response.data.version);
          setShowVersionModal(true);
        } else {
          setSelectedPromptVersion(response.data.version);
          setShowPromptVersionModal(true);
        }
      }
    } catch (error) {
      console.error("Error loading version:", error);
      toast.error("Erreur lors du chargement de la version");
    }
  };

  const viewDiff = async (oldHash, newHash, type = "code") => {
    try {
      const endpoint = type === "code"
        ? `${API}/api/backup/code/diff/${oldHash}/${newHash}`
        : `${API}/api/backup/prompts/diff/${oldHash}/${newHash}`;
      
      const response = await axios.get(endpoint);
      if (response.data.success) {
        setDiffData(response.data);
        setShowDiffModal(true);
      }
    } catch (error) {
      console.error("Error loading diff:", error);
      toast.error("Erreur lors du chargement du diff");
    }
  };

  const scanAndBackup = async (silent = false) => {
    setScanning(true);
    try {
      const response = await axios.post(`${API}/api/backup/code/scan`);
      if (response.data.success) {
        if (!silent) {
          toast.success(`${response.data.backed_up} fichiers sauvegardés`);
        }
        await loadCodeFiles();
        await loadStats();
      }
    } catch (error) {
      console.error("Error scanning:", error);
      if (!silent) {
        toast.error("Erreur lors du scan");
      }
    }
    setScanning(false);
  };

  // Effects - after function declarations
  useEffect(() => {
    loadStats();
    loadCodeFiles();
    loadPromptVersions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeSubTab === "code") {
      const interval = setInterval(() => {
        scanAndBackup(true);
      }, 30000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSubTab]);

  const filteredCodeFiles = codeFiles.filter(file => 
    file.file_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                <FileText className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-400">
                  {stats?.prompts?.version_count || 0}
                </p>
                <p className="text-xs text-gray-400">Versions Prompts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                <FileCode className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-400">
                  {stats?.code?.file_count || 0}
                </p>
                <p className="text-xs text-gray-400">Fichiers Code</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                <GitCommit className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-green-400">
                  {stats?.code?.version_count || 0}
                </p>
                <p className="text-xs text-gray-400">Versions Code</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 border-orange-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                <Database className="h-5 w-5 text-orange-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-400">
                  {formatBytes((stats?.prompts?.storage_bytes || 0) + (stats?.code?.storage_bytes || 0))}
                </p>
                <p className="text-xs text-gray-400">Stockage Total</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sub-tabs */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-card">
          <TabsTrigger 
            value="prompts" 
            className="data-[state=active]:bg-blue-500 data-[state=active]:text-white"
            data-testid="backup-prompts-tab"
          >
            <FileText className="h-4 w-4 mr-2" />
            Prompts
          </TabsTrigger>
          <TabsTrigger 
            value="code" 
            className="data-[state=active]:bg-purple-500 data-[state=active]:text-white"
            data-testid="backup-code-tab"
          >
            <Code className="h-4 w-4 mr-2" />
            Code
          </TabsTrigger>
        </TabsList>

        {/* Prompts Tab */}
        <TabsContent value="prompts" className="space-y-4">
          <Card className="bg-card border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-400" />
                    Gestionnaire de Prompts
                  </CardTitle>
                  <CardDescription>
                    Gérez et versionnez vos prompts IA avec historique complet
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadPromptVersions}
                  className="border-blue-500/50 text-blue-400"
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Actualiser
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Prompt Manager Component */}
              <PromptManager />
              
              {/* Version History */}
              {promptVersions.length > 0 && (
                <div className="mt-6 pt-6 border-t border-border">
                  <h4 className="text-white font-medium mb-3 flex items-center gap-2">
                    <History className="h-4 w-4 text-blue-400" />
                    Historique des Versions ({promptVersions.length})
                  </h4>
                  <ScrollArea className="h-[300px]">
                    <div className="space-y-2">
                      {promptVersions.map((version, index) => (
                        <div
                          key={version.hash}
                          className="flex items-center justify-between p-3 bg-background rounded-lg border border-border hover:border-blue-500/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                              <GitCommit className="h-4 w-4 text-blue-400" />
                            </div>
                            <div>
                              <p className="text-white text-sm font-mono">
                                {version.hash}
                              </p>
                              <p className="text-gray-400 text-xs">
                                {formatDate(version.created_at)} • {version.message}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {formatBytes(version.size_bytes)}
                            </Badge>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => viewVersion(version.hash, "prompt")}
                              className="h-8 w-8 p-0"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {index < promptVersions.length - 1 && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => viewDiff(promptVersions[index + 1].hash, version.hash, "prompt")}
                                className="h-8 w-8 p-0 text-purple-400"
                              >
                                <GitBranch className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Code Tab */}
        <TabsContent value="code" className="space-y-4">
          <Card className="bg-card border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Code className="h-5 w-5 text-purple-400" />
                    Backup du Code
                  </CardTitle>
                  <CardDescription>
                    Versioning automatique des fichiers modifiés (temps réel)
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => scanAndBackup(false)}
                    disabled={scanning}
                    className="border-purple-500/50 text-purple-400"
                  >
                    {scanning ? (
                      <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4 mr-1" />
                    )}
                    Scanner
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Search */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher un fichier..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-background"
                />
              </div>

              {/* File List */}
              <ScrollArea className="h-[400px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Fichier</TableHead>
                      <TableHead>Dernière Version</TableHead>
                      <TableHead>Versions</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCodeFiles.map((file) => (
                      <TableRow
                        key={file.file_path}
                        className="cursor-pointer hover:bg-background/50"
                        onClick={() => loadFileVersions(file.file_path)}
                      >
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <FileCode className="h-4 w-4 text-purple-400" />
                            <div>
                              <p className="text-white text-sm">
                                {file.file_path.split('/').pop()}
                              </p>
                              <p className="text-gray-500 text-xs truncate max-w-[300px]">
                                {file.file_path}
                              </p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-gray-300 text-sm font-mono">
                              {file.latest_hash}
                            </p>
                            <p className="text-gray-500 text-xs">
                              {formatDate(file.latest_date)}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-purple-400">
                            {file.version_count} versions
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              viewVersion(file.latest_hash, "code");
                            }}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>

              {/* Selected File Versions */}
              {selectedFile && fileVersions.length > 0 && (
                <div className="mt-6 pt-6 border-t border-border">
                  <h4 className="text-white font-medium mb-3 flex items-center gap-2">
                    <History className="h-4 w-4 text-purple-400" />
                    Historique: {selectedFile.split('/').pop()}
                  </h4>
                  <ScrollArea className="h-[250px]">
                    <div className="space-y-2">
                      {fileVersions.map((version, index) => (
                        <div
                          key={version.hash}
                          className="flex items-center justify-between p-3 bg-background rounded-lg border border-border"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                              <GitCommit className="h-4 w-4 text-purple-400" />
                            </div>
                            <div>
                              <p className="text-white text-sm font-mono">
                                {version.hash}
                              </p>
                              <div className="flex items-center gap-2 text-xs">
                                <span className="text-gray-400">
                                  {formatDate(version.created_at)}
                                </span>
                                {version.diff_stats && (
                                  <>
                                    <span className="text-green-400">
                                      +{version.diff_stats.additions}
                                    </span>
                                    <span className="text-red-400">
                                      -{version.diff_stats.deletions}
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {version.lines} lignes
                            </Badge>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => viewVersion(version.hash, "code")}
                              className="h-8 w-8 p-0"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {index < fileVersions.length - 1 && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => viewDiff(fileVersions[index + 1].hash, version.hash, "code")}
                                className="h-8 w-8 p-0 text-purple-400"
                              >
                                <GitBranch className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Version View Modal */}
      <Dialog open={showVersionModal} onOpenChange={setShowVersionModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileCode className="h-5 w-5 text-purple-400" />
              Version: {selectedVersion?.hash}
            </DialogTitle>
            <DialogDescription>
              {selectedVersion?.file_path} • {formatDate(selectedVersion?.created_at)}
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[500px] mt-4">
            <pre className="bg-background p-4 rounded-lg text-sm text-gray-300 overflow-x-auto">
              <code>{selectedVersion?.content}</code>
            </pre>
          </ScrollArea>
          <DialogFooter>
            <Button variant="outline" onClick={() => copyContent(selectedVersion?.content)}>
              <Copy className="h-4 w-4 mr-2" />
              Copier
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Prompt Version Modal */}
      <Dialog open={showPromptVersionModal} onOpenChange={setShowPromptVersionModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-400" />
              Version Prompt: {selectedPromptVersion?.hash}
            </DialogTitle>
            <DialogDescription>
              {formatDate(selectedPromptVersion?.created_at)} • {selectedPromptVersion?.message}
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[500px] mt-4">
            <pre className="bg-background p-4 rounded-lg text-sm text-gray-300 overflow-x-auto">
              <code>{JSON.stringify(selectedPromptVersion?.content, null, 2)}</code>
            </pre>
          </ScrollArea>
          <DialogFooter>
            <Button variant="outline" onClick={() => copyContent(selectedPromptVersion?.content)}>
              <Copy className="h-4 w-4 mr-2" />
              Copier
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Diff Modal */}
      <Dialog open={showDiffModal} onOpenChange={setShowDiffModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <GitBranch className="h-5 w-5 text-purple-400" />
              Comparaison des Versions
            </DialogTitle>
            <DialogDescription>
              <span className="text-green-400">+{diffData?.additions || 0} ajouts</span>
              {" • "}
              <span className="text-red-400">-{diffData?.deletions || 0} suppressions</span>
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[500px] mt-4">
            <pre className="bg-background p-4 rounded-lg text-sm overflow-x-auto">
              {diffData?.diff?.map((line, i) => (
                <div
                  key={i}
                  className={
                    line.startsWith('+') && !line.startsWith('+++')
                      ? 'text-green-400 bg-green-500/10'
                      : line.startsWith('-') && !line.startsWith('---')
                      ? 'text-red-400 bg-red-500/10'
                      : 'text-gray-400'
                  }
                >
                  {line}
                </div>
              ))}
            </pre>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BackupManager;
