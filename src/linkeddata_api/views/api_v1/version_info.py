from flask_tern import openapi

from .blueprint import bp
from linkeddata_api.version import version


@bp.route("/version")
@openapi.validate(validate_response=False)
def version_get():
    return version
