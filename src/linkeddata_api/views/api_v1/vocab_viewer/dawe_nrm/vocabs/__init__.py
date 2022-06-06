from flask import request
from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit

from linkeddata_api.pydantic_jsonify import jsonify
from linkeddata_api.views.api_v1.blueprint import bp
from . import crud


@bp.route("/vocab_viewer/dawe_nrm/vocabs")
@openapi.validate(validate_response=False)
def get_dawe_nrm_vocabs():
    # TODO: add log audit.

    items = crud.get()

    return jsonify(items)
