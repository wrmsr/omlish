import abc
import string
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang


##


def render_node(n: 'Node') -> str:
    if isinstance(n, Var):
        return n.name
    if isinstance(n, Num):
        return str(n.num)
    if isinstance(n, Op):
        return f'({render_node(n.a)}{n.glyph}{n.b})'
    raise TypeError(n)


##


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

    def __neg__(self) -> 'Node':
        return self * -1

    def __add__(self, b: ta.Union['Node', int]) -> 'Node':
        return Node.sum([self, b if isinstance(b, Node) else Num(b)])

    def __sub__(self, b: ta.Union['Node', int]) -> 'Node':
        return self + -b

    def __ge__(self, b: int) -> 'Node':
        return Ge.new(self, b)

    def __lt__(self, b: int) -> 'Node':
        return Lt.new(self, b)

    def __mul__(self, b: int) -> 'Node':
        if b == 0:
            return Num(0)
        elif b == 1:
            return self
        return Mul.new(self, b)

    def _floordiv(self, b: int, factoring_allowed: bool = True) -> 'Node':
        if b == 0:
            raise ValueError
        if b < 0:
            return (self // -b) * -1
        if b == 1:
            return self

        # the numerator of div is not allowed to be negative
        if self.min < 0:
            offset = self.min // b
            # factor out an "offset" to make the numerator positive. don't allowing factoring again
            return (self + -offset * b)._floordiv(b, factoring_allowed=False) + offset

        return Div.new(self, b)

    def __floordiv__(self, b: int) -> 'Node':
        return self._floordiv(b)

    def __mod__(self, b: int) -> 'Node':
        if b <= 0:
            raise ValueError
        if b == 1:
            return Num(0)
        if self.min >= 0 and self.max < b:
            return self
        if self.min < 0:
            return (self - ((self.min // b) * b)) % b
        return Mod.new(self, b)


##


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


##


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


##


class Op(Node, lang.Abstract):   # noqa

    def __init__(self, a: Node, b: int, *, _min: int, _max: int) -> None:
        super().__init__()
        self._a = check.isinstance(a, Node)
        self._b = check.isinstance(b, int)
        self._min = check.isinstance(_min, int)
        self._max = check.isinstance(_max, int)

    @property
    def a(self) -> Node:
        return self._a

    @property
    def b(self) -> int:
        return self._b

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    @classmethod
    def new(cls, a: Node, b: int) -> 'Node':
        mn, mx = cls.calc_bounds(a, b)
        if mn == mx:
            return Num(mn)
        return cls(a, b, _min=mn, _max=mx)

    glyph: ta.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        raise NotImplementedError


class Ge(Op):
    glyph = '>='

    @classmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        return int(a.min >= b), int(a.max >= b)

    def __mul__(self, b: int) -> Node:
        return (self.a * b) >= (self.b * b)

    def _floordiv(self, b: int, factoring_allowed: bool = True) -> Node:
        return (self.a // b) >= (self.b // b)


class Lt(Op):
    glyph = '<'

    @classmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        return int(a.max < b), int(a.min < b)

    def __mul__(self, b: int) -> Node:
        return (self.a * b) < (self.b * b)

    def _floordiv(self, b: int, factoring_allowed: bool = False) -> Node:
        return (self.a // b) < (self.b // b)


class Mul(Op):
    glyph = '*'

    @classmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        if b >= 0:
            return a.min * b, a.max * b
        else:
            return a.max * b, a.min * b

    def __mul__(self, b: int) -> Node:
        return self.a * (self.b * b)  # two muls in one mul

    def _floordiv(self, b: int, factoring_allowed: bool = False) -> Node:
        # NOTE: mod negative isn't handled right
        if self.b % b == 0:
            return self.a * (self.b // b)
        if b % self.b == 0 and self.b > 0:
            return self.a // (b // self.b)
        return super()._floordiv(b, factoring_allowed)

    def __mod__(self, b: int):
        a = self.a * (self.b % b)
        return a % b


class Div(Op):
    glyph = '//'

    @classmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        if a.min < 0:
            raise ValueError
        return a.min // b, a.max // b

    def _floordiv(self, b: int, factoring_allowed: bool = False) -> Node:
        return self.a // (self.b * b)  # two divs is one div


class Mod(Op):
    glyph = '%'

    @classmethod
    def calc_bounds(cls, a: Node, b: int) -> ta.Tuple[int, int]:
        if a.min < 0:
            raise ValueError
        if a.max - a.min >= b or (a.min != a.max and a.min % b >= a.max % b):
            return 0, b - 1
        else:
            return a.min % b, a.max % b

    def _floordiv(self, b: int, factoring_allowed: bool = True) -> Node:
        if self.b % b == 0:
            return (self.a // b) % (self.b // b)  # put the div inside mod
        return super()._floordiv(b, factoring_allowed)


##


class Red(Node, lang.Abstract):
    def __init__(self, nodes: ta.Sequence[Node], *, _min: int, _max: int) -> None:
        super().__init__()
        self._nodes = [check.isinstance(n, Node) for n in nodes]
        self._min = check.isinstance(_min, int)
        self._max = check.isinstance(_max, int)

    @property
    def nodes(self) -> ta.Sequence[Node]:
        return self._nodes

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    @classmethod
    def new(cls, nodes: ta.Sequence['Node']) -> 'Node':
        mn, mx = cls.calc_bounds(nodes)
        return cls(nodes, _min=mn, _max=mx)

    glyph: ta.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def calc_bounds(cls, nodes: ta.Sequence[Node]) -> ta.Tuple[int, int]:
        raise NotImplementedError


class Sum(Red):
    glyph = '+'

    @classmethod
    def calc_bounds(cls, nodes: ta.Sequence[Node]) -> ta.Tuple[int, int]:
        return sum(x.min for x in nodes), sum(x.max for x in nodes)


class And(Red):
    glyph = 'and '

    @classmethod
    def calc_bounds(cls, nodes: ta.Sequence[Node]) -> ta.Tuple[int, int]:
        return min(x.min for x in nodes), max(x.max for x in nodes)


##


def _test_variable(v, n, m, s):
    assert render_node(v) == s
    assert v.min == n
    assert v.max == m


def test_symbolic():
    idx1 = Var('idx1', 0, 3)
    idx2 = Var('idx2', 0, 3)
    assert idx1 == idx1
    assert idx1 != idx2


def test_ge():
    _test_variable(Var('a', 3, 8) >= 77, 0, 0, '0')
    _test_variable(Var('a', 3, 8) >= 9, 0, 0, '0')
    _test_variable(Var('a', 3, 8) >= 8, 0, 1, '(a>=8)')
    _test_variable(Var('a', 3, 8) >= 4, 0, 1, '(a>=4)')
    _test_variable(Var('a', 3, 8) >= 3, 1, 1, '1')
    _test_variable(Var('a', 3, 8) >= 2, 1, 1, '1')
