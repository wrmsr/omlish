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
from omlish import logs

if ta.TYPE_CHECKING:
    import asyncssh
else:
    asyncssh = lang.proxy_import('asyncssh')

from ..secrets import load_secrets


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


@dc.dataclass(frozen=True)
class SshConfig:
    host: ta.Optional[str] = None
    port: ta.Optional[int] = None

    username: ta.Optional[str] = None
    password: ta.Optional[str] = None

    key_file_path: ta.Optional[str] = None


class SshSubprocessCommandRunner(CommandRunner):
    def __init__(
            self,
            cfg: SshConfig,
            lcr: ta.Optional[LocalCommandRunner] = None,
    ) -> None:
        super().__init__()
        self._cfg = check.isinstance(cfg, SshConfig)
        self._lcr = check.isinstance(lcr, LocalCommandRunner) if lcr is not None else LocalCommandRunner()

    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        args = ['ssh']

        if self._cfg.key_file_path is not None:
            args.extend(['-i', self._cfg.key_file_path])

        if self._cfg.port is not None:
            args.extend(['-p', str(self._cfg.port)])

        dst = check.non_empty_str(self._cfg.host)
        if self._cfg.username is not None:
            dst = f'{self._cfg.username}@{dst}'
        if self._cfg.password is not None:
            raise NotImplementedError

        args.append(dst)
        args.extend(cmd.args)
        lcmd = CommandRunner.Command(
            args=args,
            in_=cmd.in_,
        )
        return await self._lcr.run_command(lcmd)


async def _a_main() -> None:
    cmd = CommandRunner.Command(
        ['ls', '-al'],
    )

    rc = await LocalCommandRunner().run_command(cmd)
    check.equal(rc.rc, 0)
    print(rc.out.decode())

    cfg = load_secrets()

    sc = SshConfig(
        host=cfg['ec2_ssh_host'],
        username=cfg['ec2_ssh_user'],
        key_file_path=cfg['ec2_ssh_key_file'],
    )

    rc = await SshSubprocessCommandRunner(sc).run_command(cmd)
    check.equal(rc.rc, 0)
    print(rc.out.decode())


if __name__ == '__main__':
    asyncio.run(_a_main())
