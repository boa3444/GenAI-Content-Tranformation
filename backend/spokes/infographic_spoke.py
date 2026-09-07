from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, InfographicSchema

async def generate_infographic_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    
    # Strict boundary system instruction targeting only source content
    system_instruction = (
        "You are strictly an information extractor and visual infographic designer.\n\n"
        "Your task is to transform the provided source text into an infographic blueprint matching InfographicSchema.\n\n"
        "🚫 UNBREAKABLE NEGATIVE PROMPT - FORBIDDEN WORDS:\n"
        "Zero self-reference: Do NOT use, mention, or reference any of the following forbidden words under any circumstances: "
        "\"Antigravity\", \"FAISS\", \"BM25\", \"LLM\", \"Agent\", \"Prompt\", \"Backend\".\n\n"
        "⚠️ CRITICAL MANDATE:\n"
        "You are strictly an information extractor. Your data_points and layout must ONLY contain facts, numbers, and concepts explicitly written in the Source Content Context. Do not invent system diagrams about how you process data.\n\n"
        "SCHEMA REQUIREMENTS:\n"
        "1. main_title: Captivating headline summarizing the primary subject from the source content.\n"
        "2. data_points: Array of key statistics, metrics, facts, and concepts extracted directly from the source content.\n"
        "3. layout_flow_recommendation: Visual blueprint and structural flow describing how to render these source facts visually."
    )

    prompt = f"""
    Source Content Context:
    {context}

    Style: {config.content_style}

    Extract specific numbers, concepts, quotes, and structural themes strictly from the source content context above to construct a visual infographic blueprint.
    Do NOT mention Antigravity, FAISS, BM25, LLM, Agent, Prompt, or Backend. Do not invent system diagrams about how you process data.
    """

    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=InfographicSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=InfographicSchema
        )

    # Normalize response JSON structures to match the frontend expectations
    if res:
        if "main_title" in res and "title" not in res:
            res["title"] = res["main_title"]
        if "data_points" in res and "key_metrics" not in res:
            res["key_metrics"] = [
                {"label": f"Key Topic {i+1}", "value": dp, "icon": "book-open"} 
                for i, dp in enumerate(res["data_points"])
            ]
        return res

    # Fallback response if API fails
    snippet = context[:150].replace("\n", " ")

    return {
        "main_title": "ACADEMIC INFOGRAPHIC: Concept & Syllabus Overview",
        "title": "ACADEMIC INFOGRAPHIC: Concept & Syllabus Overview",
        "data_points": [
            f"Core Topic 1: {snippet}",
            "Fundamental Principles: Key definitions and architectural frameworks",
            "Functional Analysis: System components and protocol structures",
            "Practical Application: Self-assessment and checklist outcomes"
        ],
        "key_metrics": [
            {"label": "Module Coverage", "value": "100%", "icon": "check-circle"},
            {"label": "Core Concepts", "value": "Essential", "icon": "book-open"},
            {"label": "Practical Focus", "value": "Applied", "icon": "zap"}
        ],
        "layout_flow_recommendation": (
            "3-Tier Vertical Layout: Top Hero Banner introducing the primary subject title and core thesis; "
            "Middle 2x2 Grid displaying core concept cards with high-contrast highlight borders; "
            "Bottom Timeline Diagram mapping sequential learning outcomes and topic checklists."
        )
    }
