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
import tempfile

from omlish.argparse import all as ap

from ..cli import CliModule
from .ides import Ide
from .ides import get_ide_version
from .ides import infer_directory_ide
from .open import open_ide


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
            return Ide[ai.upper()]  # noqa

        if (ii := infer_directory_ide(cwd)) is not None:
            return ii

        return Ide.PYCHARM

    @ap.cmd(
        ap.arg('-e', '--ide'),
    )
    def version(self) -> None:
        i = self._get_ide()
        v = get_ide_version(i)
        print(v)

    @ap.cmd(
        ap.arg('dir', nargs='?'),
        ap.arg('-e', '--ide'),
    )
    def open(self) -> None:
        dir = os.path.abspath(self.args.dir or '.')  # noqa
        ide = self._get_ide(cwd=dir)
        open_ide(dir, ide=ide)


def _main() -> None:
    IntellijCli()(exit=True)


# @omlish-manifest
_CLI_MODULE = CliModule(['intellij', 'ij'], __name__)


if __name__ == '__main__':
    _main()
