from flask import abort, request
from flask_tern import openapi

from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api import domain
from linkeddata_api.domain.viewer.entrypoints.exceptions import (
    RequestError,
    SPARQLResultJSONError,
    ViewerIDNotFoundError,
)
from linkeddata_api.domain.pydantic_jsonify import jsonify


mapping = {
    "nrm": {
        "func": domain.viewer.entrypoints.nrm.get,
        "sparql_endpoint": "https://graphdb.tern.org.au/repositories/dawe_vocabs_core",
    },
    "tern": {
        "func": domain.viewer.entrypoints.tern.get,
        "sparql_endpoint": "https://graphdb.tern.org.au/repositories/tern_vocabs_core",
    },
}


@bp.get("/viewer/entrypoint/<string:viewer_id>")
@openapi.validate(validate_request=False, validate_response=False)
def get_entrypoint(viewer_id: str):
    page = int(request.args.get("page", 1))
    if page < 1:
        page = 1

    try:
        obj = mapping.get(viewer_id)
        if obj is None:
            raise ViewerIDNotFoundError(f"Key '{viewer_id}' not found")

        sparql_endpoint = obj["sparql_endpoint"]
        entrypoint_items = obj["func"](sparql_endpoint, page)
    except ViewerIDNotFoundError as err:
        abort(404, str(err))
    except (RequestError, SPARQLResultJSONError) as err:
        abort(502, err.description)
    except Exception as err:
        abort(500, err)

    return jsonify(
        entrypoint_items, headers={"cache-control": "max-age=600, s-maxage=3600"}
    )
