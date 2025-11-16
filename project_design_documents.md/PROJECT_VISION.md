# Project Vision

Project name: Replace with project short name

Elevator pitch
- One-paragraph summary: This project presents compact, efficient contemporary AI models (such as LLM chat completions, vision LLMs, structured output LLMs, diffusion image generators, TTS, STT, etc.) as standard generative AI endpoints (such as OpenAI chat completion or stable diffusion image generation, as examples). It is specifically tuned to run on the M5Stack ax650 / llm8850 PCIe accelerator running on a Raspberry Pi 5 computer running contemporary Bookworm Ubuntu Raspberry Pi OS. Since models and runtimes need to be specially tuned to this specific hardware, we will take inspiration from the manufacturer's demo repos and provided drivers and utilities.

Goals
- Goal 1: Re-use as much as possible from the manufacturer's provided resource and demo repos
- Goal 2: Present select, pre-tuned available models for M5Stack ax650 / llm8850 via persistant API listeners that present standard interfaces for the respective media generation types (or a subset of supported minimum calls / parameters)
- Goal 3: Be able to run multiple listeners at once, but avoid unloading models as much as possible so that there is little to no delay overhead to load a model when a request is received
- Goal 4: Monitor the ax650 / llm8850 status, and reset if it is in an unavailable state
- Goal 5: Use python as preferred language wherever possible, but not to a fault!

Non-goals
- What this project will not do (helps avoid scope creep)

Success metrics
- Metric 1: e.g., latency, uptime, or adoption target
- Metric 2: e.g., test coverage, error rate

Audience & stakeholders
- Primary users and teams responsible for maintenance
