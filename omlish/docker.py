"""
TODO:
 - merged compose configs: https://github.com/wrmsr/bane/blob/27647abdcfb323b73e6982a5c318c7029496b203/core/dev/docker/compose.go#L38
 - https://github.com/mag37/dockcheck/blob/3d122f2b868eb53a25a3014f0f6bd499390a3a29/dockcheck.sh
  - https://github.com/regclient/regclient
  - https://stackoverflow.com/questions/71409458/how-to-download-docker-image-using-http-api-using-docker-hub-credentials
  - https://stackoverflow.com/questions/55386202/how-can-i-use-the-docker-registry-api-to-pull-information-about-a-container-get
  - https://ops.tips/blog/inspecting-docker-image-without-pull/
  
repo=library/nginx
token=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${repo}:pull" | jq -r '.token')
curl -H "Authorization: Bearer $token" -s "https://registry-1.docker.io/v2/${repo}/tags/list" | jq
api="application/vnd.docker.distribution.manifest.v2+json"
apil="application/vnd.docker.distribution.manifest.list.v2+json"
curl -H "Accept: ${api}" -H "Accept: ${apil}" -H "Authorization: Bearer $token" -s "https://registry-1.docker.io/v2/${repo}/manifests/latest" | jq .
"""  # noqa
import datetime
import re
import shlex
import subprocess
import typing as ta

from . import check
from . import dataclasses as dc
from . import json
from . import lang
from . import marshal as msh

if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


@dc.dataclass(frozen=True)
class PsItem(lang.Final):
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.CAMEL,
        unknown_field='x',
    ))

    command: str
    created_at: datetime.datetime
    id: str = dc.field(metadata={msh.FieldMetadata: msh.FieldMetadata(name='ID')})
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
class Inspect(lang.Final):
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.CAMEL,
        unknown_field='x',
    ))

    id: str
    created: datetime.datetime

    x: ta.Mapping[str, ta.Any] | None = None


def cli_inspect(ids: list[str]) -> list[Inspect]:
    o = subprocess.check_output(['docker', 'inspect', *ids])
    return msh.unmarshal(json.loads(o.decode()), list[Inspect])


class ComposeConfig:
    def __init__(
            self,
            prefix: str,
            *,
            compose_path: str | None = None,
    ) -> None:
        super().__init__()

        self._prefix = prefix
        self._compose_path = compose_path

    @lang.cached_function
    def get_config(self) -> ta.Mapping[str, ta.Any]:
        with open(check.not_none(self._compose_path), 'r') as f:
            buf = f.read()
        dct = yaml.safe_load(buf)

        ret = {}
        for n, c in dct['services'].items():
            check.state(n.startswith(self._prefix))
            ret[n[len(self._prefix):]] = c

        return ret


def timebomb_payload(delay_s: int | float, name: str = 'omlish-timebomb') -> str:
    return (
        '('
        f'echo {shlex.quote(name)} && '
        f'sleep {delay_s:g} && '
        'sh -c \'killall5 -9 -o $PPID -o $$ ; kill 1\''
        ') &'
    )
