import decimal
import uuid
from http import HTTPStatus

import simplejson as json
from flask import Response, make_response

from response import APIResponse, APIError, APIErrorEnum, APIResponseStatus


class JSONDecimalEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        elif isinstance(o, uuid.UUID):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super().iterencode(o, _one_shot)


def check_uuid(suuid: str) -> bool:
    try:
        uuid.UUID(suuid)
        return True
    except (ValueError, TypeError):
        return False


def check_required_api_fields(*args):
    errors = []
    for arg in args:
        if arg is None or (isinstance(args, str) and arg.strip() == ''):
            error = APIError(code='COMMON-000000', message='REQUIRED_FIELD_ERROR %s phrase' % arg,
                             developer_message='REQUIRED_FIELD_ERROR description')
            errors.append(error)
    return errors


def make_api_response(http_code: int, data: APIResponse = None) -> Response:
    if data is None:
        resp = make_response('', http_code)
    else:
        resp = make_response(json.dumps(data.serialize()), http_code)
    resp.mimetype = "application/json"

    if data is not None and data.headers is not None:
        headers = data.headers
        for k, v in headers.items():
            resp.headers[k] = v

    return resp


def make_error_request_response(http_code: HTTPStatus, err: APIErrorEnum = None):
    if err is None:
        response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code)
    else:
        error_message = err.message
        error_code = err.code
        developer_message = err.developer_message
        response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, error=error_message,
                                    developer_message=developer_message, error_code=error_code)
    return make_api_response(data=response_data, http_code=http_code)
