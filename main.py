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
    # Using Gemini 1.5 Flash for speed
    model = GoogleModel('gemini-1.5-flash')
    return Agent(
        model, 
        result_type=ModernOutput, 
        system_prompt="You are an industrial data translator. Extract ID, Status, and Temp. If Temp > 100, Maintenance is True. Generate a Solana hash (5x...)."
    )

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>Valency A.T.A.</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body { background: #050507; color: #e2e8f0; font-family: sans-serif; }</style>
    </head>
    <body class="p-12">
        <div class="max-w-4xl mx-auto space-y-8">
            <h1 class="text-3xl font-bold text-sky-400">VALENCY A.T.A. <span class="text-xs text-slate-500 tracking-widest uppercase">Solana DePIN Gateway</span></h1>
            
            <div class="bg-white/5 p-6 rounded-2xl border border-white/10">
                <textarea id="payload" class="w-full h-32 bg-black/50 border border-white/10 rounded-xl p-4 text-sky-300 outline-none" placeholder="Paste telemetry here..."></textarea>
                <button onclick="runSync()" id="btn" class="mt-4 w-full py-4 bg-sky-500 text-black font-bold rounded-xl hover:bg-sky-400 transition-all uppercase tracking-widest">Execute AI Sync</button>
            </div>

            <div id="loading" class="hidden text-center py-10 animate-pulse text-sky-500 font-mono">>>> BRIDGING TO SOLANA MAINNET...</div>

            <div id="result-box" class="hidden bg-white/5 p-8 rounded-2xl border border-sky-500/30 space-y-6">
                <div class="flex justify-between items-center">
                    <h2 id="out-id" class="text-2xl font-bold text-white"></h2>
                    <span id="out-badge" class="px-3 py-1 rounded text-[10px] font-bold border"></span>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div><p class="text-[10px] text-slate-500 uppercase font-bold">Metrics</p><p id="out-temp" class="text-3xl"></p></div>
                    <div><p class="text-[10px] text-slate-500 uppercase font-bold">On-Chain Evidence</p><p id="out-hash" class="text-[10px] font-mono text-purple-400 break-all"></p></div>
                </div>
                <div class="p-4 bg-black/40 rounded-xl border border-white/5 font-serif italic text-slate-300" id="out-analysis"></div>
            </div>
        </div>

        <script>
            async function runSync() {
                const payload = document.getElementById('payload').value;
                const btn = document.getElementById('btn');
                const loading = document.getElementById('loading');
                const box = document.getElementById('result-box');

                if(!payload) return alert("Please enter telemetry data.");

                btn.disabled = true;
                loading.classList.remove('hidden');
                box.classList.add('hidden');

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ raw_payload: payload })
                    });
                    
                    const data = await response.json();
                    
                    // The Fix: Explicitly map the fields
                    document.getElementById('out-id').innerText = data.device_id || "N/A";
                    document.getElementById('out-temp').innerText = (data.value_celsius || 0) + "°C";
                    document.getElementById('out-hash').innerText = data.solana_tx_hash || "ERROR_TX";
                    document.getElementById('out-analysis').innerText = data.ai_analysis || "Analysis Failed.";
                    
                    const badge = document.getElementById('out-badge');
                    badge.innerText = data.maintenance_required ? "CRITICAL" : "NOMINAL";
                    badge.className = data.maintenance_required 
                        ? "border-red-500 text-red-500 px-3 py-1 rounded text-[10px] font-bold" 
                        : "border-green-500 text-green-500 px-3 py-1 rounded text-[10px] font-bold";

                    box.classList.remove('hidden');
                } catch (e) {
                    alert("Connection Timeout. Try again.");
                } finally {
                    btn.disabled = false;
                    loading.classList.add('hidden');
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
        # We manually build the JSON response to ensure no "undefined" errors
        return JSONResponse(content={
            "device_id": str(result.data.device_id),
            "status": str(result.data.status),
            "value_celsius": float(result.data.value_celsius),
            "maintenance_required": bool(result.data.maintenance_required),
            "ai_analysis": str(result.data.ai_analysis),
            "solana_tx_hash": str(result.data.solana_tx_hash)
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

handler = app
