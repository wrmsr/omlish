from omlish.argparse import all as ap
from omlish.logs.std.standard import configure_standard_logging

from .codegen import DataclassCodeGen


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('roots', metavar='root', nargs='+'),
    )
    def codegen(self) -> None:
        import asyncio
        asyncio.run(DataclassCodeGen(
            # dump_inline=True,
        ).run(
            self.args.roots,
        ))


##


def _main() -> None:
    configure_standard_logging()

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
