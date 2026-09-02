import os
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BhashiniTranslator:
    """
    Bhashini API Translation Engine for localization of text outputs & video subtitles.
    Supports English to Indian languages (Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, etc.)
    and generic language translation fallbacks.
    """
    def __init__(self):
        self.api_key = os.environ.get("BHASHINI_API_KEY")
        self.user_id = os.environ.get("BHASHINI_USER_ID")
        self.pipeline_id = os.environ.get("BHASHINI_PIPELINE_ID")

    def translate(self, text: str, target_lang: str) -> str:
        if not text or target_lang.lower() in ["english", "en"]:
            return text

        if self.api_key and self.user_id:
            try:
                # Bhashini NMT API call endpoint
                url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "translation",
                            "config": {
                                "language": {
                                    "sourceLanguage": "en",
                                    "targetLanguage": target_lang.lower()[:2]
                                }
                            }
                        }
                    ],
                    "inputData": {
                        "input": [{"source": text}]
                    }
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=5)
                if resp.status_code == 200:
                    res_json = resp.json()
                    translated = res_json['pipelineResponse'][0]['output'][0]['target']
                    return translated
            except Exception as e:
                logger.error(f"Bhashini translation API error: {e}")

        # Localized mock translation fallback annotation for verification
        return f"[{target_lang.upper()} TRANSLATION]: {text}"

translator = BhashiniTranslator()
