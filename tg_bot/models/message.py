from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    user_id: int
    text: str
    created_at: str = datetime.now(timezone.utc).isoformat()

    model_config = ConfigDict(use_enum_values=True)
