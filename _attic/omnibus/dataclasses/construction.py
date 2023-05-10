"""
TODO:
 - how to detect changes?
  - source file hash? if source not available default yolo?
"""
import dataclasses as dc
import typing as ta

from .. import check
from .. import code
from .. import lang
from .reflect import DataSpec
from .types import _Placeholder


@dc.dataclass(frozen=True)
class Spec:
    actions: ta.Sequence['Action']

    def __post_init__(self):
        check.isinstance(self.actions, ta.Sequence)
        for a in self.actions:
            check.isinstance(a, Action)


class Action(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class SetAttr(Action):
    name: str
    value: 'Value'

    def __post_init__(self):
        check.non_empty_str(self.name)
        check.isinstance(self.value, Value)


class Value(lang.Abstract):
    pass


CONST_TYPES = (int, float, str, type(None))


class Const(Value):
    value: ta.Any

    def __post_init__(self):
        check.isinstance(self.value, CONST_TYPES)


@dc.dataclass(frozen=True)
class Function(Value):
    name: str
    arg_spec: code.ArgSpec
    body: str
    locals: ta.Optional[ta.Mapping[str, Value]] = None

    def __post_init__(self):
        check.non_empty_str(self.name)
        check.isinstance(self.arg_spec, code.ArgSpec)
        check.isinstance(self.body, str)
        check.isinstance(self.locals, (ta.Mapping, None))
        for k, v in (self.locals or {}).items():
            check.non_empty_str(k)
            check.isinstance(v, Value)


@dc.dataclass(frozen=True)
class ClassParam(Value):
    name: str

    def __post_init__(self):
        check.non_empty_str(self.name)


@dc.dataclass(frozen=True)
class FieldParam(Value):
    field: str
    name: str

    def __post_init__(self):
        check.non_empty_str(self.name)
        check.non_empty_str(self.field)


@dc.dataclass(frozen=True)
class Context:
    spec: DataSpec

    def __post_init__(self):
        check.isinstance(self.spec, DataSpec)


def apply(act: Action, ctx: Context) -> None:
    if isinstance(act, SetAttr):
        if act.name in ctx.spec.cls.__dict__:
            ev = ctx.spec.cls.__dict__[act.name]
            if ev is not _Placeholder:
                raise TypeError(f'Cannot overwrite attribute {act.name}')
        setattr(ctx.spec.cls, act.name, build(act.value, ctx))

    else:
        raise TypeError(act)


def build(val: Value, ctx: Context) -> ta.Any:
    if isinstance(val, Const):
        return val.value

    elif isinstance(val, Function):
        return code.create_function(
            val.name,
            val.arg_spec,
            val.body,
            locals={k: build(v, ctx) for k, v in val.locals.items()} if val.locals else None,
            globals=ctx.spec.globals,
        )

    else:
        raise TypeError(val)
