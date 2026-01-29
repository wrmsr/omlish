import pytest

from ..main import _run_session_cfg
from ..profiles import ChatProfile


@pytest.mark.asyncs('asyncio')
async def test_chat():
    await _run_session_cfg(ChatProfile().configure([
        '-bdummy',
        '--ephemeral',
        'hi',
    ]))
