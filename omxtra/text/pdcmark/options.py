"""
Parser options + presets.

Cf. `pulldown-cmark/src/lib.rs::Options` (bitflags). We use a frozen `kw_only` dataclass instead; it's more
discoverable, supports non-boolean fields (depth caps, fuel, broken-link resolver), and composes via `dc.replace` for
preset variants.
"""
from omcore import dataclasses as dc

from .brokenlinks import BrokenLinkResolver


##


@dc.dataclass(frozen=True, kw_only=True)
class Options:
    # Extensions.
    tables: bool = False
    strikethrough: bool = False
    tasklists: bool = False
    gfm_blockquote_kinds: bool = False  # [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION]

    # Resource bounds (DoS mitigation). Defaults mirror pulldown-cmark.
    max_nested_parens: int = 32  # pulldown-cmark/src/parse.rs::LINK_MAX_NESTED_PARENS
    max_container_depth: int = 32
    link_ref_expansion_min: int = 100_000  # cf. parse.rs::ParserInner::link_ref_expansion_limit

    # Oneshot-only: do a quick pre-pass to collect refdefs so forward-references resolve. Ignored by `StreamingParser`,
    # which cannot look ahead.
    prescan_refdefs: bool = False

    # Hook for unresolved reference links. None means "use the no-op resolver" - link is emitted with a `*_UNKNOWN`
    # LinkType.
    broken_link_resolver: BrokenLinkResolver | None = None


COMMONMARK = Options()

GFM = dc.replace(
    COMMONMARK,
    tables=True,
    strikethrough=True,
    tasklists=True,
    gfm_blockquote_kinds=True,
)
