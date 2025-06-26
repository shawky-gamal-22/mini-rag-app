from enum import Enum

class LLMEnum(Enum):

    """Enum for LLM providers."""

    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnum(Enum):
    """Enum for OpenAI models."""

    SYSTEM= "system"
    USER = "user"
    ASSISTANT = "assistant"

