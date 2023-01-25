from pydantic import BaseModel


class ClassItem(BaseModel):
    id: str
    label: str
