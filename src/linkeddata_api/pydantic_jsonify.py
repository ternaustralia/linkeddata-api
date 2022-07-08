import json
from typing import Union, List

from flask import Response
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


def jsonify(
    data: Union[List[BaseModel], BaseModel],
    status: int = 200,
    mimetype: str = "application/json",
    headers: dict = None,
) -> Response:
    """Return a Flask Response that uses pydantic_encoder with json.dumps()."""

    return Response(
        json.dumps(data, indent=2, default=pydantic_encoder),
        status=status,
        mimetype=mimetype,
        headers=headers,
    )
