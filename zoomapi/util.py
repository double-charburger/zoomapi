# THIS FILE WAS CHANGED FROM THE ORIGINAL

"""Utility classes and functions"""

import contextlib
import json
import requests
from requests_oauthlib import OAuth2Session
import time
import jwt
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from threading import Thread
from urllib.parse import urlparse, urlencode, quote
import os
import functools, time


class ApiClient(object):
    """Simple wrapper for REST API requests"""

    def __init__(self, base_uri=None, timeout=15, **kwargs):
        """Setup a new API Client

        :param base_uri: The base URI to the API
        :param timeout: The timeout to use for requests
        :param kwargs: Any other attributes. These will be added as
                           attributes to the ApiClient object.
        """
        self.base_uri = base_uri
        self.timeout = timeout
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def timeout(self):
        """The timeout"""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """The default timeout"""
        if value is not None:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("timeout value must be an integer")
        self._timeout = value

    @property
    def base_uri(self):
        """The base_uri"""
        return self._base_uri

    @base_uri.setter
    def base_uri(self, value):
        """The default base_uri"""
        if value and value.endswith("/"):
            value = value[:-1]
        self._base_uri = value

    def url_for(self, endpoint):
        """Get the URL for the given endpoint

        :param endpoint: The endpoint
        :return: The full URL for the endpoint
        """
        if not endpoint.startswith("/"):
            endpoint = "/{}".format(endpoint)
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        return self.base_uri + endpoint

    def get_request(self, endpoint, params=None, headers=None):
        """Helper function for GET requests

        :param endpoint: The endpoint
        :param params: The URL parameters
        :param headers: request headers
        :return: The :class:``requests.Response`` object for this request
        """
        if headers is None:
            headers = {"Authorization": "Bearer {}".format(self.config.get("token"))}
        return requests.get(
            self.url_for(endpoint), params=params, headers=headers, timeout=self.timeout
        )

    def post_request(
        self, endpoint, params=None, data=None, headers=None, cookies=None
    ):
        """Helper function for POST requests

        :param endpoint: The endpoint
        :param params: The URL parameters
        :param data: The data (either as a dict or dumped JSON string) to
                     include with the POST
        :param headers: request headers
        :param cookies: request cookies
        :return: The :class:``requests.Response`` object for this request
        """
        if data and not is_str_type(data):
            data = json.dumps(data)
        if headers is None:
            headers = {"Authorization": "Bearer {}".format(self.config.get("token"))}
        headers["Content-type"] = "application/json"
        return requests.post(
            self.url_for(endpoint),
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=self.timeout,
        )

    def patch_request(
        self, endpoint, params=None, data=None, headers=None, cookies=None
    ):
        """Helper function for PATCH requests

        :param endpoint: The endpoint
        :param params: The URL parameters
        :param data: The data (either as a dict or dumped JSON string) to
                     include with the PATCH
        :param headers: request headers
        :param cookies: request cookies
        :return: The :class:``requests.Response`` object for this request
        """
        if data and not is_str_type(data):
            data = json.dumps(data)
        if headers is None:
            headers = {"Authorization": "Bearer {}".format(self.config.get("token"))}
        headers["Content-type"] = "application/json"
        return requests.patch(
            self.url_for(endpoint),
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=self.timeout,
        )

    def delete_request(
        self, endpoint, params=None, data=None, headers=None, cookies=None
    ):
        """Helper function for DELETE requests

        :param endpoint: The endpoint
        :param params: The URL parameters
        :param data: The data (either as a dict or dumped JSON string) to
                     include with the DELETE
        :param headers: request headers
        :param cookies: request cookies
        :return: The :class:``requests.Response`` object for this request
        """
        if data and not is_str_type(data):
            data = json.dumps(data)
        if headers is None:
            headers = {"Authorization": "Bearer {}".format(self.config.get("token"))}
        headers["Content-type"] = "application/json"
        return requests.delete(
            self.url_for(endpoint),
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=self.timeout,
        )

    def put_request(self, endpoint, params=None, data=None, headers=None, cookies=None):
        """Helper function for PUT requests

        :param endpoint: The endpoint
        :param params: The URL paramaters
        :param data: The data (either as a dict or dumped JSON string) to
                     include with the PUT
        :param headers: request headers
        :param cookies: request cookies
        :return: The :class:``requests.Response`` object for this request
        """
        if data and not is_str_type(data):
            data = json.dumps(data)
        if headers is None:
            headers = {"Authorization": "Bearer {}".format(self.config.get("token"))}
        headers["Content-type"] = "application/json"
        return requests.put(
            self.url_for(endpoint),
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=self.timeout,
        )


@contextlib.contextmanager
def ignored(*exceptions):
    """Simple context manager to ignore expected Exceptions

    :param \*exceptions: The exceptions to safely ignore
    """
    try:
        yield
    except exceptions:
        pass


def is_str_type(val):
    """Check whether the input is of a string type.

    We use this method to ensure python 2-3 capatibility.

    :param val: The value to check wither it is a string
    :return: In python2 it will return ``True`` if :attr:`val` is either an
             instance of str or unicode. In python3 it will return ``True`` if
             it is an instance of str
    """
    with ignored(NameError):
        return isinstance(val, basestring)
    return isinstance(val, str)


def require_keys(d, keys, allow_none=True):
    """Require that the object have the given keys

    :param d: The dict the check
    :param keys: The keys to check :attr:`obj` for. This can either be a single
                 string, or an iterable of strings

    :param allow_none: Whether ``None`` values are allowed
    :raises:
        :ValueError: If any of the keys are missing from the obj
    """
    if is_str_type(keys):
        keys = [keys]
    for k in keys:
        if k not in d:
            raise ValueError("'{}' must be set".format(k))
        if not allow_none and d[k] is None:
            raise ValueError("'{}' cannot be None".format(k))
    return True


def date_to_str(d):
    """Convert date and datetime objects to a string

    Note, this does not do any timezone conversion.

    :param d: The :class:`datetime.date` or :class:`datetime.datetime` to
              convert to a string
    :returns: The string representation of the date
    """
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_jwt(key, secret):
    header = {"alg": "HS256", "typ": "JWT"}

    payload = {"iss": key, "exp": int(time.time() + 3600)}

    token = jwt.encode(payload, secret, algorithm="HS256", headers=header)
    return token.decode("utf-8")


class TokenHandler(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        # print("GET " + self.path)
        query = urlparse(self.path).query
        if len(query) > 0:
            # print("query: " + query)
            query_components = dict(qc.split("=") for qc in query.split("&"))
            TokenHandler.code = query_components["code"]
            # print("***" + TokenHandler.code + "***")
        self.send_response(200)
        self.end_headers()


def start_http_receiver(port):
    with socketserver.TCPServer(("", port), TokenHandler) as httpd:
        print(f"Start listening at localhost:{port}")
        while TokenHandler.code == None:
            httpd.handle_request()
        print("Stop listening")


def get_oauth_token(cid, client_secret, port, redirect_url, browser_path):
    oauth = OAuth2Session(client_id=cid, redirect_uri=redirect_url)
    authorization_url, state = oauth.authorization_url(
        "https://zoom.us/oauth/authorize"
    )

    # print ('Going to %s to authorize access.' % authorization_url)
    if os.name == "nt":
        authorization_url = authorization_url.replace("&", "^&")
    else:
        authorization_url = authorization_url.replace("&", "\&")
    # print(authorization_url)

    # bring up the browser
    os.system(browser_path + " " + authorization_url)

    # start the receiver to get the code (TokenHandler.code)
    # {10_char_code}_{user_id}
    start_http_receiver(port)

    # get oauth token
    token = oauth.fetch_token(
        "https://zoom.us/oauth/token",
        code=TokenHandler.code,
        client_secret=client_secret,
    )
    resp = dict(token)
    return resp["access_token"]


class Throttled:
    INTERVAL = 0.150  # A bit slower than the documented rate
    time = 0

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, obj, *args, **kwargs):
        now = time.perf_counter()
        delta = now - Throttled.time
        if delta < Throttled.INTERVAL:
            print(f'...Slowing down by {Throttled.INTERVAL - delta}...')
            time.sleep(Throttled.INTERVAL - delta)
        result = self.func(obj, *args, **kwargs)
        Throttled.time = time.perf_counter()
        return result
