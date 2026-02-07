import os

from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.getenv("DB_URI"),
        S3_URL=os.getenv("S3_URL"),
        S3_BUCKET=os.getenv("S3_BUCKET"),
        S3_ACCESS=os.getenv("S3_ACCESS"),
        S3_SECRET=os.getenv("S3_SECRET"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from pnogo_api.auth import require_app_key

    from . import auth

    app.register_blueprint(auth.bp)

    from . import common

    app.register_blueprint(common.bp)

    from . import api

    app.register_blueprint(api.bp)

    CORS(app)

    return app
