import json

from omlish import marshal as msh

from ..types import Content
from ..types import Message
from ..types import Text
from ..types import ToolResult
from ..types import ToolUse


def test_marshal():
    msg = Message(
        role='user',
        content=(
            Text('hi'),
            Text('hi eph', cache_control=Content.EphemeralCacheControl()),
            ToolUse('abc', 'foo', {'arg': 'huh'}),
            ToolResult('abc', 'what'),
        ),
    )

    mm = msh.marshal(msg)
    mj = json.dumps(mm)
    print(mj)

    msg2 = msh.unmarshal(json.loads(mj), Message)
    assert msg == msg2
