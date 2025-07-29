import dataclasses as dc
import os.path
import shlex
import subprocess
import sys
import tempfile
import typing as ta

from .ides import Ide
from .ides import infer_directory_ide


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


#


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
class _WmctrlLine:
    window_id: str
    desktop_id: str
    pid: str
    wm_class: str
    user: str
    title: str


# TODO: https://stackoverflow.com/a/79016360
def _parse_wmctrl_lxp_line(l: str) -> _WmctrlLine:
    return _WmctrlLine(*l.strip().split(maxsplit=5))


#


def open_ide(
        dir: str,  # noqa
        *,
        ide: Ide | None = None,
        default_ide: Ide = Ide.PYCHARM,
) -> None:
    if ide is None:
        if (ide := infer_directory_ide(dir)) is None:
            ide = default_ide

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
        wls = [_parse_wmctrl_lxp_line(l) for l in wmc_out.splitlines()]
        tgt_wmc = _LINUX_WM_CLASS_BY_IDE[ide]
        tgt_wl = next(wl for wl in wls if wl.wm_class == tgt_wmc)
        subprocess.check_call(['wmctrl', '-ia', tgt_wl.window_id], env=env)

        scpt = _LINUX_OPEN_SCRIPT.format(dir=shlex.quote(os.path.expanduser(dir)))
        print(scpt)
        # subprocess.check_call(scpt, shell=True, env=env)  # noqa
        raise NotImplementedError

    else:
        raise OSError(plat)
