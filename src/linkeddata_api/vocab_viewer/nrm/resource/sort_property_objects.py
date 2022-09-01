from typing import Union

from linkeddata_api.vocab_viewer import nrm


def sort_property_objects(item: list[Union[nrm.schema.URI, nrm.schema.Literal]]):
    if item.list_item:
        return item.list_item_number
    else:
        if item.type == "uri":
            return item.label
        else:
            return item.value
