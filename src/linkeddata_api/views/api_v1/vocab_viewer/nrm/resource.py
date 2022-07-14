from flask import request
from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from linkeddata_api.pydantic_jsonify import jsonify
from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api.vocab_viewer import nrm


@bp.get("/vocab_viewer/nrm/resource")
@openapi.validate(validate_response=False)
def get_nrm_resource():
    uri = request.args.get("uri")
    sparql_endpoint = request.args.get("sparql_endpoint")

    try:
        result = nrm.resource.get(uri, sparql_endpoint)
    except nrm.exceptions.SPARQLNotFoundError as err:
        raise HTTPException(err.description, Response(err.description, 404)) from err
    except (nrm.exceptions.RequestError, nrm.exceptions.SPARQLResultJSONError) as err:
        raise HTTPException(err.description, Response(err.description, 502)) from err
    except Exception as err:
        raise HTTPException(str(err), Response(str(err), 500)) from err

    return jsonify(result, headers={"cache-control": "max-age=600, s-maxage=3600"})
