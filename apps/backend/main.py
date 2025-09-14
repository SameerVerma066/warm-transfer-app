import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from pydantic import BaseModel

# FastAPI application setup
app = FastAPI()

# Configuration for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the request payload
class TokenResponse(BaseModel):
    token: str

@app.get("/token", response_model=TokenResponse)
async def get_livekit_token(roomName: str, participantName: str):
    """
    Generates a LiveKit access token for a given room and participant.
    """
    # Load LiveKit credentials from environment variables
    livekit_url = os.environ.get("LIVEKIT_URL")
    livekit_api_key = os.environ.get("LIVEKIT_API_KEY")
    livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET")

    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        raise HTTPException(
            status_code=500,
            detail="Server not configured. LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set as environment variables."
        )

    # Use the LiveKit SDK to create a new access token
    token = api.AccessToken(livekit_api_key, livekit_api_secret)
    token.with_identity(participantName)
    token.with_name(participantName)
    token.with_grants(api.VideoGrants(room_join=True, room=roomName))

    jwt_token = token.to_jwt()

    return {"token": jwt_token}