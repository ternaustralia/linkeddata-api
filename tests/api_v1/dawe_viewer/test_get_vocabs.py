import pytest
from pytest_mock import MockerFixture

from flask.testing import FlaskClient

from requests import Response


@pytest.fixture
def url() -> str:
    return "/api/v1.0/vocab_viewer/dawe_nrm/vocabs"


def test_get_vocabs(client: FlaskClient, url: str):
    response = client.get(url)
    data = response.json
    assert len(data) >= 5


def test_get_vocabs_request_error(client: FlaskClient, url: str, mocker: MockerFixture):
    mocked_response = Response()
    mocked_response.status_code = 400

    mocker.patch("requests.post", return_value=mocked_response)

    response = client.get(url)
    assert response.status_code == 502


def test_get_vocabs_bad_sparql_response(
    client: FlaskClient, url: str, mocker: MockerFixture, logger
):
    mocked_response = Response()
    mocked_response.status_code = 200
    mocked_response._content = b"{}"

    mocker.patch("requests.post", return_value=mocked_response)

    response = client.get(url)

    assert response.status_code == 502
    assert "Unexpected SPARQL result set." in response.text
