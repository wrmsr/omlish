import pytest

from ..main import ChatProfile


@pytest.mark.asyncs('asyncio')
async def test_chat():
    await ChatProfile().run([
        '-bdummy',
        '--ephemeral',
        'hi',
    ])
