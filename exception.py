class APIException(Exception):
    __version__ = 1

    http_code = None
    code = None
    message = None
    data = None

    def __init__(self, message: str, code: int, http_code: int, data: dict = None, *args):
        super().__init__(*args)

        self.code = code
        self.message = message
        self.data = data
        self.http_code = http_code
        self.data = data
