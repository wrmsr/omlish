from omlish.argparse import all as ap
from omlish.logs.standard import configure_standard_logging

from .codegen import DataclassCodeGen


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('roots', metavar='root', nargs='+'),
    )
    def codegen(self) -> None:
        DataclassCodeGen().run(self.args.roots)


##


def _main() -> None:
    configure_standard_logging()

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
