from linkeddata_api.vocab_viewer import nrm


def exists_uri(target_uri: str, uris: list[nrm.schema.URI]) -> bool:
    for uri in uris:
        if uri.value == target_uri:
            return True
    return False
