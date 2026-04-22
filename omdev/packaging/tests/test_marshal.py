from omlish import marshal as msh

from .. import marshal as _  # noqa
from ..requires import parse_requirement


def test_marshal():
    req = parse_requirement('foo == 0.1')
    print(req)
    print(msh.marshal(req))
