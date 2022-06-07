import pytest
from pytest_mock import MockerFixture

from flask.testing import FlaskClient

import requests


@pytest.fixture
def url() -> str:
    return "/api/v1.0/ontology_viewer/classes/flat"


def test_classes_flat(client: FlaskClient, url: str):
    response = client.get(url, query_string={"ontology_id": "tern-ontology"})
    data = response.json
    assert len(data) >= 30


def test_classes_flat_invalid_id(client: FlaskClient, url: str):
    response = client.get(url, query_string={"ontology_id": "bad-id"})
    assert response.status_code == 404


def test_classes_flat_request_error(
    client: FlaskClient, url: str, mocker: MockerFixture
):
    mocked_response = requests.Response()
    mocked_response.status_code = 400

    mocker.patch("requests.post", return_value=mocked_response)

    response = client.get(url, query_string={"ontology_id": "tern-ontology"})
    assert response.status_code == 502
