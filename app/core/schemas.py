from typing import Any, Dict, List, Optional


from pydantic import BaseModel, ConfigDict, Field



class ChatMessage(BaseModel):

    role: str

    content: str

class LLMRequest(BaseModel):

    messages: List[ChatMessage]


    max_new_tokens: int = 256

    temperature: float = 0.0

    top_p: float = 1.0


# Dynamic context (separate from system/user)

    context: str = ""


    metadata: Dict[str, Any] = Field(default_factory=dict)



class LLMResponse(BaseModel):

# Fixes: Field "model_name" conflict with protected namespace "model_"

    model_config = ConfigDict(protected_namespaces=())


    text: str

    model_name: str

    usage: Dict[str, Any] = Field(default_factory=dict)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    error: Optional[str] = None


class BotResponse(BaseModel):
    """Simplified response wrapper returned by the ResilienceBot.

    Only contains the final text produced by the bot; additional fields can
    be added later if more metadata is needed.
    """
    text: str

