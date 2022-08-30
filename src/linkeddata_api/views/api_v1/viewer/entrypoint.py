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


mapping = {"nrm": domain.viewer.entrypoints.nrm.get}


@bp.get("/viewer/entrypoint/<string:viewer_id>")
@openapi.validate(validate_request=False, validate_response=False)
def get_entrypoint(viewer_id: str):
    try:
        func = mapping.get(viewer_id)
        if func is None:
            raise ViewerIDNotFoundError(f"Key '{viewer_id}' not found")

        items = func()
    except ViewerIDNotFoundError as err:
        raise HTTPException(str(err), Response(str(err), 404)) from err
    except (RequestError, SPARQLResultJSONError) as err:
        raise HTTPException(err.description, Response(err.description, 502)) from err
    except Exception as err:
        raise HTTPException(str(err), Response(str(err), 500)) from err

    return jsonify(items, headers={"cache-control": "max-age=600, s-maxage=3600"})
