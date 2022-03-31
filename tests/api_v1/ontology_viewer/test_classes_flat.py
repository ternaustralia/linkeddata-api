from flask.testing import FlaskClient


def test_classes_flat(client: FlaskClient):
    response = client.get(
        "/api/v1.0/ontology_viewer/classes/flat", query_string={"ontology_id": "tern-ontology"}
    )
    data = response.json
    assert len(data) >= 30


# TODO: Test invalid ontology_id value returns correct response.
# TODO: Test external request errors are raised and forwarded to client. Use pytest-mock here.
