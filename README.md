# AX650/LLM8850 Generative AI Services

## Overview

This project aims to deliver compact, efficient generative AI services, such as LLM chat completions and Stable Diffusion image generation, optimized for the M5Stack AX650/LLM8850 PCIe accelerator running on a Raspberry Pi 5. These services are designed to provide OpenAI-compatible endpoints for seamless integration into existing workflows, with a focus on interactive art installations and similar use cases.

## Goals

1. **Leverage Manufacturer Resources**: Reuse and adapt the provided SDKs, demo repositories, and utilities for the AX650/LLM8850 hardware.
2. **Persistent API Services**: Present pre-tuned models via persistent API listeners for generative tasks, minimizing model load times.
3. **Multi-Model Support**: Enable multiple services to run concurrently while avoiding unnecessary model unloading.
4. **Hardware Monitoring**: Continuously monitor the AX650/LLM8850 status and implement automatic recovery mechanisms.
5. **Python-First Approach**: Prioritize Python for implementation to simplify development and integration.

## Key Features

- **OpenAI-Compatible API**: Provides endpoints for chat completions and other generative tasks, ensuring compatibility with existing OpenAI client libraries.
- **Model Persistence**: Keeps models loaded in memory to minimize latency and ensure responsiveness.
- **Health Monitoring**: Includes a background health monitor to track device temperature, memory usage, and overall status.
- **Stateless Design**: Each request is independent, with no server-side conversation state, simplifying client integration.
- **Extensibility**: Designed to support additional generative AI tasks, such as TTS and STT, in the future.

## Architecture

### Hardware Interaction

The AX650/LLM8850 hardware features two memory pools:
- **System Memory (DRAM)**: Used for general operations and temporary storage.
- **Contiguous Media Memory (CMM)**: Dedicated to model weights, inference buffers, and persistent data.

### Software Stack

- **Runtime API**: Handles NPU inference and memory management.
- **Native API**: Supports video and image processing tasks.
- **Python Bindings**: Utilizes `PyAXEngine` for high-level model execution and `pyaxcl` for low-level hardware interactions.

### Service Design

- **FastAPI Framework**: Provides HTTP endpoints for generative tasks.
- **Model Loading**: Models are loaded at startup and remain resident in CMM.
- **Request Handling**: Stateless design ensures each request includes all necessary context.
- **Health Monitoring**: A background thread periodically checks device metrics and triggers recovery actions if needed.

## Implementation Roadmap

### Phase 1: MVP Development
- Build a FastAPI service with OpenAI-compatible endpoints.
- Load models using `PyAXEngine` and allocate persistent buffers.
- Implement basic health monitoring.

### Phase 2: Performance Tuning
- Optimize concurrency and memory usage.
- Add Prometheus metrics for monitoring.
- Implement systemd service files for deployment.

### Phase 3: Advanced Features
- Add support for session-based KV caching.
- Enable dynamic model loading and unloading.
- Extend API to support additional generative tasks.

## Success Metrics

1. **Reliability**: Services run continuously for 24+ hours without manual intervention.
2. **Performance**: Response times under 3 seconds for typical requests.
3. **Compatibility**: OpenAI client libraries work with minimal changes.
4. **Scalability**: Supports multiple concurrent requests without significant performance degradation.

## Quickstart

### Prerequisites

- Raspberry Pi 5 with AX650/LLM8850 PCIe accelerator.
- Python 3.9+ installed.

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Validate hardware
axcl-smi
axcl-smi info --cmm -d 0

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{"model":"qwen3-4b-ax650","messages":[{"role":"user","content":"Hello"}],"max_tokens":64}'
```

## Future Work

- Extend support for additional generative tasks, such as image-to-text and structured output generation.
- Explore multi-device setups for increased scalability.
- Integrate advanced error handling and recovery mechanisms.

## Acknowledgments

This project builds on the resources and SDKs provided by the AX650/LLM8850 hardware manufacturer. Special thanks to the open-source community for tools and libraries that simplify generative AI development.