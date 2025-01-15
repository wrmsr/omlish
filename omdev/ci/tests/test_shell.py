import unittest

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.subprocesses import subprocesses

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
