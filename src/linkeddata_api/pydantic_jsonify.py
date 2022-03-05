import json
from typing import Union, List

from flask import Response
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


def jsonify(
    data: Union[List[BaseModel], BaseModel],
    status: int = 200,
    mimetype: str = "application/json",
) -> Response:
    """Return a Flask Response that uses pydantic_encoder to perform the Python object to JSON string."""

    return Response(
        json.dumps(data, indent=2, default=pydantic_encoder),
        status=status,
        mimetype=mimetype,
    )
