import io
import typing as ta

from omlish import lang


with lang.auto_proxy_import(globals()):
    import rich.console


##


def console_render(obj: ta.Any, **kwargs: ta.Any) -> str:
    temp_console = rich.console.Console(
        file=(out := io.StringIO()),
        **kwargs,
    )
    temp_console.print(obj)
    return out.getvalue()
