from flask import (
    Blueprint, request, send_file, send_from_directory, current_app, abort
)
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from io import BytesIO
import os
import json
import random
from markupsafe import escape

from pnogo_api.auth import require_app_key
from pnogo_api.db import query_db, execute_db

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
    pnogos = query_db('SELECT p.id, p.file, p.description, p.points, p.sent, CAST(p.daily_date AS TEXT) FROM pictures p JOIN cndr c ON p.cndr_id=c.id WHERE c.name LIKE %s', [escape(cndr)], multi=True)
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
    pnid = request.args.get('id')
    desc = request.args.get('description')
    execute_db('UPDATE pictures SET description = ? WHERE id = ?', (desc, pnid,))
    return f"done! set desc of {pnid} to: {desc}"


@bp.route('/info')
@bp.route('/infopnogo')
@require_app_key
def infopnogo():
    pnid = request.args.get('id')
    pongo = query_db('SELECT p.file, p.description, p.points, p.sent, CAST(p.daily_date AS TEXT), c.name FROM pictures p JOIN cndr c ON p.cndr_id=c.id WHERE p.id = ?', [pnid])
    return {
        "file": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
        "sent": pongo[3],
        "daily_date": pongo[4],
        "name": pongo[5],
    } if pongo else abort(404)


@bp.route('/count')
@require_app_key
def count_all():
    res = query_db('SELECT count(*) FROM pictures')
    return {"count": res[0]} if res else abort(404)


@bp.route('/count/<cndr>')
@require_app_key
def count(cndr):
    res = query_db('SELECT count(*) FROM pictures JOIN cndr c ON cndr_id=c.id WHERE c.name ILIKE %s', [escape(cndr)])
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
    pongo = query_db('SELECT file FROM pictures WHERE id = %s', (pnid,))

    if pongo:
        img = Image.open(os.path.join(current_app.config['PONGHI'], pongo[0])).convert('RGB')
        img = ImageOps.exif_transpose(img)
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
            img = img.resize((width, height), Image.LANCZOS)

        img_io = BytesIO()
        img.save(img_io, 'JPEG', optimize=True, quality=85)
        img_io.seek(0)

        execute_db('UPDATE pictures SET sent = sent + 1 WHERE id = %s', (pnid,))

        return send_file(img_io, mimetype='image/jpeg')
    else:
        return abort(404)


@bp.route('/getstretched')
@bp.route('/getstretchedpnogo')
@require_app_key
def getstretchedpnogo():
    pnid = request.args.get('id')
    maxsize = int(request.args.get('maxsize') or 1920)
    otherside = int(random.uniform(1/20, 1) * maxsize)
    direc = random.random() < 0.5
    width = otherside if direc else maxsize
    height = maxsize if direc else otherside
    pongo = query_db('SELECT file FROM pictures WHERE id = %s', (pnid,))

    if pongo:
        img = Image.open(os.path.join(current_app.config['PONGHI'], pongo[0])).convert('RGB')

        img = img.resize((width, height), Image.LANCZOS)

        img_io = BytesIO()
        img.save(img_io, 'JPEG', optimize=True, quality=85)
        img_io.seek(0)

        execute_db('UPDATE pictures SET sent = sent + 1 WHERE id = %s', (pnid,))

        return send_file(img_io, mimetype='image/jpeg')
    else:
        return abort(404)

@bp.route('/getbitmap')
@require_app_key
def getbitmap():
    pnid = request.args.get('id')
    width = request.args.get('width') or 128
    height = request.args.get('height') or 64
    pongo = query_db('SELECT file FROM pictures WHERE id = %s', (pnid,))

    if pongo:
        img = Image.open(os.path.join(current_app.config['PONGHI'], pongo[0])).convert('RGB')
        img = img.resize((width, height), Image.LANCZOS)
        img = img.convert("1")
        out = "".join("0x%02x," % b for b in img.tobytes())

        execute_db('UPDATE pictures SET sent = sent + 1 WHERE id = %s', (pnid,))

        return out
    else:
        return abort(404)

@bp.route('/getoriginal')
@bp.route('/getpnogoriginal')
@require_app_key
def getpnogoriginal():
    pnid = request.args.get('id')
    pongo = query_db('SELECT file FROM pictures WHERE id = %s', [pnid])
    return send_from_directory(current_app.config['PONGHI'], pongo[0],
                               mimetype='image/jpeg') if pongo else abort(404)


@bp.route('/random')
@require_app_key
def random_all():
    pongo = query_db(
        'SELECT p.id, p.description, p.points, c.name FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE p.id IN (SELECT id FROM pictures ORDER BY RANDOM() LIMIT 1)')
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
        "name": pongo[3],
    } if pongo else abort(404)


@bp.route('/random/<cndr>')
@require_app_key
def random_cndr(cndr):
    pongo = query_db(
        'SELECT id, description, points FROM pictures WHERE id IN (SELECT p.id FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name ILIKE %s ORDER BY RANDOM() LIMIT 1)', [escape(cndr)])
    return {
        "id": pongo[0],
        "description": pongo[1],
        "points": pongo[2],
    } if pongo else abort(404)


@bp.route('/randompnogo')
@require_app_key
def randompnogo():
    return random_cndr('pongo')


@bp.route('/dailypnogo')
@bp.route('/daily')
@require_app_key
def daily():
    pnid = query_db("SELECT id FROM pictures WHERE daily_date=now()::date ORDER BY RANDOM() LIMIT 1")
    if pnid is None:
        pnid = query_db("SELECT id FROM pictures WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
        if pnid is None:
            execute_db("UPDATE pictures SET daily_date=null")
            pnid = query_db("SELECT id FROM pictures WHERE daily_date is null ORDER BY RANDOM() LIMIT 1")
    if pnid is not None:
        execute_db("UPDATE pictures SET daily_date=now()::date WHERE id = %s", pnid)
        pongo = query_db("SELECT p.id, p.description, p.points, c.name FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE p.id=%s", pnid)
        return {
            "id": pongo[0],
            "description": pongo[1],
            "points": pongo[2],
            "name": pongo[3],
        }
    else:
        abort(404)


@bp.route('/update')
@require_app_key
def update():  # function now useless!
    return {
        "added": 0,
        "removed": 0,
    }


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/add/<cndr>', methods=['GET', 'POST'])
@require_app_key
def add(cndr):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'picture' not in request.files:
            return 'morte: no parameter'
        file = request.files['picture']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file is None or file.filename == '':
            return 'morte: no file'
        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return 'morte: file type not allowed'
        pnid = query_db('SELECT id FROM pictures WHERE file = %s', [filename])
        if pnid is not None:
            return f'morte: {filename} already present in db with id {pnid[0]}'
        cndr_id = query_db('SELECT id FROM cndr WHERE name ILIKE %s', [escape(cndr)])
        if cndr_id is None:
            return f'morte: {escape(cndr)} non è presente nel db'
        file.save(os.path.join(current_app.config['PONGHI'], filename))
        execute_db('INSERT INTO pictures (file, cndr_id) VALUES (%s,%s)', (filename, cndr_id[0]))
        return 'done!'

    return f'''
    <!doctype html>
    <title>Upload new {cndr}</title>
    <h1>Upload new {cndr}</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=picture>
      <input type=submit value=Upload>
    </form>
    '''


@bp.route('/addpnogo', methods=['GET', 'POST'])
@require_app_key
def addpnogo():
    return add('pongo')


@bp.route('/create')
@require_app_key
def create():
    name = escape(request.args.get('name'))
    success = execute_db('INSERT INTO cndr (name) VALUES (%s)', (name,))
    return 'done' if success else f'morte: {name} already present in db'


@bp.route('/remove')
@require_app_key
def remove():
    name = escape(request.args.get('name'))
    cnt = query_db('SELECT COUNT(p.id) FROM pictures p JOIN cndr c ON cndr_id=c.id WHERE c.name ILIKE %s', (name,))
    if cnt[0] > 0:
        return f'morte: some pictures of {name} are still in the db'

    execute_db('DELETE FROM cndr WHERE name=%s', (name,))
    return 'done'


@bp.route('/list')
@require_app_key
def listcndr():
    cndrs = query_db('SELECT id, name FROM cndr', multi=True)
    keys = ['id', 'name']
    out = [dict(zip(keys, cndr)) for cndr in cndrs] if cndrs else []
    return json.dumps(out)


@bp.route('/version')
@require_app_key
def version():
    import pkg_resources
    vrs = pkg_resources.require("pnogo_api")[0].version
    return {'version': vrs}
