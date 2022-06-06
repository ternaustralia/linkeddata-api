import pytest

from flask.testing import FlaskClient


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


# TODO: Test external request errors are raised and forwarded to client. Use pytest-mock here.
