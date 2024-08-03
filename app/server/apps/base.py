import os

from omserv.apps.templates import j2_helper


def base_server_url() -> str:
    return os.environ.get('BASE_SERVER_URL', 'http://localhost:8000/')


@j2_helper
def url_for(s: str) -> str:
    return base_server_url() + s
