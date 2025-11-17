"""Runtime adapter that launches (optional) runtime binary and communicates via HTTP.

This adapter expects a runtime providing `/api/reset` and `/api/chat` as described in the spec.
For development the adapter supports a mock runtime when `MOCK_RUNTIME` is enabled in config.
"""
from __future__ import annotations
import subprocess
import threading
import time
from typing import Any, Dict, List

import requests
from urllib.parse import urljoin

import config as _config
settings = _config.settings


class RuntimeAdapter:
    def __init__(self):
        self.base_url = f"http://{settings.RUNTIME_HOST}:{settings.RUNTIME_PORT}"
        self.process: subprocess.Popen | None = None
        self._lock = threading.Lock()

        if settings.MOCK_RUNTIME:
            # nothing to start
            return

        # Optionally start the runtime binary if provided
        if settings.RUNTIME_BIN:
            self.start_runtime_bin(settings.RUNTIME_BIN)

    def start_runtime_bin(self, path: str) -> None:
        if self.process:
            return
        # launch the runtime binary; don't capture stdout/stderr permanently
        self.process = subprocess.Popen([path, "--port", str(settings.RUNTIME_PORT)])
        # allow it to initialize
        time.sleep(0.2)

    def stop_runtime(self) -> None:
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
            self.process = None

    def _post(self, path: str, payload: Dict[str, Any], timeout: float = 30.0) -> requests.Response:
        url = urljoin(self.base_url, path)
        # Use a session object to potentially improve performance and handle retries if needed.
        with requests.Session() as session:
            return session.post(url, json=payload, timeout=timeout)

    def reset_then_chat(self, system_prompt: str, messages: List[Dict[str, str]], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Reset runtime KV and then perform a chat call.

        This function includes a retry mechanism to handle the race condition where the 
        runtime is still busy after a reset.
        """
        with self._lock:
            if settings.MOCK_RUNTIME:
                # produce a mocked assistant text
                return {
                    "id": "mock-1",
                    "text": "This is a mock response.",
                    "usage": {"prompt_tokens": sum(len(m["content"].split()) for m in messages), "completion_tokens": 5}
                }

            # 1. Reset the runtime
            try:
                self._post("/api/reset", {"system_prompt": system_prompt}).raise_for_status()
            except Exception as exc:
                raise RuntimeError(f"Failed to reset runtime: {exc}") from exc

            # 2. Attempt to chat with a retry loop
            # CRITICAL FIX: The C++ runtime (main_api_axcl_aarch64) reverses the message array internally.
            # We must reverse it here so it gets reversed back to the correct order.
            # Evidence: Testing with reversed vs. non-reversed conversations showed the runtime
            # consistently responds based on the FIRST message sent, not the LAST (most recent).
            # See: https://github.com/gregm123456/ax650_raspberry_pi_services/issues/XXX
            reversed_messages = list(reversed(messages))
            print(f"DEBUG: Sending {len(reversed_messages)} messages to runtime")
            for i, msg in enumerate(reversed_messages):
                print(f"  Message {i}: {msg['role']}: {msg['content'][:50]}...")
            payload: Dict[str, Any] = {"messages": reversed_messages}
            
            max_retries = 20  # Max attempts, increased for safety
            retry_delay = 0.2  # Seconds to wait between retries (200ms)

            for attempt in range(max_retries):
                try:
                    # Use a longer timeout for the actual chat call
                    resp = self._post("/api/chat", payload, timeout=90.0)
                    
                    # Check response body BEFORE calling raise_for_status()
                    # This allows us to handle the "llm is running" error gracefully
                    response_data = resp.json()
                    
                    # Specifically check for the "llm is running" error in the response body
                    if response_data.get("error") == "llm is running":
                        if attempt < max_retries - 1:
                            print(f"LLM is busy, retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            continue
                        else:
                            # All retries failed
                            raise RuntimeError("Chat call failed: LLM was still busy after multiple retries.")
                    
                    # Now check for HTTP errors (non-2xx status codes)
                    resp.raise_for_status()
                    
                    # If no error, return the successful response
                    return response_data

                except requests.exceptions.HTTPError as http_err:
                    # Handle non-2xx responses that are not the "llm is running" error
                    raise RuntimeError(f"Chat call failed with HTTP error: {http_err}. Response: {http_err.response.text}") from http_err
                except requests.exceptions.RequestException as req_err:
                    # Handle network-level errors (timeout, connection error, etc.)
                    if attempt < max_retries - 1:
                        print(f"Network error during chat call, retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise RuntimeError(f"Chat call failed after multiple retries due to network error: {req_err}") from req_err
                except Exception as exc:
                    # Handle other unexpected errors (e.g., JSON decoding)
                    raise RuntimeError(f"An unexpected error occurred during chat call: {exc}") from exc
            
            # This line should theoretically be unreachable
            raise RuntimeError("Chat call failed: Exceeded max retries.")

    def health(self) -> bool:
        if settings.MOCK_RUNTIME:
            return True
        try:
            r = requests.get(urljoin(self.base_url, "/api/health"), timeout=1.0)
            return r.status_code == 200
        except Exception:
            return False


runtime_adapter = RuntimeAdapter()
