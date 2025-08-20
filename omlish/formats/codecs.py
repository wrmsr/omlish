import typing as ta

from .. import codecs
from .. import reflect as rfl


ObjectCodecT = ta.TypeVar('ObjectCodecT', bound='ObjectCodec')


##


class ObjectCodec(codecs.Codec):
    pass


def make_object_codec(
        cls: type[ObjectCodecT],
        name: str,
        dumps: ta.Callable,
        loads: ta.Callable,
        *,
        input: rfl.Type,  # noqa
        output: rfl.Type = rfl.type_(ta.Any),
        aliases: ta.Sequence[str] | None = None,
) -> ObjectCodecT:
    return cls(
        name=name,
        aliases=aliases,

        input=input,
        output=output,

        new=lambda: codecs.FnPairEagerCodec.of(dumps, loads),
    )


##


class BytesObjectCodec(ObjectCodec):
    pass


def make_bytes_object_codec(
        name: str,
        dumps: ta.Callable[[ta.Any], bytes],
        loads: ta.Callable[[bytes], ta.Any],
        **kwargs: ta.Any,
) -> BytesObjectCodec:
    return make_object_codec(
        BytesObjectCodec,
        name,
        dumps,
        loads,
        input=bytes,
        **kwargs,
    )


##


class StrObjectCodec(ObjectCodec):
    pass


def make_str_object_codec(
        name: str,
        dumps: ta.Callable[[ta.Any], str],
        loads: ta.Callable[[str], ta.Any],
        **kwargs: ta.Any,
) -> StrObjectCodec:
    return make_object_codec(
        StrObjectCodec,
        name,
        dumps,
        loads,
        input=str,
        **kwargs,
    )


##


def make_object_lazy_loaded_codec(
        module: str,
        attr: str,
        codec: ObjectCodec,
) -> codecs.LazyLoadedCodec:
    return codecs.LazyLoadedCodec.new(
        module,
        attr,
        codec,
    )
