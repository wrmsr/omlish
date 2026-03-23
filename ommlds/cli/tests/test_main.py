import pytest

from ..main import _run_mode_cfg
from ..profiles import ChatProfile


@pytest.mark.asyncs('asyncio')
async def test_chat():
    await _run_mode_cfg(ChatProfile().configure([
        '-bdummy',
        '--ephemeral',
        'hi',
    ]))
