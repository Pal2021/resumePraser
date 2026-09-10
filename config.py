import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    azure_openai_endpoint: str
    azure_token_scope: str
    azure_openai_model: str
    server_name: str
    port: int
    api_key: str | None = None
    share: bool = False

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://newaiprashant.services.ai.azure.com/openai/v1").rstrip("/"),
            azure_token_scope=os.getenv("AZURE_TOKEN_SCOPE", "https://ai.azure.com/.default"),
            azure_openai_model=os.getenv("AZURE_OPENAI_MODEL", "gpt-5"),
            server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
            port=int(os.getenv("PORT", "7860")),
            api_key=os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            share=os.getenv("GRADIO_SHARE", "false").lower() in ("true", "1", "yes"),
        )
