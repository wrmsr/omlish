import abc
import functools
import typing as ta

from ... import lang
from ...lang import warn_unstable


warn_unstable()


T = ta.TypeVar('T')


_CODE_IGNORE = frozenset(['co_filename', 'co_firstlineno'])


def _code_dct(co, *, ignore=()):
    ignore = {*_CODE_IGNORE, *ignore}
    return {a: getattr(co, a) for a in dir(co) if a.startswith('co_') and a not in ignore}


def _code_diff(l, r, *, ignore=()):
    dl, dr = [_code_dct(o.__code__, ignore=ignore) for o in [l, r]]
    return {k: (vl, vr) for k in sorted({*dl, *dr}) for vl, vr in [(dl.get(k), dr.get(k))] if vl != vr}


class LambdaWrapper(ta.Generic[T], lang.Abstract):
    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError

    @classmethod
    def maybe_of(cls, obj):
        if isinstance(obj, cls):
            return obj
        if not isinstance(obj, type(lambda: 0)):
            return obj
        ret = cls._maybe_of(obj)
        if ret is not obj:
            functools.update_wrapper(ret, obj)
        return ret

    @abc.abstractclassmethod  # noqa
    def _maybe_of(cls, obj):
        raise NotImplementedError


class ConstLambda(LambdaWrapper[T], lang.Final):

    def __init__(self, value: T) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self._value}>'

    def __call__(self) -> T:
        return self._value

    @classmethod
    def _maybe_of(cls, obj):
        cd = _code_diff(obj, lambda: 0, ignore=['co_consts'])
        if cd:
            return obj

        consts = obj.__code__.co_consts
        if len(consts) == 1:
            [val] = consts
        elif len(consts) == 2 and consts[0] is None:
            _, val = consts
        else:
            return obj

        return cls(val)


_GLOBAL = None


class GlobalLambda(LambdaWrapper[T], lang.Final):

    def __init__(self, name: str, module: str, globals: ta.Mapping) -> None:
        super().__init__()
        self._name = name
        self._module = module
        self._globals = globals

    @property
    def name(self) -> str:
        return self._name

    @property
    def module(self) -> str:
        return self._module

    @property
    def globals(self) -> ta.Mapping:
        return self._globals

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self._module}.{self._name}>'

    def __call__(self) -> T:
        return self._globals[self._name]

    @classmethod
    def _maybe_of(cls, obj):
        cd = _code_diff(obj, lambda: _GLOBAL, ignore=['co_names'])
        if cd:
            return obj

        names = obj.__code__.co_names
        if len(names) != 1:
            return obj

        [name] = names
        module = obj.__module__
        globals = obj.__globals__
        return cls(name, module, globals)


_Cell = ta.Any


class CellLambda(LambdaWrapper[T], lang.Final):

    def __init__(self, name: str, whence: str, cell: _Cell) -> None:
        super().__init__()
        self._name = name
        self._whence = whence
        self._cell = cell

    @property
    def name(self) -> str:
        return self._name

    @property
    def whence(self) -> str:
        return self._whence

    @property
    def cell(self) -> _Cell:
        return self._cell

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self._whence}::{self._name}@{id(self._cell):x}>'

    def __call__(self) -> T:
        return self._cell.cell_contents

    @classmethod
    def _maybe_of(cls, obj):
        stub = 0
        cd = _code_diff(obj, lambda: stub, ignore=['co_freevars'])
        if cd:
            return obj

        names = obj.__code__.co_freevars
        if len(names) != 1:
            return obj

        [name] = names
        [cell] = obj.__closure__
        whence = '.'.join(p for s in [obj.__module__, obj.__qualname__] for p in s.split('.') if p.isidentifier())
        return CellLambda(name, whence, cell)


LAMBDA_WRAPPERS: ta.Sequence[ta.Type[LambdaWrapper]] = [
    ConstLambda,
    GlobalLambda,
    CellLambda,
]


def maybe_wrap(obj):
    for wc in LAMBDA_WRAPPERS:
        w = wc.maybe_of(obj)
        if w is not obj:
            return w
    return obj


###


class C:
    def __init__(self):
        self.l = []


GLOBAL_C = C()


def test_wrap():
    l = maybe_wrap(lambda: 420)
    assert isinstance(l, ConstLambda)
    assert l.value == 420

    l = maybe_wrap(lambda: 'hi')
    assert isinstance(l, ConstLambda)
    assert l.value == 'hi'

    cell = 0
    l = maybe_wrap(lambda: cell)
    assert not isinstance(l, ConstLambda)

    l = maybe_wrap(lambda: GLOBAL_C)
    assert not isinstance(l, ConstLambda)

    l = maybe_wrap(lambda: sum(range(100)))
    assert not isinstance(l, ConstLambda)

    gl = maybe_wrap(lambda: GLOBAL_C)
    assert isinstance(gl, GlobalLambda)
    assert gl() is GLOBAL_C

    cell2 = object()
    rl = lambda: cell2
    l = maybe_wrap(rl)
    assert isinstance(l, CellLambda)
    assert l() is cell2
