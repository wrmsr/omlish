import http  # noqa


def format_status(status: http.HTTPStatus) -> str:
    return '%d %s' % (int(status), status.phrase)


STATUS_OK = format_status(http.HTTPStatus.OK)
STATUS_BAD_REQUEST = format_status(http.HTTPStatus.BAD_REQUEST)
STATUS_FORBIDDEN = format_status(http.HTTPStatus.FORBIDDEN)
STATUS_NOT_FOUND = format_status(http.HTTPStatus.NOT_FOUND)
STATUS_METHOD_NOT_ALLOWED = format_status(http.HTTPStatus.METHOD_NOT_ALLOWED)


CONTENT_TYPE = 'Content-Type'
CONTENT_TEXT = 'text/plain'
CONTENT_JSON = 'application/json'
CONTENT_ICON = 'image/x-icon'
CONTENT_BYTES = 'application/octet-stream'
