"""
LLM Router Module
Handles endpoints for generating conversation summaries using OpenAI API.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

def get_openai_client() -> OpenAI:
    """
    Create an OpenAI client only when needed and ensure the API key is set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY must be set in environment variables."
        )
    return OpenAI(api_key=api_key)

class SummaryRequest(BaseModel):
    conversation_text: str
    context: str = ""

@router.post("/summarize")
async def generate_summary(
    request: SummaryRequest,
    client: OpenAI = Depends(get_openai_client)
):
    """
    Generate a concise summary of a conversation using OpenAI API.
    """
    try:
        prompt = (
            "Please provide a concise, single-paragraph summary of the following "
            "customer service conversation, focusing on the main issue, key points, "
            "and any resolution.\n\n"
            f"Context: {request.context}\n\n"
            f"Conversation:\n{request.conversation_text}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()
        return {"summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
