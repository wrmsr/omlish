"""
TODO:
 - PyCharm.app/Contents/plugins/python-ce/helpers/pydev/_pydevd_bundle/pydevd_constants.py -> USE_LOW_IMPACT_MONITORING
 - DISPLAY=":1" - ls /tmp/.X11-unix/X1 ?
  - https://unix.stackexchange.com/questions/17255/is-there-a-command-to-list-all-open-displays-on-a-machine
  - w -oush
"""
import dataclasses as dc
import inspect
import os.path
import shlex
import subprocess
import sys
import tempfile

from omlish.argparse import all as ap
from omlish.diag.pycharm import get_pycharm_version


##


_DARWIN_OPEN_SCRIPT = """
tell application "{app}"
    activate
    open "{dir}"
end tell
return
"""


##


_LINUX_PYCHARM_WM_CLASS = 'jetbrains-pycharm.jetbrains-pycharm'
_LINUX_CLION_WM_CLASS = 'jetbrains-clion.jetbrains-pycharm'


# sudo apt install xdotool wmctrl
# TODO: nohup pycharm.sh "$PROJECT_PATH" > /dev/null 2>&1 & ?
_LINUX_OPEN_SCRIPT = """
xdotool key --delay 1000 alt+f alt+o
xdotool type --delay 1000 {dir}
xdotool key Return
"""


@dc.dataclass(frozen=True)
class WmctrlLine:
    window_id: str
    desktop_id: str
    pid: str
    wm_class: str
    user: str
    title: str


# TODO: https://stackoverflow.com/a/79016360
def parse_wmctrl_lxp_line(l: str) -> WmctrlLine:
    return WmctrlLine(*l.strip().split(maxsplit=5))


##


class Cli(ap.Cli):
    @ap.cmd()
    def version(self) -> None:
        print(get_pycharm_version())

    @ap.cmd(
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

    @ap.cmd(
        ap.arg('dir', nargs='?'),
        ap.arg('-c', '--clion', action='store_true'),
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
            env = os.environ
            env.setdefault('DISPLAY', ':1')

            wmc_out = subprocess.check_output(['wmctrl', '-lxp'], env=env).decode()
            wls = [parse_wmctrl_lxp_line(l) for l in wmc_out.splitlines()]
            tgt_wmc = _LINUX_CLION_WM_CLASS if self.args.clion else _LINUX_PYCHARM_WM_CLASS
            tgt_wl = next(wl for wl in wls if wl.wm_class == tgt_wmc)
            subprocess.check_call(['wmctrl', '-ia', tgt_wl.window_id], env=env)

            scpt = _LINUX_OPEN_SCRIPT.format(dir=shlex.quote(os.path.expanduser(dir)))
            print(scpt)
            # subprocess.check_call(scpt, shell=True, env=env)  # noqa
            raise NotImplementedError

        else:
            raise OSError(plat)


def _main() -> None:
    Cli()(exit=True)


if __name__ == '__main__':
    _main()
