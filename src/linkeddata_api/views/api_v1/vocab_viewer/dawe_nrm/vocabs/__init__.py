from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from linkeddata_api.pydantic_jsonify import jsonify
from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api.vocab_viewer import nrm


@bp.route("/vocab_viewer/nrm/vocabs")
@openapi.validate(validate_response=False)
def get_dawe_nrm_vocabs():
    # TODO: add log audit.

    try:
        items = nrm.vocabs.get()
    except (nrm.exceptions.RequestError, nrm.exceptions.SPARQLResultJSONError) as err:
        raise HTTPException(err.description, Response(err.description, 502)) from err

    return jsonify(items, headers={"cache-control": "max-age=600, s-maxage=3600"})
