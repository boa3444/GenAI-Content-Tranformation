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
    main_bullet_points: List[str] = Field(
        ...,
        description="Must contain at least 4 to 6 content-dense bullet points. Each bullet point MUST be a complete, detailed 2-line sentence explaining mechanisms, definitions, and applications, rather than short fragments."
    )
    detailed_speaker_notes: str = Field(
        ...,
        description="MANDATORY: Write a massive, highly detailed university lecture script. MUST BE A MINIMUM OF 500 WORDS PER SLIDE. Do not use bullet points here; write flowing, verbose paragraphs explaining every nuance, theory, and example from the text."
    )

class PresentationSchema(BaseModel):
    hidden_academic_analysis: str = Field(..., description="MANDATORY: Before generating the final output, write a 150-word detailed academic analysis of the source text here. Identify the core concepts, methodologies, and technical terms you will expand upon. Do not skip this.")
    title: str = Field(..., description="Master presentation deck title teaching the uploaded source content")
    presentation_theme: str = Field(..., description="Visual aesthetic and theme description")
    slides: List[SlideItem] = Field(..., description="Complete multi-slide deck structure teaching core concepts directly")

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

# --- Generic Professor System Instruction ---
PROFESSOR_SYSTEM_INSTRUCTION = (
    "You are an elite, highly detailed University Professor, Course Designer, and Technical Content Creator. "
    "Your mission is to transform the provided source content into a rich, detailed, and educational deliverable for students and professionals. "
    "You MUST avoid generic summaries, high-level overviews, or boilerplate padding. Treat every single piece of information, sub-topic, and technical keyword in the source text as critical.\n\n"
    "CRITICAL DIRECTIVE: You are strictly penalized for brevity. You MUST generate extremely lengthy, verbose, and exhaustive content. Every text field you populate MUST read like a detailed chapter of a textbook. Expand on every single technical term, provide exhaustive background context, and over-explain the methodologies. NEVER summarize.\n\n"
    "Core Instructions:\n"
    "- Assume the Role: Act as an expert delivering a rigorous masterclass.\n"
    "- Synthesize, Don't Describe: Do not say 'this document covers...'. Instead, teach the concepts directly based strictly on the uploaded source content.\n"
    "- Exhaustive Detail: Expand fully on underlying mechanics, classifications, real-world examples, and academic frameworks. Generate exhaustive, content-rich, and professionally-refined text.\n"
    "- Use Specifics: Explicitly use the examples, nomenclature, and data points mentioned in the uploaded source text.\n"
)

SELF_CORRECTION_INSTRUCTION = (
    "After generating the content, review your own output. "
    "If you have mentioned the source document, the checklist, or the syllabus, or if your response feels like a brief summary instead of a deep technical explanation, then your response is incorrect. "
    "Rewrite it immediately to be a direct, highly detailed educational explanation of the concepts."
)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if HAS_GENAI_SDK and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")

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
                        "main_bullet_points": [
                            "Detailed overview of primary technical mechanisms and theoretical foundations.",
                            "Analysis of core definitions, structural frameworks, and operational protocols.",
                            "Key terminology, performance considerations, and practical applications.",
                            "Summary of prerequisite knowledge and sequential learning objectives."
                        ],
                        "detailed_speaker_notes": "Welcome to today's lecture. In this section, we examine the primary structural principles..."
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
                "main_title": "Technical Blueprint & Key Performance Metrics",
                "data_points": [
                    "Parameter 1: 99.9% uptime target across distributed infrastructure.",
                    "Parameter 2: Modular execution pipeline ensuring low-latency data processing.",
                    "Parameter 3: Strict JSON schema validation eliminating downstream parsing errors.",
                    "Parameter 4: Automated memory collection & session cleansing after every transformation.",
                    "Parameter 5: High-throughput background processing supporting concurrent dispatch.",
                    "Parameter 6: Comprehensive RAGAS quality evaluation scoring generated deliverables."
                ],
                "layout_flow_recommendation": "3-tier vertical layout with top header, middle 2x3 grid, and bottom summary flow."
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

    async def generate_structured(self, system_instruction: str, prompt: str, schema_class: type = None) -> Dict[str, Any]:
        """Calls Gemini API requesting JSON output matching the target schema with max_output_tokens=8192."""
        if not self.client:
            logger.info("GenAI client unavailable. Returning fallback structure.")
            return self._get_fallback_for_schema(schema_class)

        full_system_instruction = f"{PROFESSOR_SYSTEM_INSTRUCTION}\n\n{system_instruction}"
        full_prompt = f"{prompt}\n\n{SELF_CORRECTION_INSTRUCTION}"

        for attempt in range(3):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    response_mime_type="application/json",
                    temperature=0.3, # Low temp for factual precision
                    max_output_tokens=8192,
                )
                if schema_class:
                    config.response_schema = schema_class

                # Upgraded model for deep reasoning and massive context handling
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash", 
                    contents=full_prompt,
                    config=config
                )
                try:
                    parsed = json.loads(response.text)
                    return parsed
                except (json.JSONDecodeError, Exception) as parse_err:
                    logger.error(f"Gemini structured JSON parsing error: {parse_err}. Attempting repair/fallback.")
                    return self._attempt_json_repair_or_fallback(getattr(response, "text", ""), schema_class)
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini API rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 20s before retry...")
                    await asyncio.sleep(20)
                    continue
                logger.error(f"Gemini API generation error (attempt {attempt + 1}/3): {e}")
                return self._get_fallback_for_schema(schema_class)

    async def generate_multimodal(
        self,
        system_instruction: str,
        prompt: str,
        image_bytes: bytes,
        mime_type: str,
        schema_class: type = None
    ) -> Dict[str, Any]:
        """Directly sends raw image bytes + prompt to Gemini vision model."""
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
                    temperature=0.3,
                    max_output_tokens=8192,
                )
                if schema_class:
                    config.response_schema = schema_class

                # Upgraded model
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=config
                )
                try:
                    parsed = json.loads(response.text)
                    return parsed
                except (json.JSONDecodeError, Exception) as parse_err:
                    logger.error(f"Gemini multimodal JSON parsing error: {parse_err}. Attempting repair/fallback.")
                    return self._attempt_json_repair_or_fallback(getattr(response, "text", ""), schema_class)
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini Multimodal API rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 20s before retry...")
                    await asyncio.sleep(20)
                    continue
                logger.error(f"Gemini multimodal API generation error (attempt {attempt + 1}/3): {e}")
                return self._get_fallback_for_schema(schema_class)

    async def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        """Lightweight unstructured text call to Gemini 3.6 Flash for Phase 1 Master Draft generation."""
        if not self.client:
            logger.info("GenAI client unavailable. Returning raw prompt.")
            return prompt

        full_system_instruction = f"{PROFESSOR_SYSTEM_INSTRUCTION}\n\n{system_instruction}" if system_instruction else PROFESSOR_SYSTEM_INSTRUCTION

        for attempt in range(3):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    temperature=0.4,
                    max_output_tokens=8192,
                )
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text
                return prompt
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "exhausted" in err_str or "rate" in err_str or "resource_exhausted" in err_str
                if is_rate_limit and attempt < 2:
                    logger.warning(f"Gemini generate_text rate limit 429 encountered (attempt {attempt + 1}/3). Waiting 20s before retry...")
                    await asyncio.sleep(20)
                    continue
                logger.error(f"Gemini generate_text API error (attempt {attempt + 1}/3): {e}")
                return prompt

gemini_service = GeminiService()
