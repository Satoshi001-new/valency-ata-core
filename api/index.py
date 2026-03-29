import os
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# 1. Initialize FastAPI
app = FastAPI()

# 2. Setup the Model
# Important: Ensure GEMINI_API_KEY is in your Vercel Environment Variables!
gemini_model = GoogleModel('gemini-1.5-flash')

class StatusResponse(BaseModel):
    status: str
    engine: str
    key_found: bool

# 3. Define the Agent
agent = Agent(gemini_model, result_type=StatusResponse)

@app.get("/api")
async def root():
    return {
        "status": "Valency ATA Online",
        "key_detected": "GEMINI_API_KEY" in os.environ
    }

@app.get("/api/test")
async def test_ai():
    try:
        result = await agent.run("Confirm system connection")
        return result.data
    except Exception as e:
        return {"error": str(e)}
