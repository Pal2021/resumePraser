import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    azure_endpoint: str
    model: str
    token_scope: str
    temperature: float
    max_tokens: int
    server_name: str
    port: int
    share: bool

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/") + "/",
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-5"),
            token_scope=os.getenv("AZURE_TOKEN_SCOPE", "https://ai.azure.com/.default"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "16000")),
            server_name=os.getenv("SERVER_NAME", "127.0.0.1"),
            port=int(os.getenv("PORT", "7860")),
            share=os.getenv("GRADIO_SHARE", "false").lower() == "true",
        )