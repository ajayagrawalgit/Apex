from apex.agent import root_agent
from google.adk.runtime.framework import AdkApp
import uvicorn
import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

adk_app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

app = adk_app.get_fastapi_app()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        response = root_agent.chat(data["text"])
        await websocket.send_json({"sender": "bot", "text": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)