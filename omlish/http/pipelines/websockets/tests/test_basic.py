# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta
import unittest

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from ..frames import IoPipelineWebsocketFrameDecoder
from ..frames import IoPipelineWebsocketFrameEncoder
from ..handshakes import IoPipelineWebsocketHandshakes
from ..objects import IoPipelineWebsocketFrame
from ..objects import IoPipelineWebsocketOpcode
from ..objects import IoPipelineWebsocketText


class OutboundAdapter(IoPipelineHandler):
    """Converts inbound into outbound to exercise encoders in tests."""

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(msg)


class TestBasic(unittest.TestCase):
    def test_ws_accept_computation(self):
        # From RFC 6455 example
        key = 'dGhlIHNhbXBsZSBub25jZQ=='
        expected_accept = 's3pPLMBiTxaQ9kYGzzhZRbK+xOo='
        assert IoPipelineWebsocketHandshakes.compute_accept_for_key(key) == expected_accept

    def test_text_roundtrip_encode_decode(self):
        # Encode as a client (masking enabled)
        enc = IoPipelineWebsocketFrameEncoder(mask=True)
        p_enc = IoPipeline.new([enc, OutboundAdapter()])

        p_enc.feed_in(IoPipelineWebsocketText('hi'))
        data = p_enc.output.poll()
        assert isinstance(data, (bytes, bytearray))
        assert data is not None and len(data) >= 6  # header + mask + payload

        # Decode as a server (expects masked inbound)
        dec = IoPipelineWebsocketFrameDecoder(expect_masked=True)
        p_dec = IoPipeline(IoPipeline.Spec([dec, ibq := InboundQueueIoPipelineHandler()]))

        p_dec.feed_in(data)

        # Find the decoded frame in the tap
        got = [m for m in ibq.drain() if isinstance(m, IoPipelineWebsocketFrame)]
        assert len(got) >= 1
        f = got[-1]
        assert f.opcode == IoPipelineWebsocketOpcode.TEXT
        assert f.payload == b'hi'
