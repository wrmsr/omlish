import typing as ta

from .images import ImageContent
from .text import TextContent


##


SingleRawContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    TextContent,
    ImageContent,
]


SINGLE_RAW_CONTENT_TYPES: tuple[type, ...] = (
    str,
    TextContent,
    ImageContent,
)


#


RawContent: ta.TypeAlias = ta.Union[  # noqa
    SingleRawContent,
    ta.Sequence[SingleRawContent],
]


RAW_CONTENT_TYPES: tuple[type, ...] = (
    str,
    TextContent,
    ImageContent,
    ta.Sequence,
)
