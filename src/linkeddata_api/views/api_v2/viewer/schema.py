from typing import Union

from pydantic import BaseModel


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


class Resource(BaseModel):
    uri: str
    label: str
    profile: Union[str, None] = None
    types: list[URI]
    properties: list[URI]
    properties_require_profile: list[str]


class PredicateValues(BaseModel):
    uri: str
    predicate: str
    count: int
    objects: list[Union[URI, Literal]]
