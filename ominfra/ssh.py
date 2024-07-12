"""
https://github.com/ronf/asyncssh

bcrypt
fido2
gssapi
libnacl
pkcs11
pyOpenSSL

asyncssh[bcrypt,fido2,gssapi,libnacl,pkcs11,pyOpenSSL]
"""
import asyncio
import shlex
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

if ta.TYPE_CHECKING:
    import asyncssh
else:
    asyncssh = lang.proxy_import('asyncssh')

from .cmds import CommandRunner
from .cmds import LocalCommandRunner
from .secrets import load_secrets


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


class AsyncsshSshCommandRunner(CommandRunner):
    def __init__(
            self,
            cfg: SshConfig,
    ) -> None:
        super().__init__()
        self._cfg = check.isinstance(cfg, SshConfig)

    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        arg = ' '.join(map(shlex.quote, cmd.args))

        async with asyncssh.connect(
                self._cfg.host,
                encoding=None,
                **(dict(port=int(self._cfg.port)) if self._cfg.port is not None else {}),
                **(dict(username=self._cfg.username) if self._cfg.username is not None else {}),
                **(dict(password=self._cfg.password) if self._cfg.password is not None else {}),
                **(dict(client_keys=[self._cfg.key_file_path]) if self._cfg.key_file_path is not None else {}),
                known_hosts=None,
        ) as conn:
            async with await conn.create_process(arg) as proc:
                checkw = False
                timeout = None
                res = await proc.wait(checkw, timeout)

        return CommandRunner.Result(
            rc=check.not_none(res.returncode),
            out=check.isinstance(res.stdout, bytes),
            err=check.isinstance(res.stderr, bytes),
        )


async def _a_main() -> None:
    cmd = CommandRunner.Command(
        ['ls', '-al'],
    )

    cfg = load_secrets()

    sc = SshConfig(
        host=cfg['ec2_ssh_host'],
        username=cfg['ec2_ssh_user'],
        key_file_path=cfg['ec2_ssh_key_file'],
    )

    for scr in [
        SshSubprocessCommandRunner(sc),
        AsyncsshSshCommandRunner(sc),
    ]:
        rc = await scr.run_command(cmd)
        check.equal(rc.rc, 0)
        print(rc.out.decode())


if __name__ == '__main__':
    asyncio.run(_a_main())
