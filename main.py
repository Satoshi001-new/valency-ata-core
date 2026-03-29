import os
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# 1. Initialize FastAPI
app = FastAPI()

# 2. Setup Agent (Simplified to prevent boot-up crash)
gemini_model = GoogleModel('gemini-1.5-flash')
agent = Agent(gemini_model)

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online",
        "key_found": "GEMINI_API_KEY" in os.environ,
        "msg": "If you see this, the 500 error is fixed."
    }

@app.get("/ai")
async def ai_test():
    try:
        result = await agent.run("Confirm connection")
        return {"response": result.data}
    except Exception as e:
        return {"error": str(e)}

# 3. Vercel looks for 'app' or 'handler'
handler = app
