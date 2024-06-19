"""
TODO:
 - merged compose configs: https://github.com/wrmsr/bane/blob/27647abdcfb323b73e6982a5c318c7029496b203/core/dev/docker/compose.go#L38
"""  # noqa
import datetime
import re
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


def cli_cmd(args) -> bytes:
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    o, _ = p.communicate()
    check.equal(p.returncode, 0)
    return o


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
    o = cli_cmd([
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
    o = cli_cmd(['docker', 'inspect', *ids])
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
