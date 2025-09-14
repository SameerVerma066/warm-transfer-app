import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants
from pydantic import BaseModel

# FastAPI application setup
app = FastAPI()

# Configuration for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the request payload, now including the LiveKit URL
class TokenResponse(BaseModel):
    token: str
    livekit_url: str

@app.get("/token", response_model=TokenResponse)
async def get_livekit_token(roomName: str, participantName: str):
    livekit_url = os.environ.get("LIVEKIT_URL")
    livekit_api_key = os.environ.get("LIVEKIT_API_KEY")
    livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET")

    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        raise HTTPException(
            status_code=500,
            detail="Server not configured. LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set as environment variables."
        )

    # Use the LiveKit SDK to create a new access token
    token = AccessToken(livekit_api_key, livekit_api_secret)
    token.with_identity(participantName)
    token.with_name(participantName)
    token.with_grants(VideoGrants(room_join=True, room=roomName))

    jwt_token = token.to_jwt()

    # Return both the token and the LiveKit URL
    return {"token": jwt_token, "livekit_url": livekit_url}
