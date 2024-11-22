"""
TODO:
 - import mimetypes lol
 - http.HTTPStatus / http.HTTPMethod
"""
import base64
import http


##


def format_status(status: http.HTTPStatus) -> str:
    return f'{int(status)} {status.phrase}'


STATUS_OK = format_status(http.HTTPStatus.OK)

STATUS_FOUND = format_status(http.HTTPStatus.FOUND)
STATUS_TEMPORARY_REDIRECT = format_status(http.HTTPStatus.TEMPORARY_REDIRECT)

STATUS_BAD_REQUEST = format_status(http.HTTPStatus.BAD_REQUEST)
STATUS_UNAUTHORIZED = format_status(http.HTTPStatus.UNAUTHORIZED)
STATUS_FORBIDDEN = format_status(http.HTTPStatus.FORBIDDEN)
STATUS_NOT_FOUND = format_status(http.HTTPStatus.NOT_FOUND)
STATUS_METHOD_NOT_ALLOWED = format_status(http.HTTPStatus.METHOD_NOT_ALLOWED)
STATUS_REQUEST_TIMEOUT = format_status(http.HTTPStatus.REQUEST_TIMEOUT)

STATUS_INTERNAL_SERVER_ERROR = format_status(http.HTTPStatus.INTERNAL_SERVER_ERROR)
STATUS_NOT_IMPLEMENTED = format_status(http.HTTPStatus.NOT_IMPLEMENTED)
STATUS_BAD_GATEWAY = format_status(http.HTTPStatus.BAD_GATEWAY)
STATUS_SERVICE_UNAVAILABLE = format_status(http.HTTPStatus.SERVICE_UNAVAILABLE)
STATUS_GATEWAY_TIMEOUT = format_status(http.HTTPStatus.GATEWAY_TIMEOUT)


##


HEADER_CONTENT_TYPE = b'Content-Type'
HEADER_CONTENT_LENGTH = b'Content-Length'
HEADER_ACCEPT = b'Accept'

CONTENT_CHARSET_UTF8 = b'charset=utf-8'

CONTENT_TYPE_BYTES = b'application/octet-stream'

CONTENT_TYPE_FORM_URLENCODED = b'application/x-www-form-urlencoded'

CONTENT_TYPE_HTML = b'text/html'
CONTENT_TYPE_HTML_UTF8 = b'; '.join([CONTENT_TYPE_HTML, CONTENT_CHARSET_UTF8])

CONTENT_TYPE_ICON = b'image/x-icon'

CONTENT_TYPE_JSON = b'application/json'
CONTENT_TYPE_JSON_UTF8 = b'; '.join([CONTENT_TYPE_JSON, CONTENT_CHARSET_UTF8])

CONTENT_TYPE_PNG = b'image/png'

CONTENT_TYPE_TEXT = b'text/plain'
CONTENT_TYPE_TEXT_UTF8 = b'; '.join([CONTENT_TYPE_TEXT, CONTENT_CHARSET_UTF8])


##


HEADER_AUTH = b'Authorization'
BEARER_AUTH_HEADER_PREFIX = b'Bearer '
BASIC_AUTH_HEADER_PREFIX = b'Basic '


def format_bearer_auth_header(token: str | bytes) -> bytes:
    return BEARER_AUTH_HEADER_PREFIX + (token.encode('ascii') if isinstance(token, str) else token)


def format_basic_auth_header(username: str, password: str) -> bytes:
    return BASIC_AUTH_HEADER_PREFIX + base64.b64encode(':'.join([username, password]).encode())
