import os.path

import pytest

from ..main import _run_mode_cfg
from ..profiles import ChatProfile


@pytest.mark.asyncs('asyncio')
async def test_chat(tmp_path):
    db_file_path = os.path.join(str(tmp_path), 'state.db')

    await _run_mode_cfg(ChatProfile().configure([
        '-bdummy',
        '-n',
        '--db', db_file_path,
        'hi',
    ]))
