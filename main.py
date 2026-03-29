from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
import os

app = FastAPI(title="Valency A.T.A. MVP")

# 1. Define the Legacy Data Schema (The "Problem")
class LegacyPayload(BaseModel):
    raw_string: str  # e.g., "UNIT:04|TEMP:98.6|STAT:OK"
    protocol: str    # e.g., "MODBUS-RTU"

# 2. Define the Modern Output Schema (The "Solution")
class ModernSchema(BaseModel):
    unit_id: int
    temperature_celsius: float
    status: str
    risk_level: str

# 3. Create the Valency Translation Agent
# Note: For the MVP, we use a clear system prompt
agent = Agent(
    'openai:gpt-4o', # Or 'gemini-1.5-flash'
    result_type=ModernSchema,
    system_prompt=(
        "You are the Valency A.T.A. Translation Engine. "
        "Convert legacy industrial strings into modern, type-safe JSON. "
        "Assess risk level based on temperature (Above 100 = High)."
    ),
)

@app.get("/")
def home():
    return {"status": "Valency A.T.A. System Online", "bridge": "Active"}

@app.post("/translate", response_model=ModernSchema)
async def translate_data(payload: LegacyPayload):
    """
    Simulates the bridge between a legacy industrial API and a modern system.
    """
    result = await agent.run(payload.raw_string)
    return result.data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
