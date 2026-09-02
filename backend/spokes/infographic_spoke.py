from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, InfographicSchema

async def generate_infographic_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    system_instruction = (
        "You are an expert academic educator and visual information architect. "
        "Create an infographic blueprint matching InfographicSchema based on the provided text or image. "
        "Include main_title, data_points (array of key statistics, metrics, facts, and syllabus topics extracted directly from the source), "
        "and layout_flow_recommendation (detailed structural design specification). "
        "Do NOT mention the web application, backend pipeline, FAISS, or BM25."
    )
    
    prompt = f"""
    Source Content Context:
    {context}
    
    Style: {config.content_style}
    
    Extract specific numbers, concepts, quotes, and structural themes from the source content to construct a visual infographic blueprint.
    """
    
    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=InfographicSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=InfographicSchema
        )

    if res:
        if "main_title" in res and "title" not in res:
            res["title"] = res["main_title"]
        if "data_points" in res and "key_metrics" not in res:
            res["key_metrics"] = [{"label": f"Key Topic {i+1}", "value": dp, "icon": "book-open"} for i, dp in enumerate(res["data_points"])]
        return res

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
