import os
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

app = FastAPI()

# Simple Model Setup
gemini_model = GoogleModel('gemini-1.5-flash')

class ModernOutput(BaseModel):
    status: str
    message: str

agent = Agent(gemini_model, result_type=ModernOutput)

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online",
        "key_detected": "GEMINI_API_KEY" in os.environ,
        "region": "IAD1"
    }

@app.get("/test-ai")
async def test_ai():
    try:
        result = await agent.run("Say hello")
        return result.data
    except Exception as e:
        return {"error": str(e)}
