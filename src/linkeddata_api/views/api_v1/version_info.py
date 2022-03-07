from flask import current_app
from flask_tern import openapi

from .blueprint import bp


@bp.route("/version")
@openapi.validate(validate_response=False)
def version_get():
    return current_app.config["VERSION"]
