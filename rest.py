import json
import logging
from http import HTTPStatus
from json import JSONDecodeError

import requests
import simplejson

from api import ResourcePagination, APIException, APINotFoundException
from response import APIResponse, APIResponseStatus, CustomJSONEncoder

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class RESTService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }
    _url = None

    __auth = None

    def __init__(self, api_url: str, resource_name: str, headers: dict = None, auth: set = None) -> None:
        super().__init__()

        self._url = "%s/%s" % (api_url, resource_name)

        if headers:
            self._headers = headers

        self.__auth = auth

        self.logger.debug(f"{self.__class__}: RESTService init. %s" % self.__repr__())

    def _get(self, url: str = None, params: dict = None, headers: dict = None,
             pagination: ResourcePagination = None) -> APIResponse:
        if url is None:
            url = self._url
        if pagination and pagination.is_paginated:
            params = pagination.fill_dict(d=params)
        self.logger.debug(f"{self.__class__}: get method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.get(url=url, params=params, headers=headers, auth=self.__auth)
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

        if not api_response.is_ok:
            if api_response.code == HTTPStatus.NOT_FOUND:
                raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response

    def _post(self, data: dict, url: str = None, headers: dict = None, timeout: int = None) -> APIResponse:
        if url is None:
            url = self._url
        self.logger.debug(f"{self.__class__}: post method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.post(url=url, json=data, headers=headers, auth=self.__auth, timeout=(timeout, timeout))
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

        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response

    def _put(self, data: dict, url: str = None, headers: dict = None) -> APIResponse:
        if url is None:
            url = self._url
        self.logger.debug(f"{self.__class__}: put method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.put(url=url, data=json.dumps(data, cls=CustomJSONEncoder), headers=headers, auth=self.__auth)
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

        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response

    def _delete(self, url: str = None, headers: dict = None) -> APIResponse:
        if url is None:
            url = self._url
        self.logger.debug(f"{self.__class__}: put method. URL: %s" % url)
        if headers is not None:
            headers = {**self._headers, **headers}
        else:
            headers = self._headers
        try:
            req = requests.delete(url=url, headers=headers, auth=self.__auth)
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

        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response

    def _build_url_pagination(self, limit: int = 0, offset: int = 0, url: str = None):
        if url is None:
            url = self._url
        if limit != 0:
            if "?" not in url:
                url = self._url + "?limit=%s&offset=%s" % (limit, offset)
            else:
                url = self._url + "&limit=%s&offset=%s" % (limit, offset)

        return url

    def __repr__(self):
        return self.__dict__
