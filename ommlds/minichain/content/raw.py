import typing as ta

from .images import ImageContent
from .text import TextContent


##


NonStrSingleRawContent: ta.TypeAlias = ta.Union[  # noqa
    TextContent,
    ImageContent,
]


NON_STR_SINGLE_RAW_CONTENT_TYPES: tuple[type, ...] = (
    TextContent,
    ImageContent,
)


#


SingleRawContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    NonStrSingleRawContent,
]


SINGLE_RAW_CONTENT_TYPES: tuple[type, ...] = (
    str,
    *NON_STR_SINGLE_RAW_CONTENT_TYPES,
)


#


RawContent: ta.TypeAlias = ta.Union[  # noqa
    SingleRawContent,
    ta.Sequence[SingleRawContent],
]


RAW_CONTENT_TYPES: tuple[type, ...] = (
    *SINGLE_RAW_CONTENT_TYPES,
    ta.Sequence,
)
