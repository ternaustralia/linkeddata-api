from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit

from .blueprint import bp
from linkeddata_api.crud.api_v1 import ont_viewer
from linkeddata_api.pydantic_jsonify import jsonify


@bp.route("/classes/flat")
@openapi.validate(validate_response=False)
def classes_flat_get():
    # TODO: add log audit.

    ontology_id = "tern-ontology"
    classes = ont_viewer.classes.flat.get(ontology_id)

    return jsonify(classes)
