import os

from .secrets import load_secrets  # noqa


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
