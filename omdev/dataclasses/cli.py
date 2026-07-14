from omcore.argparse import all as ap
from omcore.logs.std.standard import configure_standard_logging

from .codegen import DataclassCodeGen


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('roots', metavar='root', nargs='+'),
        ap.arg('--dump-inline', action='store_true'),
        ap.arg('--dry-run', action='store_true'),
        ap.arg('--print-code', action='store_true'),
        ap.arg('--debug', action='store_true'),
        ap.arg('-j', '--jobs', type=int),
    )
    def codegen(self) -> None:
        import asyncio

        asyncio.run(DataclassCodeGen(
            dump_inline=self.args.dump_inline,
            dry_run=self.args.dry_run,
            print_code=self.args.print_code,
            debug=self.args.debug,
        ).run(
            self.args.roots,
            **(dict(concurrency=self.args.jobs) if self.args.jobs is not None else {}),
        ))


##


def _main() -> None:
    configure_standard_logging()

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
