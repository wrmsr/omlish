"""
TODO:
 - inject[ability], obviously
"""
import typing as ta

from .materialize import CanContent
from .materialize import materialize_content
from .transforms.interleave import interleave_content
from .transforms.squeeze import squeeze_content
from .transforms.stringify import stringify_content
from .types import Content


##


DEFAULT_BLOCK_SEPARATOR = '\n\n'


def prepare_content(
        c: CanContent,
        *,
        strip_strings: bool = True,
        block_separator: Content = DEFAULT_BLOCK_SEPARATOR,
) -> Content:
    c = materialize_content(c)
    c = squeeze_content(c, strip_strings=strip_strings)
    c = interleave_content(c, block_separator=block_separator)
    return c


def prepare_content_str(c: CanContent, **kwargs: ta.Any) -> str:
    return stringify_content(prepare_content(c, **kwargs))
