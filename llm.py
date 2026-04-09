import os
from dataclasses import dataclass
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


@dataclass
class ChatResponse:
    text: str
    input_tokens: int
    output_tokens: int


def chat(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> ChatResponse:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    kwargs: dict = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return ChatResponse(
        text=response.content[0].text,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
