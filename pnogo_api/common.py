import os

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("common", __name__)


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@bp.route("/")
def hello_world():
    return "Hello World!"
