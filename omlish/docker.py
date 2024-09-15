"""
TODO:
 - merged compose configs: https://github.com/wrmsr/bane/blob/27647abdcfb323b73e6982a5c318c7029496b203/core/dev/docker/compose.go#L38
 - https://github.com/mag37/dockcheck/blob/3d122f2b868eb53a25a3014f0f6bd499390a3a29/dockcheck.sh
  - https://github.com/regclient/regclient
  - https://stackoverflow.com/questions/71409458/how-to-download-docker-image-using-http-api-using-docker-hub-credentials
  - https://stackoverflow.com/questions/55386202/how-can-i-use-the-docker-registry-api-to-pull-information-about-a-container-get
  - https://ops.tips/blog/inspecting-docker-image-without-pull/
  
"""  # noqa
import datetime
import os
import re
import shlex
import subprocess
import sys
import typing as ta
import urllib.request

from . import check
from . import dataclasses as dc
from . import lang
from . import marshal as msh
from .formats import json


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


##


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, unknown_field='x')
@msh.update_fields_metadata(['id'], name='ID')
class PsItem(lang.Final):
    command: str
    created_at: datetime.datetime
    id: str
    image: str
    labels: str
    local_volumes: str
    mounts: str
    names: str
    networks: str
    ports: str
    running_for: str
    size: str
    state: str
    status: str

    x: ta.Mapping[str, ta.Any] | None = None


class Port(ta.NamedTuple):
    ip: str
    from_port: int
    to_port: int
    proto: str


_PORT_PAT = re.compile(r'(?P<ip>[^:]+):(?P<from_port>\d+)->(?P<to_port>\d+)/(?P<proto>\w+)')


def parse_port(s: str) -> Port:
    # '0.0.0.0:35221->22/tcp, 0.0.0.0:35220->8000/tcp'
    m = check.not_none(_PORT_PAT.fullmatch(s))
    return Port(
        m.group('ip'),
        int(m.group('from_port')),
        int(m.group('to_port')),
        m.group('proto'),
    )


def cli_ps() -> list[PsItem]:
    o = subprocess.check_output([
        'docker',
        'ps',
        '--no-trunc',
        '--format', '{{json .}}',
    ])

    ret: list[PsItem] = []
    for l in o.decode().splitlines():
        d = json.loads(l)
        pi = msh.unmarshal(d, PsItem)
        ret.append(pi)

    return ret


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, unknown_field='x')
class Inspect(lang.Final):
    id: str
    created: datetime.datetime

    x: ta.Mapping[str, ta.Any] | None = None


def cli_inspect(ids: list[str]) -> list[Inspect]:
    o = subprocess.check_output(['docker', 'inspect', *ids])
    return msh.unmarshal(json.loads(o.decode()), list[Inspect])


##


class ComposeConfig:
    def __init__(
            self,
            prefix: str,
            *,
            file_path: str | None = None,
    ) -> None:
        super().__init__()

        self._prefix = prefix
        self._file_path = file_path

    @lang.cached_function
    def get_config(self) -> ta.Mapping[str, ta.Any]:
        with open(check.not_none(self._file_path)) as f:
            buf = f.read()
        return yaml.safe_load(buf)

    @lang.cached_function
    def get_services(self) -> ta.Mapping[str, ta.Any]:
        ret = {}
        for n, c in self.get_config()['services'].items():
            check.state(n.startswith(self._prefix))
            ret[n[len(self._prefix):]] = c

        return ret


def get_compose_port(cfg: ta.Mapping[str, ta.Any], default: int) -> int:
    return check.single(
        int(l)
        for p in cfg['ports']
        for l, r in [p.split(':')]
        if int(r) == default
    )


##


def timebomb_payload(delay_s: float, name: str = 'omlish-docker-timebomb') -> str:
    return (
        '('
        f'echo {shlex.quote(name)} && '
        f'sleep {delay_s:g} && '
        'sh -c \'killall5 -9 -o $PPID -o $$ ; kill 1\''
        ') &'
    )


##


DOCKER_FOR_MAC_HOSTNAME = 'docker.for.mac.localhost'


_LIKELY_IN_DOCKER_PATTERN = re.compile(r'^overlay / .*/docker/')


def is_likely_in_docker() -> bool:
    if sys.platform != 'linux':
        return False
    with open('/proc/mounts') as f:  # type: ignore
        ls = f.readlines()
    return any(_LIKELY_IN_DOCKER_PATTERN.match(l) for l in ls)


##


# Set by pyproject, docker-dev script
DOCKER_HOST_PLATFORM_KEY = 'DOCKER_HOST_PLATFORM'


def get_docker_host_platform() -> str | None:
    return os.environ.get(DOCKER_HOST_PLATFORM_KEY)


##


@dc.dataclass(frozen=True)
class HubRepoInfo:
    repo: str
    tags: ta.Mapping[str, ta.Any]
    latest_manifests: ta.Mapping[str, ta.Any]


def get_hub_repo_info(
        repo: str,
        *,
        auth_url: str = 'https://auth.docker.io/',
        api_url: str = 'https://registry-1.docker.io/v2/',
) -> HubRepoInfo:
    """
    https://stackoverflow.com/a/39376254

    ==

    repo=library/nginx
    token=$(
        curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${repo}:pull" \
        | jq -r '.token' \
    )
    curl -H "Authorization: Bearer $token" -s "https://registry-1.docker.io/v2/${repo}/tags/list" | jq
    curl \
        -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
        -H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
        -H "Authorization: Bearer $token" \
        -s "https://registry-1.docker.io/v2/${repo}/manifests/latest" \
    | jq .
    """

    auth_url = auth_url.rstrip('/')
    api_url = api_url.rstrip('/')

    #

    def req_json(url: str, **kwargs: ta.Any) -> ta.Any:
        with urllib.request.urlopen(urllib.request.Request(url, **kwargs)) as resp:  # noqa
            return json.loads(resp.read().decode('utf-8'))

    #

    token_dct = req_json(f'{auth_url}/token?service=registry.docker.io&scope=repository:{repo}:pull')
    token = token_dct['token']

    req_hdrs = {'Authorization': f'Bearer {token}'}

    #

    tags_dct = req_json(
        f'{api_url}/{repo}/tags/list',
        headers=req_hdrs,
    )

    latest_mani_dct = req_json(
        f'{api_url}/{repo}/manifests/latest',
        headers={
            **req_hdrs,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
        },
    )

    return HubRepoInfo(
        repo,
        tags_dct,
        latest_mani_dct,
    )
