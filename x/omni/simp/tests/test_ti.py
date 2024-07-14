import ast
import inspect
import textwrap
import typing as ta

from .. import nodes as no
from ... import check
from ... import code
from ... import collections as col
from ... import dataclasses as dc
from ... import dispatch
from ..pyasts import translate


class Ty(dc.Enum):
    pass


class VarTy(Ty):
    s: str

    def __str__(self) -> str:
        return self.s


class ConTy(Ty):
    s: str

    def __str__(self) -> str:
        return self.s


class AppTy(Ty):
    a: Ty
    b: Ty

    def __str__(self) -> str:
        return f'{self.a} {self.b}'


class FunTy(Ty):
    args: ta.Sequence[Ty]
    ret: Ty

    def __str__(self) -> str:
        return f'({", ".join(map(str, self.args))}) -> {self.ret}'


Constraint = ta.Tuple[Ty, Ty]
Env = ta.Mapping[str, Ty]
MutEnv = ta.MutableMapping[str, Ty]


def seq(t: Ty) -> Ty:
    return AppTy(ConTy('Seq'), t)


class TypeInferrer(dispatch.Class):

    def __init__(self) -> None:
        super().__init__()

        self._constraints: ta.List[Constraint] = []
        self._env: MutEnv = {}
        self._name_gen = code.name_generator()

        self._types_by_node: ta.MutableMapping[no.Node, Ty] = col.IdentityKeyDict()

        self._ret = VarTy('$ret')

    def fresh(self):
        return VarTy('$' + self._name_gen())

    visit = dispatch.property()

    def visit(self, node: no.Node) -> ta.Optional[Ty]:  # noqa
        raise TypeError(node)

    def visit(self, node: no.Fn) -> ta.Optional[Ty]:  # noqa
        tys = [self.fresh() for _ in node.args.args]
        for arg, ty in zip(node.args.args, tys):
            self._types_by_node[arg] = ty
            self._env[arg.name.s] = ty
        for b in node.body:
            self.visit(b)
        return FunTy(tys, self._ret)

    def visit(self, node: no.Const) -> ta.Optional[Ty]:  # noqa
        tv = self.fresh()
        self._types_by_node[node] = tv
        return tv

    def visit(self, node: no.SetVar) -> ta.Optional[Ty]:  # noqa
        ty = self.visit(node.value)
        if node.name.s in self._env:
            self._constraints += [(ty, self._env[node.name.s])]
        self._env[node.name.s] = ty
        self._types_by_node[node] = ty
        return None

    def visit(self, node: no.GetItem) -> ta.Optional[Ty]:  # noqa
        tv = self.fresh()
        ty = self.visit(node.value)
        ixty = self.visit(node.idx)
        self._constraints += [(ty, seq(tv)), (ixty, int)]
        return tv

    def visit(self, node: no.BinExpr) -> ta.Optional[Ty]:  # noqa
        tya = self.visit(node.left)
        tyb = self.visit(node.right)
        self._constraints += [(tya, tyb)]
        return tyb

    def visit(self, node: no.GetVar) -> ta.Optional[Ty]:  # noqa
        ty = self._env[node.name.s]
        self._types_by_node[node] = ty
        return ty

    def visit(self, node: no.Return) -> ta.Optional[Ty]:  # noqa
        ty = self.visit(node.value)
        self._constraints += [(ty, self._ret)]
        return None


def ftv(t: Ty) -> ta.AbstractSet[Ty]:
    if isinstance(t, ConTy):
        return frozenset()
    elif isinstance(t, AppTy):
        return ftv(t.a) | ftv(t.b)
    elif isinstance(t, FunTy):
        s = {t.ret}
        for a in t.args:
            s |= ftv(a)
        return frozenset(s)
    elif isinstance(t, VarTy):
        return frozenset([t])
    else:
        raise TypeError(t)


def apply(s: Env, t: Ty) -> Ty:
    if isinstance(t, ConTy):
        return t
    elif isinstance(t, AppTy):
        return AppTy(apply(s, t.a), apply(s, t.b))
    elif isinstance(t, FunTy):
        args = [apply(s, a) for a in t.args]
        ret = apply(s, t.ret)
        return FunTy(args, ret)
    elif isinstance(t, VarTy):
        return s.get(t.s, t)


def unify(x: Ty, y: Ty) -> Env:
    if isinstance(x, AppTy) and isinstance(y, AppTy):
        s1 = unify(x.a, y.a)
        s2 = unify(apply(s1, x.b), apply(s1, y.b))
        return compose(s2, s1)
    elif isinstance(x, ConTy) and isinstance(y, ConTy) and (x == y):
        return {}
    elif isinstance(x, FunTy) and isinstance(y, FunTy):
        if len(x.args) != len(y.args):
            raise Exception(x, y)
        s1 = solve(zip(x.args, y.args))
        s2 = unify(apply(s1, x.ret), apply(s1, y.ret))
        return compose(s2, s1)
    elif isinstance(x, VarTy):
        return bind(x.s, y)
    elif isinstance(y, VarTy):
        return bind(y.s, x)
    else:
        raise TypeError(x, y)


def bind(n: str, x: Ty) -> Env:
    if x == n:
        return {}
    elif n in ftv(x):
        raise Exception(n, x)
    else:
        return {n: x}


def compose(s1: Env, s2: Env) -> Env:
    s3 = {t: apply(s1, u) for t, u in s2.items()}
    return {**s1, **s3}


def solve(xs: ta.Iterable[Constraint]) -> Env:
    mgu = {}
    cs = col.deque(xs)
    while len(cs):
        (a, b) = cs.pop()
        s = unify(a, b)
        mgu = compose(s, mgu)
        cs = col.deque((apply(s, x), apply(s, y)) for (x, y) in cs)
    return mgu


def test_ti():
    def f(x, y):
        a = x + 2
        b = a * y
        return b + 1

    ar = ast.parse(textwrap.dedent(inspect.getsource(f)), 'exec')
    nr = translate(check.isinstance(ar, ast.Module).body[0])
    ti = TypeInferrer()
    ty = ti.visit(nr)

    mgu = solve(ti._constraints)
    ity = apply(mgu, ty)

    print()
    print(ity)

    print()
    print('\n'.join(sorted(map(str, ti._constraints))))
