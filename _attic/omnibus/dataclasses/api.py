"""
TODO:
 - DC.REPLACE
  - __dataclass_replace__
  - builtin doesn't validate *or* coerce
 - option to freeze after post_init
  - frozen_after_post_init? frozen='post' ?
 - Field options:
  - transient (+cache_hash)
  - *default_factory with lambda args* - toposort again
 - Class options:
  - coerce: True=just call w val, cls-lvl default on/off, unary void callable
  - validate: True=default, cls-lvl default on/off, unary void callable ...
  - iterable: ta.Union[Iterability, str], enum Iterability: VALUES, KEYS, ITEMS
   - VALUES = namedtuple compat, destructuring
  - validation 'profiles' including str_is_not_seq
 - typecheck defaults on def
 - pyo3 + cy struct type interop
  - derive dataclasses from external
 - observable? dc.observe? per-cls/per-field? config-lvl?
 - intern? class-level, can intern fields w/ just coerce
 - freeze a non-frozen dc
 - lazy derivers
 - gen
  - interops:
   - protobuf
   - thrift
   - jsonschema
   - avro
  - incl enums
  - extend w functions? grpc/twirp/thrift?
 - partial validation - subclass?
 - standard named aspect packs: tuple, dict, pyrsistent
  - 'profiles' - will also be in serde too (but keep eye on inj interop)
   - * frozen coercion profile - frozenlist for seq, frozendict for mapping
    - use for pure
 - ** CYTHON **
  - dogfood CacheLink
  - with jitted/compiled dataclasses ~can bypass dict hits~...
  - maven style classpath scan at build, hash/cmp structure at boot, use if present / warn if not
   - just like tok
 - sql interop? https://marshmallow-sqlalchemy.readthedocs.io/en/latest/
 - enforce immut metadata
 - replace aspect phases w/ dag?
 - dc.touch
  - dc.property? cached if frozen? dc.init then? dc.eager vs dc.lazy? properties.cached but dc aware?
 - want frozen + internal fields - dc.PrivateVar? per-field frozen? both
 - om.properties *hooks*? dc-awareness injected by importing dc? make lazyprop know to _-prefix?
  - ** explicit support for cached at least **
 - memoize predicate/factory/specialmethod?
  - workaround its done in .of() lols
 - WIRE:
  -
"""
import collections
import collections.abc
import copy
import dataclasses as dc
import functools
import keyword
import types
import typing  # noqa
import typing as ta
import weakref

from . import process
from .. import lang
from .internals import DataclassParams
from .internals import is_dataclass_instance
from .kwargs import update_field_kwargs_metadata
from .types import Checker
from .types import Deriver
from .types import ExtraFieldParams
from .types import ExtraParams
from .types import Extras
from .types import Mangler
from .types import Metadata
from .types import METADATA_ATTR
from .types import MISSING_TYPE
from .types import PostInit
from .types import Validator


_reflect = lang.proxy_import('.reflect', __package__)


T = ta.TypeVar('T')


Field = dc.Field
FrozenInstanceError = dc.FrozenInstanceError
InitVar = dc.InitVar
is_dataclass = dc.is_dataclass
MISSING = dc.MISSING
replace = dc.replace


def make_dataclass(
        cls_name: str,
        fields: ta.Union[str, ta.Tuple],
        *,
        bases: ta.Iterable[type] = (),
        namespace: ta.MutableMapping[str, ta.Any] = None,
        **kwargs
) -> type:
    if namespace is None:
        namespace = {}
    else:
        namespace = namespace.copy()

    seen = set()
    anns = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            namespace[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifiers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        anns[name] = tp

    namespace['__annotations__'] = anns
    cls = types.new_class(cls_name, tuple(bases), {}, lambda ns: ns.update(namespace))
    return dataclass(cls, **kwargs)


def fields(class_or_instance: ta.Union[type, object]) -> ta.Iterable[Field]:
    return dc.fields(class_or_instance)


def fields_dict(class_or_instance) -> ta.Dict[str, Field]:
    return {f.name: f for f in fields(class_or_instance)}


def asdict(obj, *, dict_factory=dict, shallow=False):
    if not is_dataclass_instance(obj):
        raise TypeError('asdict() should be called on dataclass instances')
    if shallow:
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    # https://bugs.python.org/issue35540
    if is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, collections.defaultdict):
        return type(obj)(obj.default_factory, ((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory)) for k, v in obj.items()))  # noqa
    elif isinstance(obj, dict):
        return type(obj)((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory)) for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


def astuple(obj, *, tuple_factory=tuple):
    if not is_dataclass_instance(obj):
        raise TypeError('astuple() should be called on dataclass instances')
    return _astuple_inner(obj, tuple_factory)


def _astuple_inner(obj, tuple_factory):
    if is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _astuple_inner(getattr(obj, f.name), tuple_factory)
            result.append(value)
        return tuple_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_astuple_inner(v, tuple_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_astuple_inner(v, tuple_factory) for v in obj)
    elif isinstance(obj, collections.defaultdict):
        return type(obj)(obj.default_factory, ((_asdict_inner(k, tuple_factory), _asdict_inner(v, tuple_factory)) for k, v in obj.items()))  # noqa
    elif isinstance(obj, dict):
        return type(obj)((_astuple_inner(k, tuple_factory), _astuple_inner(v, tuple_factory)) for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


def field(
        default: ta.Union[ta.Any, MISSING_TYPE] = MISSING,
        *,
        default_factory: ta.Union[ta.Callable[[], ta.Any], MISSING_TYPE] = MISSING,
        init: bool = True,
        repr: bool = True,
        hash: ta.Optional[bool] = None,
        compare: bool = True,
        metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None,

        new: ta.Union[ta.Callable[[], ta.Any], MISSING_TYPE] = MISSING,

        doc: ta.Optional[str] = None,
        mangled: ta.Optional[str] = None,
        size: ta.Optional[ta.Any] = None,
        frozen: ta.Optional[bool] = None,
        kwonly: bool = False,
        coerce: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], ta.Any]]] = None,
        derive: ta.Optional[ta.Callable[..., ta.Any]] = None,
        check: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], bool]]] = None,
        check_type: ta.Union[ta.Type, ta.Tuple, None] = None,
        validate: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], None]]] = None,
        repr_if: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
        repr_fn: ta.Optional[ta.Callable[[ta.Any], str]] = None,

        **kwargs,
) -> Field:
    if new is not MISSING:
        if default_factory is not MISSING:
            raise TypeError('May not specify both default_factory and new (an alias for default_factory)')
        default_factory, new = new, MISSING

    extra_field_params = ExtraFieldParams(
        doc=doc,
        mangled=mangled,
        size=size,
        frozen=frozen,
        kwonly=kwonly,
        coerce=coerce,
        derive=derive,
        check=check,
        check_type=check_type,
        validate=validate,
        repr_if=repr_if,
        repr_fn=repr_fn,
        kwargs=kwargs,
    )

    if metadata is not None:
        if not isinstance(metadata, ta.Mapping):
            raise TypeError(metadata)
    else:
        metadata = {}

    if ExtraFieldParams in metadata:
        raise KeyError(metadata, ExtraFieldParams)
    metadata[ExtraFieldParams] = extra_field_params

    fld = dc.field(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
    )

    fld.metadata = types.MappingProxyType(update_field_kwargs_metadata(fld, kwargs, metadata))
    return fld


def dataclass(
        _cls: ta.Optional[ta.Type[T]] = None,
        *,
        init: ta.Union[bool, MISSING_TYPE] = MISSING,  # True
        repr: ta.Union[bool, MISSING_TYPE] = MISSING,  # True
        eq: ta.Union[bool, MISSING_TYPE] = MISSING,  # True
        order: ta.Union[bool, MISSING_TYPE] = MISSING,  # False
        unsafe_hash: ta.Union[bool, MISSING_TYPE] = MISSING,  # False
        frozen: ta.Union[bool, MISSING_TYPE] = MISSING,  # False

        metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None,
        validate: ta.Union[bool, MISSING_TYPE] = MISSING,
        field_attrs: ta.Union[bool, MISSING_TYPE] = MISSING,
        kwonly: ta.Union[None, bool, MISSING_TYPE] = MISSING,
        cache_hash: ta.Union[bool, str, MISSING_TYPE] = MISSING,
        strict_eq: ta.Union[bool, MISSING_TYPE] = MISSING,
        pickle: ta.Union[bool, MISSING_TYPE] = MISSING,
        reorder: ta.Union[bool, MISSING_TYPE] = MISSING,
        allow_setattr: ta.Union[bool, str, ta.Iterable[str], MISSING_TYPE] = MISSING,
        iterable: ta.Union[bool, MISSING_TYPE] = MISSING,
        mangler: ta.Union[Mangler, MISSING_TYPE] = MISSING,
        aspects: ta.Union[None, ta.Sequence[ta.Any], MISSING_TYPE] = MISSING,
        confer: ta.Union[None, ta.Sequence[str], ta.Mapping[str, ta.Any], MISSING_TYPE] = MISSING,

        **kwargs
) -> ta.Type[T]:
    if aspects is not MISSING and aspects is not None:
        aspects = list(aspects)
    if confer is not MISSING and confer is not None:
        confer = dict(confer) if isinstance(confer, ta.Mapping) else set(confer)

    if metadata is not None:
        if not isinstance(metadata, ta.Mapping):
            raise TypeError(metadata)
    else:
        metadata = {}

    params = DataclassParams(
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
    )

    extra_params = ExtraParams(
        metadata=metadata,
        validate=validate,
        field_attrs=field_attrs,
        kwonly=kwonly,
        cache_hash=cache_hash,
        strict_eq=strict_eq,
        pickle=pickle,
        reorder=reorder,
        allow_setattr=allow_setattr,
        iterable=iterable,
        mangler=mangler,
        aspects=aspects,
        confer=confer,
        kwargs=kwargs,
    )

    def build(cls):
        ctx = process.Context(cls, params, extra_params)
        drv = process.Driver(ctx)
        drv()
        return cls

    if _cls is None:
        return build
    return build(_cls)


@lang.cls_dct_fn()
def _install(cls_dct, cls, *args, **kwargs):
    if len(args) == 1 and isinstance(args[0], cls):
        [obj] = args
        ret = obj
    else:
        obj = cls(*args, **kwargs)
        ret = args[0] if args else None
    cls_dct.setdefault(METADATA_ATTR, {}).setdefault(Extras, []).append(obj)
    return ret


check_ = functools.partial(_install, Checker)
derive = functools.partial(_install, Deriver)
post_init = functools.partial(_install, PostInit)
validate = functools.partial(_install, Validator)


@lang.cls_dct_fn()
def metadata(cls_dct, *args, **kwargs) -> None:
    objs = []
    for arg in args:
        if isinstance(arg, Metadata):
            objs.append(arg)
        elif isinstance(arg, ta.Mapping):
            objs.append(Metadata(dict(arg)))
        else:
            raise TypeError(arg)
    if kwargs:
        objs.append(Metadata(kwargs))
    cls_dct.setdefault(METADATA_ATTR, {}).setdefault(Extras, []).extend(objs)


_METADATAS_CACHE: ta.Mapping[bool, ta.MutableMapping[type, ta.Sequence[ta.Mapping[ta.Any, ta.Any]]]] = \
    {shallow: weakref.WeakKeyDictionary() for shallow in [False, True]}


def metadatas(cls: type, *, shallow: bool = False) -> ta.Sequence[ta.Mapping[ta.Any, ta.Any]]:
    try:
        return _METADATAS_CACHE[shallow][cls]
    except KeyError:
        if not isinstance(cls, type) or not is_dataclass(cls):  # type: ignore
            raise TypeError(cls)
        spec = _reflect.get_cls_spec(cls)  # noqa
        if shallow:
            mds = spec.shallow_extras_by_cls[Metadata]
        else:
            mds = spec.rmro_extras_by_cls[Metadata]
        ret = _METADATAS_CACHE[shallow][cls] = tuple(md.metadata for md in mds)
        return ret


def metadatas_dict(cls: type, *, shallow: bool = False) -> ta.Mapping[ta.Any, ta.Any]:
    dct = {}
    for cdct in metadatas(cls, shallow=shallow):
        dct.update(cdct)
    return dct


def _only_test(v: ta.Any) -> bool:
    if v is None:
        return False
    elif isinstance(v, collections.abc.Iterable):
        return bool(v)
    else:
        return True


def only(
        obj: ta.Any,
        flds: ta.Iterable[str],
        *,
        all: bool = False,
        test: ta.Callable[[ta.Any], bool] = _only_test,
) -> bool:
    if isinstance(flds, str):
        raise TypeError(flds)
    fdct = fields_dict(obj)
    for fn in flds:
        if fn not in fdct:
            raise KeyError(fn)
    rem = set(flds)
    for fn, f in fdct.items():
        if not f.compare and fn not in rem:
            continue
        v = getattr(obj, fn)
        if test(v):
            if fn in rem:
                rem.remove(fn)
            else:
                return False
    if rem and all:
        return False
    return True
