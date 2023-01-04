import logging

import requests

logger = logging.getLogger(__name__)

# URIs that don't have curies in external service.
not_found = {}

# Predefined prefixes. New prefixes get added at runtime.
prefixes = {
    "http://purl.org/dc/terms/": "dcterms",
    "http://www.w3.org/2004/02/skos/core#": "skos",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
    "https://schema.org/": "schema",
    "https://w3id.org/tern/ontologies/tern/": "tern",
    "http://www.w3.org/2002/07/owl#": "owl",
    "http://www.w3.org/2001/XMLSchema#": "xsd",
    "http://rdfs.org/ns/void#": "void",
    "http://www.w3.org/ns/prov#": "prov",
}

# Don't find curies for these - speeds up request processing.
# TODO: these may no longer be needed since we don't fetch for subjects or objects of an RDF statement anymore.
skips = [
    "https://linked.data.gov.au/def/nrm",
    "https://linked.data.gov.au/def/test/dawe-cv",
    "http://linked.data.gov.au/dataset",
    "https://linked.data.gov.au/dataset",
]


def uri_in_skips(uri: str) -> bool:
    for skip in skips:
        if uri.startswith(skip):
            return True
    return False


def get(uri: str):
    """Get curie

    1. Check if it exists in prefixes.
    2. Check if it exists in cache.
    3. Make an expensive request to an external service. Cache the result.

    If all steps fail to find a curie, return the uri as-is.
    """

    for key, val in prefixes.items():
        if uri.startswith(key):
            localname = uri.split("#")[-1].split("/")[-1]
            curie = f"{val}:{localname}"
            return curie

    if uri in not_found:
        return not_found.get(uri)
    if uri_in_skips(uri):
        return uri

    logger.info("Fetching curie from external service - %s", uri)
    localname = uri.split("#")[-1].split("/")[-1]
    r_index = uri.rfind(localname)
    base_uri = uri[:r_index]

    response = requests.post(
        "https://prefix.zazuko.com/api/v1/shrink", params={"q": base_uri}, timeout=60
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        not_found[uri] = uri
        return uri

    prefix = response.json()["value"][:-1]
    prefixes[base_uri] = prefix
    curie = f"{prefix}:{localname}"
    logger.info("Curie fetch completed for %s, found %s", uri, curie)

    return curie
