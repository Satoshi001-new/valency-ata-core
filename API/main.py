import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# 1. Initialize FastAPI
app = FastAPI()

# 2. Setup the Model 
# DO NOT pass api_key here. Pydantic AI reads it from the environment automatically.
gemini_model = GoogleModel('gemini-1.5-flash')

# 3. Define the Data Schemas
class LegacyData(BaseModel):
    raw_payload: str

class ModernOutput(BaseModel):
    device_id: str
    value_celsius: float
    maintenance_required: bool
    ai_analysis: str

# 4. Define the Agent
agent = Agent(
    gemini_model,
    result_type=ModernOutput,
    system_prompt="Extract industrial data. If VAL > 100, maintenance is True."
)

@app.get("/")
async def root():
    # Simple check to see if Vercel sees your key
    return {
        "status": "Valency ATA Online",
        "key_configured": "GEMINI_API_KEY" in os.environ
    }

@app.post("/translate")
async def translate(data: LegacyData):
    try:
        result = await agent.run(data.raw_payload)
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
