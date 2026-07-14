# ruff: noqa: PT009
import unittest

from omcore.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omcore.subprocesses.sync import subprocesses

from ..shell import ShellCmd


class TestShell(unittest.IsolatedAsyncioTestCase):
    def test_shell_cmd(self) -> None:
        cmd = ShellCmd('uname -a')
        o = cmd.run(
            subprocesses.check_output,
        )
        print(o.decode())

    async def test_shell_cmd_async(self) -> None:
        cmd = ShellCmd('uname -a')
        o = await cmd.run(
            asyncio_subprocesses.check_output,
        )
        print(o.decode())

    def test_shell_cmd_env(self) -> None:
        cmd = ShellCmd('echo "$BARF"')
        o = cmd.run(
            subprocesses.check_output,
            env={'BARF': 'foo'},
        )
        self.assertEqual(o.decode().strip(), 'foo')
