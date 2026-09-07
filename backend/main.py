import os
import uuid
import logging
import gc
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from websocket_manager import manager
from parsers import parse_source_document
from retrieval import reset_global_retrieval_state, global_vector_db, global_chunks
from spokes.dispatcher import dispatch_hub_and_spoke

# ==========================================
# 🔐 Environment Configuration & Startup Check
# ==========================================

# 1. Load environment variables from your local .env file
load_dotenv()

# 2. Access the Gemini API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 3. Add a critical startup safety check 
if not GEMINI_API_KEY:
    raise ValueError(
        "🔴 FATAL ERROR: GEMINI_API_KEY is not set in the environment or a .env file. "
        "The application cannot start. Please create a .env file containing: GEMINI_API_KEY=\"your_key_here\""
    )

# ==========================================
# ⚙️ Logging & FastAPI Core Setup
# ==========================================

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ai_content_engine")

app = FastAPI(
    title="AI-Powered Content Transformation Engine API",
    description="Hub-and-Spoke Content Transformation Platform with BM25 + FAISS Retrieval & Real-time WebSockets",
    version="1.0.0"
)

# Enable CORS for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🔌 Endpoints & WebSockets
# ==========================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AI Content Transformation Engine API",
        "version": "1.0.0",
        "sla_target_seconds": 45
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Keep-alive receiver loop
            data = await websocket.receive_text()
            logger.debug(f"Received WS ping from {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# ==========================================
# 📥 Request Models & Ingestion Endpoint
# ==========================================

class TransformTextRequest(BaseModel):
    client_id: str
    text_content: str
    selected_spokes: List[str]
    target_audience: Optional[str] = "General Corporate"
    tone: Optional[str] = "Professional & Authoritative"
    language: Optional[str] = "English"
    level_of_detail: Optional[str] = "Comprehensive"
    communication_objective: Optional[str] = "Inform and Align"
    content_style: Optional[str] = "Executive Brief"

@app.post("/api/transform")
async def transform_content(
    background_tasks: BackgroundTasks,
    client_id: str = Form(...),
    text_content: Optional[str] = Form(None),
    selected_spokes: str = Form(...),  # Comma separated list or JSON string
    target_audience: str = Form("General Corporate"),
    tone: str = Form("Professional & Authoritative"),
    language: str = Form("English"),
    level_of_detail: str = Form("Comprehensive"),
    communication_objective: str = Form("Inform and Align"),
    content_style: str = Form("Executive Brief"),
    file: Optional[UploadFile] = File(None)
):
    """
    Ingests source document, prompt text, or raw image bytes.
    Resets global retrieval state and forces immediate garbage collection on every request.
    Generates a unique session_id per request to guarantee strict context isolation.
    """
    # 1. Reset Global States & Execute Immediate Garbage Collection
    reset_global_retrieval_state()

    session_id = str(uuid.uuid4())
    raw_text = ""
    page_count = 1
    image_bytes = None
    mime_type = None
    
    # 2. Check if uploaded file is an image or document
    if file and file.filename and file.filename.strip():
        file_bytes = await file.read()
        if file_bytes and len(file_bytes) > 0:
            filename_lower = file.filename.lower()
            if filename_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
                # True Multimodal Image Vision Bypass
                image_bytes = file_bytes
                mime_type = file.content_type or f"image/{filename_lower.split('.')[-1]}"
                if mime_type == "image/jpg":
                    mime_type = "image/jpeg"
                raw_text = f"[Image Upload: {file.filename}]"
                page_count = 1
            else:
                parsed_res = parse_source_document(file.filename, file_bytes)
                if isinstance(parsed_res, dict):
                    raw_text = parsed_res.get("text", "")
                    page_count = parsed_res.get("page_count", 1)
                else:
                    raw_text = str(parsed_res)
                    page_count = max(1, len(raw_text) // 3000)

    if not raw_text.strip() and text_content and text_content.strip():
        raw_text = text_content.strip()
        page_count = max(1, len(raw_text) // 3000)

    if not raw_text.strip() and not image_bytes:
        raise HTTPException(status_code=400, detail="Either file upload or text_content must be provided.")

    # 3. Parse Spokes List
    try:
        if isinstance(selected_spokes, str):
            if selected_spokes.startswith("["):
                import json
                spokes_list = json.loads(selected_spokes)
            else:
                spokes_list = [s.strip() for s in selected_spokes.split(",") if s.strip()]
        else:
            spokes_list = list(selected_spokes)
    except Exception:
        spokes_list = ["summary", "linkedin", "twitter"]

    config_dict = {
        "target_audience": target_audience,
        "tone": tone,
        "language": language,
        "level_of_detail": level_of_detail,
        "communication_objective": communication_objective,
        "content_style": content_style
    }

    # 4. Schedule background dispatch task with session_id & multimodal image params
    background_tasks.add_task(
        dispatch_hub_and_spoke,
        client_id=client_id,
        source_text=raw_text,
        selected_spokes=spokes_list,
        config_dict=config_dict,
        page_count=page_count,
        session_id=session_id,
        image_bytes=image_bytes,
        mime_type=mime_type
    )

    return {
        "status": "queued",
        "job_id": session_id,
        "session_id": session_id,
        "client_id": client_id,
        "page_count": page_count,
        "is_image_multimodal": bool(image_bytes),
        "spokes_queued": len(spokes_list),
        "message": f"Transformation session {session_id[:8]} queued. Global state reset and memory collected."
    }

@app.get("/api/spokes")
async def list_spokes():
    return {
        "spokes": [
            {"id": "video", "name": "Video Package (Remotion)", "icon": "video", "description": "Complete script, storyboard, narration & Remotion JSON layout payload."},
            {"id": "linkedin", "name": "LinkedIn Post", "icon": "linkedin", "description": "Professional post with hook, takeaways, CTA, and trending hashtags."},
            {"id": "twitter", "name": "Twitter/X Thread", "icon": "twitter", "description": "Platform-optimized tweet series under 280 characters."},
            {"id": "advisory", "name": "Structured Advisory", "icon": "shield-alert", "description": "Formal advisory document with risk severity and action plan."},
            {"id": "infographic", "name": "Infographic Blueprint", "icon": "bar-chart-2", "description": "Key stats, visual layout recommendations, and graphic structure."},
            {"id": "summary", "name": "Executive Summary", "icon": "file-text", "description": "Concise briefing for decision-makers and C-suite leadership."},
            {"id": "presentation", "name": "Presentation Deck", "icon": "presentation", "description": "Multi-slide presentation outline with speaker notes and visual prompts."}
        ]
    }

# ==========================================
# 🔊 Native Text-to-Speech & Translation API
# ==========================================

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"

class TTSRequest(BaseModel):
    text: str
    target_lang: str = "hi"

@app.post("/translate")
@app.post("/api/translate")
async def translate_endpoint(
    request_data: Optional[TranslateRequest] = None,
    text: Optional[str] = Form(None),
    target_lang: Optional[str] = Form(None)
):
    """
    Text Translation Endpoint.
    Supports target languages: Hindi ('hi'), Bengali ('bn'), Nepali ('ne').
    Returns JSON payload containing the translated text string.
    """
    input_text = ""
    lang = "hi"

    if request_data:
        input_text = request_data.text
        lang = request_data.target_lang
    else:
        input_text = text or ""
        lang = target_lang or "hi"

    if not input_text or not input_text.strip():
        raise HTTPException(status_code=400, detail="Text payload is required for translation.")

    lang_map = {
        "hindi": "hi", "hi": "hi",
        "bengali": "bn", "bn": "bn",
        "nepali": "ne", "ne": "ne",
        "english": "en", "en": "en"
    }
    target_code = lang_map.get(lang.lower().strip(), "hi")

    translated_text = input_text
    if target_code != "en":
        try:
            from googletrans import Translator
            translator_obj = Translator()
            res = translator_obj.translate(input_text, dest=target_code)
            if res and res.text:
                translated_text = res.text
        except Exception as e:
            logger.warning(f"googletrans error: {e}. Falling back to Bhashini / Gemini fallback.")
            try:
                from translation_service import translator as bhashini_translator
                translated_text = bhashini_translator.translate(input_text, target_code)
            except Exception as e2:
                logger.error(f"Fallback translation error: {e2}")

    return {
        "original_text": input_text,
        "translated_text": translated_text,
        "target_lang": target_code
    }

@app.post("/text-to-speech")
@app.post("/api/text-to-speech")
async def text_to_speech_endpoint(
    request_data: Optional[TTSRequest] = None,
    text: Optional[str] = Form(None),
    target_lang: Optional[str] = Form(None)
):
    """
    Native Text-to-Speech & Translation Endpoint.
    Supports target languages: Hindi ('hi'), Bengali ('bn'), Nepali ('ne').
    Translates text first, converts to gTTS MP3 audio stream, and returns audio/mpeg bytes directly without saving files to disk.
    """
    input_text = ""
    lang = "hi"

    if request_data:
        input_text = request_data.text
        lang = request_data.target_lang
    else:
        input_text = text or ""
        lang = target_lang or "hi"

    if not input_text or not input_text.strip():
        raise HTTPException(status_code=400, detail="Text payload is required for TTS generation.")

    # Standardize target language code (hi, bn, ne)
    lang_map = {
        "hindi": "hi", "hi": "hi",
        "bengali": "bn", "bn": "bn",
        "nepali": "ne", "ne": "ne",
        "english": "en", "en": "en"
    }
    target_code = lang_map.get(lang.lower().strip(), "hi")

    # 1. Translation using googletrans
    translated_text = input_text
    if target_code != "en":
        try:
            from googletrans import Translator
            translator = Translator()
            res = translator.translate(input_text, dest=target_code)
            if res and res.text:
                translated_text = res.text
        except Exception as e:
            logger.warning(f"googletrans error: {e}. Falling back to raw input text.")

    # 2. Clean text for TTS (strip markdown syntax)
    import re
    clean_text = re.sub(r'[\*\#\_\`\[\]\(\)\>\<\~]', ' ', translated_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    if not clean_text:
        clean_text = translated_text

    if len(clean_text) > 1000:
        clean_text = clean_text[:1000]

    # 3. Convert to gTTS MP3 Audio Stream in memory
    import io
    from fastapi.responses import Response

    mp3_bytes = None
    try:
        from gtts import gTTS
        tts = gTTS(text=clean_text, lang=target_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        mp3_bytes = fp.getvalue()
    except Exception as tts_err:
        logger.error(f"gTTS generation error: {tts_err}. Returning fallback MP3 stream.")
        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text[:200], lang="en", slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            mp3_bytes = fp.getvalue()
        except Exception:
            # Fallback 1-second synthetic audio stream
            mp3_bytes = b'\xff\xf3\x40\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' * 50

    return Response(
        content=mp3_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=tts_{target_code}.mp3",
            "X-Target-Language": target_code
        }
    )

