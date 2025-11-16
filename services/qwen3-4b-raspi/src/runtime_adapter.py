"""Runtime adapter that launches (optional) runtime binary and communicates via HTTP.

This adapter expects a runtime providing `/api/reset` and `/api/chat` as described in the spec.
For development the adapter supports a mock runtime when `MOCK_RUNTIME` is enabled in config.
"""
from __future__ import annotations
import subprocess
import time
import requests
import threading
from urllib.parse import urljoin
from typing import Any, Dict, List

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
        return requests.post(url, json=payload, timeout=timeout)

    def reset_then_chat(self, system_prompt: str, messages: List[Dict[str, str]], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Reset runtime KV and then perform a chat call.

        Returns JSON response from runtime's /api/chat.
        """
        with self._lock:
            if settings.MOCK_RUNTIME:
                # produce a mocked assistant text
                return {
                    "id": "mock-1",
                    "text": "This is a mock response.",
                    "usage": {"prompt_tokens": sum(len(m["content"].split()) for m in messages), "completion_tokens": 5}
                }

            # Reset
            try:
                self._post("/api/reset", {"system_prompt": system_prompt}).raise_for_status()
            except Exception as exc:
                raise RuntimeError(f"Failed to reset runtime: {exc}") from exc

            # Build chat payload; adapt to runtime's expected schema
            payload: Dict[str, Any] = {"messages": messages}
            if params:
                payload.update(params)

            try:
                resp = self._post("/api/chat", payload)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                raise RuntimeError(f"Chat call failed: {exc}") from exc

    def health(self) -> bool:
        if settings.MOCK_RUNTIME:
            return True
        try:
            r = requests.get(urljoin(self.base_url, "/api/health"), timeout=1.0)
            return r.status_code == 200
        except Exception:
            return False


runtime_adapter = RuntimeAdapter()
