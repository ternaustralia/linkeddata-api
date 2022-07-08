from typing import Union

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    label: str
    description: str = None
    created: str = None
    modified: str = None


class URI(BaseModel):
    type: str = "uri"
    label: str
    value: str
    internal: bool


class Literal(BaseModel):
    type: str = "literal"
    value: str
    datatype: URI = ""
    language: str = ""


class PredicateObjects(BaseModel):
    predicate: URI
    objects: list[Union[URI, Literal]]


class Resource(BaseModel):
    uri: str
    label: str
    types: list[URI]
    properties: list[PredicateObjects]
