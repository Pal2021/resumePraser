from typing import Iterator, Protocol

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from config import Settings


class LLM(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str: ...

    def stream(self, system_prompt: str, user_prompt: str) -> Iterator[str]: ...


class AzureOpenAIClient:
    """Infrastructure adapter for Azure OpenAI."""

    def __init__(self, client: OpenAI, model: str):
        self._client = client
        self._model = model

    @classmethod
    def from_settings(cls, settings: Settings) -> "AzureOpenAIClient":
        if settings.api_key:
            client = OpenAI(
                base_url=settings.azure_openai_endpoint,
                api_key=settings.api_key,
            )
        else:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), settings.azure_token_scope
            )
            client = OpenAI(
                base_url=settings.azure_openai_endpoint,
                api_key=token_provider,
            )
        return cls(client, settings.azure_openai_model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def stream(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        for chunk in response:
            if not chunk.choices:
                continue
            token = chunk.choices[0].delta.content or ""
            if token:
                yield token
