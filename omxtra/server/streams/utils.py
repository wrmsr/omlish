import typing as ta

from omlish.logs import all as logs

from ..config import Config
from ..events import Request
from ..types import Scope


log = logs.get_module_logger(globals())


##


def valid_server_name(config: Config, request: Request) -> bool:
    if not config.server_names:
        return True

    host = ''
    for name, value in request.headers:
        if name.lower() == b'host':
            host = value.decode()
            break
    return host in config.server_names


def build_and_validate_headers(headers: ta.Iterable[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    # Validates that the header name and value are bytes
    validated_headers: list[tuple[bytes, bytes]] = []
    for name, value in headers:
        if name[0] == b':'[0]:
            raise ValueError('Pseudo headers are not valid')
        validated_headers.append((bytes(name).strip(), bytes(value).strip()))
    return validated_headers


def suppress_body(method: str, status_code: int) -> bool:
    return method == 'HEAD' or 100 <= status_code < 200 or status_code in {204, 304}


class ResponseSummary(ta.TypedDict):
    status: int
    headers: ta.Iterable[tuple[bytes, bytes]]


def log_access(
        config: Config,
        request: 'Scope',
        response: ta.Optional['ResponseSummary'],
        request_time: float,
) -> None:
    # if self.access_logger is not None:
    #     self.access_logger.info(
    #         self.access_log_format, self.atoms(request, response, request_time)
    #     )
    log.info('access: %r %r', request, response)
