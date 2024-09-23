import logging
import os

from omdev.secrets import load_secrets
from omlish import check
from omlish import inject as inj
from omlish import secrets as sec


log = logging.getLogger(__name__)


##


def get_secret_db_url() -> str:
    cfg = load_secrets()
    return f'postgresql+asyncpg://{cfg["postgres_user"]}:{cfg["postgres_pass"]}@{cfg["postgres_host"]}:5432'


def get_docker_db_url() -> str:
    from omlish import docker
    cc = docker.ComposeConfig('omlish-', file_path='docker/compose.yml')
    svc = cc.get_services()['postgres']
    port = docker.get_compose_port(svc, 5432)
    env = svc['environment']
    return f'postgresql+asyncpg://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@127.0.0.1:{port}'


def get_db_url() -> str:
    if os.environ.get('PROD', '').lower() in ('1', 'true'):  # FIXME: lol
        return get_secret_db_url()
    else:
        return get_docker_db_url()


##


def bind_secrets() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(sec.Secrets, to_fn=lambda: sec.LoggingSecrets(sec.MappingSecrets({
            'session_secret_key': 'secret-key-goes-here',  # noqa
            'db_url': check.not_none(get_db_url()),

            'sd_auth_token': os.environ.get('SD_AUTH_TOKEN', ''),
            'sd2_url': os.environ.get('SD2_URL', ''),
        })), singleton=True),
    )
