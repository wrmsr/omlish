import typing as ta

from omlish.text import templating as tpl

from .namespaces import ContentNamespace
from .placeholders import ContentPlaceholder
from .placeholders import ContentPlaceholderMarker
from .types import ExtendedContent


##


_InnerCanContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,

    ContentPlaceholder,
    type[ContentPlaceholderMarker],

    type[ContentNamespace],

    tpl.Templater,
]

CanContent: ta.TypeAlias = ta.Union[  # noqa
    ta.Iterable['CanContent'],

    None,

    _InnerCanContent,
]
