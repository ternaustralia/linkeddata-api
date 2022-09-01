from flask import request
from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit

from linkeddata_api.domain.pydantic_jsonify import jsonify
from linkeddata_api.views.api_v1.blueprint import bp
from . import crud


@bp.route("/ontology_viewer/classes/flat")
@openapi.validate(validate_response=False)
def classes_flat_get():
    # TODO: add log audit.

    ontology_id = request.args.get("ontology_id")
    classes = crud.get(ontology_id)

    return jsonify(classes)
