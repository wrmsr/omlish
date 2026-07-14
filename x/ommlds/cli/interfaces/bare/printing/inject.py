from omlish import inject as inj
from omlish import lang

from .configs import PrintingConfig


with lang.auto_proxy_import(globals()):
    from . import markdown as _markdown
    from . import raw as _raw
    from . import types as _types


##


def bind_printing(cfg: PrintingConfig = PrintingConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.markdown:
        els.extend([
            inj.bind(_types.ContentPrinting, to_ctor=_markdown.MarkdownContentPrinting, singleton=True),
            inj.bind(_types.StreamContentPrinting, to_ctor=_markdown.MarkdownStreamContentPrinting, singleton=True),
        ])

    else:
        els.extend([
            inj.bind(_types.ContentPrinting, to_ctor=_raw.RawContentPrinting, singleton=True),
            inj.bind(_types.StreamContentPrinting, to_ctor=_raw.RawStreamContentPrinting, singleton=True),
        ])

    return inj.as_elements(*els)
