import abc
import string
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang


def render_node(n: 'Node') -> str:
    if isinstance(n, Var):
        return n.name
    if isinstance(n, Num):
        return str(n.num)
    raise TypeError(n)


class Node(lang.Abstract, lang.Sealed):

    @property
    @abc.abstractmethod
    def min(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def max(self) -> int:
        raise NotImplementedError

    @cached.property
    def key(self) -> str:
        return render_node(self)

    def __eq__(self, other: ta.Any) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.key == other.key


class Var(Node, lang.Final):
    _name_first_set: ta.Final[ta.AbstractSet[str]] = frozenset(string.ascii_letters + '_')
    _name_rest_set: ta.Final[ta.AbstractSet[str]] = frozenset([*_name_first_set, *string.digits])

    def __init__(self, name: str, min: int, max: int) -> None:
        if min < 0 or min >= max:
            raise ValueError(f'Invalid var range: {name!r} {min} {max}')
        if name[0] not in Var._name_first_set or frozenset(name[1:]) - Var._name_rest_set:
            raise ValueError(f'Invalid var name: {name!r} {min} {max}')
        super().__init__()
        self._name = check.non_empty_str(name)
        self._min = check.isinstance(min, int)
        self._max = check.isinstance(max, int)

    @property
    def name(self) -> str:
        return self._name

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max


class Num(Node, lang.Final):
    def __init__(self, num: int) -> None:
        super().__init__()
        self._num = check.isinstance(num, int)

    @property
    def num(self) -> int:
        return self._num

    @property
    def min(self) -> int:
        return self._num

    @property
    def max(self) -> int:
        return self._num


# class Op(Node, lang.Abstract):
#     pass
#
#
# class Red(Node, lang.Abstract):
#     pass


def _test_variable(v, n, m, s):
    assert v.render() == s
    assert v.min == n
    assert v.max == m


def test_symbolic():
    idx1 = Var('idx1', 0, 3)
    idx2 = Var('idx2', 0, 3)
    assert idx1 == idx1
    assert idx1 != idx2
