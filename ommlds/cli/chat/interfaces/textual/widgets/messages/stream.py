# ruff: noqa: SLF001
import abc
import io
import typing as ta
import uuid

from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import Message
from .base import MessageFinalized


##


StreamMessageState: ta.TypeAlias = ta.Literal[  # noqa
    'new',
    'new_finalizing',
    'streaming',
    'finalized',
]


@dc.dataclass(frozen=True)
class StreamMessagePart(lang.Abstract):
    message_cls: type[StreamMessage]
    message_uuid: uuid.UUID


@dc.dataclass(frozen=True)
class ContentStreamMessagePart(StreamMessagePart):
    content: str


@dc.dataclass(frozen=True)
class FinalStreamMessagePart(StreamMessagePart):
    pass


class StreamMessage(Message, lang.Abstract):
    def __init__(
            self,
            *initial_contents: str,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._initial_contents: list[str] = list(initial_contents)

        self._state: StreamMessageState = 'new'

    @property
    def state(self) -> StreamMessageState:
        return self._state

    #

    @property
    def message_content(self) -> ta.Any | None:
        match self._state:
            case 'new':
                return None
            case 'finalized':
                return self._final_content
            case _:
                return self._stream_content.getvalue()

    #

    _final_content: str

    @property
    def final_content(self) -> str:
        check.state(self._state == 'finalized')
        return self._final_content

    #

    _stream_content: io.StringIO

    @ta.final
    async def start_stream(self) -> None:
        check.state(self._state in ('new', 'new_finalizing'))

        self._stream_content = io.StringIO()

        await self._start_stream_content()

        if (ics := self._initial_contents):
            for ic in ics:
                self._stream_content.write(ic)
                await self._append_stream_content(ic)

        del self._initial_contents

        if self._state == 'new':
            self._state = 'streaming'

        elif self._state == 'new_finalizing':
            await self._finalize_stream()

        else:
            raise RuntimeError(f'unexpected state: {self._state}')

    @abc.abstractmethod
    async def _start_stream_content(self) -> None:
        raise NotImplementedError

    async def append_stream_content(self, content: str) -> None:
        if not content:
            return

        if self._state == 'new':
            self._initial_contents.append(content)

        elif self._state == 'streaming':
            self._stream_content.write(content)
            await self._append_stream_content(content)

        else:
            raise RuntimeError(f'unexpected state: {self._state}')

    @abc.abstractmethod
    async def _append_stream_content(self, c: str) -> None:
        raise NotImplementedError

    async def _finalize_stream(self) -> None:
        await self._finalize_stream_content()

        self._final_content = self._stream_content.getvalue()
        del self._stream_content

        self._state = 'finalized'

        self.post_message(MessageFinalized(self))

    @abc.abstractmethod
    async def _finalize_stream_content(self) -> None:
        raise NotImplementedError

    async def finalize_stream(self) -> None:
        if self._state == 'new':
            self._state = 'new_finalizing'

        elif self._state == 'streaming':
            await self._finalize_stream()

        else:
            raise RuntimeError(f'unexpected state: {self._state}')


#


class MarkdownStreamMessage(StreamMessage, lang.Abstract):
    _stream: tx.MarkdownStream

    async def _start_stream_content(self) -> None:
        self._stream = tx.Markdown.get_stream(self.query_one(tx.Markdown))

    async def _append_stream_content(self, c: str) -> None:
        await self._stream.write(c)

    async def _finalize_stream_content(self) -> None:
        await self._stream.stop()
        del self._stream
