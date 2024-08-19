"""
FIXME:
 - ubuntu installs py3.10 lols
"""
import asyncio
import os.path

from ominfra.deploy.tests import utils as u


TIMEBOMB_DELAY_S = 20 * 60


async def _a_main():
    img_name = 'wrmsr/omlish-pyremote-demo'
    cur_dir = os.path.dirname(__file__)
    u.build_docker_image(img_name, cur_dir)

    ssh_password = 'foobar'  # noqa

    with u.launch_docker_container(
            '-e', f'SSH_PASSWORD={ssh_password}',
            '-p', '9092:22',
            img_name,
            timebomb_delay_s=TIMEBOMB_DELAY_S,
    ) as ctr_id:  # noqa
        try:
            pass

        except Exception as e:  # noqa
            print(e)


if __name__ == '__main__':
    asyncio.run(_a_main())
