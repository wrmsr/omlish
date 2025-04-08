import typing as ta
import warnings

from omlish import lang


if ta.TYPE_CHECKING:
    from markdown_it import MarkdownIt


##


@lang.cached_function(lock=True)
def markdown_parser() -> ta.Optional['MarkdownIt']:
    try:
        from markdown_it import MarkdownIt
    except ModuleNotFoundError:
        warnings.warn('The markdown parser requires `markdown-it-py` to be installed')
        return None

    parser = (
        MarkdownIt()
        .enable('linkify')
        .enable('table')
        .enable('strikethrough')
    )

    try:
        import mdit_py_plugins  # noqa F401
    except ModuleNotFoundError:
        pass
    else:
        from mdit_py_plugins.amsmath import amsmath_plugin  # noqa
        from mdit_py_plugins.dollarmath.index import dollarmath_plugin  # noqa
        from mdit_py_plugins.texmath.index import texmath_plugin  # noqa

        parser.use(texmath_plugin)
        parser.use(dollarmath_plugin)
        parser.use(amsmath_plugin)

    return parser
