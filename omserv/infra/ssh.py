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


async def _a_main() -> None:
    with open('secrets.yml', 'r') as f:
        cfg = yaml.safe_load(f)

    print(cfg)

    async with asyncssh.connect(
            cfg['ec2_ssh_host'],
            username=cfg['ec2_ssh_user'],
            client_keys=[cfg['ec2_ssh_key_file']],
    ) as conn:
        result = await conn.run('echo "Hello!"', check=True)
        print(result.stdout, end='')


if __name__ == '__main__':
    asyncio.run(_a_main())
