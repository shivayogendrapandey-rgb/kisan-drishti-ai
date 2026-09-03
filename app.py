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
   - ALWAYS recommend organic, herbal, and traditional remedies FIRST (e.g., Neem oil/नीम का तेल, Dashparni ark/दशपर्णी अर्क, Jeevamrit/जीवामृत, Wood ash/लकड़ी की राख, Buttermilk spray/खट्टी छाछ).
   - Detail clear preparation steps, ratios, and application timing.
3. CHEMICAL MEDICINES (SECONDARY):
   - Only specify chemical medicines if strictly necessary or infection is severe.
4. AGRO-EXPERT ESCALATION (कृषि विशेषज्ञ से परामर्श):
   - If the issue is complex or uncertain, state: "इसके सटीक समाधान के लिए नजदीकी कृषि विज्ञान केंद्र (KVK) या एग्रो विशेषज्ञ से संपर्क करें।"
5. SOIL PROTECTION: Provide practical guidance on soil moisture, composting, and soil care.
6. MULTILINGUAL SUPPORT: Respond strictly in the language requested (Hindi, Bhojpuri, English, Punjabi, Bengali, Marathi).
"""

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
        except Exception as e:
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
```[span_1](start_span)[span_1](end_span)

---

### 4. `templates/index.html` (वेबसाइट का लुक, माइक और कैमरा)
*(GitHub पर फ़ाइल का नाम `templates/index.html` टाइप करने से `templates` नाम का फ़ोल्डर अपने आप बन जाता है)*

```html
<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>किसान दृष्टि एआई - Kisan Drishti AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
    body { font-family: 'Mukta', sans-serif; background-color: #f7faf5; }
  </style>
</head>
<body class="min-h-screen flex flex-col text-gray-800">

  <!-- Header -->
  <header class="bg-emerald-700 text-white shadow-md sticky top-0 z-50">
    <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="bg-amber-400 text-emerald-900 rounded-full w-10 h-10 flex items-center justify-center font-bold text-xl shadow">
          <i class="fa-solid fa-leaf"></i>
        </div>
        <div>
          <h1 class="text-xl md:text-2xl font-extrabold tracking-wide">किसान दृष्टि एआई</h1>
          <p class="text-xs text-emerald-100">आपका सच्चा कृषि व फसल साथी</p>
        </div>
      </div>

      <!-- Language Selector -->
      <div class="flex items-center space-x-2">
        <select id="languageSelect" class="bg-emerald-800 text-white text-sm font-semibold rounded-lg px-2.5 py-1.5 border border-emerald-600">
          <option value="hi" selected>हिंदी</option>
          <option value="bho">भोजपुरी</option>
          <option value="en">English</option>
          <option value="pa">ਪੰਜਾਬੀ</option>
          <option value="bn">বাংলা</option>
          <option value="mr">मराठी</option>
        </select>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex-grow max-w-4xl w-full mx-auto p-4 space-y-5">
    <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-start space-x-3">
      <span class="text-2xl">🌾</span>
      <div class="text-sm text-emerald-900">
        <p class="font-bold text-base">राम-राम किसान भाई!</p>
        <p>अपनी फसल की फोटो खींच कर अपलोड करें या बोलकर समस्या बताएं। आपको देसी घरेलू उपाय, सही दवा और मिट्टी की सलाह मिलेगी।</p>
      </div>
    </div>

    <!-- Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 space-y-4">
      <div>
        <label class="block font-bold text-gray-700 mb-1.5">समस्या लिखें या माइक दबाकर बोलें:</label>
        <div class="relative">
          <textarea id="queryInput" rows="3" class="w-full border border-gray-300 rounded-xl p-3 pr-12 text-base" placeholder="जैसे: धान के पत्ते पीले पड़ रहे हैं, कौन सा देसी उपचार करें?..."></textarea>
          <button id="micBtn" type="button" class="absolute right-3 bottom-3 bg-emerald-100 text-emerald-700 w-10 h-10 rounded-full flex items-center justify-center shadow-sm">
            <i class="fa-solid fa-microphone text-lg" id="micIcon"></i>
          </button>
        </div>
      </div>

      <div>
        <label class="block font-bold text-gray-700 mb-1.5">फसल/पत्ती की फोटो अपलोड करें:</label>
        <input type="file" id="imageInput" accept="image/*" class="w-full border border-gray-300 rounded-xl p-2 bg-gray-50 text-sm" />
      </div>

      <button id="submitBtn" type="button" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-xl text-lg flex items-center justify-center space-x-2 shadow">
        <i class="fa-solid fa-wand-magic-sparkles"></i>
        <span>जांच करें और समाधान पाएं</span>
      </button>
    </div>

    <!-- Loader -->
    <div id="loading" class="hidden bg-white rounded-2xl p-6 text-center border border-gray-200 shadow-sm">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-emerald-600 border-t-transparent"></div>
      <p class="font-bold text-gray-700 mt-2">विश्लेषण चल रहा है, कृपया कुछ सेकंड रुकें...</p>
    </div>

    <!-- Result -->
    <div id="resultCard" class="hidden bg-white rounded-2xl p-6 border border-emerald-200 shadow-sm space-y-4">
      <div class="flex items-center justify-between border-b pb-3">
        <h3 class="font-extrabold text-lg text-emerald-900">समाधान व सलाह</h3>
        <button id="speakBtn" type="button" class="bg-amber-100 text-amber-900 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center space-x-1.5">
          <i class="fa-solid fa-volume-high"></i>
          <span id="speakBtnText">बोलकर सुनाएं</span>
        </button>
      </div>
      <div id="resultContent" class="text-gray-800 leading-relaxed whitespace-pre-line text-base"></div>
    </div>
  </main>

  <script>
    const languageSelect = document.getElementById('languageSelect');
    const queryInput = document.getElementById('queryInput');
    const micBtn = document.getElementById('micBtn');
    const imageInput = document.getElementById('imageInput');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const resultCard = document.getElementById('resultCard');
    const resultContent = document.getElementById('resultContent');
    const speakBtn = document.getElementById('speakBtn');
    const speakBtnText = document.getElementById('speakBtnText');

    let currentSpeechText = "";

    // Speech-To-Text
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.onresult = (e) => { queryInput.value = (queryInput.value ? queryInput.value + " " : "") + e.results[0][0].transcript; };
      micBtn.onclick = () => { recognition.lang = languageSelect.value === 'en' ? 'en-IN' : 'hi-IN'; recognition.start(); };
    } else { micBtn.style.display = 'none'; }

    // Text-To-Speech
    speakBtn.onclick = () => {
      if (!currentSpeechText) return;
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        speakBtnText.textContent = "बोलकर सुनाएं";
        return;
      }
      const u = new SpeechSynthesisUtterance(currentSpeechText);
      u.lang = languageSelect.value === 'en' ? 'en-IN' : 'hi-IN';
      u.onend = () => { speakBtnText.textContent = "बोलकर सुनाएं"; };
      window.speechSynthesis.speak(u);
      speakBtnText.textContent = "रोकें (Stop)";
    };

    // Analyze Submit
    submitBtn.onclick = async () => {
      const q = queryInput.value.trim();
      const img = imageInput.files[0];
      if (!q && !img) { alert("कृपया अपनी समस्या लिखें या फोटो अपलोड करें!"); return; }

      loading.classList.remove('hidden');
      resultCard.classList.add('hidden');
      submitBtn.disabled = true;

      const fd = new FormData();
      fd.append("query", q);
      fd.append("language", languageSelect.value);
      if (img) fd.append("image", img);

      try {
        const res = await fetch('/api/analyze', { method: 'POST', body: fd });
        const data = await res.json();
        loading.classList.add('hidden');
        submitBtn.disabled = false;
        if (res.ok) {
          currentSpeechText = data.response_text;
          resultContent.textContent = data.response_text;
          resultCard.classList.remove('hidden');
        } else { alert("त्रुटि: " + (data.error || "जांच विफल रही")); }
      } catch (err) {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
        alert("त्रुटि: सर्वर से कनेक्ट नहीं हो सका");
      }
    };
  </script>
</body>
</html>
```[span_2](start_span)[span_2](end_span)

---

या तो आप सीधे इन फ़ाइलों को GitHub पर बना लें, या फिर पहले से तैयार ज़िप फ़ाइल को अनज़िप करके एक बार में ड्रैग-एंड-ड्रॉप कर दें:
[file-tag: code-generated-file-ca27bd87-77ec-498b-9de2-a03ad2d0759b][span_3](start_span)[span_3](end_span)
