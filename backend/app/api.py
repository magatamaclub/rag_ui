
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import json

from .database import get_db
from .models import DifyConfig

router = APIRouter()

# Dify API configuration (will be fetched from DB)
DIFY_API_URL = None
DIFY_API_KEY = None

class DifyConfigCreate(BaseModel):
    api_url: str
    api_key: str

@router.post("/dify-config")
async def set_dify_config(config: DifyConfigCreate, db: Session = Depends(get_db)):
    existing_config = db.query(DifyConfig).first()
    if existing_config:
        existing_config.api_url = config.api_url
        existing_config.api_key = config.api_key
    else:
        new_config = DifyConfig(api_url=config.api_url, api_key=config.api_key)
        db.add(new_config)
    db.commit()
    db.refresh(existing_config or new_config)
    global DIFY_API_URL, DIFY_API_KEY
    DIFY_API_URL = config.api_url
    DIFY_API_KEY = config.api_key
    return {"message": "Dify configuration saved successfully"}

@router.get("/dify-config")
async def get_dify_config(db: Session = Depends(get_db)):
    config = db.query(DifyConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Dify configuration not found")
    return {"api_url": config.api_url, "api_key": config.api_key}

@router.on_event("startup")
async def load_dify_config_on_startup(db: Session = Depends(get_db)):
    global DIFY_API_URL, DIFY_API_KEY
    config = db.query(DifyConfig).first()
    if config:
        DIFY_API_URL = config.api_url
        DIFY_API_KEY = config.api_key

@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    if not DIFY_API_URL or not DIFY_API_KEY:
        raise HTTPException(status_code=400, detail="Dify API configuration is missing. Please set it via /api/v1/dify-config.")

    url = f"{DIFY_API_URL}/files/upload"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}"
    }
    files = {
        'file': (file.filename, await file.read(), file.content_type)
    }
    data = {
        'user': 'gemini-user' # A unique identifier for the user
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Dify API: {e}")

@router.post("/chat")
async def chat(request: Request):
    if not DIFY_API_URL or not DIFY_API_KEY:
        raise HTTPException(status_code=400, detail="Dify API configuration is missing. Please set it via /api/v1/dify-config.")

    data = await request.json()
    query = data.get("query")
    conversation_id = data.get("conversation_id")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    url = f"{DIFY_API_URL}/chat-messages"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": "gemini-user",
        "conversation_id": conversation_id if conversation_id else ""
    }

    def generate_dify_response():
        try:
            with requests.post(url, headers=headers, json=payload, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error calling Dify chat API: {e}")

    return StreamingResponse(generate_dify_response(), media_type="text/event-stream")
