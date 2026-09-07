import sys
import os
import asyncio
from dotenv import load_dotenv

# This forces Python to read your .env file and load your API keys!
load_dotenv()

import json
import logging

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from websocket_manager import manager

logger = logging.getLogger(__name__)

# Diagnostically check environment path
logger.info(f"Python Executable Path: {sys.executable}")

import google.genai as genai
from google.genai import types
HAS_GENAI_SDK = True

# Attempt to import google-genai SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False
    logger.warning("google-genai SDK not found. Fallback structures will be used if API key is not present.")

class SpokeConfig(BaseModel):
    target_audience: str = "General Corporate"
    tone: str = "Professional & Authoritative"
    language: str = "English"
    level_of_detail: str = "Exhaustive and Highly Technical"
    communication_objective: str = "Inform and Align"
    content_style: str = "Executive Brief"

# --- Granular Pydantic Schemas for Deliverable Spokes ---

class VideoScene(BaseModel):
    scene_number: int = Field(..., description="1-indexed sequence number of the scene")
    background_color: str = Field(default="#0a0a0c", description="Hex background color code (e.g., #0a0a0c, #00f0ff)")
    narration_text: str = Field(..., description="MANDATORY: Write a comprehensive, long-form documentary script for this scene. MUST BE A MINIMUM OF 400 WORDS PER SCENE. Detail every mechanism and real-world application extensively. Do not summarize.")
    subtitle_text: str = Field(..., description="On-screen subtitles text overlay highlighting the most critical terms.")
    visual_description: str = Field(..., description="Highly detailed description of images, diagrams, or graphics to display.")
    duration_seconds: int = Field(default=15, description="Duration of this scene in seconds (default 10-15 seconds for long narration).")

class VideoPackageSchema(BaseModel):
    hidden_academic_analysis: str = Field(..., description="MANDATORY: Before generating the final output, write a 150-word detailed academic analysis of the source text here. Identify the core concepts, methodologies, and technical terms you will expand upon. Do not skip this.")
    video_title: str = Field(..., description="Educational video title teaching the uploaded content")
    target_duration_seconds: int = Field(..., description="Total target duration in seconds")
    scenes: List[VideoScene] = Field(..., description="List of granular Remotion video scenes teaching the concepts in profound detail.")

# Alias for backward compatibility
VideoSchema = VideoPackageSchema

class SlideItem(BaseModel):
    slide_number: int = Field(..., description="Sequential slide number")
    title: str = Field(..., description="The title of the core concept being taught (e.g., 'Primary Structural Principles').")
    bullet_points: List[str] = Field(
        ...,
        description="Maximum 3 short, concise bullet points per slide so slides do not get overcrowded."
    )
    speaker_notes: str = Field(
        ...,
        description="Detailed script that the presenter reads to explain the slide's bullet points."
    )

class PresentationSchema(BaseModel):
    hidden_academic_analysis: str = Field(..., description="MANDATORY: Before generating the final output, write a 150-word detailed academic analysis of the source text here. Identify the core concepts, methodologies, and technical terms you will expand upon. Do not skip this.")
    title: str = Field(..., description="Master presentation deck title teaching the uploaded source content")
    presentation_theme: str = Field(..., description="Visual aesthetic and theme description")
    slides: List[SlideItem] = Field(..., description="An array containing EXACTLY 5 to 7 slide objects. MUST NOT be less than 5.")

class AdvisorySchema(BaseModel):
    hidden_academic_analysis: str = Field(..., description="MANDATORY: Before generating the final output, write a 150-word detailed academic analysis of the source text here. Identify the core concepts, methodologies, and technical terms you will expand upon. Do not skip this.")
    title: str = Field(..., description="Formal advisory document title teaching technical risk/concepts from source content")
    advisory_id: str = Field(..., description="Unique advisory code identifier")
    severity: str = Field(..., description="Impact & risk severity classification")
    executive_summary: str = Field(..., description="MANDATORY: Write a massive, comprehensive executive summary. MUST BE A MINIMUM OF 400 WORDS. Detail every technical risk, underlying cause, and operational context extensively in flowing paragraphs.")
    threat_or_context_analysis: str = Field(..., description="MANDATORY: Write an exhaustive, textbook-chapter level analysis. MUST BE A MINIMUM OF 600 WORDS. Deeply explain structural mechanics, threat vectors, system architecture, and real-world impacts.")
    detailed_recommendations: List[str] = Field(..., description="MANDATORY: At least 5 massive, highly detailed actionable recommendations. Each recommendation MUST be a comprehensive paragraph of at least 100 words.")
    conclusion: str = Field(..., description="Final strategic summary and educational directive.")

class LinkedInSchema(BaseModel):
    hook: str = Field(..., description="High-converting opening hook teaching a core concept from the source content")
    main_body: str = Field(..., description="MANDATORY: Write a deeply informative, highly detailed educational post. MUST BE A MINIMUM OF 400 WORDS. Include detailed technical breakdowns, specific definitions, and rich professional commentary.")
    hashtags: List[str] = Field(..., description="Targeted trending hashtags")
    suggested_image_prompt: str = Field(..., description="Detailed AI image generation prompt to accompany the post")

class TwitterSchema(BaseModel):
    hook: str = Field(..., description="Attention-grabbing opening tweet hook teaching a core concept")
    main_body: str = Field(..., description="Core tweet thesis summary teaching the concept")
    thread: List[str] = Field(..., description="MANDATORY: Write a series of 7 to 10 deeply detailed tweets forming a comprehensive masterclass thread. Each tweet MUST be as long and content-dense as possible, explaining technical parameters in detail.")
    hashtags: List[str] = Field(..., description="Targeted hashtags")
    suggested_image_prompt: str = Field(..., description="AI visual prompt for thread graphic")

class InfographicSchema(BaseModel):
    main_title: str = Field(..., description="Infographic master header teaching the concept")
    data_points: List[str] = Field(..., description="At least 6-8 extracted key statistics, complex metrics, and facts teaching concepts directly from the source content.")
    layout_flow_recommendation: str = Field(..., description="Detailed visual layout blueprint and structural diagram flow")

class ExecutiveSummarySchema(BaseModel):
    title: str = Field(..., description="Executive briefing title teaching concepts from the uploaded content")
    executive_abstract: str = Field(..., description="MANDATORY: Write a comprehensive, long-form master abstract. MUST BE A MINIMUM OF 500 WORDS. Provide exhaustive analytical explanations covering all methodologies, mechanisms, and strategic directives.")
    core_insights: List[str] = Field(..., description="At least 5 extracted core insights, written as detailed analytical explanations.")
    strategic_implications: List[str] = Field(..., description="Deep operational and technical implications.")
    recommended_next_steps: List[str] = Field(..., description="Clear strategic directives and next steps.")

# --- Production-Ready System Prompt ---
SYSTEM_PROMPT = f"""
[SYSTEM DIRECTIVE: STRICT DATA FORMATTING ENGINE]
You are a deterministic, production-grade data-formatting function operating within an automated content engine.
Your SOLE purpose is to process input payloads and produce rich, engaging, and highly structured technical deliverables.

[CRITICAL OUTPUT CONSTRAINTS]
1. ZERO CONVERSATIONAL FILLER: Strictly FORBIDDEN from generating preambles, introductory statements ("Here is...", "Sure!"), conversational fluff, concluding remarks, or meta-commentary.
2. STRICT DATA-FORMATTING MODE: Act purely as a data-formatting function. Return ONLY the formatted deliverable or valid structured JSON. Any conversational text outside the required payload is a critical protocol violation.
3. NO METADATA REFLECTION: Never mention prompt rules, schemas, instructions, checklists, or system prompt directives in your output text.

[STRUCTURAL & ENGAGEMENT MANDATES]
1. HIERARCHICAL MARKDOWN FORMATTING: Use H2 (##) and H3 (###) headers logically to structure content sections.
2. KEYWORD EMPHASIS: Bold (**term**) all critical domain nomenclature, technical definitions, key algorithms, and quantitative metrics.
3. LOGICAL BULLET POINTS: Use clear, content-dense bullet points for structural breakdowns, ensuring complete analytical depth in every point.
4. EXHAUSTIVE RICHNESS & RIGOR: Maintain textbook-level academic rigor, providing long-form, comprehensive explanations without summarizing or truncating data.
"""

PROFESSOR_SYSTEM_INSTRUCTION = SYSTEM_PROMPT

SELF_CORRECTION_INSTRUCTION = (
    "After generating the content, review your own output. "
    "If you have mentioned the source document, the checklist, or the syllabus, or if your response feels like a brief summary instead of a deep technical explanation, then your response is incorrect. "
    "Rewrite it immediately to be a direct, highly detailed educational explanation of the concepts."
)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self._context_cache_map: Dict[str, str] = {}
        if HAS_GENAI_SDK and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")

    def get_or_create_context_cache(self, text: str) -> Optional[str]:
        """
        Implements Google Context Caching for any content payload larger than 32k tokens.
        Prevents Gemini from re-analyzing the same content on repeated clicks.
        """
        if not self.client or not text:
            return None

        # 1 token is approx 4 characters (~32k tokens = 128k characters)
        estimated_tokens = len(text) // 4
        if estimated_tokens < 32000:
            return None

        import hashlib
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        if content_hash in self._context_cache_map:
            cached_name = self._context_cache_map[content_hash]
            logger.info(f"Reusing existing Gemini Context Cache (~{estimated_tokens} tokens): {cached_name}")
            return cached_name

        try:
            cached_content = self.client.caches.create(
                model="gemini-3.6-flash",
                config=types.CreateCachedContentConfig(
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=text)]
                        )
                    ],
                    display_name=f"cache_{content_hash[:10]}",
                    ttl="3600s"
                )
            )
            cached_name = cached_content.name
            self._context_cache_map[content_hash] = cached_name
            logger.info(f"Created new Gemini Context Cache for payload (~{estimated_tokens} tokens): {cached_name}")
            return cached_name
        except Exception as cache_err:
            logger.warning(f"Gemini Context Cache creation skipped/failed ({cache_err}). Continuing without cache.")
            return None

    def _attempt_json_repair_or_fallback(self, response_text: str, schema_class: type = None) -> Dict[str, Any]:
        """Attempts to repair truncated JSON, or returns a safe schema fallback dictionary."""
        if not response_text:
            return self._get_fallback_for_schema(schema_class)

        text = response_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except Exception:
            logger.warning("Direct json.loads failed. Attempting JSON repair for truncated response.")

        # Attempt repairing truncated JSON by closing unclosed strings and brackets/braces
        try:
            in_string = False
            escape = False
            stack = []
            clean_chars = []

            for ch in text:
                if escape:
                    clean_chars.append(ch)
                    escape = False
                    continue
                if ch == '\\':
                    clean_chars.append(ch)
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    clean_chars.append(ch)
                    continue
                if in_string:
                    clean_chars.append(ch)
                    continue
                if ch in '{[':
                    stack.append(ch)
                    clean_chars.append(ch)
                elif ch in '}]':
                    if stack:
                        top = stack[-1]
                        if (ch == '}' and top == '{') or (ch == ']' and top == '['):
                            stack.pop()
                    clean_chars.append(ch)
                else:
                    clean_chars.append(ch)

            if in_string:
                clean_chars.append('"')

            repaired_str = "".join(clean_chars).rstrip().rstrip(',')
            for item in reversed(stack):
                if item == '{':
                    repaired_str += '}'
                elif item == '[':
                    repaired_str += ']'

            repaired_json = json.loads(repaired_str)
            logger.info("JSON repair successfully recovered truncated response.")
            return repaired_json
        except Exception as e:
            logger.warning(f"JSON repair failed ({e}). Returning schema fallback structure.")

        return self._get_fallback_for_schema(schema_class)

    def _get_fallback_for_schema(self, schema_class: type = None) -> Dict[str, Any]:
        schema_name = schema_class.__name__ if schema_class else ""
        if schema_class == VideoPackageSchema or schema_name in ["VideoPackageSchema", "VideoSchema"]:
            return {
                "hidden_academic_analysis": "Comprehensive academic analysis of core concepts, protocols, and technical frameworks from the uploaded document.",
                "video_title": "Educational Video Lecture: Core Analysis",
                "target_duration_seconds": 30,
                "scenes": [
                    {
                        "scene_number": 1,
                        "background_color": "#0a0a0c",
                        "narration_text": "Welcome to today's lecture. We examine fundamental principles and core structural definitions.",
                        "subtitle_text": "ACADEMIC LESSON: CORE PRINCIPLES",
                        "visual_description": "Title card displaying core subject over dark motion background.",
                        "duration_seconds": 10
                    },
                    {
                        "scene_number": 2,
                        "background_color": "#0d0e14",
                        "narration_text": "Detailed analysis of structural frameworks, definitions, and technical parameters.",
                        "subtitle_text": "TECHNICAL BREAKDOWN",
                        "visual_description": "Diagram animation highlighting concept interactions.",
                        "duration_seconds": 20
                    }
                ]
            }
        elif schema_class == PresentationSchema or schema_name == "PresentationSchema":
            return {
                "hidden_academic_analysis": "Comprehensive academic analysis of core concepts, protocols, and technical frameworks from the uploaded document.",
                "title": "Academic Presentation: Core Concepts",
                "presentation_theme": "Academic / Dark Theme",
                "slides": [
                    {
                        "slide_number": 1,
                        "title": "Fundamental Concepts & Principles",
                        "bullet_points": [
                            "Detailed overview of primary technical mechanisms and theoretical foundations.",
                            "Analysis of core definitions, structural frameworks, and operational protocols.",
                            "Key terminology, performance considerations, and practical applications."
                        ],
                        "speaker_notes": "Welcome to today's lecture. In this section, we examine the primary structural principles..."
                    }
                ]
            }
        elif schema_class == AdvisorySchema or schema_name == "AdvisorySchema":
            return {
                "hidden_academic_analysis": "Comprehensive academic analysis of core concepts, protocols, and technical frameworks from the uploaded document.",
                "title": "Technical Advisory: Risk & Mitigation Blueprints",
                "advisory_id": "ADV-2026-001",
                "severity": "HIGH / ACTION REQUIRED",
                "executive_summary": "Comprehensive technical advisory detailing structural risks and operational impacts.",
                "threat_or_context_analysis": "Exhaustive analysis explaining operational mechanics and risk mitigation strategies.",
                "detailed_recommendations": [
                    "Review primary technical specifications and protocol guidelines.",
                    "Implement robust error handling and fallback mechanisms across all components.",
                    "Conduct thorough system audit and performance evaluation."
                ],
                "conclusion": "Adhering to these recommendations ensures operational resilience and stability."
            }
        elif schema_class == LinkedInSchema or schema_name == "LinkedInSchema":
            return {
                "hook": "🚀 Technical Breakdown: Core Takeaways & Architectural Insights",
                "main_body": "Deep dive into structural mechanisms and technical frameworks. Key takeaways highlight operational efficiency, robust error handling, and scalable design.",
                "hashtags": ["#TechLeadership", "#Architecture", "#Engineering", "#Innovation"],
                "suggested_image_prompt": "High-tech 3D architectural diagram with glowing nodes on dark background."
            }
        elif schema_class == TwitterSchema or schema_name == "TwitterSchema":
            return {
                "hook": "🧵 Technical Thread: Essential parameters & system design principles",
                "main_body": "Comprehensive educational thread mapping out core mechanisms and real-world impacts.",
                "thread": [
                    "1/ Understanding system architecture requires examining fundamental operational principles.",
                    "2/ Key metrics demonstrate significant performance gains when modular components are decoupled.",
                    "3/ Implementing standard fallback strategies prevents cascading downstream failures.",
                    "4/ Strategic summary: Resilience and clear schemas drive overall system stability."
                ],
                "hashtags": ["#TechThread", "#SystemDesign", "#Engineering"],
                "suggested_image_prompt": "Minimalist high-tech graphic showing data flows."
            }
        elif schema_class == InfographicSchema or schema_name == "InfographicSchema":
            return {
                "main_title": "Source Content Infographic & Key Findings",
                "data_points": [
                    "Key Metric 1: Core foundational principles and conceptual frameworks from source text.",
                    "Key Metric 2: Primary operational benchmarks and system definitions.",
                    "Key Metric 3: Strategic findings and practical implementation guidelines.",
                    "Key Metric 4: Key performance indicators and topic mastery milestones."
                ],
                "layout_flow_recommendation": "3-tier vertical layout with top header banner, central metric grid, and bottom summary flow."
            }
        elif schema_class == ExecutiveSummarySchema or schema_name == "ExecutiveSummarySchema":
            return {
                "title": "Executive Briefing: Technical Frameworks & Strategic Directives",
                "executive_abstract": "Comprehensive briefing detailing operational mechanisms, analytical insights, and strategic directives.",
                "core_insights": [
                    "Decoupled modular architecture optimizes processing speed and error isolation.",
                    "Strict JSON schema enforcement guarantees structured integration with downstream applications.",
                    "Automated fallback strategies ensure continuous availability during high-load scenarios."
                ],
                "strategic_implications": [
                    "Higher reliability and reduced error rates in automated content transformation pipelines.",
                    "Enhanced maintenance velocity due to standardized payload schemas."
                ],
                "recommended_next_steps": [
                    "Deploy updated schema handlers to production environment.",
                    "Monitor error rates and WebSocket status broadcasts."
                ]
            }
        return {
            "title": "Generated Artifact",
            "content": "Analysis completed matching required schema specifications."
        }

    async def generate_structured(
        self,
        system_instruction: str,
        prompt: str,
        schema_class: type = None,
        client_id: Optional[str] = None,
        spoke_name: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calls Gemini API requesting JSON output matching the target schema with streaming & max_output_tokens=8192."""
        if not self.client:
            logger.info("GenAI client unavailable. Returning fallback structure.")
            return self._get_fallback_for_schema(schema_class)

        full_system_instruction = f"{PROFESSOR_SYSTEM_INSTRUCTION}\n\n{system_instruction}"
        full_prompt = f"{prompt}\n\n{SELF_CORRECTION_INSTRUCTION}"
        cached_name = self.get_or_create_context_cache(prompt)

        for attempt in range(3):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    response_mime_type="application/json",
                    temperature=0.7,
                    max_output_tokens=8192,
                )
                if schema_class:
                    config.response_schema = schema_class
                if cached_name:
                    config.cached_content = cached_name

                full_text = ""
                try:
                    response_stream = await self.client.aio.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=full_prompt,
                        config=config
                    )
                    async for chunk in response_stream:
                        if chunk.text:
                            full_text += chunk.text
                            if client_id:
                                await manager.broadcast_stream_chunk(client_id, spoke_name or "structured", chunk.text, session_id)
                except Exception as stream_err:
                    logger.warning(f"Async streaming error ({stream_err}), falling back to generate_content.")
                    response = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=full_prompt,
                        config=config
                    )
                    full_text = response.text or ""

                try:
                    parsed = json.loads(full_text)
                    return parsed
                except (json.JSONDecodeError, Exception) as parse_err:
                    logger.error(f"Gemini structured JSON parsing error: {parse_err}. Attempting repair/fallback.")
                    return self._attempt_json_repair_or_fallback(full_text, schema_class)
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini API rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 2s before retry...")
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Gemini API generation error (attempt {attempt + 1}/3): {e}")
                return self._get_fallback_for_schema(schema_class)

    async def generate_multimodal(
        self,
        system_instruction: str,
        prompt: str,
        image_bytes: bytes,
        mime_type: str,
        schema_class: type = None,
        client_id: Optional[str] = None,
        spoke_name: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Directly sends raw image bytes + prompt to Gemini vision model with streaming chunks."""
        if not self.client:
            logger.info("GenAI client unavailable. Returning fallback structure.")
            return self._get_fallback_for_schema(schema_class)

        full_system_instruction = f"{PROFESSOR_SYSTEM_INSTRUCTION}\n\n{system_instruction}"
        full_prompt = (
            f"Analyze the provided image (diagram, chart, screenshot, or document) completely. "
            f"Use ONLY the image content to generate the requested artifact.\n\n{prompt}\n\n{SELF_CORRECTION_INSTRUCTION}"
        )

        for attempt in range(3):
            try:
                image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                contents = [image_part, full_prompt]

                config = types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    response_mime_type="application/json",
                    temperature=0.7,
                    max_output_tokens=8192,
                )
                if schema_class:
                    config.response_schema = schema_class

                full_text = ""
                try:
                    response_stream = await self.client.aio.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=contents,
                        config=config
                    )
                    async for chunk in response_stream:
                        if chunk.text:
                            full_text += chunk.text
                            if client_id:
                                await manager.broadcast_stream_chunk(client_id, spoke_name or "multimodal", chunk.text, session_id)
                except Exception as stream_err:
                    logger.warning(f"Async multimodal streaming error ({stream_err}), falling back to generate_content.")
                    response = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents,
                        config=config
                    )
                    full_text = response.text or ""

                try:
                    parsed = json.loads(full_text)
                    return parsed
                except (json.JSONDecodeError, Exception) as parse_err:
                    logger.error(f"Gemini multimodal JSON parsing error: {parse_err}. Attempting repair/fallback.")
                    return self._attempt_json_repair_or_fallback(full_text, schema_class)
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini Multimodal API rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 2s before retry...")
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Gemini multimodal API generation error (attempt {attempt + 1}/3): {e}")
                return self._get_fallback_for_schema(schema_class)

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        client_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Lightweight unstructured text call to Gemini Flash with streaming chunks over WebSocket."""
        if not self.client:
            logger.info("GenAI client unavailable. Returning raw prompt.")
            return prompt

        full_system_instruction = f"{PROFESSOR_SYSTEM_INSTRUCTION}\n\n{system_instruction}" if system_instruction else PROFESSOR_SYSTEM_INSTRUCTION
        cached_name = self.get_or_create_context_cache(prompt)

        for attempt in range(3):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    temperature=0.7,
                    max_output_tokens=8192,
                )
                if cached_name:
                    config.cached_content = cached_name
                full_text = ""
                try:
                    response_stream = await self.client.aio.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=prompt,
                        config=config
                    )
                    async for chunk in response_stream:
                        if chunk.text:
                            full_text += chunk.text
                            if client_id:
                                await manager.broadcast_stream_chunk(client_id, "master_draft", chunk.text, session_id)
                except Exception as stream_err:
                    logger.warning(f"Async generate_text streaming error ({stream_err}), falling back to generate_content.")
                    response = self.client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                        config=config
                    )
                    full_text = response.text or ""

                if full_text:
                    return full_text
                return prompt
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini generate_text rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 2s before retry...")
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Gemini generate_text API error (attempt {attempt + 1}/3): {e}")
                return prompt

gemini_service = GeminiService()
