"""
TODO:
 - {sum,and}_nodes -> cls.new
"""
import abc
import math
import string
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import lang


##


def render_node(n: 'Node') -> str:
    if isinstance(n, Var):
        return n.name
    if isinstance(n, Num):
        return str(n.b)
    if isinstance(n, Op):
        return f'({render_node(n.a)}{n.glyph}{n.b})'
    if isinstance(n, Red):
        return f'({n.glyph.join(sorted(render_node(x) for x in n.nodes))})'
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
        return sum_nodes([self, b if isinstance(b, Node) else Num(b)])

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
    def __init__(self, b: int) -> None:
        super().__init__()
        self._b = check.isinstance(b, int)

    @property
    def b(self) -> int:
        return self._b

    @property
    def min(self) -> int:
        return self._b

    @property
    def max(self) -> int:
        return self._b


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


def sum_nodes(nodes: ta.Sequence[Node]) -> Node:
    news: ta.List[Node] = []
    sums: ta.List[Sum] = []
    nums: ta.List[Num] = []
    muls: ta.List[Mul] = []
    for node in nodes:
        if isinstance(node, Num):
            nums.append(node)
        elif isinstance(node, Mul):
            muls.append(node)
        elif isinstance(node, Sum):  # expand any sums inside one sum
            sums.append(node)
        else:
            news.append(node)

    # expand any sums inside one sum
    if sums:
        news.extend(nums)
        news.extend(muls)
        for x in sums:
            news += x.nodes
        return sum_nodes(news)

    # combine any numbers inside a sum
    if nums:
        news.append(Num(sum([x.b for x in nums])))

    # combine any Muls that factorize (big hack sticking the Mul(x, 1) on things)
    # FIXME: lol
    muls += [check.isinstance(Mul.new(x, 1), Mul) for x in news]
    mul_groups: ta.Dict[str, ta.Tuple[Node, ta.List[Mul]]] = {}
    for node in muls:  # NOTE can we somehow avoid rendering here?
        key = node.a.key
        try:
            t = mul_groups[key]
        except KeyError:
            l = []
        else:
            l = t[1]
        l.append(node)
        mul_groups[key] = (node.a, l)
    new_muls = [k * sum(x.b for x in g) for k, g in mul_groups.values()]
    news = [x if not isinstance(x, Mul) or x.b != 1 else x.a for x in new_muls]

    # filter 0s
    news = [x for x in news if x.min != 0 or x.max != 0]
    if len(news) > 1:
        return Sum.new(news)
    elif len(news) == 1:
        return news[0]
    else:
        return Num(0)


class Sum(Red):
    glyph = '+'

    @classmethod
    def calc_bounds(cls, nodes: ta.Sequence[Node]) -> ta.Tuple[int, int]:
        return sum(x.min for x in nodes), sum(x.max for x in nodes)

    def __mul__(self, b: int) -> Node:
        return sum_nodes([x * b for x in self.nodes])  # distribute mul into sum

    def _floordiv(self, b: int, factoring_allowed: bool = True) -> Node:
        if not factoring_allowed:
            return super()._floordiv(b, factoring_allowed)

        factors, tmp_nofactor = col.partition(self.nodes, lambda x: (isinstance(x, (Mul, Num))) and x.b % b == 0)

        # ugh, i doubt this is universally right
        nofactor: ta.List[Node] = []
        for x in tmp_nofactor:
            if isinstance(x, Num):
                if (x.b % b) != x.b:
                    factors.append(Num(x.b - (x.b % b)))  # python does floor division
                nofactor.append(Num(x.b % b))
            else:
                nofactor.append(x)

        gcd = [
            math.gcd(x.b, b) if isinstance(x, (Mul, Num)) else None
            for x in nofactor
        ]

        if len(factors) > 0:
            # these don't have to be the same, just having a common factor
            if len(gcd) > 0 and col.all_equal(gcd) and gcd[0] is not None and gcd[0] > 1:
                nofactor_term = sum_nodes([
                    (x.a * (x.b // gcd[0])) if isinstance(x, Mul) else Num(x.b // gcd[0])  # type: ignore  # FIXME: ??
                    for x in nofactor
                ]) // (b // gcd[0])
            else:
                nofactor_term = sum_nodes(nofactor) // b

            return sum_nodes([
                                 (x.a * (x.b // b)) if isinstance(x, Mul) else Num(x.b // b)  # type: ignore
                                 for x in factors
                             ] + [nofactor_term])

        muls = [x.b for x in nofactor if isinstance(x, Mul)]
        for m in muls:
            if m > 1 and b % m == 0:
                return (self // m) // (b // m)

        return super()._floordiv(b, factoring_allowed)

    def __mod__(self, b: int) -> Node:
        new_nodes: ta.List[Node] = []
        for x in self.nodes:
            if isinstance(x, Num):
                new_nodes.append(Num(x.b % b))
            elif isinstance(x, Mul):
                new_nodes.append(x.a * (x.b % b))
            else:
                new_nodes.append(x)
        return sum_nodes(new_nodes) % b


def and_nodes(nodes: ta.Sequence[Node]) -> Node:
    if any((x.min == 0 and x.max == 0) for x in nodes):
        return Num(0)

    # filter 1s
    nodes = [x for x in nodes if x.min != x.max]
    if len(nodes) > 1:
        return And.new(nodes)
    elif len(nodes) == 1:
        return nodes[0]
    else:
        return Num(1)


class And(Red):
    glyph = ' and '

    @classmethod
    def calc_bounds(cls, nodes: ta.Sequence[Node]) -> ta.Tuple[int, int]:
        return min(x.min for x in nodes), max(x.max for x in nodes)

    def __mul__(self, b: int) -> Node:
        return and_nodes([x * b for x in self.nodes])

    def _floordiv(self, b: int, factoring_allowed: bool = True) -> Node:
        return and_nodes([x // b for x in self.nodes])
