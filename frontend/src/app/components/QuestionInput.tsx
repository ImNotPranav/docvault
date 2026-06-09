import { Send, Loader2, Shield } from "lucide-react";
import { UploadStatus } from "../App";
import { useState, useRef, useEffect } from "react";

interface QuestionInputProps {
  question: string;
  setQuestion: React.Dispatch<React.SetStateAction<string>>;
  uploadStatus: UploadStatus;
  handleAsk: () => Promise<void>
  isAsking: boolean;
  handleKeyPress: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
}

export default function QuestionInput({ question, setQuestion, uploadStatus, handleAsk, isAsking, handleKeyPress }: QuestionInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [question]);

  const isDisabled = uploadStatus !== "ready" || isAsking;
  const canSend = !isDisabled && question.trim().length > 0;

  return (
    <div className="sticky bottom-0 left-0 right-0 bg-gradient-to-t from-[#0a0a1a] via-[#0a0a1a]/95 to-transparent pt-6 pb-4">
      <div className="max-w-3xl mx-auto">
        <div
          className={`
            relative bg-[#12122a]/90 backdrop-blur-xl rounded-2xl
            border transition-all duration-300
            ${isFocused
              ? 'border-emerald-500/50 shadow-lg shadow-emerald-500/10'
              : 'border-white/10 hover:border-white/20'
            }
            ${isDisabled ? 'opacity-50' : ''}
          `}
        >
          <div className="flex items-end gap-2 p-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleAsk();
                  }
                }}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder={
                  uploadStatus === "ready"
                    ? "Ask anything about your document..."
                    : "Upload a document to start analyzing..."
                }
                disabled={isDisabled}
                rows={1}
                className={`
                  w-full bg-transparent text-white placeholder-slate-600
                  focus:outline-none resize-none py-2.5 px-3
                  text-sm leading-relaxed
                  disabled:cursor-not-allowed
                `}
                style={{ maxHeight: '200px' }}
              />
            </div>

            <button
              onClick={handleAsk}
              disabled={!canSend}
              className={`
                flex-shrink-0 w-10 h-10 rounded-xl
                flex items-center justify-center
                transition-all duration-200
                ${canSend
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 hover:scale-105 active:scale-95'
                  : 'bg-white/5 text-slate-600 cursor-not-allowed'
                }
              `}
              title={isAsking ? "Analyzing..." : "Send message"}
            >
              {isAsking ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>

          {uploadStatus === "ready" && (
            <div className="px-4 pb-3 flex items-center justify-center gap-2">
              <Shield className="w-3 h-3 text-emerald-400/60" />
              <span className="text-[11px] text-slate-600">
                All answers are generated locally · Press Enter to send
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
