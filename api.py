from http import HTTPStatus
from pprint import pprint

from flask.views import MethodView
from werkzeug.local import LocalProxy

from rest import APIException
from utils import check_sec_token


class ResourceAPI(MethodView):
    __version__ = 1

    pagination = None
    _config = None

    is_protected = False
    is_auth_passed = True

    def __init__(self, config: dict, is_protected: bool = False):
        self.is_protected = is_protected
        self._config = config

    def get(self, **kwargs):
        req = kwargs.get('req')
        self.pagination = ResourcePagination(req=req)

        self._check_token(req=req)

    def post(self, **kwargs):
        req = kwargs.get('req')
        self._check_token(req=req)

    def delete(self, **kwargs):
        req = kwargs.get('req')
        self._check_token(req=req)

    def put(self, **kwargs):
        req = kwargs.get('req')
        self._check_token(req=req)

    def _check_token(self, req: LocalProxy):
        if self.is_protected and not self._config['DEBUG']:
            x_auth_token = req.headers.get("X-Auth-Token", None)
            if not check_sec_token(token=x_auth_token):
                raise APIException(http_code=HTTPStatus.UNAUTHORIZED)


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
