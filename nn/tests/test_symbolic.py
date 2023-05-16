from omlish import lang


class Node(lang.Abstract, lang.Sealed):
    pass


class Var(Node, lang.Final):
    pass


class Num(Node, lang.Final):
    pass


class Op(Node, lang.Abstract):
    pass


class Red(Node, lang.Abstract):
    pass


def test_symbolic():
    pass
