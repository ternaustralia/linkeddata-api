from flask.testing import FlaskClient


def test_classes_flat(client: FlaskClient):
    response = client.get(
        "/api/v1.0/classes/flat", query_string={"ontology_id": "tern-ontology"}
    )
    data = response.json
    assert len(data) >= 30
