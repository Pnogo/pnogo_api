from flask import (
    Blueprint, request, send_file, send_from_directory, current_app, abort
)
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import os
import json
import random
from markupsafe import escape

from pnogo_api.auth import require_app_key
from pnogo_api.db import query_db, execute_db
from pnogo_api.utils import sync_pnogo

bp = Blueprint('api', __name__)


@bp.route('/getall')
@require_app_key
def getall_all():
    pnogos = query_db('SELECT p.id, p.file, p.description, p.points, p.sent, p.daily_date, c.name FROM pictures p JOIN cndr c ON p.cndr_id=c.id', multi=True)
    keys = ['id', 'file', 'description', 'points', 'sent', 'daily_date', 'name']
    out = [dict(zip(keys, pong)) for pong in pnogos] if pnogos else []
    return json.dumps(out)


@bp.route('/getall/<cndr>')
@require_app_key
def getall(cndr):
    pnogos = query_db('SELECT p.id, p.file, p.description, p.points, p.sent, p.daily_date FROM pictures p JOIN cndr c ON p.cndr_id=c.id WHERE c.name LIKE ?', [escape(cndr)], multi=True)
    keys = ['id', 'file', 'description', 'points', 'sent', 'daily_date']
    out = [dict(zip(keys, pong)) for pong in pnogos] if pnogos else []
    return json.dumps(out)


@bp.route('/getallpnoghi')
@require_app_key
def getallpnoghi():
    return getall('pongo')


@bp.route('/desc')
@bp.route('/descpnogo')
@require_app_key
def descpnogo():
    id = request.args.get('id')
    desc = request.args.get('description')
    execute_db(f"UPDATE pictures SET description = '{desc}' WHERE id = {id}")
    return f"done! set desc of {id} to: {desc}"


@bp.route('/info')
@bp.route('/infopnogo')
@require_app_key
def infopnogo():
    pnid = request.args.get('id')
    pongo = query_db('SELECT file, description, points, sent, daily_date FROM pictures WHERE id = ?', [pnid])
    return {
        "file": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
        "sent": pongo[3],
        "daily_date": pongo[4],
    } if pongo else abort(404)


@bp.route('/count')
@require_app_key
def count_all():
    res = query_db('SELECT count(*) FROM pictures')
    return {"count": res[0]} if res else abort(404)


@bp.route('/count/<cndr>')
@require_app_key
def count(cndr):
    res = query_db('SELECT count(*) FROM pictures JOIN cndr c ON cndr_id=c.id WHERE c.name LIKE ?', [escape(cndr)])
    return {"count": res[0]} if res else abort(404)


@bp.route('/countpnogo')
@require_app_key
def countpnogo():
    return count('pongo')


@bp.route('/kill')
@bp.route('/killpnogo')
@require_app_key
def killpnogo():
    pnid = request.args.get('id')
    morte = query_db('SELECT file FROM pictures WHERE id = ?', (pnid,))
    if morte:
        execute_db('DELETE FROM pictures WHERE id = ?', (pnid,))
        os.remove(os.path.join(current_app.config['PONGHI'], morte[0]))
        return 'success!<br>il pongo numero ' + pnid + ' è stato abbattuto, pace all\'anima sua'
    else:
        return abort(404)


@bp.route('/get')
@bp.route('/getpnogo')
@require_app_key
def getpnogo():
    pnid = request.args.get('id')
    width = request.args.get('width')
    height = request.args.get('height')
    maxsize = request.args.get('maxsize') or 1280
    pongo = query_db('SELECT file FROM pictures WHERE id = ?', (pnid,))

    if pongo:
        img = Image.open(os.path.join(current_app.config['PONGHI'], pongo[0])).convert('RGB')
        overscale = True

        if width is None and height is None:
            overscale = False
            if img.size[0] > img.size[1]:
                width = int(maxsize)
            else:
                height = int(maxsize)

        if height is None:
            width = int(width)
            percent = (int(width) / float(img.size[0]))
            height = int((float(img.size[1]) * float(percent)))
        elif width is None:
            height = int(height)
            percent = (int(height) / float(img.size[1]))
            width = int((float(img.size[0]) * float(percent)))
        else:
            width = int(width)
            height = int(height)

        if overscale or img.size[0] > width or img.size[1] > height:
            img = img.resize((width, height), Image.ANTIALIAS)

        img_io = BytesIO()
        img.save(img_io, 'JPEG', optimize=True, quality=85)
        img_io.seek(0)

        execute_db('UPDATE pictures SET sent = sent + 1 WHERE id = ?', (pnid,))

        return send_file(img_io, mimetype='image/jpeg')
    else:
        return abort(404)


@bp.route('/getstretched')
@bp.route('/getstretchedpnogo')
@require_app_key
def getstretchedpnogo():
    pnid = request.args.get('id')
    maxsize = request.args.get('maxsize') or 1920
    width = int(random.uniform(0.1, 1) * random.uniform(0, 2) * int(maxsize))
    height = int(random.uniform(0.1, 1) * random.uniform(0, 2) * int(maxsize))
    pongo = query_db('SELECT file FROM pictures WHERE id = ?', (pnid,))

    if pongo:
        img = Image.open(os.path.join(current_app.config['PONGHI'], pongo[0])).convert('RGB')

        img = img.resize((width, height), Image.ANTIALIAS)

        img_io = BytesIO()
        img.save(img_io, 'JPEG', optimize=True, quality=85)
        img_io.seek(0)

        execute_db('UPDATE pictures SET sent = sent + 1 WHERE id = ?', (pnid,))

        return send_file(img_io, mimetype='image/jpeg')
    else:
        return abort(404)


@bp.route('/getoriginal')
@bp.route('/getpnogoriginal')
@require_app_key
def getpnogoriginal():
    pnid = request.args.get('id')
    pongo = query_db('SELECT file FROM pictures WHERE id = ?', [pnid])
    return send_from_directory(current_app.config['PONGHI'], pongo[0],
                               mimetype='image/jpeg') if pongo else abort(404)


@bp.route('/random/<cndr>')
@require_app_key
def random(cndr):
    pongo = query_db(
        'SELECT id, description, points FROM pictures WHERE id IN (SELECT p.id FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name LIKE ? ORDER BY RANDOM() LIMIT 1)', [escape(cndr)])
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    } if pongo else abort(404)


@bp.route('/randompnogo')
@require_app_key
def randompnogo():
    return random('pongo')


@bp.route('/daily/<cndr>')
@require_app_key
def daily(cndr):
    pnid = query_db("SELECT p.id FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name LIKE ? AND daily_date=DATE('now') ORDER BY RANDOM() LIMIT 1", [escape(cndr)])
    if pnid is None:
        pnid = query_db("SELECT p.id FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name LIKE ? AND daily_date is null ORDER BY RANDOM() LIMIT 1", [escape(cndr)])
        if pnid is None:
            execute_db("UPDATE pictures SET daily_date=null WHERE cndr_id=(SELECT id FROM cndr WHERE name LIKE ?)", (escape(cndr),))
            pnid = query_db("SELECT p.id FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name LIKE ? AND daily_date is null ORDER BY RANDOM() LIMIT 1", [escape(cndr)])
    if pnid is not None:
        execute_db("UPDATE pictures SET daily_date=DATE('now') WHERE id = ?", pnid)
        pongo = query_db("SELECT id, description, points FROM pictures WHERE id=?", pnid)
        return {
            "id": pongo[0],
            "description": pongo[1],
            "points": pongo[2],
        }
    else:
        abort(404)


@bp.route('/dailypnogo')
@require_app_key
def dailypnogo():
    return daily('pongo')


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
