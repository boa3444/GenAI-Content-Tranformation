import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export interface Scene {
  scene_number?: number;
  scene_id?: number;
  duration_seconds?: number;
  duration?: number;
  background_color?: string;
  narration_text?: string;
  voiceover_line?: string;
  subtitle_text?: string;
  on_screen_text?: string;
  visual_description?: string;
  heading?: string;
  b_roll_suggestion?: string;
}

export interface RemotionPayload {
  video_title?: string;
  title?: string;
  target_duration_seconds?: number;
  duration_seconds?: number;
  narrator_script?: string;
  scenes?: Scene[];
  storyboard_scenes?: Scene[];
  remotion_props?: {
    fps?: number;
    width?: number;
    height?: number;
  };
}

const SceneItem: React.FC<{
  scene: Scene;
  index: number;
  totalScenes: number;
}> = ({ scene, index, totalScenes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Heading slide down animation from top
  const headingSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });
  const headingY = interpolate(headingSpring, [0, 1], [-80, 0]);
  const headingOpacity = interpolate(headingSpring, [0, 1], [0, 1]);

  // Subtitle / Main text fade and pop in animation
  const subtitleSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 12, mass: 0.9 },
  });
  const subtitleScale = interpolate(subtitleSpring, [0, 1], [0.85, 1]);
  const subtitleOpacity = interpolate(subtitleSpring, [0, 1], [0, 1]);

  // Narration bar slide up animation from bottom
  const narrationSpring = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 14, mass: 0.8 },
  });
  const narrationY = interpolate(narrationSpring, [0, 1], [50, 0]);
  const narrationOpacity = interpolate(narrationSpring, [0, 1], [0, 1]);

  const bg = scene.background_color || "#0a0a0c";
  const sceneNum = scene.scene_number || scene.scene_id || index + 1;
  const headingText = scene.heading || `SCENE ${sceneNum}`;
  const mainText = scene.subtitle_text || scene.on_screen_text || "SUBTITLE TEXT";
  const narration = scene.narration_text || scene.voiceover_line;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bg,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "60px 80px",
        color: "#ffffff",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Top Header Badge */}
      <div
        style={{
          transform: `translateY(${headingY}px)`,
          opacity: headingOpacity,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          width: "100%",
          zIndex: 10,
        }}
      >
        <div
          style={{
            padding: "8px 20px",
            borderRadius: "8px",
            backgroundColor: "rgba(0, 240, 255, 0.15)",
            border: "1px solid rgba(0, 240, 255, 0.4)",
            color: "#00f0ff",
            fontSize: "24px",
            fontWeight: "bold",
            letterSpacing: "2px",
            textTransform: "uppercase",
          }}
        >
          {headingText} ({sceneNum} / {totalScenes})
        </div>
        <div
          style={{
            fontSize: "22px",
            color: "#9ca3af",
            fontFamily: "monospace",
          }}
        >
          ⏱️ {scene.duration_seconds || scene.duration || 6}s
        </div>
      </div>

      {/* Main Subtitle / Animated Concept Banner */}
      <div
        style={{
          transform: `scale(${subtitleScale})`,
          opacity: subtitleOpacity,
          textAlign: "center",
          margin: "auto",
          maxWidth: "1400px",
          zIndex: 10,
        }}
      >
        <h1
          style={{
            fontSize: "64px",
            fontWeight: 800,
            lineHeight: 1.2,
            background: "linear-gradient(to right, #ffffff, #00f0ff, #38bdf8)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            filter: "drop-shadow(0 4px 12px rgba(0, 240, 255, 0.3))",
            margin: 0,
          }}
        >
          {mainText}
        </h1>
        {scene.visual_description && (
          <p
            style={{
              fontSize: "24px",
              color: "rgba(255, 255, 255, 0.7)",
              marginTop: "24px",
              fontWeight: 500,
            }}
          >
            🎬 {scene.visual_description}
          </p>
        )}
      </div>

      {/* Bottom Voiceover / Narration Box */}
      {narration && (
        <div
          style={{
            transform: `translateY(${narrationY}px)`,
            opacity: narrationOpacity,
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(12px)",
            padding: "24px 36px",
            borderRadius: "16px",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            maxWidth: "1400px",
            margin: "0 auto",
            textAlign: "center",
            zIndex: 10,
          }}
        >
          <p
            style={{
              fontSize: "24px",
              color: "#fcd34d",
              margin: 0,
              fontWeight: 600,
              lineHeight: 1.4,
            }}
          >
            🗣️ {narration}
          </p>
        </div>
      )}

      {/* Subtle Background Gradient Overlay */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

export const VideoComposition: React.FC<{ payload: RemotionPayload }> = ({
  payload,
}) => {
  const { fps } = useVideoConfig();
  const safePayload = payload || {};
  const scenes = safePayload.scenes || safePayload.storyboard_scenes || [];

  if (scenes.length === 0) {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#0a0a0c",
          color: "#ffffff",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "32px",
        }}
      >
        No scenes available in Remotion package.
      </AbsoluteFill>
    );
  }

  let accumulatedFrames = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0c" }}>
      {scenes.map((scene, index) => {
        const durationSec = scene.duration_seconds || scene.duration || 6;
        const durationInFrames = Math.max(1, Math.round(durationSec * fps));
        const from = accumulatedFrames;
        accumulatedFrames += durationInFrames;

        return (
          <Sequence
            key={index}
            from={from}
            durationInFrames={durationInFrames}
          >
            <SceneItem
              scene={scene}
              index={index}
              totalScenes={scenes.length}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
