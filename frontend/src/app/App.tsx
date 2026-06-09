import { useState, useEffect } from "react";
import { AlertCircle, Shield, Lock } from "lucide-react";
import Navbar from "./components/Navbar";
import PdfUploadCard from "./components/PdfUploadCard";
import QuestionInput from "./components/QuestionInput";
import { AnswerDisplay, Source } from "./components/AnswerDisplay";
import AnalysisPanel from "./components/AnalysisPanel";
import OllamaStatusBanner from "./components/OllamaStatusBanner";
import Footer from "./components/Footer";

export type UploadStatus = "idle" | "uploading" | "processing" | "ready" | "error";

type AnalysisOption = {
  type: string;
  label: string;
  icon: string;
};

type Conversation = {
  id: string;
  question: string;
  answer: string;
  timestamp: Date;
  audioFile?: string;
  sources?: Source[];
};

const API_BASE_URL = import.meta.env.VITE_BASE_API_URL || "http://localhost:8000";

export default function App() {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [fileName, setFileName] = useState<string>("");
  const [documentType, setDocumentType] = useState<string>("general");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string>("");
  const [analyses, setAnalyses] = useState<AnalysisOption[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeAnalysis, setActiveAnalysis] = useState<string | null>(null);

  // Fetch available analyses when document is ready
  useEffect(() => {
    if (uploadStatus === "ready") {
      fetchAnalyses();
    }
  }, [uploadStatus]);

  const fetchAnalyses = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/analyses`);
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data.analyses || []);
        setDocumentType(data.document_type || "general");
      }
    } catch {
      // Non-critical — just means analysis buttons won't show
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, docType: string) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setError("Please upload a PDF file");
      return;
    }

    setFileName(file.name);
    setUploadStatus("uploading");
    setError("");
    setConversations([]);
    setAnalyses([]);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", docType);

    try {
      const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload PDF");
      }

      setUploadStatus("processing");
      await new Promise((resolve) => setTimeout(resolve, 500));
      setUploadStatus("ready");
    } catch (err) {
      setUploadStatus("error");
      setError(err instanceof Error ? err.message : "Failed to upload PDF");
    }
  };

  const handleAsk = async () => {
    if (!question.trim() || uploadStatus !== "ready") return;

    setIsAsking(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), save_audio: false }),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data = await response.json();

      const newConversation: Conversation = {
        id: Date.now().toString(),
        question: data.question,
        answer: data.answer,
        timestamp: new Date(),
        audioFile: data.audio_file,
        sources: data.sources || [],
      };

      setConversations((prev) => [...prev, newConversation]);
      setQuestion("");

      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get answer");
    } finally {
      setIsAsking(false);
    }
  };

  const handleAnalyze = async (analysisType: string) => {
    if (uploadStatus !== "ready") return;

    setIsAnalyzing(true);
    setActiveAnalysis(analysisType);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_type: analysisType,
          document_type: documentType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to run analysis");
      }

      const data = await response.json();

      const analysisLabel = analyses.find((a) => a.type === analysisType)?.label || analysisType;

      const newConversation: Conversation = {
        id: Date.now().toString(),
        question: `📋 ${analysisLabel}`,
        answer: data.answer,
        timestamp: new Date(),
        sources: data.sources || [],
      };

      setConversations((prev) => [...prev, newConversation]);

      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run analysis");
    } finally {
      setIsAnalyzing(false);
      setActiveAnalysis(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex flex-col">
      <Navbar />

      {/* Ambient background glows — emerald-teal theme */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[15%] w-[500px] h-[500px] bg-emerald-600/8 rounded-full blur-[120px]" />
        <div className="absolute top-[20%] right-[10%] w-[400px] h-[400px] bg-teal-600/6 rounded-full blur-[100px]" />
        <div className="absolute bottom-[10%] left-[30%] w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-[140px]" />
      </div>

      <main className="flex-1 pt-24 pb-8">
        {/* Hero Section */}
        <section className="text-center px-4 mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-medium text-emerald-300">Privacy-First · 100% Local Processing</span>
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 tracking-tight leading-tight">
            Private Document Analysis
            <br />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-400 bg-clip-text text-transparent">
              Powered by Local AI
            </span>
          </h1>
          <p className="text-base md:text-lg text-slate-500 max-w-xl mx-auto leading-relaxed">
            Analyze contracts, financial reports, and sensitive documents.
            <br />
            <span className="inline-flex items-center gap-1 mt-1">
              <Lock className="w-3.5 h-3.5 text-emerald-500/60" />
              <span className="text-emerald-400/70 text-sm">No data ever leaves your device.</span>
            </span>
          </p>
        </section>

        {/* Ollama Status Banner */}
        <OllamaStatusBanner apiBaseUrl={API_BASE_URL} />

        {/* Error Banner */}
        {error && (
          <div className="max-w-2xl mx-auto px-4 mb-6">
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-red-300 font-medium text-sm">Error</h3>
                <p className="text-red-200/80 text-sm mt-0.5">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Section */}
        <section className="px-4 mb-12">
          <PdfUploadCard
            uploadStatus={uploadStatus}
            fileName={fileName}
            onFileUpload={handleFileUpload}
          />
        </section>

        {/* Analysis Panel — appears after document upload */}
        {uploadStatus === "ready" && analyses.length > 0 && (
          <section className="max-w-3xl mx-auto px-4 mb-6">
            <AnalysisPanel
              analyses={analyses}
              documentType={documentType}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              activeAnalysis={activeAnalysis}
            />
          </section>
        )}

        {/* Chat Section */}
        {uploadStatus !== "idle" && (
          <section className="max-w-3xl mx-auto px-4 space-y-6">
            {conversations.length > 0 && (
              <AnswerDisplay
                conversations={conversations}
                apiBaseUrl={API_BASE_URL}
                onAudioGenerated={(conversationId, audioFile) => {
                  setConversations((prev) =>
                    prev.map((conv) =>
                      conv.id === conversationId
                        ? { ...conv, audioFile }
                        : conv
                    )
                  );
                }}
              />
            )}
            <QuestionInput
              question={question}
              setQuestion={setQuestion}
              uploadStatus={uploadStatus}
              handleAsk={handleAsk}
              isAsking={isAsking}
              handleKeyPress={handleKeyPress}
            />
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}