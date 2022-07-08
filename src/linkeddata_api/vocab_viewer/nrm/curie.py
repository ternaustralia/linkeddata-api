import requests

# TODO: Improve this, use a cache lib
# TODO: Serve cache if time limit reached but still make request
cache = {}
skips = [
    "https://linked.data.gov.au/def/nrm",
    "https://linked.data.gov.au/def/test/dawe-cv",
]


def uri_in_skips(uri: str) -> bool:
    for skip in skips:
        if uri.startswith(skip):
            return True
    return False


# TODO: use async?
def get(uri: str):
    if uri in cache:
        return cache.get(uri)
    if uri_in_skips(uri):
        return uri

    response = requests.post(
        "https://prefix.zazuko.com/api/v1/shrink", params={"q": uri}
    )

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        cache[uri] = uri
        return uri

    value = response.json()["value"]
    cache[uri] = value
    return value
