"""
TODO:
 - {sum,and}_syms -> cls.new
 - *** NEED BOUNDS ON KEY?
  - sdm
"""
import abc
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


##


class SymRenderer:
    @dispatch.method
    def render(self, n: 'Sym') -> str:
        raise TypeError(n)

    @render.register
    def render_var(self, n: 'Var') -> str:
        return n.name

    @render.register
    def render_num(self, n: 'Num') -> str:
        return str(n.b)

    @render.register
    def render_op(self, n: 'Op') -> str:
        return f'({self.render(n.a)}{n.glyph}{n.b})'

    @render.register
    def render_red(self, n: 'Red') -> str:
        return f'({n.glyph.join(sorted(self.render(x) for x in n.syms))})'


class DebugSymRenderer(SymRenderer):
    @SymRenderer.render.register
    def render_var(self, n: 'Var') -> str:
        return f'{n.name if n.name is not None else "?"}[{n.min},{n.max}]'


##


class Sym(lang.Abstract, lang.Sealed):

    @property
    @abc.abstractmethod
    def min(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def max(self) -> int:
        raise NotImplementedError

    @cached.property
    def expr(self) -> str:
        return SymRenderer().render(self)

    @cached.property
    def debug(self) -> str:
        return DebugSymRenderer().render(self)

    def vars(self) -> ta.Iterator['Var']:
        yield
        return

    @cached.property
    def key(self) -> str:
        return self.debug

    def __repr__(self) -> str:
        return f'<{self.debug}>'

    def __hash__(self) -> int:
        return hash(self.key)

    def __bool__(self) -> bool:
        return not (self.max == self.min == 0)

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

    def __le__(self, b: SymInt) -> 'Sym':
        return self < (b + 1)

    def __gt__(self, b: SymInt) -> 'Sym':
        return (-self) < (-b)

    def __ge__(self, b: SymInt) -> 'Sym':
        return Lt.new(-self, -b + 1)

    def __lt__(self, b: SymInt) -> 'Sym':
        lhs = self
        if isinstance(lhs, Sum) and isinstance(b, int):
            muls, others = col.partition(lhs.syms, lambda x: isinstance(x, Mul) and x.b > 0 and x.max >= b)
            if len(muls):
                # NOTE: gcd in python 3.8 takes exactly 2 args
                mul_gcd = muls[0].b
                for x in muls[1:]:
                    mul_gcd = math.gcd(mul_gcd, x.b)
                if b % mul_gcd == 0:
                    all_others = sum_(others)
                    # print(mul_gcd, muls, all_others)
                    if all_others.min >= 0 and all_others.max < mul_gcd:
                        # TODO: should we divide both by mul_gcd here?
                        lhs = sum_(muls)
        return Lt.new(lhs, b)

    def __mul__(self, b: SymInt) -> 'Sym':
        if b == 0:
            return Num(0)
        elif b == 1:
            return self
        if isinstance(self,  Num):
            if isinstance(b, int):
                return Num(self.b * b)
            else:
                return Mul.new(b, self.b)
        return Mul.new(self, b)

    def __rmul__(self, b: SymInt) -> 'Sym':
        return self * b

    def __rfloordiv__(self, b: int) -> 'Sym':
        raise TypeError(f'Not supported: {b} // {self}')

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> 'Sym':
        if isinstance(b, Sym):
            if (b > self).min > 0 and self.min >= 0:
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
        raise TypeError(f'Not supported: {b} % {self}')

    def __mod__(self, b: SymInt) -> 'Sym':
        if isinstance(b, Sym):
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


def var(name: ta.Optional[str], min: int, max: int) -> Sym:
    if name is not None:
        if not name or name[0] not in Var._name_first_set or frozenset(name[1:]) - Var._name_rest_set:
            raise ValueError(f'Invalid var name: {name!r} {min} {max}')
    if check.isinstance(min, int) == check.isinstance(max, int):
        return Num(min)
    return Var(name, min, max)


class Var(Sym, lang.Final):
    _name_first_set: ta.Final[ta.AbstractSet[str]] = frozenset(string.ascii_letters + '_')
    _name_rest_set: ta.Final[ta.AbstractSet[str]] = frozenset([*_name_first_set, *string.digits])

    def __init__(self, name: ta.Optional[str], min: int, max: int) -> None:
        check.isinstance(min, int)
        check.isinstance(max, int)
        if min < 0 or min >= max:
            raise ValueError(f'Invalid var range: {name!r} {min} {max}')
        if name is not None:
            if not name or name[0] not in Var._name_first_set or frozenset(name[1:]) - Var._name_rest_set:
                raise ValueError(f'Invalid var name: {name!r} {min} {max}')
        super().__init__()
        self._name = name
        self._min = min
        self._max = max

    @property
    def name(self) -> str:
        return self._name

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    def vars(self) -> ta.Iterator['Var']:
        yield self


##


class Num(Sym, lang.Final):
    def __init__(self, b: int) -> None:
        super().__init__()
        self._b = check.isinstance(b, int)

    def __int__(self):
        return self._b

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

    def __init__(self, a: Sym, b: SymInt, *, _min: int, _max: int) -> None:
        super().__init__()
        self._a = check.isinstance(a, (Sym, int))
        self._b = check.isinstance(b, (Sym, int))
        self._min = check.isinstance(_min, int)
        self._max = check.isinstance(_max, int)

    @property
    def a(self) -> Sym:
        return self._a

    @property
    def b(self) -> SymInt:
        return self._b

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
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
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[int, int]:
        raise NotImplementedError

    def vars(self) -> ta.Iterator[Var]:
        yield from self._a.vars()
        if isinstance(self._b, Sym):
            yield from self._b.vars()


class Lt(Op):
    glyph = '<'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[int, int]:
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
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[int, int]:
        if b >= 0:
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
        return Sym.__mod__(a, b)  # FIXME:


def factorize(syms: ta.Iterable[Sym]) -> list[Sym]:
    mul_groups: dict[Sym, int] = {}
    for x in syms:
        a, b = (x.a, x.b) if isinstance(x, Mul) else (x, 1)
        mul_groups[a] = mul_groups.get(a, 0) + b
    return [Mul.new(a, b_sum) if b_sum != 1 else a for a, b_sum in mul_groups.items() if b_sum != 0]


class Div(Op):
    glyph = '//'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[int, int]:
        if a.min < 0 or not isinstance(b, int):
            raise ValueError(b)
        return a.min // b, a.max // b

    def _floordiv(self, b: SymInt, factoring_allowed: bool = False) -> Sym:
        return self.a // (self.b * b)  # two divs is one div


class Mod(Op):
    glyph = '%'

    @classmethod
    def calc_bounds(cls, a: Sym, b: SymInt) -> ta.Tuple[int, int]:
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


class Red(Sym, lang.Abstract):
    def __init__(self, syms: ta.Sequence[Sym], *, _min: int, _max: int) -> None:
        super().__init__()
        self._syms = [check.isinstance(n, Sym) for n in syms]
        self._min = check.isinstance(_min, int)
        self._max = check.isinstance(_max, int)

    @property
    def syms(self) -> ta.Sequence[Sym]:
        return self._syms

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    @classmethod
    def new(cls, syms: ta.Sequence['Sym']) -> 'Sym':
        mn, mx = cls.calc_bounds(syms)
        return cls(syms, _min=mn, _max=mx)

    glyph: ta.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[int, int]:
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
    for sym in Sum.new(syms).flat():
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


class Sum(Red):
    glyph = '+'

    @classmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[int, int]:
        return sum(x.min for x in syms), sum(x.max for x in syms)

    def __mul__(self, b: SymInt) -> Sym:
        return sum_([x * b for x in self.syms])  # distribute mul into sum

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> Sym:
        fully_divided: list[Sym] = []
        rest: list[Sym] = []
        if isinstance(b, Sum):
            nu_num = sum(sym.b for sym in self.flat() if isinstance(sym, Num))
            de_num = sum(sym.b for sym in b.flat() if isinstance(sym, Num))
            if de_num and nu_num % de_num == 0 and b * (d := nu_num // de_num) == self:
                return Num(d)
        if isinstance(b, Sym):
            for x in self.flat():
                if x % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
            if (b > (sum_rest := Sum.new(rest))).min and (sum_rest >= 0).min:
                return Sum.new(fully_divided)
            return Sym._floordiv(self, b, False)
        if b == 1:
            return self
        if not factoring_allowed:
            return Sym._floordiv(self, b, factoring_allowed)

        fully_divided, rest = [], []
        _gcd = b
        divisor = 1
        for x in self.flat():
            if isinstance(x, (Num, Mul)):
                if x.b % b == 0:
                    fully_divided.append(x // b)
                else:
                    rest.append(x)
                    _gcd = math.gcd(_gcd, x.b)
                    if isinstance(x, Mul) and divisor == 1 and b % x.b == 0:
                        divisor = x.b
            else:
                rest.append(x)
                _gcd = 1

        if _gcd > 1:
            return sum_(fully_divided) + sum_(rest)._floordiv(_gcd) // (b // _gcd)
        if divisor > 1:
            return sum_(fully_divided) + sum_(rest)._floordiv(divisor) // (b // divisor)
        return sum_(fully_divided) + Sym._floordiv(sum_(rest), b)

    def __mod__(self, b: SymInt):
        if isinstance(b, Sum):
            nu_num = sum(sym.b for sym in self.flat() if isinstance(sym, Num))
            de_num = sum(sym.b for sym in b.flat() if isinstance(sym, Num))
            if de_num and nu_num % de_num == 0 and b * (nu_num // de_num) == self:
                return Num(0)
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
        return Sym.__mod__(sum_(new_syms), b)

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


class And(Red):
    glyph = ' and '

    @classmethod
    def calc_bounds(cls, syms: ta.Sequence[Sym]) -> ta.Tuple[int, int]:
        return min(x.min for x in syms), max(x.max for x in syms)

    def __mul__(self, b: SymInt) -> Sym:
        return and_([x * b for x in self.syms])

    def _floordiv(self, b: SymInt, factoring_allowed: bool = True) -> Sym:
        return and_([x // b for x in self.syms])
