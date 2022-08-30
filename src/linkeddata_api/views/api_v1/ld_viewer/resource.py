from flask import request, Response
from werkzeug.exceptions import HTTPException
from flask_tern import openapi

from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api import domain
from linkeddata_api.domain.viewer.resource import (
    RequestError,
    SPARQLNotFoundError,
    SPARQLResultJSONError,
)


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

    try:
        result = domain.viewer.resource.get(
            uri, sparql_endpoint, format_, include_incoming_relationships
        )
    except SPARQLNotFoundError as err:
        raise HTTPException(err.description, Response(err.description, 404)) from err
    except (RequestError, SPARQLResultJSONError) as err:
        raise HTTPException(
            description=err.description,
            response=Response(err.description, status=502),
        ) from err
    except Exception as err:
        raise HTTPException(
            description=str(err),
            response=Response(str(err), mimetype="text/plain", status=500),
        ) from err

    return Response(result, mimetype=format_)
