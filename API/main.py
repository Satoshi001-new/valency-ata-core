import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# 1. Initialize FastAPI
app = FastAPI()

# 2. Setup the Model (DO NOT PASS api_key IN CODE)
# Ensure GEMINI_API_KEY is in your Vercel Project Settings -> Env Variables
gemini_model = GoogleModel('gemini-1.5-flash')

class TranslationResponse(BaseModel):
    device_id: str
    status: str
    maintenance: bool

# 3. Define the Agent
agent = Agent(gemini_model, result_type=TranslationResponse)

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online", 
        "key_active": "GEMINI_API_KEY" in os.environ
    }

@app.post("/translate")
async def translate(payload: str):
    try:
        result = await agent.run(payload)
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
