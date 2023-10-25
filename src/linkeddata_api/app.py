import logging

from flask import Flask, redirect, url_for
from flask_tern import init_app
from flask_tern.utils.config import load_settings
from flask_tern.utils.json import TernJSONProvider

from linkeddata_api.version import version


def create_app(config=None) -> Flask:
    ###################################################
    # Setup Flask App
    ###################################################
    app = Flask("linkeddata_api")
    app.config["VERSION"] = version

    if app.config["ENV"] == "development":
        logging.basicConfig(level=logging.INFO)

    ###################################################
    # custom json encoder
    ###################################################
    app.json = TernJSONProvider(app)

    ################################################################
    # Configure application
    ################################################################
    # load defaults
    from linkeddata_api import settings

    load_settings(app, env_prefix="LINKEDDATA_API_", defaults=settings, config=config)

    ################################################################
    # Configure flask_tern extensions
    ################################################################
    init_app(app)

    ##############################################
    # Register routes and views
    ##############################################
    # register oidc session login blueprints
    from flask_tern.auth.login import oidc_login

    app.register_blueprint(oidc_login, url_prefix="/api/oidc")

    # register api blueprints
    from linkeddata_api.views import api_v1, api_v2, home

    app.register_blueprint(home.bp, url_prefix="/api")
    app.register_blueprint(api_v1.bp, url_prefix="/api/v1.0")
    app.register_blueprint(api_v2.bp, url_prefix="/api/v2.0")

    # setup build_only route so that we can use url_for("root", _external=True) - "root" route required by oidc session login
    # app.add_url_rule("/", "root", build_only=True)
    app.add_url_rule("/", "root", view_func=lambda: redirect(url_for("home.home", _external=True)))
    return app
