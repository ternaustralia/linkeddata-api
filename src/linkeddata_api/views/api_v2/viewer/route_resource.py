from flask import Response, abort, request
from flask_tern import openapi
from pydantic import BaseModel

from linkeddata_api import domain
from linkeddata_api.domain.viewer.resource import (
    RequestError,
    SPARQLNotFoundError,
    SPARQLResultJSONError,
)
from linkeddata_api.views.api_v2.blueprint import bp

from .json_renderer import json_renderer


@bp.get("/viewer/resource")
@openapi.validate(validate_request=False, validate_response=False)
def get_resource():
    sparql_endpoint = request.args.get("sparql_endpoint")
    uri = request.args.get("uri")

    # TODO: Curently we don't support multiple format types in accept headers.
    format_ = request.args.get("format") or request.headers.get("accept")
    if not format_ or "," in format_:
        format_ = "text/turtle"

    # TODO: We don't support incoming relationshpis for resources yet in the JSON renderer.
    include_incoming_relationships = request.args.get("include_incoming_relationships")
    include_incoming_relationships = (
        True if include_incoming_relationships == "true" else False
    )

    if not uri or not sparql_endpoint:
        err_msg = (
            "Required query parameters 'uri' or 'sparql_endpoint' was not provided."
        )
        abort(400, err_msg)

    try:
        if format_ == "application/json":
            result = json_renderer(uri, sparql_endpoint)
        else:
            result = domain.viewer.resource.handle_rdf_response(
                uri, sparql_endpoint, format_, include_incoming_relationships
            )
    except SPARQLNotFoundError as err:
        abort(404, err.description)
    except (RequestError, SPARQLResultJSONError) as err:
        abort(502, err.description)
    except Exception as err:
        abort(500, err)

    return Response(
        result,
        mimetype=format_,
        headers={"cache-control": "max-age=600, s-maxage=3600"},
    )
