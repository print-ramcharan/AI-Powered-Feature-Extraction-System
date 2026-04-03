"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Upload, 
  Link as LinkIcon, 
  FileArchive, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  Download,
  AlertTriangle,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Dashboard() {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for status if a job is active
  useEffect(() => {
    let interval: any;
    if (currentJobId && jobStatus?.status !== "completed" && jobStatus?.status !== "failed") {
      interval = setInterval(async () => {
        try {
          const status = await api.getStatus(currentJobId);
          setJobStatus(status);
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [currentJobId, jobStatus?.status]);

  const handleUpload = async (file: File) => {
    if (!file.name.endsWith(".zip")) {
      setError("Please upload a ZIP file.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const { job_id } = await api.uploadZip(file);
      setCurrentJobId(job_id);
    } catch (err) {
      setError("Failed to upload file.");
      setLoading(false);
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const { job_id } = await api.processUrl(urlInput);
      setCurrentJobId(job_id);
    } catch (err) {
      setError("Failed to start processing from URL.");
      setLoading(false);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  }, []);

  return (
    <main className="min-h-screen p-8 md:p-12 lg:p-24 bg-background">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-secondary/10 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header */}
        <header className="space-y-4">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60"
          >
            AI Feature Extraction
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-lg text-white/40"
          >
            Unlock geospatial insights from your TIF + SHP archives using advanced AI processing.
          </motion.p>
        </header>

        {!currentJobId ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-8"
          >
            {/* Upload Zone */}
            <div 
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={cn(
                "glass-card p-12 text-center transition-all duration-300 relative overflow-hidden group",
                dragActive ? "border-primary bg-primary/5 scale-[1.01]" : "border-white/10 hover:border-white/20"
              )}
            >
              <div className="space-y-6 relative z-10">
                <div className="mx-auto w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Upload className="w-10 h-10 text-primary" />
                </div>
                <div>
                  <h3 className="text-2xl font-semibold mb-2">Drop your ZIP archive</h3>
                  <p className="text-white/40">Includes .tif raster and .shp feature layers</p>
                </div>
                <div className="flex items-center justify-center gap-4">
                  <label className="bg-primary hover:bg-primary/90 text-white font-medium py-3 px-8 rounded-full cursor-pointer transition-all shadow-lg shadow-primary/20">
                    Select File
                    <input type="file" className="hidden" accept=".zip" onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])} />
                  </label>
                </div>
              </div>
              
              {/* Pulse effect when drag active */}
              {dragActive && (
                <div className="absolute inset-0 bg-primary/5 animate-pulse" />
              )}
            </div>

            {/* URL Input */}
            <div className="glass-card p-8">
              <form onSubmit={handleUrlSubmit} className="flex gap-4">
                <div className="relative flex-1">
                  <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                  <input 
                    type="url"
                    placeholder="Enter URL to remote ZIP..."
                    className="w-full bg-white/5 border border-white/10 rounded-full py-4 pl-12 pr-6 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                  />
                </div>
                <button 
                  type="submit"
                  disabled={!urlInput}
                  className="bg-white/10 hover:bg-white/20 text-white font-medium py-4 px-8 rounded-full transition-all disabled:opacity-50"
                >
                  Fetch ZIP
                </button>
              </form>
            </div>
          </motion.div>
        ) : (
          /* Processing / Result State */
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-12 space-y-12"
          >
            {/* Status Header */}
            <div className="flex items-center justify-between border-b border-white/10 pb-8">
              <div className="flex items-center gap-4">
                <div className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center",
                  jobStatus?.status === "completed" ? "bg-secondary/10" : 
                  jobStatus?.status === "failed" ? "bg-destructive/10" : "bg-primary/10"
                )}>
                  {jobStatus?.status === "completed" ? <CheckCircle2 className="text-secondary w-6 h-6" /> :
                   jobStatus?.status === "failed" ? <XCircle className="text-destructive w-6 h-6" /> :
                   <Loader2 className="text-primary w-6 h-6 animate-spin" />}
                </div>
                <div>
                  <h2 className="text-2xl font-bold capitalize">{jobStatus?.status || "Initializing"}</h2>
                  <p className="text-white/40">{jobStatus?.message || "Preparing extraction..."}</p>
                </div>
              </div>
              
              {jobStatus?.status === "completed" && (
                <a 
                  href={api.getDownloadUrl(currentJobId)}
                  className="bg-secondary hover:bg-secondary/90 text-white font-bold py-4 px-10 rounded-full flex items-center gap-2 transition-all shadow-lg shadow-secondary/20"
                >
                  <Download className="w-5 h-5" />
                  Download Package
                </a>
              )}
            </div>

            {/* Progress Bar */}
            <div className="space-y-4">
              <div className="flex justify-between text-sm font-medium">
                <span className="text-white/40 uppercase tracking-widest">Job ID: {currentJobId.slice(0, 8)}...</span>
                <span className="text-primary">{jobStatus?.progress || 0}% Complete</span>
              </div>
              <div className="w-full h-3 bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  className="h-full bg-primary"
                  initial={{ width: 0 }}
                  animate={{ width: `${jobStatus?.progress || 0}%` }}
                  transition={{ type: "spring", stiffness: 50 }}
                />
              </div>
            </div>

            {/* Stats Display */}
            {jobStatus?.stats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
                <div className="glass p-6 text-center space-y-2">
                  <span className="text-xs text-white/40 uppercase font-bold tracking-tighter">Positives</span>
                  <p className="text-4xl font-black text-secondary">{jobStatus.stats.positives}</p>
                </div>
                <div className="glass p-6 text-center space-y-2">
                  <span className="text-xs text-white/40 uppercase font-bold tracking-tighter">Hard Negatives</span>
                  <p className="text-4xl font-black text-white/80">{jobStatus.stats.hard_negatives}</p>
                </div>
                <div className="glass p-6 text-center space-y-2">
                  <span className="text-xs text-white/40 uppercase font-bold tracking-tighter">Tiles Total</span>
                  <p className="text-4xl font-black text-primary">
                    {(jobStatus.stats.positives + jobStatus.stats.hard_negatives + jobStatus.stats.easy_negatives)}
                  </p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            {(jobStatus?.status === "completed" || jobStatus?.status === "failed") && (
              <div className="flex justify-center pt-8 border-t border-white/10">
                <button 
                  onClick={() => {
                    setCurrentJobId(null);
                    setJobStatus(null);
                  }}
                  className="text-white/40 hover:text-white transition-colors flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Start New Process
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Footer info */}
        <footer className="flex flex-wrap justify-center gap-x-8 gap-y-4 text-xs font-medium text-white/20 uppercase tracking-widest">
          <div className="flex items-center gap-2">
            <Info className="w-3 h-3" />
            YOLOv8 Formatting
          </div>
          <div className="flex items-center gap-2">
            <FileArchive className="w-3 h-3" />
            Rasterio & GeoPandas Powered
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-3 h-3" />
            V3.1 Engine
          </div>
        </footer>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed bottom-12 left-1/2 -translate-x-1/2 bg-destructive text-white py-4 px-8 rounded-full flex items-center gap-3 shadow-2xl z-50"
          >
            <XCircle className="w-5 h-5" />
            {error}
            <button onClick={() => setError(null)} className="ml-4 hover:scale-110 transition-transform">✕</button>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
