from omlish import inject as inj
from omlish import lang

from .configs import RenderingConfig


with lang.auto_proxy_import(globals()):
    from . import markdown as _markdown
    from . import raw as _raw
    from . import types as _types


##


def bind_rendering(cfg: RenderingConfig = RenderingConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.markdown:
        els.extend([
            inj.bind(_types.ContentRendering, to_ctor=_markdown.MarkdownContentRendering, singleton=True),
            inj.bind(_types.StreamContentRendering, to_ctor=_markdown.MarkdownStreamContentRendering, singleton=True),
        ])

    else:
        els.extend([
            inj.bind(_types.ContentRendering, to_ctor=_raw.RawContentRendering, singleton=True),
            inj.bind(_types.StreamContentRendering, to_ctor=_raw.RawStreamContentRendering, singleton=True),
        ])

    return inj.as_elements(*els)
