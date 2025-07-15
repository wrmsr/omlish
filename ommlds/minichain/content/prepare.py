"""
TODO:
 - inject[ability], obviously
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import lang

from .materialize import CanContent
from .materialize import materialize_content
from .transforms.interleave import interleave_content
from .transforms.squeeze import squeeze_content
from .transforms.stringify import stringify_content
from .types import Content


##


class ContentPreparer(lang.Abstract):
    @abc.abstractmethod
    def prepare(self, c: CanContent) -> Content:
        raise NotImplementedError


class ContentStrPreparer(lang.Abstract):
    @abc.abstractmethod
    def prepare_str(self, c: CanContent) -> str:
        raise NotImplementedError


##


DEFAULT_BLOCK_SEPARATOR = '\n\n'


@dc.dataclass(frozen=True)
class DefaultContentPreparer(ContentPreparer):
    _: dc.KW_ONLY

    strip_strings: bool = True
    block_separator: Content = DEFAULT_BLOCK_SEPARATOR

    def prepare(self, c: CanContent) -> Content:
        c = materialize_content(c)
        c = squeeze_content(c, strip_strings=self.strip_strings)
        c = interleave_content(c, block_separator=self.block_separator)
        return c


@dc.dataclass(frozen=True)
class DefaultContentStrPreparer(ContentStrPreparer):
    content_preparer: ContentPreparer

    def prepare_str(self, c: CanContent) -> str:
        return stringify_content(self.content_preparer.prepare(c))


##


def prepare_content(c: CanContent, **kwargs: ta.Any) -> Content:
    return DefaultContentPreparer(**kwargs).prepare(c)


def prepare_content_str(c: CanContent, **kwargs: ta.Any) -> str:
    return DefaultContentStrPreparer(DefaultContentPreparer(**kwargs)).prepare_str(c)
