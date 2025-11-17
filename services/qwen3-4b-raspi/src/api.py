"""FastAPI app exposing a small OpenAI-compatible subset for chat completions.

Endpoints:
- POST /v1/completions - chat completion (expects OpenAI-like payload)
- GET /v1/models - list models
- POST /v1/models/load - admin: set current model
- GET /health - simple liveness/readiness
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time
import uuid

import config as _config
settings = _config.settings

from tokenizer import load_tokenizer
from model_manager import ModelManager
from runtime_adapter import runtime_adapter
from utils import logger


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = Field(default=0.0)
    max_tokens: Optional[int] = Field(default=None)


class CompletionChoice(BaseModel):
    index: int
    message: Dict[str, str]
    finish_reason: str


class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Dict[str, int]


app = FastAPI(title="qwen3-4b-raspi")

# Global components
tokenizer = load_tokenizer(None)
model_manager = ModelManager(settings.MODEL_BASE_PATH)


@app.get("/health")
async def health():
    runtime_ok = runtime_adapter.health()
    return {"status": "ok" if runtime_ok else "degraded", "runtime": runtime_ok}


@app.get("/v1/models")
async def list_models():
    return model_manager.list_models()


@app.post("/v1/models/load")
async def load_model(model_id: str):
    try:
        ok = model_manager.load_model(model_id)
        return {"loaded": model_id}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@app.post("/v1/completions")
async def completions(req: CompletionRequest):
    # Basic validation
    if req.max_tokens is None:
        req.max_tokens = settings.DEFAULT_MAX_TOKENS
    if req.max_tokens > settings.MAX_CONTEXT_TOKENS:
        raise HTTPException(status_code=400, detail="max_tokens exceeds allowed limit")

    # Build system prompt from messages if present
    system_prompt = ""
    for m in req.messages:
        if m.role == "system":
            system_prompt = m.content
            break

    # Convert messages to runtime format (exclude system messages - they go via reset)
    runtime_messages = [{"role": m.role, "content": m.content} for m in req.messages if m.role != "system"]

    try:
        resp = runtime_adapter.reset_then_chat(system_prompt=system_prompt, messages=runtime_messages, params={
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        })
    except Exception as exc:
        logger.error(f"Inference error: {exc}")
        raise HTTPException(status_code=503, detail=str(exc))

    # Runtime returns {"done": true, "message": "..."} or mock returns {"text": "...", "usage": {...}}
    if isinstance(resp, dict) and "message" in resp:
        # Real runtime format
        text = resp["message"]
        # Estimate token usage from text length
        usage = {"prompt_tokens": sum(len(m["content"].split()) for m in runtime_messages), 
                 "completion_tokens": len(text.split())}
    elif isinstance(resp, dict) and "text" in resp:
        # Mock format
        text = resp["text"]
        usage = resp.get("usage", {"prompt_tokens": 0, "completion_tokens": len(text.split())})
    else:
        # Fallback
        text = str(resp)
        usage = {"prompt_tokens": 0, "completion_tokens": len(text.split())}

    out = CompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        object="chat.completion",
        created=int(time.time()),
        model=req.model,
        choices=[CompletionChoice(index=0, message={"role": "assistant", "content": text}, finish_reason="stop")],
        usage={
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
            "total_tokens": int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0)),
        },
    )

    return out.dict()
