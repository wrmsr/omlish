import time
import wsgiref.handlers

from .config import Config


##


def _now() -> float:
    return time.time()


def response_headers(config: Config, protocol: str) -> list[tuple[bytes, bytes]]:
    headers = []
    if config.include_date_header:
        headers.append((b'date', wsgiref.handlers.format_date_time(_now()).encode('ascii')))
    if config.include_server_header:
        headers.append((b'server', f'omlicorn-{protocol}'.encode('ascii')))

    for alt_svc_header in config.alt_svc_headers:
        headers.append((b'alt-svc', alt_svc_header.encode()))

    return headers


def filter_pseudo_headers(headers: list[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    filtered_headers: list[tuple[bytes, bytes]] = [(b'host', b'')]  # Placeholder
    authority = None
    host = b''
    for name, value in headers:
        if name == b':authority':  # h2 & h3 libraries validate this is present
            authority = value
        elif name == b'host':
            host = value
        elif name[0] != b':'[0]:
            filtered_headers.append((name, value))
    filtered_headers[0] = (b'host', authority if authority is not None else host)
    return filtered_headers
