"""
Token Generation Utility for LiveKit Access
This module provides functionality for generating LiveKit access tokens with specific permissions.
"""

from typing import Optional
from livekit.api import AccessToken , VideoGrants
import os
from datetime import datetime, timedelta

class TokenGenerator:
    """
    A utility class for generating LiveKit access tokens with configurable permissions.
    """
    
    def __init__(self):
        """Initialize the TokenGenerator with API key and secret from environment variables."""
        self.api_key = os.getenv('LIVEKIT_API_KEY')
        self.api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in environment variables")

    def generate_token(
        self,
        identity: str,
        room_name: str,
        name: Optional[str] = None,
        ttl: int = 3600,  # 1 hour default
        can_publish: bool = True,
        can_subscribe: bool = True,
        can_publish_data: bool = True
    ) -> str:
        """
        Generate a LiveKit access token with specified permissions.
        """
        token = AccessToken(self.api_key, self.api_secret)
        
        # Set token identity and metadata
        token.identity = identity
        if name:
            token.name = name
            
        # Set token validity period
        token.ttl = timedelta(seconds=ttl)
        
        # Grant room access with specified permissions
        grant = token.grant
        grant.room_join = True
        grant.room = room_name
        grant.can_publish = can_publish
        grant.can_subscribe = can_subscribe
        grant.can_publish_data = can_publish_data
        
        return token.to_jwt()