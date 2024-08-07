from ... import dataclasses as dc
from ... import marshal as msh
from ..marshal import marshal_secret_field
from ..secrets import Secret


@dc.dataclass(frozen=True)
class Cred:
    username: str
    password: str | Secret = dc.field() | marshal_secret_field


def test_secrets():
    print()
    for c0 in [
        Cred('u', 'p'),
        Cred('u', Secret('p')),
    ]:
        print(c0)
        cm = msh.marshal(c0)
        print(cm)
        c1 = msh.unmarshal(cm, Cred)
        print(c1)
        print()
