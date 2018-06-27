from http import HTTPStatus
from typing import List


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


from enum import Enum

name = 'COMMON-'
i = 0


def count():
    global i
    i += 1
    return i


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

        if status == APIResponseStatus.success.status or code == HTTPStatus.NO_CONTENT:
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
        r = {
            'status': self.status,
            'data': self.data,
            'limit': self.limit,
            'offset': self.offset,
        }

        if self.errors is not None and self.errors.__len__() > 0:
            r['errors'] = self.errors
        return {k: v for k, v in r.items() if v is not None}
