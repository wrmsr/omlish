import abc
import io
import typing as ta

from omcore import dataclasses as dc
from omcore import lang


ContentT = ta.TypeVar('ContentT', bound='Content')


##


@dc.dataclass(frozen=True)
class Content(lang.Abstract):
    pass


class ContentBuilder(lang.Abstract, ta.Generic[ContentT]):
    @abc.abstractmethod
    def build(self) -> ContentT:
        raise NotImplementedError


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class TextContent(Content):
    s: str


@ta.final
class TextContentBuilder(ContentBuilder[TextContent]):
    def __init__(self) -> None:
        super().__init__()

        self.s = io.StringIO()

    def build(self) -> TextContent:
        return TextContent(
            s=self.s.getvalue(),
        )


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class ThinkingContent(Content):
    s: str


@ta.final
class ThinkingContentBuilder(ContentBuilder[ThinkingContent]):
    def __init__(self) -> None:
        super().__init__()

        self.s = io.StringIO()

    def build(self) -> ThinkingContent:
        return ThinkingContent(
            s=self.s.getvalue(),
        )
