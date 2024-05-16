import abc
import asyncio
import typing as ta

import asyncssh

from omlish import dataclasses as dc
from omlish import lang
from omlish import logs

from ..secrets import load_secrets


class CommandRunner(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Command:
        pass

    @dc.dataclass(frozen=True)
    class Result:
        rc: int

    @abc.abstractmethod
    async def run_command(self, cmd: Command) -> Result:
        raise NotImplementedError


class LocalCommandRunner(CommandRunner):
    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class SshConfig:
    host: ta.Optional[str] = None
    port: ta.Optional[int] = None

    username: ta.Optional[str] = None
    password: ta.Optional[str] = None

    key_file_path: ta.Optional[str] = None


async def _a_main() -> None:
    proc = await asyncio.create_subprocess_exec(
        'ls',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


if __name__ == '__main__':
    asyncio.run(_a_main())
