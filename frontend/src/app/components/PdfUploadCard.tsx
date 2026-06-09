import { Upload, Loader2, CheckCircle2, AlertCircle, FileUp, Lock, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { UploadStatus } from "../App";

interface PdfUploadCardProps {
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>, documentType: string) => Promise<void>;
  uploadStatus: UploadStatus;
  fileName?: string;
}

const DOCUMENT_TYPES = [
  { value: "general", label: "General Document", description: "Any document type" },
  { value: "contract", label: "Legal Contract", description: "Agreements, NDAs, SLAs" },
  { value: "financial", label: "Financial Report", description: "Annual reports, statements" },
  { value: "compliance", label: "Compliance Document", description: "Regulatory, audit reports" },
  { value: "medical", label: "Medical Report", description: "Lab results, clinical reports" },
];

export default function PdfUploadCard({ onFileUpload, uploadStatus, fileName }: PdfUploadCardProps) {
  const [documentType, setDocumentType] = useState("general");
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);

  const selectedType = DOCUMENT_TYPES.find((t) => t.value === documentType)!;

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-[#12122a]/80 border border-white/10 rounded-2xl p-8 backdrop-blur-sm shadow-2xl shadow-emerald-500/5">
        {/* Document Type Selector */}
        {(uploadStatus === "idle" || uploadStatus === "error") && (
          <div className="mb-6">
            <label className="text-xs font-medium text-slate-400 mb-2 block">Document Type</label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowTypeDropdown(!showTypeDropdown)}
                className="w-full flex items-center justify-between px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-left hover:border-emerald-500/30 transition-colors"
              >
                <div>
                  <span className="text-sm text-white font-medium">{selectedType.label}</span>
                  <span className="text-xs text-slate-500 ml-2">— {selectedType.description}</span>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${showTypeDropdown ? "rotate-180" : ""}`} />
              </button>

              {showTypeDropdown && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-[#1a1a35] border border-white/10 rounded-xl overflow-hidden shadow-2xl z-10">
                  {DOCUMENT_TYPES.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => {
                        setDocumentType(type.value);
                        setShowTypeDropdown(false);
                      }}
                      className={`w-full px-4 py-3 text-left hover:bg-white/5 transition-colors flex items-center justify-between ${
                        documentType === type.value ? "bg-emerald-500/10" : ""
                      }`}
                    >
                      <div>
                        <span className="text-sm text-white font-medium">{type.label}</span>
                        <span className="text-xs text-slate-500 ml-2">— {type.description}</span>
                      </div>
                      {documentType === type.value && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload area */}
        <label
          htmlFor="pdf-upload"
          className={`group block border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-300 ${uploadStatus === "idle"
            ? "border-slate-700/60 hover:border-emerald-500/60 hover:bg-emerald-500/5"
            : uploadStatus === "error"
              ? "border-red-500/40 bg-red-500/5"
              : "border-emerald-500/40 bg-emerald-500/5"
            }`}
        >
          <input
            id="pdf-upload"
            type="file"
            accept=".pdf"
            onChange={(e) => onFileUpload(e, documentType)}
            className="hidden"
            disabled={uploadStatus === "uploading" || uploadStatus === "processing"}
          />

          <div className="flex flex-col items-center gap-4">
            {uploadStatus === "idle" && (
              <>
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center group-hover:from-emerald-500/30 group-hover:to-teal-500/30 transition-all duration-300">
                  <FileUp className="w-8 h-8 text-emerald-400 group-hover:text-emerald-300 transition-colors" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">Drop your document here</p>
                  <p className="text-slate-500 text-sm mt-1.5">Or click to browse from your computer</p>
                </div>
              </>
            )}

            {uploadStatus === "uploading" && (
              <>
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">Uploading...</p>
                  <p className="text-slate-500 text-sm mt-1.5">{fileName}</p>
                </div>
              </>
            )}

            {uploadStatus === "processing" && (
              <>
                <div className="w-16 h-16 rounded-2xl bg-teal-500/20 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">Processing document locally...</p>
                  <p className="text-slate-500 text-sm mt-1.5">Creating embeddings — no data sent to the cloud</p>
                </div>
              </>
            )}

            {uploadStatus === "ready" && (
              <>
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">Ready to analyze!</p>
                  <p className="text-slate-500 text-sm mt-1.5">{fileName}</p>
                </div>
              </>
            )}

            {uploadStatus === "error" && (
              <>
                <div className="w-16 h-16 rounded-2xl bg-red-500/20 flex items-center justify-center">
                  <AlertCircle className="w-8 h-8 text-red-400" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">Upload failed</p>
                  <p className="text-slate-500 text-sm mt-1.5">Click to try again</p>
                </div>
              </>
            )}
          </div>
        </label>
      </div>

      {/* Privacy badge */}
      <div className="flex items-center justify-center gap-2 mt-5">
        <Lock className="w-3 h-3 text-emerald-500/60" />
        <p className="text-xs text-slate-500">Your documents never leave your device — 100% local processing</p>
      </div>
    </div>
  );
}
