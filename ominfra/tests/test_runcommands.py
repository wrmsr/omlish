# ruff: noqa: UP006 PT009
import io
import json
import typing as ta
import unittest

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from .runcommands import CommandRequest
from .runcommands import CommandResponse
from .runcommands import _run_commands_loop  # noqa


class TestPayload(unittest.TestCase):
    def test_payload_loop(self):
        reqs = [
            CommandRequest(cmd=['echo', 'hi']),
            CommandRequest(cmd=['uptime']),
            CommandRequest(cmd=['false']),
        ]
        input = io.BytesIO()  # noqa
        for req in reqs:
            input.write(json_dumps_compact(marshal_obj(req)).encode('utf-8'))
            input.write(b'\n')
        input.write(b'\n')
        input.seek(0)
        output = io.BytesIO()
        _run_commands_loop(input, output)
        output.seek(0)
        resps: ta.List[CommandResponse] = [
            unmarshal_obj(json.loads(l.decode('utf-8')), CommandResponse)
            for l in output.readlines()
            if l.strip()
        ]
        self.assertEqual(len(resps), 3)
        self.assertEqual(resps[0].rc, 0)
        self.assertEqual(resps[0].out, b'hi\n')
        self.assertEqual(resps[1].rc, 0)
        self.assertEqual(resps[2].rc, 1)
