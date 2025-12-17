# ruff: noqa: F401
# flake8: noqa: F401
from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from rich import align  # noqa
    from rich import console  # noqa
    from rich import live  # noqa
    from rich import markdown  # noqa
    from rich import repr  # noqa
    from rich import text  # noqa
    from rich.align import Align  # noqa
    from rich.color import Color  # noqa
    from rich.color import blend_rgb  # noqa
    from rich.color_triplet import ColorTriplet  # noqa
    from rich.console import Console  # noqa
    from rich.console import Group  # noqa
    from rich.live import Live  # noqa
    from rich.markdown import Markdown  # noqa
    from rich.segment import Segment  # noqa
    from rich.segment import SegmentLines  # noqa
    from rich.style import Style  # noqa
    from rich.syntax import Syntax  # noqa
    from rich.table import Table  # noqa
    from rich.text import Text  # noqa
    from rich.theme import Theme  # noqa

    ##

    from .console2 import (  # noqa
        console_render,
    )

    from .markdown2 import (  # noqa
        configure_markdown_parser,
        markdown_from_tokens,
        flatten_tokens_filter,
        flatten_tokens,

        MarkdownLiveStream,
        NaiveMarkdownLiveStream,
        IncrementalMarkdownLiveStream,
    )
