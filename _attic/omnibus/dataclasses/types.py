import dataclasses as dc
import inspect
import typing as ta

from .. import check
from .. import lang
from .internals import FIELDS


T = ta.TypeVar('T')

FieldValidator = ta.Callable[[T], None]
FieldValidation = ta.Callable[[dc.Field], FieldValidator[T]]

FieldMetadataKwargHandler = ta.Callable[[dc.Field, ta.Any], ta.Any]
ClassMetadataKwargHandler = ta.Callable[[type, ta.Any], ta.Any]


MISSING_TYPE = type(dc.MISSING)


METADATA_ATTR = '__dataclass_metadata__'


class Extras(lang.Marker):
    pass


@dc.dataclass(frozen=True)
class Checker(lang.Final):
    fn: ta.Callable[..., bool]


@dc.dataclass(frozen=True)
class Deriver(lang.Final):
    attrs: ta.Union[str, ta.Iterable[str]]
    fn: ta.Callable[..., T]


@dc.dataclass(frozen=True)
class Metadata(lang.Final):
    metadata: ta.Mapping[ta.Any, ta.Any]


@dc.dataclass(frozen=True)
class PostInit(lang.Final):
    fn: ta.Callable[[T], None]


@dc.dataclass(frozen=True)
class Validator(lang.Final):
    fn: ta.Callable[..., None]


@dc.dataclass(frozen=True)
class CheckException(Exception):
    values: ta.Dict[str, ta.Any]
    checker: Checker


@dc.dataclass(frozen=True)
class ExtraFieldParams(lang.Final):
    doc: ta.Optional[str] = None
    mangled: ta.Optional[str] = None
    size: ta.Optional[ta.Any] = None
    frozen: ta.Optional[bool] = None
    kwonly: bool = False
    coerce: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], ta.Any]]] = None
    derive: ta.Optional[ta.Callable[..., ta.Any]] = None
    check: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], bool]]] = None
    check_type: ta.Union[ta.Type, ta.Tuple, None] = None
    validate: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], None]]] = None
    repr_if: ta.Optional[ta.Callable[[ta.Any], bool]] = None
    repr_fn: ta.Optional[ta.Callable[[ta.Any], ta.Optional[str]]] = None
    kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None

    def __post_init__(self) -> None:
        check.isinstance(self.doc, (str, None))
        check.isinstance(self.mangled, (str, None))
        check.isinstance(self.frozen, (bool, None))
        check.isinstance(self.kwonly, bool)
        check.isinstance(self.coerce, (bool, lang.Callable, None))
        check.isinstance(self.derive, (lang.Callable, None))
        check.isinstance(self.check, (bool, lang.Callable, None))
        check.isinstance(self.validate, (bool, lang.Callable, None))
        check.isinstance(self.repr_if, (lang.Callable, None))
        check.isinstance(self.repr_fn, (lang.Callable, None))
        check.isinstance(self.kwargs, (ta.Mapping, None))


check.empty(set(dc.Field.__slots__) & {f.name for f in dc.fields(ExtraFieldParams)})


Mangler = ta.Callable[[str], str]


@dc.dataclass(frozen=True)
class Conferrer(lang.Final):
    fn: ta.Callable[[str, ta.Mapping[str, ta.Any], ta.Mapping[str, ta.Any], ta.Sequence[type]], ta.Any]
    weak: bool = False


SUPER = Conferrer(lambda att, sub, sup, bases: sup[att])


PARAMS_CONFER_DEFAULTS = dict(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
)


@dc.dataclass(frozen=True)
class ExtraParams(lang.Final):
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
    validate: ta.Optional[bool] = None
    field_attrs: bool = False
    kwonly: ta.Optional[bool] = None
    cache_hash: ta.Union[bool, str] = False
    strict_eq: ta.Union[bool] = False
    pickle: bool = False
    reorder: bool = False
    allow_setattr: ta.Union[bool, str, ta.Iterable[str]] = False
    iterable: bool = False
    mangler: ta.Optional[Mangler] = None
    aspects: ta.Optional[ta.Collection[ta.Any]] = None
    confer: ta.Optional[ta.Union[ta.Collection[str], ta.Mapping[str, ta.Any]]] = None
    kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None

    def __post_init__(self) -> None:
        check.isinstance(self.metadata, (ta.Mapping, None, MISSING_TYPE))
        check.isinstance(self.validate, (bool, None, MISSING_TYPE))
        check.isinstance(self.field_attrs, (bool, MISSING_TYPE))
        check.isinstance(self.kwonly, (bool, None, MISSING_TYPE))
        check.isinstance(self.cache_hash, (bool, str, MISSING_TYPE))
        check.isinstance(self.strict_eq, (bool, MISSING_TYPE))
        check.isinstance(self.pickle, (bool, MISSING_TYPE))
        check.isinstance(self.reorder, (bool, MISSING_TYPE))
        check.isinstance(self.allow_setattr, (bool, str, ta.Iterable, MISSING_TYPE))
        check.isinstance(self.iterable, (bool, MISSING_TYPE))
        check.isinstance(self.mangler, (lang.Callable, None, MISSING_TYPE))
        check.isinstance(self.aspects, (ta.Collection, None, MISSING_TYPE))
        check.isinstance(self.confer, (ta.Collection, ta.Mapping, None, MISSING_TYPE))
        check.isinstance(self.kwargs, (ta.Mapping, None, MISSING_TYPE))

        if self.confer is not dc.MISSING and self.confer is not None:
            check.arg(not isinstance(self.confer, str))
            check.empty(set(self.confer) - CONFERS)


check.empty(set(inspect.signature(dc.dataclass).parameters) & {f.name for f in dc.fields(ExtraParams)})


EXTRA_PARAMS_CONFER_DEFAULTS = {
    fld.name: fld.default
    for fld in getattr(ExtraParams, FIELDS).values()
}


@dc.dataclass(frozen=True)
class MetaclassParams(lang.Final):
    slots: bool = False
    no_weakref: bool = False
    abstract: bool = False
    final: bool = False
    sealed: ta.Union[bool, str] = False

    def __post_init__(self) -> None:
        check.isinstance(self.slots, (bool, MISSING_TYPE))
        check.isinstance(self.no_weakref, (bool, MISSING_TYPE))
        check.isinstance(self.abstract, (bool, MISSING_TYPE))
        check.isinstance(self.final, (bool, MISSING_TYPE))
        check.isinstance(self.sealed, (bool, str, MISSING_TYPE))


METACLASS_PARAMS_CONFER_DEFAULTS = {
    fld.name: fld.default
    for fld in getattr(MetaclassParams, FIELDS).values()
}


CONFERS = set(check.unique([a for l in [
    PARAMS_CONFER_DEFAULTS,
    EXTRA_PARAMS_CONFER_DEFAULTS,
    METACLASS_PARAMS_CONFER_DEFAULTS,
] for a in l]))


@dc.dataclass(frozen=True)
class Original(ta.Generic[T], lang.Final):
    type: ta.Type[T]


Mangled = str
Unmangled = ta.Optional[str]


class Mangling(ta.Dict[Mangled, Unmangled]):
    pass


class Unmangling(ta.Dict[Unmangled, Mangled]):
    pass


class _Placeholder(lang.Marker):
    pass
