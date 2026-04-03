from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os

router = APIRouter()

@router.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    print("Received request for /v1/chat/completions")
    body = await request.json()

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:         
            BASE_URL = os.environ['LLM_BASE_URL']
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                json=body,
                headers={"Content-Type": "application/json"},
            )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Upstream LLM unavailable: {str(e)}")
    except ValueError:
        raise HTTPException(status_code=502, detail="Upstream LLM returned non-JSON response")