import datetime
import subprocess
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import json
from .. import lang
from .. import marshal as msh


def cli_cmd(*args) -> bytes:
    p = subprocess.Popen(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    o, _ = p.communicate()
    check.equal(p.returncode, 0)
    return o


@dc.dataclass(frozen=True)
class PsItem(lang.Final):
    dc.metadata(msh.DataclassMetadata(
        field_naming=msh.FieldNaming.CAMEL,
        # unknown_field='x',
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

    # x: ta.Mapping[str, ta.Any] | None = None


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
    dc.metadata(msh.DataclassMetadata(
        field_naming=msh.FieldNaming.CAMEL,
        # unknown_field='x',
    ))

    id: str
    created: datetime.datetime

    # x: ta.Mapping[str, ta.Any] | None = None


def cli_inspect(ids: list[str]) -> list[Inspect]:
    o = cli_cmd(['docker', 'inspect', *ids])
    return msh.unmarshal(json.loads(o.decode()), list[Inspect])


def test_docker():
    pis = cli_ps()
    print(json.dumps_pretty(msh.marshal(pis, list[PsItem])))
    print(json.dumps_pretty(msh.marshal(pis)))

    iis = cli_inspect([pi.id for pi in pis])
    print(json.dumps_pretty(msh.marshal(iis, list[Inspect])))
