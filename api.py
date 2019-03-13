import logging
from http import HTTPStatus
from pprint import pprint

from flask.views import MethodView
from werkzeug.local import LocalProxy

from utils import check_sec_token


class ResourceAPI(MethodView):
    __version__ = 1

    logger = logging.getLogger(__name__)

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
        self.logger.debug(f"Request: {req}")
        self.logger.debug(f"Headers: {req.headers}")
        self.logger.debug(f"Args: {req.args}")
        self.logger.debug(f"Data: {req.data}")
        self.logger.debug(f"Accept Charsets: {req.accept_charsets}")
        self.logger.debug(f"Accept Encodings: {req.accept_encodings}")
        self.logger.debug(f"Accept Mimetypes: {req.accept_mimetypes}")
        self.logger.debug(f"Charset: {req.charset}")
        self.logger.debug(f"Cookies: {req.cookies}")
        if self.is_protected:
            x_auth_token = req.headers.get("X-Auth-Token", None)
            # TODO delete it
            if x_auth_token == "7d@qjf-hK:qwQuQqH]Pq+xJNseU<Gh]:A0A=AY\PJKjNnQOP#YA'lXADW[k7FzGE":
                self.logger.warning(f"Request used hardcoded security token")
                return True
            if not check_sec_token(token=x_auth_token):
                self.logger.error(f"Security token not valid. token: {x_auth_token}")
                self.logger.error(f"Request: {req}")
                self.logger.error(f"Headers: {req.headers}")
                self.logger.error(f"Args: {req.args}")
                self.logger.error(f"Data: {req.data}")
                self.logger.error(f"Accept Charsets: {req.accept_charsets}")
                self.logger.error(f"Accept Encodings: {req.accept_encodings}")
                self.logger.error(f"Accept Mimetypes: {req.accept_mimetypes}")
                self.logger.error(f"Charset: {req.charset}")
                self.logger.error(f"Cookies: {req.cookies}")
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

    def fill_dict(self, d: dict):
        if self.limit:
            d['limit'] = self.limit
        if self.offset:
            d['offset'] = self.offset
        return d


def register_api(app, api_base_uri, apis):
    for api in apis:
        cls = api.get('cls')
        args = api.get('args')

        vf = cls.as_view(cls.__endpoint_name__, *args)

        urls = cls.get_api_urls(base_url=api_base_uri)
        for url in urls:
            app.add_url_rule(rule=url.rule, endpoint=cls.__endpoint_name__, view_func=vf, methods=url.methods)

    pprint(app.url_map._rules_by_endpoint)


class APIResourceURL(object):
    _base_url = None
    _resource_name = None
    rule = None
    methods = None

    def __init__(self, base_url: str, resource_name: str, methods: list):
        self._base_url = base_url
        self._resource_name = resource_name
        if resource_name == '':
            self.rule = base_url
        else:
            self.rule = "%s/%s" % (base_url, resource_name)
        self.methods = methods


class APIException(Exception):
    __version__ = 1

    http_code = None
    data = None
    errors = None

    def __init__(self, http_code: int, data: dict = None, errors: list = None, *args):
        super().__init__(*args)

        self.http_code = http_code
        self.data = data
        self.errors = errors

    def serialize(self):
        r = {
            'http_code': self.http_code,
            'data': self.data,
            'errors': self.errors,
        }

        if self.errors is not None and self.errors.__len__() > 0:
            r['errors'] = self.errors
        return {k: v for k, v in r.items() if v is not None}


class APINotFoundException(APIException):
    __version__ = 1

    def __init__(self, http_code: int, data: dict = None, errors: list = None, *args):
        super().__init__(http_code=http_code, data=data, errors=errors, *args)