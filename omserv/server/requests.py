from .config import Config
from .events import Request


def valid_server_name(config: Config, request: Request) -> bool:
    if not config.server_names:
        return True

    host = ''
    for name, value in request.headers:
        if name.lower() == b'host':
            host = value.decode()
            break
    return host in config.server_names
