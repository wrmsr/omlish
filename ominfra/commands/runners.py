"""
TODO:
 - timeout
 - stream in/out/err
 - *sessions*
 - anyio
"""
import abc
import asyncio
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


class CommandRunner(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Command:
        args: ta.Sequence[str]
        in_: bytes | None = None

    @dc.dataclass(frozen=True)
    class Result:
        rc: int
        out: bytes
        err: bytes

        def check(self) -> ta.Self:
            if self.rc != 0:
                raise CommandRunner.ReturnCodeError(self)
            return self

    class ReturnCodeError(Exception):
        def __init__(self, result: 'CommandRunner.Result') -> None:
            super().__init__(f'Bad return code: {result.rc}', result)

            self.result = result

    @abc.abstractmethod
    async def run_command(self, cmd: Command) -> Result:
        raise NotImplementedError


class LocalCommandRunner(CommandRunner):
    @dc.dataclass(frozen=True)
    class Config:
        cwd: str | None = None

    def __init__(self, cfg: Config = Config()) -> None:
        super().__init__()

        self._cfg = check.isinstance(cfg, LocalCommandRunner.Config)

    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        proc = await asyncio.create_subprocess_exec(
            *cmd.args,
            stdin=io.BytesIO(cmd.in_) if cmd.in_ is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **(dict(cwd=self._cfg.cwd) if self._cfg.cwd is not None else {}),  # type: ignore
        )

        out, err = await proc.communicate()

        return CommandRunner.Result(
            rc=check.not_none(proc.returncode),
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
