"use client";

import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import {
  Sparkles,
  Bot,
  User,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Video,
  Linkedin,
  Twitter,
  ShieldAlert,
  BarChart2,
  FileText,
  Presentation,
  Share2,
  Clock,
  Layers,
  Globe,
  Volume2,
  Play
} from "lucide-react";

import { DashboardForm, ALL_SPOKES } from "./DashboardForm";
import { ShareIntents } from "./ShareIntents";
import { RemotionPreview } from "./RemotionPreview";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

// Studio Light Minimal 3-Star Constellation
const StarConstellation = () => (
  <div className="flex items-center justify-center gap-5 py-3">
    {/* Left Flanking Star - Outlined, Opacity 40% */}
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="opacity-40 shrink-0"
    >
      <path
        d="M12 2L14.85 8.65L22 9.24L16.5 13.97L18.18 21L12 17.27L5.82 21L7.5 13.97L2 9.24L9.15 8.65L12 2Z"
        stroke="#0A0A0A"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>

    {/* Center Main BIG Prominent Black Star */}
    <svg
      width="48"
      height="48"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="drop-shadow-md transition-transform duration-300 hover:scale-105 shrink-0"
    >
      <path
        d="M12 2L14.85 8.65L22 9.24L16.5 13.97L18.18 21L12 17.27L5.82 21L7.5 13.97L2 9.24L9.15 8.65L12 2Z"
        fill="#0A0A0A"
        stroke="#0A0A0A"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>

    {/* Right Flanking Star - Outlined, Opacity 40% */}
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="opacity-40 shrink-0"
    >
      <path
        d="M12 2L14.85 8.65L22 9.24L16.5 13.97L18.18 21L12 17.27L5.82 21L7.5 13.97L2 9.24L9.15 8.65L12 2Z"
        stroke="#0A0A0A"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  </div>
);

export const FormattedMarkdown: React.FC<{ content: string; className?: string }> = ({ content, className = "" }) => {
  if (!content) return null;
  return (
    <div className={`prose prose-neutral max-w-none text-gray-800 leading-relaxed ${className}`}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => <h2 className="text-xl font-bold text-[#0A0A0A] border-b border-gray-200 pb-2 mb-3 mt-4 tracking-tight">{children}</h2>,
          h2: ({ children }) => <h2 className="text-lg font-bold text-[#0A0A0A] border-b border-gray-200 pb-1.5 mb-2.5 mt-3 tracking-tight">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-semibold text-[#0A0A0A] mb-2 mt-2">{children}</h3>,
          p: ({ children }) => <p className="text-sm text-gray-700 leading-relaxed mb-3">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1.5 text-sm text-gray-700 mb-3 bg-[#F8F9FA] p-4 rounded-2xl border border-gray-200">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1.5 text-sm text-gray-700 mb-3 bg-[#F8F9FA] p-4 rounded-2xl border border-gray-200">{children}</ol>,
          li: ({ children }) => <li className="text-sm text-gray-700">{children}</li>,
          strong: ({ children }) => <strong className="font-bold text-white bg-[#0A0A0A] px-1.5 py-0.5 rounded-md">{children}</strong>,
          code: ({ children }) => <code className="bg-gray-100 text-[#0A0A0A] font-mono text-xs px-1.5 py-0.5 rounded-md border border-gray-200">{children}</code>,
          blockquote: ({ children }) => <blockquote className="border-l-4 border-[#0A0A0A] bg-[#F8F9FA] p-3.5 italic text-gray-700 rounded-r-2xl my-3">{children}</blockquote>
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export const Dashboard: React.FC = () => {
  // Input State
  const [file, setFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState<string>("");
  const [selectedSpokes, setSelectedSpokes] = useState<string[]>([
    "video",
    "linkedin",
    "twitter",
    "advisory",
    "infographic",
    "summary",
    "presentation"
  ]);

  // Real-time State
  const [clientId, setClientId] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>("Ready to transform content");
  const [logs, setLogs] = useState<string[]>([]);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [spokeResults, setSpokeResults] = useState<Record<string, any>>({});
  const [activeTab, setActiveTab] = useState<string>("");

  // TTS Audio & Language State
  const [selectedLang, setSelectedLang] = useState<string>("hi");
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const [translatedContent, setTranslatedContent] = useState<Record<string, string>>({});
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const feedEndRef = useRef<HTMLDivElement | null>(null);

  // Initialize Client ID & WebSocket connection
  useEffect(() => {
    const id = "client_" + Math.random().toString(36).substring(2, 9);
    setClientId(id);

    const ws = new WebSocket(`${WS_URL}/ws/${id}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket Connected:", id);
      setLogs((prev) => [...prev, `[System] Real-time WebSocket established (${id})`]);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "status_update") {
          setProgress(msg.progress);
          setStatusMessage(msg.message);
          setLogs((prev) => [...prev, `[${msg.step.toUpperCase()}] ${msg.message}`]);

          if (msg.step === "complete") {
            setIsProcessing(false);
            if (timerRef.current) clearInterval(timerRef.current);
          }
        } else if (msg.type === "spoke_completed" || msg.event === "spoke_result") {
          const spokeKey = msg.spoke;
          const payloadData = msg.result || msg.payload || msg.data;
          setSpokeResults((prev) => {
            const next = { ...prev, [spokeKey]: payloadData };
            if (!activeTab) setActiveTab(spokeKey);
            return next;
          });
          setLogs((prev) => [...prev, `[SPOKE] Generated deliverable: ${spokeKey.toUpperCase()}`]);
        } else if (msg.type === "error" || msg.event === "error") {
          setIsProcessing(false);
          setStatusMessage(`Error: ${msg.message || msg.error}`);
          if (timerRef.current) clearInterval(timerRef.current);
        }
      } catch (err) {
        console.error("WS Message Error:", err);
      }
    };

    return () => {
      ws.close();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  useEffect(() => {
    if (isProcessing || Object.keys(spokeResults).length > 0) {
      feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [isProcessing, spokeResults]);

  const handleTransform = async () => {
    if (!file && !textContent.trim()) return;
    if (selectedSpokes.length === 0) return;

    setIsProcessing(true);
    setProgress(5);
    setStatusMessage("Submitting job to Hub-and-Spoke Engine...");
    setSpokeResults({});
    setActiveTab("");
    setElapsedTime(0);
    setLogs([`[Init] Transformation job started for ${selectedSpokes.length} selected spokes.`]);

    const startTime = Date.now();
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 500);

    const formData = new FormData();
    formData.append("client_id", clientId);
    if (file) formData.append("file", file);
    if (textContent) formData.append("text_content", textContent);
    formData.append("selected_spokes", JSON.stringify(selectedSpokes));
    formData.append("target_audience", "General Corporate");
    formData.append("tone", "Professional & Authoritative");
    formData.append("language", "English");
    formData.append("level_of_detail", "Comprehensive");
    formData.append("communication_objective", "Inform and Align");
    formData.append("content_style", "Executive Brief");

    try {
      const res = await fetch(`${BACKEND_URL}/api/transform`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Transformation request failed");
      }
    } catch (err: any) {
      setIsProcessing(false);
      setStatusMessage(`Error: ${err.message}`);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const extractTextForTTS = (spokeKey: string, dataObj: any): string => {
    if (!dataObj) return "";
    const data = dataObj.data || dataObj;
    if (spokeKey === "video") {
      return data.narrator_script || data.video_title || "Video script presentation.";
    } else if (spokeKey === "linkedin") {
      return `${data.headline || ""}. ${data.post_body || data.main_body || ""}`;
    } else if (spokeKey === "twitter") {
      return (data.thread || []).join(" ");
    } else if (spokeKey === "advisory") {
      return `${data.title || ""}. ${data.executive_summary || data.executive_overview || ""}. ${data.threat_or_context_analysis || ""}`;
    } else if (spokeKey === "summary") {
      return `${data.title || ""}. ${data.executive_abstract || ""}`;
    } else if (spokeKey === "presentation") {
      const notes = (data.slides || []).map((s: any) => s.speaker_notes || s.detailed_speaker_notes || s.title).join(". ");
      return `${data.title || ""}. ${notes}`;
    }
    return data.title || data.content || JSON.stringify(data);
  };

  const handleTranslateAndPlay = async (targetLangCode: string) => {
    setSelectedLang(targetLangCode);
    const activeText = extractTextForTTS(activeTab, spokeResults[activeTab]);
    if (!activeText || !activeText.trim()) return;

    setIsTranslating(true);
    setIsPlayingAudio(true);

    try {
      let textToSpeak = activeText;

      if (targetLangCode === "en") {
        setTranslatedContent((prev) => {
          const next = { ...prev };
          delete next[activeTab];
          return next;
        });
      } else {
        // 1. Fetch translated text from /api/translate
        const transRes = await fetch(`${BACKEND_URL}/api/translate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: activeText, target_lang: targetLangCode })
        });
        if (transRes.ok) {
          const transData = await transRes.json();
          if (transData.translated_text) {
            textToSpeak = transData.translated_text;
            setTranslatedContent((prev) => ({
              ...prev,
              [activeTab]: transData.translated_text
            }));
          }
        }
      }

      setIsTranslating(false);

      // 2. Fetch and play audio stream from /api/text-to-speech using browser native Audio API
      const ttsRes = await fetch(`${BACKEND_URL}/api/text-to-speech`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSpeak, target_lang: targetLangCode })
      });

      if (!ttsRes.ok) {
        throw new Error(`TTS server error: ${ttsRes.statusText}`);
      }

      const blob = await ttsRes.blob();
      const audioUrl = URL.createObjectURL(blob);

      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlayingAudio(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = (e) => {
        console.error("Audio playback error:", e);
        setIsPlayingAudio(false);
      };

      await audio.play();
    } catch (err) {
      console.error("Translation & Audio error:", err);
      setIsTranslating(false);
      setIsPlayingAudio(false);
    }
  };

  const playTTSAudio = async (textToSpeak: string) => {
    await handleTranslateAndPlay(selectedLang);
  };

  const renderSpokeIcon = (id: string) => {
    switch (id) {
      case "video": return <Video className="w-4 h-4 text-[#0A0A0A]" />;
      case "linkedin": return <Linkedin className="w-4 h-4 text-[#0A0A0A]" />;
      case "twitter": return <Twitter className="w-4 h-4 text-[#0A0A0A]" />;
      case "advisory": return <ShieldAlert className="w-4 h-4 text-[#0A0A0A]" />;
      case "infographic": return <BarChart2 className="w-4 h-4 text-[#0A0A0A]" />;
      case "summary": return <FileText className="w-4 h-4 text-[#0A0A0A]" />;
      case "presentation": return <Presentation className="w-4 h-4 text-[#0A0A0A]" />;
      default: return <Sparkles className="w-4 h-4 text-[#0A0A0A]" />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white text-[#0A0A0A]">
      {/* 1. Studio Header Bar */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3.5">
          <div className="p-2 rounded-2xl bg-[#F8F9FA] border border-gray-200 flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5 text-[#0A0A0A]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#0A0A0A] tracking-tight leading-tight flex items-center gap-2">
              AI Content Transformation Engine
            </h1>
            <p className="text-xs text-gray-500">
              Studio Light Minimal Engine | Multi-Language TTS & Translation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3.5 py-1.5 rounded-full bg-[#F8F9FA] border border-gray-200 text-[#0A0A0A] text-xs font-semibold flex items-center gap-2 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#0A0A0A] animate-ping" />
            Live WS: <span className="font-mono font-bold">{clientId || "Connecting..."}</span>
          </span>
        </div>
      </header>

      {/* 4. Conversational Main Feed Container */}
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 pb-48 space-y-8">
        
        {/* Starting Page Constellation Hero Section */}
        {Object.keys(spokeResults).length === 0 && !isProcessing && (
          <div className="text-center py-12 space-y-5">
            {/* 3-Star Constellation */}
            <StarConstellation />

            <h2 className="text-3xl font-extrabold text-[#0A0A0A] tracking-tight">
              What content would you like to transform today?
            </h2>
            <p className="text-sm text-gray-500 max-w-lg mx-auto leading-relaxed">
              Attach a document or enter text below. Select your target output spokes (Video, Presentation, Advisory, LinkedIn, Twitter, Infographic, Summary) to generate multi-channel deliverables in seconds.
            </p>

            {/* Quick Prompt Suggestions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 max-w-2xl mx-auto pt-4 text-left">
              <button
                type="button"
                onClick={() => setTextContent("Explain the architectural principles of high-throughput distributed vector retrieval and BM25 rank fusion.")}
                className="p-4 rounded-3xl bg-[#F8F9FA] border border-gray-200 hover:border-gray-400 hover:bg-white text-xs text-gray-800 transition-all duration-300 ease-in-out shadow-studio-card flex items-start gap-3"
              >
                <FileText className="w-4 h-4 text-[#0A0A0A] shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-[#0A0A0A] block">Vector & Hybrid Retrieval</span>
                  <span className="text-gray-500">Explain BM25 rank fusion & FAISS context indexing.</span>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setTextContent("Draft a technical advisory on securing multi-tenant web applications against server-side request forgery.")}
                className="p-4 rounded-3xl bg-[#F8F9FA] border border-gray-200 hover:border-gray-400 hover:bg-white text-xs text-gray-800 transition-all duration-300 ease-in-out shadow-studio-card flex items-start gap-3"
              >
                <ShieldAlert className="w-4 h-4 text-[#0A0A0A] shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-[#0A0A0A] block">Technical Risk Advisory</span>
                  <span className="text-gray-500">Formulate operational risk blueprints & mitigations.</span>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Processing State Feed Card */}
        {isProcessing && (
          <div className="p-6 rounded-3xl bg-[#F8F9FA] border border-gray-200 shadow-studio-diffused space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[#0A0A0A] font-bold text-sm">
                <RefreshCw className="w-4 h-4 animate-spin text-[#0A0A0A]" />
                Processing Transformation Request ({elapsedTime}s)
              </div>
              <span className="text-xs font-mono font-bold text-white bg-[#0A0A0A] px-3 py-1 rounded-full">
                {progress}%
              </span>
            </div>

            <div className="w-full h-2 rounded-full bg-gray-200 overflow-hidden">
              <div
                className="h-full bg-[#0A0A0A] transition-all duration-300 rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="text-xs text-gray-700 font-medium">{statusMessage}</p>

            {/* Live Terminal Log Snippet */}
            <div className="bg-[#0A0A0A] text-white font-mono text-[11px] p-4 rounded-2xl max-h-28 overflow-y-auto space-y-1">
              {logs.map((log, i) => (
                <div key={i}>
                  <span className="text-gray-400">&gt;</span> {log}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Delivered Outputs Feed */}
        {Object.keys(spokeResults).length > 0 && (
          <div className="space-y-6">
            {/* Horizontal Deliverable Tab Bar */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-gray-200 scrollbar-none">
              {Object.keys(spokeResults).map((spokeKey) => {
                const isActive = activeTab === spokeKey;
                const spokeMeta = ALL_SPOKES.find((s) => s.id === spokeKey);
                return (
                  <button
                    key={spokeKey}
                    type="button"
                    onClick={() => setActiveTab(spokeKey)}
                    className={`shrink-0 flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-semibold transition-all duration-300 ease-in-out ${
                      isActive
                        ? "bg-[#0A0A0A] text-white shadow-md font-bold"
                        : "bg-[#F8F9FA] border border-gray-200 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    {renderSpokeIcon(spokeKey)}
                    {spokeMeta ? spokeMeta.name : spokeKey}
                  </button>
                );
              })}
            </div>

            {/* Active Output Card */}
            {activeTab && spokeResults[activeTab] && (
              <div className="bg-[#F8F9FA] rounded-3xl border border-gray-200 shadow-studio-diffused overflow-hidden animate-fadeIn">
                {/* Header Card Bar with Native Target Language Dropdown & Solid Black Listen Button */}
                <div className="bg-white px-6 py-4 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    {renderSpokeIcon(activeTab)}
                    <h3 className="text-sm font-bold text-[#0A0A0A] uppercase tracking-wider">
                      {ALL_SPOKES.find((s) => s.id === activeTab)?.name || activeTab} Deliverable
                    </h3>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    {/* Language Translation & Audio Buttons */}
                    <div className="flex items-center gap-1.5 bg-[#F8F9FA] border border-gray-200 rounded-2xl p-1 shadow-sm">
                      <Globe className="w-3.5 h-3.5 text-[#0A0A0A] ml-2 mr-1" />
                      {[
                        { code: "en", label: "English 🇬🇧" },
                        { code: "hi", label: "Hindi 🇮🇳" },
                        { code: "bn", label: "Bengali 🇧🇩" },
                        { code: "ne", label: "Nepali 🇳🇵" },
                      ].map((lang) => (
                        <button
                          key={lang.code}
                          type="button"
                          onClick={() => handleTranslateAndPlay(lang.code)}
                          disabled={isTranslating || isPlayingAudio}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer disabled:opacity-50 ${
                            selectedLang === lang.code
                              ? "bg-[#0A0A0A] text-white shadow-sm"
                              : "bg-transparent text-gray-700 hover:bg-gray-200"
                          }`}
                        >
                          {lang.label}
                        </button>
                      ))}
                    </div>

                    {/* Studio Solid Black "Listen" Button */}
                    <button
                      type="button"
                      onClick={() => handleTranslateAndPlay(selectedLang)}
                      disabled={isPlayingAudio || isTranslating}
                      className="px-4 py-2 rounded-2xl bg-[#0A0A0A] text-white text-xs font-bold hover:bg-neutral-800 transition-all duration-300 ease-in-out flex items-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
                    >
                      {isPlayingAudio || isTranslating ? (
                        <>
                          <Volume2 className="w-4 h-4 animate-pulse text-white" />
                          <span>{isTranslating ? "Translating..." : "Listening..."}</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 text-white" />
                          <span>Listen</span>
                        </>
                      )}
                    </button>

                    <span className="px-3 py-1 rounded-full bg-[#0A0A0A] text-white text-xs font-semibold">
                      Generated Output
                    </span>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  {/* Real-time Translated Text Banner */}
                  {translatedContent[activeTab] && (
                    <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-950 space-y-2 shadow-sm animate-fadeIn">
                      <div className="flex items-center justify-between">
                        <span className="font-bold flex items-center gap-2 text-amber-950 text-sm">
                          <Globe className="w-4 h-4 text-amber-700" />
                          Translated Text ({selectedLang.toUpperCase()})
                        </span>
                        <button
                          type="button"
                          onClick={() => setTranslatedContent((prev) => ({ ...prev, [activeTab]: "" }))}
                          className="text-amber-800 font-semibold underline text-xs cursor-pointer hover:text-amber-950"
                        >
                          Reset to Original Text
                        </button>
                      </div>
                      <div className="text-gray-900 leading-relaxed font-medium pt-1">
                        <FormattedMarkdown content={translatedContent[activeTab]} />
                      </div>
                    </div>
                  )}
                  {/* Video Remotion Player Output */}
                  {activeTab === "video" && (
                    <div className="space-y-4">
                      <RemotionPreview payload={spokeResults[activeTab].data || spokeResults[activeTab]} />
                      <ShareIntents
                        title={spokeResults[activeTab].data?.title || spokeResults[activeTab].title}
                        text={spokeResults[activeTab].data?.narrator_script || ""}
                      />
                    </div>
                  )}

                  {/* LinkedIn Output */}
                  {activeTab === "linkedin" && (
                    <div className="space-y-4">
                      <div className="space-y-3">
                        <h4 className="text-lg font-bold text-[#0A0A0A]">
                          {spokeResults[activeTab].data?.headline || spokeResults[activeTab].headline || spokeResults[activeTab].hook}
                        </h4>
                        <FormattedMarkdown
                          content={spokeResults[activeTab].data?.post_body || spokeResults[activeTab].post_body || spokeResults[activeTab].main_body || ""}
                        />
                        <div className="flex flex-wrap gap-1.5 pt-2">
                          {(spokeResults[activeTab].data?.hashtags || spokeResults[activeTab].hashtags)?.map(
                            (tag: string, i: number) => (
                              <span key={i} className="text-xs font-semibold text-[#0A0A0A] font-mono bg-white px-2.5 py-1 rounded-lg border border-gray-200 shadow-sm">
                                {tag}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                      <ShareIntents
                        text={`${spokeResults[activeTab].data?.headline || ""}\n\n${spokeResults[activeTab].data?.post_body || ""}`}
                        hashtags={spokeResults[activeTab].data?.hashtags}
                        platform="linkedin"
                      />
                    </div>
                  )}

                  {/* Twitter Output */}
                  {activeTab === "twitter" && (
                    <div className="space-y-4">
                      <div className="space-y-3">
                        {(spokeResults[activeTab].data?.thread || spokeResults[activeTab].thread)?.map(
                          (tweet: string, i: number) => (
                            <div key={i} className="p-4 rounded-2xl bg-white border border-gray-200 text-xs text-gray-800 shadow-sm">
                              <FormattedMarkdown content={tweet} />
                            </div>
                          )
                        )}
                      </div>
                      <ShareIntents
                        text={(spokeResults[activeTab].data?.thread || spokeResults[activeTab].thread)?.join("\n\n") || ""}
                        platform="twitter"
                      />
                    </div>
                  )}

                  {/* Advisory Output */}
                  {activeTab === "advisory" && (
                    <div className="space-y-4">
                      <div className="space-y-4 text-xs text-gray-800">
                        <div className="flex items-center justify-between">
                          <span className="px-3.5 py-1 rounded-full bg-[#0A0A0A] text-white font-bold uppercase tracking-wider">
                            {spokeResults[activeTab].data?.severity || spokeResults[activeTab].severity || "HIGH"}
                          </span>
                          <span className="font-mono text-gray-500">{spokeResults[activeTab].data?.advisory_id}</span>
                        </div>
                        <h4 className="text-lg font-bold text-[#0A0A0A]">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                        
                        <div className="space-y-2">
                          <h5 className="font-bold text-[#0A0A0A] uppercase tracking-wider text-xs">Executive Summary</h5>
                          <FormattedMarkdown content={spokeResults[activeTab].data?.executive_summary || spokeResults[activeTab].data?.executive_overview || spokeResults[activeTab].executive_summary || ""} />
                        </div>

                        <div className="space-y-2">
                          <h5 className="font-bold text-[#0A0A0A] uppercase tracking-wider text-xs">Threat & Context Analysis</h5>
                          <FormattedMarkdown content={spokeResults[activeTab].data?.threat_or_context_analysis || spokeResults[activeTab].threat_or_context_analysis || ""} />
                        </div>
                        
                        {(spokeResults[activeTab].data?.detailed_recommendations || spokeResults[activeTab].data?.key_findings || spokeResults[activeTab].key_findings) && (
                          <div className="space-y-2">
                            <h5 className="font-bold text-[#0A0A0A] uppercase tracking-wider text-xs">Recommended Actions & Key Findings</h5>
                            <div className="space-y-2">
                              {(spokeResults[activeTab].data?.detailed_recommendations || spokeResults[activeTab].data?.key_findings || spokeResults[activeTab].key_findings).map((item: string, i: number) => (
                                <div key={i} className="p-4 rounded-2xl bg-white border border-gray-200 shadow-sm">
                                  <FormattedMarkdown content={item} />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Infographic Output */}
                  {activeTab === "infographic" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-[#0A0A0A]">{spokeResults[activeTab].data?.title || spokeResults[activeTab].main_title}</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                        {(spokeResults[activeTab].data?.key_metrics || spokeResults[activeTab].data_points)?.map((m: any, i: number) => (
                          <div key={i} className="p-4 rounded-2xl bg-white border border-gray-200 text-center space-y-1 shadow-sm">
                            <span className="text-lg font-extrabold text-[#0A0A0A] block">{typeof m === 'string' ? `Metric ${i+1}` : m.value}</span>
                            <span className="text-xs text-gray-500 font-medium block">{typeof m === 'string' ? m : m.label}</span>
                          </div>
                        ))}
                      </div>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Summary Output */}
                  {activeTab === "summary" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-[#0A0A0A]">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                      <FormattedMarkdown content={spokeResults[activeTab].data?.executive_abstract || spokeResults[activeTab].executive_abstract || ""} />
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Presentation Output */}
                  {activeTab === "presentation" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-[#0A0A0A]">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                      <div className="space-y-4">
                        {(spokeResults[activeTab].data?.slides || spokeResults[activeTab].slides)?.map((slide: any, i: number) => (
                          <div key={i} className="p-5 rounded-2xl bg-white border border-gray-200 space-y-3 text-xs shadow-sm">
                            <h5 className="font-bold text-[#0A0A0A] text-sm">Slide {slide.slide_number}: {slide.title}</h5>
                            <ul className="list-disc list-inside text-gray-700 space-y-1.5">
                              {(slide.bullet_points || slide.main_bullet_points)?.map((bp: string, j: number) => (
                                <li key={j} className="text-gray-700">
                                  <FormattedMarkdown content={bp} className="inline-block" />
                                </li>
                              ))}
                            </ul>
                            {(slide.speaker_notes || slide.detailed_speaker_notes) && (
                              <div className="text-gray-800 bg-[#F8F9FA] p-4 rounded-2xl border border-gray-200 space-y-1.5">
                                <span className="text-xs font-bold text-[#0A0A0A] block">🗣️ Verbatim Speaker Notes:</span>
                                <FormattedMarkdown content={slide.speaker_notes || slide.detailed_speaker_notes} />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        <div ref={feedEndRef} />
      </div>

      {/* 2 & 3. Bottom Sticky Container: Unified Chat Input Bar & Chip Selectors */}
      <div className="fixed bottom-0 left-0 right-0 z-30 bg-gradient-to-t from-white via-white/95 to-transparent pt-6 pb-6 px-4">
        <DashboardForm
          textContent={textContent}
          setTextContent={setTextContent}
          file={file}
          setFile={setFile}
          selectedSpokes={selectedSpokes}
          setSelectedSpokes={setSelectedSpokes}
          isProcessing={isProcessing}
          onTransform={handleTransform}
        />
      </div>
    </div>
  );
};
