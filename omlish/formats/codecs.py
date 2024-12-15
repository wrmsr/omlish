import typing as ta

from .. import codecs


##


class ObjectCodec(codecs.Codec):
    pass


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

        input=bytes,
        output=bytes,

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
