from typing import Union

from linkeddata_api import domain


def sort_property_objects(item: list[Union[domain.schema.URI, domain.schema.Literal]]):
    if item.list_item:
        return item.list_item_number
    else:
        if item.type == "uri":
            return item.label
        else:
            return item.value
