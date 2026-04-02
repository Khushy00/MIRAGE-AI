from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import logging

from models.schemas import RequestLog, AttackEvent, BlockedIP
from detection.engine import engine
from websocket.manager import manager

router = APIRouter(prefix="/api", tags=["API Monitoring"])
logger = logging.getLogger("mirage_ai.api")

async def get_db(request: Request):
    return request.app.state.db

@router.post("/request")
async def process_request(req_log: RequestLog, request: Request):
    """
    Main endpoint that processes all incoming telemetry payload.
    It feeds data to the Detection Engine.
    """
    db = await get_db(request)
    client_ip = request.client.host if request.client else req_log.ip_address

    # Check if IP is already blocked
    is_blocked = await db.blocked_ips.find_one({"ip_address": client_ip})
    if is_blocked:
        raise HTTPException(status_code=403, detail="IP Blocked due to malicious behavior")
    
    # Send through Detection Engine
    is_login = "login" in req_log.endpoint.lower()
    analysis = engine.analyze_payload(client_ip, req_log.endpoint, req_log.payload or "", is_login=is_login)

    # Broadcast raw request event to SOC dashboard
    await manager.broadcast({
        "event_type": "request_received",
        "timestamp": str(datetime.utcnow()),
        "ip": client_ip,
        "endpoint": req_log.endpoint,
        "is_malicious": analysis["is_malicious"]
    })

    if analysis["is_malicious"]:
        event_doc = AttackEvent(
            source_ip=client_ip,
            attack_type=analysis["attack_type"],
            severity=analysis["severity"],
            payload=req_log.payload,
            action_taken=analysis["action"]
        )
        await db.attack_logs.insert_one(event_doc.dict())

        # Broadcast threat event
        await manager.broadcast({
            "event_type": "threat_detected",
            "data": event_doc.dict(exclude={"timestamp" : True}) 
        })

        if "Block" in analysis["action"]:
            blocked_doc = BlockedIP(ip_address=client_ip, reason=analysis["attack_type"])
            await db.blocked_ips.insert_one(blocked_doc.dict())
            
            await manager.broadcast({
                "event_type": "ip_blocked",
                "ip": client_ip,
                "reason": analysis["attack_type"]
            })

            # Force routing to Honeypot
            return JSONResponse(status_code=302, headers={"Location": "/honeypot/admin"}, content={"message": "Redirecting..."})

    return {"status": "success", "message": "Request processed normally."}

@router.get("/logs/events")
async def get_event_logs(request: Request, limit: int = 50):
    db = await get_db(request)
    logs = await db.attack_logs.find().sort("timestamp", -1).limit(limit).to_list(limit)
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs
