import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "Valency ATA Online",
        "system": "Fixed",
        "key_detected": "GEMINI_API_KEY" in os.environ
    }

# This is the entry point Vercel needs
handler = app
