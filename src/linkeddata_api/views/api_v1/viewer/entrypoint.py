from flask import Response
from werkzeug.exceptions import HTTPException
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
    }
}


@bp.get("/viewer/entrypoint/<string:viewer_id>")
@openapi.validate(validate_request=False, validate_response=False)
def get_entrypoint(viewer_id: str):
    try:
        obj = mapping.get(viewer_id)
        if obj is None:
            raise ViewerIDNotFoundError(f"Key '{viewer_id}' not found")

        sparql_endpoint = obj["sparql_endpoint"]
        items = obj["func"](sparql_endpoint)
    except ViewerIDNotFoundError as err:
        raise HTTPException(str(err), Response(str(err), 404)) from err
    except (RequestError, SPARQLResultJSONError) as err:
        raise HTTPException(err.description, Response(err.description, 502)) from err
    except Exception as err:
        raise HTTPException(str(err), Response(str(err), 500)) from err

    return jsonify(items, headers={"cache-control": "max-age=600, s-maxage=3600"})
