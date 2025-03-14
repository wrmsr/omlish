"""
TODO:
 - read .idea/ for inference?
 - PyCharm.app/Contents/plugins/python-ce/helpers/pydev/_pydevd_bundle/pydevd_constants.py -> USE_LOW_IMPACT_MONITORING
 - DISPLAY=":1" - ls /tmp/.X11-unix/X1 ?
  - https://unix.stackexchange.com/questions/17255/is-there-a-command-to-list-all-open-displays-on-a-machine
  - w -oush
"""
import dataclasses as dc
import enum
import inspect
import os.path
import shlex
import subprocess
import sys
import tempfile
import typing as ta

from omlish.argparse import all as ap
from omlish.diag.pycharm import get_pycharm_version

from ..cli import CliModule


##


class Ide(enum.Enum):
    PYCHARM = enum.auto()
    IDEA = enum.auto()
    CLION = enum.auto()
    WEBSTORM = enum.auto()
    GOLAND = enum.auto()


##


_INFER_FILE_NAME_SETS_BY_IDE: ta.Mapping[Ide, ta.AbstractSet[str]] = {
    Ide.PYCHARM: frozenset([
        'setup.py',
        'setup.cfg',
        'pyproject.toml',
        'requirements.txt',
        'Pipfile',
        'poetry.lock',
        '.python-version',
        'wsgi.py',
        'asgi.py',
        'manage.py',
    ]),
    Ide.IDEA: frozenset([
        'pom.xml',
        'mvnw',
        'build.gradle',
        'build.gradle.kts',
        'gradlew',
        'module-info.java',
        '.java-version',
    ]),
    Ide.CLION: frozenset([
        'CMakeLists.txt',
        'configure.ac',
        'configure.in',
        'config.h.in',
        'vcpkg.json',
    ]),
    Ide.WEBSTORM: frozenset([
        'package.json',
        'package-lock.json',
    ]),
    Ide.GOLAND: frozenset([
        'go.mod',
        'go.sum',
    ]),
}


def _infer_directory_ide(cwd: str | None) -> Ide | None:
    if cwd is None:
        cwd = os.getcwd()

    for i, fs in _INFER_FILE_NAME_SETS_BY_IDE.items():
        for f in fs:
            if os.path.exists(os.path.join(cwd, f)):
                return i

    return None


##


def _get_ide_version(ide: Ide) -> str:
    if ide is Ide.PYCHARM:
        return get_pycharm_version()
    else:
        raise ValueError(ide)


##


_DARWIN_OPEN_SCRIPT_APP_BY_IDE: ta.Mapping[Ide, str] = {
    Ide.PYCHARM: 'PyCharm',
    Ide.CLION: 'CLion',
    Ide.IDEA: 'IntelliJ IDEA',
    Ide.WEBSTORM: 'WebStorm',
    Ide.GOLAND: 'GoLand',
}

_DARWIN_OPEN_SCRIPT = """
tell application "{app}"
    activate
    open "{dir}"
end tell
return
"""


##


_LINUX_WM_CLASS_BY_IDE: ta.Mapping[Ide, str] = {
    Ide.PYCHARM: 'jetbrains-pycharm.jetbrains-pycharm',
    Ide.CLION: 'jetbrains-clion.jetbrains-clion',
    Ide.IDEA: 'jetbrains-idea.jetbrains-idea',
    Ide.WEBSTORM: 'jetbrains-webstorm.jetbrains-webstorm',
    Ide.GOLAND: 'jetbrains-goland.jetbrains-goland',
}


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


class IntellijCli(ap.Cli):
    @ap.cmd(
        ap.arg('python-exe'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def pycharm_runhack(self) -> int:
        if not os.path.isfile(exe := self.args.python_exe):
            raise FileNotFoundError(exe)

        from omlish.diag._pycharm import runhack  # noqa
        src = inspect.getsource(runhack)

        src_file = tempfile.mktemp(__package__ + '-runhack')  # noqa
        with open(src_file, 'w') as f:
            f.write(src)

        proc = subprocess.run([exe, src_file, *self.args.args], check=False)
        return proc.returncode

    #

    def _get_ide(
            self,
            *,
            cwd: str | None = None,
    ) -> Ide:  # noqa
        if (ai := self.args.ide) is not None:
            return Ide(ai)

        if (ii := _infer_directory_ide(cwd)) is not None:
            return ii

        return Ide.PYCHARM

    @ap.cmd(
        ap.arg('-e', '--ide'),
    )
    def version(self) -> None:
        i = self._get_ide()
        v = _get_ide_version(i)
        print(v)

    @ap.cmd(
        ap.arg('dir', nargs='?'),
        ap.arg('-e', '--ide'),
    )
    def open(self) -> None:
        dir = os.path.abspath(self.args.dir or '.')  # noqa
        ide = self._get_ide(cwd=dir)

        if (plat := sys.platform) == 'darwin':
            if '"' in dir:
                raise ValueError(dir)

            scpt_src = _DARWIN_OPEN_SCRIPT.format(
                app=_DARWIN_OPEN_SCRIPT_APP_BY_IDE[ide],
                dir=dir,
            )

            scpt_file = tempfile.mktemp(__package__ + '-intellij-open')  # noqa
            with open(scpt_file, 'w') as f:
                f.write(scpt_src)

            subprocess.check_call(['osascript', scpt_file])

        elif plat == 'linux':
            env = os.environ
            env.setdefault('DISPLAY', ':1')

            wmc_out = subprocess.check_output(['wmctrl', '-lxp'], env=env).decode()
            wls = [parse_wmctrl_lxp_line(l) for l in wmc_out.splitlines()]
            tgt_wmc = _LINUX_WM_CLASS_BY_IDE[ide]
            tgt_wl = next(wl for wl in wls if wl.wm_class == tgt_wmc)
            subprocess.check_call(['wmctrl', '-ia', tgt_wl.window_id], env=env)

            scpt = _LINUX_OPEN_SCRIPT.format(dir=shlex.quote(os.path.expanduser(dir)))
            print(scpt)
            # subprocess.check_call(scpt, shell=True, env=env)  # noqa
            raise NotImplementedError

        else:
            raise OSError(plat)


def _main() -> None:
    IntellijCli()(exit=True)


# @omlish-manifest
_CLI_MODULE = CliModule(['intellij', 'ij'], __name__)


if __name__ == '__main__':
    _main()
