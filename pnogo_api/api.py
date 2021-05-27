from flask import (
    Blueprint, request, send_from_directory, current_app, abort
)
from werkzeug.utils import secure_filename
import os

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
                               mimetype='image/jpeg') if pongo else abort(404)


@bp.route('/randompnogo')
@require_app_key
def randompnogo():
    pongo = query_db(
        'SELECT id, description, points FROM ponghi WHERE id IN (SELECT id FROM ponghi ORDER BY RANDOM() LIMIT 1)')
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    } if pongo else abort(404)


@bp.route('/dailypnogo')
@require_app_key
def dailypnogo():
    pnid = query_db("SELECT id FROM ponghi WHERE daily_date=DATE('now') ORDER BY RANDOM() LIMIT 1")
    if pnid is None:
        pnid = query_db("SELECT id FROM ponghi WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
        if pnid is None:
            execute_db("UPDATE ponghi SET daily_date=null")
            pnid = query_db("SELECT id FROM ponghi WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
    if pnid is not None:
        execute_db("UPDATE ponghi SET daily_date=DATE('now') WHERE id = ?", pnid)
        pongo = query_db("SELECT id, description, points FROM ponghi WHERE id=?", pnid)
        return {
            "id": pongo[0],
            "description": pongo[1],
            "points": pongo[2],
        }
    else:
        abort(404)


@bp.route('/update')
@require_app_key
def update():
    res = sync_pnogo()
    return {
        "added": res[0],
        "removed": res[1],
    }

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/addpnogo', methods=['GET', 'POST'])
@require_app_key
def addpnogo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'picture' not in request.files:
            return 'morte: no file'
        file = request.files['picture']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return 'morte: no file name'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['PONGHI'], filename))
            return 'done!'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=picture>
      <input type=submit value=Upload>
    </form>
    '''
