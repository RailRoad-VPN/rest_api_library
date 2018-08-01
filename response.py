import datetime
import decimal
import json
import logging
import uuid
from enum import Enum
from http import HTTPStatus
from typing import List

from flask import make_response, Response

logger = logging.getLogger(__name__)


class APIError(object):
    __version__ = 1

    code = None
    message = None
    developer_message = None

    def __init__(self, code: str, message: str, developer_message: str = None):
        self.code = code
        self.message = message
        self.developer_message = developer_message

    def serialize(self):
        return {
            'code': self.code,
            'message': self.message,
            'developer_message': self.developer_message,
        }


class APIErrorEnum(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, code, message, developer_message):
        self.code = code
        self.message = message
        self.developer_message = developer_message


class APIResponseStatus(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, code, status):
        self.code = code
        self.status = status

    success = (1, 'success')
    failed = (0, 'failed')


class APIResponse(object):
    __version__ = 1

    is_ok = False
    status = None
    code = None
    headers = None
    data = {}
    errors = List[APIError]
    limit = None
    offset = None

    def __init__(self, status: str, code: int, headers=None, errors: List[APIError] = None, data=None,
                 error: str = None, error_code: int = None, developer_message: str = None, limit: int = None,
                 offset: int = None):
        logger.debug(f"Prepare APIResponse with parameters: status={status}, code={code}, errors={errors}, "
                     f"data={data}, error={error}, error_code={error_code}, developer_message={developer_message},"
                     f"limit={limit}, offset={offset}")
        self.status = status
        self.code = code
        self.data = data
        self.limit = limit
        self.offset = offset
        self.errors = errors
        if headers:
            self.headers = dict(headers.items())
        if error is not None or error_code is not None or developer_message is not None:
            self.add_error(code=error_code, message=error, developer_message=developer_message)

        if status == APIResponseStatus.success.status:
            self.is_ok = True
        else:
            self.is_ok = False

    def add_error(self, code, message, developer_message):
        error = {
            'message': message,
            'code': code,
            'developer_message': developer_message,
        }
        if self.errors is None:
            self.errors = []
        self.errors.append({k: v for k, v in error.items() if v is not None})

    def serialize(self):
        # clean data from empty objects
        if self.data:
            if type(self.data) is list:
                t_data = []
                for el in self.data:
                    t_data.append({k: v for k, v in el.items() if v is not None})
                self.data = t_data
            elif type(self.data) is dict:
                self.data = {k: v for k, v in self.data.items() if v is not None}

        r = {
            'status': self.status,
            'data': self.data,
            'limit': self.limit,
            'offset': self.offset,
        }

        if self.errors is not None and self.errors.__len__() > 0:
            r['errors'] = self.errors
        return {k: v for k, v in r.items() if v is not None}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if o.utcoffset() is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        else:
            return super(CustomJSONEncoder, self).default(o)


def make_api_response(http_code: int, data: APIResponse = None) -> Response:
    if data is None:
        resp = make_response('', http_code)
    else:
        resp = make_response(json.dumps(data.serialize(), cls=CustomJSONEncoder), http_code)
    resp.mimetype = "application/json"

    return resp


def make_error_request_response(http_code: HTTPStatus, err=None):
    if err is None:
        response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code)
    else:
        if isinstance(err, list):
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=err)
        else:
            error_message = err.message
            error_code = err.code
            developer_message = err.developer_message
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, error=error_message,
                                        developer_message=developer_message, error_code=error_code)
    return make_api_response(data=response_data, http_code=http_code)


def check_required_api_fields(fields: dict):
    errors = []
    for k, v in fields.items():
        if v is None or (isinstance(v, str) and v.strip() == ''):
            error = APIError(code='COMMON-000000', message='Field \'%s\' is REQUIRED' % k,
                             developer_message='Fill this field to perform request')
            errors.append(error.serialize())
    return errors
