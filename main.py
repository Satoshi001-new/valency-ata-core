import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Data Schemas
class LegacyData(BaseModel):
    raw_payload: str

class ModernOutput(BaseModel):
    device_id: str
    status: str
    value_celsius: float
    maintenance_required: bool
    ai_analysis: str

# Lazy Loading Function for the Agent
def get_agent():
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    
    model = GoogleModel('gemini-1.5-flash')
    return Agent(
        model, 
        result_type=ModernOutput,
        system_prompt="You are the Valency A.T.A. Translator. Extract ID, STATUS, and TEMP (as value_celsius). If TEMP > 100, maintenance is True."
    )

@app.get("/")
async def root():
    return {"status": "Valency ATA Online", "mode": "Agentic AI Active"}

@app.post("/translate", response_model=ModernOutput)
async def translate_payload(data: LegacyData):
    try:
        agent = get_agent()
        result = await agent.run(data.raw_payload)
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = app
