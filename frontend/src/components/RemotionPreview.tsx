"use client";

import React, { useState } from "react";
import { Film, Play, Layers, Clock, MessageSquare, Sparkles, Download } from "lucide-react";
import { Player } from "@remotion/player";
import { VideoComposition, RemotionPayload, Scene } from "../remotion/VideoComposition";

export const RemotionPreview: React.FC<{ payload: RemotionPayload }> = ({ payload }) => {
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const safePayload = payload || {};
  const rawScenes = safePayload.scenes || safePayload.storyboard_scenes || [];
  const activeScene = rawScenes[activeSceneIndex] || null;
  const title = safePayload.video_title || safePayload.title || "Remotion Video Package";

  const fps = safePayload.remotion_props?.fps || 30;
  const totalDuration = safePayload.target_duration_seconds || safePayload.duration_seconds || 30;

  const calculatedTotalFrames = rawScenes.reduce((acc, scene) => {
    const durSec = scene.duration_seconds || scene.duration || 6;
    return acc + Math.round(durSec * fps);
  }, 0);

  const durationInFrames = Math.max(
    1,
    calculatedTotalFrames || Math.round(totalDuration * fps)
  );

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between p-4 rounded-2xl bg-white border border-gray-200 shadow-sm gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Film className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-gray-900">{title}</h3>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Target Duration: <span className="text-blue-700 font-mono font-semibold">{totalDuration}s</span> | Resolution:{" "}
            <span className="text-blue-700 font-mono font-semibold">
              {safePayload.remotion_props?.width || 1920}x{safePayload.remotion_props?.height || 1080}
            </span>{" "}
            @ <span className="text-blue-700 font-mono font-semibold">{fps}fps</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => alert("MP4 Rendering started in the background!")}
            className="px-3.5 py-1.5 rounded-xl bg-blue-600 text-white font-semibold text-xs hover:bg-blue-700 transition-all flex items-center gap-1.5 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            Download MP4
          </button>
          <span className="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-medium flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            Remotion Package Schema Ready
          </span>
        </div>
      </div>

      {/* Interactive Remotion Player & Storyboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Real Playable Remotion Player */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative aspect-video rounded-2xl border border-gray-200 overflow-hidden shadow-md bg-black">
            <Player
              component={VideoComposition}
              inputProps={{ payload: safePayload }}
              durationInFrames={durationInFrames}
              fps={fps}
              compositionWidth={safePayload.remotion_props?.width || 1920}
              compositionHeight={safePayload.remotion_props?.height || 1080}
              style={{ width: "100%", height: "100%" }}
              controls
            />
          </div>

          {/* Visual & B-Roll Recommendation Notes */}
          <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-blue-600" /> Remotion Scene Visual Description & B-Roll
            </h4>
            <p className="text-xs text-gray-700 bg-gray-50 p-2.5 rounded-xl border border-gray-200">
              <span className="text-gray-500 font-semibold">Visual Graphics:</span>{" "}
              {activeScene?.visual_description || "Dynamic motion graphics & visual diagrams"}
            </p>
            <p className="text-xs text-gray-700 bg-gray-50 p-2.5 rounded-xl border border-gray-200">
              <span className="text-gray-500 font-semibold">Background Color:</span>{" "}
              <span className="font-mono text-blue-600 font-bold">{activeScene?.background_color || "#0a0a0c"}</span>
            </p>
          </div>
        </div>

        {/* Right 1 Col: Scene Selector List */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1.5">
            <Play className="w-3.5 h-3.5 text-blue-600" /> Remotion Scenes Timeline
          </h4>
          <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
            {rawScenes.map((scene, idx) => (
              <button
                key={idx}
                onClick={() => setActiveSceneIndex(idx)}
                className={`w-full text-left p-3 rounded-xl border transition-all ${
                  activeSceneIndex === idx
                    ? "bg-blue-50 border-blue-300 text-blue-900 shadow-sm font-medium"
                    : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-700">Scene {scene.scene_number || scene.scene_id || idx + 1}</span>
                  <span className="text-[10px] font-mono text-gray-400">{scene.duration_seconds || scene.duration || 6}s</span>
                </div>
                <div className="text-xs font-semibold text-gray-800 mt-1 truncate">
                  {scene.subtitle_text || scene.on_screen_text || `Scene ${idx + 1}`}
                </div>
                <div className="text-[11px] text-gray-500 line-clamp-1 mt-0.5">{scene.narration_text || scene.voiceover_line}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Subtitles & Script Tabs */}
      <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-sm space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700 flex items-center gap-1.5">
          <MessageSquare className="w-4 h-4 text-blue-600" /> Remotion Narration Script & Subtitles
        </h4>
        <div className="bg-gray-50 p-3 rounded-xl border border-gray-200 max-h-48 overflow-y-auto space-y-2 font-mono text-xs">
          {rawScenes.map((scene, i) => (
            <div key={i} className="flex items-start gap-3 border-b border-gray-200/60 pb-1.5">
              <span className="text-blue-600 font-semibold shrink-0">
                [Scene {scene.scene_number || i + 1} - {scene.duration_seconds || 6}s]
              </span>
              <span className="text-gray-700">{scene.narration_text || scene.voiceover_line}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
