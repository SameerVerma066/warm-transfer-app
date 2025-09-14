"""
Main FastAPI Application Entry Point
Configures and runs the FastAPI application with all routes and middleware.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import livekit_router, llm_router
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Warm Transfer API",
    description="API for handling warm transfers in LiveKit rooms with conversation summarization",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(livekit_router.router, prefix="/livekit", tags=["livekit"])
app.include_router(llm_router.router, prefix="/llm", tags=["llm"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
