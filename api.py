from typing import Any

from flask.views import MethodView


class ResourceAPI(MethodView):
    __version__ = 1

    _offset_field = 'offset'

    def __init__(self):
        pass

    def get(self, **kwargs):
        pass

    def post(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def put(self, **kwargs):
        pass
