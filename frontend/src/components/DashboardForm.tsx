"use client";

import React, { useRef, ChangeEvent, KeyboardEvent } from "react";
import { Paperclip, ArrowUp, X, FileText, Check } from "lucide-react";

export interface SpokeOption {
  id: string;
  name: string;
  iconName: string;
  description: string;
}

export const ALL_SPOKES: SpokeOption[] = [
  { id: "video", name: "Video Package", iconName: "video", description: "Multi-scene video script & Remotion payload." },
  { id: "linkedin", name: "LinkedIn Post", iconName: "linkedin", description: "Professional post with hook and hashtags." },
  { id: "twitter", name: "Twitter/X Thread", iconName: "twitter", description: "Platform-optimized educational tweet thread." },
  { id: "advisory", name: "Technical Advisory", iconName: "shield-alert", description: "Formal advisory with risk analysis." },
  { id: "infographic", name: "Infographic", iconName: "bar-chart-2", description: "Visual blueprint with metrics & structure." },
  { id: "summary", name: "Executive Briefing", iconName: "file-text", description: "Concise summary briefing for decision-makers." },
  { id: "presentation", name: "Presentation Deck", iconName: "presentation", description: "Multi-slide deck with verbatim speaker notes." }
];

interface DashboardFormProps {
  textContent: string;
  setTextContent: (val: string) => void;
  file: File | null;
  setFile: (file: File | null) => void;
  selectedSpokes: string[];
  setSelectedSpokes: React.Dispatch<React.SetStateAction<string[]>>;
  isProcessing: boolean;
  onTransform: () => void;
}

export const DashboardForm: React.FC<DashboardFormProps> = ({
  textContent,
  setTextContent,
  file,
  setFile,
  selectedSpokes,
  setSelectedSpokes,
  isProcessing,
  onTransform,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const toggleSpoke = (id: string) => {
    setSelectedSpokes((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedSpokes.length === ALL_SPOKES.length) {
      setSelectedSpokes([]);
    } else {
      setSelectedSpokes(ALL_SPOKES.map((s) => s.id));
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isProcessing && (file || textContent.trim()) && selectedSpokes.length > 0) {
        onTransform();
      }
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3">
      {/* Hidden File Input element wired to fileInputRef */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        onClick={(e) => {
          (e.target as HTMLInputElement).value = "";
        }}
        className="hidden"
        accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.json"
      />

      {/* 3. Spoke Selectors as Horizontal Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          type="button"
          onClick={toggleSelectAll}
          className="shrink-0 px-3.5 py-1.5 rounded-full border border-gray-200 text-xs font-semibold text-gray-700 bg-white hover:bg-gray-50 transition-all shadow-sm"
        >
          {selectedSpokes.length === ALL_SPOKES.length ? "Deselect All" : "Select All"}
        </button>

        <div className="h-4 w-px bg-gray-300 shrink-0" />

        {ALL_SPOKES.map((spoke) => {
          const isSelected = selectedSpokes.includes(spoke.id);
          return (
            <button
              key={spoke.id}
              type="button"
              onClick={() => toggleSpoke(spoke.id)}
              className={`shrink-0 flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all ${
                isSelected
                  ? "bg-blue-100 text-blue-700 border-blue-300 shadow-sm font-semibold"
                  : "bg-white text-gray-700 border-gray-200 hover:border-gray-300 hover:bg-gray-50"
              }`}
            >
              {isSelected && <Check className="w-3.5 h-3.5 text-blue-600" />}
              {spoke.name}
            </button>
          );
        })}
      </div>

      {/* Attached File Preview Pill displayed above/inside the input container */}
      {file && (
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-medium shadow-sm">
            <Paperclip className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span className="max-w-xs truncate font-semibold">{file.name}</span>
            <button
              type="button"
              onClick={() => setFile(null)}
              title="Remove attached file"
              className="text-blue-500 hover:text-blue-700 p-0.5 rounded-full hover:bg-blue-100 transition-all"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* 2. The Unified Input Field (The Chat Bar) */}
      <div className="relative bg-white rounded-3xl border border-gray-200 shadow-lg hover:border-gray-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all p-3 space-y-2">
        <div className="flex items-center gap-2">
          {/* File Upload Attachment Icon Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            title="Attach Document or Image"
            className="p-2.5 rounded-full text-gray-500 hover:text-blue-600 hover:bg-blue-50 transition-all shrink-0"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Auto-resizing Prompt Text Area */}
          <textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask AI engine to transform document into video scripts, advisory, slides, posts..."
            rows={1}
            className="w-full text-sm text-gray-800 placeholder-gray-400 bg-transparent resize-none focus:outline-none py-2 px-1 max-h-32 min-h-[40px]"
          />

          {/* Submit Icon Button */}
          <button
            type="button"
            onClick={onTransform}
            disabled={isProcessing || (!file && !textContent.trim()) || selectedSpokes.length === 0}
            className={`p-2.5 rounded-full text-white transition-all shrink-0 flex items-center justify-center ${
              isProcessing || (!file && !textContent.trim()) || selectedSpokes.length === 0
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 shadow-md text-white"
            }`}
          >
            <ArrowUp className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
