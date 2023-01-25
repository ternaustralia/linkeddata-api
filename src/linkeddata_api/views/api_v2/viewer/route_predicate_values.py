from flask import Response, abort, request
from flask_tern import openapi

from linkeddata_api.domain.viewer.resource import (
    RequestError,
    SPARQLNotFoundError,
    SPARQLResultJSONError,
)
from linkeddata_api.views.api_v2.blueprint import bp

from .json_renderer import get_predicate_values


@bp.get("/viewer/predicate-values")
@openapi.validate(validate_request=False, validate_response=False)
def get_resource_predicate_values():

    uri = request.args.get("uri")
    predicate = request.args.get("predicate")
    sparql_endpoint = request.args.get("sparql_endpoint")
    profile = request.args.get("profile", "")
    page = int(request.args.get("page", 1))
    if page < 1:
        page = 1
    page_size = int(request.args.get("page_size", 20))
    if page < 1:
        page = 20

    if not uri or not predicate or not sparql_endpoint:
        err_msg = "Required query parameters 'uri' or 'predicate' or 'sparql_endpoint' was not provided."
        abort(400, err_msg)

    try:
        result = get_predicate_values(
            uri, predicate, sparql_endpoint, profile, limit=page_size, page=page
        )
    except SPARQLNotFoundError as err:
        abort(404, err.description)
    except (RequestError, SPARQLResultJSONError) as err:
        abort(502, err.description)
    except Exception as err:
        abort(500, err)

    return Response(
        result,
        mimetype="application/json",
        headers={"cache-control": "max-age=600, s-maxage=3600"},
    )
