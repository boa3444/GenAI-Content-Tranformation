"use client";

import React, { useState, useEffect, useRef } from "react";
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
  Layers
} from "lucide-react";

import { DashboardForm, ALL_SPOKES } from "./DashboardForm";
import { ShareIntents } from "./ShareIntents";
import { RemotionPreview } from "./RemotionPreview";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

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

  const renderSpokeIcon = (id: string) => {
    switch (id) {
      case "video": return <Video className="w-4 h-4 text-blue-600" />;
      case "linkedin": return <Linkedin className="w-4 h-4 text-blue-600" />;
      case "twitter": return <Twitter className="w-4 h-4 text-sky-500" />;
      case "advisory": return <ShieldAlert className="w-4 h-4 text-rose-500" />;
      case "infographic": return <BarChart2 className="w-4 h-4 text-emerald-600" />;
      case "summary": return <FileText className="w-4 h-4 text-amber-600" />;
      case "presentation": return <Presentation className="w-4 h-4 text-indigo-600" />;
      default: return <Sparkles className="w-4 h-4 text-blue-600" />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 text-gray-800">
      {/* 1. Header Bar */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-gray-200 px-6 py-3.5 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-50 border border-blue-200 text-blue-600">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">
              AI Content Transformation Engine
            </h1>
            <p className="text-xs text-gray-500">
              Conversational Multi-Spoke Generator | BM25 + FAISS Hybrid Engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-medium flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
            Live WS: <span className="font-mono font-semibold">{clientId || "Connecting..."}</span>
          </span>
        </div>
      </header>

      {/* 4. Conversational Main Feed Container */}
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 pb-48 space-y-8">
        
        {/* Welcome Hero State (Empty Feed) */}
        {Object.keys(spokeResults).length === 0 && !isProcessing && (
          <div className="text-center py-12 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center mx-auto shadow-sm">
              <Sparkles className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 tracking-tight">
              What content would you like to transform today?
            </h2>
            <p className="text-sm text-gray-500 max-w-lg mx-auto">
              Attach a document or enter text below. Select your target output spokes (Video, Presentation, Advisory, LinkedIn, Twitter, Infographic, Summary) to generate multi-channel deliverables in seconds.
            </p>

            {/* Quick Prompt Suggestions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto pt-4 text-left">
              <button
                type="button"
                onClick={() => setTextContent("Explain the architectural principles of high-throughput distributed vector retrieval and BM25 rank fusion.")}
                className="p-3.5 rounded-2xl bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50/50 text-xs text-gray-700 transition-all shadow-sm flex items-start gap-2.5"
              >
                <FileText className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-gray-900 block">Vector & Hybrid Retrieval</span>
                  <span className="text-gray-500">Explain BM25 rank fusion & FAISS context indexing.</span>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setTextContent("Draft a technical advisory on securing multi-tenant web applications against server-side request forgery.")}
                className="p-3.5 rounded-2xl bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50/50 text-xs text-gray-700 transition-all shadow-sm flex items-start gap-2.5"
              >
                <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-gray-900 block">Technical Risk Advisory</span>
                  <span className="text-gray-500">Formulate operational risk blueprints & mitigations.</span>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Processing State Feed Card */}
        {isProcessing && (
          <div className="p-6 rounded-2xl bg-white border border-blue-100 shadow-md space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-blue-700 font-bold text-sm">
                <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                Processing Transformation Request ({elapsedTime}s)
              </div>
              <span className="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
                {progress}%
              </span>
            </div>

            <div className="w-full h-2 rounded-full bg-gray-100 overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300 rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="text-xs text-gray-600 font-medium">{statusMessage}</p>

            {/* Live Terminal Log Snippet */}
            <div className="bg-gray-900 text-gray-200 font-mono text-[11px] p-3 rounded-xl max-h-28 overflow-y-auto space-y-1">
              {logs.map((log, i) => (
                <div key={i}>
                  <span className="text-blue-400">&gt;</span> {log}
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
                    className={`shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-blue-600 text-white shadow-sm"
                        : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
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
              <div className="bg-white rounded-2xl border border-gray-200 shadow-md overflow-hidden animate-fadeIn">
                {/* Header Card Bar */}
                <div className="bg-blue-50 px-6 py-4 border-b border-blue-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {renderSpokeIcon(activeTab)}
                    <h3 className="text-sm font-bold text-blue-900 uppercase tracking-wide">
                      {ALL_SPOKES.find((s) => s.id === activeTab)?.name || activeTab} Deliverable
                    </h3>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-white text-blue-700 text-xs font-semibold border border-blue-200">
                    Generated Output
                  </span>
                </div>

                <div className="p-6 space-y-6">
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
                        <h4 className="text-lg font-bold text-gray-900">
                          {spokeResults[activeTab].data?.headline || spokeResults[activeTab].headline || spokeResults[activeTab].hook}
                        </h4>
                        <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                          {spokeResults[activeTab].data?.post_body || spokeResults[activeTab].post_body || spokeResults[activeTab].main_body}
                        </p>
                        <div className="flex flex-wrap gap-1.5 pt-2">
                          {(spokeResults[activeTab].data?.hashtags || spokeResults[activeTab].hashtags)?.map(
                            (tag: string, i: number) => (
                              <span key={i} className="text-xs font-semibold text-blue-600 font-mono">
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
                            <div key={i} className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-xs text-gray-800 font-medium">
                              {tweet}
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
                          <span className="px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 font-bold uppercase tracking-wider">
                            {spokeResults[activeTab].data?.severity || spokeResults[activeTab].severity || "HIGH"}
                          </span>
                          <span className="font-mono text-gray-500">{spokeResults[activeTab].data?.advisory_id}</span>
                        </div>
                        <h4 className="text-lg font-bold text-gray-900">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                        <p className="text-sm text-gray-700 leading-relaxed">{spokeResults[activeTab].data?.executive_overview || spokeResults[activeTab].executive_summary}</p>
                        
                        {(spokeResults[activeTab].data?.key_findings || spokeResults[activeTab].key_findings) && (
                          <div className="space-y-2">
                            <h5 className="font-bold text-blue-700 uppercase">Key Findings</h5>
                            <ul className="list-disc list-inside space-y-1 text-gray-700">
                              {(spokeResults[activeTab].data?.key_findings || spokeResults[activeTab].key_findings).map((item: string, i: number) => (
                                <li key={i}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Infographic Output */}
                  {activeTab === "infographic" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-gray-900">{spokeResults[activeTab].data?.title || spokeResults[activeTab].main_title}</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {(spokeResults[activeTab].data?.key_metrics || spokeResults[activeTab].data_points)?.map((m: any, i: number) => (
                          <div key={i} className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center">
                            <span className="text-lg font-extrabold text-blue-600 block">{typeof m === 'string' ? `Metric ${i+1}` : m.value}</span>
                            <span className="text-xs text-gray-600 font-medium">{typeof m === 'string' ? m : m.label}</span>
                          </div>
                        ))}
                      </div>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Summary Output */}
                  {activeTab === "summary" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-gray-900">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                      <p className="text-sm text-gray-700 leading-relaxed">{spokeResults[activeTab].data?.executive_abstract || spokeResults[activeTab].executive_abstract}</p>
                      <ShareIntents text={spokeResults[activeTab].data?.title || ""} />
                    </div>
                  )}

                  {/* Presentation Output */}
                  {activeTab === "presentation" && (
                    <div className="space-y-4">
                      <h4 className="text-lg font-bold text-gray-900">{spokeResults[activeTab].data?.title || spokeResults[activeTab].title}</h4>
                      <div className="space-y-3">
                        {(spokeResults[activeTab].data?.slides || spokeResults[activeTab].slides)?.map((slide: any, i: number) => (
                          <div key={i} className="p-4 rounded-xl bg-gray-50 border border-gray-200 space-y-2 text-xs">
                            <h5 className="font-bold text-indigo-700">Slide {slide.slide_number}: {slide.title}</h5>
                            <ul className="list-disc list-inside text-gray-700 space-y-1">
                              {(slide.bullet_points || slide.main_bullet_points)?.map((bp: string, j: number) => (
                                <li key={j}>{bp}</li>
                              ))}
                            </ul>
                            {(slide.speaker_notes || slide.detailed_speaker_notes) && (
                              <p className="text-gray-500 bg-white p-2 rounded-lg border border-gray-200">
                                🗣️ <strong>Speaker Notes:</strong> {slide.speaker_notes || slide.detailed_speaker_notes}
                              </p>
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
      <div className="fixed bottom-0 left-0 right-0 z-30 bg-gradient-to-t from-gray-50 via-gray-50/95 to-transparent pt-6 pb-6 px-4">
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
