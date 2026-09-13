from typing import Protocol

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from config import Settings


class LLM(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class AzureOpenAIClient:
    def __init__(
        self,
        client: OpenAI,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    @classmethod
    def from_settings(cls, settings: Settings) -> "AzureOpenAIClient":
        if not settings.azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not set.")

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            settings.token_scope,
        )

        client = OpenAI(
            base_url=settings.azure_endpoint,
            api_key=token_provider,  # type: ignore[arg-type]
        )

        return cls(
            client=client,
            model=settings.model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

    def complete(self, system: str, user: str) -> str:
        reasoning_family = self._model.lower().startswith(
            ("gpt-5", "o1", "o3", "o4")
        )

        kwargs: dict = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        if reasoning_family:
            kwargs["max_completion_tokens"] = self._max_tokens
        else:
            kwargs["max_tokens"] = self._max_tokens
            kwargs["temperature"] = self._temperature

        resp = self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""