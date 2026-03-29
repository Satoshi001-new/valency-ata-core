import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

class LegacyData(BaseModel):
    raw_payload: str

class ModernOutput(BaseModel):
    device_id: str
    status: str
    value_celsius: float
    maintenance_required: bool
    ai_analysis: str

def get_agent():
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    model = GoogleModel('gemini-1.5-flash')
    return Agent(model, result_type=ModernOutput, system_prompt="Industrial Translator. Extract ID, Status, and Temp. If Temp > 100, Maintenance is True.")

# --- THE NEW UI SECTION ---
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Valency A.T.A. | Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Space Grotesk', sans-serif; background: #0a0a0c; color: #e2e8f0; }
            .terminal { font-family: 'Fira Code', monospace; background: #111113; border: 1px solid #2d2d30; }
            .glow { box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-6">
        <div class="max-w-4xl w-full">
            <header class="mb-8 text-center">
                <h1 class="text-4xl font-bold tracking-tighter text-sky-400 mb-2">VALENCY A.T.A.</h1>
                <p class="text-slate-400 uppercase tracking-widest text-xs font-semibold">Universal API Translation Layer • v1.0.2</p>
            </header>

            <div class="grid md:grid-cols-2 gap-8">
                <div class="terminal p-6 rounded-xl glow">
                    <h2 class="text-sm font-bold mb-4 text-slate-500 uppercase">Legacy Telemetry Input</h2>
                    <textarea id="payload" class="w-full h-32 bg-transparent border-none focus:ring-0 text-sky-300 resize-none" placeholder="Enter raw data (e.g. UNIT:4 | TEMP:105)..."></textarea>
                    <button onclick="translate()" id="btn" class="mt-4 w-full py-3 bg-sky-500 hover:bg-sky-400 text-black font-bold rounded-lg transition-all">TRANSLATE PROTOCOL</button>
                </div>

                <div id="output-box" class="terminal p-6 rounded-xl border-sky-900/50 hidden">
                    <h2 class="text-sm font-bold mb-4 text-slate-500 uppercase">AI Structured Intelligence</h2>
                    <div id="result" class="space-y-3 text-sm"></div>
                </div>
            </div>
        </div>

        <script>
            async def translate() {
                const payload = document.getElementById('payload').value;
                const btn = document.getElementById('btn');
                const box = document.getElementById('output-box');
                const resDiv = document.getElementById('result');

                btn.innerText = "PROCESSING...";
                btn.disabled = true;

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({raw_payload: payload})
                    });
                    const data = await response.json();
                    
                    box.classList.remove('hidden');
                    resDiv.innerHTML = `
                        <div class="flex justify-between border-b border-white/5 pb-2"><span>Device ID:</span><span class="text-sky-400 font-bold">${data.device_id}</span></div>
                        <div class="flex justify-between border-b border-white/5 pb-2"><span>Status:</span><span class="${data.status === 'CRITICAL' ? 'text-red-400' : 'text-green-400'}">${data.status}</span></div>
                        <div class="flex justify-between border-b border-white/5 pb-2"><span>Value:</span><span>${data.value_celsius}°C</span></div>
                        <div class="p-3 bg-white/5 rounded mt-4 italic text-slate-300">"${data.ai_analysis}"</div>
                    `;
                } catch (e) {
                    alert("System Error. Check Console.");
                } finally {
                    btn.innerText = "TRANSLATE PROTOCOL";
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/translate", response_model=ModernOutput)
async def translate_payload(data: LegacyData):
    try:
        agent = get_agent()
        result = await agent.run(data.raw_payload)
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = app
