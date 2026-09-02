from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, LinkedInSchema

async def generate_linkedin_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    system_instruction = (
        "You are an elite B2B Content Strategist and LinkedIn Thought Leader. "
        "Create an in-depth, professional LinkedIn publication matching the LinkedInSchema based on the provided text or image. "
        "Include hook, main_body (incorporating specific data points, quotes, and analytical insights from the source content/diagram), hashtags, and suggested_image_prompt."
    )
    
    prompt = f"""
    Source Content Context:
    {context}
    
    Configuration Parameters:
    - Audience: {config.target_audience}
    - Tone: {config.tone}
    - Objective: {config.communication_objective}
    
    Write a comprehensive LinkedIn post. Embed specific quotes, statistics, or diagram details from the source content into the main_body.
    """
    
    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=LinkedInSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=LinkedInSchema
        )

    if res:
        if "hook" in res and "main_body" in res and "headline" not in res:
            res["headline"] = res["hook"]
        if "main_body" in res and "post_body" not in res:
            res["post_body"] = res["main_body"]
        return res

    fallback_hook = "🚀 Strategic Update: Key Insights & Industry Impact"
    fallback_body = (
        f"Organizations face rapidly shifting dynamics. Here is a high-impact breakdown of our latest intelligence:\n\n"
        f"📌 Core Finding & Quotes: {context[:350]}\n\n"
        f"Key operational implications include streamlined decision-making, proactive risk mitigation, and heightened responsiveness.\n\n"
        f"How is your team addressing these strategic priorities this quarter?"
    )

    return {
        "hook": fallback_hook,
        "headline": fallback_hook,
        "main_body": fallback_body,
        "post_body": fallback_body,
        "hashtags": ["#Leadership", "#Innovation", "#StrategicIntelligence", "#OperationalExcellence", "#AI"],
        "suggested_image_prompt": "A modern 3D corporate visual depicting data streams transforming into glowing neon blue geometric insights over a sleek dark background."
    }
