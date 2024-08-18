# -*- coding: utf-8 -*-


import asyncio
import io
import os
import pytest
import signal

from aiotk import mock_subprocess
from aiotk._testing import Process, OutputStreamAdapter
from unittest import mock


@pytest.mark.asyncio
async def test_process(event_loop):

    async def run():
        return 456

    process = Process(
        pid=123,
        run=run,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 456
    assert process.returncode == 456


@pytest.mark.asyncio
async def test_process_status(event_loop):

    async def run():
        pass

    process = Process(
        pid=123,
        run=run,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 0
    assert process.returncode == 0


@pytest.mark.asyncio
async def test_process_stdout(event_loop):

    async def run(stdout):
        stdout.write(b'FUBAR')
        return 456

    process = Process(
        pid=123,
        run=run,
        stdout=asyncio.subprocess.PIPE,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 456
    assert process.returncode == 456
    stdout = await asyncio.wait_for(process.stdout.read(), timeout=5.0)
    assert stdout == b'FUBAR'


@pytest.mark.asyncio
async def test_process_stdout_no_redirect(event_loop, capsys):

    async def run(stdout):
        stdout.write(b'FUBAR')
        return 456

    process = Process(
        pid=123,
        run=run,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    await asyncio.wait_for(process.communicate(), timeout=5.0)
    assert process.returncode == 456
    stdout, _ = capsys.readouterr()
    assert stdout == 'FUBAR'


@pytest.mark.asyncio
async def test_process_stderr(event_loop):

    async def run(stderr):
        stderr.write(b'FUBAR')
        return 456

    process = Process(
        pid=123,
        run=run,
        stderr=asyncio.subprocess.PIPE,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 456
    assert process.returncode == 456
    stderr = await asyncio.wait_for(process.stderr.read(), timeout=5.0)
    assert stderr == b'FUBAR'


@pytest.mark.asyncio
async def test_process_stderr_no_redirect(event_loop, capsys):

    async def run(stderr):
        stderr.write(b'FUBAR')
        return 456

    process = Process(
        pid=123,
        run=run,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    await asyncio.wait_for(process.communicate(), timeout=5.0)
    assert process.returncode == 456
    _, stderr = capsys.readouterr()
    assert stderr == 'FUBAR'


@pytest.mark.asyncio
async def test_process_stdin(event_loop):

    async def run(stdin):
        message = await asyncio.wait_for(stdin.read(), timeout=5.0)
        assert message == b'FUBAR'
        return 456

    process = Process(
        pid=123,
        run=run,
        stdin=asyncio.subprocess.PIPE,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    process.stdin.write(b'FUBAR')
    process.stdin.write_eof()
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 456
    assert process.returncode == 456


@pytest.mark.asyncio
async def test_process_communicate(event_loop):

    async def run(stdin, stdout, stderr):
        message = await asyncio.wait_for(stdin.read(), timeout=5.0)
        assert message == b'FUBAR'
        stdout.write(b'THIS IS')
        stderr.write(b'SPARTA!')
        return 456

    process = Process(
        pid=123,
        run=run,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    stdout, stderr = await asyncio.wait_for(
        process.communicate(input=b'FUBAR'), timeout=5.0
    )
    assert process.returncode == 456
    assert stdout == b'THIS IS'
    assert stderr == b'SPARTA!'


@pytest.mark.asyncio
async def test_process_signals(event_loop):

    async def run(signals):
        sig = await asyncio.wait_for(signals.get(), timeout=5.0)
        assert sig == 789
        return 456

    process = Process(
        pid=123,
        run=run,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    process.send_signal(789)
    status = await asyncio.wait_for(
        process.wait(), timeout=5.0
    )
    assert status == 456
    assert process.returncode == 456


@pytest.mark.asyncio
async def test_process_exception(event_loop):

    async def run(stderr):
        raise Exception('BLARGH!')

    process = Process(
        pid=123,
        run=run,
        stderr=asyncio.subprocess.PIPE,
        loop=event_loop,
    )
    assert process.pid == 123
    assert process.returncode is None
    status = await asyncio.wait_for(process.wait(), timeout=5.0)
    assert status == 1
    assert process.returncode == 1
    stderr = await asyncio.wait_for(process.stderr.read(), timeout=5.0)
    lines = stderr.strip().split(b'\n')
    assert lines[0] == b'Traceback (most recent call last):'
    assert lines[-1] == b'Exception: BLARGH!'


@pytest.mark.asyncio
async def test_mock_subprocess(event_loop):

    async def run(stdin, stdout, stderr):
        message = await asyncio.wait_for(stdin.read(), timeout=5.0)
        assert message == b'FUBAR'
        stdout.write(b'THIS IS')
        stderr.write(b'SPARTA!')
        return 456

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=b'FUBAR'), timeout=5.0
        )
        assert process.returncode == 456
        assert stdout == b'THIS IS'
        assert stderr == b'SPARTA!'


@pytest.mark.asyncio
async def test_mock_subprocess_argv_defaults(event_loop):

    async def run(argv):
        assert argv == []

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        status = await asyncio.wait_for(process.wait(), timeout=5.0)
        assert status == 0
        assert process.returncode == 0


@pytest.mark.asyncio
async def test_mock_subprocess_argv(event_loop):

    async def run(argv):
        assert argv == ['a', 'b', 'c']

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            'a', 'b', 'c',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        status = await asyncio.wait_for(process.wait(), timeout=5.0)
        assert status == 0
        assert process.returncode == 0


@pytest.mark.asyncio
async def test_mock_subprocess_env_default(event_loop):

    async def run(env):
        assert env == os.environ
        assert env is not os.environ

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        status = await asyncio.wait_for(process.wait(), timeout=5.0)
        assert status == 0
        assert process.returncode == 0


@pytest.mark.asyncio
async def test_mock_subprocess_env(event_loop):

    async def run(env):
        assert env == {
            'A': 'B',
            'C': 'D',
        }

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                'A': 'B',
                'C': 'D',
            },
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        status = await asyncio.wait_for(process.wait(), timeout=5.0)
        assert status == 0
        assert process.returncode == 0


@pytest.mark.asyncio
async def test_mock_subprocess_kwds(event_loop):

    async def run(kwds):
        assert kwds == {
            'creationflags': 512,
        }

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=512,  # subprocess.CREATE_NEW_PROCESS_GROUP
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        status = await asyncio.wait_for(process.wait(), timeout=5.0)
        assert status == 0
        assert process.returncode == 0


@pytest.mark.asyncio
async def test_mock_subprocess_terminate(event_loop):

    async def run():
        await asyncio.wait_for(asyncio.Future(), timeout=5.0)

    with mock_subprocess(run):
        process = await asyncio.create_subprocess_exec(
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=512,  # subprocess.CREATE_NEW_PROCESS_GROUP
            loop=event_loop,
        )
        assert process.pid != 0
        assert process.returncode is None
        process.terminate()
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=5.0
        )
        assert process.returncode == 1
        assert stdout == b''
        assert stderr == b''


@pytest.mark.parametrize('platform', [
    'darwin',
    'linux',
])
@pytest.mark.asyncio
async def test_mock_subprocess_kill_posix(platform, event_loop):

    async def run(signals):
        sig = await asyncio.wait_for(signals.get(), timeout=5.0)
        assert sig == signal.SIGINT

    with mock.patch('sys.platform', platform):
        with mock_subprocess(run):
            process = await asyncio.create_subprocess_exec(
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=512,  # subprocess.CREATE_NEW_PROCESS_GROUP
                loop=event_loop,
            )
            assert process.pid != 0
            assert process.returncode is None
            process.kill()
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=5.0
            )
            assert process.returncode == 0
            assert stdout == b''
            assert stderr == b''


@pytest.mark.asyncio
async def test_mock_subprocess_kill_win32(event_loop):

    async def run():
        await asyncio.wait_for(asyncio.Future(), timeout=5.0)

    with mock.patch('sys.platform', 'win32'):
        with mock_subprocess(run):
            process = await asyncio.create_subprocess_exec(
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                loop=event_loop,
            )
            assert process.pid != 0
            assert process.returncode is None
            process.kill()
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=5.0
            )
            assert process.returncode == 1
            assert stdout == b''
            assert stderr == b''


def test_output_stream_adapter():
    stream = io.StringIO()
    writer = OutputStreamAdapter(stream)
    assert writer.can_write_eof()
    writer.write(b'FUBAR')
    assert stream.getvalue() == 'FUBAR'


def test_output_stream_adapter_writelines():
    stream = io.StringIO()
    writer = OutputStreamAdapter(stream)
    writer.writelines([
        b'FOO',
        b'BAR',
    ])
    assert stream.getvalue() == 'FOO\nBAR\n'
