from flask import (
    Blueprint, request, send_from_directory, current_app, abort
)

from pnogo_api.auth import require_app_key
from pnogo_api.db import query_db, execute_db
from pnogo_api.utils import sync_pnogo

bp = Blueprint('api', __name__)


@bp.route('/getpnogo')
@require_app_key
def getpnogo():
    pnid = request.args.get('id')
    pongo = query_db('SELECT file FROM ponghi WHERE id = ?', [pnid])
    return send_from_directory(current_app.config['PONGHI'], pongo[0],
                               mimetype='image/jpeg') if pongo is not None else abort(404)


@bp.route('/randompnogo')
@require_app_key
def randompnogo():
    pongo = query_db(
        'SELECT id, description, points FROM ponghi WHERE id IN (SELECT id FROM ponghi ORDER BY RANDOM() LIMIT 1)')
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    }


@bp.route('/dailypnogo')
@require_app_key
def dailypnogo():
    pnid = query_db("SELECT id FROM ponghi WHERE daily_date=DATE('now') ORDER BY RANDOM() LIMIT 1")
    if pnid is None:
        pnid = query_db("SELECT id FROM ponghi WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
        if pnid is None:
            execute_db("UPDATE ponghi SET daily_date=null")
            pnid = query_db("SELECT id FROM ponghi WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
        execute_db("UPDATE ponghi SET daily_date=DATE('now') WHERE id = ?", pnid)
    pongo = query_db("SELECT id, description, points FROM ponghi WHERE id=?", pnid)
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    }


@bp.route('/update')
@require_app_key
def update():
    res = sync_pnogo()
    return {
        "added": res[0],
        "removed": res[1],
    }
