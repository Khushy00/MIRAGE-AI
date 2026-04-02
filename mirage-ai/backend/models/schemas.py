from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class RequestLog(BaseModel):
    ip_address: str
    endpoint: str
    method: str
    payload: Optional[str] = None
    headers: Optional[dict] = None

class AttackEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attack_type: str
    source_ip: str
    payload: Optional[str]
    severity: str
    action_taken: str

class HoneypotEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attacker_ip: str
    fake_resource_accessed: str
    captured_payload: Optional[str]

class BlockedIP(BaseModel):
    ip_address: str
    reason: str
    blocked_time: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None
