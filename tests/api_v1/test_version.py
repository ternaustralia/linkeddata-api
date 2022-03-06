from flask.testing import FlaskClient

from linkeddata_api.version import version


def test_version(client: FlaskClient):
    response = client.get("/api/v1.0/version")
    assert response.data.decode("utf-8") == version
