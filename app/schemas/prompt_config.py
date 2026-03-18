from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PromptConfigRequest(BaseModel):
    """Payload for updating the global prompt."""

    prompt: str


class PromptConfigResponse(BaseModel):
    """Response containing the current global prompt and metadata."""

    prompt: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
