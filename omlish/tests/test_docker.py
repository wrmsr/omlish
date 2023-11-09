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


def test_docker():
    p = subprocess.Popen(
        ['docker', 'ps', '--format', '{{json .}}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    o, e = p.communicate()
    check.equal(p.returncode, 0)
    print(o)
    print(e)

    d = json.loads(o.decode('utf-8'))
    print(d)

    pi = msh.unmarshal(d, PsItem)

    print(pi)

    print(json.dumps_pretty(msh.marshal(pi)))
