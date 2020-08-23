from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from bluelog.apis.v1 import api_v1


def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')
    
    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response


class ValidationError(ValueError):
    pass


@api_v1.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.args[0])
