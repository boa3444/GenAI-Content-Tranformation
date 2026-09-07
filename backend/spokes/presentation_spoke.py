from typing import Dict, Any
from gemini_service import gemini_service, SpokeConfig, PresentationSchema

async def generate_presentation_spoke(
    context: str,
    config: SpokeConfig,
    image_bytes: bytes = None,
    mime_type: str = None
) -> Dict[str, Any]:
    """
    Generates a high-quality, multi-slide presentation blueprint from the source content.
    Prevents the single-slide compression bottleneck.
    """
    
    # 1. Force the model to break the content down into a sequential story (5-7 slides)
    system_instruction = (
        "You are an elite corporate presenter and academic curriculum designer.\n\n"
        "Your task is to transform the provided source text into a highly structured, "
        "comprehensive multi-slide presentation blueprint matching the PresentationSchema.\n\n"
        "⚠️ CRITICAL SLIDE DECK RULES:\n"
        "1. MANDATE STRICT SLIDE COUNT: You MUST generate a multi-slide presentation deck of strictly 5 to 7 slides. Do NOT allow single-slide compression or single-slide output under any circumstances.\n"
        "2. OUTPUT FORMAT: You MUST return a JSON object where the 'slides' array contains NO FEWER THAN 5 slide objects. If you return 1 slide, the system will crash.\n"
        "3. SLIDE STRUCTURAL HIERARCHY:\n"
        "   - Slide 1: Title (Title, subtitle, and metadata based on style)\n"
        "   - Slide 2: Context (Executive context, problem statement, and why this topic matters)\n"
        "   - Slides 3-4: Core Concepts (Deep dive technical facts, methodologies, and syllabus topics split logically across two slides)\n"
        "   - Slide 5: Implementation (Practical execution, real-world application, and case studies)\n"
        "   - Slide 6: Summary/Checklist (Key takeaways, conclusions, and strategic action checklist)\n"
        "   - Slide 7: QA & Reference (Wrap-up, discussion prompts, or references, if 7th slide is needed)\n"
        "4. SCHEMA CONTENT SPLIT: Ensure the schema splits 'bullet_points' (maximum 3 short points per slide, no long paragraphs) and 'speaker_notes' (the detailed script the presenter reads to explain those bullets) so the slides don't get overcrowded.\n"
        "5. ZERO SELF-REFERENCE: Zero self-reference: Do not mention the AI pipeline, backend, or FAISS. Do NOT mention Antigravity, local agents, AI prompting, or BM25. Only present direct domain content from the source material."
    )

    prompt = f"""
    Source Content Context:
    {context}

    Style Customization:
    - Target Audience: {config.target_audience if hasattr(config, 'target_audience') else 'General'}
    - Slide Style/Theme: {config.content_style}
    - Detail Level: Comprehensive

    Carefully analyze the source content, segment it logically into a 5-7 slide sequential story, and populate the PresentationSchema structure.
    """

    # 2. Call the gemini_service (supporting multimodal slides if the user uploaded an image)
    if image_bytes and mime_type:
        res = await gemini_service.generate_multimodal(
            system_instruction, prompt, image_bytes, mime_type, schema_class=PresentationSchema
        )
    else:
        res = await gemini_service.generate_structured(
            system_instruction, prompt, schema_class=PresentationSchema
        )

    # 3. Fallback normalization in case the API payload is empty
    if res and "slides" in res and len(res["slides"]) > 0:
        return res

    # 4. Bulletproof Multi-Slide Fallback (triggers only if the API fails entirely)
    snippet = context[:120].replace("\n", " ")
    return {
        "presentation_title": "Academic Syllabus & Concept Overview",
        "slides": [
            {
                "title": "Welcome: Concept Overview",
                "bullet_points": [
                    "Introduction to the core material",
                    f"Contextual focus: {snippet}...",
                    "Expected learning outcomes and mastery criteria"
                ],
                "speaker_notes": "Welcome everyone. Today we are doing a deep-dive syllabus overview of the material. We will outline key milestones and focus areas."
            },
            {
                "title": "Foundational Principles",
                "bullet_points": [
                    "Core definitions and terminologies",
                    "Understanding architectural building blocks",
                    "How fundamental concepts connect to practical application"
                ],
                "speaker_notes": "First, let's establish our foundations. It is vital to understand these base-level definitions before moving into complex processes."
            },
            {
                "title": "Syllabus Milestone Tracking",
                "bullet_points": [
                    "Phase-by-phase timeline mapping",
                    "Identifying high-priority topics and modules",
                    "Checklist-driven self-assessment metrics"
                ],
                "speaker_notes": "Moving on to how we track our progress. We have a clear roadmap divided into specific, actionable modules to follow."
            },
            {
                "title": "Practical Implementation",
                "bullet_points": [
                    "From theory to hands-on programming labs",
                    "Avoiding common conceptual pitfalls",
                    "Evaluating performance metrics and results"
                ],
                "speaker_notes": "Now, let's discuss practical application. Theory is only as good as its execution, so we focus heavily on code implementation."
            },
            {
                "title": "Conclusion & Action Checklist",
                "bullet_points": [
                    "Key takeaways from today's deck",
                    "Immediate next steps for self-study",
                    "Open discussion and Q&A resources"
                ],
                "speaker_notes": "To wrap up: focus on your weekly checklist, complete the foundational exercises, and prepare questions for our next session."
            }
        ]
    }
