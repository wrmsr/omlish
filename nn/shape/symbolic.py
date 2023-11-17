from __future__ import annotations

import abc
import functools
import itertools
import math
import typing as ta

from omlish import collections as col
from omlish import dispatch


# NOTE: Python has different behavior for negative mod and floor div than c
# symbolic matches the Python behavior, but the code output is agnostic, and will never have negative numbers in div or
# mod


def is_sym_int(x: ta.Any) -> bool:
    return isinstance(x, (int, Node))


ENFORCE_SYM_TRUTHY = False


class sym_truthy:  # noqa
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __new__(cls, v):  # noqa
        if isinstance(v, NumNode):
            v = v.b
        if isinstance(v, int):
            if v != 0:
                return cls.TRUE
            else:
                return cls.FALSE
        if isinstance(v, Node):
            return cls.UNKNOWN
        raise TypeError(v)

    def __init__(self, _):
        pass

    def __bool__(self):
        raise TypeError

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        if not isinstance(o, sym_truthy):
            raise TypeError(o)
        return self is o

    @classmethod
    def _new(cls, name):
        ret = object.__new__(cls)
        ret.name = name
        return ret

    TRUE: ta.Final[sym_truthy]  # noqa
    FALSE: ta.Final[sym_truthy]  # noqa
    UNKNOWN: ta.Final[sym_truthy]  # noqa

    @property
    def is_true(self):
        return self is sym_truthy.TRUE

    @property
    def is_not_true(self):
        return self is not sym_truthy.TRUE

    @property
    def is_false(self):
        return self is sym_truthy.FALSE

    @property
    def is_not_false(self):
        return self is not sym_truthy.FALSE

    @property
    def is_unknown(self):
        return self is sym_truthy.UNKNOWN


sym_truthy.TRUE: ta.Final[sym_truthy] = sym_truthy._new('truthy.TRUE')  # noqa
sym_truthy.FALSE: ta.Final[sym_truthy] = sym_truthy._new('truthy.FALSE')  # noqa
sym_truthy.UNKNOWN: ta.Final[sym_truthy] = sym_truthy._new('truthy.UNKNOWN')  # noqa


class Node:
    b: sint
    min: int
    max: int

    def render(self, ops=None, ctx=None) -> ta.Any:
        assert self.__class__ in (Variable, NumNode) or self.min != self.max
        if ops is None:
            if ctx == 'DEBUG':
                cls = DebugNodeRenderer
            elif ctx == 'REPR':
                cls = ReprNodeRenderer
            elif ctx is None:
                cls = NodeRenderer
            else:
                raise ValueError(ctx)
            return cls().render(self)
        else:
            return ops[type(self)](self, ops, ctx)

    def vars(self):
        return []

    def expand_idx(self) -> VariableOrNum:
        return next((v for v in self.vars() if v.expr is None), NumNode(0))

    # expand a Node into list[Node] that enumerates the underlying Variables from min to max
    # expand increments earlier variables faster than later variables (as specified in the argument)
    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def expand(self, idxs: ta.Optional[tuple[VariableOrNum, ...]] = None) -> list[Node]:
        if idxs is None:
            idxs = (self.expand_idx(),)
        return [
            self.substitute(dict(zip(idxs, (NumNode(x) for x in rep))))
            for rep in Node.iter_idxs(idxs)
        ]

    @staticmethod
    def iter_idxs(idxs: tuple[VariableOrNum, ...]) -> ta.Iterator[tuple[int, ...]]:
        yield from (
            x[::-1]
            for x in itertools.product(
                *[[x for x in range(v.min, v.max + 1)] for v in idxs[::-1]]
            )
        )

    # substitute Variables with the values in var_vals
    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        raise RuntimeError(self.__class__.__name__)

    def unbind(self) -> tuple[Node, ta.Optional[int]]:
        return self.substitute({v: v.unbind()[0] for v in self.vars() if v.val is not None}), None

    @functools.cached_property
    def key(self) -> str:
        return self.render(ctx="DEBUG")

    @functools.cached_property
    def hash(self) -> int:
        return hash(self.key)

    def __repr__(self):
        return self.render(ctx="REPR")

    def __str__(self):
        return "<" + self.key + ">"

    def __hash__(self):
        return self.hash

    def eqz(self):
        return not (self.max == self.min == 0)

    def __bool__(self):
        if ENFORCE_SYM_TRUTHY:
            raise TypeError
        return self.eqz()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.key == other.key

    def __neg__(self):
        return self * -1

    def __add__(self, b: sint):
        return Variable.sum([self, b if isinstance(b, Node) else Variable.num(b)])

    def __radd__(self, b: int):
        return self + b

    def __sub__(self, b: sint):
        return self + -b

    def __rsub__(self, b: int):
        return -self + b

    def __le__(self, b: sint):
        return self < (b + 1)

    def __gt__(self, b: sint):
        return (-self) < (-b)

    def __ge__(self, b: sint):
        return (-self) < (-b + 1)

    def __lt__(self, b: sint):
        return create_node(LtNode(self, b))

    def __mul__(self, b: sint):
        if b == 0:
            return NumNode(0)
        if b == 1:
            return self
        if self.__class__ is NumNode:
            return NumNode(self.b * b) if isinstance(b, int) else b * self.b
        return (
            create_node(MulNode(self, b.b))
            if isinstance(b, NumNode)
            else create_node(MulNode(self, b))
        )

    def __rmul__(self, b: int):
        return self * b

    # *** complex ops ***

    def __rfloordiv__(self, b: int):
        if self.min > b >= 0:
            return NumNode(0)
        if isinstance(self, NumNode):
            return NumNode(b // self.b)
        raise RuntimeError(f"not supported: {b} // {self}")

    def __floordiv__(self, b: sint, factoring_allowed=True):
        if isinstance(b, Node):
            if b.__class__ is NumNode:
                return self // b.b
            if self == b:
                return NumNode(1)
            if sym_truthy((b - self).min > 0).is_true and sym_truthy(self.min >= 0).is_true:
                return NumNode(0)  # b - self simplifies the node
            raise RuntimeError(f"not supported: {self} // {b}")
        assert b != 0
        if b < 0:
            return (self // -b) * -1
        if b == 1:
            return self

        # the numerator of div is not allowed to be negative
        if self.min < 0:
            offset = self.min // b
            # factor out an "offset" to make the numerator positive. don't allowing factoring again
            return (self + -offset * b).__floordiv__(
                b, factoring_allowed=False
            ) + offset
        return create_node(DivNode(self, b))

    def __rmod__(self, b: int):
        if self.min > b >= 0:
            return NumNode(b)
        if isinstance(self, NumNode):
            return NumNode(b % self.b)
        raise RuntimeError(f"not supported: {b} % {self}")

    def __mod__(self, b: sint):
        if isinstance(b, Node):
            if b.__class__ is NumNode:
                return self % b.b
            if self == b:
                return NumNode(0)
            if sym_truthy((b - self).min > 0).is_not_false and sym_truthy(self.min >= 0).is_not_false:
                return self  # b - self simplifies the node
            raise RuntimeError(f"not supported: {self} % {b}")
        assert b > 0
        if b == 1:
            return NumNode(0)
        if self.min >= 0 and self.max < b:
            return self
        if (self.min // b) == (self.max // b):
            return self - (b * (self.min // b))
        if self.min < 0:
            return (self - ((self.min // b) * b)) % b
        return create_node(ModNode(self, b))

    @staticmethod
    def num(num: int) -> NumNode:
        return NumNode(num)

    @staticmethod
    def factorize(nodes: list[Node]) -> list[Node]:
        mul_groups: dict[Node, int] = {}
        for x in nodes:
            a, b = (x.a, x.b) if isinstance(x, MulNode) else (x, 1)
            mul_groups[a] = mul_groups.get(a, 0) + b
        return [
            MulNode(a, b_sum) if b_sum != 1 else a
            for a, b_sum in mul_groups.items()
            if b_sum != 0
        ]

    @staticmethod
    def sum(nodes: list[Node]) -> Node:
        nodes = [x for x in nodes if sym_truthy(x.max).is_not_false or sym_truthy(x.min).is_not_false]
        if not nodes:
            return NumNode(0)
        if len(nodes) == 1:
            return nodes[0]

        new_nodes: list[Node] = []
        num_node_sum = 0
        for node in SumNode(nodes).flat_components:
            if node.__class__ is NumNode:
                num_node_sum += node.b
            else:
                new_nodes.append(node)

        if len(new_nodes) > 1 and len(
            set([x.a if isinstance(x, MulNode) else x for x in new_nodes])
        ) < len(new_nodes):
            new_nodes = Node.factorize(new_nodes)
        if num_node_sum:
            new_nodes.append(NumNode(num_node_sum))
        return (
            create_rednode(SumNode, new_nodes)
            if len(new_nodes) > 1
            else new_nodes[0]
            if len(new_nodes) == 1
            else NumNode(0)
        )

    @staticmethod
    def ands(nodes: list[Node]) -> Node:
        if not nodes:
            return NumNode(1)
        if len(nodes) == 1:
            return nodes[0]
        if any(sym_truthy(x).is_false for x in nodes):
            return NumNode(0)

        # filter 1s
        nodes = [x for x in nodes if x.min != x.max]
        return (
            create_rednode(AndNode, nodes)
            if len(nodes) > 1
            else (nodes[0] if len(nodes) == 1 else NumNode(1))
        )


# 4 basic node types


class Variable(Node):
    def __new__(cls, expr: ta.Optional[str], nmin: int, nmax: int):
        assert sym_truthy(nmin >= 0).is_not_false and sym_truthy(nmin <= nmax).is_not_false
        if nmin == nmax:
            return NumNode(nmin)
        return super().__new__(cls)

    def __init__(self, expr: ta.Optional[str], nmin: int, nmax: int) -> None:
        super().__init__()
        self.expr = expr
        self.min = nmin
        self.max = nmax
        self._val: ta.Optional[int] = None

    @property
    def val(self):
        assert self._val is not None, f"Variable isn't bound, can't access val of {self}"
        return self._val

    def bind(self, val):
        assert self._val is None and self.min <= val <= self.max, f"cannot bind {val} to {self}"
        self._val = val
        return self

    def unbind(self) -> tuple[Variable, int]:
        assert self.val is not None, f"cannot unbind {self}"
        return Variable(self.expr, self.min, self.max), self.val

    def vars(self):
        return [self]

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return var_vals[self] if self in var_vals else self


class NumNode(Node):
    def __init__(self, num: int) -> None:
        super().__init__()
        assert isinstance(num, int), f"{num} is not an int"
        self.b: int = num
        self.min = num
        self.max = num

    def bind(self, val):
        assert self.b == val, f"cannot bind {val} to {self}"
        return self

    def __eq__(self, other):
        return self.b == other

    def __hash__(self):
        return self.hash  # needed with __eq__ override

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return self


def create_node(ret: Node):
    assert (
        not sym_truthy(ret.min <= ret.max).is_false
    ), f"min greater than max! {ret.min} {ret.max} when creating {type(ret)} {ret}"
    if ret.min == ret.max:
        return NumNode(ret.min)
    return ret


class OpNode(Node):
    def __init__(self, a: Node, b: sint) -> None:
        super().__init__()
        self.a = a
        self.b = b
        self.min, self.max = self.get_bounds()

    def vars(self):
        return self.a.vars() + (self.b.vars() if isinstance(self.b, Node) else [])

    @abc.abstractmethod
    def get_bounds(self) -> tuple[int, int]:
        pass


class LtNode(OpNode):
    def __floordiv__(self, b: sint, _=False):
        return (self.a // b) < (self.b // b)

    def get_bounds(self) -> tuple[int, int]:
        if isinstance(self.b, int):
            return (
                (1, 1)
                if self.a.max < self.b
                else (0, 0)
                if self.a.min >= self.b
                else (0, 1)
            )
        return (
            (1, 1)
            if self.a.max < self.b.min
            else (0, 0)
            if self.a.min >= self.b.max
            else (0, 1)
        )

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return self.a.substitute(var_vals) < (
            self.b if isinstance(self.b, int) else self.b.substitute(var_vals)
        )


class MulNode(OpNode):
    def __lt__(self, b: sint):
        if isinstance(b, Node) or isinstance(self.b, Node) or self.b == -1:
            return Node.__lt__(self, b)
        sgn = 1 if self.b > 0 else -1
        return Node.__lt__(self.a*sgn, (b + abs(self.b) - 1)//abs(self.b))

    def __mul__(self, b: sint):
        return self.a * (self.b * b)  # two muls in one mul

    def __floordiv__(
        self, b: sint, factoring_allowed=False
    ):  # NOTE: mod negative isn't handled right
        if self.b % b == 0:
            return self.a * (self.b // b)
        if b % self.b == 0 and self.b > 0:
            return self.a // (b // self.b)
        return Node.__floordiv__(self, b, factoring_allowed)

    def __mod__(self, b: sint):
        a = self.a * (self.b % b)
        return Node.__mod__(a, b)

    def get_bounds(self) -> tuple[int, int]:
        return (
            (self.a.min * self.b, self.a.max * self.b)
            if sym_truthy(self.b >= 0).is_true
            else (self.a.max * self.b, self.a.min * self.b)
        )

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return self.a.substitute(var_vals) * (
            self.b if isinstance(self.b, int) else self.b.substitute(var_vals)
        )


class DivNode(OpNode):
    def __floordiv__(self, b: sint, _=False):
        return self.a // (self.b * b)  # two divs is one div

    def get_bounds(self) -> tuple[int, int]:
        assert self.a.min >= 0 and isinstance(self.b, int)
        return self.a.min // self.b, self.a.max // self.b

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return self.a.substitute(var_vals) // self.b


class ModNode(OpNode):
    def __mod__(self, b: sint):
        if isinstance(b, Node) or isinstance(self.b, Node):
            return Node.__mod__(self, b)
        return self.a % b if math.gcd(self.b, b) == b else Node.__mod__(self, b)

    def __floordiv__(self, b: sint, factoring_allowed=True):
        if self.b % b == 0:
            return (self.a // b) % (self.b // b)  # put the div inside mod
        return Node.__floordiv__(self, b, factoring_allowed)

    def get_bounds(self) -> tuple[int, int]:
        assert self.a.min >= 0 and isinstance(self.b, int)
        return (
            (0, self.b - 1)
            if self.a.max - self.a.min >= self.b
            or (self.a.min != self.a.max and self.a.min % self.b >= self.a.max % self.b)
            else (self.a.min % self.b, self.a.max % self.b)
        )

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return self.a.substitute(var_vals) % self.b


class RedNode(Node):
    def __init__(self, nodes: list[Node]) -> None:
        super().__init__()
        self.nodes = nodes

    def vars(self):
        return functools.reduce(lambda l, x: l + x.vars(), self.nodes, [])


class SumNode(RedNode):
    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def __mul__(self, b: sint):
        return Node.sum([x * b for x in self.nodes])  # distribute mul into sum

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def __floordiv__(self, b: sint, factoring_allowed=True):
        fully_divided: list[Node] = []
        rest: list[Node] = []
        if isinstance(b, SumNode):
            nu_num = sum(node.b for node in self.flat_components if node.__class__ is NumNode)
            de_num = sum(node.b for node in b.flat_components if node.__class__ is NumNode)
            if nu_num > 0 and de_num and (d := nu_num // de_num) > 0:
                return NumNode(d) + (self - b * d) // b
        if isinstance(b, Node):
            for x in self.flat_components:
                if x % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
            if (sum_fully_divided := create_rednode(SumNode, fully_divided)) != 0:
                return sum_fully_divided + create_rednode(SumNode, rest) // b
            return Node.__floordiv__(self, b, False)
        if b == 1:
            return self
        if not factoring_allowed:
            return Node.__floordiv__(self, b, factoring_allowed)
        fully_divided, rest = [], []
        _gcd = b
        divisor = 1
        for x in self.flat_components:
            if x.__class__ in (NumNode, MulNode):
                if x.b % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
                    if isinstance(x.b, int):
                        _gcd = math.gcd(_gcd, x.b)
                        if x.__class__ == MulNode and divisor == 1 and b % x.b == 0:
                            divisor = x.b
                    else:
                        _gcd = 1
            else:
                rest.append(x)
                _gcd = 1
        if _gcd > 1:
            return Node.sum(fully_divided) + Node.sum(rest).__floordiv__(_gcd) // (b // _gcd)
        if divisor > 1:
            return Node.sum(fully_divided) + Node.sum(rest).__floordiv__(divisor) // (b // divisor)
        return Node.sum(fully_divided) + Node.__floordiv__(Node.sum(rest), b)

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def __mod__(self, b: sint):
        if isinstance(b, SumNode):
            nu_num = sum(node.b for node in self.flat_components if node.__class__ is NumNode)
            de_num = sum(node.b for node in b.flat_components if node.__class__ is NumNode)
            if nu_num > 0 and de_num and (d := nu_num // de_num) > 0:
                return (self - b * d) % b
        if isinstance(b, Node) and (b - self).min > 0:
            return self  # b - self simplifies the node
        new_nodes: list[Node] = []
        for x in self.nodes:
            if x.__class__ is NumNode:
                new_nodes.append(Variable.num(x.b % b))
            elif isinstance(x, MulNode):
                new_nodes.append(x.a * (x.b % b))
            else:
                new_nodes.append(x)
        return Node.__mod__(Node.sum(new_nodes), b)

    def __lt__(self, b: sint):
        lhs: Node = self
        if isinstance(b, int):
            new_sum = []
            for x in self.nodes:
                # TODO: should we just force the last one to always be the number
                if isinstance(x, NumNode):
                    b -= x.b
                else:
                    new_sum.append(x)
            lhs = Node.sum(new_sum)
            nodes = lhs.nodes if isinstance(lhs, SumNode) else [lhs]
            muls, others = col.partition(nodes, lambda x: isinstance(x, MulNode) and x.b > 0 and x.max >= b)
            if muls:
                # NOTE: gcd in python 3.8 takes exactly 2 args
                mul_gcd = b
                for x in muls:
                    mul_gcd = math.gcd(mul_gcd, x.b)  # type: ignore  # mypy cannot tell x.b is int here
                all_others = Variable.sum(others)
                if all_others.min >= 0 and all_others.max < mul_gcd:
                    lhs, b = Variable.sum([mul // mul_gcd for mul in muls]), b // mul_gcd
        return Node.__lt__(lhs, b)

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        return Variable.sum([node.substitute(var_vals) for node in self.nodes])

    @property
    def flat_components(self):  # recursively expand sumnode components
        new_nodes = []
        for x in self.nodes:
            new_nodes += x.flat_components if isinstance(x, SumNode) else [x]
        return new_nodes


class AndNode(RedNode):
    def __floordiv__(self, b: sint, _=True):
        return Variable.ands([x // b for x in self.nodes])

    def substitute(self, var_vals: dict[VariableOrNum, Node]) -> Node:
        subed = []
        for node in self.nodes:
            if not (sub := node.substitute(var_vals)):
                return NumNode(0)
            subed.append(sub)
        return Variable.ands(subed)


def create_rednode(typ: type[RedNode], nodes: list[Node]):
    ret = typ(nodes)
    if typ == SumNode:
        ret.min, ret.max = (sum([x.min for x in nodes]), sum([x.max for x in nodes]))
    elif typ == AndNode:
        ret.min, ret.max = (min([x.min for x in nodes]), max([x.max for x in nodes]))
    return create_node(ret)


@functools.lru_cache(maxsize=None)
def sym_rename(s) -> str:
    return f"s{sym_rename.cache_info().currsize}"


def sym_render(a: sint, ops=None, ctx=None) -> str:
    return str(a) if isinstance(a, int) else a.render(ops, ctx)


def sym_infer(a: sint, var_vals: dict[Variable, int]) -> int:
    if isinstance(a, (int, float)):
        return a
    ret = a.substitute({k: Variable.num(v) for k, v in var_vals.items()})
    assert isinstance(ret, NumNode), f"sym_infer didn't produce NumNode from {a} with {var_vals}"
    return ret.b


# symbolic int
sint = ta.Union[Node, int]
VariableOrNum = ta.Union[Variable, NumNode]


##


class NodeRenderer:

    @dispatch.method
    def render(self, n: sint) -> str:
        raise TypeError(n)

    @render.register
    def render_int(self, n: int) -> str:
        return str(n)

    @render.register
    def render_variable(self, n: Variable) -> str:
        return f"{n.expr}"

    @render.register
    def render_num(self, n: NumNode) -> str:
        return f"{n.b}"

    @render.register
    def render_mul(self, n: MulNode) -> str:
        return f"({self.render(n.a)}*{self.render(n.b)})"

    @render.register
    def render_div(self, n: DivNode) -> str:
        return f"({self.render(n.a)}//{n.b})"

    @render.register
    def render_mod(self, n: ModNode) -> str:
        return f"({self.render(n.a)}%{n.b})"

    @render.register
    def render_lt(self, n: LtNode) -> str:
        return f"({self.render(n.a)}<{self.render(n.b)})"

    @render.register
    def render_sum(self, n: SumNode) -> str:
        return f"({'+'.join(sorted([self.render(x) for x in n.nodes]))})"

    @render.register
    def render_and(self, n: AndNode) -> str:
        return f"({' and '.join(sorted([self.render(x) for x in n.nodes]))})"


class DebugNodeRenderer(NodeRenderer):

    @NodeRenderer.render.register
    def render_variable(self, n: Variable) -> str:
        return f"{n.expr}[{n.min}-{n.max}{'=' + str(n.val) if n._val is not None else ''}]"


class ReprNodeRenderer(NodeRenderer):

    @NodeRenderer.render.register
    def render_variable(self, n: Variable) -> str:
        return f"Variable('{n.expr}', {n.min}, {n.max})" + (f".bind({n.val})" if n._val is not None else '')

    @NodeRenderer.render.register
    def render_num(self, n: NumNode) -> str:
        return f"NumNode({n.b})"
