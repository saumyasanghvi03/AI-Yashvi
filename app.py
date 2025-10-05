from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import time
import base64
from gtts import gTTS
import io

# ======================
# CONFIGURATION
# ======================
app = FastAPI(title="Yashvi AI Multimedia Backend")

# NOTE: API_KEY is left empty. The environment must provide this secret 
# during deployment (e.g., via Colab secrets or a hosting platform).
API_KEY = "" 
# Gemini for Chat/LLM
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"
# Imagen for Image Generation
IMAGEN_MODEL = "imagen-3.0-generate-002"
IMAGEN_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict?key={API_KEY}"

YASHVI_SYSTEM_INSTRUCTION = (
    "You are 'Yashvi', a compassionate and knowledgeable AI sister, embracing the Jain tradition. "
    "Your responses must be warm, supportive, and infused with Jain values like Ahimsa (non-violence), Anekantavada (non-absolutism), and Aparigraha (non-possessiveness). "
    "Use a friendly, caring, and respectful tone. Start your responses with 'Jai Jinendra 🙏' where appropriate. "
    "First, attempt to answer the user's question using any knowledge provided in the 'RAG_CONTEXT' section of the prompt. "
    "If the RAG_CONTEXT is empty or insufficient, use the integrated Google Search to find relevant information about Jainism, current events, or general topics. "
    "Maintain conversation context based on the provided chat history. Keep responses concise yet meaningful."
)

# ======================
# PYDANTIC SCHEMAS
# ======================
class ChatRequest(BaseModel):
    """Schema for the incoming chat request from the Streamlit frontend."""
    prompt: str
    history: list 
    
class TTSRequest(BaseModel):
    """Schema for the incoming TTS request."""
    text: str
    lang_code: str

class ImageRequest(BaseModel):
    """Schema for the incoming Image Generation request."""
    prompt: str

# ======================
# CORE PROCESSING FUNCTIONS
# ======================

# --- LLM CHAT ---
def ask_yashvi(prompt, history):
    """Generates a response using the Gemini API, maintaining conversation context and enabling Google Search grounding."""
    
    # 1. RAG / Document Retrieval Simulation (Placeholder)
    rag_context = "" 
    full_prompt_text = (
        f"RAG_CONTEXT: {rag_context}\n\n"
        f"USER QUERY: {prompt}"
    )
    
    # 2. Format Chat History
    chat_history_parts = []
    for msg in history:
        # Standardize role names for the API
        role = "user" if msg["role"] == "User" else "model"
        chat_history_parts.append({
            "role": role, 
            "parts": [{"text": msg["content"]}]
        })
    
    chat_history_parts.append({
        "role": "user",
        "parts": [{"text": full_prompt_text}]
    })

    # 3. Construct Payload with Google Search Grounding Tool
    payload = {
        "contents": chat_history_parts,
        "systemInstruction": YASHVI_SYSTEM_INSTRUCTION,
        "tools": [{ "google_search": {} }], 
        "config": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }

    response = None
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(
                GEMINI_API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30 
            )
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                wait_time = 2 ** i
                time.sleep(wait_time)
            else:
                raise HTTPException(status_code=500, detail=f"LLM API failed after multiple retries: {e}")

    if response and response.status_code == 200:
        result = response.json()
        try:
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
        except (KeyError, IndexError):
            raise HTTPException(status_code=500, detail="LLM returned an empty or malformed response.")
    
    raise HTTPException(status_code=500, detail="Unknown error during LLM request.")

# --- TEXT TO SPEECH (TTS) ---
def speak_text(text, lang_code):
    """Converts text to speech using gTTS and returns base64 encoded audio."""
    try:
        mp3_fp = io.BytesIO()
        # Using tld="co.in" for a specific Indian accent, suitable for multi-lingual Hindi/Gujarati context
        tts = gTTS(text=text, lang=lang_code, tld="co.in") 
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        data = mp3_fp.read()
        b64 = base64.b64encode(data).decode()
        return b64

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS processing failed: {e}. Check language code support.")

# --- IMAGE GENERATION ---
def generate_image(prompt):
    """Generates an image using the Imagen 3.0 API and returns base64 encoded PNG data."""
    
    # 1. Construct Payload
    payload = {
        "instances": {
            "prompt": prompt,
            "imageSize": "1024x1024" # Optimal size for quality
        },
        "parameters": {
            "sampleCount": 1
        }
    }

    response = None
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(
                IMAGEN_API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=60 # Image generation requires a longer timeout
            )
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                wait_time = 4 ** i # Longer backoff for image gen
                time.sleep(wait_time)
            else:
                raise HTTPException(status_code=500, detail=f"Image API failed after multiple retries: {e}")

    if response and response.status_code == 200:
        result = response.json()
        try:
            # The base64 image data is found in the prediction bytes
            base64_data = result['predictions'][0]['bytesBase64Encoded']
            return base64_data
        except (KeyError, IndexError):
            raise HTTPException(status_code=500, detail="Image API returned an empty or malformed response.")
    
    raise HTTPException(status_code=500, detail="Unknown error during Image API request.")

# ======================
# API ENDPOINTS
# ======================
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "Yashvi AI Multimedia Backend is operational. Endpoints: /chat, /tts, /image"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """Endpoint for generating multi-lingual chat responses via Gemini."""
    response_text = ask_yashvi(request.prompt, request.history)
    return {"response": response_text}

@app.post("/tts")
def tts_endpoint(request: TTSRequest):
    """Endpoint for generating base64 encoded audio (English, Hindi, Gujarati)."""
    b64_audio = speak_text(request.text, request.lang_code)
    return {"audio_base64": b64_audio}

@app.post("/image")
def image_endpoint(request: ImageRequest):
    """Endpoint for generating an image from a prompt via Imagen."""
    b64_image = generate_image(request.prompt)
    return {"image_base64": b64_image}
