import json
import os.path

from .. import utils as u


TIMEBOMB_DELAY_S = 20 * 60

SCRIPT_TEMP_FILE = False
PYCHARM_DEBUG = False


def _main() -> None:
    img_name = 'wrmsr/omlish-sup-demo'
    cur_dir = os.path.dirname(__file__)

    u.build_docker_image(img_name, cur_dir)
    with u.launch_docker_container(
            img_name,
            '-p', '9322:22',
            '-p', '9380:80',
            '-p', '9343:443',
            timebomb_delay_s=TIMEBOMB_DELAY_S,
    ) as ctr_id:
        cfg = dict(
            python_bin='python3.12',
            app_name='omlish',
            repo_url='https://github.com/wrmsr/omlish',
            revision='d2002c719fcba45d30b9d0e288f317478315f534',
            requirements_txt='requirements.txt',
            entrypoint='omserv.server.tests.hello',
        )

        ##

        with open(os.path.join(os.path.dirname(__file__), 'scripts/supdeploy.py')) as f:
            buf = f.read()

        if PYCHARM_DEBUG:
            buf = u.pycharm_debug_preamble(43251) + '\n' * 2 + buf

        if SCRIPT_TEMP_FILE:
            fname = u.write_docker_temp_file(ctr_id, buf.encode())
            u.check_call([
                'docker', 'exec', '-i', ctr_id,
                'python3', fname, 'deploy', json.dumps(cfg),
            ])

        else:
            u.run([
                'docker', 'exec', '-i', ctr_id,
                'python3', '-', 'deploy', json.dumps(cfg),
            ], input=buf.encode(), check=True)


if __name__ == '__main__':
    _main()
