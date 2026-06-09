import { useState } from "react";
import {
  FileText, ListChecks, Calendar, XCircle, AlertTriangle,
  RefreshCw, BarChart3, TrendingUp, Search, ClipboardList,
  List, Loader2, Zap
} from "lucide-react";

interface AnalysisOption {
  type: string;
  label: string;
  icon: string;
}

interface AnalysisPanelProps {
  analyses: AnalysisOption[];
  documentType: string;
  onAnalyze: (analysisType: string) => Promise<void>;
  isAnalyzing: boolean;
  activeAnalysis: string | null;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  FileText: <FileText className="w-4 h-4" />,
  ListChecks: <ListChecks className="w-4 h-4" />,
  Calendar: <Calendar className="w-4 h-4" />,
  XCircle: <XCircle className="w-4 h-4" />,
  AlertTriangle: <AlertTriangle className="w-4 h-4" />,
  RefreshCw: <RefreshCw className="w-4 h-4" />,
  BarChart3: <BarChart3 className="w-4 h-4" />,
  TrendingUp: <TrendingUp className="w-4 h-4" />,
  Search: <Search className="w-4 h-4" />,
  ClipboardList: <ClipboardList className="w-4 h-4" />,
  List: <List className="w-4 h-4" />,
};

const DOC_TYPE_LABELS: Record<string, string> = {
  contract: "Contract Analysis",
  financial: "Financial Analysis",
  compliance: "Compliance Analysis",
  medical: "Medical Report Analysis",
  general: "Document Analysis",
};

export default function AnalysisPanel({
  analyses,
  documentType,
  onAnalyze,
  isAnalyzing,
  activeAnalysis,
}: AnalysisPanelProps) {
  if (analyses.length === 0) return null;

  return (
    <div className="animate-fadeIn">
      <div className="bg-[#12122a]/80 border border-white/10 rounded-2xl p-6 backdrop-blur-sm shadow-2xl shadow-emerald-500/5">
        {/* Header */}
        <div className="flex items-center gap-3 mb-5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Quick Analysis</h3>
            <p className="text-xs text-slate-500">
              {DOC_TYPE_LABELS[documentType] || "Document Analysis"} — click to run
            </p>
          </div>
        </div>

        {/* Analysis buttons */}
        <div className="flex flex-wrap gap-2">
          {analyses.map((analysis) => {
            const isActive = isAnalyzing && activeAnalysis === analysis.type;
            const isDisabled = isAnalyzing;

            return (
              <button
                key={analysis.type}
                onClick={() => onAnalyze(analysis.type)}
                disabled={isDisabled}
                className={`
                  group flex items-center gap-2 px-4 py-2.5 rounded-xl
                  text-sm font-medium transition-all duration-200
                  ${isActive
                    ? "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300"
                    : isDisabled
                      ? "bg-white/5 border border-white/5 text-slate-600 cursor-not-allowed"
                      : "bg-white/5 border border-white/10 text-slate-300 hover:bg-emerald-500/10 hover:border-emerald-500/30 hover:text-emerald-300 hover:shadow-lg hover:shadow-emerald-500/5 active:scale-95"
                  }
                `}
              >
                {isActive ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <span className={`transition-colors ${!isDisabled ? "text-slate-500 group-hover:text-emerald-400" : ""}`}>
                    {ICON_MAP[analysis.icon] || <FileText className="w-4 h-4" />}
                  </span>
                )}
                <span>{analysis.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
