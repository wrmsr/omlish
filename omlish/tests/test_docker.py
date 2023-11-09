import datetime
import subprocess
import json

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh


@dc.dataclass(frozen=True)
class PsItem(lang.Final):
    dc.metadata(msh.DataclassMetadata(
        field_naming=msh.FieldNaming.CAMEL,
    ))

    command: str
    created_at: datetime.datetime


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

    mr = msh.Registry()
    uf = msh.new_standard_unmarshaler_factory()
    uc = msh.UnmarshalContext(mr, factory=uf)
    pi = uc.make(PsItem).unmarshal(uc, d)

    print(pi)
