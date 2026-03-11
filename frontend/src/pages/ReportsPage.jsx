import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Upload, FileText, ArrowLeft, Check, AlertTriangle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

export default function ReportsPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  const [previewTitle, setPreviewTitle] = useState("");

  const fetchReports = useCallback(async () => {
    try {
      const res = await fetch(`${API}/reports/`);
      const data = await res.json();
      setReports(data.reports || []);
    } catch {
      toast.error("Impossible de charger la liste des rapports");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  const handleDownload = (slug, filename) => {
    const link = document.createElement("a");
    link.href = `${API}/reports/${slug}/download`;
    link.download = filename;
    link.click();
    toast.success("Téléchargement lancé");
  };

  const handlePreview = async (slug, title) => {
    try {
      const res = await fetch(`${API}/reports/${slug}/content`);
      const data = await res.json();
      setPreviewContent(data.content);
      setPreviewTitle(title);
    } catch {
      toast.error("Impossible de charger l'aperçu");
    }
  };

  const handleUpload = async (slug, e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.endsWith(".md")) {
      toast.error("Seuls les fichiers .md sont acceptés");
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/reports/${slug}/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error();
      toast.success("Rapport mis à jour avec succès");
      fetchReports();
      setPreviewContent(null);
    } catch {
      toast.error("Erreur lors de l'upload");
    } finally {
      setUploading(false);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} o`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} Ko`;
    return `${(bytes / 1048576).toFixed(1)} Mo`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0f1a] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white" data-testid="reports-page">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="text-white/60 hover:text-white hover:bg-white/10"
            data-testid="reports-back-btn"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-white">Rapports BIONIC V5</h1>
            <p className="text-sm text-white/50">Télécharger ou mettre à jour les documents d'analyse</p>
          </div>
        </div>

        {/* Reports list */}
        <div className="space-y-4">
          {reports.map((report) => (
            <Card key={report.slug} className="bg-[#111827] border-white/10" data-testid={`report-card-${report.slug}`}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-[#f5a623]/10">
                      <FileText className="h-5 w-5 text-[#f5a623]" />
                    </div>
                    <div>
                      <CardTitle className="text-lg text-white">{report.title}</CardTitle>
                      <CardDescription className="text-white/50">{report.description}</CardDescription>
                    </div>
                  </div>
                  {report.exists ? (
                    <span className="flex items-center gap-1 text-xs text-emerald-400">
                      <Check className="h-3 w-3" /> Disponible
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-xs text-amber-400">
                      <AlertTriangle className="h-3 w-3" /> Non créé
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-xs text-white/40">
                    {report.exists && (
                      <span>{report.filename} — {formatSize(report.size_bytes)}</span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {report.exists && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handlePreview(report.slug, report.title)}
                          className="border-white/20 text-white hover:bg-white/10"
                          data-testid={`report-preview-${report.slug}`}
                        >
                          <FileText className="h-4 w-4 mr-1" /> Aperçu
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleDownload(report.slug, report.filename)}
                          className="bg-[#f5a623] text-black hover:bg-[#f5a623]/80"
                          data-testid={`report-download-${report.slug}`}
                        >
                          <Download className="h-4 w-4 mr-1" /> Télécharger
                        </Button>
                      </>
                    )}
                    <label>
                      <input
                        type="file"
                        accept=".md"
                        className="hidden"
                        onChange={(e) => handleUpload(report.slug, e)}
                        data-testid={`report-upload-input-${report.slug}`}
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-white/20 text-white hover:bg-white/10 cursor-pointer"
                        disabled={uploading}
                        asChild
                      >
                        <span>
                          {uploading ? (
                            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <Upload className="h-4 w-4 mr-1" />
                          )}
                          Uploader
                        </span>
                      </Button>
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Preview modal */}
        {previewContent && (
          <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4" data-testid="report-preview-modal">
            <div className="bg-[#111827] border border-white/10 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b border-white/10">
                <h2 className="text-lg font-semibold text-white">{previewTitle}</h2>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setPreviewContent(null)}
                  className="text-white/60 hover:text-white"
                  data-testid="report-preview-close"
                >
                  Fermer
                </Button>
              </div>
              <div className="overflow-auto p-6 flex-1">
                <pre className="text-sm text-white/80 whitespace-pre-wrap font-mono leading-relaxed">
                  {previewContent}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
