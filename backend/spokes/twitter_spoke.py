from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, TwitterSchema

async def generate_twitter_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    system_instruction = (
        "You are a top Twitter/X Tech & Policy Analyst. "
        "Create a comprehensive tweet thread matching the TwitterSchema based on the provided text or image. "
        "Include hook, main_body, thread (array of 4-6 tweets under 280 chars each with specific quotes/stats from the source), hashtags, and suggested_image_prompt."
    )
    
    prompt = f"""
    Source Content Context:
    {context}
    
    Target Audience: {config.target_audience}
    Tone: {config.tone}
    
    Generate an engaging thread extracting key quotes, statistics, and takeaways.
    """
    
    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=TwitterSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=TwitterSchema
        )

    if res:
        if "hook" in res and "single_tweet" not in res:
            res["single_tweet"] = f"{res['hook']} {res.get('suggested_image_prompt', '')[:50]}"
        return res

    return {
        "hook": f"🚨 NEW ANALYSIS: Key insights on {context[:100]}...",
        "main_body": f"Comprehensive breakdown of source intelligence: {context[:250]}",
        "single_tweet": f"🚨 NEW ANALYSIS: Key insights on {context[:120]}... Read the full breakdown below 🧵👇 #TechNews #Analysis",
        "thread": [
            f"1/ 🧵 Breaking down the latest intelligence: {context[:180]}...",
            f"2/ Key Quote & Data: {context[180:350]}",
            f"3/ Operational impact: Reduced turnaround times, standardized communication across channels, and automated compliance.",
            f"4/ Summary: Staying ahead requires intelligent automation built directly into core workflows. Thoughts? 👇"
        ],
        "hashtags": ["#TechNews", "#AI", "#DataAnalytics", "#StrategicIntelligence"],
        "suggested_image_prompt": "Minimalist high-tech Twitter header graphic with neon blue nodes and data connectivity."
    }
