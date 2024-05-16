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
import abc
import asyncio
import typing as ta

import asyncssh

from omlish import dataclasses as dc
from omlish import lang
from omlish import logs

from ..secrets import load_secrets


class SshCommandRunner(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Config:
        host: ta.Optional[str] = None
        port: ta.Optional[int] = None

        username: ta.Optional[str] = None
        password: ta.Optional[str] = None

        key_file_path: ta.Optional[str] = None


class CommandRunner(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Command:
        pass

    @dc.dataclass(frozen=True)
    class CommandResult:
        rc: int

    @abc.abstractmethod
    async def run_command(self, cmd: Command) -> CommandResult:
        raise NotImplementedError


async def _a_main() -> None:
    logs.configure_standard_logging()

    cfg = load_secrets()

    print(cfg)

    # asyncssh.set_log_level('DEBUG')
    # asyncssh.set_debug_level(3)

    async with asyncssh.connect(
            cfg['ec2_ssh_host'],
            username=cfg['ec2_ssh_user'],
            client_keys=[cfg['ec2_ssh_key_file']],
    ) as conn:
        result = await conn.run('echo "Hello!"', check=True)
        print(result.stdout, end='')

    async with asyncssh.connect(
            cfg['lambdalabs_ssh_host'],
            username=cfg['lambdalabs_ssh_user'],
            client_keys=[cfg['lambdalabs_ssh_key_file']],
            known_hosts=None,
    ) as conn:
        result = await conn.run('echo "Hello!"', check=True)
        print(result.stdout, end='')

    async with asyncssh.connect(
            cfg['runpod_ssh_host'],
            username=cfg['runpod_ssh_user'],
            port=cfg['runpod_ssh_port'],
            client_keys=[cfg['runpod_ssh_key_file']],
    ) as conn:
        result = await conn.run('echo "Hello!"', check=True)
        print(result.stdout, end='')


if __name__ == '__main__':
    asyncio.run(_a_main())
