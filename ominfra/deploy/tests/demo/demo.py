"""
FIXME:
 - ubuntu installs py3.10 lols
"""
import asyncio
import os.path
import typing as ta

from omlish import check
from omlish.docker import timebomb_payload
from omlish.testing.pydevd import silence_subprocess_check

from .... import cmds
from .... import ssh
from ...deploy import do_deploy


TIMEBOMB_DELAY_S = 20 * 60


async def _a_main():
    silence_subprocess_check()

    img_name = 'wrmsr/omlish-deploy-demo'
    cur_dir = os.path.dirname(__file__)

    async def check_call(cmd: ta.Sequence[str], **kwargs: ta.Any) -> None:
        proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
        await proc.wait()
        if proc.returncode:
            raise Exception(f'process failed: {proc.returncode}')

    async def check_output(cmd: ta.Sequence[str], **kwargs: ta.Any) -> bytes:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, **kwargs)
        await proc.wait()
        if proc.returncode:
            raise Exception(f'process failed: {proc.returncode}')
        return await check.not_none(proc.stdout).read()

    await check_call([
        'docker', 'build',
        '--tag', img_name,
        '-f', os.path.join(cur_dir, 'Dockerfile'),
        cur_dir,
    ])

    ssh_password = 'foobar'  # noqa

    ctr_id = (await check_output([
        'docker', 'run',
        '-d',
        '-e', f'SSH_PASSWORD={ssh_password}',
        '-p', '9082:22',
        '-p', '9081:9081',
        img_name,
    ])).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            await check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

        cr: cmds.CommandRunner = ssh.AsyncsshSshCommandRunner(ssh.SshConfig(
            host='localhost',
            port=9082,
            username='root',
            password=ssh_password,
        ))

        try:
            await do_deploy(
                cr,
                skip_submodules=True,
            )
        except Exception as e:  # noqa
            print(e)

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    finally:
        await check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    asyncio.run(_a_main())
