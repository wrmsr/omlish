"""
TODO:
 - PyCharm.app/Contents/plugins/python-ce/helpers/pydev/_pydevd_bundle/pydevd_constants.py -> USE_LOW_IMPACT_MONITORING
 - DISPLAY=":1" - ls /tmp/.X11-unix/X1 ?
  - https://unix.stackexchange.com/questions/17255/is-there-a-command-to-list-all-open-displays-on-a-machine
  - w -oush
"""
import inspect
import os.path
import subprocess
import sys
import tempfile

from omlish import argparse as ap
from omlish.diag.pycharm import get_pycharm_version


_DARWIN_OPEN_SCRIPT = """
tell application "{app}"
    activate
    open "{dir}"
end tell
return
"""


_LINUX_OPEN_SCRIPT = """
# sudo apt install xdotool wmctrl

# wmctrl -lx
# 0x03000054  0 jetbrains-pycharm.jetbrains-pycharm  spinlock-ws omlish - cli.py
# 0x0480004c  0 jetbrains-clion.jetbrains-clion  spinlock-ws cpython – ceval.c
# wmctrl -i -a 0x03000054

if pgrep -x "pycharm.sh" > /dev/null; then
    # export DISPLAY=":1"
    wmctrl -x -a jetbrains-pycharm.jetbrains-pycharm
    xdotool key --delay 20 alt+f alt+o
    xdotool type --delay 10 "$(pwd)"
    xdotool key Return
else
    nohup pycharm.sh "$PROJECT_PATH" > /dev/null 2>&1 &
fi
"""


class Cli(ap.Cli):
    @ap.command()
    def version(self) -> None:
        print(get_pycharm_version())

    @ap.command(
        ap.arg('python-exe'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def runhack(self) -> int:
        if not os.path.isfile(exe := self.args.python_exe):
            raise FileNotFoundError(exe)

        from omlish.diag._pycharm import runhack  # noqa
        src = inspect.getsource(runhack)

        src_file = tempfile.mktemp(__package__ + '-runhack')  # noqa
        with open(src_file, 'w') as f:
            f.write(src)

        proc = subprocess.run([exe, src_file, *self.args.args], check=False)
        return proc.returncode

    @ap.command(
        ap.arg('dir', nargs='?'),
        ap.arg('--clion', action='store_true'),
    )
    def open(self) -> None:
        dir = os.path.abspath(self.args.dir or '.')  # noqa

        if (plat := sys.platform) == 'darwin':
            if '"' in dir:
                raise ValueError(dir)

            scpt_src = _DARWIN_OPEN_SCRIPT.format(
                app='CLion' if self.args.clion else 'PyCharm',
                dir=dir,
            )

            scpt_file = tempfile.mktemp(__package__ + '-pycharm-open')  # noqa
            with open(scpt_file, 'w') as f:
                f.write(scpt_src)

            subprocess.check_call(['osascript', scpt_file])

        elif plat == 'linux':
            # FIXME:
            raise NotImplementedError

        else:
            raise OSError(plat)


def _main() -> None:
    Cli().call_and_exit()


if __name__ == '__main__':
    _main()
