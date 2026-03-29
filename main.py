import os
import sys

# 1. DEBUG: Catch errors before FastAPI even starts
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
except Exception as e:
    # If this triggers, your requirements.txt is failing
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

app = FastAPI()

# 2. Setup Agent
# Ensure GEMINI_API_KEY is in Vercel -> Settings -> Environment Variables
gemini_model = GoogleModel('gemini-1.5-flash')

class TranslationResponse(BaseModel):
    status: str
    message: str

agent = Agent(gemini_model, result_type=TranslationResponse)

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online",
        "python_version": sys.version,
        "key_found": "GEMINI_API_KEY" in os.environ
    }

@app.get("/test-ai")
async def test_ai():
    try:
        result = await agent.run("Is the Valency engine online?")
        return result.data
    except Exception as e:
        return {"error": str(e)}
