import json
import logging
from enum import IntEnum
from http import HTTPStatus
from json import JSONDecodeError

import requests

from services.response import APIResponse, APIResponseStatus


class RESTService(object):
    __version__ = 1

    _headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    _url = None

    def __init__(self, api_url: str, headers: dict = None) -> None:
        super().__init__()

        self._url = api_url

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
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE,
                               code=APIError.UNKNOWN_ERROR_CODE,
                               message=HTTPStatus.SERVICE_UNAVAILABLE.phrase)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed),
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
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE,
                               code=APIError.UNKNOWN_ERROR_CODE,
                               message=HTTPStatus.SERVICE_UNAVAILABLE.phrase)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', APIResponseStatus.failed),
                                   code=req.status_code, headers=req.headers, data=req_json)
        return api_response

    def _put(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        logging.debug("put method")
        if url is None:
            url = self._url
        try:
            req = requests.put(url=url, data=json.dumps(data), headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=HTTPStatus.SERVICE_UNAVAILABLE,
                               code=APIError.UNKNOWN_ERROR_CODE, message=HTTPStatus.SERVICE_UNAVAILABLE.phrase)

        req_json = {}
        try:
            req_json = req.json()
        except JSONDecodeError:
            pass

        api_response = APIResponse(status=req_json.get('status', None), code=req.status_code, headers=req.headers,
                                   data=req_json)
        return api_response

    def __repr__(self):
        return self.__dict__


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

    code = None
    http_code = None
    message = None
    data = None

    def __init__(self, message: str, code: int, http_code: int, data: dict = None, *args):
        super().__init__(*args)

        self.code = code
        self.http_code = http_code
        self.message = message
        self.data = data
