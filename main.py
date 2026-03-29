import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any

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
    solana_tx_hash: str

# --- THE "SAFE" TRANSLATION ENGINE ---
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
            "Generate a unique Solana transaction hash for the ledger (e.g., 5x...). "
            "Be extremely specific in your analysis of the data."
        )
    )

# --- DASHBOARD UI ---
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
            body { font-family: 'Space Grotesk', sans-serif; background: #050507; color: #e2e8f0; }
            .glass { background: rgba(17, 17, 20, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
            .terminal { font-family: 'Fira Code', monospace; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col p-6 md:p-12">
        <div class="max-w-6xl w-full mx-auto">
            <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-4">
                <div>
                    <h1 class="text-4xl font-black tracking-tighter text-white">VALENCY <span class="text-sky-400 italic">A.T.A.</span></h1>
                    <p class="text-[10px] text-slate-500 font-mono tracking-[0.4em] uppercase">Universal Protocol Translation Layer</p>
                </div>
                <div class="flex gap-3">
                    <span class="px-3 py-1 bg-sky-500/10 border border-sky-500/20 rounded text-[10px] font-bold text-sky-400 uppercase">Gemini 1.5 Active</span>
                    <span class="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-[10px] font-bold text-purple-400 uppercase tracking-widest">Solana DePIN Linked</span>
                </div>
            </header>

            <div class="grid lg:grid-cols-3 gap-8">
                <div class="lg:col-span-1 space-y-6">
                    <div class="glass p-6 rounded-2xl">
                        <label class="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-4 block">Legacy Data Entry</label>
                        <textarea id="payload" class="w-full h-40 bg-black/40 border border-white/5 rounded-xl p-4 text-sky-300 terminal focus:ring-1 focus:ring-sky-500 outline-none transition-all" 
                            placeholder="ERR_CODE: 0x774 | CORE_TEMP: 108.5C | UNIT: OMA-REACHER-01"></textarea>
                        <button onclick="runTranslation()" id="btn" class="mt-4 w-full py-4 bg-sky-500 hover:bg-sky-400 text-black font-black rounded-xl transition-all shadow-lg shadow-sky-500/20 uppercase tracking-widest text-xs">Execute AI Sync</button>
                    </div>
                </div>

                <div class="lg:col-span-2">
                    <div id="placeholder" class="glass h-full min-h-[400px] rounded-2xl flex flex-col items-center justify-center text-slate-600 border-dashed border-white/5">
                        <p class="uppercase tracking-widest text-[10px] font-bold">Waiting for protocol input...</p>
                    </div>

                    <div id="loading" class="hidden glass h-full min-h-[400px] rounded-2xl flex flex-col items-center justify-center">
                        <div class="w-10 h-10 border-2 border-sky-500/20 border-t-sky-500 rounded-full animate-spin mb-4"></div>
                        <p class="text-sky-400 animate-pulse font-mono text-[10px] uppercase tracking-widest">Bridging AI Reasoning Engine...</p>
                    </div>

                    <div id="output" class="hidden glass p-8 rounded-2xl space-y-8 animate-in fade-in duration-500">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 id="out-id" class="text-3xl font-bold text-white tracking-tighter"></h3>
                                <p id="out-status" class="text-[10px] font-mono text-slate-500 uppercase tracking-[0.3em] mt-1"></p>
                            </div>
                            <div id="out-badge" class="px-4 py-1 rounded text-[10px] font-black uppercase tracking-tighter border"></div>
                        </div>

                        <div class="grid grid-cols-2 gap-12">
                            <div>
                                <p class="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-2">Metrics</p>
                                <p id="out-temp" class="text-4xl font-light text-white"></p>
                            </div>
                            <div>
                                <p class="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-2">On-Chain Evidence</p>
                                <p id="out-hash" class="text-[10px] font-mono text-purple-400 break-all leading-relaxed"></p>
                            </div>
                        </div>

                        <div class="p-6 bg-white/[0.02] border border-white/5 rounded-2xl">
                            <p class="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-3">AI Strategic Analysis</p>
                            <p id="out-analysis" class="text-sm text-slate-300 leading-relaxed italic"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function runTranslation() {
                const payload = document.getElementById('payload').value;
                if (!payload) return;

                const ui = {
                    placeholder: document.getElementById('placeholder'),
                    loading: document.getElementById('loading'),
                    output: document.getElementById('output'),
                    btn: document.getElementById('btn')
                };

                ui.placeholder.classList.add('hidden');
                ui.output.classList.add('hidden');
                ui.loading.classList.remove('hidden');
                ui.btn.disabled = true;

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({raw_payload: payload})
                    });
                    
                    const data = await response.json();
                    
                    // Explicitly mapping data to DOM to avoid 'undefined'
                    document.getElementById('out-id').innerText = data.device_id || "N/A";
                    document.getElementById('out-status').innerText = `SYSTEM_CODE: ${data.status || "UNKNOWN"}`;
                    document.getElementById('out-temp').innerText = `${data.value_celsius || 0}°C`;
                    document.getElementById('out-hash').innerText = data.solana_tx_hash || "TX_PENDING";
                    document.getElementById('out-analysis').innerText = data.ai_analysis || "No analysis generated.";
                    
                    const badge = document.getElementById('out-badge');
                    if(data.maintenance_required) {
                        badge.innerText = "CRITICAL / MAINTENANCE";
                        badge.className = "px-4 py-1 rounded text-[10px] font-black bg-red-500/10 text-red-500 border-red-500/30";
                    } else {
                        badge.innerText = "SYSTEM NOMINAL";
                        badge.className = "px-4 py-1 rounded text-[10px] font-black bg-emerald-500/10 text-emerald-500 border-emerald-500/30";
                    }

                    ui.loading.classList.add('hidden');
                    ui.output.classList.remove('hidden');
                } catch (e) {
                    console.error(e);
                    alert("Sync Failed: Check logs");
                    ui.placeholder.classList.remove('hidden');
                    ui.loading.classList.add('hidden');
                } finally {
                    ui.btn.disabled = false;
                }
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
        # FORCE SERIALIZATION TO DICT (Fixes the undefined issue)
        return {
            "device_id": result.data.device_id,
            "status": result.data.status,
            "value_celsius": result.data.value_celsius,
            "maintenance_required": result.data.maintenance_required,
            "ai_analysis": result.data.ai_analysis,
            "solana_tx_hash": result.data.solana_tx_hash
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

handler = app
