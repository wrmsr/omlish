"""
These attempt to punch through *all* wrappers. The the usecases involve having things like bound methods, classmethods,
functools.partial instances, and needing to get the metadata of the underlying thing the end-user wrote.

TODO:
 - re type targets:
  - unwrap instances of objects to their types?
  - merge mro?
  - are these better left up to callers? too usecase-specific to favor either way?
"""
import threading
import types
import typing as ta

from . import check
from . import lang


T = ta.TypeVar('T')


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
    tgt: ta.Any = obj
    tgt = lang.unwrap_func(tgt)

    if not isinstance(tgt, _VALID_OBJECT_METADATA_TARGET_TYPES):
        raise ObjectMetadataTargetTypeError(tgt)

    return tgt


##


_OBJECT_METADATA_LOCK = threading.RLock()

_OBJECT_METADATA_ATTR = '__' + __name__.replace('.', '_') + '__metadata__'


def append_object_metadata(obj: T, *mds: ObjectMetadata) -> T:
    for md in mds:
        check.isinstance(md, ObjectMetadata)

    tgt = _unwrap_object_metadata_target(obj)
    dct = tgt.__dict__

    if isinstance(dct, types.MappingProxyType):
        try:
            lst = dct[_OBJECT_METADATA_ATTR]
        except KeyError:
            with _OBJECT_METADATA_LOCK:
                try:
                    lst = dct[_OBJECT_METADATA_ATTR]
                except KeyError:
                    setattr(tgt, _OBJECT_METADATA_ATTR, lst := [])

    else:
        lst = dct.setdefault(_OBJECT_METADATA_ATTR, [])

    lst.extend(mds)
    return obj


def get_object_metadata(obj: ta.Any, *, strict: bool = False) -> ta.Sequence[ObjectMetadata]:
    try:
        tgt = _unwrap_object_metadata_target(obj)
    except ObjectMetadataTargetTypeError:
        if not strict:
            return ()
        raise

    try:
        dct = tgt.__dict__
    except AttributeError:
        return ()

    return dct.get(_OBJECT_METADATA_ATTR, ())


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
            setattr(cls, '_OBJECT_METADATA_TARGET_TYPES', tts)

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
