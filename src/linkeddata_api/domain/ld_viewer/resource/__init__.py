from rdflib import URIRef

from linkeddata_api import data, domain
from linkeddata_api.data.exceptions import (
    RequestError,
    SPARQLNotFoundError,
    SPARQLResultJSONError,
)
from . import json


def _handle_json_response(uri: str, sparql_endpoint: str) -> domain.schema.Resource:
    try:
        result = json.get(uri, sparql_endpoint)
    except (RequestError, SPARQLNotFoundError, SPARQLResultJSONError) as err:
        raise err

    return result.json()


def _handle_rdf_response(
    uri: str, sparql_endpoint: str, format_: str, include_incoming_relationships: bool
) -> str:
    try:
        response = data.sparql.post(
            f"DESCRIBE <{uri}>", sparql_endpoint, accept=format_
        )
    except RequestError as err:
        raise err

    graph = domain.rdf.create_graph()

    graph.parse(data=response.text, format=format_)

    if len(graph) == 0:
        return "Resource not found", 404

    if not include_incoming_relationships:
        graph.remove((None, None, URIRef(uri)))

    result = graph.serialize(format=format_)
    return result


def get(
    uri: str, sparql_endpoint: str, format_: str, include_incoming_relationships: bool
) -> str:
    """Get an RDF resource

    :param uri: URI of resource
    :param sparql_endpoint: SPARQL endpoint to query
    :param format_: Response format one of ["text/turtle", "application/n-triples", "application/ld+json", "application/json]
    :param include_incoming_relationships: Some RDF stores include statements of incoming relationships in DESCRIBE queries. If this is False, it will filter the incoming statements out of the response value
    :return: Response value
    :raises RequestError: An error occurred in the data layer
    """

    if format_ == "application/json":
        result = _handle_json_response(uri, sparql_endpoint)
    else:
        result = _handle_rdf_response(
            uri, sparql_endpoint, format_, include_incoming_relationships
        )
    return result
