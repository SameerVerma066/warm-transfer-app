"""
LiveKit Router Module
Handles all LiveKit-specific endpoints including token generation and room management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from utils.token_generator import TokenGenerator
import uuid

router = APIRouter()

# Dependency to create TokenGenerator only when needed
def get_token_generator() -> TokenGenerator:
    return TokenGenerator()

class TokenRequest(BaseModel):
    identity: str
    room_name: str
    name: Optional[str] = None

class WarmTransferRequest(BaseModel):
    caller_id: str
    agent_a_id: str
    agent_b_id: str
    current_room: str
    conversation_context: str

class DisconnectRequest(BaseModel):
    room_name: str
    participant_id: str


@router.post("/token")
async def generate_token(
    request: TokenRequest,
    token_generator: TokenGenerator = Depends(get_token_generator)
):
    """
    Generate a LiveKit access token for a participant.
    """
    try:
        token = token_generator.generate_token(
            identity=request.identity,
            room_name=request.room_name,
            name=request.name
        )
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm-transfer")
async def initiate_warm_transfer(
    request: WarmTransferRequest,
    token_generator: TokenGenerator = Depends(get_token_generator)
):
    """
    Initiate a warm transfer by creating a new room and generating tokens.
    """
    try:
        new_room = f"transfer-{uuid.uuid4()}"
        caller_token = token_generator.generate_token(
            identity=request.caller_id,
            room_name=new_room
        )
        agent_b_token = token_generator.generate_token(
            identity=request.agent_b_id,
            room_name=new_room
        )
        return {
            "new_room": new_room,
            "caller_token": caller_token,
            "agent_b_token": agent_b_token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def disconnect_participant(request: DisconnectRequest):
    """
    Disconnect a participant from a room.
    """
    try:
        # In production, use LiveKit server API to force-disconnect.
        return {
            "message": f"Participant {request.participant_id} disconnected from room {request.room_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
