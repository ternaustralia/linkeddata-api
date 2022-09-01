import json

from flask import request, Response
from flask_tern import openapi
from flask_tern.logging import create_audit_event, log_audit

from linkeddata_api.domain.pydantic_jsonify import jsonify
from linkeddata_api.views.api_v1.blueprint import bp
from linkeddata_api import rdf


@bp.route("/rdf_tools/convert", methods=["POST"])
@openapi.validate(validate_request=False, validate_response=False)
def rdf_tools_convert():
    # TODO: add log audit.

    content_type = request.headers.get("content-type")
    accept = request.headers.get("accept")
    data = request.data.decode("utf-8")

    graph = rdf.create_graph()
    graph.parse(data=data, format=content_type)

    response_data = graph.serialize(format=accept)
    return Response(response_data, mimetype=accept)
