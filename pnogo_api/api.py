import os

from flask import (
    Blueprint, request, send_from_directory, current_app
)

from pnogo_api.auth import require_app_key
from pnogo_api.db import query_db

bp = Blueprint('api', __name__)


@bp.route('/getpnogo')
@require_app_key
def getpnogo():
    id = request.args.get('id')
    pongo = query_db('SELECT file FROM ponghi WHERE id = ?', [id])
    return send_from_directory(os.path.join(current_app.instance_path, 'pnoghi'), pongo[0],
                               mimetype='image/jpeg')


@bp.route('/dailypnogo')
@require_app_key
def dailypnogo():
    pongo = query_db(
        'SELECT id, description, points FROM ponghi WHERE id IN (SELECT id FROM ponghi ORDER BY RANDOM() LIMIT 1)')
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    }
