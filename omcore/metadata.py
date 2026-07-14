# ruff: noqa: SLF001
"""
These attempt to punch through *all* wrappers. The the usecases involve having things like bound methods, classmethods,
functools.partial instances, and needing to get the metadata of the underlying thing the end-user wrote.

Notably, there is no way to remove metadata once applied - this is intentional.

====

TODO:
 - re type targets:
  - unwrap instances of objects to their types?
  - merge mro?
  - are these better left up to callers? too usecase-specific to favor either way?
 - unique? too much? turns into just typedvalues?
  - ... typedvalues?
 - mro-merge cache?
  - hm, flag to make sure md ctrs present on all baseclasses, then under lock.. something?
  - ctrs contain lazy strong mro parent + weakref child links?
  - result is one single 'cache_ver' int, usable as key part into separate external cache (like a tv.TypedValues coll)
 - dc.Field target type?
  - no, but maybe a Map[str, ...] helper? maybe a merging helper?
"""
import threading
import types
import typing as ta

from . import check
from . import lang


T = ta.TypeVar('T')

ObjectMetadataT = ta.TypeVar('ObjectMetadataT', bound='ObjectMetadata')


##


class ObjectMetadata(lang.Abstract):
    pass


class ObjectMetadataTarget(lang.Abstract):
    pass


##


_VALID_OBJECT_METADATA_TARGET_TYPES: tuple[type, ...] = (
    type,

    types.FunctionType,
    # *not* types.MethodType - must unwrap to unbound class func
    # *not* functools.partial - must unwrap to underlying func

    ObjectMetadataTarget,
)


class ObjectMetadataTargetTypeError(TypeError):
    pass


def _unwrap_object_metadata_target(obj: ta.Any) -> ta.Any:
    if isinstance(obj, type):
        return obj

    tgt: ta.Any = obj
    tgt = lang.unwrap_func(tgt)

    if not isinstance(tgt, _VALID_OBJECT_METADATA_TARGET_TYPES):
        raise ObjectMetadataTargetTypeError(tgt)

    return tgt


##


@ta.final
class _ObjectMetadataState:
    def __init__(self, ver: int, seq: ta.Sequence[ta.Any]) -> None:
        self._ver = ver
        self._seq = seq

    @property
    def ver(self) -> int:
        return self._ver

    @property
    def seq(self) -> ta.Sequence[ta.Any]:
        return self._seq

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._ver}, {self._seq!r})'


_EMPTY_OBJECT_METADATA_STATE = _ObjectMetadataState(0, ())


#


@ta.final
class _ObjectMetadataContainer:
    __slots__ = ('_state',)

    def __init__(self, state: _ObjectMetadataState) -> None:
        self._state = state

    @property
    def state(self) -> _ObjectMetadataState:
        return self._state

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._state!r})'


##


_OBJECT_METADATA_LOCK = threading.Lock()

_OBJECT_METADATA_ATTR = '__' + __name__.replace('.', '_') + '__metadata__'


def append_object_metadata(obj: T, *mds: ObjectMetadata) -> T:
    if not mds:
        return obj

    for md in mds:
        check.isinstance(md, ObjectMetadata)

    tgt = _unwrap_object_metadata_target(obj)
    dct = tgt.__dict__

    with _OBJECT_METADATA_LOCK:
        if isinstance(dct, types.MappingProxyType):
            try:
                ctr = dct[_OBJECT_METADATA_ATTR]
            except KeyError:
                setattr(tgt, _OBJECT_METADATA_ATTR, ctr := _ObjectMetadataContainer(_EMPTY_OBJECT_METADATA_STATE))

        else:
            try:
                ctr = dct[_OBJECT_METADATA_ATTR]
            except KeyError:
                dct[_OBJECT_METADATA_ATTR] = ctr = _ObjectMetadataContainer(_EMPTY_OBJECT_METADATA_STATE)

        ctr._state = _ObjectMetadataState(ctr._state._ver + 1, (*ctr._state._seq, *mds))

    return obj


##


def has_object_metadata(
        obj: ta.Any,
        *,
        non_strict: bool = False,
) -> bool:
    try:
        tgt = _unwrap_object_metadata_target(obj)
    except ObjectMetadataTargetTypeError:
        if non_strict:
            return False
        raise

    return hasattr(tgt, _OBJECT_METADATA_ATTR)


#


_type = type


@ta.overload
def get_object_metadata(
        obj: ta.Any,
        *,
        non_strict: bool = False,
        mro_merge: bool = False,
        type: ta.Type[ObjectMetadataT],  # noqa
) -> ta.Sequence[ObjectMetadataT]:
    ...


@ta.overload
def get_object_metadata(
        obj: ta.Any,
        *,
        non_strict: bool = False,
        mro_merge: bool = False,
        type: ta.Type | tuple[ta.Type, ...] | None = None,  # noqa
) -> ta.Sequence[ta.Any]:
    ...


def get_object_metadata(
        obj,
        *,
        non_strict=False,
        mro_merge=False,
        type=None,  # noqa
):
    try:
        tgt = _unwrap_object_metadata_target(obj)
    except ObjectMetadataTargetTypeError:
        if non_strict:
            return ()
        raise

    if mro_merge and isinstance(tgt, _type):
        tgt_lst: ta.Sequence[ta.Any] = tgt.__mro__[-2::-1]
    else:
        tgt_lst = (tgt,)

    ret: list = []

    for cur in tgt_lst:
        try:
            dct = cur.__dict__
        except AttributeError:
            continue

        try:
            cur_ctr = dct[_OBJECT_METADATA_ATTR]
        except KeyError:
            continue
        cur_mds = cur_ctr._state._seq
        if not cur_mds:
            continue

        if type is not None:
            for o in cur_mds:
                if isinstance(o, type):
                    ret.append(o)
        else:
            ret.extend(cur_mds)

    return ret


#


@ta.overload
def get_single_object_metadata(
        obj: ta.Any,
        *,
        non_strict: bool = False,
        mro_merge: bool = False,
        type: ta.Type[ObjectMetadataT],  # noqa
) -> ObjectMetadataT | None:
    ...


@ta.overload
def get_single_object_metadata(
        obj: ta.Any,
        *,
        non_strict: bool = False,
        mro_merge: bool = False,
        type: ta.Type | tuple[ta.Type, ...] | None = None,  # noqa
) -> ta.Any | None:
    ...


def get_single_object_metadata(
        obj,
        *,
        non_strict=False,
        mro_merge=False,
        type=None,  # noqa
):
    try:
        tgt = _unwrap_object_metadata_target(obj)
    except ObjectMetadataTargetTypeError:
        if non_strict:
            return ()
        raise

    if mro_merge and isinstance(tgt, _type):
        tgt_lst: ta.Sequence[ta.Any] = tgt.__mro__[:-1]
    else:
        tgt_lst = (tgt,)

    for cur in tgt_lst:
        try:
            dct = cur.__dict__
        except AttributeError:
            continue

        try:
            cur_ctr = dct[_OBJECT_METADATA_ATTR]
        except KeyError:
            continue
        cur_mds = cur_ctr._state._seq
        if not cur_mds:
            continue

        if type is not None:
            for o in reversed(cur_mds):
                if isinstance(o, type):
                    return o
        else:
            return cur_mds[-1]

    return None


##


class DecoratorObjectMetadata(ObjectMetadata, lang.Abstract):
    _OBJECT_METADATA_TARGET_TYPES: ta.ClassVar[tuple[type, ...] | None] = None

    def __init_subclass__(
            cls,
            *,
            object_metadata_target_types: ta.Iterable[type] | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        if object_metadata_target_types is not None:
            tts = tuple(object_metadata_target_types)
            for tt in tts:
                check.issubclass(tt, _VALID_OBJECT_METADATA_TARGET_TYPES)
            cls._OBJECT_METADATA_TARGET_TYPES = tts

    def __call__(self, obj: T) -> T:
        tgt: ta.Any = obj
        if (tts := type(self)._OBJECT_METADATA_TARGET_TYPES) is not None:  # noqa
            tgt = _unwrap_object_metadata_target(tgt)
            check.isinstance(tgt, tts)

        append_object_metadata(tgt, self)
        return obj


#


class ClassDecoratorObjectMetadata(
    DecoratorObjectMetadata,
    lang.Abstract,
    object_metadata_target_types=[type],
):
    pass


class FunctionDecoratorObjectMetadata(
    DecoratorObjectMetadata,
    lang.Abstract,
    object_metadata_target_types=[types.FunctionType],
):
    pass
