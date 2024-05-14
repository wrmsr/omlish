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

import asyncssh
import yaml

from omlish import logs


async def _a_main() -> None:
    logs.configure_standard_logging()

    with open('secrets.yml', 'r') as f:
        cfg = yaml.safe_load(f)

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
