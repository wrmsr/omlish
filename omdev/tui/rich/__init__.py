# ruff: noqa: F401
# flake8: noqa: F401
from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from rich import console  # noqa
    from rich import live  # noqa
    from rich import markdown  # noqa
    from rich import text  # noqa
    from rich.console import Console  # noqa
    from rich.live import Live  # noqa
    from rich.markdown import Markdown  # noqa
    from rich.text import Text  # noqa

    ##

    from .markdown import (  # noqa
        configure_markdown_parser,
        IncrementalMarkdownRenderer,
    )
