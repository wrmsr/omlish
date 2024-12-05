"""
FIXME:
 - ubuntu installs py3.10 lols
"""
import asyncio
import os.path

from ..... import cmds
from ..... import ssh
from ...remote import do_remote_deploy
from .. import utils as u


TIMEBOMB_DELAY_S = 20 * 60


async def _a_main():
    img_name = 'wrmsr/omlish-deploy-demo'
    cur_dir = os.path.dirname(__file__)
    u.build_docker_image(img_name, cur_dir)

    ssh_password = 'foobar'  # noqa

    with u.launch_docker_container(
            '-e', f'SSH_PASSWORD={ssh_password}',
            '-p', '9082:22',
            '-p', '9081:9081',
            img_name,
            timebomb_delay_s=TIMEBOMB_DELAY_S,
    ) as ctr_id:  # noqa
        cr: cmds.CommandRunner = ssh.AsyncsshSshCommandRunner(ssh.SshConfig(
            host='localhost',
            port=9082,
            username='root',
            password=ssh_password,
        ))

        try:
            await do_remote_deploy(
                cr,
                skip_submodules=True,
            )

        except Exception as e:  # noqa
            print(e)


if __name__ == '__main__':
    asyncio.run(_a_main())
