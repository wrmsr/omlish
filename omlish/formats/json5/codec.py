import typing as ta

from ... import lang
from .. import json
from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec


if ta.TYPE_CHECKING:
    from . import parsing
    from . import rendering
else:
    parsing = lang.proxy_import('.parsing', __package__)
    rendering = lang.proxy_import('.rendering', __package__)


##


def dumps(
        obj: ta.Any,
        *,
        multiline_strings: bool = False,
        **kwargs: ta.Any,
) -> str:
    if multiline_strings:
        return rendering.Json5Renderer.render_str(
            obj,
            multiline_strings=True,
            **kwargs,
        )

    else:
        return json.dumps(obj, **kwargs)


def dumps_pretty(obj: ta.Any, **kwargs: ta.Any) -> str:
    return dumps(obj, **json.PRETTY_KWARGS, **kwargs)


def dumps_compact(obj: ta.Any, **kwargs: ta.Any) -> str:
    return dumps(obj, **json.COMPACT_KWARGS, **kwargs)


def dump(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    fp.write(dumps(obj, **kwargs))


def dump_pretty(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    fp.write(dumps_pretty(obj, **kwargs))


def dump_compact(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    fp.write(dumps_compact(obj, **kwargs))


#


def loads(s: str, **kwargs: ta.Any) -> ta.Any:
    return parsing.parse(s, **kwargs)


def load(fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
    return loads(fp.read(), **kwargs)


##


JSON5_CODEC = make_str_object_codec('json5', dumps, loads)

# @omlish-manifest
_JSON5_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON5_CODEC', JSON5_CODEC)
