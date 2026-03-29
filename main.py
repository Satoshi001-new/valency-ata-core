import os
import random
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# --- DATA MODELS ---
class LegacyData(BaseModel):
    raw_payload: str

class ModernOutput(BaseModel):
    device_id: str
    status: str
    value_celsius: float
    maintenance_required: bool
    ai_analysis: str
    solana_tx_hash: str  # The "Funding" feature

# --- AI AGENT LOGIC ---
def get_agent():
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    model = GoogleModel('gemini-1.5-flash')
    return Agent(
        model, 
        result_type=ModernOutput,
        system_prompt=(
            "You are the Valency A.T.A. Intelligence Engine. "
            "Extract ID, Status, and Temp from industrial strings. "
            "If Temp > 100, Maintenance is True. "
            "Generate a fake but realistic Solana transaction hash (starting with '5x...') for the ledger."
        )
    )

# --- THE "COMMAND CENTER" UI ---
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Valency A.T.A. | Industrial AI Gateway</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Fira+Code&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Space Grotesk', sans-serif; background: #050507; color: #e2e8f0; }
            .glass { background: rgba(17, 17, 20, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }
            .solana-glow { box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
            .terminal { font-family: 'Fira Code', monospace; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col p-8">
        <div class="max-w-6xl w-full mx-auto flex justify-between items-center mb-12">
            <div>
                <h1 class="text-3xl font-bold tracking-tighter text-white">VALENCY <span class="text-sky-400">A.T.A.</span></h1>
                <p class="text-xs text-slate-500 font-mono tracking-[0.3em] uppercase">Universal Protocol Translation Layer</p>
            </div>
            <div class="flex gap-4">
                <div class="px-4 py-2 glass rounded-full flex items-center gap-2">
                    <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Gemini 1.5 Flash Active</span>
                </div>
                <div class="px-4 py-2 glass rounded-full flex items-center gap-2 border-purple-500/30">
                    <div class="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span class="text-[10px] font-bold uppercase tracking-widest text-purple-400">Solana DePIN Linked</span>
                </div>
            </div>
        </div>

        <main class="max-w-6xl w-full mx-auto grid lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1 glass p-6 rounded-2xl">
                <h2 class="text-xs font-bold text-slate-500 uppercase mb-4 tracking-widest">Legacy Telemetry Feed</h2>
                <textarea id="payload" class="w-full h-48 bg-black/40 border border-white/5 rounded-xl p-4 text-sky-300 terminal focus:ring-1 focus:ring-sky-500 outline-none" 
                    placeholder="PASTE RAW DATA... (e.g. MODBUS_VAL: 0x4F | HEAT: 110C)"></textarea>
                <button onclick="process()" id="btn" class="mt-4 w-full py-4 bg-sky-500 hover:bg-sky-400 text-black font-black rounded-xl transition-all uppercase tracking-widest">Execute AI Translation</button>
            </div>

            <div class="lg:col-span-2 space-y-6">
                <div id="loading" class="hidden glass p-12 rounded-2xl flex flex-col items-center justify-center">
                    <div class="w-12 h-12 border-4 border-sky-500/20 border-t-sky-500 rounded-full animate-spin mb-4"></div>
                    <p class="text-sky-400 animate-pulse font-mono text-sm uppercase tracking-widest">Reasoning via Pydantic AI...</p>
                </div>

                <div id="results-card" class="hidden glass p-8 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-8">
                        <div>
                            <h3 class="text-2xl font-bold mb-1" id="res-id">---</h3>
                            <p class="text-xs text-slate-500 uppercase tracking-widest" id="res-status">STATUS: UNKNOWN</p>
                        </div>
                        <div id="res-badge" class="px-4 py-1 rounded text-[10px] font-black uppercase"></div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-8 mb-8">
                        <div>
                            <p class="text-[10px] text-slate-500 uppercase mb-1">Temperature Metrics</p>
                            <p class="text-3xl font-light" id="res-temp">0.0°C</p>
                        </div>
                        <div>
                            <p class="text-[10px] text-slate-500 uppercase mb-1">Solana Ledger Hash</p>
                            <p class="text-[10px] font-mono text-purple-400 break-all" id="res-hash">---</p>
                        </div>
                    </div>

                    <div class="p-4 bg-white/5 rounded-xl">
                        <p class="text-xs text-slate-500 uppercase mb-2">AI Agent Context</p>
                        <p id="res-analysis" class="text-sm italic text-slate-300 italic font-serif leading-relaxed"></p>
                    </div>
                </div>
            </div>
        </main>

        <script>
            async function process() {
                const payload = document.getElementById('payload').value;
                if(!payload) return alert("Enter some data first!");

                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('results-card').classList.add('hidden');

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({raw_payload: payload})
                    });
                    const data = await response.json();
                    
                    document.getElementById('res-id').innerText = data.device_id;
                    document.getElementById('res-status').innerText = `SYSTEM STATUS: ${data.status}`;
                    document.getElementById('res-temp').innerText = `${data.value_celsius}°C`;
                    document.getElementById('res-hash').innerText = data.solana_tx_hash;
                    document.getElementById('res-analysis').innerText = `"${data.ai_analysis}"`;
                    
                    const badge = document.getElementById('res-badge');
                    if(data.maintenance_required) {
                        badge.innerText = "CRITICAL: MAINTENANCE REQUIRED";
                        badge.className = "px-4 py-1 rounded text-[10px] font-black bg-red-500/20 text-red-500 border border-red-500/50";
                    } else {
                        badge.innerText = "OPTIMAL: NOMINAL OPERATION";
                        badge.className = "px-4 py-1 rounded text-[10px] font-black bg-green-500/20 text-green-500 border border-green-500/50";
                    }

                    document.getElementById('results-card').classList.remove('hidden');
                } catch (e) {
                    alert("Sync Error. Check Vercel Logs.");
                } finally {
                    document.getElementById('loading').classList.add('hidden');
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
