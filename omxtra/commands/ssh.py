"""
TODO:
 - sessionized
 - streamed
 - actual timeout

bcrypt
fido2
gssapi
libnacl
pkcs11
pyOpenSSL

asyncssh[bcrypt,fido2,gssapi,libnacl,pkcs11,pyOpenSSL]
"""
import asyncio
import contextlib
import shlex
import typing as ta

from omdev.home.secrets import load_secrets
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .runners import CommandRunner
from .runners import LocalCommandRunner


if ta.TYPE_CHECKING:
    import asyncssh
    import paramiko
else:
    asyncssh = lang.proxy_import('asyncssh')
    paramiko = lang.proxy_import('paramiko')


##


@dc.dataclass(frozen=True)
class SshConfig:
    host: str | None = None
    port: int | None = None

    username: str | None = None
    password: str | None = None

    key_file_path: str | None = None


class SshSubprocessCommandRunner(CommandRunner):
    def __init__(
            self,
            cfg: SshConfig,
            lcr: LocalCommandRunner | None = None,
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
            proc: asyncssh.SSHClientProcess
            async with await conn.create_process(arg) as proc:
                checkw = False
                timeout = None
                res = await proc.wait(checkw, timeout)

        return CommandRunner.Result(
            rc=check.not_none(res.returncode),
            out=check.isinstance(res.stdout, bytes),
            err=check.isinstance(res.stderr, bytes),
        )


class ParamikoSshCommandRunner(CommandRunner):
    def __init__(
            self,
            cfg: SshConfig,
    ) -> None:
        super().__init__()

        self._cfg = check.isinstance(cfg, SshConfig)

    def _run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        arg = ' '.join(map(shlex.quote, cmd.args))

        kw: dict[str, ta.Any] = {}
        if self._cfg.port is not None:
            kw.update(port=int(self._cfg.port))
        if self._cfg.username is not None:
            kw.update(username=self._cfg.username)
        if self._cfg.password is not None:
            kw.update(password=self._cfg.password)
        if self._cfg.key_file_path is not None:
            kw.update(key_filename=self._cfg.key_file_path)

        client: paramiko.client.SSHClient
        with contextlib.closing(paramiko.client.SSHClient()) as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                check.not_none(self._cfg.host),
                **kw,
            )

            si, so, se = client.exec_command(arg)
            # https://stackoverflow.com/questions/60037299/attributeerror-nonetype-object-has-no-attribute-time-paramiko
            si.close()

            rc = so.channel.recv_exit_status()
            out = so.read()
            err = se.read()

        return CommandRunner.Result(
            rc=rc,
            out=out,
            err=err,
        )

    async def run_command(self, cmd: CommandRunner.Command) -> CommandRunner.Result:
        return await asyncio.to_thread(self._run_command, cmd)


async def _a_main() -> None:
    cmd = CommandRunner.Command(
        ['ls', '-al'],
    )

    cfg = load_secrets()

    sc = SshConfig(
        host=cfg.get('ec2_ssh_host').reveal(),
        username=cfg.get('ec2_ssh_user').reveal(),
        key_file_path=cfg.get('ec2_ssh_key_file').reveal(),
    )

    for scr in [
        SshSubprocessCommandRunner(sc),
        AsyncsshSshCommandRunner(sc),
        ParamikoSshCommandRunner(sc),
    ]:
        rc = await scr.run_command(cmd)
        check.equal(rc.rc, 0)
        print(rc.out.decode())


if __name__ == '__main__':
    asyncio.run(_a_main())
