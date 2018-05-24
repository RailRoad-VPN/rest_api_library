class APIResponse(object):
    status = None
    code = None
    headers = None
    data = {}
    errors = []
    limit = None
    offset = None

    def __init__(self, status: str, code: int, headers=None, errors: list = None, data=None, error: str = None,
                 error_code: int = None, developer_message: str = None, limit: int = None, offset: int = None):
        self.status = status
        self.code = code
        self.data = data
        self.limit = limit
        self.offset = offset
        self.errors = errors
        if headers:
            self.headers = headers
        if error is not None or error_code is not None or developer_message is not None:
            self.add_error(code=error_code, message=error, developer_message=developer_message)

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


from enum import Enum


class APIResponseStatus(Enum):
    success = 'success'
    failed = 'failed'
