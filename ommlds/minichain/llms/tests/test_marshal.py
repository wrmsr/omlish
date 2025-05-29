from omlish import marshal as msh

from ..tokens import Tokens


def test_marshal_tokens():
    tks = Tokens([1, 2, 3])
    mtks = msh.marshal(tks)
    print(mtks)
