import os.path
import tomllib
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.argparse import all as argparse

from ....home.paths import get_home_paths
from .app import IrcApp


##


@dc.dataclass(frozen=True)
class Config:
    autoexec: ta.Sequence[str] | None = None


def load_config(cfg_file: str | None = None) -> Config | None:
    if cfg_file is not None:
        check.state(os.path.exists(cfg_file), 'Config file does not exist')

    else:
        cfg_file = os.path.join(get_home_paths().config_dir, 'irc.toml')
        if not os.path.exists(cfg_file):
            return None

    with open(cfg_file) as f:
        cfg_src = f.read()

    cfg_dct = tomllib.loads(cfg_src)
    return msh.unmarshal(cfg_dct, Config)


##


def _main() -> None:
    parser = argparse.ArgumentParser(description='Simple IRC client using Textual')

    parser.add_argument(
        '-x',
        action='append',
        dest='commands',
        help='Execute slash command on startup (can be specified multiple times)',
    )

    parser.add_argument('-c', '--config', help='Specify config file')
    parser.add_argument('-C', '--no-config', action='store_true', help='Disable config file')

    args = parser.parse_args()

    #

    cfg: Config | None = None
    if not args.no_config:
        cfg = load_config(args.config)

    #

    autoexec: list[str] = []

    if cfg is not None:
        if isinstance(cfg.autoexec, str):
            autoexec.append(cfg.autoexec)
        elif cfg.autoexec:
            autoexec.extend(cfg.autoexec)

    if args.commands:
        autoexec.extend(args.commands)

    #

    app = IrcApp(
        startup_commands=autoexec,
    )
    app.run()


if __name__ == '__main__':
    _main()
