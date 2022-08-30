from linkeddata_api import domain


def exists_uri(target_uri: str, uris: list[domain.schema.URI]) -> bool:
    for uri in uris:
        if uri.value == target_uri:
            return True
    return False
