import requests

from . import exceptions


def post(
    query: str, sparql_endpoint: str, accept: str = "application/sparql-results+json"
) -> requests.Response:
    """Make a SPARQL POST request

    If the response is JSON, use `response.json()` to get the Python dict.

    :param query: SPARQL query
    :param sparql_endpoint: SPARQL endpoint to query
    :param accept: The mimetype of the response value
    :return: Response object
    :raises exceptions.RequestError: An error occurred and the response status code is not in the 200 range.
    """
    headers = {
        "accept": accept,
        "content-type": "application/sparql-query",
    }

    response = requests.post(url=sparql_endpoint, headers=headers, data=query, timeout=60)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise exceptions.RequestError(err.response.text) from err

    # TODO: raise empty response error here.

    return response


def get(
    query: str, sparql_endpoint: str, accept: str = "application/sparql-results+json"
) -> requests.Response:
    """Make a SPARQL GET request

    If the response is JSON, use `response.json()` to get the Python dict.

    :param query: SPARQL query
    :param sparql_endpoint: SPARQL endpoint to query
    :param accept: The mimetype of the response value
    :return: Response object
    :raises exceptions.RequestError: An error occurred and the response status code is not in the 200 range.
    """
    headers = {
        "accept": accept,
    }
    params = {"query": query}

    response = requests.get(url=sparql_endpoint, headers=headers, params=params, timeout=60)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise exceptions.RequestError(err.response.text) from err

    # TODO: raise empty response error here.

    return response
