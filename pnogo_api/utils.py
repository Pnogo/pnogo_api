import os

from flask import current_app

from pnogo_api.db import query_db, execute_db


def sync_pnogo():
    os.system(
        'rclone sync --include *.jpg --include *.jpeg "marcogp:shared-album/Pnogo dumpster" ' + current_app.config[
            'PONGHI'])
    return sync_db()


def sync_db():
    folp = set(zip(os.listdir(current_app.config['PONGHI'])))
    dbp = set(query_db('SELECT file FROM pictures', multi=True) or [])
    add = folp - dbp
    rem = dbp - folp

    execute_db('INSERT INTO pictures (file) VALUES (?)', add)
    execute_db('DELETE FROM pictures WHERE file=?', rem)

    return len(add), len(rem)
