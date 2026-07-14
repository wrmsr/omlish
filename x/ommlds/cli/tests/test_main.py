import os.path

import pytest

from ..chat.profiles import ChatProfile
from ..main import _run_entrypoint_cfg


@pytest.mark.asyncs('asyncio')
async def test_chat(tmp_path):
    db_file_path = os.path.join(str(tmp_path), 'state.db')

    await _run_entrypoint_cfg(ChatProfile().configure([
        '-bdummy',
        '-n',
        '--db', db_file_path,
        'hi',
    ]))


@pytest.mark.asyncs('asyncio')
async def test_chat_scripted_oneshot(tmp_path, capsys):
    """
    The whole real cli stack - profile args, registry backend resolution, bare interface, timeline printing -
    offline via the scripted backend's demo script.
    """

    db_file_path = os.path.join(str(tmp_path), 'state.db')

    await _run_entrypoint_cfg(ChatProfile().configure([
        '-bscripted',
        '-n',
        '--db', db_file_path,
        'hello there',
    ]))

    out = capsys.readouterr().out
    assert 'demo script' in out


@pytest.mark.asyncs('asyncio')
async def test_chat_scripted_oneshot_resumes(tmp_path, capsys):
    """Two oneshot runs over the same state db continue the same chat (and the scripted demo loops)."""

    db_file_path = os.path.join(str(tmp_path), 'state.db')

    await _run_entrypoint_cfg(ChatProfile().configure([
        '-bscripted',
        '-n',
        '--db', db_file_path,
        'first',
    ]))

    await _run_entrypoint_cfg(ChatProfile().configure([
        '-bscripted',
        '--db', db_file_path,
        'second',
    ]))

    out = capsys.readouterr().out
    assert 'demo script' in out
