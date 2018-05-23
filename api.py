from flask.views import MethodView
from werkzeug.local import LocalProxy


class ResourceAPI(MethodView):
    __version__ = 1

    pagination = None

    def __init__(self):
        pass

    def get(self, **kwargs):
        self.pagination = ResourcePagination(req=kwargs.get('req'))

    def post(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def put(self, **kwargs):
        pass


class ResourcePagination(object):
    __version__ = 1

    limit = None
    offset = None

    is_paginated = False

    _offset_field = 'offset'
    _limit_field = 'limit'

    def __init__(self, req: LocalProxy):
        if self._limit_field in req.args:
            self.is_paginated = True
            self.limit = req.args.get(self._limit_field)
            self.offset = req.args.get(self._offset_field, 0)
