import typing as ta
import unittest

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.lite.check import check

from ....core import PipelineChannel
from ....handlers.queues import InboundQueueChannelPipelineHandler
from ...requests import PipelineHttpRequestAborted
from ...requests import PipelineHttpRequestContentChunkData
from ...requests import PipelineHttpRequestEnd
from ...requests import PipelineHttpRequestHead
from ..objects import PipelineHttpObjectDecoder


class PipelineHttpRequestDecoder(PipelineHttpObjectDecoder):
    @property
    def _parse_mode(self) -> HttpParser.Mode:
        return HttpParser.Mode.REQUEST

    def _make_head(self, parsed: ParsedHttpMessage) -> PipelineHttpRequestHead:
        request = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=request.method,
            target=check.not_none(request.request_target).decode('utf-8'),
            version=request.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def _make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpRequestAborted(reason)

    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpRequestContentChunkData(data)

    def _make_end(self) -> ta.Any:
        return PipelineHttpRequestEnd()


class TestPipelineHttpRequestHeadDecoder(unittest.TestCase):
    def test_basic_request_head(self) -> None:
        decoder = PipelineHttpRequestDecoder()
        channel = PipelineChannel(PipelineChannel.Spec([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ]).update_pipeline_config(raise_immediately=True))

        request = b'GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertIsInstance(head, PipelineHttpRequestHead)
        self.assertEqual(head.method, 'GET')
        self.assertEqual(head.target, '/path')
        self.assertEqual(head.headers.single.get('host'), 'example.com')
