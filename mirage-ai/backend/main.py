import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

# Local imports
from routes import api
from honeypot import endpoints as honeypot_endpoints
from websocket.manager import manager

app = FastAPI(title="Mirage AI - Active Defense System Backend", version="1.0")

# Setup CORS to allow dashboard connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production ready must restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.mirage_ai

# Set database instance for routes to easily inject
app.state.db = db

# Setup Routes
app.include_router(api.router)
app.include_router(honeypot_endpoints.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for incoming messages if any
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_db_client():
    pass

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
