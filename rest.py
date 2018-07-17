import json
import logging
from http import HTTPStatus
from json import JSONDecodeError

import requests
import simplejson

from response import APIResponse, APIResponseStatus, CustomJSONEncoder

logger = logging.getLogger(__name__)


class RESTService(object):
    __version__ = 1

    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }
    _url = None

    def __init__(self, api_url: str, resource_name: str, headers: dict = None) -> None:
        super().__init__()

        self._url = "%s/%s" % (api_url, resource_name)

        if headers:
            self._headers = headers

        logger.debug("RESTService init. %s" % self.__repr__())

    def _get(self, url: str = None, params: dict = None, headers: dict = None) -> APIResponse:
        if url is None:
            url = self._url
        logger.debug("get method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.get(url=url, params=params, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except (JSONDecodeError, simplejson.errors.JSONDecodeError):
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed.status), code=req.status_code,
                                   headers=req.headers, data=req_json.get('data', {}),
                                   errors=req_json.get('errors', {}))

        return api_response

    def _post(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        if url is None:
            url = self._url
        logger.debug("post method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.post(url=url, json=data, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except (JSONDecodeError, simplejson.errors.JSONDecodeError):
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed.status),
                                   code=req.status_code,
                                   headers=req.headers,
                                   data=req_json.get('data', {}),
                                   errors=req_json.get('errors', {}))
        return api_response

    def _put(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        if url is None:
            url = self._url
        logger.debug("put method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.put(url=url, data=json.dumps(data, cls=CustomJSONEncoder), headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except (JSONDecodeError, simplejson.errors.JSONDecodeError):
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed.status),
                                   code=req.status_code,
                                   headers=req.headers,
                                   data=req_json.get('data', {}),
                                   errors=req_json.get('errors', {}))
        return api_response

    def _build_url_pagination(self, limit: int = 0, offset: int = 0, url: str = None):
        if url is None:
            url = self._url
        if limit != 0:
            url = self._url + "?limit=%s&offset=%s" % (limit, offset)

        return url

    def __repr__(self):
        return self.__dict__


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
