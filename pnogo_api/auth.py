import functools

from flask import (
    Blueprint, request, abort
)

from pnogo_api.db import query_db

bp = Blueprint('auth', __name__)


def match_api_keys(key):
    out = query_db('select name from auth where key = ?', [key])
    return out is not None


def require_app_key(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if match_api_keys(request.args.get('key')):
            return f(*args, **kwargs)
        else:
            abort(401)

    return decorated
