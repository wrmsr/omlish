import datetime
import subprocess

from .. import check
from .. import dataclasses as dc
from .. import json
from .. import lang
from .. import marshal as msh


@dc.dataclass(frozen=True)
class PsItem(lang.Final):
    dc.metadata(msh.DataclassMetadata(
        field_naming=msh.FieldNaming.CAMEL,
    ))

    command: str
    created_at: datetime.datetime
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


def cli_ps() -> list[PsItem]:
    p = subprocess.Popen(
        ['docker', 'ps', '--format', '{{json .}}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    o, _ = p.communicate()
    check.equal(p.returncode, 0)

    ret: list[PsItem] = []
    for l in o.decode('utf-8').splitlines():
        d = json.loads(o.decode('utf-8'))
        pi = msh.unmarshal(d, PsItem)
        ret.append(pi)

    return ret


def test_docker():
    pis = cli_ps()
    print(json.dumps_pretty(msh.marshal(pis, list[PsItem])))
