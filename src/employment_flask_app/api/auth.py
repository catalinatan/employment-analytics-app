import hmac
import os
from functools import wraps

from flask import jsonify, request


def require_api_key(fn):
    """Reject requests missing a matching x-api-key header.

    Uses hmac.compare_digest to avoid timing side-channels when comparing
    the caller-supplied key against ENTERPRISE_API_KEY.
    """
    @wraps(fn)
    def wrapped(*args, **kwargs):
        provided = request.headers.get('x-api-key', '')
        expected = os.environ.get('ENTERPRISE_API_KEY', '')
        if not expected or not hmac.compare_digest(provided, expected):
            return jsonify(
                error='unauthorized',
                message='Missing or invalid x-api-key header'
            ), 401
        return fn(*args, **kwargs)
    return wrapped
