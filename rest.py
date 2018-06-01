import json
import logging
from enum import IntEnum
from http import HTTPStatus
from json import JSONDecodeError

import requests

from response import APIResponse, APIResponseStatus


class RESTService(object):
    __version__ = 1

    _headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    _url = None

    def __init__(self, api_url: str, resource_name: str, headers: dict = None) -> None:
        super().__init__()

        self._url = "%s/%s" % (api_url, resource_name)

        if headers:
            self._headers = headers

        logging.debug("RESTService init. %s" % self.__repr__())

    def _get(self, url: str = None, params: dict = None, headers: dict = None) -> APIResponse:
        logging.debug("get method")
        if url is None:
            url = self._url
        try:
            req = requests.get(url=url, params=params, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed.value),
                                   data=req_json.get('data', {}), code=req.status_code, headers=req.headers,
                                   error=req_json.get('error', None), error_code=req_json.get('error_code', None),
                                   developer_message=req_json.get('developer_message', None))

        return api_response

    def _post(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        logging.debug("post method")
        if url is None:
            url = self._url
        try:
            req = requests.post(url=url, json=data, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed.value),
                                   code=req.status_code, headers=req.headers, data=req_json)
        return api_response

    def _put(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        logging.debug("put method")
        if url is None:
            url = self._url
        if headers is None:
            headers = self._headers
        try:
            req = requests.put(url=url, data=json.dumps(data), headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', None), code=req.status_code, headers=req.headers,
                                   data=req_json)
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

        self.rule = "%s/%s" % (base_url, resource_name)
        self.methods = methods



class APIError(IntEnum):
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    UNKNOWN_ERROR_CODE = (0, '', '')


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
