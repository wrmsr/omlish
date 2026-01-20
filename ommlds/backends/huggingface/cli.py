import os
import sys
import typing as ta

from omdev.cli import CliModule
from omlish.argparse import all as ap
from omlish.logs import all as logs


log = logs.get_module_logger(globals())


##


class Cli(ap.Cli):
    def _passthrough_args_cmd(
            self,
            exe: str,
            pre_args: ta.Sequence[str] = (),
            post_args: ta.Sequence[str] = (),
    ) -> ta.NoReturn:
        os.execvp(
            exe,
            [
                sys.executable,
                *pre_args,
                *self.unknown_args,
                *self.args.args,
                *post_args,
            ],
        )

    @ap.cmd(
        ap.arg('args', nargs=ap.REMAINDER),
        name='cli',
        accepts_unknown=True,
    )
    def cli_cmd(self) -> None:
        self._passthrough_args_cmd(sys.executable, ['-m', 'huggingface_hub.cli.hf'])


##


def _main() -> None:
    logs.configure_standard_logging('INFO')
    Cli()()


# @omlish-manifest
_CLI_MODULE = CliModule('hf', __name__)


if __name__ == '__main__':
    _main()
