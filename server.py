"""
AstroCheck FastAPI Web Application Server
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from app_engine import calculate_chart
from ai_service import query_ai_model

app = FastAPI(title="AstroCheck — Six-Culture Verified Natal System", version="2.0.0")

# Mount static folder
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChartRequest(BaseModel):
    birth_date: str
    birth_time: str
    latitude: float
    longitude: float
    gender: str = "male"
    birthplace_name: str = ""
    time_certainty: str = "exact"
    current_residence: Optional[str] = ""
    custom_tz_offset_hours: Optional[float] = None

class AIExplainRequest(BaseModel):
    provider: str
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    custom_endpoint: Optional[str] = ""
    system_prompt: Optional[str] = "You are a master comparative astrologer and philosopher analyzing a verified six-culture natal chart."
    user_prompt: str
    dossier_text: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/calculate")
async def calculate_endpoint(req: ChartRequest):
    try:
        res = calculate_chart(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            latitude=req.latitude,
            longitude=req.longitude,
            gender=req.gender,
            birthplace_name=req.birthplace_name,
            time_certainty=req.time_certainty,
            current_residence=req.current_residence or "",
            custom_tz_offset_hours=req.custom_tz_offset_hours
        )
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.post("/api/ai/explain")
async def ai_explain_endpoint(req: AIExplainRequest):
    # Only require API key if not using local endpoint (which might not need one)
    if req.provider.lower() not in ["other", "custom"] and (not req.api_key or len(req.api_key.strip()) < 5):
        raise HTTPException(status_code=400, detail="A valid API Key is required for this provider. Please open AI Settings.")
    
    res = query_ai_model(
        provider=req.provider,
        api_key=req.api_key or "",
        model=req.model or "",
        system_prompt=req.system_prompt,
        user_prompt=req.user_prompt,
        dossier_text=req.dossier_text or "",
        custom_endpoint=req.custom_endpoint or ""
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    is_prod = bool(os.environ.get("PORT"))
    print("\n" + "=" * 60)
    print("✨ AstroCheck Web App is ready!")
    print(f"👉 Running on http://{host}:{port}")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host=host, port=port, reload=not is_prod)
