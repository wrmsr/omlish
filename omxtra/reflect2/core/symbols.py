"""
Unlike in mypy these types are part of the public api - internal code *should* access private fields, but for external
code it is hidden behind properties.
"""
import enum
import typing as ta


if ta.TYPE_CHECKING:
    from .types import Type
    from .types import TypeVarLikeType


##


class VarianceKind(enum.Enum):
    IN = 0
    CO = 1
    CONTRA = 2
    NOT_READY = 3


class ArgKind(enum.Enum):
    POS = 0
    OPT = 1
    STAR = 2
    NAMED = 3
    STAR2 = 4
    NAMED_OPT = 5


##


class SymbolNode:
    __slots__ = ()

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def fullname(self) -> str:
        raise NotImplementedError


@ta.final
class TypeInfo(SymbolNode):
    __slots__ = (
        '_name',
        '_fullname',
        '_bases',
        '_mro',
        '_type_vars',
        '_variances',
        '_is_protocol',
        '_is_enum',
        '_enum_members',
        '_new_type_supertype',
    )

    def __init__(
            self,
            name: str,
            fullname: str | None = None,
            *,
            bases: list[Type] | None = None,
            mro: list[TypeInfo] | None = None,
            type_vars: list[TypeVarLikeType] | None = None,
            variances: list[VarianceKind] | None = None,
            is_protocol: bool = False,
            is_enum: bool = False,
            enum_members: list[str] | None = None,
            new_type_supertype: Type | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._fullname = name if fullname is None else fullname
        self._bases = [] if bases is None else bases
        self._mro = [self] if mro is None else mro
        self._type_vars = [] if type_vars is None else type_vars
        self._variances = [] if variances is None else variances
        self._is_protocol = is_protocol
        self._is_enum = is_enum
        self._enum_members = [] if enum_members is None else enum_members
        self._new_type_supertype = new_type_supertype

    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def bases(self) -> ta.Sequence[Type]:
        return self._bases

    @property
    def mro(self) -> ta.Sequence[TypeInfo]:
        return self._mro

    @property
    def type_vars(self) -> ta.Sequence[TypeVarLikeType]:
        return self._type_vars

    @property
    def variances(self) -> ta.Sequence[VarianceKind]:
        return self._variances

    @property
    def is_protocol(self) -> bool:
        return self._is_protocol

    @property
    def is_enum(self) -> bool:
        return self._is_enum

    @property
    def enum_members(self) -> ta.Sequence[str]:
        return self._enum_members

    @property
    def new_type_supertype(self) -> Type | None:
        return self._new_type_supertype


@ta.final
class TypeAlias(SymbolNode):
    __slots__ = (
        '_name',
        '_fullname',
        '_target',
        '_alias_tvars',
        '_runtime_object',
        '_is_recursive',
    )

    def __init__(
            self,
            name: str,
            target: Type,
            *,
            fullname: str | None = None,
            alias_tvars: list[TypeVarLikeType] | None = None,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._fullname = name if fullname is None else fullname
        self._target = target
        self._alias_tvars = [] if alias_tvars is None else alias_tvars
        self._runtime_object = runtime_object
        self._is_recursive: bool | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def target(self) -> Type:
        return self._target

    @property
    def alias_tvars(self) -> ta.Sequence[TypeVarLikeType]:
        return self._alias_tvars

    @property
    def runtime_object(self) -> object | None:
        return self._runtime_object
