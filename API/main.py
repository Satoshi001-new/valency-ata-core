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

# 3. Define the Data Schema
class ModernOutput(BaseModel):
    status: str
    message: str

# 4. Define the Agent
agent = Agent(gemini_model, result_type=ModernOutput)

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online",
        "key_detected": "GEMINI_API_KEY" in os.environ
    }

@app.get("/test-ai")
async def test_ai():
    try:
        # A quick test to ensure the agent is actually talking to Google
        result = await agent.run("Confirm system connection")
        return result.data
    except Exception as e:
        return {"error": str(e)}
