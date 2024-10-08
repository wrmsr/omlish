import os
import subprocess
import threading  # noqa

from omlish.docker import timebomb_payload
from omlish.diag.pydevd import silence_subprocess_check


TIMEBOMB_DELAY_S = 20 * 60


def _main():
    silence_subprocess_check()

    img_name = 'python:3.8'

    ctr_id = subprocess.check_output([
        'docker', 'run', '-d', img_name,
        'sleep', 'infinity',
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

        import mitogen.utils
        mitogen.utils.log_to_file(level='DEBUG')

        import mitogen.master
        router = mitogen.master.Router()

        ctr = router.docker(container=ctr_id, python_path='python3', debug=True)
        ctr.call(os.system, 'whoami')

        ctr.call(exec, """
import threading, sys, traceback
for th in threading.enumerate():
    print(th)
    fr = sys._current_frames()[th.ident]
    traceback.print_stack(fr, file=sys.stdout)
    print()
""")

        root = router.su(via=ctr)
        root.call(os.system, 'whoami')

        # root.shutdown(True)
        # ctr.shutdown(True)

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
