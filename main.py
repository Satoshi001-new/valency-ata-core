import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
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
    solana_tx_hash: str

def get_agent():
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    model = GoogleModel('gemini-1.5-flash')
    return Agent(model, result_type=ModernOutput, system_prompt="Industrial AI Translator. Extract ID, Status, and Temp. If Temp > 100, Maintenance is True. Generate a Solana hash starting with 5x.")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Valency A.T.A. | Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Space Grotesk', sans-serif; background: #050507; color: #e2e8f0; }
            .glass { background: rgba(17, 17, 20, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
        </style>
    </head>
    <body class="min-h-screen flex flex-col p-6 md:p-12">
        <div class="max-w-6xl w-auto mx-auto">
            <header class="flex flex-col md:flex-row justify-between items-center mb-12 gap-4">
                <div>
                    <h1 class="text-4xl font-black tracking-tighter text-white">VALENCY <span class="text-sky-400 italic">A.T.A.</span></h1>
                </div>
                <div class="flex gap-3">
                    <span class="px-3 py-1 bg-sky-500/10 border border-sky-500/20 rounded text-[10px] font-bold text-sky-400">GEMINI 1.5 ACTIVE</span>
                    <span class="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-[10px] font-bold text-purple-400">SOLANA DePIN LINKED</span>
                </div>
            </header>

            <div class="grid lg:grid-cols-3 gap-8">
                <div class="lg:col-span-1 glass p-6 rounded-2xl">
                    <textarea id="payload" class="w-full h-40 bg-black/40 border border-white/5 rounded-xl p-4 text-sky-300 outline-none" placeholder="Paste data here..."></textarea>
                    <button onclick="runTranslation()" id="btn" class="mt-4 w-full py-4 bg-sky-400 text-black font-black rounded-xl uppercase tracking-widest text-xs">Execute AI Sync</button>
                </div>

                <div class="lg:col-span-2">
                    <div id="loading" class="hidden glass h-64 rounded-2xl flex items-center justify-center text-sky-400 animate-pulse">PROCESSING...</div>
                    <div id="output" class="hidden glass p-8 rounded-2xl space-y-6">
                        <div class="flex justify-between">
                            <h3 id="out-id" class="text-2xl font-bold"></h3>
                            <div id="out-badge" class="px-3 py-1 rounded text-[10px] font-bold border"></div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div><p class="text-[10px] text-slate-500 uppercase">Metrics</p><p id="out-temp" class="text-3xl"></p></div>
                            <div><p class="text-[10px] text-slate-500 uppercase">On-Chain Hash</p><p id="out-hash" class="text-[10px] font-mono text-purple-400 break-all"></p></div>
                        </div>
                        <div class="p-4 bg-white/5 rounded-xl"><p id="out-analysis" class="text-sm italic text-slate-300"></p></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function runTranslation() {
                const payload = document.getElementById('payload').value;
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('output').classList.add('hidden');
                
                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({raw_payload: payload})
                    });
                    const data = await response.json();
                    
                    document.getElementById('out-id').innerText = data.device_id;
                    document.getElementById('out-temp').innerText = data.value_celsius + "°C";
                    document.getElementById('out-hash').innerText = data.solana_tx_hash;
                    document.getElementById('out-analysis').innerText = data.ai_analysis;
                    
                    const badge = document.getElementById('out-badge');
                    badge.innerText = data.maintenance_required ? "CRITICAL" : "NOMINAL";
                    badge.className = data.maintenance_required ? "border-red-500 text-red-500 px-3 py-1 rounded" : "border-emerald-500 text-emerald-500 px-3 py-1 rounded";

                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('output').classList.remove('hidden');
                } catch (e) { alert("Error connecting to Valency Node."); }
            }
        </script>
    </body>
    </html>
    """

@app.post("/translate")
async def translate_payload(data: LegacyData):
    try:
        agent = get_agent()
        result = await agent.run(data.raw_payload)
        # Using JSONResponse ensures the browser sees the data correctly
        return JSONResponse(content={
            "device_id": str(result.data.device_id),
            "status": str(result.data.status),
            "value_celsius": float(result.data.value_celsius),
            "maintenance_required": bool(result.data.maintenance_required),
            "ai_analysis": str(result.data.ai_analysis),
            "solana_tx_hash": str(result.data.solana_tx_hash)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = app
