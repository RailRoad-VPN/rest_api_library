from pprint import pprint

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

    def __init__(self, req: LocalProxy = None, limit: int = None, offset: int = None):
        if req is not None:
            if self._limit_field in req.args:
                self.is_paginated = True
                try:
                    self.limit = int(req.args.get(self._limit_field))
                    self.offset = int(req.args.get(self._offset_field, 0))
                except ValueError:
                    self.is_paginated = False
        elif limit is not None:
            self.is_paginated = True
            self.limit = limit
            self.offset = offset


def register_api(app, api_base_uri, apis):
    for api in apis:
        cls = api.get('cls')
        args = api.get('args')

        vf = cls.as_view(cls.__endpoint_name__, *args)

        urls = cls.get_api_urls(base_url=api_base_uri)
        for url in urls:
            app.add_url_rule(rule=url.rule, endpoint=cls.__endpoint_name__, view_func=vf, methods=url.methods)

    pprint(app.url_map._rules_by_endpoint)
