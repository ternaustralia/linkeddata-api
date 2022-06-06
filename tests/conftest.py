import base64
import logging

# from flask_tern.testing.fixtures import monkeypatch_session, cache_spec, basic_auth
import pytest
from flask import Flask

from linkeddata_api import create_app

# from linkeddata_api.models import db

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def app():
    _app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "OIDC_DISCOVERY_URL": "https://auth.example.com/.well-known/openid-configuration",
            "OIDC_CLIENT_ID": "oidc-test",
        }
    )
    # setup db
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    #     # here we would set up initial data for all tests if needed

    yield _app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def logger():
    return logging.getLogger(__name__)
