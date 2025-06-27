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

class CoHereEnums(Enum):
    """Enum for OpenAI models."""

    SYSTEM= "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = 'search_document'
    QUERY = 'search_query'


class DocumentTypeEnum(Enum):
    DOCUMENT = 'document'
    QUERY = 'query'

