from typing import Union

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    label: str
    description: str = None
    created: str = None
    modified: str = None


class RDFListItemMixin(BaseModel):
    """An item in an RDF List"""

    list_item: bool = False
    list_item_number: int | None = None


class URI(RDFListItemMixin):
    type: str = "uri"
    label: str
    value: str
    internal: bool

    def __hash__(self):
        return hash(self.value)


class Literal(RDFListItemMixin):
    type: str = "literal"
    value: str
    datatype: URI = None
    language: str = ""

    def __hash__(self):
        datatype = self.datatype.value if self.datatype else ""
        return hash(self.value + datatype + self.language)


class SubjectPredicates(BaseModel):
    predicate: URI
    subjects: list[URI]


class PredicateObjects(BaseModel):
    predicate: URI
    objects: list[Union[URI, Literal]]


class Resource(BaseModel):
    uri: str
    profile: str = ""
    label: str
    types: list[URI]
    properties: list[PredicateObjects]
    incoming_properties: list[SubjectPredicates]
