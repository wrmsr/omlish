"""
TODO:
 - timeout
 - stream in/out/err
"""
import abc
import asyncio
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


class CommandRunner(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Command:
        args: ta.Sequence[str]
        in_: ta.Optional[bytes] = None

    @dc.dataclass(frozen=True)
    class Result:
        rc: int
        out: bytes
        err: bytes

    @abc.abstractmethod
    async def run_command(self, cmd: Command) -> Result:
        raise NotImplementedError


class LocalCommandRunner(CommandRunner):
    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        proc = await asyncio.create_subprocess_exec(
            *cmd.args,
            stdin=cmd.in_,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        out, err = await proc.communicate()

        return CommandRunner.Result(
            rc=proc.returncode,
            out=out,
            err=err,
        )


async def _a_main() -> None:
    cmd = CommandRunner.Command(
        ['ls', '-al'],
    )

    rc = await LocalCommandRunner().run_command(cmd)
    check.equal(rc.rc, 0)
    print(rc.out.decode())


if __name__ == '__main__':
    asyncio.run(_a_main())
