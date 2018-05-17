class APIResponse(object):
    status = None
    code = None
    data = {}
    error = None
    error_code = None
    developer_message = None
    headers = None

    def __init__(self, status: str, code: int, headers: dict = headers, data: dict = None, error: str = None,
                 error_code: int = None, developer_message: str = None):
        self.status = status
        self.data = data
        self.code = code
        self.error = error
        self.error_code = error_code
        self.developer_message = developer_message
        if headers:
            try:
                self.headers = headers.items()
            except AttributeError:
                pass

    def serialize(self):
        return {
            'status': self.status,
            'code': self.code,
            'data': self.data,
            'error': self.error,
            'error_code': self.error_code,
            'developer_message': self.developer_message,
            'headers': self.headers,
        }


from enum import Enum


class APIResponseStatus(Enum):
    success = 'success'
    failed = 'failed'
