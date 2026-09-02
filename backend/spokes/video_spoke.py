import json
from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, VideoPackageSchema

async def generate_video_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    system_instruction = (
        "You are an expert University Professor and Remotion Motion Graphics Producer. "
        "Transform the provided context into a complete video generation package formatted as strict JSON matching VideoPackageSchema. "
        "Include video_title, target_duration_seconds, and scenes. "
        "Each scene MUST contain: scene_number (int), background_color (hex string like #0a0a0c or #00f0ff), "
        "narration_text (verbatim voiceover script line teaching concepts directly from the uploaded context), subtitle_text (on-screen subtitles text), "
        "visual_description (descriptions of images/graphics to display), and duration_seconds (int, 5-8 seconds)."
    )
    
    prompt = f"""
    Create a video package based strictly and only on this uploaded context:
    {context}
    
    Configuration Parameters:
    - Audience: {config.target_audience}
    - Tone: {config.tone}
    - Language: {config.language}
    - Style: {config.content_style}
    
    Generate deep educational video package for Remotion matching VideoPackageSchema.
    """

    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=VideoPackageSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=VideoPackageSchema
        )

    if res:
        # Standardize helper aliases for UI backwards compatibility
        if "video_title" in res and "title" not in res:
            res["title"] = res["video_title"]
        if "target_duration_seconds" in res and "duration_seconds" not in res:
            res["duration_seconds"] = res["target_duration_seconds"]

        if "scenes" in res:
            storyboard_scenes = []
            subtitles = []
            curr_time = 0.0
            for idx, scene in enumerate(res["scenes"]):
                dur = scene.get("duration_seconds", 6)
                bg = scene.get("background_color", "#0a0a0c")
                narr = scene.get("narration_text", "")
                sub = scene.get("subtitle_text", narr)
                vis = scene.get("visual_description", "")

                storyboard_scenes.append({
                    "scene_id": scene.get("scene_number", idx + 1),
                    "duration": dur,
                    "heading": f"Scene {scene.get('scene_number', idx + 1)}",
                    "visual_description": f"[Background {bg}] {vis}",
                    "on_screen_text": sub,
                    "voiceover_line": narr,
                    "b_roll_suggestion": vis
                })
                subtitles.append({
                    "start": curr_time,
                    "end": curr_time + dur,
                    "text": sub
                })
                curr_time += dur
            res["storyboard_scenes"] = storyboard_scenes
            res["subtitles"] = subtitles

        return res

    snippet = context[:120].replace("\n", " ") if context else "Educational Lecture Content"

    # Standard generic fallback matching VideoPackageSchema
    return {
        "video_title": f"Educational Video Lecture: {snippet[:40]}",
        "title": f"Educational Video Lecture: {snippet[:40]}",
        "target_duration_seconds": 30,
        "duration_seconds": 30,
        "narrator_script": f"Welcome to today's academic lesson. We are examining core topic concepts: {snippet}.",
        "scenes": [
            {
                "scene_number": 1,
                "background_color": "#0a0a0c",
                "narration_text": f"Welcome to today's lecture. We begin with fundamental concepts: {snippet[:80]}.",
                "subtitle_text": "ACADEMIC LESSON: FUNDAMENTAL PRINCIPLES",
                "visual_description": "Close-up motion graphic title card introducing lesson topic over dark cyber background.",
                "duration_seconds": 6
            },
            {
                "scene_number": 2,
                "background_color": "#0d0e14",
                "narration_text": f"Core Analysis: Reviewing structural mechanisms and functional relationships within the subject matter.",
                "subtitle_text": "DETAILED CONCEPT BREAKDOWN",
                "visual_description": "Wide diagram animation mapping structural concepts and definitions.",
                "duration_seconds": 14
            },
            {
                "scene_number": 3,
                "background_color": "#00f0ff",
                "narration_text": "Review the full curriculum text and apply these concepts to practical learning outcomes.",
                "subtitle_text": "SUMMARY & TOPIC MASTERY",
                "visual_description": "Interactive summary graphic highlighting key takeaways.",
                "duration_seconds": 10
            }
        ],
        "storyboard_scenes": [
            {
                "scene_id": 1,
                "duration": 6,
                "heading": "Scene 1: Introduction",
                "visual_description": "[Background #0a0a0c] Close-up motion graphic title card introducing lesson topic.",
                "on_screen_text": "ACADEMIC LESSON: FUNDAMENTAL PRINCIPLES",
                "voiceover_line": f"Welcome to today's lecture. We begin with fundamental concepts: {snippet[:80]}.",
                "b_roll_suggestion": "Abstract digital motion graphic"
            },
            {
                "scene_id": 2,
                "duration": 14,
                "heading": "Scene 2: Core Analysis",
                "visual_description": "[Background #0d0e14] Wide diagram animation mapping structural concepts.",
                "on_screen_text": "DETAILED CONCEPT BREAKDOWN",
                "voiceover_line": "Core Analysis: Reviewing structural mechanisms and functional relationships.",
                "b_roll_suggestion": "Conceptual diagram overlay"
            },
            {
                "scene_id": 3,
                "duration": 10,
                "heading": "Scene 3: Summary",
                "visual_description": "[Background #00f0ff] Interactive summary graphic.",
                "on_screen_text": "SUMMARY & TOPIC MASTERY",
                "voiceover_line": "Review the full curriculum text and apply these concepts.",
                "b_roll_suggestion": "Checklist animation"
            }
        ],
        "subtitles": [
            {"start": 0.0, "end": 6.0, "text": "ACADEMIC LESSON: FUNDAMENTAL PRINCIPLES"},
            {"start": 6.0, "end": 20.0, "text": "DETAILED CONCEPT BREAKDOWN"},
            {"start": 20.0, "end": 30.0, "text": "SUMMARY & TOPIC MASTERY"}
        ],
        "remotion_props": {
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "primaryColor": "#00f0ff",
            "backgroundColor": "#0a0a0c",
            "accentColor": "#3b82f6"
        }
    }
