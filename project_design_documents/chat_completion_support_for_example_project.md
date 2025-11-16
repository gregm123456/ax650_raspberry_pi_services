# Chat Completion Support for Example Project (coyote_interactive)

**Date**: November 16, 2025  
**Status**: Requirements Analysis

---

## Executive Summary

This document analyzes the `coyote_interactive` sample project to identify specific requirements our AX650/LLM8850 chat completion service must support for interactive art installations.

**Key Findings**:
1. **Stateful Conversations**: External conversation state management (JSON file-based)
2. **Low Latency Required**: Interactive response times needed for real-time conversations
3. **Flexible LLM Backend**: Must support drop-in replacement for Azure OpenAI and Ollama
4. **Parameter Control**: Temperature, max_tokens, top_p, etc. must be configurable per request
5. **Conversation Persistence**: Long-running conversations with archival support

---

## Sample Project Analysis

### Architecture Overview

The `coyote_interactive` project is a Raspberry Pi-based interactive art installation where "Wile E. Coyote" watches television and talks with visitors. It demonstrates a **real-world interactive art use case** that our service must support.

**Core Flow**:
```
┌──────────────────────────────────────────────┐
│  Hardware Inputs (Buttons, Switch, Audio)    │
├──────────────────────────────────────────────┤
│  Event Loop (coyote.py)                      │
│  - TV button → comment_on_television()       │
│  - Person button → talk_with_person()        │
│  - Continuous transcription (whisper-stream) │
├──────────────────────────────────────────────┤
│  Conversation Manager                        │
│  - JSON file storage (conversation.json)     │
│  - System message + conversation history     │
│  - Archive on demand (timestamped)           │
├──────────────────────────────────────────────┤
│  LLM Chat Completion (llm_chat_completion.py)│
│  - Currently: Azure OpenAI OR Ollama         │
│  - Future: AX650 local service               │
├──────────────────────────────────────────────┤
│  Hardware Outputs (LEDs, TTS)                │
└──────────────────────────────────────────────┘
```

### Current LLM Integration Patterns

#### 1. Conversation State Management

**External State Storage** (not managed by LLM service):
```python
# conversation.json structure
[
    {"role": "system", "content": "You are Wile E. Coyote..."},
    {"role": "user", "content": "Here's what you heard on TV..."},
    {"role": "assistant", "content": "The product I heard is..."},
    # ... conversation continues
]
```

**Implication for AX650 Service**:
- Service receives **full conversation array** with each request
- Service is **stateless** — no server-side conversation tracking required
- Client manages conversation history, archiving, and system message

#### 2. Request Pattern

**Azure OpenAI Implementation**:
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=config.AZURE_OPENAI_GPT4_ENDPOINT,
    api_key=config.AZURE_OPENAI_GPT4_KEY,
    api_version="2024-02-15-preview"
)

completion = client.chat.completions.create(
    model=config.AZURE_MODEL,
    messages=messages,  # Full conversation array
    temperature=0.9,
    max_tokens=125,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
)

response = completion.choices[0].message.content
```

**Ollama Implementation**:
```python
payload = {
    "model": config.OLLAMA_MODEL,
    "keep_alive": -1,  # Keep model loaded indefinitely
    "stream": False,
    "options": {
        "temperature": 0.99,
        "top_k": 85,
        "top_p": 0.9,
        "num_ctx": 1024,
        "repeat_last_n": 64,
        "repeat_penalty": 1.5,
        "num_predict": 100,
        "stop": ["#", "["]
    },
    "messages": messages
}

response = requests.post(config.OLLAMA_ENDPOINT, json=payload)
response_json = response.json()
text = response_json['message']['content']
```

**Implication for AX650 Service**:
- Must support **OpenAI-compatible API format** (priority)
- Should also support **Ollama-compatible format** (nice-to-have)
- Must accept `messages` array with `role` and `content` fields
- Must return response in expected JSON structure

#### 3. Performance Requirements

**Interactive Response Times**:
- User presses button → LED indicates processing → Audio response plays
- Target: **< 5 seconds** from button press to audio start for acceptable UX
- Breakdown:
  - Audio capture: ~5-30 seconds (variable, user-controlled)
  - LLM inference: **< 3 seconds** (critical path)
  - TTS: ~1-2 seconds

**LED Feedback Patterns** (indicate LLM is working):
```python
# Start LED during LLM processing
led_thread = start_led(led_intercom, "flashing")
response = llm_chat_completion(conversation_file)
stop_led(led_thread)
```

**Implication for AX650 Service**:
- Must provide **fast inference** (< 3s for ~100 token responses)
- Model must stay **loaded and warm** (no cold-start delays)
- Synchronous blocking responses are acceptable (no streaming required initially)

#### 4. Parameter Configuration

**Required Parameters**:
- `temperature`: 0.9-0.99 (high creativity for character)
- `max_tokens`: 100-125 (brief responses)
- `top_p`: 0.9-0.95 (nucleus sampling)
- `stop`: Custom stop sequences (e.g., `["#", "["]`)

**Optional Parameters** (Ollama-specific):
- `top_k`: 85
- `repeat_last_n`: 64
- `repeat_penalty`: 1.5
- `num_ctx`: 1024 (context window)
- `keep_alive`: -1 (keep model loaded)

**Implication for AX650 Service**:
- Must support **per-request parameter overrides**
- Default values should be reasonable but configurable
- `keep_alive` equivalent → model persistence (already planned)

### 5. Conversation Length & Context

**Typical Usage Patterns**:
- **Short sessions**: 5-10 exchanges (TV commentary mode)
- **Long sessions**: 20-50+ exchanges (visitor conversations)
- **Context window**: 1024-2048 tokens typical
- **System message**: ~100 tokens (character definition)

**Archival System**:
```python
def archive_conversation(config):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_file_name = f"conversation_{timestamp}.json"
    os.rename(conversation_file, archived_file)
```

**Implication for AX650 Service**:
- Must handle **context windows of 2048+ tokens**
- No server-side archival needed (client handles)
- Should gracefully handle context overflow (truncate or error)

---

## API Compatibility Requirements

### Priority 1: OpenAI-Compatible Endpoint

**Target**: Drop-in replacement for `openai.AzureOpenAI`

**Endpoint**: `POST /v1/chat/completions`

**Request Body**:
```json
{
  "model": "qwen3-4b-ax650",
  "messages": [
    {"role": "system", "content": "You are..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.9,
  "max_tokens": 125,
  "top_p": 0.95,
  "frequency_penalty": 0,
  "presence_penalty": 0,
  "stop": null
}
```

**Response Body**:
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1732000000,
  "model": "qwen3-4b-ax650",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The product I heard about is..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

**Client Code Migration** (minimal changes):
```python
# OLD: Azure OpenAI
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint="https://...",
    api_key="..."
)

# NEW: AX650 Local Service
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # or remove auth entirely
)

# Same API calls work!
completion = client.chat.completions.create(
    model="qwen3-4b-ax650",
    messages=messages,
    temperature=0.9,
    max_tokens=125
)
```

### Priority 2: Ollama-Compatible Endpoint (Optional)

**Endpoint**: `POST /api/chat`

**Request Body**:
```json
{
  "model": "qwen3-4b-ax650",
  "messages": [...],
  "stream": false,
  "options": {
    "temperature": 0.99,
    "top_k": 85,
    "top_p": 0.9,
    "num_predict": 100
  }
}
```

**Response Body**:
```json
{
  "model": "qwen3-4b-ax650",
  "created_at": "2025-11-16T...",
  "message": {
    "role": "assistant",
    "content": "..."
  },
  "done": true
}
```

---

## System Integration Checklist

### Must-Have Features

- [ ] **OpenAI-compatible `/v1/chat/completions` endpoint**
- [ ] **Stateless request handling** (client manages conversation)
- [ ] **Fast inference** (< 3s for 100 tokens)
- [ ] **Model persistence** (no cold starts)
- [ ] **Parameter support**: `temperature`, `max_tokens`, `top_p`, `stop`
- [ ] **Context window**: 2048+ tokens
- [ ] **Standard JSON response format**

### Should-Have Features

- [ ] **Ollama-compatible `/api/chat` endpoint** (for easy migration)
- [ ] **Health check endpoint** (`/health`)
- [ ] **Model info endpoint** (`/v1/models`)
- [ ] **Metrics endpoint** (`/metrics`) for monitoring
- [ ] **Graceful error handling** (context overflow, OOM, etc.)

### Nice-to-Have Features

- [ ] **Streaming responses** (`stream=true`) for future UX improvements
- [ ] **Multiple model support** (dynamic loading/unloading)
- [ ] **Request queuing** with priority levels
- [ ] **API key authentication** (optional security)

---

## Migration Path for Coyote Interactive

### Step 1: Configuration Changes

**Add to `config_secrets.py`**:
```python
# AX650 Local LLM Service
AX650_ENDPOINT = "http://localhost:8000/v1"
AX650_MODEL = "qwen3-4b-ax650"
AX650_MAX_TOKENS = 125
```

**Update `config.py`**:
```python
# LLM configuration
# azure, ollama, or ax650
LLM = "ax650"
```

### Step 2: Add AX650 Backend to llm_chat_completion.py

```python
def chat_completion_ax650(conversation_file):
    # Load conversation messages from file
    with open(conversation_file, "r") as f:
        messages = json.load(f)

    # Use OpenAI client with local base_url
    from openai import OpenAI
    client = OpenAI(
        base_url=config.AX650_ENDPOINT,
        api_key="not-needed"  # No auth for local service
    )

    completion = client.chat.completions.create(
        model=config.AX650_MODEL,
        messages=messages,
        temperature=0.9,
        max_tokens=config.AX650_MAX_TOKENS,
        top_p=0.95
    )

    response = completion.choices[0].message.content
    print("\n")
    print(response)
    print("\n")

    return response

def llm_chat_completion(conversation_file):
    if config.LLM == "azure":
        return chat_completion_azure(conversation_file)
    elif config.LLM == "ollama":
        return chat_completion_ollama(conversation_file)
    elif config.LLM == "ax650":
        return chat_completion_ax650(conversation_file)
    # Fallback
    return f"Unknown LLM: {config.LLM}"
```

### Step 3: Testing

**Smoke Test**:
```bash
# Start AX650 service
cd ~/ax650_llm_service
python main.py

# In coyote_interactive, update config
LLM = "ax650"

# Test conversation
python coyote.py
# Press TV button, verify response
# Press person button, verify conversation flow
```

**Performance Verification**:
```python
import time
start = time.time()
response = llm_chat_completion(conversation_file)
elapsed = time.time() - start
print(f"LLM response time: {elapsed:.2f}s")
assert elapsed < 5.0, "Response too slow for interactive use"
```

---

## Lessons for Service Design

### 1. Client-Side State Management is Preferred

**Why it works**:
- Simple for clients (just maintain JSON array)
- No server-side session complexity
- Easy to archive/backup conversations
- Natural for art installations (persistence across reboots)

**Service implication**:
- Don't build complex session/KV cache management initially
- Focus on **fast, stateless inference**
- Let clients handle conversation history

### 2. Low Latency Over Throughput

**Interactive art prioritizes**:
- Fast single-request response (< 3s)
- Model always warm and ready
- Minimal queuing delay

**Not critical**:
- High concurrent request throughput
- Batch processing
- Multi-user scaling

**Service implication**:
- **Single-request optimization** over queue management
- Keep model loaded permanently
- Simple FIFO queue sufficient initially

### 3. Reasonable Defaults, Easy Overrides

**Good defaults for interactive art**:
```python
{
  "temperature": 0.9,  # Creative but coherent
  "max_tokens": 100,   # Brief responses
  "top_p": 0.95,       # Diverse but focused
  "stop": None         # Natural endings
}
```

**Allow per-request overrides** for experimentation.

### 4. Fail Gracefully

**Installation context**:
- May run unattended for hours/days
- Network issues common
- Hardware errors possible

**Service requirements**:
- Return clear error messages (not crashes)
- Health check endpoint for monitoring
- Automatic recovery from device resets
- Timeout handling (don't hang forever)

---

## Updated Success Criteria

Our service **successfully supports interactive art installations** when:

1. **Drop-in replacement**: Coyote Interactive works with < 10 lines of code changes
2. **Performance**: 95% of requests complete in < 3 seconds (100 token responses)
3. **Reliability**: Service runs for 24+ hours without manual intervention
4. **Compatibility**: OpenAI Python client works without modification
5. **Context**: Handles 2048+ token conversations without errors

**Test Case**: Run full coyote_interactive demo for 1 hour with AX650 service, verify:
- All button interactions work
- Response times feel natural
- No crashes or hangs
- LED feedback patterns work correctly
- Audio output quality maintained
