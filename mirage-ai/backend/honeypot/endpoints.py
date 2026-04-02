from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

router = APIRouter(prefix="/honeypot", tags=["Honeypot Decoys"])
logger = logging.getLogger("mirage_ai.honeypot")

@router.get("/admin")
@router.post("/admin")
async def fake_admin(request: Request):
    """
    Honeypot endpoint that looks like a vulnerability.
    """
    client_ip = request.client.host
    logger.warning(f"HONEYPOT TRIPPED: Potential attacker {client_ip} accessed /admin")
    
    # Return fake admin configuration that looks legitimate to an attacker
    fake_config = {
        "status": "success",
        "system": "Production Node 01",
        "db_connection": "mysql://root:superman123@prod-db.local:3306/users",
        "debug_mode": True,
        "users": [
            {"id": 1, "username": "admin", "hash": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"},
            {"id": 2, "username": "system_svc", "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
        ]
    }
    return JSONResponse(content=fake_config, status_code=200)

@router.get("/config")
@router.get("/backup")
async def fake_sensitive_files(request: Request):
    client_ip = request.client.host
    logger.warning(f"HONEYPOT TRIPPED: Arbitrary file read attempt by {client_ip} on {request.url.path}")
    
    fake_backup = """
    # SERVER CONFIGURATION BACKUP
    export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
    export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    export DB_PASSWORD="master_password_42!"
    """
    return JSONResponse(content={"file_content": fake_backup}, status_code=200)
