from omlish import marshal as msh

from ..configs import ModelRepo
from ..configs import ModelSpecifier


def test_marshal():
    mr = ModelRepo('foo', 'bar')
    m = msh.marshal(mr, ModelSpecifier)
    print(m)
