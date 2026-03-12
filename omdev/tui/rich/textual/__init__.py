from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    from .dark import TEXTUAL_DARK  # noqa

    from .themes import (  # noqa
        DumpedTextualTheme,

        build_pygments_theme,
        build_theme,
    )
