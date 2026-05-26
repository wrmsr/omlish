"""
pdcmark - pure-python streaming markdown parser, modeled on pulldown-cmark.

See docs/00_Goals.md for goals / non-goals, docs/02_PrePlan.md for the streaming model, and docs/03_Plan.md for the
implementation plan and module layout.

Based on pulldown-cmark - see LICENSE file.
~ https://github.com/pulldown-cmark/pulldown-cmark/tree/b93cbc043fe8a24b5ee3868b21299e320e0f7d41
"""


from .brokenlinks import (  # noqa
    BrokenLink,
    BrokenLinkResolution,
    BrokenLinkResolver,
    NOOP_BROKEN_LINK_RESOLVER,
)

from .errors import (  # noqa
    ParserStateError,
    PdcmarkError,
    ResourceLimitExceededError,
)

from .events import (  # noqa
    Alignment,
    BlockQuote,
    BlockQuoteKind,
    Code,
    Emphasis,
    End,
    Event,
    FencedCodeBlock,
    HardBreak,
    Heading,
    Html,
    HtmlBlock,
    Image,
    IndentedCodeBlock,
    InlineHtml,
    Item,
    Link,
    LinkType,
    List,
    Paragraph,
    Rule,
    SoftBreak,
    Start,
    Strikethrough,
    Strong,
    Table,
    TableCell,
    TableHead,
    TableRow,
    Tag,
    TaskListMarker,
    Text,
)

from .options import (  # noqa
    COMMONMARK,
    GFM,
    Options,
)

from .utils.text_merge import (  # noqa
    merge_text,
)

from .parsing import (  # noqa
    parse,
)

from .streaming.output import (  # noqa
    FeedOutput,
)

from .streaming.parser import (  # noqa
    StreamingParser,
)
