import os.path

import pytest

from ..main import _run_entrypoint_cfg
from ..profiles import ChatProfile


@pytest.mark.asyncs('asyncio')
async def test_chat(tmp_path):
    db_file_path = os.path.join(str(tmp_path), 'state.db')

    await _run_entrypoint_cfg(ChatProfile().configure([
        '-bdummy',
        '-n',
        '--db', db_file_path,
        'hi',
    ]))
