import typing as ta

from .. import codecs
from .. import reflect as rfl


##


class ObjectCodec(codecs.Codec):
    pass


##


class BytesObjectCodec(ObjectCodec):
    pass


def make_bytes_object_codec(
        name: str,
        dumps: ta.Callable[[ta.Any], bytes],
        loads: ta.Callable[[bytes], ta.Any],
        *,
        aliases: ta.Collection[str] | None = None,
) -> BytesObjectCodec:
    return BytesObjectCodec(
        name=name,
        aliases=aliases,

        input=rfl.type_(ta.Any),
        output=bytes,

        new=lambda: codecs.FnPairEagerCodec.of(dumps, loads),
    )


##


class StrObjectCodec(ObjectCodec):
    pass


def make_str_object_codec(
        name: str,
        dumps: ta.Callable[[ta.Any], str],
        loads: ta.Callable[[str], ta.Any],
        *,
        aliases: ta.Collection[str] | None = None,
) -> StrObjectCodec:
    return StrObjectCodec(
        name=name,
        aliases=aliases,

        input=rfl.type_(ta.Any),
        output=str,

        new=lambda: codecs.FnPairEagerCodec.of(dumps, loads),
    )


##


def make_object_lazy_loaded_codec(
        mod_name: str,
        attr_name: str,
        codec: ObjectCodec,
) -> codecs.LazyLoadedCodec:
    return codecs.LazyLoadedCodec.new(
        mod_name,
        attr_name,
        codec,
    )
