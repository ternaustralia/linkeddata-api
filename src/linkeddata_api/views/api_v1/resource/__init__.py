import requests
from flask import request, Response
from werkzeug.exceptions import HTTPException
from flask_tern import openapi
from rdflib import URIRef

from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api import rdf

# TODO: Move this somewhere else.
GRAPHDB_URL = "https://graphdb.tern.org.au/repositories/"


@bp.get("/resource")
@openapi.validate(validate_request=False, validate_response=False)
def get_resource():
    repository_id = request.args.get("repository_id")
    uri = request.args.get("uri")
    format_ = request.headers.get("accept")
    include_incoming_relationships = request.args.get("include_incoming_relationships")
    include_incoming_relationships = (
        True if include_incoming_relationships == "true" else False
    )

    response = requests.get(
        GRAPHDB_URL + repository_id,
        headers={"accept": format_},
        params={"query": f"DESCRIBE <{uri}>"},
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(
            description=err.response.text,
            response=Response(err.response.text, status=502),
        ) from err

    graph = rdf.create_graph()
    graph.parse(data=response.text)
    print(len(graph))
    if len(graph) == 0:
        return "Resource not found", 404

    if not include_incoming_relationships:
        graph.remove((None, None, URIRef(uri)))

    result = graph.serialize(format=format_)
    return Response(result, mimetype=format_)
