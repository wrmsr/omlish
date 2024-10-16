import inspect
import os.path
import subprocess
import tempfile

from ... import argparse as ap
from .pycharm import get_pycharm_version


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

        from .._pycharm import runhack
        src = inspect.getsource(runhack)

        src_file = tempfile.mktemp(__package__ + '-runhack')  # noqa
        with open(src_file, 'w') as f:
            f.write(src)

        proc = subprocess.run([exe, src_file, *self.args.args], check=False)
        return proc.returncode


def _main() -> None:
    Cli().call_and_exit()


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'pycharm',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    _main()
