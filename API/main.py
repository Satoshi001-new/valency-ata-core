import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# Initialize FastAPI
app = FastAPI()

# Setup the Model (Pydantic AI looks for GEMINI_API_KEY env var)
gemini_model = GoogleModel('gemini-1.5-flash')

class LegacyData(BaseModel):
    raw_payload: str

class ModernOutput(BaseModel):
    device_id: str
    value_celsius: float
    maintenance_required: bool

# Agent definition
agent = Agent(gemini_model, result_type=ModernOutput)

@app.get("/")
async def root():
    return {"status": "Valency ATA Online", "key": "GEMINI_API_KEY" in os.environ}

@app.post("/translate")
async def translate(data: LegacyData):
    try:
        result = await agent.run(data.raw_payload)
        return result.data
    except Exception as e:
        return {"error": str(e)}
