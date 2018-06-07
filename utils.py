import decimal
import uuid

import simplejson as json
from flask import Response, make_response

from response import APIResponse


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
    except ValueError:
        return False


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
