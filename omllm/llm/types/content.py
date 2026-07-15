import abc
import io
import typing as ta

from omcore import check
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
    text: str


@ta.final
class TextContentBuilder(ContentBuilder[TextContent]):
    def __init__(self) -> None:
        super().__init__()

        self.text = io.StringIO()

    def build(self) -> TextContent:
        return TextContent(
            text=self.text.getvalue(),
        )


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class ThinkingContent(Content):
    text: str


@ta.final
class ThinkingContentBuilder(ContentBuilder[ThinkingContent]):
    def __init__(self) -> None:
        super().__init__()

        self.text = io.StringIO()

    def build(self) -> ThinkingContent:
        return ThinkingContent(
            text=self.text.getvalue(),
        )


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ToolCall(Content):
    id: str
    name: str
    args: ta.Mapping[str, ta.Any]


class ToolCallBuilder(ContentBuilder[ToolCall]):
    def __init__(self) -> None:
        super().__init__()

        self.id: str | None = None
        self.name: str | None = None
        self.args: ta.Mapping[str, ta.Any] | None = None

    def build(self) -> ToolCall:
        return ToolCall(
            id=check.non_empty_str(self.id),
            name=check.non_empty_str(self.name),
            args=check.not_none(self.args),
        )
