# ruff: noqa: SLF001
import typing as ta

from ..errors import ReflectionTypeError
from .types import CallableType
from .types import Instance
from .types import ParamSpecType
from .types import ProperType
from .types import TupleType
from .types import Type
from .types import TypeList
from .types import TypeVarId
from .types import TypeVarLikeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnpackType
from .typevisitor import TypeTranslator


ExpandEnvKey: ta.TypeAlias = TypeVarId | TypeVarLikeType
ExpandEnv: ta.TypeAlias = ta.Mapping[ExpandEnvKey, Type]


##


@ta.overload
def expand_type(typ: CallableType, env: ExpandEnv) -> CallableType:
    ...


@ta.overload
def expand_type(typ: ProperType, env: ExpandEnv) -> ProperType:
    ...


@ta.overload
def expand_type(typ: Type, env: ExpandEnv) -> Type:
    ...


def expand_type(typ: Type, env: ExpandEnv) -> Type:
    expanded = typ.accept(ExpandTypeVisitor(env))
    if isinstance(typ, CallableType) and not isinstance(expanded, CallableType):
        raise ReflectionTypeError(expanded)
    return expanded


class ExpandTypeVisitor(TypeTranslator):
    __slots__ = ('env',)

    def __init__(self, env: ExpandEnv) -> None:
        super().__init__()

        self.env = env

    def _lookup(self, typ: TypeVarLikeType) -> Type | None:
        try:
            return self.env[typ]
        except KeyError:
            pass

        try:
            return self.env[typ._id]
        except KeyError:
            pass

        return None

    def visit_type_var(self, typ: TypeVarType) -> Type:
        if (replacement := self._lookup(typ)) is not None:
            return replacement
        return typ

    def visit_param_spec(self, typ: ParamSpecType) -> Type:
        if (replacement := self._lookup(typ)) is not None:
            return replacement
        return typ

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> Type:
        if (replacement := self._lookup(typ)) is not None:
            return replacement
        return typ

    def visit_tuple_type(self, typ: TupleType) -> Type:
        partial_fallback = typ._partial_fallback.accept(self)
        if not isinstance(partial_fallback, Instance):
            raise ReflectionTypeError(partial_fallback)

        items: list[Type] = []
        for item in typ._items:
            expanded = item.accept(self)

            if isinstance(item, TypeVarTupleType):
                if isinstance(expanded, TupleType):
                    items.extend(expanded._items)
                    continue
                if isinstance(expanded, TypeList):
                    items.extend(expanded._items)
                    continue

            if isinstance(item, UnpackType) and isinstance(expanded, UnpackType):
                if isinstance(expanded._type, TupleType):
                    items.extend(expanded._type._items)
                    continue
                if isinstance(expanded._type, TypeList):
                    items.extend(expanded._type._items)
                    continue

            items.append(expanded)

        return TupleType(items, partial_fallback)
