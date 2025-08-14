from omlish.argparse import all as ap

from .codegen import DataclassCodeGen


##


class Cli(ap.Cli):
    @ap.cmd()
    def codegen(self) -> None:
        DataclassCodeGen().run()


##


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
