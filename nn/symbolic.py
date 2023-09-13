"""
TODO:
 - {sum,and}_syms -> cls.new
 - *** NEED BOUNDS ON KEY?
  - sdm
"""
import abc
import itertools
import math
import string
import typing as ta

from omlish import cached
from omlish import check
from omlish import dispatch
from omlish import collections as col
from omlish import lang


SymInt: ta.TypeAlias = ta.Union['Sym', int]


def is_sym_int(o: ta.Any) -> bool:
    return isinstance(o, (Sym, int))


def check_sym_int(o: ta.Any) -> SymInt:
    return check.isinstance(o, (Sym, int))


##


class SymRenderer:
    @dispatch.method
    def render(self, n: SymInt) -> str:
        raise TypeError(n)

    @render.register
    def render_int(self, n: int) -> str:
        return str(n)

    @render.register
    def render_var(self, n: 'Var') -> str:
        return n.name

    @render.register
    def render_num(self, n: 'Num') -> str:
        return str(n.b)

    @render.register
    def render_op(self, n: 'Op') -> str:
        return f'({self.render(n.a)}{n.glyph}{self.render(n.b)})'

    @render.register
    def render_red(self, n: 'Red') -> str:
        return f'({n.glyph.join(sorted(self.render(x) for x in n.syms))})'


def render(n: SymInt) -> str:
    return SymRenderer().render(n)


class DebugSymRenderer(SymRenderer):
    @SymRenderer.render.register
    def render_var(self, n: 'Var') -> str:
        return f'{n.name if n.name is not None else "?"}[{n.min},{n.max}]'


##


def truthy(s: SymInt) -> ta.Optional[bool]:
    if isinstance(s, (int, Num)):
        return s != 0
    if isinstance(s, Sym):
        return None
    raise TypeError(s)


class Sym(lang.Abstract, lang.Sealed):
    def __init__(self) -> None:
        super().__init__()
        if truthy(self.min > self.max):
            raise ValueError
        if self.min == self.max and not isinstance(self, Num):
            raise ValueError

    @property
    @abc.abstractmethod
    def min(self) -> SymInt:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def max(self) -> SymInt:
        raise NotImplementedError

    @cached.property
    def expr(self) -> str:
        return SymRenderer().render(self)

    @cached.property
    def debug(self) -> str:
        return DebugSymRenderer().render(self)

    def vars(self) -> ta.Iterator['Var']:
        return
        yield  # type: ignore  # noqa

    @cached.property
    def key(self) -> str:
        return self.debug

    def __repr__(self) -> str:
        return f'<{self.debug}>'

    def __hash__(self) -> int:
        return hash(self.key)

    def eqz(self) -> SymInt:
        return not (self.max == self.min == 0)

    def __bool__(self) -> bool:  # FIXME:
        # raise TypeError(self)  # FIXME:
        return self.eqz()

    def __eq__(self, other: ta.Any) -> bool:
        if not isinstance(other, Sym):
            return NotImplemented
        return self.key == other.key

    def __neg__(self) -> 'Sym':
        return self * -1

    def __add__(self, b: SymInt) -> 'Sym':
        return sum_([self, b if isinstance(b, Sym) else Num(b)])

    def __radd__(self, b: int) -> 'Sym':
        return self + b

    def __sub__(self, b: SymInt) -> 'Sym':
        return self + -b

    def __rsub__(self, b: int) -> 'Sym':
        return -self + b

    def __le__(self, b: SymInt) -> 'Sym':
        return self < (b + 1)

    def __gt__(self, b: SymInt) -> 'Sym':
        return (-self) < (-b)

    def __ge__(self, b: SymInt) -> 'Sym':
        return Lt.new(-self, -b + 1)

    def __lt__(self, b: SymInt) -> 'Sym':
        return Lt.new(self, b)

    def __mul__(self, b: SymInt) -> 'Sym':
        if b == 0:
            return Num(0)
        if b == 1:
            return self
        if isinstance(self, Num):
            if isinstance(b, int):
                return Num(self.b * b)
            return b * self.b
        if isinstance(b, Num):
            return Mul.new(self, b.b)
        return Mul.new(self, b)

    def __rmul__(self, b: SymInt) -> 'Sym':
        return self * b

    def __rfloordiv__(self, b: int) -> 'Sym':
        if self.min > b >= 0:
            return Num(0)
        if isinstance(self, Num):
            return Num(b // self.b)
        raise TypeError(f'Not supported: {b} // {self}')

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> 'Sym':
        if isinstance(b, Sym):
            if isinstance(b, Num):
                return self // b.b
            if self == b:
                return Num(1)
            if (b - self).min > 0 and self.min >= 0:
                return Num(0)
            raise TypeError(f'Not supported: {self} // {b}')

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

    def __floordiv__(self, b: SymInt) -> 'Sym':
        return self._floordiv(b)

    def __rmod__(self, b: int) -> 'Sym':
        if self.min > b >= 0:
            return Num(b)
        if isinstance(self, Num):
            return Num(b % self.b)
        raise TypeError(f'Not supported: {b} % {self}')

    def __mod__(self, b: SymInt) -> 'Sym':
        if isinstance(b, Sym):
            if isinstance(b, Num):
                return self % b.b
            if self == b:
                return Num(0)
            if (b - self).min > 0 and self.min >= 0:
                return self  # b - self simplifies the sym
            raise TypeError(f'Not supported: {self} % {b}')
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


def var(name: ta.Optional[str], min: SymInt, max: SymInt) -> Sym:
    if name is not None:
        if not name or name[0] not in Var._name_first_set or frozenset(name[1:]) - Var._name_rest_set:
            raise ValueError(f'Invalid var name: {name!r} {min} {max}')
    if isinstance(min, int) and isinstance(max, int) and min == max:
        return Num(min)
    return Var(name, min, max)


class Var(Sym, lang.Final):
    _name_first_set: ta.Final[ta.AbstractSet[str]] = frozenset(string.ascii_letters + '_')
    _name_rest_set: ta.Final[ta.AbstractSet[str]] = frozenset([*_name_first_set, *string.digits])

    def __init__(self, name: ta.Optional[str], min: SymInt, max: SymInt) -> None:
        check_sym_int(min)
        check_sym_int(max)
        if truthy(min < 0) or truthy(min >= max):
            raise ValueError(f'Invalid var range: {name!r} {min} {max}')
        if name is not None:
            if not name or name[0] not in Var._name_first_set or frozenset(name[1:]) - Var._name_rest_set:
                raise ValueError(f'Invalid var name: {name!r} {min} {max}')
        self._name = name
        self._min = min
        self._max = max
        super().__init__()

    @property
    def name(self) -> str:
        return self._name

    @property
    def min(self) -> SymInt:
        return self._min

    @property
    def max(self) -> SymInt:
        return self._max

    def vars(self) -> ta.Iterator['Var']:
        yield self


##


class Num(Sym, lang.Final):
    def __init__(self, b: int) -> None:
        self._b = check.isinstance(b, int)
        super().__init__()

    def __eq__(self, other: ta.Any) -> bool:
        return self.b == other

    def __hash__(self) -> int:
        return super().__hash__()

    def __int__(self) -> int:
        return self._b

    def __index__(self) -> int:
        return self.b

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


class Op(Sym, lang.Abstract):   # noqa
    def __init__(self, a: Sym, b: SymInt, *, _min: SymInt, _max: SymInt) -> None:
        self._a = check.isinstance(a, Sym)
        self._b = check_sym_int(b)
        self._min = check_sym_int(_min)
        self._max = check_sym_int(_max)
        super().__init__()

    @property
    def a(self) -> Sym:
        return self._a

    @property
    def b(self) -> SymInt:
        return self._b

    @property
    def min(self) -> SymInt:
        return self._min

    @property
    def max(self) -> SymInt:
        return self._max

    @classmethod
    def new(cls, a: Sym, b: SymInt) -> Sym:
        mn, mx = cls.calc_bounds(a, b)
        if mn == mx:
            return Num(mn)
        return cls(a, b, _min=mn, _max=mx)

    glyph: ta.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[SymInt, SymInt]:
        raise NotImplementedError

    def vars(self) -> ta.Iterator[Var]:
        yield from self._a.vars()
        if isinstance(self._b, Sym):
            yield from self._b.vars()


class Lt(Op):
    glyph = '<'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[SymInt, SymInt]:
        # return int(a.max < b), int(a.min < b)
        if isinstance(b, int):
            return int(a.max < b), int(a.min < b)
        elif a.max < b.min:
            return (1, 1)
        elif a.min > b.max:
            return (0, 0)
        else:
            return (0, 1)

    def __mul__(self, b: SymInt) -> Sym:
        return (self.a * b) < (self.b * b)

    def _floordiv(self, b: SymInt, factoring_allowed: bool = False) -> Sym:
        return (self.a // b) < (self.b // b)


class Mul(Op):
    glyph = '*'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[SymInt, SymInt]:
        if truthy(b >= 0):
            return a.min * b, a.max * b
        else:
            return a.max * b, a.min * b

    def __mul__(self, b: SymInt) -> Sym:
        return self.a * (self.b * b)  # two muls in one mul

    def _floordiv(self, b: SymInt, factoring_allowed: bool = False) -> Sym:
        # NOTE: mod negative isn't handled right
        if self.b % b == 0:
            return self.a * (self.b // b)
        if b % self.b == 0 and self.b > 0:
            return self.a // (b // self.b)
        return super()._floordiv(b, factoring_allowed)

    def __mod__(self, b: int):
        a = self.a * (self.b % b)
        return Sym.__mod__(a, b)  # FIXME: :|


class Div(Op, lang.Final):
    glyph = '//'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[SymInt, SymInt]:
        if a.min < 0 or not isinstance(b, int):
            raise ValueError(b)
        return a.min // b, a.max // b

    def _floordiv(self, b: SymInt, factoring_allowed: bool = False) -> Sym:
        return self.a // (self.b * b)  # two divs is one div


class Mod(Op, lang.Final):
    glyph = '%'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[SymInt, SymInt]:
        if a.min < 0 or not isinstance(b, int):
            raise ValueError(b)
        if a.max - a.min >= b or (a.min != a.max and a.min % b >= a.max % b):
            return 0, b - 1
        else:
            return a.min % b, a.max % b

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> Sym:
        if self.b % b == 0:
            return (self.a // b) % (self.b // b)  # put the div inside mod
        return super()._floordiv(b, factoring_allowed)


##


RedT = ta.TypeVar('RedT', bound='Red')


class Red(Sym, lang.Abstract):
    def __init__(self, syms: ta.Sequence[Sym], *, _min: SymInt, _max: SymInt) -> None:
        self._syms = [check.isinstance(n, Sym) for n in syms]
        self._min = check_sym_int(_min)
        self._max = check_sym_int(_max)
        super().__init__()

    @property
    def syms(self) -> ta.Sequence[Sym]:
        return self._syms

    @property
    def min(self) -> SymInt:
        return self._min

    @property
    def max(self) -> SymInt:
        return self._max

    @classmethod
    def new(cls: ta.Type[RedT], syms: ta.Sequence[Sym]) -> Sym:
        mn, mx = cls.calc_bounds(syms)
        if mn == mx:
            return Num(mn)
        return cls(syms, _min=mn, _max=mx)

    glyph: ta.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[SymInt, SymInt]:
        raise NotImplementedError

    def vars(self) -> ta.Iterator[Var]:
        for n in self._syms:
            yield from n.vars()


def sum_(syms: ta.Sequence[Sym]) -> Sym:
    syms = [x for x in syms if x.max or x.min]
    if not syms:
        return Num(0)
    if len(syms) == 1:
        return syms[0]

    new_syms: list[Sym] = []
    num_sym_sum = 0
    flat: list[Sym]
    if isinstance((summed := Sum.new(syms)), Sum):
        flat = list(ta.cast(Sum, summed).flat())
    else:
        flat = [check.isinstance(summed, Num)]
    for sym in flat:
        if isinstance(sym, Num):
            num_sym_sum += sym.b
        else:
            new_syms.append(sym)

    if len(new_syms) > 1 and len(set([x.a if isinstance(x, Mul) else x for x in new_syms])) < len(new_syms):
        new_syms = factorize(new_syms)
    if num_sym_sum:
        new_syms.append(Num(num_sym_sum))
    if len(new_syms) > 1:
        return Sum.new(new_syms)
    elif len(new_syms) == 1:
        return new_syms[0]
    else:
        return Num(0)


class Sum(Red, lang.Final):
    glyph = '+'

    @classmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[SymInt, SymInt]:
        return sum(x.min for x in syms), sum(x.max for x in syms)

    def __mul__(self, b: SymInt) -> Sym:
        return sum_([x * b for x in self.syms])  # distribute mul into sum

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> Sym:
        if isinstance(b, Sum):
            nu_num = sum(sym.b for sym in self.flat() if isinstance(sym, Num))
            de_num = sum(sym.b for sym in b.flat() if isinstance(sym, Num))
            if nu_num > 0 and de_num and (d := nu_num // de_num) > 0:
                return Num(d) + (self - b * d) // b

        fully_divided: list[Sym] = []
        rest: list[Sym] = []
        if isinstance(b, Sym):
            for x in self.flat():
                if x % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
            if (sum_fully_divided := Sum.new(fully_divided)) != 0:
                return sum_fully_divided + Sum.new(rest) // b
            return super()._floordiv(b, False)

        if b == 1:
            return self
        if not factoring_allowed:
            return super()._floordiv(b, factoring_allowed)

        fully_divided, rest = [], []
        gcd = b
        divisor = 1
        for x in self.flat():
            if isinstance(x, (Num, Mul)):
                if x.b % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
                    gcd = math.gcd(gcd, x.b)
                    if isinstance(x, Mul) and divisor == 1 and b % x.b == 0:
                        divisor = x.b
            else:
                rest.append(x)
                gcd = 1

        if gcd > 1:
            return sum_(fully_divided) + sum_(rest)._floordiv(gcd) // (b // gcd)
        if divisor > 1:
            return sum_(fully_divided) + sum_(rest)._floordiv(divisor) // (b // divisor)
        return sum_(fully_divided) + Sym._floordiv(sum_(rest), b)  # FIXME: :|

    def __mod__(self, b: SymInt) -> Sym:
        if isinstance(b, Sum):
            nu_num = sum(sym.b for sym in self.flat() if isinstance(sym, Num))
            de_num = sum(sym.b for sym in b.flat() if isinstance(sym, Num))
            if nu_num > 0 and de_num and (d := nu_num // de_num) > 0:
                return (self - b * d) % b

        if isinstance(b, Sym) and (b - self).min > 0:
            return self  # b - self simplifies the sym

        new_syms: list[Sym] = []
        for x in self.syms:
            if isinstance(x, Num):
                new_syms.append(Num(x.b % b))
            elif isinstance(x, Mul):
                new_syms.append(x.a * (x.b % b))
            else:
                new_syms.append(x)

        return Sym.__mod__(sum_(new_syms), b)  # FIXME: :|

    def __lt__(self, b: SymInt) -> SymInt:
        lhs: Sym = self

        if isinstance(b, int):
            new_sum = []
            for x in self.syms:
                # TODO: should we just force the last one to always be the number
                if isinstance(x, Num):
                    b -= x.b
                else:
                    new_sum.append(x)
            lhs = sum_(new_sum)

            if isinstance(lhs, Sum):
                muls: list[Mul]
                muls, others = col.partition(lhs.syms, lambda x: isinstance(x, Mul) and x.b > 0 and x.max >= b)
                if muls:
                    # NOTE: gcd in python 3.8 takes exactly 2 args
                    mul_gcd = muls[0].b
                    for x in muls[1:]:
                        mul_gcd = gcd(mul_gcd, x.b)  # type: ignore  # mypy cannot tell x.b is int here

                    if b % mul_gcd == 0:
                        all_others = sum_(others)
                        if all_others.min >= 0 and all_others.max < mul_gcd:
                            # TODO: should we divide both by mul_gcd here?
                            lhs = sum_(muls)

        return Sym.__lt__(lhs, b)  # FIXME: :|

    def flat(self) -> ta.Iterator[Sym]:
        for x in self.syms:
            if isinstance(x, Sum):
                yield from x.flat()
            else:
                yield x


def and_(syms: ta.Sequence[Sym]) -> Sym:
    if not syms:
        return Num(1)
    if len(syms) == 1:
        return syms[0]
    if any(not x for x in syms):
        return Num(0)

    # filter 1s
    syms = [x for x in syms if x.min != x.max]
    if len(syms) > 1:
        return And.new(syms)
    elif len(syms) == 1:
        return syms[0]
    else:
        return Num(1)


class And(Red, lang.Final):
    glyph = ' and '

    @classmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[SymInt, SymInt]:
        return min(x.min for x in syms), max(x.max for x in syms)

    def __mul__(self, b: SymInt) -> Sym:
        return and_([x * b for x in self.syms])

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> Sym:
        return and_([x // b for x in self.syms])


##


def factorize(syms: ta.Iterable[Sym]) -> list[Sym]:
    mul_groups: dict[Sym, int] = {}
    for x in syms:
        a, b = (x.a, x.b) if isinstance(x, Mul) else (x, 1)
        mul_groups[a] = mul_groups.get(a, 0) + b
    return [Mul.new(a, b_sum) if b_sum != 1 else a for a, b_sum in mul_groups.items() if b_sum != 0]


def substitute(n: Sym, var_vals: ta.Mapping[Var, Sym]) -> Sym:
    if isinstance(n, Num):
        return n
    if isinstance(n, Var):
        return var_vals.get(n, n)
    if isinstance(n, Lt):
        return substitute(n.a, var_vals) < (n.b if isinstance(n.b, int) else substitute(n.b, var_vals))
    if isinstance(n, Mul):
        return substitute(n.a, var_vals) * (n.b if isinstance(n.b, int) else substitute(n.b, var_vals))
    if isinstance(n, Div):
        return substitute(n.a, var_vals) // check.isinstance(n.b, int)
    if isinstance(n, Mod):
        return substitute(n.a, var_vals) % n.b
    if isinstance(n, Sum):
        return sum_([substitute(s, var_vals) for s in n.syms])
    if isinstance(n, And):
        subed = []
        for node in n.syms:
            if not (sub := substitute(node, var_vals)):
                return Num(0)
            subed.append(sub)
        return and_(subed)
    raise TypeError(n)


def infer(n: SymInt, var_vals: ta.Mapping[Var, int]) -> int:
    if isinstance(n, Num):
        return n.b
    ret = substitute(n, {k: Num(v) for k, v in var_vals.items()})
    return check.isinstance(ret, Num).b


def expand(n: Sym) -> ta.List[Sym]:
    if isinstance(n, Var):
        return [n] if n.expr is not None else [Num(j) for j in range(n.min, n.max + 1)]
    if isinstance(n, Num):
        return [n]
    if isinstance(n, Mul):
        return [x * n.b for x in expand(n.a)]
    if isinstance(n, Div):
        return [x // n.b for x in expand(n.a)]
    if isinstance(n, Mod):
        return [x % n.b for x in expand(n.a)]
    if isinstance(n, Sum):
        return [sum_(it) for it in itertools.product(*[expand(x) for x in n.syms])]
    raise TypeError(n)


##


class Labeler:
    def __init__(self, prefix: str = 's') -> None:
        super().__init__()
        self._dct: dict[Sym, str] = {}
        self._pfx = prefix

    def clear(self) -> None:
        self._dct.clear()

    def __call__(self, s: Sym) -> str:
        check.isinstance(s, Sym)
        try:
            return self._dct[s]
        except KeyError:
            l = self._dct[s] = f'{self._pfx}{len(self._dct)}'
            return l


_LABELER = Labeler()


def label(s: Sym) -> str:
    return _LABELER(s)
