import requests

from linkeddata_api.vocab_viewer import nrm


def post(query: str, sparql_endpoint: str) -> dict:
    headers = {
        "accept": "application/sparql-results+json",
        "content-type": "application/sparql-query",
    }

    response = requests.post(url=sparql_endpoint, headers=headers, data=query)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        raise nrm.exceptions.RequestError(err.response.text) from err

    return response.json()
