import logging

from flask import request, Response, abort
from flask_tern import openapi

from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api import domain
from linkeddata_api.domain.viewer.resource import (
    RequestError,
    SPARQLNotFoundError,
    SPARQLResultJSONError,
)

logger = logging.getLogger(__name__)


@bp.get("/viewer/resource")
@openapi.validate(validate_request=False, validate_response=False)
def get_resource():
    sparql_endpoint = request.args.get("sparql_endpoint")
    uri = request.args.get("uri")
    format_ = request.args.get("format") or request.headers.get("accept")
    # TODO: Curently we don't support multiple format types in accept headers.
    if not format_ or "," in format_:
        format_ = "text/turtle"
    include_incoming_relationships = request.args.get("include_incoming_relationships")
    include_incoming_relationships = (
        True if include_incoming_relationships == "true" else False
    )

    if uri is None or sparql_endpoint is None:
        err_msg = (
            "Required query parameters 'uri' or 'sparql_endpoint' was not provided."
        )
        abort(404, err_msg)

    logger.info(
        """
GET /viewer/resource
    query parameters:
        uri: 
            %s
        sparql_endpoint:
            %s
        format:
            %s
        include_incoming_relationships:
            %s
        """,
        uri,
        sparql_endpoint,
        format_,
        include_incoming_relationships,
    )

    try:
        result = domain.viewer.resource.get(
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
