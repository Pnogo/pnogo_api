import psycopg

from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)


def get_db():
    pg_uri = current_app.config['DATABASE']
    if 'db' not in g:
        create = 0 # todo reimplement creation
        g.db = psycopg.connect(pg_uri)
        if create:
            with current_app.open_resource('schema.sql') as f:
                g.db.executescript(f.read().decode('utf8'))

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def query_db(query, args=(), multi=False):
    cur = get_db().execute(query, args)
    res = cur.fetchone() if not multi else cur.fetchall()
    cur.close()
    return res or None


def execute_db(query, args=()):
    db = get_db()
    try:
        if type(args) is tuple:
            db.execute(query, args)
        else:
            db.executemany(query, args)
        db.commit()
    except psycopg.Error:
        return False
    return True
