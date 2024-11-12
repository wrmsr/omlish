import inspect
import os.path
import subprocess
import sys
import tempfile

from omlish import argparse as ap
from omlish.diag.pycharm import get_pycharm_version


_DARWIN_OPEN_SCRIPT = """
tell application "PyCharm"
    activate
    open "{dir}"
end tell
return
"""


_LINUX_OPEN_SCRIPT = """
# Check if PyCharm is already running
if pgrep -x "pycharm.sh" > /dev/null; then
    echo "PyCharm is already running. Opening project..."

    # Bring PyCharm to the foreground
    wmctrl -a "PyCharm"

    # Simulate the keyboard shortcut to open a new project
    xdotool key --delay 100 ctrl+shift+a
    xdotool type "$PROJECT_PATH"
    xdotool key Return

else
    echo "Starting PyCharm with project..."
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
    )
    def open(self) -> None:
        dir = os.path.abspath(self.args.dir or '.')  # noqa

        if (plat := sys.platform) == 'darwin':
            if '"' in dir:
                raise ValueError(dir)

            scpt_src = _DARWIN_OPEN_SCRIPT.format(dir=dir)

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
