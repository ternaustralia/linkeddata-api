from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
