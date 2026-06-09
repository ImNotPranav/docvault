import { useState, useEffect } from "react";
import { CheckCircle2, AlertCircle, Loader2, Wifi, WifiOff } from "lucide-react";

interface OllamaStatusBannerProps {
  apiBaseUrl: string;
}

type HealthStatus = {
  status: string;
  ollama_available: boolean;
  model_loaded: boolean;
  model_name: string;
  documents_loaded: any[];
};

export default function OllamaStatusBanner({ apiBaseUrl }: OllamaStatusBannerProps) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const checkHealth = async () => {
    setLoading(true);
    setError(false);
    try {
      const response = await fetch(`${apiBaseUrl}/health`);
      if (!response.ok) throw new Error("Backend unreachable");
      const data = await response.json();
      setHealth(data);
    } catch {
      setError(true);
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    // Re-check every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [apiBaseUrl]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 mb-6 animate-fadeIn">
        <div className="bg-slate-500/10 border border-slate-500/20 rounded-xl px-4 py-3 flex items-center gap-3">
          <Loader2 className="w-4 h-4 text-slate-400 animate-spin flex-shrink-0" />
          <span className="text-sm text-slate-400">Checking system status...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 mb-6 animate-fadeIn">
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <WifiOff className="w-4 h-4 text-red-400 flex-shrink-0" />
            <div>
              <span className="text-sm text-red-300 font-medium">Backend not reachable</span>
              <p className="text-xs text-red-400/70 mt-0.5">Make sure the DocVault server is running on {apiBaseUrl}</p>
            </div>
          </div>
          <button
            onClick={checkHealth}
            className="text-xs text-red-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-red-500/20 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (health && !health.ollama_available) {
    return (
      <div className="max-w-2xl mx-auto px-4 mb-6 animate-fadeIn">
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <div>
              <span className="text-sm text-amber-300 font-medium">Ollama not detected</span>
              <p className="text-xs text-amber-400/70 mt-0.5">
                Please install and start Ollama, then run: <code className="bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-300">ollama pull {health.model_name}</code>
              </p>
            </div>
          </div>
          <button
            onClick={checkHealth}
            className="text-xs text-amber-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-amber-500/20 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (health && health.ollama_available && !health.model_loaded) {
    return (
      <div className="max-w-2xl mx-auto px-4 mb-6 animate-fadeIn">
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <div>
              <span className="text-sm text-amber-300 font-medium">Model not installed</span>
              <p className="text-xs text-amber-400/70 mt-0.5">
                Ollama is running, but the model is missing. Run: <code className="bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-300">ollama pull {health.model_name}</code>
              </p>
            </div>
          </div>
          <button
            onClick={checkHealth}
            className="text-xs text-amber-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-amber-500/20 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // All good
  return (
    <div className="max-w-2xl mx-auto px-4 mb-6 animate-fadeIn">
      <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <div className="flex items-center gap-2">
            <span className="text-sm text-emerald-300 font-medium">System ready</span>
            <span className="text-xs text-slate-500">·</span>
            <span className="text-xs text-slate-400">{health?.model_name} via Ollama</span>
            <span className="text-xs text-slate-500">·</span>
            <div className="flex items-center gap-1">
              <Wifi className="w-3 h-3 text-emerald-500" />
              <span className="text-xs text-emerald-400/70">Local only</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
