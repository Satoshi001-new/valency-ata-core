import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# 1. Initialize FastAPI
app = FastAPI(title="Valency A.T.A. Translation Bridge")

# 2. Setup the Free Gemini Model
# Pydantic AI automatically looks for 'GEMINI_API_KEY' in your environment.
gemini_model = GoogleModel('gemini-1.5-flash')

# 3. Define the Data Schemas
class LegacyData(BaseModel):
    raw_payload: str
    source_protocol: str

class ModernOutput(BaseModel):
    device_id: str
    status: str
    value_celsius: float
    maintenance_required: bool
    ai_analysis: str

# 4. Define the Agent
# Fixed: 'result_type' is now 'result_data_type' in the latest pydantic-ai version
agent = Agent(
    gemini_model,
    result_data_type=ModernOutput,
    system_prompt=(
        "You are the Valency A.T.A. Industrial Translator. "
        "Extract structured data from legacy strings. "
        "Example input: 'DEV_01|VAL:102.5'. "
        "If 'VAL' is over 100, set maintenance_required to True."
    ),
)

@app.get("/")
def health_check():
    # Check if the environment variable is present
    has_key = "GEMINI_API_KEY" in os.environ
    return {
        "status": "Valency A.T.A. System Online", 
        "engine": "Gemini-1.5-Flash",
        "key_detected": has_key
    }

@app.post("/translate", response_model=ModernOutput)
async def translate_payload(data: LegacyData):
    try:
        # Run the agent to translate the raw string into the Pydantic model
        result = await agent.run(data.raw_payload)
        return result.data
    except Exception as e:
        # Catch any API or logic errors
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
