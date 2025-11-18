import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Use the path to your agent.py and subagents
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app_args = {
    "agents_dir": AGENT_DIR,  # directory containing agent.py
    "web": True              # enables ADK web interface
}

app: FastAPI = get_fast_api_app(**app_args)

app.title = "Apex ADK Agent"
app.description = "Apex: Malicious URL Analyzer with Google ADK web interface"
app.version = "1.0.0"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "apex-adk-agent"}

@app.get("/")
def root():
    return {
        "service": "apex-adk-agent",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
