"""
Broken-link callback hook.

When inline parsing encounters a reference link whose label isn't in the refdef table - either because the doc has no
such refdef, or because we're streaming and it would only appear later - the parser consults a `BrokenLinkResolver`.
Default behavior is to emit the link with a `*_UNKNOWN` `LinkType` and no destination; an alternative resolver may
supply a fallback URL / title.

Cf. `pulldown-cmark/src/parse.rs::ParserCallbacks::handle_broken_link` and `BrokenLink`. Simpler than the rust version
because Python has no per-callback monomorphization concerns; we use a small protocol instead of generics.
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .events import LinkType


##


@dc.dataclass(frozen=True)
class BrokenLink:
    span: tuple[int, int]
    link_type: LinkType
    reference: str


@dc.dataclass(frozen=True)
class BrokenLinkResolution:
    dest_url: str
    title: str


class BrokenLinkResolver(lang.Abstract):
    """
    Subclass and override `resolve` to supply a destination for unresolved reference links.

    Called by the inline parser when a `[label][ref]` / `[label][]` / `[label]` shortcut links references a label not in
    the refdef table. Return `None` to leave the link unresolved (renders as literal bracketed text); return a
    `BrokenLinkResolution(dest_url, title)` to materialize the link with that destination. The link's `LinkType` is
    forced to the corresponding `*_UNKNOWN` variant so callers can distinguish resolved-via-fallback links.

    Cf. pulldown-cmark/src/parse.rs::ParserCallbacks::handle_broken_link.
    """

    @ta.final
    def __call__(self, link: BrokenLink) -> BrokenLinkResolution | None:
        return self.resolve(link)

    def resolve(self, link: BrokenLink) -> BrokenLinkResolution | None:
        raise NotImplementedError


class NoopBrokenLinkResolver(BrokenLinkResolver):
    def resolve(self, link: BrokenLink) -> BrokenLinkResolution | None:
        return None


NOOP_BROKEN_LINK_RESOLVER = NoopBrokenLinkResolver()
