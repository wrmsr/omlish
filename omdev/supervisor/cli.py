"""
TODO:
 - omlish.daemon?
  - add subprocess backend? is that 'too weak' to justify the daemon subsystem?
 - classic daemon cli - start/stop/status
 - STRICTLY USE AMALG SCRIPT ONLY
"""
from omlish.argparse import all as ap


##


class Cli(ap.Cli):
    pass


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
