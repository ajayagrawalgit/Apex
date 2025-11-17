from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os
from apex.agent import root_agent

app = FastAPI(title="Apex URL Safety Analyzer")

@app.get("/")
async def root():
    return {"message": "Apex URL Safety Analyzer API", "status": "running"}

@app.post("/analyze")
async def analyze_url(request: dict):
    """
    Analyze URL safety
    Request body: {"url": "https://example.com"}
    """
    url = request.get("url")
    if not url:
        return JSONResponse(
            status_code=400,
            content={"error": "URL is required"}
        )
    
    try:
        # Execute the root agent with the URL
        result = await root_agent.run(
            user_prompt=f"Analyze the safety of this URL: {url}"
        )
        return {"result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)