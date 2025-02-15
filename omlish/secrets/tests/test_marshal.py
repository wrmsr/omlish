from ... import dataclasses as dc
from ... import marshal as msh
from ..secrets import SecretRef


@dc.dataclass(frozen=True)
class Cred:
    username: str
    password: str | SecretRef


def test_secrets():
    print()
    for c0 in [
        Cred('u', 'p'),
        Cred('u', SecretRef('p')),
    ]:
        print(c0)
        cm = msh.marshal(c0)
        print(cm)
        c1 = msh.unmarshal(cm, Cred)
        print(c1)
        print()
