import io
import json

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ..payload import _payload_loop  # noqa
from ..payload import CommandRequest
from ..payload import CommandResponse


def test_payload_loop():
    reqs = [
        CommandRequest(cmd=['echo', 'hi']),
        CommandRequest(cmd=['uptime']),
    ]
    input = io.BytesIO()
    for req in reqs:
        input.write(json_dumps_compact(marshal_obj(req)).encode('utf-8'))
        input.write(b'\n')
    input.write(b'\n')
    input.seek(0)
    output = io.BytesIO()
    _payload_loop(input, output)
    output.seek(0)
    resps = [
        unmarshal_obj(json.loads(l.decode('utf-8')), CommandResponse)
        for l in input.readlines()
        if l.strip()
    ]
    print(resps)
