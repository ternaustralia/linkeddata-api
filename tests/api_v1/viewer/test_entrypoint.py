import pytest
import requests
from pytest_mock import MockerFixture
from flask.testing import FlaskClient
from werkzeug.test import TestResponse


@pytest.fixture
def url() -> str:
    return "/api/v1.0/viewer/entrypoint"


@pytest.mark.parametrize(
    "status_code, viewer_id, content_type, content",
    [
        (404, "not-exist", "application/json", "Key 'not-exist' not found"),
        (200, "nrm", "application/json", None),
    ],
)
def test(
    client: FlaskClient,
    url: str,
    mocker: MockerFixture,
    status_code: int,
    viewer_id: str,
    content_type: str,
    content: str,
):
    mocked_response = requests.Response()
    mocked_response.status_code = status_code
    if status_code != 200:
        mocked_response._content = content.encode("utf-8")

    mocker.patch("requests.get", return_value=mocked_response)

    response: TestResponse = client.get(url + f"/{viewer_id}")
    assert response.status_code == status_code, response.text
    assert content_type in response.headers.get("content-type")
