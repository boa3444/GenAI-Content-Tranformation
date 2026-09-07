import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from websocket_manager import manager
from retrieval import get_hybrid_context
from gemini_service import (
    SpokeConfig,
    gemini_service,
    VideoPackageSchema,
    PresentationSchema,
    AdvisorySchema,
    LinkedInSchema,
    TwitterSchema,
    InfographicSchema,
    ExecutiveSummarySchema
)
from translation_service import translator
from qa_evaluator import evaluate_quality

logger = logging.getLogger(__name__)

SPOKE_MAPPING = {
    "video": {
        "schema": VideoPackageSchema,
        "prompt_generator": lambda draft: f"You are a Computer Science Professor. Based strictly on the academic master draft inside <source_content>, write a massive multi-scene video script matching VideoPackageSchema. For each scene's narration, you MUST write a comprehensive documentary script containing AT LEAST 400 WORDS PER SCENE. Explain every definition, algorithm, and real-world example in profound, exhaustive detail. Do NOT summarize or shorten anything.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "presentation": {
        "schema": PresentationSchema,
        "prompt_generator": lambda draft: f"Create a master-class presentation matching PresentationSchema. Based strictly on the master draft inside <source_content>, write at least 500 words of flowing, highly technical lecture text for each slide's speaker notes. Write out complete, verbose explanations of every single theory, mechanism, and example from the draft. Do not compress or summarize the source text.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "advisory": {
        "schema": AdvisorySchema,
        "prompt_generator": lambda draft: f"Generate an exhaustive, textbook-length formal technical advisory document matching AdvisorySchema based strictly on the text inside <source_content>. You MUST write at least 400 words for the executive summary and at least 600 words for the threat analysis. Detail every structural risk, underlying mechanism, and mitigation blueprint in massive detail.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "linkedin": {
        "schema": LinkedInSchema,
        "prompt_generator": lambda draft: f"Draft a massive, deeply informative academic thought leadership post matching LinkedInSchema based strictly on the text inside <source_content>. You MUST write at least 400 words of flowing text in main_body, teaching the technical parameters, definitions, and metrics from the draft in exhaustive detail.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "twitter": {
        "schema": TwitterSchema,
        "prompt_generator": lambda draft: f"Create a comprehensive 7 to 10-tweet educational masterclass thread matching TwitterSchema based strictly on the text inside <source_content>. Make each tweet in the thread as long, dense, and detailed as possible, explaining technical parameters in exhaustive depth.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "infographic": {
        "schema": InfographicSchema,
        "prompt_generator": lambda draft: f"You are strictly an information extractor. Create an infographic blueprint matching InfographicSchema. Your data_points and layout must ONLY contain facts, numbers, and concepts explicitly written in <source_content>. Do NOT mention Antigravity, FAISS, BM25, LLM, Agent, Prompt, or Backend. Do not invent system diagrams about how you process data.\n\n<source_content>\n{draft}\n</source_content>"
    },
    "summary": {
        "schema": ExecutiveSummarySchema,
        "prompt_generator": lambda draft: f"Write a massive executive briefing matching ExecutiveSummarySchema based strictly on the text inside <source_content>. You MUST write at least 500 words for the executive abstract, explaining the advanced technical mechanisms and academic frameworks in exhaustive detail.\n\n<source_content>\n{draft}\n</source_content>"
    }
}

async def dispatch_hub_and_spoke(
    client_id: str,
    source_text: str,
    selected_spokes: List[str],
    config_dict: Dict[str, Any],
    page_count: int = 1,
    session_id: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None
):
    valid_spokes = [s for s in selected_spokes if s in SPOKE_MAPPING]
    total_spokes = len(valid_spokes)
    if total_spokes == 0:
        return

    await manager.send_json(client_id, {
        "event": "status_update",
        "job_id": session_id,
        "status": "processing",
        "progress": 5,
        "message": "Extracting context..."
    })

    # Step 1: Context Retrieval
    objective_query = f"Generate overview for: {config_dict}"
    full_context = get_hybrid_context(source_text, objective_query, page_count=page_count)
    
    if not full_context or not full_context.strip():
        await manager.send_json(client_id, {
            "event": "error",
            "job_id": session_id,
            "message": "Failed to extract text."
        })
        return

    # PHASE 1: Generate Unstructured Academic Master Draft (Thinking Phase)
    await manager.send_json(client_id, {
        "event": "status_update",
        "job_id": session_id,
        "status": "processing",
        "progress": 10,
        "message": "Phase 1: Generating Unstructured Academic Master Draft (2,000+ words)..."
    })
    await manager.broadcast_status(
        client_id,
        step="master_draft",
        progress=10,
        message="Phase 1: Generating Unstructured Academic Master Draft (2,000+ words)..."
    )

    draft_prompt = (
        "You are an elite, highly detailed University Professor. Study the provided source context "
        "inside <source_content> and write an exhaustive, highly technical academic draft. Expand fully "
        "on every definition, theoretical framework, classification, and real-world example found in the "
        "document. Do not summarize. Write a comprehensive, long-form master reference guide containing "
        "at least 2,000 words explaining these concepts.\n\n<source_content>\n" + full_context + "\n</source_content>"
    )

    academic_master_draft = await gemini_service.generate_text(
        prompt=draft_prompt,
        system_instruction="You are an elite, highly detailed University Professor and Course Designer.",
        client_id=client_id,
        session_id=session_id
    )

    if not academic_master_draft or not academic_master_draft.strip():
        logger.warning("Academic master draft generation returned empty text. Falling back to full context.")
        academic_master_draft = full_context

    await manager.send_json(client_id, {
        "event": "status_update",
        "job_id": session_id,
        "status": "processing",
        "progress": 20,
        "message": f"Phase 2: Concurrently processing {total_spokes} structural deliverable spokes..."
    })

    # PHASE 2: Async Parallel Execution (Concurrent Spoke Generation)
    async def process_spoke(spoke_name: str) -> Optional[Dict[str, Any]]:
        spoke_config = SPOKE_MAPPING[spoke_name]
        try:
            await manager.send_json(client_id, {
                "event": "status_update",
                "job_id": session_id,
                "status": "processing",
                "spoke": spoke_name,
                "progress": 30,
                "message": f"Generating spoke: {spoke_name.upper()}..."
            })
            await manager.broadcast_status(
                client_id,
                step="spoke_dispatch",
                progress=30,
                message=f"Generating spoke: {spoke_name.upper()}..."
            )

            prompt = spoke_config["prompt_generator"](academic_master_draft)
            system_instruction = f"User config: {config_dict}. You MUST act as an elite Technical Expert. Use the provided master draft to format rich outputs."
            
            if image_bytes:
                result_data = await gemini_service.generate_multimodal(
                    system_instruction, prompt, image_bytes, mime_type, spoke_config["schema"],
                    client_id=client_id, spoke_name=spoke_name, session_id=session_id
                )
            else:
                result_data = await gemini_service.generate_structured(
                    system_instruction, prompt, spoke_config["schema"],
                    client_id=client_id, spoke_name=spoke_name, session_id=session_id
                )
            
            if result_data:
                if isinstance(result_data, dict):
                    # UI compatibility field aliases
                    if spoke_name == "video":
                        if "video_title" in result_data and "title" not in result_data:
                            result_data["title"] = result_data["video_title"]
                        if "target_duration_seconds" in result_data and "duration_seconds" not in result_data:
                            result_data["duration_seconds"] = result_data["target_duration_seconds"]
                        if "scenes" in result_data:
                            storyboard_scenes = []
                            subtitles = []
                            curr_time = 0.0
                            for scene_idx, scene in enumerate(result_data["scenes"]):
                                dur = scene.get("duration_seconds", 6)
                                bg = scene.get("background_color", "#0a0a0c")
                                narr = scene.get("narration_text", "")
                                sub = scene.get("subtitle_text", narr)
                                vis = scene.get("visual_description", "")
                                storyboard_scenes.append({
                                    "scene_id": scene.get("scene_number", scene_idx + 1),
                                    "duration": dur,
                                    "heading": f"Scene {scene.get('scene_number', scene_idx + 1)}",
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
                            result_data["storyboard_scenes"] = storyboard_scenes
                            result_data["subtitles"] = subtitles

                    elif spoke_name == "presentation":
                        if "slides" in result_data:
                            for s in result_data["slides"]:
                                if "main_bullet_points" in s and "bullet_points" not in s:
                                    s["bullet_points"] = s["main_bullet_points"]
                                if "detailed_speaker_notes" in s and "speaker_notes" not in s:
                                    s["speaker_notes"] = s["detailed_speaker_notes"]

                    elif spoke_name == "advisory":
                        if "threat_or_context_analysis" in result_data and "key_findings" not in result_data:
                            result_data["key_findings"] = [result_data["threat_or_context_analysis"]]
                        if "detailed_recommendations" in result_data and "recommended_actions" not in result_data:
                            result_data["recommended_actions"] = result_data["detailed_recommendations"]
                        if "executive_summary" in result_data and "executive_overview" not in result_data:
                            result_data["executive_overview"] = result_data["executive_summary"]

                    elif spoke_name == "linkedin":
                        if "hook" in result_data and "main_body" in result_data and "headline" not in result_data:
                            result_data["headline"] = result_data["hook"]
                        if "main_body" in result_data and "post_body" not in result_data:
                            result_data["post_body"] = result_data["main_body"]

                    elif spoke_name == "twitter":
                        if "hook" in result_data and "single_tweet" not in result_data:
                            result_data["single_tweet"] = f"{result_data['hook']} {result_data.get('suggested_image_prompt', '')[:50]}"

                    elif spoke_name == "infographic":
                        if "main_title" in result_data and "title" not in result_data:
                            result_data["title"] = result_data["main_title"]
                        if "data_points" in result_data and "key_metrics" not in result_data:
                            result_data["key_metrics"] = [{"label": f"Key Topic {i+1}", "value": dp, "icon": "book-open"} for i, dp in enumerate(result_data["data_points"])]

                payload_msg = {
                    "event": "spoke_result",
                    "job_id": session_id,
                    "spoke": spoke_name,
                    "status": "completed",
                    "payload": result_data
                }
                await manager.send_json(client_id, payload_msg)
                await manager.broadcast_spoke_result(client_id, spoke_name, {"spoke": spoke_name, "data": result_data})
                return result_data
            else:
                await manager.send_json(client_id, {
                    "event": "spoke_result",
                    "job_id": session_id,
                    "spoke": spoke_name,
                    "status": "failed",
                    "error": "Generated payload was empty or invalid."
                })
                return None
        except Exception as e:
            logger.error(f"Failed spoke {spoke_name}: {e}")
            await manager.send_json(client_id, {
                "event": "spoke_result",
                "job_id": session_id,
                "spoke": spoke_name,
                "status": "failed",
                "error": str(e)
            })
            return None

    # Execute all selected spokes concurrently in parallel using asyncio.gather
    spoke_tasks = [process_spoke(spoke_name) for spoke_name in valid_spokes]
    results = await asyncio.gather(*spoke_tasks, return_exceptions=True)
    completed_count = sum(1 for r in results if r and not isinstance(r, Exception))

    # Finish Pipeline
    await manager.send_json(client_id, {
        "event": "status_update",
        "job_id": session_id,
        "status": "completed",
        "progress": 100,
        "message": "All tasks completed successfully!"
    })
    await manager.broadcast_status(
        client_id,
        step="complete",
        progress=100,
        message="All deliverables generated successfully!",
        data={"total_spokes": completed_count, "session_id": session_id}
    )
