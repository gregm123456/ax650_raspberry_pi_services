import os


class Settings:
    # Service ports
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "127.0.0.1")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8080"))

    # Runtime (main_api_ax650) settings
    RUNTIME_HOST: str = os.getenv("RUNTIME_HOST", "127.0.0.1")
    RUNTIME_PORT: int = int(os.getenv("RUNTIME_PORT", "8000"))
    RUNTIME_BIN: str | None = os.getenv("RUNTIME_BIN", None)

    # Model / tokenizer paths
    MODEL_BASE_PATH: str = os.getenv("MODEL_BASE_PATH", "/opt/qwen3-4b")

    # Behavior flags
    MOCK_RUNTIME: bool = bool(int(os.getenv("QWEN3_MOCK_RUNTIME", "0")))

    # Operational limits
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "2048"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "128"))


settings = Settings()
