# ruff: noqa: SLF001
"""
TODO:
 - omlish.daemon?
  - add subprocess backend? is that 'too weak' to justify the daemon subsystem?
 - classic daemon cli - start/stop/status
 - STRICTLY USE AMALG SCRIPT ONLY
"""
import os.path
import sys
import typing as ta

from omlish import check
from omlish import lang
from omlish.argparse import all as ap

from ..home.paths import get_home_paths


##


@lang.cached_function
def import_script() -> ta.Any:
    from ominfra.scripts import supervisor  # noqa

    return supervisor


@lang.cached_function
def script_path() -> ta.Any:
    return import_script().__file__


##


@lang.cached_function
def config_file_path() -> str:
    return os.path.join(get_home_paths().config_dir, 'supervisor.toml')


def init_config_file(config_path: str) -> None:
    check.state(not os.path.exists(config_path))

    hp = get_home_paths()

    http_socket_path = os.path.join(hp.run_dir, 'supervisor', 'supervisor.sock')
    os.makedirs(os.path.dirname(http_socket_path), exist_ok=True)

    toml_src = '\n'.join([
        f"http_socket_path = '{http_socket_path}'",
        '',
    ])

    with open(config_path, 'w') as f:
        f.write(toml_src)


##


class Cli(ap.Cli):
    @ap.cmd()
    def path(self) -> None:
        print(script_path())

    @ap.cmd(
        ap.arg('config-file', nargs='?'),

        ap.arg('--_dev', action='store_true'),

        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
        no_help=True,
    )
    def run(self) -> None:
        if (cfp := self.args.config_file) is None:
            cfp = config_file_path()
            if not os.path.exists(cfp):
                init_config_file(cfp)

        args = [
            cfp,
            *(['--no-daemon'] if self.args._dev else []),
            *self.unknown_args,
            *(self.args.args or []),
        ]

        if self.args._dev:
            from ominfra.supervisor.main import main as dev_main  # noqa

            dev_main(args)

        else:
            os.execvp(
                exe := sys.executable,
                [
                    exe,
                    script_path(),
                ],
            )


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
