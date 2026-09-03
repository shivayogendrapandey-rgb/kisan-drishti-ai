import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from google import genai
from google.genai import types

app = FastAPI(title="Kisan Drishti AI - किसान दृष्टि एआई")
templates = Jinja2Templates(directory="templates")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are "Kisan Drishti AI" (किसान दृष्टि एआई) - an expert, compassionate, and farmer-friendly agricultural AI assistant dedicated to Indian smallholder farmers.

CORE OPERATIONAL PRINCIPLES:
1. FARMER-FIRST & SIMPLE TONE: Speak directly, clearly, warmly, and respectfully to farmers without academic jargon.
2. ORGANIC / DESI (घरेलू व आयुर्वेदिक) FIRST:
   - ALWAYS recommend organic, herbal, and traditional remedies FIRST (e.g., Neem oil, Dashparni ark, Jeevamrit, Wood ash, Buttermilk spray).
   - Detail clear preparation steps, ratios, and application timing.
3. CHEMICAL MEDICINES (SECONDARY):
   - Only specify chemical medicines if strictly necessary or infection is severe.
4. AGRO-EXPERT ESCALATION:
   - If the issue is complex or uncertain, state: "इसके सटीक समाधान के लिए नजदीकी कृषि विज्ञान केंद्र (KVK) या एग्रो विशेषज्ञ से संपर्क करें।"
5. SOIL PROTECTION: Provide practical guidance on soil moisture, composting, and soil care.
6. MULTILINGUAL SUPPORT: Respond strictly in the language requested (Hindi, Bhojpuri, English, Punjabi, Bengali, Marathi).
"""

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Kisan Drishti AI"}

@app.post("/api/analyze")
async def analyze_crop(
    query: Optional[str] = Form(None),
    language: str = Form("hi"),
    image: Optional[UploadFile] = File(None)
):
    global client
    if not client:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(status_code=500, content={"error": "GEMINI_API_KEY सर्वर पर कॉन्फ़िगर नहीं है।"})
        client = genai.Client(api_key=api_key)

    lang_map = {
        "hi": "Hindi (हिंदी)",
        "bho": "Bhojpuri (भोजपुरी)",
        "en": "English",
        "pa": "Punjabi (ਪੰਜਾਬੀ)",
        "bn": "Bengali (বাংলা)",
        "mr": "Marathi (मराठी)"
    }
    target_language = lang_map.get(language, "Hindi (हिंदी)")
    contents = []

    if image and image.filename:
        try:
            image_bytes = await image.read()
            pil_image = Image.open(io.BytesIO(image_bytes))
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            contents.append(pil_image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

    user_text = query.strip() if query else ""
    if not user_text and not contents:
        raise HTTPException(status_code=400, detail="Please provide text or an image.")

    prompt_instruction = f"""
Farmer's Query: {user_text if user_text else 'कृपया इस फसल की फोटो देखकर बीमारी, देसी उपचार और मिट्टी की सलाह दें।'}
Target Response Language: {target_language}
"""
    contents.append(prompt_instruction)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3
            )
        )
        return JSONResponse(content={"status": "success", "response_text": response.text})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"जांच विफल रही: {str(e)}"})
