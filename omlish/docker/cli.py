"""
TODO:
 - https://github.com/mag37/dockcheck/blob/3d122f2b868eb53a25a3014f0f6bd499390a3a29/dockcheck.sh
  - https://github.com/regclient/regclient
  - https://stackoverflow.com/questions/71409458/how-to-download-docker-image-using-http-api-using-docker-hub-credentials
  - https://stackoverflow.com/questions/55386202/how-can-i-use-the-docker-registry-api-to-pull-information-about-a-container-get
  - https://ops.tips/blog/inspecting-docker-image-without-pull/
"""  # noqa
import datetime
import re
import subprocess
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from ..formats import json


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


def has_cli() -> bool:
    try:
        proc = subprocess.run(['docker', '--version'])  # noqa
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    else:
        return not proc.returncode
