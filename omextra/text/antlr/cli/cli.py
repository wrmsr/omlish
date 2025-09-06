import logging
import re
import subprocess
import sys

from omlish.argparse import all as ap
from omlish.logs import all as logs

from .consts import ANTLR_RUNTIME_PACKAGE
from .gen import GenPy
from .gen import get_jar_path


log = logs.get_module_logger(globals())


##


class Cli(ap.Cli):
    @ap.cmd()
    def jar(self) -> None:
        print(get_jar_path())

    @ap.cmd()
    def latest(self) -> None:
        o, _ = subprocess.Popen(
            [
                sys.executable,
                '-m', 'pip',
                'index', 'versions',
                ANTLR_RUNTIME_PACKAGE,
            ],
            stdout=subprocess.PIPE,
        ).communicate()
        tl = o.decode().splitlines()[0]
        m = re.fullmatch(rf'{ANTLR_RUNTIME_PACKAGE} \((?P<version>[^)]+)\)', tl)
        if m is None:
            raise ValueError(f'Failed to parse version: {tl}')
        v = m.groupdict()['version']
        print(v)

    #

    @ap.cmd(
        ap.arg('roots', nargs='+'),
    )
    def gen(self) -> None:
        gp = GenPy(
            self.args.roots,
        )
        gp.run()


def _main() -> None:
    logs.configure_standard_logging(logging.INFO)
    cli = Cli()
    cli()


if __name__ == '__main__':
    _main()
