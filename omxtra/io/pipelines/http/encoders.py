# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import io
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.lite.abstract import Abstract

from .objects import FullPipelineHttpMessage
from .objects import PipelineHttpMessageContentChunkData
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageHead


##


class PipelineHttpObjectEncoder(Abstract):
    def __init__(self) -> None:
        super().__init__()

        self._streaming = False
        self._chunked = False

    #

    @property
    @abc.abstractmethod
    def _head_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageHead]]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _full_type(self) -> ta.Optional[ta.Type[FullPipelineHttpMessage]]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _content_chunk_data_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageContentChunkData]]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _end_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageEnd]]:
        raise NotImplementedError

    @abc.abstractmethod
    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        raise NotImplementedError

    #

    def outbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        ty: ta.Any

        if (ty := self._head_type) is not None and isinstance(msg, ty):
            return self._handle_request_head(msg)

        elif (ty := self._content_chunk_data_type) is not None and isinstance(msg, ty):
            return self._handle_content_chunk_data(msg)

        elif (ty := self._end_type) is not None and isinstance(msg, ty):
            return self._handle_request_end(msg)

        elif (ty := self._full_type) is not None and isinstance(msg, ty):
            return self._handle_full_request(msg)

        else:
            return [msg]

    def _handle_request_head(self, msg: PipelineHttpMessageHead) -> ta.Sequence[ta.Any]:
        """Emit request line + headers, enter streaming mode."""

        self._streaming = True
        self._chunked = self._is_chunked(msg.headers)

        return [self._encode_head(msg)]

    def _handle_content_chunk_data(self, msg: PipelineHttpMessageContentChunkData) -> ta.Sequence[ta.Any]:
        """Emit body chunk (raw or chunked-encoded)."""

        if not self._streaming:
            # Not in streaming mode - pass through unchanged
            return [msg]

        elif len(msg.data) < 1:
            return []

        elif self._chunked:
            # Chunked encoding: <size-hex>\r\n<data>\r\n
            return [
                f'{len(msg.data):x}\r\n'.encode('ascii'),
                msg.data,
                b'\r\n',
            ]

        else:
            # Raw data
            return [msg.data]

    def _handle_request_end(self, msg: PipelineHttpMessageEnd) -> ta.Sequence[ta.Any]:
        """Emit terminator if chunked, reset state."""

        if not self._streaming:
            # Not in streaming mode - pass through
            return [msg]

        was_chunked = self._chunked

        # Reset state
        self._streaming = False
        self._chunked = False

        if was_chunked:
            # Emit final chunk: 0\r\n\r\n
            return [b'0\r\n\r\n']
        else:
            return []

    def _handle_full_request(self, msg: FullPipelineHttpMessage) -> ta.Any:
        """Emit complete request in one shot."""

        return [
            self._encode_head(msg.head),
            *([msg.body] if len(msg.body) > 0 else []),
        ]

    #

    def _encode_head(self, head: PipelineHttpMessageHead) -> bytes:
        buf = io.BytesIO()

        buf.write(self._encode_head_line(head))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        return buf.getvalue()

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        """Encode headers as 'Name: value\r\n' lines."""

        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines

    def _is_chunked(self, headers: HttpHeaders) -> bool:
        """Check if Transfer-Encoding includes 'chunked'."""

        te = headers.lower.get('transfer-encoding', ())
        return 'chunked' in te
